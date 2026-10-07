"""Preserve exact local input/output identities and explicit recovery gaps after timing."""
import hashlib
from common import *

def identity(path):
    path = pathlib.Path(path)
    before = path.stat()
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    after = path.stat()
    assert (before.st_size, before.st_mtime_ns, before.st_ino) == (after.st_size, after.st_mtime_ns, after.st_ino), path
    return {'path': str(path), 'bytes': before.st_size, 'sha256': digest}

if __name__ == '__main__':
    no_gpu()
    p2 = INPUT_PARENT / 'golden-swap-phase2-20261007T093357Z'
    prior = load(p2 / 'input-manifest.json')
    original = {t['task_id']: t for t in load(P0 / 'benchmark-manifest.json')['tasks']}
    independent = load(C / 'inputs/independent-task-manifest.json')
    runs = load(C / 'results/live-attempts.json')
    inputs = []
    with Heartbeat('input and binary artifact identity manifests', 5):
        for inherited in prior['inputs']:
            x = dict(inherited)
            task = original.get(x['id'], independent)
            tape = pathlib.Path(x['tape'])
            assert identity(tape)['sha256'] == x['sha256']
            x['phase3_usage'] = 'fixed primary regression' if x['id'] in ['code-archive', 'math-inventory', 'text-websocket', 'mixed-chinook'] else 'previously evaluated independent-source check' if x['id'] == independent['task_id'] else 'deterministic development/calibration parity; math-rational also live development'
            x['phase3_prior_evaluation_exposure'] = True
            x['phase3_pristine_holdout'] = False
            x['source_group'] = task['source_group']
            x['profile'] = task['profile']
            x['source_provenance'] = {k: task[k] for k in ['source_revision', 'source_url', 'source_urls', 'source_sha256', 'license', 'excerpt_sha256', 'tool_execution'] if k in task}
            actual = next((r for r in runs if r['task'] == x['id']), None)
            if actual:
                x.update(actual_output_tokens=actual['output'], verify_windows=actual['windows'], work_sha256=actual['work_sha256'], replay_initial_state_sha256=actual['initial_state_sha256'])
                episode = load(C / 'raw' / actual['label'] / 'episode.json')
                x['context_occupancy_tokens'] = actual['input'] - 1 + episode['fidelity']['state_committed_tokens']
                x['context_occupancy_definition'] = 'End committed position: input -1 + sum(accepted+1), including any un-emitted suffix in the final verifier window.'
            if x['id'] == independent['task_id']:
                x.update(main_output_tokens=independent['main_output_tokens'], main_windows=independent['main_windows'], observed_tail_tokens=independent['observed_tail_tokens'], context_occupancy_tokens=independent['context_occupancy_tokens'], continuation='Same continuous recorded request; measured main prefix plus observed finite tail; reused from Phase2')
            inputs.append(x)
        save(C / 'input-manifest.json', {'inputs': inputs, 'phase0_source_manifest': str(P0 / 'benchmark-manifest.json'), 'phase2_input_manifest': str(p2 / 'input-manifest.json'), 'all_sources_previously_exposed': True, 'no_fit_or_retuning': True, 'frozen_model': {'family': 'unsloth/Qwen3.8-Flash-Next-GGUF', 'quantization': 'UD-Q4_K_XL', 'revision': '38bb39ee97821de2c9009abb7e93950eec396e66', 'backing': '/srv/ai/models/strata/packs/ud-q4_k_xl-v0132', 'recovery': 'Pinned downloadable model plus pack reconstruction contract in retained Phase0/oracle manifests; no model-weight upload'}, 'ordinary_settings': load(C / 'configs/protocol.json')['unchanged_frozen_settings']})
        input_manifest = load(C / 'input-manifest.json')
        input_manifest['inherited_input_contract'] = {k:v for k,v in prior.items() if k != 'inputs'}
        input_manifest['inherited_input_contract_note'] = 'Historical Phase2 references retained verbatim; Phase3 exposure and gzip publication scope above supersede historical freshness/exclusion statements.'
        save(C / 'input-manifest.json', input_manifest)
        binaries = []
        for root in [W / 'raw', W / 'logs']:
            for path in sorted(root.rglob('*')):
                if not path.is_file() or path.is_symlink():
                    continue
                # Complete eligible text is retained by the separate checked gzip protocol.
                if path.suffix.lower() in {'.json', '.jsonl', '.log', '.txt'}:
                    continue
                binaries.append(identity(path))
        for path in [BUILD / 'strata', W / 'builds/libfnv64.so']:
            binaries.append(identity(path))
    reproduction = load(C / 'tests/reproduction-checks.json')['live']['directory']
    save(C / 'artifact-manifest.json', {'runtime_identity': load(C / 'configs/runtime-identity.json'), 'external_work_root': str(W), 'raw_directory': str(W / 'raw'), 'binary_and_nontext_files': binaries, 'input_manifest': 'input-manifest.json', 'frozen_checkpoint': identity(C / 'models/logistic.txt'), 'source_recovery': {'public_base': '6f32ec070f23ced9f50e704d854d775da52591ab', 'public_repository': 'https://github.com/Niko1221/Strata', 'patch': 'patches/cumulative-from-original.diff', 'tested_receipt': 'tests/source-recovery.json', 'build_commands': 'configs/runtime-identity.json', 'scope': 'Source reconstructed byte-for-byte excluding machine-local .venv link; actual measured binary built; no second build claimed'}, 'text_evidence_publication': {'protocol': '../../../../docs/text-evidence.md', 'archives': [{'path': 'evidence/completed-text-v1', 'source_root': str(W / 'raw')}, {'path': 'evidence/runner-logs-v1', 'source_root': str(W / 'logs')}, {'path': 'evidence/reproduction-text-v1', 'source_root': reproduction}, {'path': 'evidence/fixtures-text-v1', 'source_root': str(C / 'tests')}], 'scope': 'Complete eligible source files, strictly smaller than10MiB per gzip, no splitting. Original text remains immutable; compressed manifest records all omissions.'}, 'recovery_limit': 'Exact natural tapes and raw binary journals remain persistent host-local evidence without an identified independent off-host backup. Model and public dependencies are downloadable; source changes are reconstructible from public base plus tracked cumulative patch. Exact natural tape generation is not guaranteed reproducible. Git and complete gzip text preserve the interpretation and text records but cannot recover the omitted binary bytes.'})
    print('MANIFESTS WRITTEN', len(inputs), len(binaries), flush=True)
