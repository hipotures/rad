"""Reconstruct normal draft acceptance from existing upstream verify-window trace."""
import json,re
from pathlib import Path

def reconstruct(log,record):
 windows=[(int(p),int(t)) for p,t in re.findall(r'^strata trace: window (\d+) (\d+)$',log,re.M)]
 assert windows,'Upstream STRATA_TRACE emitted no verify windows'
 accepted_total=int(record['accepted_tokens']);offered_total=int(record['draft_tokens'])
 assert sum(t-1 for p,t in windows)==offered_total,'Trace offered sum differs from request-end counter'
 assert len(windows)==record['verify_rounds'],'Trace window count differs from decode timing'
 first=windows[0][0];accepted=0;offered=0;rows=[]
 for i,(position,width) in enumerate(windows):
  a=windows[i+1][0]-position-1 if i+1<len(windows) else accepted_total-accepted
  assert 0<=a<=width-1,'Trace acceptance outside verify-window bounds'
  accepted+=a;offered+=width-1
  index=min(position-first+a+1,int(record['generated_tokens']))
  rows.append({'window':i+1,'position':position,'verify_width':width,'generated_token_index':index,'offered_drafts':width-1,'accepted_drafts':a,'draft_offered_cumulative':offered,'draft_accepted_cumulative':accepted,'cumulative_acceptance_pct':100*accepted/offered if offered else None,'final_window_reconciled':i+1==len(windows)})
 assert accepted==accepted_total and offered==offered_total
 assert rows[-1]['generated_token_index']==record['generated_tokens'],'Trace output axis differs from generated count'
 return {'status':'VERIFIED_AGAINST_REQUEST_END_COUNTERS','rows':rows,'draft_offered':offered,'draft_accepted':accepted,'verify_windows':len(windows),'generated_tokens':record['generated_tokens'],'instrumentation':'Existing upstream STRATA_TRACE=1; no engine patch','scope':'Combined MTP and suffix-lookup draft counters. Consecutive positions give accepted drafts; last window reconciled against aggregate. Final verified drafts may exceed emitted output cap. This is a cumulative curve; no per-window origin distinction. Logging overhead is part of these long-run timings.'}

def save(root,name,record):
 root=Path(root);source=root/'raw'/f'{name}-engine.log';result=reconstruct(source.read_text(),record);result['source']=str(source)
 path=root/'raw'/f'{name}-acceptance-trace.json';path.write_text(json.dumps(result,indent=2)+'\n');return path
