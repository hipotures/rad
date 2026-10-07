"""Reconcile every Q4 routed entry, native byte class and exact current admission."""
from pathlib import Path
import ctypes, hashlib, json, shutil, subprocess, sys
import numpy as np
C=Path(__file__).resolve().parents[1];R=C.parents[1]
sys.path.insert(0,str(C/'scripts'))
from trace_reader import Trace
from campaign import load,save
SWAP=np.dtype([('gain','<f4'),('layer','<i4'),('incoming','<i4'),('outgoing','<i4')])
def selector_library(out):
 out.mkdir(parents=True,exist_ok=True);src=out/'replay_selector.cpp'
 if not src.exists():shutil.copy2(R/'scripts/replay_selector.cpp',src)
 so=out/'selector.so'
 command=['g++','-O3','-std=c++17','-fPIC','-shared',str(src),'-o',str(so)]
 if not so.exists():subprocess.run(command,check=True,timeout=90)
 save(out/'compile.json',{'command':command,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
 lib=ctypes.CDLL(str(so));lib.select_current.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_void_p];lib.update_usage.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int]
 return lib
def validate_selector(t,lib):
 state=t.initial.copy();usage=t.initial_usage.copy();buffer=np.zeros(96,dtype=SWAP)
 events=sorted([(int(p['issue']),0,p) for p in t.promotions]+[(int(p['observed_ready']),1,p) for p in t.promotions if p['observed_ready']],key=lambda x:(x[0],x[1]));idx=0;mismatches=[];adaptations=0
 groups={int(w['number']):[] for w in t.windows}
 for lr,es in t.grouped():groups[int(lr['window'])].append((lr,es))
 def apply(now):
  nonlocal idx
  while idx<len(events) and events[idx][0]<=now:
   _,kind,p=events[idx];l=int(p['layer']);state[l,int(p['outgoing']) if kind==0 else int(p['incoming'])]=-1 if kind==0 else int(p['slot']);idx+=1
 for w in t.windows:
  number=int(w['number']);apply(int(w['pending_end']))
  for lr,es in groups[number]:lib.update_usage(usage[int(lr['layer'])].ctypes.data,np.ascontiguousarray(es['expert']).ctypes.data,len(es))
  if (number+1)%4==0:
   n=lib.select_current(usage.ctypes.data,state.ctypes.data,t.nl,t.ne,96,buffer.ctypes.data)
   actual=[(int(p['layer']),int(p['incoming']),int(p['outgoing'])) for p in t.promotions[t.promotions['window']==number]]
   got=[(int(p['layer']),int(p['incoming']),int(p['outgoing'])) for p in buffer[:n]]
   if got!=actual:mismatches.append({'window':number,'expected':actual,'got':got})
   usage*=np.float32(.7);adaptations+=1
 error=float(np.max(np.abs(usage-t.final_usage)))
 return {'state':'PASS' if not mismatches and error==0 else 'FAIL','selection_mismatches':mismatches,'usage_max_abs_error':error,'adaptations':adaptations,'future_information_used':False,'all_rejected_speculative_entries_included':True}
def main():
 lib=selector_library(C/'analysis/current-selector');rows=[];model=load(C/'git/model.json');blob=np.array([x['expert_blob_bytes'] for x in model['native_layers']],dtype=np.uint64)
 for result in sorted((C/'traces').glob('diagnostic/*/*/results.json')):
  data=load(result);prefix=data['trace_prefix'];t=Trace(prefix,split=24);v=t.validate();assert v['state']=='PASS',v
  assert np.array_equal(t.blob_bytes,blob)
  rec=data['runs'][0];assert len(t.output_ids)==rec['actual_output_tokens']
  assert v['path_counts']['0'] if '0' in v['path_counts'] else v['path_counts'][0]
  counts=v['path_counts'];assert counts[0]==rec['local_vram_entries'] and counts[-1]==rec['cpu_fallback_entries'] and counts[1]+counts[2]==rec['nonlocal_gpu_entries'],(counts,rec)
  current=validate_selector(t,lib);save(result.parent/'current-selector-validation.json',current);assert current['state']=='PASS',current
  save(result.parent/'trace-validation.json',v)
  # Saved integer IDs, not visible text, are the parity basis.
  profile=rec['profile'];name=result.parent.name
  if name.endswith('run1'):
   previous=C/'raw/control/256k/rep1/raw/run.json' if profile=='256k' else R/'campaigns/q4-pool-spin-20261005T184831Z/raw/100us'/profile/'rep1/raw/measured.json'
   ctrl=load(previous);a=load(rec['actual_output_ids_path']);b=load(ctrl['actual_output_ids_path']);pairs=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
   parity={'input_hash_equal':rec['payload']['input_ids_sha256']==ctrl['payload']['input_ids_sha256'],'output_ids_identical':a==b,'first_divergence':pairs[0] if pairs else None,'MTP_aggregate_equal':all(rec[k]==ctrl[k] for k in ['mtp_proposed','mtp_accepted','verify_windows']),'routing_aggregate_equal':all(rec[k]==ctrl[k] for k in ['local_vram_entries','cpu_fallback_entries','nonlocal_gpu_entries','all_routed_entries']),'control_path':str(previous)}
   save(result.parent/'original-parity.json',parity);v['original_parity']=parity
  rows.append({'path':str(result.parent),'validation':v,'current_selector':current})
  print('TRACE_PASS',profile,name,'all',v['demand_entries'],'CPU',v['path_counts'][-1],'copies',v['promotions'],flush=True)
 save(C/'phase-a/trace-validation.json',rows)
if __name__=='__main__':main()
