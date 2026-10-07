"""Phase0 descriptive traces and measured cost accounting; no predictor or policy fitting."""
import bisect,collections,csv,hashlib,json,math,pathlib,statistics,time,subprocess
import numpy as np
from legacy_tape import Tape
from validate_traces import L,N
C=pathlib.Path(__file__).resolve().parents[1]
def load(p):return json.loads(pathlib.Path(p).read_text())
def save(p,x):pathlib.Path(p).write_text(json.dumps(x,indent=2)+'\n')
def stats(x):
 x=np.asarray(x,dtype=float)
 return {'count':len(x),'min':float(x.min()),'median':float(np.median(x)),'mean':float(x.mean()),'max':float(x.max())} if len(x) else None
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True,timeout=8).strip(),'No heavy analysis during GPU inference'
manifest=load(C/'benchmark-manifest.json');summaries=[];freqs={};labels=[];scan=[]
for task in manifest['tasks']:
 p=C/'raw'/task['task_id'];ep=p/'episode.json'
 if not ep.exists():
  task.update(measurement_status='DEFERRED',defer_reason='Not recorded inside bounded queue/time/family limits',trace_type=None,trace_ready=False);continue
 episode=load(ep);validation=load(p/'validation.json') if (p/'validation.json').exists() else {};run=episode.get('run',{})
 task.update(measurement_status='MEASURED',measured_phase_times={k:episode.get(k) for k in ['startup_s','warmup_s','shutdown_s','total_operating_s']},measured_request=run,trace_type=validation.get('trace_type','INVALID_TRACE'),trace_ready=validation.get('state')=='PASS',trace_path=str(p/'tape.bin'),trace_hashes=validation.get('file_hashes'),validation_path=str(p/'validation.json'),validation_status=validation.get('state'),eligibility_reason=validation.get('errors',episode.get('error')))
 if validation.get('state')!='PASS':continue
 start=time.monotonic();t=Tape(p/'tape.bin');a=np.fromfile(p/'raw/native-layers.bin',L);n=np.fromfile(p/'raw/native-native.bin',N);h=np.zeros((48,512),dtype=np.int64);gap=[];distance=[];perexpert_gaps=collections.defaultdict(list);uses=collections.defaultdict(list);counts=collections.Counter();last=np.full((48,512),-1,dtype=np.int64)
 # Every row is a simultaneous routed batch. Endpoints do not impose lane order.
 for wi,w in enumerate(t.ws):
  T=int(w['T'])
  for l in range(48):
   ids=w['routes']['ids'][l,:10*T];h[l]+=np.bincount(ids,minlength=512);unique=np.unique(ids);previous=last[l,unique].copy()
   for e,prev in zip(unique,previous):
    e=int(e);uses[(l,e)].append(wi)
    if prev>=0:
     g=wi-int(prev);gap.append(g);perexpert_gaps[(l,e)].append(g);distance.append(int(np.count_nonzero(last[l]>prev)))
   last[l,unique]=wi
 mtph=np.zeros(512,dtype=np.int64)
 for w in t.ws:
  nd=int(w['draft_count']);mtph+=np.bincount(w['routes']['mtp_ids'][:nd].reshape(-1),minlength=512)
 burst=[]
 for x in perexpert_gaps.values():
  if len(x)>=2:
   mu=float(np.mean(x));sd=float(np.std(x));burst.append((sd-mu)/(sd+mu))
 for j,event in enumerate(n):
  l=int(event['layer']);victim=int(event['victim']);w=int(event['window']);u=uses.get((l,victim),[]);i=bisect.bisect_right(u,w);future=u[i] if i<len(u) else None;prior=u[i-1] if i else None
  labels.append({'task_id':task['task_id'],'native_event_id':j,'layer':l,'victim':victim,'incoming':int(event['incoming']),'eviction_after_main_window':w,'physical_issue_ns':int(event['issue_ns']),'physical_publication_ns':int(event['publish_ns']) or None,'expert_payload_bytes':int(event['bytes']),'causal_features':{'initial_heat':float(t.heat[l,victim]),'last_main_use_window_at_decision':prior,'prior_main_batches_with_use':i,'resident_slot_before_eviction':int(event['slot']),'current_usage_heat':None,'protection_queue_state':None},'labels':{'next_main_use_window':future,'eviction_to_first_return_windows':future-w if future is not None else None,'right_censored':future is None,'observation_end_window':len(t.ws)-1},'scope':'Observed demand return after actual native eviction; no counterfactual regret or performance claim'})
 paragraphs=pathlib.Path(run['text_path']).read_text().splitlines();nonempty=[x.strip() for x in paragraphs if len(x.strip())>60];rep=sum(v-1 for v in collections.Counter(nonempty).values() if v>1);tail=pathlib.Path(run['text_path']).read_text()[-300:]
 begin=run['first_monotonic'];end=run['end_monotonic'];telemetry=[loadline for x in (p/'telemetry/run.jsonl').read_text().splitlines() if (loadline:=json.loads(x))['monotonic']>=begin and loadline['monotonic']<=end]
 def mean_field(f):v=[f(r) for r in telemetry];v=[x for x in v if x is not None];return float(np.mean(v)) if v else None
 system={'decode_samples':len(telemetry),'CPU_pct':mean_field(lambda r:r.get('system_cpu_pct')),'steal_pct':mean_field(lambda r:r.get('cpu_times_percent',{}).get('steal')),'RAM_GiB':mean_field(lambda r:r.get('ram_used_gib')),'RSS_GiB':mean_field(lambda r:sum(q['rss_gib'] for q in r.get('processes',[]))),'swap_bytes':0 if pathlib.Path('/proc/swaps').read_text().count('\n')==1 else None,'swap_evidence':'Guest has no swap device; heartbeat samples preserved','GPUs':{}}
 for d in [0,1]:
  gr=[g for row in telemetry for g in row.get('gpus',[]) if int(g['index'])==d];system['GPUs'][str(d)]={k:float(np.mean([g[k] for g in gr])) if gr else None for k in ['util_pct','power_w','vram_mib','sm_mhz','temperature_c']}
 row={'task_id':task['task_id'],'family':task['family'],'subtask':task['subtask'],'source_group':task['source_group'],'split':task['split'],'prior_exposure':task['prior_evaluation_exposure'],'context_limit':task['context_limit'],'actual_input_tokens':run['actual_input_tokens'],'output_tokens':run['output_tokens'],'stop_reason':run['stop_reason'],'startup_s':episode['startup_s'],'warmup_s':episode['warmup_s'],'prefill_s':run['prefill_s'],'decode_s':run['decode_s'],'request_wall_s':run['request_wall_s'],'trace_drain_s':run['trace_drain_s'],'shutdown_s':episode['shutdown_s'],'total_operating_s':episode['total_operating_s'],'PP':run['PP'],'TG':run['TG'],'TTFT_s':run['TTFT_s'],'windows':len(t.ws),'main_entries':int(h.sum()),'MTP_entries':int(mtph.sum()),'all_main_and_MTP_entries':int(h.sum()+mtph.sum()),'unique_layer_experts':int(np.count_nonzero(h)),'unique_MTP_experts':int(np.count_nonzero(mtph)),'local_pct':100*run['local_entries']/run['all_entries'],'cpu_pct':100*run['cpu_entries']/run['all_entries'],'mapped_pct':100*run['mapped_entries']/run['all_entries'],'native_admissions':len(n),'native_payload_bytes_issued':int(n['bytes'].sum()),'native_publications':int(np.count_nonzero(n['publish_ns'])),'copies_pending_at_record_end':int(np.count_nonzero(n['publish_ns']==0)),'gap_windows':stats(gap),'batch_distinct_expert_reuse_distance':stats(distance),'burstiness':stats(burst),'right_censored_expert_tails':len(uses),'source_groups':1,'trace_type':'FULL_REPLAY_TAPE','trace_validation':'PASS','trace_ready':True,'stored_tape_bytes':(p/'tape.bin').stat().st_size,'output_limit_incomplete_slice':run['stop_reason'] in ['OUTPUT_CAP','PLANNED_TIME_SLICE'],'short_output':run['output_tokens']<256,'repeated_long_output_lines':rep,'inspected_output_tail':tail,'system':system,'core':True,'screening':task['screening']}
 freqs[task['task_id']]=h;np.save(C/'analysis'/('frequency-'+task['task_id']+'.npy'),h);summaries.append(row);elapsed=time.monotonic()-start;scan.append({'task':task['task_id'],'read_histogram_reuse_labels_s':elapsed,'tape_bytes':row['stored_tape_bytes']});print('SCANNED',task['task_id'],'windows',len(t.ws),'elapsed',round(elapsed,3),flush=True)
sim=[]
for i,x in enumerate(summaries):
 for y in summaries[i+1:]:
  a=freqs[x['task_id']].reshape(-1).astype(float);b=freqs[y['task_id']].reshape(-1).astype(float);cos=float(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)));a/=a.sum();b/=b.sum();m=(a+b)/2
  js=0
  for v in [a,b]:mask=v>0;js+=float(np.sum(v[mask]*np.log2(v[mask]/m[mask])))/2
  sim.append({'task_A':x['task_id'],'task_B':y['task_id'],'same_family':x['family']==y['family'],'cosine_main_layer_expert_entry_histogram':cos,'JS_divergence_bits':js})
save(C/'analysis/trace-diversity.json',{'tasks':summaries,'similarity':sim,'definitions':{'cosine':'Cosine of flattened48x512 main token-expert-entry count histograms; layer-aware; includes rejected verifier lanes','JS':'Jensen-Shannon divergence,base2,between normalized main48x512 entry distributions;0same,1disjoint','inter_use_gap':'Difference in logical main verifier-window index between observed batched uses of one(layer,expert); within-batch order unspecified','distinct_reuse_distance':'Number of distinct experts routed in the same layer in intervening windows,excluding both endpoint batches; all lanes simultaneous','burstiness':'Per expert with at least2observed gaps,B=(sd(gaps)-mean(gaps))/(sd+mean); descriptive,finite/censored windows','denominator':'Normal main local+CPU+mapped entries; MTP entries retained separately','semantic_independence':'Declared from source provenance; no routing threshold used'},'caveats':['No candidate replacement policy tested; no family speedup claim','Finite traces are right-censored; each request stands alone','Native issue timestamp precedes immediate host victim removal; main window already consumed','Prefix-derived last-use counts are causal; next-use is labels only; dynamic heat/protection unknown']})
save(C/'analysis/victim-return-labels.json',{'namespace':'labels/evaluation only; never runtime features','records':labels,'right_censored':sum(x['labels']['right_censored'] for x in labels),'observed_returns':sum(not x['labels']['right_censored'] for x in labels),'no_counterfactual_regret':True})
save(C/'analysis/offline-scan-cost.json',{'operations':'Read existing tape, histogram, batch-aware reuse distances and native victim-return labels; no predictor training or policy evaluation','passes':1,'tasks':scan,'total_s':sum(x['read_histogram_reuse_labels_s'] for x in scan),'replay_policy_evaluation_cost':None,'replay_policy_evaluation_note':'Not measured in Phase0; use parser scan as measured data-preparation cost, not a policy execution estimate'})
manifest['status']='CALIBRATED';save(C/'benchmark-manifest.json',manifest)
fields=['task_id','family','subtask','source_group','split','prior_exposure','context_limit','actual_input_tokens','output_tokens','stop_reason','startup_s','warmup_s','prefill_s','decode_s','request_wall_s','trace_drain_s','shutdown_s','total_operating_s','PP','TG','TTFT_s','windows','main_entries','MTP_entries','all_main_and_MTP_entries','unique_layer_experts','local_pct','cpu_pct','mapped_pct','native_admissions','native_payload_bytes_issued','native_publications','trace_type','trace_validation','stored_tape_bytes','short_output','repeated_long_output_lines','core','screening']
with (C/'trace-summary.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r[k] for k in fields} for r in summaries)
print('ANALYZED',len(summaries),'tasks; no policy fit or oracle matrix')
