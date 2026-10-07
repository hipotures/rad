"""Reason evidence: never assign new-run truth to unmatched historical actions."""
from pathlib import Path
from collections import Counter
import json,hashlib,numpy as np
from campaign import C,V,load,save
D=np.dtype([('window','<i4'),('layer','<i4'),('n','<i4'),('reserved','<i4'),('ids','<i4',(40,)),('slots','<i4',(40,))])
CH=np.dtype([(k,'<i4') for k in ('window','layer','expert','old_slot','new_slot')])
assert D.itemsize==336 and CH.itemsize==20
def rows(path):return [json.loads(x) for x in Path(path).read_text().splitlines() if x]
def analyze(prefix):
 events=rows(str(prefix)+'.jsonl');demands=np.fromfile(str(prefix)+'-demand.bin',D);changes=np.fromfile(str(prefix)+'-native-changes.bin',CH)
 windows=int(demands['window'].max())+1;counts=Counter(e['classification'] for e in events);reason=[]
 for k,n in sorted(counts.items()):reason.append({'reason':k,'count':n,'bytes':n*3072000,'GB':n*3072000/1e9,'percent_issued':100*n/len(events)})
 total=local=cpu=mapped=0
 for d in demands:
  ids=d['ids'][:d['n']];slots=d['slots'][:d['n']];missing=[]
  for e,s in zip(ids,slots):
   if s<0 and int(e) not in missing:missing.append(int(e))
  nm=len(missing)*72//256;mapped_set=set(missing[-nm:]) if nm else set();local+=int((slots>=0).sum());mapped+=sum(int(e) in mapped_set for e,s in zip(ids,slots) if s<0);cpu+=sum(int(e) not in mapped_set for e,s in zip(ids,slots) if s<0);total+=len(ids)
 out={'events':len(events),'windows':windows,'reason_counts':reason,'copied_GB':len(events)*.003072,'published':counts['target-ready-persistent'],'unpublished_GB':(len(events)-counts['target-ready-persistent'])*.003072,'censored_action_count':sum(e['right_censored'] for e in events),'demand':{'local':local,'CPU':cpu,'mapped':mapped,'nonlocal':cpu+mapped,'all':total},'native_state_changes':len(changes),'schema':{'demand_bytes':D.itemsize,'change_bytes':CH.itemsize,'feature_count':48}}
 return out
def main():
 path=C/'traces/reason-v1/32k/32k-run1';prefix=path/'events-request2';assert (path/'results.json').exists()
 new=analyze(prefix);rec=load(path/'raw/run.json');assert new['demand']['local']==rec['local_vram_entries'] and new['demand']['CPU']==rec['cpu_fallback_entries'] and new['demand']['mapped']==rec['nonlocal_gpu_entries'],(new['demand'],rec)
 oldpath=V/'diagnostics/early-diagnostic/32k';old=rows(oldpath/'early-events-request2.jsonl');now=rows(str(prefix)+'.jsonl');oldrec=load(oldpath/'raw/run.json')
 equal={'same_input':rec['actual_engine_input']==oldrec['actual_engine_input'],'same_output':rec['actual_output_ids_sha256']==oldrec['actual_output_ids_sha256'],'same_actions':[(e['window'],e['layer'],e['incoming'],e['published_ns']>0) for e in old]==[(e['window'],e['layer'],e['incoming'],e['published_ns']>0) for e in now],'counter_parity':{k:rec[k]==oldrec[k] for k in ('mtp_proposed','mtp_accepted','verify_windows','local_vram_entries','cpu_fallback_entries','nonlocal_gpu_entries')}}
 oldcounts=Counter(e['classification'] for e in old);new_bykey={(e['window'],e['layer'],e['incoming']):e for e in now};matched=Counter();unmatched=0
 for e in old:
  if e['classification']!='wrong-or-superseded':continue
  k=e['window'],e['layer'],e['incoming'];n=new_bykey.get(k)
  if n:matched[n['classification']]+=1
  else:unmatched+=1
 output={'historical':{'issued':len(old),'counts':dict(oldcounts),'ambiguous_wrong_count':oldcounts['wrong-or-superseded'],'ambiguous_wrong_GB':oldcounts['wrong-or-superseded']*.003072,'cannot_infer_historical_reasons_without_matching_trace':True},'new_diagnostic':new,'parity':equal,'historical_action_key_match_descriptive':dict(matched),'unmatched_historical_wrong':unmatched,'causal_code_audit':{'superseded_by_new_prediction':'Impossible once issued: one immutable Worker target/incoming until retirement/publication; newer predictions see busy and do not displace it.','duplicate_or_inflight':'Worker state check prevents an issued duplicate; busy proposals counted separately.','victim_became_protected':'No victim reserved at enqueue in v2; victim chosen at actual target while current routed IDs excluded. No-safe-victim is explicit. Future victim demand can still cause damage.','state_generation_mismatch':'No generation-mismatch branch in this scheduler; planner owns host residency, publication guarded before target plan.','became_resident':'Explicit target host_res check; native adaptive jobs are applied between windows, not competing host cache loads between an H4 origin and target.','deadline_missed':'Worker state != ready at intended target; separate late reason.','prediction_wrong':'Complete ready copy, but incoming absent among all actual target routed branch IDs.','right_censored':'Intended-target unobserved or last4windows future reuse censored; do not relabel all unpublished near end as established waste.'},'limitations':['Matching action keys are descriptive if output trajectory/actions differ; never transfer new labels into historical4996 as exact truth.','Diagnostic buffered feature/demand work may alter copy timing; excluded from speed claims.']}
 save(C/'phase-a/summary.json',output)
 text='# Phase A — wrong/superseded decomposition\n\nHistorical aggregate retains4996 ambiguous events (15.347712GB), plus4late (0.012288GB). Exact historical target IDs were not logged. New diagnostic separates the guard without algorithm changes.\n\n'
 text+='|Reason|Count|GB|% issued|\n|---|---:|---:|---:|\n'+''.join(f"|{r['reason']}|{r['count']}|{r['GB']:.6f}|{r['percent_issued']:.3f}|\n" for r in new['reason_counts'])
 text+='\nParity and causality:\n```json\n'+json.dumps(equal,indent=2)+'\n```\n\nOnly if all parity/actions match can newly logged guard reasons explain the historical4996 one-for-one. Otherwise key matches are descriptive and unmatched historical causes remain unavailable. Both new count/byte denominators include published actions; all staged experts have the same3.072MBclass. Near-end future labels are censored. No source/model/control mutation.\n'
 (C/'phase-a/report.md').write_text(text);print('PHASE_A',json.dumps(new),'PARITY',equal,flush=True)
if __name__=='__main__':main()
