from lab import ROOT,load,save
import subprocess
py=str(ROOT/'src/control/.venv/bin/python');base=ROOT/'experiments/E029-persistent-runtime/v2-fixed'
# Fullyrepeatbattery because changedplacementpolicy, skip re-running unchanged P1 controls.
for role in ['off','on']:
 cmd=[py,'scripts/correctness_battery.py','--variant','persistent-v2-'+role,'--experiment','E029-persistent-runtime','--attempt','v2-fixed']
 if role=='on':cmd+=['--reference',str(base/'correctness/persistent-v2-off')]
 subprocess.run(cmd,cwd=ROOT,check=True)
rows=[];checks={}
for n in range(1,11):
 a=load(base/f'correctness/persistent-v2-off/raw/case{n}.json');b=load(base/f'correctness/persistent-v2-on/raw/case{n}.json');x=load(base/f'correctness/persistent-v2-off/raw/output-ids-request{n+1}.json');y=load(base/f'correctness/persistent-v2-on/raw/output-ids-request{n+1}.json');first=next((i for i,(u,v) in enumerate(zip(x,y)) if u!=v),min(len(x),len(y)) if x!=y else None)
 rows.append({'case':n,'same_input_IDs':a['payload']['input_ids_sha256']==b['payload']['input_ids_sha256'],'same_output_IDs':x==y,'first_diverging_token':first,'same_MTP':all(a.get(k)==b.get(k) for k in ['mtp_proposed','mtp_accepted','verify_windows']),'finish_off':a['finish_reason'],'finish_on':b['finish_reason']})
for role in ['off','on']:
 raw=base/f'correctness/persistent-v2-{role}/raw';answers={n:(raw/f'case{n}-response.txt').read_text() for n in range(1,11)}
 checks[role]={'math1776':'1776' in answers[1],'equation8':'x = 8' in answers[2],'strict_JSON_case9':__import__('json').loads(answers[9])=={'name':'test','count':3,'enabled':True},'strict_JSON_case10':__import__('json').loads(answers[10])==[{'id':1,'square':1},{'id':2,'square':4},{'id':3,'square':9}],'nonempty':all(v.strip() for v in answers.values())}
assert all(all(v.values()) for v in checks.values()) and all(x['same_input_IDs'] for x in rows),checks
save(base/'correctness/paired-summary.json',{'state':'PASS_LIMITED_BATTERY','pairs':rows,'ground_truth_checks':checks,'scope':'NoNaN/Inf, numericalanswer/schema checks; noqualityjudge or generalmathproof.'});print(rows,flush=True)
