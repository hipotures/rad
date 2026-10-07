"""Replay trace public/private slot integrity checked independently from replay implementation."""
from lab import ROOT,load,save
from trace_reader import Trace
import numpy as np
base=ROOT/'experiments/E028-persistent-replay';checks=[]
for profile in ['32k','128k']:
 t=Trace(base/f'signal-v1/{profile}/traces/runtime-request2');r=load(base/f'v2-replay/{profile}-1.8.json');state=t.initial.copy();events=[]
 for i,p in enumerate(r['promotions']):
  events.append((p['issue'],0,i))
  if p['published'] is not None:events.append((p['published'],1,i))
 events.sort();reserved={};seen=set();peak=[0,0]
 for _,kind,i in events:
  p=r['promotions'][i];gpu=int(p['layer']>=25);key=(gpu,p['slot']);assert p['bytes']<=int(t.slot_bytes[gpu][p['slot']]);assert gpu==int(p['outgoing_layer']>=25)
  if not kind:
   assert state[p['outgoing_layer'],p['outgoing']]==p['slot'] and state[p['layer'],p['incoming']]<0 and key not in reserved
   state[p['outgoing_layer'],p['outgoing']]=-1;reserved[key]=i
  else:
   assert reserved.pop(key)==i and state[p['layer'],p['incoming']]<0 and p['published']>=p['ready']
   assert not np.any(state[0:25] == p['slot']) if gpu==0 else not np.any(state[25:48] == p['slot'])
   state[p['layer'],p['incoming']]=p['slot']
  for g,(lo,hi) in enumerate([(0,25),(25,48)]):
   entries=state[lo:hi];resident=entries[entries>=0];assert len(resident)==len(set(resident));used=set(int(x) for x in resident);pending={slot for device,slot in reserved if device==g};assert not used&pending
   peak[g]=max(peak[g],len(used)+len(pending));assert len(used)+len(pending)<=len(t.slot_bytes[g])
 checks.append({'profile':profile,'state':'PASS','promotions':len(r['promotions']),'peak_reserved_plus_resident_slots':peak,'allocated_slots':[len(x) for x in t.slot_bytes],'unpublished_end':len(reserved),'publication_after_complete':True,'same_owner_physical_fit':True,'unique_slot_identity':True})
save(base/'independent-capacity-audit.json',{'state':'PASS','checks':checks});print(checks)
