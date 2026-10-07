"""Audit saved evidence, frozen binaries, launch routing and unchanged model metadata."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
from lab import ROOT, load, save, hashjson

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

checks, issues = {}, []
summary = load(ROOT / 'summary.json')
assert len(summary['measured_cells']) == 22
assert sum(c['valid'] for c in summary['measured_cells']) == 66
points = {}
for cell in summary['measured_cells']:
    assert cell['valid'] == cell['attempted'] == 3
    for raw in cell['raw_paths']:
        r = load(raw)
        assert r['state'] == 'VALID' and r['actual_output_tokens'] == 4096 and r['reuse'] == 0
        assert r['actual_input_tokens'] == r['payload']['actual_input_tokens']
        assert r['actual_input_tokens'] + 4096 + 8 <= r['full_config']['max_total_context']
        assert r['full_config']['max_total_context'] in [32768, 131072]
        assert r['payload']['payload_sha256'] == hashjson(load(r['payload']['path']))
        assert r['full_config']['headline_instrumentation'] == 'OFF'
        key = (r['binary_sha256'], hashjson(r['full_config']['env']), cell['profile'],
               hashjson(r['full_config']['args']), 'frozen workload family and64-outputwarmup')
        points[key] = points.get(key, 0) + 1
    warm = load(cell['warmup_path'])
    assert warm['state'] == 'VALID' and warm['actual_output_tokens'] == 64 and warm['actual_input_tokens'] == 4096
assert max(points.values()) <= 3
checks['headline_and_repetition_invariants'] = True
for info in load(ROOT/'workloads/manifest.json')['payloads'].values():
    ids=load(info['token_ids_path'])
    assert len(ids)==info['actual_input_tokens'] and hashjson(ids)==info['input_ids_sha256']
checks['saved_effective_input_ID_hashes'] = True
binary_cache, variants = {}, []
for entry in load(ROOT / 'launch-index.json'):
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=entry['source'], text=True).strip()
    status = subprocess.check_output(['git', 'status', '--porcelain'], cwd=entry['source'], text=True)
    assert head == entry['source_sha'] and not status
    binary = entry['build']
    if binary not in binary_cache:
        binary_cache[binary] = sha(binary)
    assert binary_cache[binary] == entry['binary_sha256']
    assert entry['exercised_sessions'] and any(s['startup_record'] and s['warmup_record'] for s in entry['exercised_sessions'])
    for path in list(entry['launch_commands'].values()) + entry['diagnostic_reproducers']:
        assert Path(path).is_file() and os.access(path, os.X_OK)
        subprocess.run(['bash', '-n', path], check=True, timeout=10)
    # --help validates parser routing without starting any new inference session.
    helper = subprocess.run([entry['launch_commands']['benchmark-32k'], '--help'],
                             cwd='/tmp', capture_output=True, text=True, timeout=15)
    assert helper.returncode == 0 and '--reproduction' in helper.stdout
    for path in entry['diagnostic_reproducers']:
        helper = subprocess.run([path, '--help'], cwd='/tmp', capture_output=True, text=True, timeout=15)
        assert helper.returncode == 0 and '--reproduction' in helper.stdout
    patches = ROOT / 'git/variant-patches'
    patches.mkdir(exist_ok=True)
    patch = patches / (head + '.patch')
    if not patch.exists():
        patch.write_bytes(subprocess.check_output(['git', 'diff', '--binary',
            '6f32ec070f23ced9f50e704d854d775da52591ab', head], cwd=entry['source']))
    variants.append({'variant': entry['variant'], 'source': entry['source'], 'HEAD': head,
                     'source_status': status, 'binary': binary, 'sha256': binary_cache[binary],
                     'patch': str(patch), 'patch_sha256': sha(patch), 'state': entry['state']})
checks['source_binary_identity_and_launcher_syntax_routing'] = True
model = []
for item in load(ROOT / 'git/environment.json')['model_files']:
    p = Path(item['path']); st = p.stat()
    assert st.st_size == item['size']
    if 'mtime_ns' in item:
        assert st.st_mtime_ns == item['mtime_ns']
    if 'sha256' in item:
        assert sha(p) == item['sha256']
    model.append({'path': str(p), 'size': st.st_size, 'mtime_ns': st.st_mtime_ns,
                  'check': 'Recorded size/mtime; saved original manifest, no large-weight rehash.' if st.st_size > 1024**2 else 'SHA256 checked.'})
checks['model_profile_metadata_unchanged'] = True
for profile in ['32k', '128k']:
    for n in [1, 2, 3]:
        b = load(ROOT / f'experiments/E002-controls/v1/{profile}/raw/run{n}.json')
        c = load(ROOT / f'experiments/E024-pool-wait/v1/{profile}/raw/run{n}.json')
        fields = ['binary_sha256', 'output_text_sha256', 'mtp_proposed', 'mtp_accepted', 'verify_windows',
                  'hit_rate_pct', 'local_vram_entries', 'cpu_fallback_entries', 'offloaded_entries']
        assert all(b[f] == c[f] for f in fields)
checks['pool_wait_same_binary_visible_output_MTP_and_counters'] = True
packages = []
for d in importlib.metadata.distributions():
    m = d.metadata
    packages.append({'name': m['Name'], 'version': d.version,
        'license': m.get('License-Expression') or m.get('License'),
        'project_urls': m.get_all('Project-URL'),
        'catalog': f'https://pypi.org/project/{m["Name"]}/{d.version}/',
        'origin_limit': 'Distribution metadata and install commands retained; an unrecorded individual wheel URL is not reconstructed.'})
save(ROOT / 'git/python-dependencies-final.json', {'python': sys.executable, 'version': sys.version,
     'packages': sorted(packages, key=lambda x: x['name'].lower()),
     'install_record': str(ROOT / 'git/deps-control.json')})
save(ROOT / 'git/final-provenance.json', {'variants': variants, 'model': model,
     'model_SHA256_manifest': str(ROOT / 'references/threeway/git/IQ3_S-SHA256SUMS'),
     'environment': str(ROOT / 'git/environment.json'),
     'build_commands': str(ROOT / 'git/configure-control.json'),
     'sources': str(ROOT / 'sources.json'), 'dependencies': str(ROOT / 'git/python-dependencies-final.json')})
manifest = ROOT / 'git/artifact-inventory.jsonl'
count, total = 0, 0
with manifest.open('w') as out:
    for folder in ['experiments', 'workloads', 'references', 'scripts', 'variants']:
        for path in sorted((ROOT / folder).rglob('*')):
            if not path.is_file() or path.is_symlink() or '__pycache__' in path.parts:
                continue
            st = path.stat(); row = {'path': str(path.relative_to(ROOT)), 'size': st.st_size, 'mtime_ns': st.st_mtime_ns}
            if st.st_size <= 256 * 1024:
                row['sha256'] = sha(path)
            out.write(json.dumps(row) + '\n'); count += 1; total += st.st_size
checks['large_ignored_artifacts_manifested'] = True
checks['no_new_launcher_inference_for_audit'] = True
save(ROOT / 'analysis/final-audit.json', {'state': 'PASS_WITH_DOCUMENTED_LIMITS', 'checks': checks,
     'headline_cells': len(summary['measured_cells']), 'headline_valid_requests': 66,
     'registered_variants': len(variants), 'unique_verified_binaries': len(binary_cache),
     'manifest': str(manifest), 'manifest_files': count, 'manifest_bytes': total,
     'limitations': ['Four original native fixture/VM failures retained; no all-tests-pass claim.',
                    'Normal Session startup backend exercised for all registered variants; thin shell aliases syntax/help routed, not all independently smoke-started.',
                    'No full rehash of unchanged 83GB GGUF shards; recorded size/mtime and prior SHA256 manifest retained.',
                    'Some package license metadata/wheel origin URLs unavailable; no inferred license or origin claim.',
                    'Large ignored raw/build files remain on disk; local Git preserves reusable code/configs/patches/derived evidence.']})
print('PASS', len(variants), 'variants,', len(binary_cache), 'binaries,', count, 'manifested artifacts')
