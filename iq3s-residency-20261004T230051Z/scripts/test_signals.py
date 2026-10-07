"""Execute bounded signal schema/lifecycle tests with frozen diagnostic headers."""
import subprocess, time
from lab import ROOT, save
out=ROOT/'experiments/E008-router-boundary/v1/signal-tests'
if out.exists():raise RuntimeError('Existing test attempt')
out.mkdir(parents=True);records=[]
commands=[['c++','-std=c++20','-O2','-I'+str(ROOT/'src/diagnostic-v6/include'),'-I/usr/local/cuda/include',str(ROOT/'scripts/signal_test.cpp'),'-o',str(out/'signal-test')],[str(out/'signal-test'),str(out/'signals')]]
for n,cmd in enumerate(commands):
    start=time.time()
    with (out/f'{n}.log').open('w') as stream:r=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT,timeout=60)
    records.append({'command':cmd,'returncode':r.returncode,'elapsed_s':time.time()-start,'log':str(out/f'{n}.log')});save(out/'commands.json',records)
    if r.returncode:raise SystemExit((out/f'{n}.log').read_text())
save(out/'summary.json',{'state':'PASS','tests':['default-off','active request guard','selected layer guard','global row mapping','first64 capture bound','CPU timing schema','flush and begin reset']})
print('Signal schema/lifecycle PASS')
