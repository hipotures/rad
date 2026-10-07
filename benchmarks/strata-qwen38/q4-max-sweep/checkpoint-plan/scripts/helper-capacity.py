#!/usr/bin/env python3
"""Finish remote sweep with actual native per-pair sizes, without changing profile."""
import json,struct,subprocess
from pathlib import Path
import run as r
import topology as t

def main():
 done=r.ROOT/'raw/remote-native-capacity-selection.json'
 if done.exists():return
 selection=json.loads((r.ROOT/'raw/topology-selection.json').read_text())
 startup_paths=sorted((r.ROOT/'raw').glob('T4-*-startup.json'))
 assert startup_paths,'No helper startup succeeded; inspect unsupported/failure evidence instead of expanding'
 startup=json.loads(startup_paths[0].read_text())['metrics']['engine'];primary=startup['expert_slots_primary']
 blob=Path('/srv/ai/strata/data/expert-profile.bin').read_bytes();assert blob[:4]==b'STRP'
 ver,nl,ne,slots,n=struct.unpack_from('<5I',blob,4);assert (nl,ne)==(48,512)
 pairs=[struct.unpack_from('<HH',blob,24+4*i) for i in range(n)]
 sizes={}
 for line in Path('/srv/ai/models/strata/packs/ud-q4_k_xl/native_experts.txt').read_text().splitlines():
  if line and not line.startswith('#'):
   parts=line.split();sizes[int(parts[0])]=(int(parts[4])+255)//256*256
 free=int(subprocess.check_output(['nvidia-smi','--id=1','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).strip())*1024**2
 budget=free-2*1024**3;used=0;capacity=0
 for layer,expert in pairs[primary:]:
  if used+sizes[layer]>budget:break
  used+=sizes[layer];capacity+=1
 assert capacity>0
 values=list(dict.fromkeys([capacity,int(capacity*.9),int(capacity*.75),int(capacity*.5)]))
 evidence={'GPU1_free_bytes':free,'GPU1_budget_bytes':budget,'GPU1_reserved_bytes':2*1024**3,'GPU0_profile_prefix_slots':primary,'GPU0_prefix_runtime_evidence':str(startup_paths[0]),'native_remote_max_safe_slots':capacity,'native_prefix_bytes_at_max':used,'candidate_slots':values,'note':'Original max_blob bound was conservative. This refinement sums exact256-aligned native layer blobs for the remaining unchanged shipped profile prefix, matching RemoteExperts::open. No private profile or weights are produced.'}
 r.c.save(r.ROOT/'raw/remote-native-capacity.json',evidence)
 helpers=[x for x in selection['screened_and_confirmed'] if x['candidate'].startswith('T4-') and not x['candidate'].endswith('-confirm')];added=[]
 for placement in ['stripe','layer']:
  for N in values:
   label=f'T4-{placement}-{N}'
   cfg=r.config(label,'helper',expert_cache_device1=N,expert_cache_remote_placement=placement)
   rec=r.candidate(label,cfg,1)
   if not any(x['candidate']==label for x in helpers):helpers.append(rec);added.append(rec)
 # One targeted static helper check: upstream adaptive candidates do not exclude pairs held on helper.
 # No Cartesian product: only max native-safe capacity, one placement (same algorithm with one helper).
 label=f'T4-stripe-{capacity}-static';cfg=r.config(label,'helper',expert_cache_device1=capacity,expert_cache_remote_placement='stripe',adapt_every=0)
 rec=r.candidate(label,cfg,1);helpers.append(rec);added.append(rec)
 for item in t.top(helpers,2):
  label=item['candidate']+'-confirm';cfg=t.clone(label,item['candidate']);rec=r.candidate(label,cfg,3,True)
  if not any(x['candidate']==label for x in selection['screened_and_confirmed']):added.append(rec)
 allrows=selection['screened_and_confirmed']+added
 selection.update(screened_and_confirmed=allrows,ranking=t.top(allrows,len(allrows)),native_remote_capacity=evidence)
 r.c.save(r.ROOT/'raw/topology-selection.json',selection)
 r.c.save(done,{'status':'OK','evidence':evidence,'added':added,'top2_screen':t.top(helpers,2)})
if __name__=='__main__':main()
