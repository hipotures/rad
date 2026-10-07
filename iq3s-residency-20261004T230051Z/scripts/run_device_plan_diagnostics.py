"""Validate the new coordination path's real routing/heat before speed."""
import shlex
import subprocess
import time
from lab import ROOT, save
out = ROOT / 'experiments/E016-device-plan-ids/diagnostic-v1/commands'
if out.exists():
    raise RuntimeError('Existing diagnostic attempt')
out.mkdir(parents=True)
py = str(ROOT / 'src/control/.venv/bin/python')
variant = 'diagnostic-device-plan-ids-v1'
records = []
def call(name, command, timeout):
    path = out / f'{name}.log'
    start = time.time()
    with path.open('w') as stream:
        result = subprocess.run(command, cwd=ROOT, stdout=stream,
                                stderr=subprocess.STDOUT, timeout=timeout)
    records.append({'name': name, 'command': command, 'returncode': result.returncode,
                    'elapsed_s': time.time() - start, 'log': str(path)})
    save(out / 'commands.json', records)
    print(name, result.returncode, path.read_text()[-2500:], flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)
call('clean-native-failure-audit', [py, 'scripts/check_test_failures.py', 'E016-device-plan-ids'], 60)
call('register', [py, 'scripts/register_variant.py', variant,
    '--source', str(ROOT / 'src' / variant), '--binary', str(ROOT / 'builds' / variant / 'strata'),
    '--diagnostic', '--overrides', str(ROOT / 'experiments/E016-device-plan-ids/v1/overrides.json')], 60)
call('targeted-native', [str(ROOT / 'src/control/.venv/bin/ctest'), '--test-dir',
    str(ROOT / 'builds' / variant), '--output-on-failure', '--timeout', '60', '-R',
    '(cache|adapt|async|verify|split|expert_multi|native_expert_parity)', '-j', '1'], 300)
command = [py, str(ROOT / 'scripts/collect_traces.py'), 'profiles', '--variant', variant,
           '--experiment', 'E016-device-plan-ids', '--attempt', 'diagnostic-v1']
launcher = ROOT / 'variants' / variant / 'diagnose-profiles.sh'
launcher.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec ' +
                   ' '.join(shlex.quote(s) for s in command) + ' "$@"\n')
launcher.chmod(0o755)
call('profiles', [str(launcher)], 900)
