"""Read-only verification of the completed headline matrix and preserved old experiments."""
import hashlib
import math
import pathlib
import re
import statistics
import subprocess
from lab import ROOT, hashjson, load, save

campaign = pathlib.Path(load(ROOT / 'active-campaign.json')['path'])
experiments = ['E026-pool-generalization', 'E027-pool-baseline', 'E029-persistent-runtime']
files = {}
cells = []

def preserve(path):
    path = pathlib.Path(path)
    assert path.is_file(), path
    name = str(path)
    if name not in files:
        files[name] = {'size': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

for experiment in experiments:
    summary = load(ROOT / 'experiments' / experiment / 'summary.json')
    for cell in summary['cells']:
        assert cell['attempts'] == cell['valid_fixed_length'] == 3
        runs = []
        for name in cell['raw_paths']:
            path = pathlib.Path(name)
            raw = load(path)
            assert raw['state'] == 'VALID' and raw['actual_output_tokens'] == 4096 and raw['reuse'] == 0
            assert raw['full_config']['source_sha'] == raw['source_sha']
            assert raw['full_config']['binary_sha256'] == raw['binary_sha256']
            limit = raw['full_config']['max_total_context']
            assert limit in (32768, 131072)
            assert raw['actual_input_tokens'] + raw['actual_output_tokens'] + 8 <= limit
            payload = raw['payload']
            assert hashjson(load(payload['path'])) == payload['payload_sha256']
            ids = load(payload['token_ids_path'])
            assert len(ids) == raw['actual_input_tokens']
            assert hashjson(ids) == payload['input_ids_sha256']
            actual = load(path.parent / 'output-ids-input-request2.json')
            assert actual['count'] == len(ids) and actual['sha256'] == payload['input_ids_sha256']
            outputs = load(path.parent / 'output-ids-request2.json')
            assert len(outputs) == 4096
            if raw.get('actual_output_ids_sha256'):
                assert hashjson(outputs) == raw['actual_output_ids_sha256']
            warm = load(path.parent / 'warmup.json')
            assert warm['state'] == 'VALID' and warm['actual_output_tokens'] == 64 and warm['reuse'] == 0
            for file in [path, path.parent/'warmup.json', path.parent/'run-engine.log',
                         path.parent/'resource-check.json', path.parent/'output-ids-request2.json',
                         path.parent/'output-ids-input-request2.json', pathlib.Path(payload['path']),
                         pathlib.Path(payload['token_ids_path']), pathlib.Path(raw['telemetry']['path']),
                         path.parents[1]/'config.json', path.parents[1]/'process.json',
                         path.parents[1]/'telemetry/pcie-dmon.log']:
                preserve(file)
            runs.append(raw)
        for key in ['PP', 'TG', 'TTFT_s', 'wall_s', 'actual_input_tokens', 'actual_output_tokens',
                    'mtp_proposed', 'mtp_accepted', 'verify_windows', 'cpu_fallback_entries', 'offloaded_entries']:
            values = [run[key] for run in runs]
            expected = dict(min=min(values), median=statistics.median(values), max=max(values))
            assert all(math.isclose(cell['metrics'][key][stat], value, rel_tol=1e-10, abs_tol=1e-10)
                       for stat, value in expected.items()), (experiment, cell['profile'], cell['role'], key)
        cells.append({'experiment': experiment, 'family': cell['family'], 'profile': cell['profile'],
                      'role': cell['role'], 'valid_measured': 3, 'state': 'PASS', 'raw': cell['raw_paths']})

changed = subprocess.check_output(['git', 'diff', '--name-only', '63fc94229f8153d0c396f441dbb89c6b687eeff1'], cwd=ROOT, text=True).splitlines()
old_changes = [path for path in changed if (match := re.match(r'experiments/E(\d{3})', path)) and int(match[1]) < 26]
assert not old_changes, old_changes
result = {'state': 'PASS_REPRODUCIBLE_HEADLINE_MATRIX', 'cells': cells,
          'valid_measured_requests': sum(row['valid_measured'] for row in cells),
          'file_manifest': files, 'old_tracked_experiment_changes': old_changes,
          'limits': ['Headline scalar medians recomputed independently from saved raw records.',
                     'Old ignored raw data were not rewritten; archived root hashes are independently checked in end-state.json.',
                     'Diagnostic/screen requests are preserved separately and not pooled into headline medians.']}
save(campaign / 'reproducibility-audit.json', result)
print(result['state'], result['valid_measured_requests'], 'requests', len(files), 'hashed artifacts', flush=True)
