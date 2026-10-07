"""Append new handoff metadata without replacing completed campaign evidence."""
from pathlib import Path
import json,datetime,time,hashlib
C=Path(__file__).resolve().parents[1];R=C.parents[1]
def load(p):return json.loads(Path(p).read_text())
def save(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')
def main():
 assert load(C/'analysis/final-audit.json')['state']=='PASS'
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();d=load(C/'deadline.json');summary=load(C/'summary.json')
 assert time.monotonic()<d['deadline_monotonic'] and summary['state']=='COMPLETE'
 state=load(C/'STATUS.json');state.update(state='COMPLETE',running=None,error=None,pending=[],completed=['Frozen source/binary/model and existing evidence audit','Phase A: full-main/MTP/QSA tape, strict v3 initial state, ordinary/replay overhead and numerical diagnostics','Phase B: all48-layer/all3-class feasible logical full-future scheduling and strict offline horizons','Phase C:18/18 final paired requests, independent1024-output task, one negative H64 confirmation','Safety fixtures, reproducibility checks, preserved raw evidence, reports and owned-process/GPU cleanup'],recommendation='FEASIBLE_LIVE_ORACLE_GAIN',current_winners={'research':'Full-future same-device oracle improves fixed-work replay','real_use':'Unchanged original Q4/100us K24/.28 serving baseline'},next_exact_action='Review report; use unchanged control launchers for real prompts. No new residency work starts automatically.',updated_utc=now,completed_utc=now,elapsed_monotonic_s=time.monotonic()-d['start_monotonic'],finished_before_deadline=True,unfinished_due_to_deadline=[],launcher_validation='tests/launcher-checks/summary.json',final_audit='analysis/final-audit.json')
 save(C/'STATUS.json',state);fence=chr(96)*3
 (C/'STATUS.md').write_text('# Q4 live oracle — complete\n\nAll 18 primary attempts valid. Recommendation: FEASIBLE_LIVE_ORACLE_GAIN. The unchanged Q4/100us serving baseline remains real-use. No further experiments start automatically.\n\n[Report](report.md) · [Summary](summary.json) · [Normal control](launchers/control/README.md) · [Experimental tools](launchers/experimental/README.md) · [Final audit](analysis/final-audit.json)\n\n'+fence+'json\n'+json.dumps(state,indent=2)+'\n'+fence+'\n')
 for name in ['STATUS.json','summary.json','launch-index.json']:
  snapshot=C/'git'/('prior-root-'+name)
  if not snapshot.exists():snapshot.write_bytes((R/name).read_bytes())
 rel=str(C.relative_to(R));entry={'path':str(C),'state':'COMPLETE','recommendation':state['recommendation'],'report':str(C/'report.md'),'status':str(C/'STATUS.json'),'control_launchers':str(C/'launchers/control'),'experimental_launchers':str(C/'launchers/experimental'),'real_use':'Unchanged Q4/100us original control; clairvoyant replay not production','updated_utc':now}
 root=load(R/'STATUS.json');root['latest_campaign']=entry;save(R/'STATUS.json',root)
 root=load(R/'summary.json');root['latest_q4_live_oracle']=dict(entry,paired=summary['paired'],headline_count=18);save(R/'summary.json',root)
 marker='<!-- q4-live-oracle-20261006T040656Z -->'
 additions={
 'STATUS.md':f'\n{marker}\n\n## Q4 live oracle — complete\n\n18/18 controlled full-work requests passed. Full-future replay improves decode at 32/128/256K; one scoped H64 is negative from churn/victim damage. Research conclusion FEASIBLE_LIVE_ORACLE_GAIN; unchanged Q4/100us remains real-use. Both GPUs free, no owned inference/training/profiling processes.\n\n[Report]({rel}/report.md) · [Status]({rel}/STATUS.md)\n',
 'launch-index.md':f'\n{marker}\n\n## Q4 live oracle handoff\n\nResearch conclusion FEASIBLE_LIVE_ORACLE_GAIN. This is fixed-work clairvoyant replay, not ordinary model serving. Unchanged Q4/100us source 6f32ec070f23ced9f50e704d854d775da52591ab / binary eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d remains real-use. K24/.28,15 workers,spec4/.5,INT8,lookup/reuse OFF.\n\n[Normal control launchers]({rel}/launchers/control/README.md) · [Experimental capture/replay]({rel}/launchers/experimental/README.md) · [Report]({rel}/report.md)\n\nBoth sets have identity/config checks, finite timeouts and owned-only cleanup. Experimental wrappers create new reproduction directories after campaign completion. Shell/check-mode validation passed; their core backends ran all preserved campaign requests. No fourth headline repetition was added for thin aliases. Normal user launchers remain untouched.\n'}
 for name,text in additions.items():
  p=R/name
  if marker not in p.read_text():
   with p.open('a') as f:f.write(text)
 index=load(R/'launch-index.json')
 for v in ['control','experimental']:
  name='q4-live-oracle-'+v
  if not any(x.get('variant')==name for x in index):
   index.append({'variant':name,'state':'UNCHANGED_REAL_USE_BASELINE' if v=='control' else 'EXPERIMENTAL_FIXED_WORK_ONLY','campaign':str(C),'source_sha':'6f32ec070f23ced9f50e704d854d775da52591ab' if v=='control' else '117bc89b3bacbf263379c336557e6c8aa07aff5e','binary_sha256':'eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d' if v=='control' else '30a31432b5aff51bcd4340900c13cad0c8487a832bfdb22d05f9157b88d5bdb3','launcher_directory':str(C/'launchers'/v),'validation':str(C/'tests/launcher-checks/summary.json'),'no_production_switch':True})
 save(R/'launch-index.json',index)
 existing=(R/'experiments.jsonl').read_text()
 with (R/'experiments.jsonl').open('a') as f:
  for i,phase in [(33,'A-record-replay'),(34,'B-logical-oracle'),(35,'C-controlled-comparison')]:
   identifier=f'E0{i}-q4-live-oracle-{phase}'
   if identifier not in existing:f.write(json.dumps({'id':identifier,'status':'COMPLETE','campaign':str(C),'report':str(C/f'phase-{phase[0].lower()}/report.md'),'recommendation':'FEASIBLE_LIVE_ORACLE_GAIN','utc':now})+'\n')
 active=load(R/'active-campaign.json');assert active['campaign']==str(C);active.update(state='COMPLETE',completed_utc=now,report=str(C/'report.md'),real_use_control_unchanged=True);save(R/'active-campaign.json',active)
 prior=[]
 for old in ['q4-residency-v2-20261005T202441Z','q4-pool-spin-20261005T184831Z','q4-multigpu-20261005T164628Z','q4-conditional-admission-20261006T010859Z']:
  for n in ['report.md','summary.json','STATUS.json']:
   p=R/'campaigns'/old/n
   if p.exists():
    st=p.stat();prior.append({'path':str(p),'bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'mtime_precedes_new_campaign':st.st_mtime<=d['start_epoch'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 assert all(x['mtime_precedes_new_campaign'] for x in prior)
 save(C/'git/prior-campaign-handoff-stat.json',{'previous_reports_unchanged_during_campaign_by_mtime':True,'files':prior,'scope':'Current report/summary/status timestamps predate campaign start; no initial full-directory hash was claimed.'})
 print('LABORATORY_HANDOFF_COMPLETE',round(state['elapsed_monotonic_s']),flush=True)
if __name__=='__main__':main()
