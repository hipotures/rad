"""Bounded correctness funnel for removing redundant all-local host planning."""
import argparse
import shlex
import subprocess
import time
from lab import ROOT, load, save, owned_stop
ap = argparse.ArgumentParser()
ap.add_argument('stage', choices=['prerequisites', 'diagnostic'])
a = ap.parse_args()
experiment = 'E019-skip-local-host-plan'
variant = 'skip-local-host-plan-v1' if a.stage == 'prerequisites' else 'diagnostic-skip-local-host-plan-v1'
attempt = 'v1' if a.stage == 'prerequisites' else 'diagnostic-v1'
out = ROOT / 'experiments' / experiment / attempt / 'commands'
if out.exists():
    raise RuntimeError('Existing stage; preserve it and declare any repair separately')
out.mkdir(parents=True)
py = str(ROOT / 'src/control/.venv/bin/python')
records = []
def call(name, cmd, timeout):
    path = out / f'{name}.log'
    start = time.time()
    try:
        with path.open('w') as stream:
            result = subprocess.run(cmd, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=timeout)
    except subprocess.TimeoutExpired:
        owned = ROOT / 'variants' / variant / 'owned-process.json'
        if owned.exists():
            p = load(owned)
            owned_stop(p['pid'], p['create_time'])
        save(out / f'{name}-timeout.json', {'command': cmd, 'timeout_s': timeout})
        raise
    records.append({'name': name, 'command': cmd, 'returncode': result.returncode,
                    'elapsed_s': time.time()-start, 'log': str(path)})
    save(out / 'commands.json', records)
    print(name, result.returncode, path.read_text()[-2200:], flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)
cmd = [py, 'scripts/register_variant.py', variant, '--source', str(ROOT/'src'/variant),
       '--binary', str(ROOT/'builds'/variant/'strata'), '--overrides', str(ROOT/'experiments'/experiment/'v1/overrides.json')]
if a.stage == 'diagnostic':
    cmd += ['--diagnostic']
call('register', cmd, 60)
if a.stage == 'prerequisites':
    call('all-tests', [py, 'scripts/test_variant.py', variant, '--experiment', experiment, '--attempt', attempt], 900)
    call('test-failure-audit', [py, 'scripts/check_test_failures.py', experiment, '--attempt', attempt], 60)
    call('battery', [py, 'scripts/correctness_battery.py', '--variant', variant, '--experiment', experiment,
         '--attempt', attempt, '--reference', str(ROOT/'experiments/E006-frequency/correctness-r2/correctness/control')], 600)
    call('ground-truth', [py, 'scripts/check_battery.py', str(out.parent/'correctness'/variant)], 60)
else:
    call('targeted-native', [str(ROOT/'src/control/.venv/bin/ctest'), '--test-dir', str(ROOT/'builds'/variant),
         '--output-on-failure', '--timeout', '60', '-R', '(cache|adapt|async|verify|split|expert_multi|native_expert_parity)', '-j', '1'], 300)
    command = [py, str(ROOT/'scripts/collect_traces.py'), 'profiles', '--variant', variant,
               '--experiment', experiment, '--attempt', attempt]
    launcher = ROOT/'variants'/variant/'diagnose-profiles.sh'
    launcher.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec '+' '.join(shlex.quote(c) for c in command)+' "$@"\n')
    launcher.chmod(0o755)
    call('profiles', [str(launcher)], 900)
    call('strict-parity', [py, 'scripts/analyze_skip_local.py'], 180)
