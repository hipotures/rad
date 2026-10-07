"""Decode progression from whole-window monotonic observations; never fabricate per-token timestamps."""
from pathlib import Path
import json,numpy as np,argparse
from tape import Tape
from inspect_oracle import L,E,N
C=Path(__file__).resolve().parents[1]
def analyze(label,tape):
 p=C/'raw'/label;t=Tape(tape);o=np.fromfile(p/'raw/observations.bin',t.obs_dtype);budget=int(t.h['output_budget']);bounds=[0]+[b for b in [512,1024,2048] if b<budget]+[budget];r=[]
 layer_path=p/'raw/oracle-layers.bin';layers=np.fromfile(layer_path,L) if layer_path.exists() else None
 ep=p/'raw/oracle-admissions.bin';events=np.fromfile(ep,E) if ep.exists() else None
 npth=p/'raw/oracle-native.bin';native=np.fromfile(npth,N) if npth.exists() else None
 # End time of the first completed window reaching each boundary; report actual emitted count.
 tokens=np.minimum(np.cumsum(t.ws['accepted']+1),int(t.h['output_budget']));start=o['begin_ns'][0];markers=[(-1,0,int(start))]
 for b in bounds[1:]:
  idx=int(np.searchsorted(tokens,b));markers.append((idx,int(tokens[idx]),int(o['end_ns'][idx])))
 for a,b in zip(markers,markers[1:]):
  i,j=a[0]+1,b[0]+1;seconds=(b[2]-a[2])/1e9;n=b[1]-a[1];r.append({'actual_output_start':a[1],'actual_output_end':b[1],'elapsed_s':seconds,'interval_equivalent_tok_s':n/seconds,'cumulative_equivalent_tok_s':b[1]/((b[2]-start)/1e9),'windows':j-i,'MTP_proposed':int(np.sum(t.ws['T'][i:j]-1)),'MTP_accepted':int(np.sum(t.ws['accepted'][i:j]))})
 for interval,(a,b) in zip(r,zip(markers,markers[1:])):
  i,j=a[0]+1,b[0]+1
  if layers is not None:
   ll=layers[i*48:j*48];mask=np.arange(40)[None,:]<ll['n'][:,None];total=int(ll['n'].sum());local=int(np.count_nonzero((ll['slots']>=0)&mask));cpu=int(np.count_nonzero((ll['path']==-1)&mask));mapped=int(np.count_nonzero((ll['path']==1)&mask));interval.update(main_routed_entries=total,local_entries=local,CPU_entries=cpu,mapped_entries=mapped,local_pct=100*local/total)
  if events is not None:
   ee=events[(events['trigger']>=i*48)&(events['trigger']<j*48)];interval.update(oracle_copies_issued=len(ee),oracle_issued_GB=int(ee['bytes'].sum())/1e9)
  if native is not None:
   nn=native[(native['window']>=i)&(native['window']<j)];interval.update(native_copies_issued=len(nn),native_issued_GB=int(nn['bytes'].sum())/1e9)
  interval['MTP_acceptance_pct']=100*interval['MTP_accepted']/interval['MTP_proposed'] if interval['MTP_proposed'] else None
 out={'label':label,'intervals':r,'resolution':'whole verifier-window completion, boundary overshoot retained; includes main and actual draft/adaptation within window plus between-window work','first_last_observation_s':(int(o['end_ns'][-1])-int(start))/1e9,'request_decode_s':json.loads((p/'results.json').read_text())['runs'][0]['decode_s']}
 (C/'analysis'/f'{label}-progression.json').write_text(json.dumps(out,indent=2)+'\n');return out
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('label');a.add_argument('tape');v=a.parse_args();print(json.dumps(analyze(v.label,v.tape),indent=2))
