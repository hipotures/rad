"""Append stage transitions without losing deadline or prior decisions."""
import argparse, datetime, json, pathlib, time
ROOT=pathlib.Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('experiment');ap.add_argument('state');ap.add_argument('--next',default='');ap.add_argument('--note',default='');a=ap.parse_args()
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();r={'id':a.experiment,'state':a.state,'updated_utc':stamp,'note':a.note}
with (ROOT/'experiments.jsonl').open('a') as f:f.write(json.dumps(r)+'\n')
s=json.loads((ROOT/'STATUS.json').read_text());s['updated_utc']=stamp;s['last_stage']=r
if a.state.startswith('COMPLETE'):
 if a.experiment not in s['completed']:s['completed'].append(a.experiment)
 s['pending']=[p for p in s['pending'] if not p.startswith(a.experiment+' ')]
 s['running']=None
else:s['running']=a.experiment
s['pending']=[p for p in s['pending'] if not any(p.startswith(done+' ') for done in s['completed'])]
if a.next:s['next_exact_action']=a.next
(ROOT/'STATUS.json').write_text(json.dumps(s,indent=2)+'\n')
d=json.loads((ROOT/'deadline.json').read_text());remaining=(d['deadline_epoch']-time.time())/3600
(ROOT/'STATUS.md').write_text(f'# Research status\n\nState: {s["state"]}. Last stage: {a.experiment} / {a.state}.\n\nCompleted: {", ".join(s["completed"])}.\n\n{a.note}\n\nNext exact action: {s["next_exact_action"]}.\n\nAbsolute deadline: {d["deadline_utc"]}; remaining at update: {remaining:.2f} hours. Never reset the deadline. Read GOAL.md and STATUS.json after resumption.\n')
