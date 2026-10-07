"""Candidate-specific labels and causal history; future fields never in features."""
from pathlib import Path
import json,hashlib,numpy as np
from campaign import C,load,save
from decompose import D,CH,rows,analyze
NAMES=['h4_confidence','h4_share','h4_second_nonresident','h4_margin','h4_rank','verify_branches','predicted_unique',
 'incoming_recent1_log','incoming_recent4_log','incoming_recent16_log','incoming_recent64_log',
 'incoming_heat_log','incoming_fast_log','incoming_slow_log','incoming_frequency_log','incoming_age_log','incoming_seen',
 'incoming_CPU_history_log','incoming_mapped_history_log','incoming_initial_resident','incoming_resident_now',
 'worker_state','spare_available','layer','device','blob_class','incoming_v2_score_log','incoming_promotions_log','incoming_evictions_log',
 'victim_heat_log','victim_v2_score_log','victim_recent1_log','victim_recent4_log','victim_recent16_log','victim_recent64_log',
 'victim_age_log','victim_resident_age','victim_evictions_log','victim_recent_protection_proxy','has_victim','score_margin',
 'window_index','modeled_pinned_copy_ms','previous_Q4_staging_median_ms','router_horizon','previous_same_candidate_wrong16_log','previous_same_candidate_published16_log','previous_same_candidate_wrong1']
assert len(NAMES)==48
def episode(task):
 path=C/'traces/reason-v1/32k'/task;prefix=path/'events-request2';es=rows(str(prefix)+'.jsonl');ds=np.fromfile(str(prefix)+'-demand.bin',D)
 nw=int(ds['window'].max())+1;counts=np.zeros((nw,48,512),np.int32)
 for d in ds:np.add.at(counts[d['window'],d['layer']],d['ids'][:d['n']],1)
 previous={};features=[];labels=[];benefits=[];victims=[];censored=[]
 for e in es:
  w,l,inc=e['window'],e['layer'],e['incoming'];f=np.array(e['features'],float);prior=[p for p in previous.get((l,inc),[]) if p['window']<w and p['window']>=w-16]
  f[45]=np.log1p(sum(p['classification']=='prediction-wrong' for p in prior));f[46]=np.log1p(sum(p['published_ns']>0 for p in prior));f[47]=any(p['window']==w-1 and p['classification']=='prediction-wrong' for p in prior)
  previous.setdefault((l,inc),[]).append(e)
  # Publication truth and later benefit are labels only. Uniform bounded4window window
  # avoids ranking whole episodes by variable uncensored resident lifetimes.
  features.append(f);labels.append(e['published_ns']>0 and e['needed']==1)
  benefits.append(int(counts[w:min(nw,w+4),l,inc].sum()) if e['published_ns'] else 0)
  pv=e['proposed_victim'];victims.append(int(counts[w:min(nw,w+4),l,pv].sum()) if pv>=0 else 0)
  censored.append(w>=nw-4)
  e['benefit_next4_label']=benefits[-1];e['victim_next4_label']=victims[-1];e['causal_features']=f.tolist()
 x=np.asarray(features);y=np.asarray(labels);b=np.asarray(benefits);v=np.asarray(victims);valid=~np.asarray(censored)
 assert np.isfinite(x).all() and np.all(x[:,20]==0) and np.all(x[:,21]==0) and np.all(x[:,22]==1)
 result={'task':task,'prefix':str(prefix),'actions':len(es),'eligible_complete_labels':int(valid.sum()),'censored':int((~valid).sum()),'positive_labels':int(y[valid].sum()),'diagnostic':analyze(prefix),'input':load(path/'raw/run.json')['actual_engine_input'],'trace_hashes':{str(p.name):hashlib.sha256(p.read_bytes()).hexdigest() for p in prefix.parent.glob(prefix.name+'*') if p.is_file()}}
 return x,y,b,v,valid,es,result
def export():
 tasks=load(C/'datasets/tasks.json')['episodes'];manifest=[]
 for t in tasks:
  x,y,b,v,valid,es,meta=episode(t['id']);out=C/'datasets/episodes'/t['id'];out.mkdir(parents=True,exist_ok=False)
  np.savez_compressed(out/'candidate-actions.npz',X=x,y=y,benefit=b,victim_loss=v,valid=valid)
  save(out/'events-labeled.json',es);meta['role']=t['role'];meta['family']=t['family'];save(out/'manifest.json',meta);manifest.append(meta)
 save(C/'datasets/manifest.json',{'episodes':manifest,'features':NAMES,'split':load(C/'datasets/splits.json'),'label':'particular proposed H4 nonresident action yields ready target publication with actual target demand','benefit':'observed incoming demand in current+next3complete verifier windows; all routed branches','victim_loss':'prospective pre-enqueue victim demand current+next3windows (label only, not a proven exposed latency)','no_future_in_features':True,'availability_limits':['No exact GPU target-deadline or pending-native-copy counter. Native adapt is joined between windows.','Victim current target protection unknown before future router; recent1 is only a causal proxy.','Copy duration is measured Q4 prior, not per-action oracle.','Exact per-branch eventual MTP acceptance is unavailable before commit and never input.']})
 save(C/'datasets/features.json',{'names':NAMES,'source':'buffered snapshot at origin before enqueue plus completed prior-window outcomes only','omitted_reserved_fields':[45,46,47],'derived_previous_window_fields':[45,46,47],'normalization':'fit development tasks only','censoring':'Conservative final4windows excluded from model/threshold fit; not negative'})
 print('DATASET_COMPLETE',[(m['task'],m['actions'],m['positive_labels'] if m['role']!='holdout' else 'sealed holdout') for m in manifest],flush=True)
if __name__=='__main__':export()
