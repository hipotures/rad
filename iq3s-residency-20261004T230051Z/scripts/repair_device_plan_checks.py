"""Preserve the wrong check invocation and apply the generic checker to E016."""
import shutil
import subprocess
from lab import ROOT, save
out = ROOT / 'experiments/E016-device-plan-ids/v1/ground-truth-repair'
if out.exists():
    raise RuntimeError('Existing repair attempt')
out.mkdir(parents=True)
shutil.copy2(ROOT / 'scripts/run_device_plan_prerequisites.py', out / 'original-driver.py')
save(out / 'protocol.json', {'error': 'The old validator has no CLI parser and ignores its path argument; the first invocation rechecked E006 instead of E016.',
    'consequence': 'Its ground-truth result is invalid as E016 evidence. Original logs retained. Native tests and actual10case records remain valid.',
    'repair': 'Use generic check_battery.py on the retained E016 answers, no new inference requests.'})
cmd = [str(ROOT / 'src/control/.venv/bin/python'), str(ROOT / 'scripts/check_battery.py'),
       str(ROOT / 'experiments/E016-device-plan-ids/v1/correctness/device-plan-ids-v1')]
with (out / 'check.log').open('w') as stream:
    result = subprocess.run(cmd, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=60)
save(out / 'command.json', {'command': cmd, 'returncode': result.returncode})
print((out / 'check.log').read_text())
if result.returncode:
    raise SystemExit(result.returncode)
