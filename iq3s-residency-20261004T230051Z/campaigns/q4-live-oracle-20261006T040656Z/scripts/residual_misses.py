"""Classify observed oracle nonlocal demand from logical ownership and copy records, without inventing unlogged selection reasons."""
from pathlib import Path
import json,re,collections,argparse,bisect,numpy as np
from inspect_oracle import L,E
C=Path(__file__).resolve().parents[1]
def analyze(label):
 p=C/'raw'/label;layers=np.fromfile(p/'raw/oracle-layers.bin',L);copies=np.fromfile(p/'raw/oracle-admissions.bin',E);log=(p/'raw/run-engine.log').read_text()
 initial={(int(l),int(e)) for l,e in re.findall(r'Q4_ORACLE_RESERVE device=\d+ class=\d+ bytes=\d+ slot=\d+ layer=(\d+) expert=(\d+)',log)}
 incoming=collections.defaultdict(list);victims=collections.defaultdict(list)
 for i,e in enumerate(copies):
  incoming[(int(e['layer']),int(e['incoming']))].append((int(e['trigger']),i))
  if e['publish_ns']:victims[(int(e['layer']),int(e['victim']))].append((int(e['published_at']),i))
 for d in [incoming,victims]:
  for x in d.values():x.sort()
 nmask=np.arange(40)[None,:]<layers['n'][:,None];ri,ji=np.where(nmask&(layers['slots']<0));counts=collections.Counter();paths=collections.defaultdict(collections.Counter);per_layer=collections.defaultdict(collections.Counter)
 for r,j in zip(ri,ji):
  a=layers[r];ev=int(a['event']);key=(int(a['layer']),int(a['ids'][j]));ins=incoming.get(key,[]);vs=victims.get(key,[]);ii=bisect.bisect_right(ins,(ev,2**63))-1;vi=bisect.bisect_right(vs,(ev,2**63))-1;ie=copies[ins[ii][1]] if ii>=0 else None;ve=copies[vs[vi][1]] if vi>=0 else None
  lastpub=int(ie['published_at']) if ie is not None and ie['publish_ns'] and ie['published_at']<=ev else -1
  if ve is not None and int(ve['published_at'])>=lastpub:reason='victim_absent'
  elif key in initial and lastpub<0:reason='initial_spare_donor_absent'
  elif ie is not None and (not ie['publish_ns'] or int(ie['published_at'])>ev):
   reason='copy_complete_not_published_at_demand' if ie['copy_end'] and int(ie['copy_end'])<=int(a['begin']) else 'copy_pending_at_demand'
  else:reason='no_observed_admission_before_demand'
  counts[reason]+=1;path='CPU' if int(a['path'][j])==-1 else 'mapped' if int(a['path'][j])==1 else 'other';paths[reason][path]+=1;per_layer[str(a['layer'])][reason]+=1
 out={'label':label,'nonlocal_entries':len(ri),'reasons':dict(counts),'execution_paths':{k:dict(v) for k,v in paths.items()},'by_layer':{k:dict(v) for k,v in per_layer.items()},'definition':'Mutually exclusive observed ownership/copy-state categories at actual logical demand. Victim category takes precedence; timestamps are host monotonic, not GPU DMA-only time.','unknown_selection_reason':'No-observed-admission does not distinguish worker busy, issue frontier/slack, victim safety or utility. Rejection counters were not exported; no fabricated causal reason.', 'not_expert_bytes':'Entry count is not physical read traffic; duplicates/grouping/caching matter.'}
 (C/'analysis'/f'{label}-residual-misses.json').write_text(json.dumps(out,indent=2)+'\n');print('RESIDUAL_MISS_AUDIT',label,out['nonlocal_entries'],out['reasons'],flush=True);return out
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('labels',nargs='+');v=a.parse_args()
 for label in v.labels:analyze(label)
