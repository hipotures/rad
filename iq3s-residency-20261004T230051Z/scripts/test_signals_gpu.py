"""Record a bounded actual captured-event test before repaired diagnostics."""
import subprocess, time
from lab import ROOT, save
out=ROOT/'experiments/E008-router-boundary/v2/gpu-event-test'
if out.exists():raise RuntimeError('Existing GPU event test')
out.mkdir(parents=True);commands=[]
compile=['c++','-std=c++20','-O2','-I/usr/local/cuda/include',str(ROOT/'scripts/signals_gpu_test.cpp'),'-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-o',str(out/'test')]
for n,cmd in enumerate([compile,[str(out/'test')]]):
    start=time.time()
    with (out/f'{n}.log').open('w') as stream:r=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT,timeout=60)
    commands.append({'command':cmd,'returncode':r.returncode,'elapsed_s':time.time()-start});save(out/'commands.json',commands)
    if r.returncode:raise SystemExit((out/f'{n}.log').read_text())
save(out/'summary.json',{'state':'PASS','output':(out/'1.log').read_text(),'scope':'Two devices, default vs external captured event nodes, two graph executions each. No model loaded.'})
print((out/'1.log').read_text())
