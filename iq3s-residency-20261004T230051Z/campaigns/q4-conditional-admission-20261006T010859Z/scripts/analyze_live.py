"""Derive every runtime headline from preserved requests/logs/1Hz telemetry."""
from campaign import C,load,save
from live_matrix import parse_summary
from pathlib import Path
import statistics as st,datetime,csv,json,re

def extent(xs):
 xs=[x for x in xs if x is not None]
 return {'min':min(xs),'median':st.median(xs),'max':max(xs)} if xs else None

def phase_hardware(path,r):
 rows=[json.loads(x) for x in (path/'telemetry/run.jsonl').read_text().splitlines()]
 start=r['started_epoch']; first=start+r['TTFT_s']; end=start+r['wall_s'];out={}
 for phase,a,b in [('prefill',start,first),('decode',first,end)]:
  rs=[x for x in rows if a<=x['wall_time']<=b]
  def mean(xs):return st.mean(xs) if xs else None
  d={'samples':len(rs),'system_CPU_pct':mean([x['system_cpu_pct'] for x in rs]),'process_CPU_pct':mean([sum(p['cpu_pct'] for p in x['processes']) for x in rs]),'RAM_used_GiB_peak':max([x['ram_used_gib'] for x in rs],default=None),'RSS_sum_GiB_peak':max([sum(p['rss_gib'] for p in x['processes']) for x in rs],default=None),'MemAvailable_GiB_min':min([x['mem_available_gib'] for x in rs],default=None)}
  for i in (0,1):
   gs=[g for x in rs for g in x.get('gpus',[]) if g['index']==i]
   d[f'GPU{i}_util_pct']=mean([g['util_pct'] for g in gs]);d[f'GPU{i}_power_W']=mean([g['power_w'] for g in gs]);d[f'GPU{i}_VRAM_MiB_peak']=max([g['vram_mib'] for g in gs],default=None)
  pci={0:[],1:[]}
  for line in (path/'telemetry/pcie-dmon.log').read_text().splitlines():
   parts=line.split()
   if len(parts)!=5 or parts[0].startswith('#'):continue
   try:
    t=datetime.datetime.strptime(' '.join(parts[:2]),'%Y%m%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc).timestamp();i=int(parts[2]);rx,tx=map(float,parts[3:])
   except ValueError:continue
   if a<=t<=b:pci[i].append((rx,tx))
  for i,x in pci.items():
   d[f'GPU{i}_PCIe_RX_MBps']=mean([v[0] for v in x]);d[f'GPU{i}_PCIe_TX_MBps']=mean([v[1] for v in x]);d[f'GPU{i}_PCIe_RX_peak_MBps']=max([v[0] for v in x],default=None)
  out[phase]=d
 out['caveat']='1Hz aggregate sampled hardware; phase boundary is client first token; RSS sum may double-count shared mappings. PCIe includes all subsystems, not logical expert traffic.'
 return out

def record(path,variant,profile,rep):
 d=load(path/'results.json');r=d['runs'][0];warm=d['warmup'];assert warm['actual_output_tokens']==64 and warm['actual_input_tokens']==4096
 a=parse_summary(path/'raw/run-engine.log');early=a.get('Q4_EARLY',{});gate=a.get('Q4_CONDITIONAL',{});hardware=phase_hardware(path,r)
 out={k:r.get(k) for k in ['state','invalid_reasons','actual_input_tokens','actual_output_tokens','reuse','PP','TG','TTFT_s','wall_s','pp_s','decode_s','finish_reason','mtp_proposed','mtp_accepted','mtp_acceptance_pct','mtp_accepted_per_window','verify_windows','local_vram_entries','cpu_fallback_entries','nonlocal_gpu_entries','all_routed_entries','local_vram_share_all_pct','nonlocal_gpu_share_pct','actual_engine_input','actual_output_ids_path','actual_output_ids_sha256','source_sha','binary_sha256','application_status']}
 out.update(variant=variant,context=profile,replicate=rep,raw_result=str(path/'results.json'),request_hash=r['payload']['payload_sha256'],input_ID_hash=r['payload']['input_ids_sha256'],full_config=r['full_config'],hardware=hardware,admission=a,physical_cache=load(path/'raw/resource-check.json'))
 out['warmup']={k:warm.get(k) for k in ['actual_input_tokens','actual_output_tokens','actual_engine_input','actual_output_ids_path','actual_output_ids_sha256','mtp_proposed','mtp_accepted','verify_windows','reuse']}
 for field in ['issued','rejected_before_copy','published','unpublished_bytes','useful_local_entries','victim_absent_entries','right_censored','feature_ms','score_selection_ms','proposals']:
  out[field]=gate.get(field)
 out['copied_GB']=early.get('bytes',0)/1e9 if early else None;out['unpublished_GB']=gate['unpublished_bytes']/1e9 if 'unpublished_bytes' in gate else None
 out['feature_plus_gate_ms']=out['feature_ms']+out['score_selection_ms'] if out.get('feature_ms') is not None and out.get('score_selection_ms') is not None else None
 out['late']=early.get('late');out['prediction_wrong']=early.get('wrong');out['algorithm_tracker_ms']=early.get('scoring_ms')
 text=(path/'raw/run-engine.log').read_text();m=re.search(r'per layer-window: CPU experts ([\d.]+) \(([\d.]+) entries\), VRAM hits ([\d.]+), PCIe ([\d.]+)',text)
 out['reported_mean_layer_window']={'CPU_unique_expert_jobs_rounded':float(m[1]),'CPU_entries_rounded':float(m[2]),'VRAM_hits_rounded':float(m[3]),'PCIe_entries_rounded':float(m[4])} if m else None
 if m:out['approx_CPU_unique_jobs']=float(m[1])*48*r['verify_windows']
 out['CPU_job_estimate_caveat']='Rounded two-decimal mean times48layer windows. Exact CPU entries are separately counted; multiple branch entries can share one CPU expert job.'
 out['total_nonlocal_entries']=r['cpu_fallback_entries']+r['nonlocal_gpu_entries'] if r.get('cpu_fallback_entries') is not None and r.get('nonlocal_gpu_entries') is not None else None
 return out

def parity(a,b):
 x=load(a['actual_output_ids_path']);y=load(b['actual_output_ids_path']);div=next((i for i,(p,q) in enumerate(zip(x,y)) if p!=q),None)
 if div is None and len(x)!=len(y):div=min(len(x),len(y))
 return {'context':a['context'],'replicate':a['replicate'],'identical_input_ID_hash':a['input_ID_hash']==b['input_ID_hash'],'identical_actual_engine_input':a['actual_engine_input']==b['actual_engine_input'],'identical_output_IDs':x==y,'first_diverging_output_token':div,'MTP_same':all(a[k]==b[k] for k in ['mtp_proposed','mtp_accepted','verify_windows']),'warmup_same_output_IDs':load(a['warmup']['actual_output_ids_path'])==load(b['warmup']['actual_output_ids_path']),'warmup_same_actual_input':a['warmup']['actual_engine_input']==b['warmup']['actual_engine_input'],'TG_ratio':b['TG']/a['TG'],'wall_ratio':b['wall_s']/a['wall_s'],'PP_ratio':b['PP']/a['PP'],'CPU_entries_ratio':b['cpu_fallback_entries']/a['cpu_fallback_entries'],'nonlocal_entries_ratio':(b['cpu_fallback_entries']+b['nonlocal_gpu_entries'])/(a['cpu_fallback_entries']+a['nonlocal_gpu_entries'])}

def main():
 records=[]
 for variant in ['control','conditional']:
  for profile in ['32k','128k','256k']:
   for rep in (1,2,3):
    path=C/'raw'/variant/profile/f'rep{rep}'
    if (path/'results.json').exists():records.append(record(path,variant,profile,rep))
 cells=[];pairs=[]
 for profile in ['32k','128k','256k']:
  for variant in ['control','conditional']:
   rs=[r for r in records if r['context']==profile and r['variant']==variant and r['state']=='VALID'];d={'variant':variant,'context':profile,'valid_runs':len(rs),'raw_results':[r['raw_result'] for r in rs]}
   if not rs:continue
   for k in ['actual_input_tokens','PP','TG','TTFT_s','wall_s','local_vram_share_all_pct','cpu_fallback_entries','nonlocal_gpu_entries','total_nonlocal_entries','mtp_acceptance_pct','issued','rejected_before_copy','published','copied_GB','unpublished_GB','useful_local_entries','victim_absent_entries','late','prediction_wrong','right_censored','feature_ms','score_selection_ms','feature_plus_gate_ms','algorithm_tracker_ms']:d[k]=extent([r.get(k) for r in rs])
   d['decode_hardware']={k:extent([r['hardware']['decode'].get(k) for r in rs]) for k in rs[0]['hardware']['decode']};cells.append(d)
  for rep in (1,2,3):
   a=next((r for r in records if r['variant']=='control' and r['context']==profile and r['replicate']==rep),None);b=next((r for r in records if r['variant']=='conditional' and r['context']==profile and r['replicate']==rep),None)
   if a and b:pairs.append(parity(a,b))
 paired=[]
 for profile in ['32k','128k','256k']:
  ps=[r for r in pairs if r['context']==profile]
  if ps:paired.append({'context':profile,**{k:extent([p[k] for p in ps]) for k in ['TG_ratio','wall_ratio','PP_ratio','CPU_entries_ratio','nonlocal_entries_ratio']},'all_same_input':all(p['identical_actual_engine_input'] for p in ps),'same_outputs':sum(p['identical_output_IDs'] for p in ps),'pairs':len(ps)})
 save(C/'analysis/live-records.json',records);save(C/'analysis/live-pairs.json',pairs);save(C/'analysis/live-cells.json',cells);save(C/'analysis/live-paired-ratios.json',paired)
 save(C/'summary.json',{'phase_A':load(C/'phase-a/summary.json'),'phase_B':load(C/'phase-b/holdout-decision.json'),'live':{'complete':len(records)==18,'records':records,'cells':cells,'paired_ratios':paired,'trajectory':pairs},'recommendation':'PENDING until complete audit','warning':'Offline filtered fixed-native-schedule attribution cannot predict TG; no holdout retuning.'})
 cols=['variant','context','valid_runs','actual_input_tokens','PP','TG','TTFT_s','wall_s','local_vram_share_all_pct','cpu_fallback_entries','nonlocal_gpu_entries','issued','rejected_before_copy','copied_GB','unpublished_GB','published','victim_absent_entries','feature_ms','score_selection_ms']
 with (C/'summary.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
  for d in cells:w.writerow({k:d.get(k,{}).get('median') if isinstance(d.get(k),dict) else d.get(k) for k in cols})
 print('LIVE_ANALYSIS',len(records),'requests',json.dumps(paired),flush=True)
if __name__=='__main__':main()
