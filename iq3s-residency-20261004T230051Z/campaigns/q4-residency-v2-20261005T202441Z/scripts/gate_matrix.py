"""Wait for finite correctness batch, validate readiness/readback, then serial clean matrix."""
from campaign import C,R,load,save,guard
import time,psutil,subprocess,json

def main():
 until=time.time()+1800
 while psutil.pid_exists(1862228):
  guard();assert time.time()<until,'Short correctness timeout';time.sleep(5)
 assert (C/'phase-c/short-correctness.json').exists(),'Correctness failed; inspect preserved failure before speed'
 all_rows=[]
 for variant in ['early-diagnostic','early-wrong','early-delayed']:
  path=C/'correctness'/variant;rows=[]
  for file in sorted(path.glob('early-events-request*.jsonl')):
   events=[json.loads(x) for x in file.read_text().splitlines()]
   for e in events:
    if e['published_ns']:assert e['copy_end_ns']>0 and e['copy_end_ns']<=e['published_ns'] and e['incoming']!=e['victim']
   rows.extend(events)
  text=(path/'logs/engine.log').read_text();checks=[]
  import re
  checks=[int(x) for x in re.findall(r'Q4_EARLY_READBACK PASS checks=(\d+)',text)]
  assert len(checks)==5,'warmup plus4 diagnostic requests must finish/restore'
  if variant=='early-diagnostic':assert sum(checks)>0,'Normal diagnostic must really publish/readback experts'
  all_rows.append({'variant':variant,'transactions':len(rows),'publication_order_pass':True,'readback_checks':checks,
         'classes':{key:sum(e['classification']==key for e in rows) for key in set(e['classification'] for e in rows)},
         'useful_entries':sum(e['uses'] for e in rows),'victim_absent_entries':sum(e['victim_entries'] for e in rows),
         'limitations':['Descriptive victim absence, not exclusive causal latency','Readback16 maximum/request; short correctness output256, not speed4096']})
 save(C/'phase-c/early-adverse-tests.json',all_rows)
 print('CORRECTNESS_GATE_PASS',flush=True)
 py=str(R/'src/control/.venv/bin/python')
 with (C/'logs/main-matrix.log').open('x') as f:r=subprocess.run([py,'scripts/main_matrix.py'],cwd=C,stdout=f,stderr=subprocess.STDOUT,timeout=7200)
 save(C/'phase-c/matrix-exit.json',{'exit_code':r.returncode,'finished_epoch':time.time()});assert not r.returncode,'Preserve/diagnose failing matrix cell'
if __name__=='__main__':main()
