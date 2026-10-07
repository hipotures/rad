"""Persist trace checks and reconcile diagnostics with independently reported totals."""
import argparse,json,pathlib
from trace_reader import Trace
from lab import ROOT,save
ap=argparse.ArgumentParser();ap.add_argument('attempt');ap.add_argument('--profile',choices=['32k','128k','episodes'],required=True);a=ap.parse_args()
base=ROOT/'experiments/E003-diagnostics'/a.attempt/a.profile
results=json.loads((base/'results.json').read_text())
checks=[]
for n,row in enumerate(results['runs'],2):
 t=Trace(base/'traces'/f'runtime-request{n}');v=t.validate()
 v['raw_request']=str(base/'raw'/('trace-run1.json' if a.profile!='episodes' else row['payload']['name']+'.json')) if row['payload'].get('name') else row['payload']['path']
 v['reported']={k:row.get(k) for k in ['actual_output_tokens','local_vram_entries','cpu_fallback_entries','offloaded_entries','verify_windows','mtp_accepted']}
 v['footer_agreement']=(v['output_tokens']==row['actual_output_tokens'] and v['path_counts'][0]==row['local_vram_entries'] and v['path_counts'][-1]==row['cpu_fallback_entries'] and v['path_counts'][1]+v['path_counts'][2]==row['offloaded_entries'] and v['windows']==row['verify_windows'] and int(t.windows['accepted'].sum())==row['mtp_accepted'])
 if not v['footer_agreement']:v['state']='FAIL';v['errors'].append('API/footer accounting mismatch')
 checks.append(v)
save(base/'validation.json',{'checks':checks,'state':'PASS' if all(x['state']=='PASS' for x in checks) else 'FAIL'})
print(json.dumps(checks,indent=2))
assert all(x['state']=='PASS' for x in checks)
