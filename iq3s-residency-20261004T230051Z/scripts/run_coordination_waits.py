"""Same-binary OFF/ON diagnostics; no concurrent builds or headline measurements."""
import shlex, subprocess, time
from lab import ROOT, load, save, owned_stop
experiment = 'E021-device-plan-waits'; build_variant = 'diagnostic-coordination-v1'
base = ROOT/'experiments'/experiment/'v1'; out = base/'commands'
assert not out.exists(); out.mkdir()
py = str(ROOT/'src/control/.venv/bin/python'); records = []
variants = []
def call(name, cmd, timeout=300):
    path = out/f'{name}.log'; start = time.time()
    try:
        with path.open('w') as f:
            result = subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, timeout=timeout)
    except subprocess.TimeoutExpired:
        for v in variants:
            owner = ROOT/'variants'/v/'owned-process.json'
            if owner.exists():
                p = load(owner); owned_stop(p['pid'], p['create_time'])
        save(out/f'{name}-timeout.json', {'command': cmd, 'timeout_s': timeout}); raise
    records.append({'name': name, 'command': cmd, 'returncode': result.returncode,
                    'elapsed_s': time.time()-start, 'log': str(path)})
    save(out/'commands.json', records)
    print(name, result.returncode, path.read_text()[-2000:], flush=True)
    if result.returncode: raise SystemExit(result.returncode)
call('tests', [py, 'scripts/test_coordination_waits.py', '--variant', build_variant,
              '--experiment', experiment, '--attempt', 'v1'])
for mode in ('off', 'on'):
    variant = f'diagnostic-coordination-{mode}-v1'; variants.append(variant)
    call('register-'+mode, [py, 'scripts/register_variant.py', variant,
         '--source', str(ROOT/'src'/build_variant), '--binary', str(ROOT/'builds'/build_variant/'strata'),
         '--diagnostic', '--overrides', str(base/f'{mode}-overrides.json')], 60)
    cmd = [py, 'scripts/collect_traces.py', 'profiles', '--variant', variant,
           '--experiment', experiment, '--attempt', 'v1/'+mode]
    launcher = ROOT/'variants'/variant/'diagnose-profiles.sh'
    launcher.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec '+
                        ' '.join(shlex.quote(x) for x in cmd)+' "$@"\n')
    launcher.chmod(0o755)
    call('profiles-'+mode, [str(launcher)], 800)
    for profile in ('32k', '128k'):
        folder = base/mode/profile
        reference = (ROOT/'experiments/E015-lowrank-router/v1'/profile if mode == 'off'
                     else base/'off'/profile)
        call(f'parity-{mode}-{profile}', [py, 'scripts/check_trace_parity.py',
             str(folder/'traces/runtime-request2'), str(reference/'traces/runtime-request2'),
             '--output', str(folder/'parity.json')], 150)
        ref_experiment = 'E015-lowrank-router' if mode == 'off' else experiment
        ref_attempt = 'v1' if mode == 'off' else 'v1/off'
        call(f'analysis-{mode}-{profile}', [py, 'scripts/analyze_coordination_waits.py', profile,
             '--experiment', experiment, '--attempt', 'v1/'+mode,
             '--reference-experiment', ref_experiment, '--reference-attempt', ref_attempt], 150)
save(base/'collection.json', {'state': 'PASS', 'same_binary': True, 'commands': records,
                            'headline': False, 'profiles': ['32k', '128k']})
