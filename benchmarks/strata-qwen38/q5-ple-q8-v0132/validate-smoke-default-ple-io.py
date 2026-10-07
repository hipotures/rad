import run as r,json,subprocess,traceback,re,hashlib
from pathlib import Path
R=r.ROOT;env=json.loads((R/'environment.json').read_text());out={'status':'RUNNING','regressions':'7/7 PASS + real Q8_0 PLE parity PASS','smokes':[],'benchmark_requests':0}
def status(phase,state='RUNNING'):
 r.c.save(R/'STATUS.json',{'status':state,'running':phase,'completed':['semantic CPU-only runtime patch','separate build','7/7 regression tests + real Q8_0 PLE parity PASS']+[x['label'] for x in out['smokes'] if x.get('status')=='PASS'],'pending':['single/two GPU smoke as needed','same GGUF llama.cpp parity','32K/128K needle'],'next_exact_action':phase or 'Read summary/next blocker; no speed benchmark'})
try:
 for label,topology in [('Q5-CPU-1GPU','arena1'),('Q5-CPU-2GPU-K24','split')]:
  cfg=r.config(label,topology,split=24,context=262144)
  status(label+' load/health')
  with r.Session(label,cfg) as s:
   status(label+' 64-token smoke')
   rec=s.request(2048,64,'smoke','smoke');log=Path(cfg['log']).read_text(errors='replace')
   assert rec['status']=='OK' and rec['generated_tokens']==64 and rec['text'].strip(),rec.get('error')
   assert rec['draft_tokens']>0,'MTP inactive'
   assert rec['abort'] is None and rec['min_mem_available_gib']>=12,'RAM guard'
   assert 'layer 2 CPU entries' in log and 'GPU expert entries 0' in log,'CPU-only layer not observed'
   state={'label':label,'status':'PASS','health':r.c.api('/health'),'smoke':rec,'cpu_only_log_lines':[x for x in log.splitlines() if 'CPU-only' in x or 'CPU_ONLY' in x]}
   out['smokes'].append(state);r.c.save(R/'summary.json',out)
   print('PASS',label,rec['text'],flush=True)
 out['status']='SMOKE_PASS_CORRECTNESS_PENDING';status('same GGUF parity and 32K/128K needle',out['status'])
except BaseException as e:
 out.update(status='STOP_NEXT_BLOCKER',error=repr(e),traceback=traceback.format_exc());print('STOP',repr(e),flush=True)
 status(None,out['status'])
finally:
 out['gpu_compute_apps_after']=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'],text=True)
 out['clean_checkout_tracked_unchanged']=not subprocess.check_output(['git','diff','--name-only'],cwd='/srv/ai/strata-v0.1.32',text=True).strip()
 out['model_stat_unchanged']=all((lambda st,x:st.st_size==x['size'] and st.st_mtime_ns==x['mtime_ns'] and st.st_ino==x['inode'])(Path(x['path']).stat(),x) for x in env['model_stat_before'])
 r.c.save(R/'summary.json',out)
 import importlib.util
 spec=importlib.util.spec_from_file_location('sr',R/'status-render.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.render()
if out['status']=='STOP_NEXT_BLOCKER':raise SystemExit(1)
