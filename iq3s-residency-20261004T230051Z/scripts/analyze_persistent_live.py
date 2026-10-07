"""Reproducible P2 aggregation; every fixed-length headline from preserved raw requests."""
import csv,json,statistics,pathlib,re,hashlib
from lab import ROOT,load,save
base=ROOT/'experiments/E029-persistent-runtime';cells=[];pairs=[]
def dist(v):
 v=[x for x in v if x is not None];return {'min':min(v),'median':statistics.median(v),'max':max(v)} if v else None
def augment(r):
 rows=[json.loads(x) for x in open(r['telemetry']['path'])];lo=r['started_epoch']+r['TTFT_s'];hi=r['started_epoch']+r['wall_s'];d=[x for x in rows if lo<=x['wall_time']<hi]
 def mean(v):return statistics.mean(v) if v else None
 r['CPU_VM_decode_mean_pct']=mean([x['system_cpu_pct'] for x in d]);r['CPU_process_decode_mean_pct']=mean([sum(y['cpu_pct'] for y in x['processes']) for x in d])
 for i in [0,1]:
  for name,key in [('util','util_pct'),('power','power_w')]:r[f'GPU{i}_{name}_decode_mean']=mean([g[key] for x in d for g in x.get('gpus',[]) if g['index']==i])
  r[f'GPU{i}_peak_VRAM_mib']=r['telemetry']['gpus'][str(i)]['peak_vram_mib']
 path=pathlib.Path(r['telemetry']['path']).parents[1]/'raw/run-engine.log';log=path.read_text();m=re.search(r'strata persistent: request=(\d+) (.+?); safe-boundary',log)
 if m:
  data={k:float(v) if '.' in v else int(v) for k,v in re.findall(r'(\w+)=([\d.]+)',m[2])};r['persistent_stats']=data
  for k,v in data.items():r['residency_'+k]=v
 r['all_nonlocal_entries']=r.get('cpu_fallback_entries',0)+r.get('offloaded_entries',0) if r.get('cpu_fallback_entries') is not None and r.get('offloaded_entries') is not None else None
 return r
keys=['PP','TG','TTFT_s','wall_s','actual_input_tokens','actual_output_tokens','mtp_proposed','mtp_accepted','mtp_acceptance_pct','mtp_accepted_per_window','verify_windows','hit_rate_pct','local_vram_entries','cpu_fallback_entries','offloaded_entries','all_nonlocal_entries','CPU_VM_decode_mean_pct','CPU_process_decode_mean_pct','GPU0_util_decode_mean','GPU1_util_decode_mean','GPU0_power_decode_mean','GPU1_power_decode_mean','GPU0_peak_VRAM_mib','GPU1_peak_VRAM_mib','residency_promotions','residency_bytes','residency_useful','residency_wasted','residency_repeated','residency_ready','residency_late','residency_unpublished','residency_useful_entries','residency_victim_entries','residency_prediction_entries','residency_selector_ms','residency_pending_ms']
for profile in ['32k','128k']:
 roles={}
 for role in ['off','on']:
  runs=[];paths=[]
  for rep in [1,2,3]:
   p=base/f'v2-fixed/final/{profile}/{role}/rep{rep}/raw/run.json'
   if not p.exists():continue
   r=augment(load(p));r['raw_path']=str(p);runs.append(r);paths.append(str(p))
  roles[role]=runs;valid=[r for r in runs if r['state']=='VALID' and r['actual_output_tokens']==4096]
  cells.append({'experiment':'E029-persistent-runtime','phase':'P2','family':'standard','profile':profile,'role':role,'attempts':len(runs),'valid_fixed_length':len(valid),'raw_paths':paths,'metrics':{k:dist([r.get(k) for r in valid]) for k in keys},'invalid':[r for r in runs if r not in valid],'source':runs[0]['source_sha'] if runs else None,'binary':runs[0]['binary_sha256'] if runs else None})
 for a,b in zip(roles['off'],roles['on']):
  def ids(r):return load(pathlib.Path(r['raw_path']).parent/'output-ids-request2.json')
  x,y=ids(a),ids(b);first=next((i for i,(u,v) in enumerate(zip(x,y)) if u!=v),min(len(x),len(y)) if x!=y else None)
  pairs.append({'profile':profile,'replicate':len([p for p in pairs if p['profile']==profile])+1,'same_binary':a['binary_sha256']==b['binary_sha256'],'same_input_IDs':a['payload']['input_ids_sha256']==b['payload']['input_ids_sha256'],'same_output_IDs':x==y,'first_diverging_token':first,'same_MTP':all(a.get(k)==b.get(k) for k in ['mtp_proposed','mtp_accepted','verify_windows']),'TG_delta_pct':100*(b['TG']/a['TG']-1),'wall_delta_pct':100*(b['wall_s']/a['wall_s']-1),'CPU_entries_delta':b['cpu_fallback_entries']-a['cpu_fallback_entries']})
complete=all(x['valid_fixed_length']==3 for x in cells)
r={'state':'COMPLETE_MEASUREMENTS' if complete else 'RUNNING','cells':cells,'paired':pairs,'limits':['Controlled input/settings/build; placement changes CPU/GPU rounding and free output/MTP trajectory. Do not interpret TGdelta as same-expert-trace causal kernel speed.','OFFguard vs originalP1 separate comparison; unchanged P1points not repeated.','PSSnot polled. CPU/GPU1Hz boundaries from clientTTFT, not submillisecond criticalpath identification.','Unavailable counters null, not zero. Final128KiQinput fits131072 including4096output+reserve.']};save(base/'summary.json',r)
with (base/'summary.csv').open('w') as f:
 rows=[]
 for c in cells:
  row={k:c[k] for k in ['profile','role','attempts','valid_fixed_length']};row.update({k+'_median':v['median'] if v else None for k,v in c['metrics'].items()});rows.append(row)
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
print(r['state'],len(pairs),'pairs',flush=True)
