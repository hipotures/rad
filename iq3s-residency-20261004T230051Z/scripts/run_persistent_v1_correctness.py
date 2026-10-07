from lab import ROOT,load,save
import subprocess,hashlib
from pathlib import Path
base=ROOT/'experiments/E029-persistent-runtime/v1-fixed';py=str(ROOT/'src/control/.venv/bin/python')
assert load(ROOT/'experiments/E029-persistent-runtime/v1/native-tests/command.json')['returncode']==0
for role in ['off','on']:
 name='persistent-v1-fixed-'+role;cmd=[py,'scripts/correctness_battery.py','--variant',name,'--experiment','E029-persistent-runtime','--attempt','v1-fixed']
 if role=='on':cmd+=['--reference',str(base/'correctness/persistent-v1-fixed-off')]
 subprocess.run(cmd,cwd=ROOT,check=True)
rows=[]
for n in range(1,11):
 a=load(base/f'correctness/persistent-v1-fixed-off/raw/case{n}.json');b=load(base/f'correctness/persistent-v1-fixed-on/raw/case{n}.json')
 def ids(r):
  folder=Path(r['telemetry']['path']).parents[1]/'token-ids';files=sorted(folder.glob('request*.json'))
  # Capture files use explicit label-independent numbered request order, warmup first.
  file=files[n] if len(files)>n else None
  if file:
   data=load(file);return data.get('output_ids',[]) if isinstance(data,dict) else data
  return None
 ids_a=load(base/f'correctness/persistent-v1-fixed-off/raw/output-ids-request{n+1}.json');ids_b=load(base/f'correctness/persistent-v1-fixed-on/raw/output-ids-request{n+1}.json')
 first=next((i for i,(x,y) in enumerate(zip(ids_a,ids_b)) if x!=y),min(len(ids_a),len(ids_b)) if ids_a!=ids_b else None)
 rows.append({'case':n,'same_output_IDs':ids_a==ids_b,'first_diverging_token':first,'same_input_IDs':a['payload']['input_ids_sha256']==b['payload']['input_ids_sha256'],'same_visible_output':a['output_text_sha256']==b['output_text_sha256'],'finish_off':a['finish_reason'],'finish_on':b['finish_reason'],'output_off':a['actual_output_tokens'],'output_on':b['actual_output_tokens'],'same_MTP':all(a.get(k)==b.get(k) for k in ['mtp_proposed','mtp_accepted','verify_windows'])})
checks={}
for role in ['off','on']:
 raw=base/f'correctness/persistent-v1-fixed-{role}/raw';answers={n:(raw/f'case{n}-response.txt').read_text() for n in range(1,11)}
 checks[role]={'math1776':'1776' in answers[1],'equation8':'x = 8' in answers[2],'strict_JSON_case9':__import__('json').loads(answers[9])=={'name':'test','count':3,'enabled':True},'strict_JSON_case10':__import__('json').loads(answers[10])==[{'id':1,'square':1},{'id':2,'square':4},{'id':3,'square':9}],'nonempty':all(v.strip() for v in answers.values())}
assert all(all(v.values()) for v in checks.values()),checks
save(base/'correctness/paired-summary.json',{'state':'PASS_LIMITED_BATTERY','pairs':rows,'ground_truth_checks':checks,'scope':'Math/code/prose/JSON shortgreedy, native suites, noNaN/Inf; not generalproof/outputbitparity acrosschangedCPU/GPU placement.'});print(rows,flush=True)
