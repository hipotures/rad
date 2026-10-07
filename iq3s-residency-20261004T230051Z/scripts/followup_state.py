"""Durable follow-up transitions; prior campaign stays archived and immutable."""
import argparse, datetime, json, time
from lab import ROOT, load, save
ap=argparse.ArgumentParser();ap.add_argument('stage');ap.add_argument('state');ap.add_argument('--next',required=True);ap.add_argument('--note',default='');a=ap.parse_args()
active=load(ROOT/'active-campaign.json');campaign=__import__('pathlib').Path(active['path']);d=load(active['deadline_path']);s=load(ROOT/'STATUS.json')
transition={'id':a.stage,'state':a.state,'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'campaign':d['campaign'],'note':a.note}
with (ROOT/'experiments.jsonl').open('a') as f:f.write(json.dumps(transition)+'\n')
with (campaign/'transitions.jsonl').open('a') as f:f.write(json.dumps(transition)+'\n')
s.update(updated_utc=transition['updated_utc'],last_stage=transition,next_exact_action=a.next,elapsed_wall_s=time.time()-d['start_epoch'],remaining_wall_s=d['deadline_epoch']-time.time())
if a.state.startswith('COMPLETE'):
    if a.stage not in s['completed']:s['completed'].append(a.stage)
    s['running']=None
    phase={'E026':'P0 ','E027':'P1 ','E029':'P2 '}.get(a.stage.split('-')[0])
    if phase:s['pending']=[p for p in s['pending'] if not p.startswith(phase)]
else:s['running']=a.stage
save(ROOT/'STATUS.json',s);save(campaign/'STATUS.json',s)
text=f'# Pool and persistent-residency follow-up\n\nState: {s["state"]}. Current stage: {a.stage} / {a.state}.\n\n{a.note}\n\nCompleted: '+', '.join(s['completed'])+'\n\nPending: '+ '; '.join(s['pending'])+f'\n\nNext exact action: {a.next}\n\nStart: {d["start_utc"]}; no new substantial experiment after {d["consolidation_start_utc"]}; absolute deadline {d["deadline_utc"]}. Remaining {(d["deadline_epoch"]-time.time())/3600:.2f}h at this checkpoint.\n'
(ROOT/'STATUS.md').write_text(text);(campaign/'STATUS.md').write_text(text)
print(a.stage,a.state,flush=True)
