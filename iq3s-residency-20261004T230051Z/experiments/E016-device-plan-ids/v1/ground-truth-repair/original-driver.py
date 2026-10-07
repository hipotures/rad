"""Complete bounded native and greedy prerequisites for the coordination candidate."""
import subprocess
import time
from lab import ROOT, load, owned_stop, save

experiment = 'E016-device-plan-ids'
variant = 'device-plan-ids-v1'
out = ROOT / 'experiments' / experiment / 'v1/prerequisite-commands'
if out.exists():
    raise RuntimeError('Existing prerequisite attempt')
out.mkdir(parents=True)
py = str(ROOT / 'src/control/.venv/bin/python')
commands = []
def call(name, command, timeout=900):
    path = out / f'{name}.log'
    start = time.time()
    try:
        with path.open('w') as stream:
            result = subprocess.run(command, cwd=ROOT, stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=timeout)
    except subprocess.TimeoutExpired:
        owned = ROOT / 'variants' / variant / 'owned-process.json'
        if owned.exists():
            p = load(owned); owned_stop(p['pid'], p['create_time'])
        save(out / (name + '-timeout.json'), {'command': command, 'timeout_s': timeout})
        raise
    commands.append({'name': name, 'command': command, 'returncode': result.returncode,
                     'elapsed_s': time.time() - start, 'log': str(path)})
    save(out / 'commands.json', commands)
    print(name, result.returncode, path.read_text()[-2500:], flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)

call('register', [py, 'scripts/register_variant.py', variant, '--source', str(ROOT / 'src' / variant),
    '--binary', str(ROOT / 'builds' / variant / 'strata'), '--overrides',
    str(ROOT / 'experiments' / experiment / 'v1/overrides.json')], 60)
call('compile-ID-fixture', ['c++', '-std=c++20', '-O2', '-I/usr/local/cuda/include',
    str(ROOT / 'scripts/device_plan_ids_test.cpp'), str(ROOT / 'builds' / variant / 'libstrata_kernels.a'),
    '-L/usr/local/cuda/lib64', '-Wl,-rpath,/usr/local/cuda/lib64', '-lcudart', '-lcublas',
    '-lcublasLt', '-o', str(out / 'ID-fixture')], 60)
call('ID-overwrite-and-repair', [str(out / 'ID-fixture')], 60)
call('native-Python-realIQ', [py, 'scripts/test_variant.py', variant,
    '--experiment', experiment, '--attempt', 'v1'])
call('battery', [py, 'scripts/correctness_battery.py', '--variant', variant,
    '--experiment', experiment, '--attempt', 'v1', '--reference',
    str(ROOT / 'experiments/E006-frequency/correctness-r2/correctness/control')], 600)
call('ground-truth', [py, 'scripts/validate_correctness_answers.py',
    str(ROOT / 'experiments' / experiment / 'v1/correctness' / variant)], 60)
