import run as r,json,time,hashlib,subprocess,importlib.util
from pathlib import Path
R=r.ROOT;label='Q5-PATCH-SMOKE';cfg=json.loads((R/'configs'/f'{label}.json').read_text());environment=json.loads((R/'environment.json').read_text());result={'status':'RUNNING','scope':'load/health + exactly one64output smoke; no benchmark','base_HEAD':r.HEAD,'build_variant':cfg['build_variant'],'local_patch_sha256':cfg['local_patch_sha256'],'measured_benchmark_requests':0}
def status(phase):r.c.save(R/'STATUS.json',{'status':'RUNNING','running':phase,'completed':['regression suite PASS','real Q5 header test PASS','CUDA build PASS'],'pending':['smoke'],'next_exact_action':phase})
try:
 assert Path(cfg['exe']).is_file();environment['finished_build']=True;environment['engine_SHA256']=hashlib.sha256(Path(cfg['exe']).read_bytes()).hexdigest();r.c.save(R/'environment.json',environment)
 assert r.c.psutil.virtual_memory().available/r.c.GIB>115,'Need91.6GiB arena plus24GiB margin'
 status('loading Q5')
 with r.Session(label,cfg) as s:
  result['health']=r.c.api('/health');status('64-token smoke')
  rec=s.request(8000,64,'smoke','smoke');result['smoke']=rec
  assert rec['status']=='OK' and rec['generated_tokens']==64 and rec['text'].strip() and rec['draft_tokens']>0 and rec['abort'] is None
  assert rec['cache_reused_tokens']==0 and rec['min_mem_available_gib']>=12
  result.update(status='PASS',health_READY=True,MTP_active=True,smoke_output_tokens=64)
 print('SMOKE PASS',rec['text'],flush=True)
except BaseException as e:
 result.update(status='FAIL_NEXT_BLOCKER',error=repr(e));print('STOP',repr(e),flush=True)
finally:
 # Session owns shutdown, including startup failures; no further model attempts.
 log=R/'logs'/f'{label}-engine.log';lines=log.read_text(errors='replace').splitlines() if log.exists() else [];result['engine_log_tail']=lines[-40:]
 result['relevant_engine_lines']=[x for x in lines if any(k in x.lower() for k in ['arena','cudahostregister','layer split','expert cache','error','unsupported','failed','unhandled','q5_k','q6_k','q8_0'])]
 checks=[]
 for x in environment['model_stat_before']:
  p=Path(x['path']);st=p.stat();checks.append(st.st_size==x['size'] and st.st_mtime_ns==x['mtime_ns'] and st.st_ino==x['inode'])
 result['model_stat_unchanged']=all(checks)
 result['clean_checkout_tracked_unchanged']=not subprocess.check_output(['git','diff','--name-only'],cwd=environment['clean_checkout'],text=True).strip()
 result['patch_unchanged']=hashlib.sha256((R/'metadata-only-gguf.patch').read_bytes()).hexdigest()==cfg['local_patch_sha256']
 result['GPU_compute_apps_after']=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'],text=True)
 r.c.save(R/'summary.json',result);r.c.save(R/'STATUS.json',{'status':result['status'],'running':None,'completed':['local patch','GGUF regression suite','real Q5 split headers','CUDA build','Q5 smoke attempted'],'pending':[],'next_exact_action':'Report smoke outcome/next blocker; no benchmark authorized'})
 spec=importlib.util.spec_from_file_location('status_render',R/'status-render.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.render()
 report=['# Q5 metadata-only loader patch and smoke','',f'Status: {result["status"]}','', 'Separate checkout /srv/ai/strata-v0.1.32-q5, exact basev0.1.32 c499bd102e7a4135c0de389dcfe38c399759ccc8 plus recordedlocaldiff. Clean checkout unchanged. No model/pack edits. No commit/push.', '', 'Regression: gguf_reader_test / gguf_split_test PASS; newly added metadata-only test FAIL with clean header and PASS with patch; tensor-bearing truncation and truncated metadata remain rejected. RealQ5 split headers6shards/1224tensors PASS. Separate defaultCUDA build sm89; Q4-fast OFF.', '', 'Runtime:2RTX4090,K24,INT8KV,max262144,prefillauto,spec4,minp0.5,same existingMTP,fullRAMarena91.6GiB, noresidentbudget. Memoryguard12GiB. Smoke8Kprompt64output only; no warmup or benchmark.']
 if result['status']=='PASS':
  q=result['smoke'];report+=['', 'Health READY;64tokens generated;normalMTPactive; text saved in raw/Q5-PATCH-SMOKE-smoke.json.', '', '```text', q['text'],'```','',f'RAM peak(system total minus MemAvailable):{q["peak_ram_used_gib"]:.2f}GiB; MemAvailable min:{q["min_mem_available_gib"]:.2f}GiB; GPU0/1 VRAM peak:{q["peak_vram0_gib"]:.2f}/{q["peak_vram1_gib"]:.2f}GiB.',f'Normal logical expert counters:{q["expert_tiers"]}; physicalSSD behindvirtiofs not proven.', '', 'This short smoke does not establish long-context speed, stability or quality.']
 else:report+=['',result.get('error',''),'', '```text',*lines[-30:],'```','', 'Stopped at next blocker; no additional patch or fallback applied.']
 report+=['', 'Patch:metadata-only-gguf.patch. Source/build/test/config/modelprovenance:environment.json; normal logs:logs/; canonical raw smoke:raw/. BothGPUreleased after run.']
 (R/'report.md').write_text('\n'.join(report)+'\n')
if result['status']!='PASS':raise SystemExit(1)
