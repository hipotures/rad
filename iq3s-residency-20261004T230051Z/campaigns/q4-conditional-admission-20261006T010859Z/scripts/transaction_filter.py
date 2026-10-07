"""Finite-byte fixed-native-schedule attribution, not a counterfactual runtime oracle.

Filtering a ready observed publication preserves its victim and removes incoming
residency until the next original native/early transaction touches either expert.
Such native interaction ends attribution, rather than inventing an alternate
adaptive schedule. Every active pair is same-layer/same3.072MBclass and preserves
capacity. A conservative lost-use upper bound is reported separately.
"""
import numpy as np
from decompose import D,CH
def replay(prefix,events,keep,evaluation_windows=None):
 ds=np.fromfile(prefix+'-demand.bin',D);changes=np.fromfile(prefix+'-native-changes.bin',CH)
 if evaluation_windows is not None:ds=ds[ds['window']<evaluation_windows]
 native={};pubs={}
 for c in changes:native.setdefault(int(c['window']),[]).append(c)
 for i,e in enumerate(events):
  if e['published_ns']:pubs[e['window'],e['layer']]=(i,e)
 overlay={};pairs={};nextpair=0;touches=0;lost=0;saved=0;cpu=mapped=local=basecpu=basemapped=baselocal=0;victim_absent=0;initial_spare_damage=None
 def invalidate(key):
  nonlocal touches
  pid=overlay.get(key,(None,None))[0]
  if pid is not None:
   for ex in pairs.pop(pid):overlay.pop(ex,None)
   touches+=1
 lastwindow=-1
 for d in ds:
  w,l,n=int(d['window']),int(d['layer']),int(d['n'])
  if w!=lastwindow:
   for change in native.get(w,[]):invalidate((int(change['layer']),int(change['expert'])))
   lastwindow=w
  event=pubs.get((w,l))
  if event:
   i,e=event;invalidate((l,e['incoming']));invalidate((l,e['victim']))
   if not keep[i]:
    pid=nextpair;nextpair+=1;keys=[(l,e['incoming']),(l,e['victim'])];pairs[pid]=keys;overlay[keys[0]]=(pid,False);overlay[keys[1]]=(pid,True)
  ids=d['ids'][:n];actual=d['slots'][:n]>=0;candidate=actual.copy()
  for k,x in enumerate(ids):
   key=l,int(x)
   if key in overlay:candidate[k]=overlay[key][1]
  lost+=int(np.count_nonzero(actual&~candidate));saved+=int(np.count_nonzero(~actual&candidate))
  for flags,baseline in [(actual,True),(candidate,False)]:
   missing=[]
   for e,yes in zip(ids,flags):
    if not yes and int(e) not in missing:missing.append(int(e))
   nm=len(missing)*72//256;mapped_ids=set(missing[-nm:]) if nm else set();lc=int(flags.sum());mc=sum(int(x) in mapped_ids for x,yes in zip(ids,flags) if not yes);cc=n-lc-mc
   if baseline:baselocal+=lc;basemapped+=mc;basecpu+=cc
   else:local+=lc;mapped+=mc;cpu+=cc
 
 # Isolated recorded-victim attribution, not exclusive exposed latency.
 all_events=events;all_keep=keep
 if evaluation_windows is not None:
  mask=np.array([e['window']<evaluation_windows for e in events]);events=[e for e,m in zip(events,mask) if m];keep=keep[mask]
 keptpub=[e for e,k in zip(events,keep) if k and e['published_ns']]
 retained=sum(e['benefit_next4_label'] for e,k in zip(events,keep) if k)
 fullbenefit=sum(e['benefit_next4_label'] for e in events)
 counts={'evaluation_windows':evaluation_windows,'excluded_near_end_actions':len(all_events)-len(events),'baseline_unpublished_GB':sum(not e['published_ns'] for e in events)*.003072,'baseline_next4_benefit':fullbenefit,'baseline_observed_uses':sum(e['uses'] for e in events),'issued_copies':int(np.sum(keep)),'rejected_before_copy':int(np.sum(~keep)),'staged_GB':float(np.sum(keep)*.003072),
  'target_ready_publications':len(keptpub),'useful_publication_count_recall':len(keptpub)/max(1,sum(bool(e['published_ns']) for e in events)),
  'useful_next4_benefit_retained':retained,'useful_next4_benefit_recall':retained/max(1,fullbenefit),
  'unpublished_GB':sum(k and not e['published_ns'] for e,k in zip(events,keep))*.003072,
  'wrong_or_superseded':sum(k and e['classification'] in ('prediction-wrong','became-resident-before-publication') for e,k in zip(events,keep)),
  'late':sum(k and 'late' in e['classification'] for e,k in zip(events,keep)),
  'right_censored':sum(k and e['right_censored'] for e,k in zip(events,keep)),
  'useful_later_observed_uses_retained':sum(e['uses'] for e in keptpub),
  'victim_absent_entries_retained':sum(e['victim_entries'] for e in keptpub),
  'baseline_victim_absent_entries':sum(e['victim_entries'] for e in events),
  'original_nonlocal_entries':basecpu+basemapped,'nonlocal_entries_attributed':cpu+mapped,
  'original_CPU_entries':basecpu,'CPU_entries_attributed':cpu,'original_mapped_entries':basemapped,'mapped_entries_attributed':mapped,
  'local_entries_attributed':local,'lost_local_entries_attributed':lost,'saved_victim_entries_attributed':saved,
  'native_interaction_attribution_ends':touches,
  'conservative_lost_observed_use_upper':sum(e['uses'] for e,k in zip(events,keep) if not k and e['published_ns']),
  'modeled_copy_queue_ms':float(np.sum(keep)*(.293449+.25535)),
  'modeled_net_gain_vs_unfiltered_ms':float((sum(not k for k in keep)*(.293449+.25535))+(basecpu-cpu)*.25),
  'modeled_saved_exposed_ms':float((basecpu-cpu)*.25-(np.sum(keep)*(.293449+.25535))),
  'cost_parameters':{'CPU_entry_ms_proxy':.25,'Q4_staging_queue_ms_median':.293449,'Q4_H2D_ms_median':.25535,'publication_wait_ms_median':1.160335},
  'capacity':'Each attributed intervention exchanges one same-layer/same3.072MBexpert, within same-device fixed capacity. Initial two-spare withdrawals common and included in original paths.',
  'limitations':['Observed output/native transactions fixed; future adaptation and MTP trajectories not counterfactually replayed.',
   'Attribution ends on next native/early touch to either member, rather than inventing an alternate cache schedule.',
   'CPU/mapped planning recomputed from distinct routed order with frozen72/256; allocation/cost is not measured hypothetical latency.',
   '.25ms per-entry is an approximate prior utility proxy, not exclusive exposed latency; overlapping CPU work is not additive request time.',
   'Conservative lost-use bound can overcount unobserved native eviction/readmission in original event uses.',
   'Predictor timing measured separately; no simulated TG. Exact aggregate disk/PCIe attribution unavailable.']}
 return counts
