"""Diagnostic contiguous-residency attribution, never hypothetical TG."""
from campaign import C,load,save
from decompose import D,CH,rows,analyze
from live_matrix import parse_summary
from pathlib import Path
import numpy as np,collections,json
def trace(path):
 prefix=path/'events-request2';events=rows(str(prefix)+'.jsonl');ds=np.fromfile(str(prefix)+'-demand.bin',D);changes=np.fromfile(str(prefix)+'-native-changes.bin',CH);nw=int(ds['window'].max())+1
 demand={}
 for d in ds:
  if int(d['layer']) in (9,16,29,36,42):demand[int(d['window']),int(d['layer'])]=d
 touches={}
 for x in changes:touches.setdefault((int(x['layer']),int(x['expert'])),[]).append(int(x['window']))
 published_windows={}
 for idx,e in enumerate(events):
  if not e['published_ns']:continue
  l,inc,slot=e['layer'],e['incoming'],e['slot'];pub=None
  for w in range(e['window'],min(nw,e['window']+4)):
   d=demand[w,l];n=int(d['n'])
   if ((d['ids'][:n]==inc)&(d['slots'][:n]==slot)).any():pub=w;break
  assert pub is not None,e
  published_windows[idx]=pub
 # Another early admission can evict or readmit either pair member without
 # appearing in the native-change stream. Stop attribution at either kind
 # of subsequent touch, not only a native-cache update.
 early_touches={}
 for idx,w in published_windows.items():
  e=events[idx]
  for expert in (e['incoming'],e['victim']):
   early_touches.setdefault((e['layer'],expert),[]).append((w,idx))
 results=[]
 for idx,e in enumerate(events):
  if not e['published_ns']:continue
  l,inc,victim,slot=e['layer'],e['incoming'],e['victim'],e['slot'];pub=None
  # Reactive events are issued in the preceding window. Infer publication
  # window from first actual local incoming use in its dedicated copied slot.
  for w in range(e['window'],min(nw,e['window']+4)):
   d=demand[w,l];n=int(d['n']);match=(d['ids'][:n]==inc)&(d['slots'][:n]==slot)
   if match.any():pub=w;break
  assert pub is not None,e
  native_in=min([w for w in touches.get((l,inc),[]) if w>pub],default=nw)
  native_victim=min([w for w in touches.get((l,victim),[]) if w>pub],default=nw)
  early_in=min([w for w,other in early_touches.get((l,inc),[]) if other!=idx and w>pub],default=nw)
  early_victim=min([w for w,other in early_touches.get((l,victim),[]) if other!=idx and w>pub],default=nw)
  end_in=min(native_in,early_in);end_victim=min(native_victim,early_victim)
  used_at_target=0;later=0;absent=0
  for w in range(pub,max(end_in,end_victim)):
   d=demand[w,l];n=int(d['n']);ids,slots=d['ids'][:n],d['slots'][:n]
   if w<end_in:
    count=int(((ids==inc)&(slots>=0)).sum())
    if w==pub:used_at_target=count
    else:later+=count
   if w<end_victim:absent+=int(((ids==victim)&(slots<0)).sum())
  results.append({'issued_window':e['window'],'published_window':pub,'layer':l,'incoming':inc,'victim':victim,'proposed_victim':e['proposed_victim'],'victim_changed':e['proposed_victim']!=victim,'target_entries':used_at_target,'later_entries_contiguous':later,'victim_absent_contiguous':absent,'incoming_attribution_end_window':end_in,'victim_attribution_end_window':end_victim,'incoming_first_native_touch_window':native_in,'victim_first_native_touch_window':native_victim,'incoming_first_other_early_touch_window':early_in,'victim_first_other_early_touch_window':early_victim,'request_end_future_censored':nw-pub<=4})
 log=path/'raw/run-engine.log';summary=parse_summary(log);early=summary.get('Q4_EARLY',{});gate=summary.get('Q4_CONDITIONAL',{});count=collections.Counter(e['classification'] for e in events)
 funnel={'H4_or_reactive_eligible_candidates':gate.get('proposals'),'passes_gate':gate.get('issued',len(events)),'rejected_before_copy':gate.get('rejected_before_copy'),'copy_issued':len(events),'copy_completed':sum(e['copy_end_ns']>0 for e in events),'published':len(results),'used_at_target':sum(e['target_entries']>0 for e in results),'reused_in_later_window_contiguous':sum(e['later_entries_contiguous']>0 for e in results),'target_local_entries':sum(e['target_entries'] for e in results),'later_local_entries_contiguous':sum(e['later_entries_contiguous'] for e in results),'victim_absent_contiguous':sum(e['victim_absent_contiguous'] for e in results),'prospective_victim_changed_at_target':sum(e['victim_changed'] for e in results),'staged_GB':len(events)*.003072,'published_GB':len(results)*.003072,'unpublished_GB':(len(events)-len(results))*.003072,'wrong_reason_counts':dict(count),'aggregate_counters':summary}
 return {'path':str(path),'actual_demand':analyze(prefix)['demand'],'funnel':funnel,'publications':results,'caveats':['Native-change samples are joined window boundaries; source audit forbids competing native host-residency updates between origin/target.','Contiguous counted demand stops at the first native touch or another early publication touching that expert; subsequent readmission is not credited as exclusive original reuse.','Victim-absent observations do not prove additional nonlocal work versus an alternate adaptive schedule.','No hypothetical TG; diagnostic readbacks/full trace excluded from speed.']}
def main():
 paths={'H4-unfiltered':C/'traces/reason-v1/32k/32k-run1','reactive-only':C/'diagnostics/reactive-only/32k','conditional':C/'diagnostics/conditional/32k'};out={k:trace(p) for k,p in paths.items()};save(C/'analysis/diagnostic-ablations.json',out)
 for k,x in out.items():print('ABLATION_FUNNEL',k,json.dumps(x['funnel']),flush=True)
if __name__=='__main__':main()
