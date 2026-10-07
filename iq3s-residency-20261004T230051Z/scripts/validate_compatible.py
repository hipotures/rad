"""Validate native policy against retained causal replay, with no background build."""
import argparse,ctypes,hashlib,pathlib,subprocess,time
import numpy as np
from lab import ROOT,save
from placement_replay import CompatibleReplay
from replay import library
from trace_reader import Trace
ap=argparse.ArgumentParser();ap.add_argument('--attempt',default='v1');ap.add_argument('--variant',default='compatible-v1');ap.add_argument('--experiment',default='E010-compatible-runtime');a=ap.parse_args()
out=ROOT/'experiments'/a.experiment/a.attempt/'selector-tests'
if out.exists():raise RuntimeError('Existing selector test attempt')
out.mkdir(parents=True);include=ROOT/'src'/a.variant/'include';commands=[]
for name,src,flags in [('unit','test_compatible.cpp',[]),('bridge','compatible_bridge.cpp',['-shared','-fPIC'])]:
    target=out/(name+'.so' if name=='bridge' else name)
    cmd=['c++','-std=c++20','-O3','-I'+str(include),*flags,str(ROOT/'scripts'/src),'-o',str(target)]
    with (out/f'{name}-compile.log').open('w') as stream:r=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT,timeout=60)
    commands.append({'command':cmd,'returncode':r.returncode});save(out/'commands.json',commands)
    if r.returncode:raise SystemExit((out/f'{name}-compile.log').read_text())
subprocess.run([str(out/'unit')],check=True,timeout=60)
lib=ctypes.CDLL(str(out/'bridge.so'));D=np.dtype([('gain','<f8'),('layer','<i4'),('incoming','<i4'),('outgoing_layer','<i4'),('outgoing','<i4')]);assert D.itemsize==24
lib.compatible_bridge.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_void_p]
class CheckedReplay(CompatibleReplay):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.native_us=[];self.matches=0;self.buffer_cpp=np.zeros(96,D)
    def compatible(self,index):
        expected=super().compatible(index);start=time.perf_counter_ns()
        n=lib.compatible_bridge(self.usage.ctypes.data,self.state.ctypes.data,self.t.nl,self.t.ne,25,self.t.blob_bytes.ctypes.data,self.t.slot_bytes[0].ctypes.data,len(self.t.slot_bytes[0]),self.t.slot_bytes[1].ctypes.data,len(self.t.slot_bytes[1]),96,self.buffer_cpp.ctypes.data)
        self.native_us.append((time.perf_counter_ns()-start)/1000)
        actual=[(int(r['layer']),int(r['incoming']),int(r['outgoing_layer']),int(r['outgoing'])) for r in self.buffer_cpp[:n]]
        if actual!=expected:raise RuntimeError(f'Native selector mismatch at window index{index}: {actual[:8]} vs {expected[:8]}')
        self.matches+=1;return actual
results=[]
for profile,attempt in [('32k','v5'),('128k','v5-portfix')]:
    prefix=ROOT/'experiments/E003-diagnostics'/attempt/profile/'traces/runtime-request2';t=Trace(prefix);assert t.validate()['state']=='PASS'
    replay=CheckedReplay(t,'global-compatible-ema',12.6,library());r=replay.run()
    previous=__import__('json').loads((ROOT/'experiments/E009-placement/v1'/profile/'replay.json').read_text())
    for key in ['nonlocal_entries','promotion_bytes','promotion_count','modeled_pending_wait_s','victim_demand_while_absent']:assert r[key]==previous[key],(key,r[key],previous[key])
    costs=np.asarray(replay.native_us)
    row={'profile':profile,'state':'PASS','selection_calls_all_match':replay.matches,'nonlocal_entries':r['nonlocal_entries'],'promotion_bytes':r['promotion_bytes'],'native_bridge_selector_us':{'median':float(np.median(costs)),'p95':float(np.percentile(costs,95)),'max':float(costs.max()),'sum':float(costs.sum())},'cost_scope':'Single-thread offline native selector plus bridge vector copies/ctypes. Includes temporary native vectors, excludes causal runtime contention; not a TG projection.','header_sha256':hashlib.sha256((include/'strata/research/compatible_policy.hpp').read_bytes()).hexdigest()}
    results.append(row);save(out/'summary.json',{'state':'PASS','rows':results,'synthetic_unit':'owner/fit/unique victim slot/immutable selection/withdraw-before-publish/no-hot/invalid slot/split/max cases pass. This is not a CUDA race proof; live copy backend is unchanged and source safety is separately audited.'})
    print(row,flush=True)
