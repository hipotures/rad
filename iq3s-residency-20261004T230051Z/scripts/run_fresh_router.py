"""Run the finite repaired router-signal study after clean measurements finish."""
import subprocess
import time
from lab import ROOT, load, owned_stop, save

out = ROOT / 'experiments/E015-lowrank-router/v1/commands'
if out.exists():
    raise RuntimeError('Existing study attempt; preserve it')
out.mkdir(parents=True)
py = str(ROOT / 'src/control/.venv/bin/python')
variant = 'diagnostic-router-fresh-v1'
records = []
def call(name, command, timeout):
    path = out / f'{name}.log'
    start = time.time()
    try:
        with path.open('w') as stream:
            result = subprocess.run(command, cwd=ROOT, stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=timeout)
    except subprocess.TimeoutExpired:
        owned = ROOT / 'variants' / variant / 'owned-process.json'
        if owned.exists():
            process = load(owned)
            owned_stop(process['pid'], process['create_time'])
        save(out / (name + '-timeout.json'), {'command': command, 'timeout_s': timeout,
                                             'owned_server_cleanup_attempted': True})
        raise
    records.append({'name': name, 'command': command, 'returncode': result.returncode,
                    'elapsed_s': time.time() - start, 'log': str(path)})
    save(out / 'commands.json', records)
    print(name, result.returncode, path.read_text()[-2500:], flush=True)
    if result.returncode:
        owned = ROOT / 'variants' / variant / 'owned-process.json'
        if owned.exists():
            process = load(owned)
            owned_stop(process['pid'], process['create_time'])
        raise SystemExit(result.returncode)

call('register', [py, 'scripts/register_variant.py', variant, '--source',
    str(ROOT / 'src' / variant), '--binary', str(ROOT / 'builds' / variant / 'strata'),
    '--diagnostic', '--overrides', str(out.parent / 'overrides.json')], 60)
call('tests', [py, 'scripts/test_fresh_router.py'], 600)
dest = ROOT / 'variants' / variant
for mode in ('profiles', 'episodes'):
    command = [py, str(ROOT / 'scripts/collect_traces.py'), mode, '--variant', variant,
               '--experiment', 'E015-lowrank-router', '--attempt', 'v1']
    script = dest / f'diagnose-{mode}.sh'
    import shlex
    script.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec ' +
                      ' '.join(shlex.quote(s) for s in command) + ' "$@"\n')
    script.chmod(0o755)
# Episode independence comes from the existing frozen task documents, not nonces.
call('episodes', [str(dest / 'diagnose-episodes.sh')], 900)
call('profiles', [str(dest / 'diagnose-profiles.sh')], 900)
factors = out.parent / 'checkpoints/gate-factors'
for n, (episode, split) in enumerate([
    ('dev-code', 'development'), ('dev-math', 'development'),
    ('cal-prose', 'calibration'), ('hold-code', 'holdout'),
    ('hold-structured', 'holdout'), ('hold-math', 'holdout')], 2):
    prefix = out.parent / 'episodes/traces' / f'runtime-request{n}'
    call('analysis-' + episode, [py, 'scripts/analyze_lowrank_router.py', str(prefix),
        '--output', str(out.parent / 'analysis' / (episode + '.json')),
        '--factors', str(factors), '--episode', episode, '--split', split], 180)
    if episode == 'cal-prose':
        call('frozen-rank-choice', [py, 'scripts/select_lowrank_router.py'], 60)
for profile in ('32k', '128k'):
    prefix = out.parent / profile / 'traces/runtime-request2'
    call('analysis-' + profile, [py, 'scripts/analyze_lowrank_router.py', str(prefix),
        '--output', str(out.parent / 'analysis' / (profile + '.json')),
        '--factors', str(factors), '--episode', profile, '--split', 'benchmark'], 180)
