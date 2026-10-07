"""Deduplicate actual target demands, distinguishing ready publication from actual service."""
import numpy as np,json,argparse,collections,bisect
from pathlib import Path
from inspect_oracle import E,L
C=Path(__file__).resolve().parents[1]
def analyze(label):
 p=C/'raw'/label;es=np.fromfile(p/'raw/oracle-admissions.bin',E);ls=np.fromfile(p/'raw/oracle-layers.bin',L);groups=collections.defaultdict(list)
 for i,e in enumerate(es):groups[int(e['target']),int(e['layer']),int(e['incoming'])].append(i)
 evictions=collections.defaultdict(list)
 for e in es:
  if e['publish_ns']:evictions[int(e['layer']),int(e['victim'])].append(int(e['publish_ns']))
 for values in evictions.values():values.sort()
 out={'label':label,'unique_target_expert_invocations':len(groups),'target_routed_entries':0,'target_local_entries':0,'target_CPU_entries':0,'target_mapped_entries':0,'target_nonlocal_entries':0,'same_admission_hit_entries':0,'publication_ready_but_absent_target_actions':0,'late_or_never_published_actions':0,'late_target_nonlocal_entries':0}
 for (target,layer,expert),indices in groups.items():
  r=ls[target];assert int(r['layer'])==layer;n=int(r['n']);mask=r['ids'][:n]==expert
  assert np.any(mask);local=mask&(r['slots'][:n]>=0);cpu=mask&(r['path'][:n]==-1);mapped=mask&(r['path'][:n]==1)
  out['target_routed_entries']+=int(mask.sum());out['target_local_entries']+=int(local.sum());out['target_CPU_entries']+=int(cpu.sum());out['target_mapped_entries']+=int(mapped.sum());out['target_nonlocal_entries']+=int(cpu.sum()+mapped.sum())
  any_same=np.zeros(n,bool);copy_late=False
  for i in indices:
   e=es[i];ends=evictions[layer,expert];j=bisect.bisect_right(ends,int(e['publish_ns']));end=ends[j] if j<len(ends) else 2**64-1
   matches=mask&(r['slots'][:n]==int(e['slot']))&bool(e['publish_ns'] and int(e['publish_ns'])<=int(r['plan_end'])<end)
   any_same|=matches
   copy_late|=bool(not e['copy_end'] or int(e['copy_end'])>int(r['plan_end']))
   out['publication_ready_but_absent_target_actions']+=bool(e['publish_ns'] and int(e['published_at'])<=target and not matches.any())
   out['late_or_never_published_actions']+=bool(not e['publish_ns'] or int(e['published_at'])>target)
  out['same_admission_hit_entries']+=int(any_same.sum())
  if copy_late:out['late_target_nonlocal_entries']+=int(cpu.sum()+mapped.sum())
 out['definition']='Targets deduplicated by logical event/layer/expert; route-lane multiplicity retained. Matching slot/publication within an unbroken admission lifetime proves observed service at target, not exclusive speed benefit. Published-before-target is separate from target-local availability. Late target nonlocal entries require both actual nonlocal service and unfinished copy at that target; publication/eviction failures are separate.'
 (C/'analysis'/f'{label}-target-readiness.json').write_text(json.dumps(out,indent=2)+'\n');return out
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('labels',nargs='+');v=a.parse_args()
 for name in v.labels:print(json.dumps(analyze(name)),flush=True)
