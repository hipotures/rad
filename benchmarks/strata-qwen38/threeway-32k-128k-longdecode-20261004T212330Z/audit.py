import json,hashlib,subprocess,re,time
from pathlib import Path
R=Path(__file__).resolve().parent
s=json.loads((R/'summary.json').read_text());cells=[c for c in s['cells'] if c['context'] in ['32K','128K']];rows=[a for a in s['runs'] if a['context_label'] in ['32K','128K']];checks={}
checks['six_primary_cells']=len(cells)==6;checks['exactly18_valid_primary']=len(rows)==18 and all(a['valid'] for a in rows)
checks['fixed4096_reuse0']=all(a['generated_tokens']==4096 and a['cache_reused_tokens']==0 and a['finish_reason']=='length' for a in rows)
checks['counts_close_to_targets']=all((31000<=a['actual_prompt_tokens']<=31600 if a['context_label']=='32K' else 126900<=a['actual_prompt_tokens']<=127100) for a in rows)
checks['three_per_cell']=all(c['valid_runs']==3 for c in cells)
checks['single_engine_generation_record']=all(len(re.findall(r'strata serve: prompt .*?4096 generated',Path(a['raw_path']).with_name(Path(a['raw_path']).stem+'-engine.log').read_text()))==1 for a in rows)
checks['payload_hashes']=all(a['payload_sha256']==hashlib.sha256(json.dumps(json.loads(Path(a['raw_path']).with_name(Path(a['raw_path']).stem+'-request.json').read_text()),sort_keys=True,separators=(',',':')).encode()).hexdigest() for a in rows)
checks['input_id_hashes_and_counts']=all(hashlib.sha256(Path(a['input_token_provenance']['token_ids_path']).read_bytes()).hexdigest()==a['input_token_provenance']['input_ids_sha256'] and len(json.loads(Path(a['input_token_provenance']['token_ids_path']).read_text()))==a['actual_prompt_tokens'] for a in rows)
warm=[]
for c in cells:
 label=c['config']+'-'+c['context'];a=json.loads((R/'raw'/f'{label}-warmup.json').read_text());warm.append(a)
checks['equal_fixed_warmup']=len({(a['actual_prompt_tokens'],a['generated_tokens'],a['payload_sha256'],a['input_token_provenance']['input_ids_sha256']) for a in warm})==1 and all(a['valid'] and a['actual_prompt_tokens']==4096 and a['generated_tokens']==64 and a['cache_reused_tokens']==0 for a in warm)
checks['lightweight_telemetry_present']=all(a.get('decode_telemetry_sample_count',0)>5 for a in rows)
checks['frozen_settings']=all(all(a['full_config']['args'][a['full_config']['args'].index(flag)+1]==val for flag,val in [('--spec','4'),('--spec-min-p','0.5'),('--kv','int8'),('--kv-resident','32768'),('--max-context','262144'),('--pool-workers','15'),('--suffix-draft','0'),('--prompt-cache','0'),('--prefill','auto')]) for a in rows)
checks['frozen_K']=all(a['full_config'].get('layer_split')=='25' for a in rows if a['variant']!='HELPER')
checks['preserved_binary_hashes']=all(hashlib.sha256(Path((c:=json.loads((R/'configs'/f'{name}.json').read_text()))['exe']).read_bytes()).hexdigest()==c['binary_sha256'] for name in ['CURRENT','HELPER','V0138'])
model=[]
for x in json.loads((R/'git/model-files-before.json').read_text()):
 p=Path(x['path']);st=p.stat();model.append({'path':str(p),'size':st.st_size,'mtime_ns':st.st_mtime_ns,'unchanged':st.st_size==x['size'] and st.st_mtime_ns==x['mtime_ns']})
checks['model_sizes_mtimes_unchanged']=all(x['unchanged'] for x in model);(R/'git/model-files-after.json').write_text(json.dumps(model,indent=2))
apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True);checks['GPUs_no_compute_processes']=not apps.strip()
processes=subprocess.check_output(['ps','-eo','pid,args'],text=True);live=[line for line in processes.splitlines() if re.search(r'/strata(?:-original)? --serve',line)];checks['no_Strata_engine']=not live
import psutil
owned_servers=[]
for proc in psutil.process_iter(['pid','cmdline']):
 cmd=proc.info.get('cmdline') or []
 if '-m' in cmd and 'serve.server' in cmd and any(str(R) in x for x in cmd):owned_servers.append(proc.info)
checks['no_benchmark_server']=not owned_servers
checks['no_periodic_PSS']=all('memory_full_info' not in body for body in [(R/'telemetry.py').read_text().split('class Sampler',1)[1]])
out={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'primary_valid_count':len(rows),'total_enriched_valid_count':len(s['runs']),'GPU_compute_apps':apps,'remaining_engine_processes':live,'time_UTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'limitations':['128K current API input IDs differ by official quoted-tag escaping; older/helper identical','Approximate1Hz progression; no in-request cache/MTP/miss identity counters','No valid16K median claimed if optional natural EOS occurs','No independent arena SSD-read counter; unavailable is not zero']}
(R/'audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['status']=='PASS'
