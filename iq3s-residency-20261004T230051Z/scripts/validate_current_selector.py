"""Re-execute the exact frozen selector with observed causal demand and publications."""
import argparse,ctypes,json,pathlib,subprocess
import numpy as np
from trace_reader import Trace
from lab import ROOT,save
ap=argparse.ArgumentParser();ap.add_argument('prefix');ap.add_argument('--output',required=True);ap.add_argument('--decay',type=float,default=.7);a=ap.parse_args()
out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=True)
libpath=out/'selector.so'
command=['g++','-O3','-std=c++17','-fPIC','-shared',str(ROOT/'scripts/replay_selector.cpp'),'-o',str(libpath)]
subprocess.run(command,check=True);save(out/'compile.json',{'command':command,'compiler':subprocess.check_output(['g++','--version'],text=True)})
lib=ctypes.CDLL(str(libpath))
SWAP=np.dtype([('gain','<f4'),('layer','<i4'),('incoming','<i4'),('outgoing','<i4')])
lib.select_current.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_void_p]
lib.update_usage.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int]
t=Trace(a.prefix);assert t.validate()['state']=='PASS'
state=t.initial.copy();usage=t.initial_usage.copy();buffer=np.zeros(96,dtype=SWAP)
by_window={int(w['number']):[] for w in t.windows}
for layer,entries in t.grouped():by_window[int(layer['window'])].append((layer,entries))
events=[]
for p in t.promotions:
 events.append((int(p['issue']),0,p))
 if p['observed_ready']:events.append((int(p['observed_ready']),1,p))
events.sort(key=lambda e:(e[0],e[1]));index=0;mismatches=[];adaptations=0
def apply(now):
 global index
 while index<len(events) and events[index][0]<=now:
  _,kind,p=events[index];l=int(p['layer'])
  state[l,int(p['outgoing']) if kind==0 else int(p['incoming'])]=-1 if kind==0 else int(p['slot'])
  index+=1
for window in t.windows:
 w=int(window['number']);apply(int(window['pending_end']))
 for layer,entries in by_window[w]:
  ids=np.ascontiguousarray(entries['expert']);l=int(layer['layer'])
  lib.update_usage(usage[l].ctypes.data,ids.ctypes.data,len(ids))
 if (w+1)%4==0:
  # Pending batches must be published before selector admission. This trace's
  # normal blocking apply_pending path supplies that ordering.
  n=lib.select_current(usage.ctypes.data,state.ctypes.data,t.nl,t.ne,96,buffer.ctypes.data)
  got=[(int(p['layer']),int(p['incoming']),int(p['outgoing'])) for p in buffer[:n]]
  actual=[(int(p['layer']),int(p['incoming']),int(p['outgoing'])) for p in t.promotions[t.promotions['window']==w]]
  if got!=actual:mismatches.append({'window':w,'expected_count':len(actual),'replay_count':len(got),'missing':list(set(actual)-set(got))[:12],'extra':list(set(got)-set(actual))[:12],'order_only':set(got)==set(actual)})
  usage*=np.float32(a.decay);adaptations+=1
final_usage_error=float(np.max(np.abs(usage-t.final_usage)))
result={'state':'PASS' if not mismatches and final_usage_error==0 else 'FAIL','prefix':a.prefix,'decay':a.decay,'adaptations':adaptations,'promotions':len(t.promotions),'selection_mismatches':mismatches,'final_usage_max_abs_error':final_usage_error,'implementation':'exact C++ comparator/partial_sort/tie behavior, repeated float32 increments; recorded copy completion times; no future-demand input'}
save(out/'validation.json',result);print(json.dumps(result,indent=2));assert result['state']=='PASS'
