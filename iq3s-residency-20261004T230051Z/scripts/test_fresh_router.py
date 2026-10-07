"""Record bounded tests of the diagnostic activation-availability repair."""
import os
import subprocess
import time
from lab import ROOT, save

variant = 'diagnostic-router-fresh-v1'
out = ROOT / 'experiments/E015-lowrank-router/v1/tests'
if out.exists():
    raise RuntimeError('Existing test attempt; preserve it')
out.mkdir(parents=True)
source, build = ROOT / 'src' / variant, ROOT / 'builds' / variant
commands = []
def call(name, command):
    path = out / f'{name}.log'
    start = time.time()
    with path.open('w') as stream:
        result = subprocess.run(command, cwd=ROOT, stdout=stream,
                                stderr=subprocess.STDOUT, timeout=300)
    commands.append({'name': name, 'command': command, 'returncode': result.returncode,
                     'elapsed_s': time.time() - start, 'log': str(path)})
    save(out / 'commands.json', commands)
    print(name, result.returncode, path.read_text()[-2000:], flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)

common = ['c++', '-std=c++20', '-O2', '-I/usr/local/cuda/include',
          '-L/usr/local/cuda/lib64', '-Wl,-rpath,/usr/local/cuda/lib64']
call('compile-doorbell-fixture', common + [str(ROOT / 'scripts/fresh_doorbell_test.cpp'),
    str(build / 'libstrata_kernels.a'), '-lcudart', '-lcublas', '-lcublasLt',
    '-o', str(out / 'doorbell-fixture')])
call('actual-doorbell-replay', [str(out / 'doorbell-fixture')])
call('compile-signal-fixture', common + ['-I' + str(source / 'include'),
    str(ROOT / 'scripts/signal_test.cpp'), '-lcudart', '-o', str(out / 'signal-fixture')])
call('signal-schema-lifecycle', [str(out / 'signal-fixture'), str(out / 'signals')])
call('compile-event-fixture', common + [str(ROOT / 'scripts/signals_gpu_test.cpp'),
    '-lcudart', '-o', str(out / 'event-fixture')])
call('external-events-both-GPUs', [str(out / 'event-fixture')])
call('targeted-native', [str(ROOT / 'src/control/.venv/bin/ctest'), '--test-dir',
    str(build), '--output-on-failure', '--timeout', '60', '-R',
    '(cache|adapt|async|verify|split|expert_multi|native_expert_parity)', '-j', '1'])
call('realIQparity', [str(build / 'native_expert_parity'),
    '/srv/ai/models/strata/models/IQ3_S/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf',
    '0', '1', '2', '12'])
save(out / 'summary.json', {'state': 'PASS', 'scope':
    'Real unchanged doorbell kernel verifies freshness condition and forced-copy graph replay; '
    'bounded signal lifecycle, two-device external events, cache/verify/native tests and real IQ parity. '
    'Diagnostic only; no inference algorithm or frontend modification.'})
