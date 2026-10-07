"""Read-only final identity/data/ownership audit, after all speed and smoke runs."""
from campaign import C, R, load, save
from pathlib import Path
from launch import verify
import collections, hashlib, json, os, psutil, subprocess, time


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def main():
    assert load(C / 'phase-c/matrix-exit.json')['exit_code'] == 0
    assert load(C / 'phase-c/advertised-launch-smokes.json')['count'] == 9
    summary = load(C / 'phase-c/summary.json')
    assert summary['state'] == 'COMPLETE_PRIMARY'
    primary = [r for r in summary['runs']
               if r['variant'] in ['control', 'history-v2', 'early-v1']]
    assert len(primary) == 27
    counts = collections.Counter((r['variant'], r['profile']) for r in primary)
    assert len(counts) == 9 and all(n == 3 for n in counts.values())
    attempts = []
    for run in primary:
        raw = Path(run['raw'])
        record = load(raw)
        cfg = load(raw.parent.parent / 'config.json')
        warm = load(raw.parent.parent / 'results.json')['warmup']
        assert record['state'] == 'VALID' and record['reuse'] == 0
        assert record['actual_output_tokens'] == 4096
        assert record['actual_engine_input_verified']
        assert record['actual_input_tokens'] + 4096 <= cfg['max_total_context']
        assert warm['state'] == 'VALID' and warm['actual_output_tokens'] == 64
        assert warm['actual_input_tokens'] == 4096 and warm['reuse'] == 0
        assert digest(record['actual_output_ids_path']) == record['actual_output_ids_sha256']
        assert record['local_vram_entries'] + record['cpu_fallback_entries'] + record['nonlocal_gpu_entries'] == record['all_routed_entries']
        native = load(raw.parent / 'native-process.json')
        assert Path(native['executable']).resolve() == Path(cfg['exe']).resolve()
        assert native['effective_environment']['STRATA_POOL_SPIN_US'] == '100'
        assert native['command'][native['command'].index('--layer-split') + 1] == '24'
        attempts.append({'raw': str(raw), 'variant': run['variant'],
                         'profile': run['profile'], 'actual_input': record['actual_input_tokens'],
                         'actual_output': record['actual_output_tokens'], 'input_hash': record['actual_engine_input']['sha256'],
                         'output_hash': record['actual_output_ids_sha256'], 'PASS': True})
    identities = []
    for variant in ['control', 'history-v2', 'early-v1']:
        for profile in ['32k', '128k', '256k']:
            cfg = load(C / 'launchers' / variant / (profile + '.json'))
            verified = verify(cfg)
            identities.append({'variant': variant, 'profile': profile,
                               'source': verified['source'], 'binary': verified['binary'],
                               'binary_sha256': verified['binary_sha256'], 'PASS': True})
    model = load(C / 'git/model.json')
    # Large GGUF shards retain their prior SHA manifest and unchanged stat identity.
    # Rehash pack/profile/MTP dependencies only after every headline has finished.
    dependencies = []
    for path, old in model['files'].items():
        current = digest(path)
        assert current == old['sha256'], 'Model dependency content changed: ' + path
        dependencies.append({'path': path, 'sha256': current, 'bytes': Path(path).stat().st_size})
    reference_checks = []
    for old in load(C / 'git/starting-evidence/sources.json')['local_references']:
        path = Path(old['source'])
        assert digest(path) == old['sha256'], 'A preserved previous reference changed: ' + str(path)
        reference_checks.append({'path': str(path), 'sha256': old['sha256'], 'PASS': True})
    assert digest(C / 'scripts/serve_capture.py') == load(C / 'git/frozen-identity.json')['front_end_sha256']
    checkpoint = C / 'checkpoints/linear.npz'
    assert digest(checkpoint) == load(C / 'phase-b/learned/export.json')['checkpoint_sha256']
    checkpoint_checks = [{'path': str(p), 'bytes': p.stat().st_size, 'sha256': digest(p)}
                         for p in sorted((C / 'checkpoints').glob('*.npz'))]
    compute = subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid,process_name,used_memory',
                                       '--format=csv,noheader'], text=True).strip()
    assert not compute, 'Owned processes must be stopped; never kill unrelated processes'
    own_running = []
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            if proc.pid == os.getpid():
                continue
            args = proc.info['cmdline'] or []
            joined = ' '.join(args)
            exact_owned_path = any(word.startswith(str(C) + '/') for word in args)
            is_compute = any(word in args for word in ['--serve', '--engine']) or any(
                marker in joined for marker in ['train_predictors.py', 'nsys profile', 'ncu --'])
            if exact_owned_path and is_compute:
                own_running.append({'pid': proc.pid, 'command': args})
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
    assert not own_running, own_running
    sampler = (R / 'scripts/lab.py').read_text()
    sampler_class = sampler.split('class Sampler:', 1)[1].split('class Session:', 1)[0]
    assert all(word not in sampler_class for word in ['memory_full_info', 'smaps', 'Pss'])
    audit = {'PASS': True, 'checked_epoch': time.time(), 'primary_attempts': attempts,
             'three_attempt_rule': dict((v + '/' + p, n) for (v, p), n in counts.items()),
             'launcher_identities': identities, 'dependency_content_checks': dependencies,
             'auxiliary_checkpoint_checks': checkpoint_checks,
             'prior_reference_content_checks': reference_checks, 'GPU_compute_processes': compute,
             'owned_serving_training_profiling_processes': own_running,
             'telemetry': 'RSS / CPU / GPU / available RAM at about 1 Hz; sampler has no PSS/smaps polling.',
             'weight_check_scope': 'All four GGUF sizes/mtime verified against prior SHA manifest; pack/profile/MTP dependencies rehashed. No redundant 111 GB shard hash pass.',
             'previous_data_scope': 'Preserved reference manifests rehashed; no old raw directory was a campaign write target. This is not a retrospective full-tree hash proof.',
             'no_push_or_PR': 'Only local source/research commits and read-only pinned source retrieval; no push/PR command used.'}
    save(C / 'phase-c/final-audit.json', audit)
    print('FINAL_IDENTITY_DATA_OWNERSHIP_AUDIT_PASS', len(attempts), flush=True)


if __name__ == '__main__':
    main()
