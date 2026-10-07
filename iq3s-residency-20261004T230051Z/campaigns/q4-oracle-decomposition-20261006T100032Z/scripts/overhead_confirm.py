"""Complete exactly three short guard pairs after variable first pair; no new engine build."""
import json,statistics
from owned import C,run
from batch import PY,point
for attempt,order in [(2,['replay','natural']),(3,['natural','replay'])]:
 for mode in order:
  if mode=='replay':point('32k','current','development'+str(attempt),payload='development',tape=C/'tapes/development-capture-v3.bin')
  else:run('development-v2-natural'+str(attempt),[PY,C/'scripts/runner.py','natural','--profile','32k','--label','development-v2-natural'+str(attempt),'--payload','development','--variant','oracle-decomposition-v2'],timeout=1200)
rows=[]
for attempt in [1,2,3]:
 suffix='' if attempt==1 else str(attempt);a=json.loads((C/'raw'/('development-v2-natural'+suffix)/'results.json').read_text())['runs'][0];b=json.loads((C/'raw'/('v2-32k-current-attemptdevelopment'+suffix)/'results.json').read_text())['runs'][0]
 aa=json.loads(__import__('pathlib').Path(a['actual_output_ids_path']).read_text());bb=json.loads(__import__('pathlib').Path(b['actual_output_ids_path']).read_text());r={'attempt':attempt,'input_equal':a['actual_engine_input']==b['actual_engine_input'],'output_equal':aa==bb,'MTP_equal':(a['mtp_proposed'],a['mtp_accepted'])==(b['mtp_proposed'],b['mtp_accepted']),'natural_decode_s':a['decode_s'],'replay_decode_s':b['decode_s'],'decode_time_ratio':b['decode_s']/a['decode_s'],'wall_time_ratio':b['wall_s']/a['wall_s']};assert r['input_equal'] and r['output_equal'] and r['MTP_equal'];rows.append(r)
summary={'state':'PASS','rows':rows,'median_paired_decode_ratio':statistics.median(x['decode_time_ratio'] for x in rows),'median_paired_wall_ratio':statistics.median(x['wall_time_ratio'] for x in rows),'scope':'three short fresh-start pairs; not proof of universal overhead or performance equivalence'}
(C/'phase-a/ordinary-replay-guard-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
