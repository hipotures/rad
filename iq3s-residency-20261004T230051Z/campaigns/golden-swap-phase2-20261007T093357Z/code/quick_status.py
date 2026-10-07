"""Small progress readout only; full analysis runs after GPU work stops."""
from common import *
x=load(C/'progress.json');print(json.dumps(x,indent=2))
p=C/'results/main-execution.json'
if p.exists():
 rows=load(p);print('VALID_MAIN',sum(r['valid'] for r in rows),'ATTEMPTS',len(rows))
 for task,b in sorted({(r['task'],r['block']) for r in rows}):
  rs=[r for r in rows if r['task']==task and r['block']==b]
  if len(rs)!=4:continue
  eps={r['arm']:load(C/'raw'/r['label']/'episode.json') for r in rs};cur=eps['REPLAY_CURRENT']['run'];full=eps['ORACLE_FULL']['run'];ret={}
  for arm in ['ORACLE_IN_HISTORY_TC','ORACLE_IN_LOGISTIC_TC']:
   a=eps[arm]['run'];den=cur['decode_s']-full['decode_s'];ret[arm]={'TG_pct':100*(cur['decode_s']/a['decode_s']-1),'wall_pct':100*(a['wall_s']/cur['wall_s']-1),'retention':(cur['decode_s']-a['decode_s'])/den if den>0 else None}
  print('COMPLETE_BLOCK',task,b,json.dumps(ret),'durations',[round(r['total_operating_s'],1) for r in rs])
