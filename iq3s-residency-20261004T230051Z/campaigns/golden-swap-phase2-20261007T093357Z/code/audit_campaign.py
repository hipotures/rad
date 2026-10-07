"""Evidence/recovery/ownership audit. No blanket pass for unavailable measurements."""
import collections,hashlib,os,psutil,subprocess,time,datetime
from common import *
import live
def sha(p):
 with pathlib.Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
if __name__=='__main__':
 no_gpu();clock=load(C/'clock.json');identity=live.identities();rows=load(C/'results/live-attempts.json');main=[x for x in rows if x.get('kind')=='main'];ind=[x for x in rows if x.get('kind')=='independent'];assert len(main)==48 and all(x['valid'] for x in main);assert len(ind)==8 and all(x['valid'] for x in ind)
 points=collections.Counter((x['task'],x['arm']) for x in rows)
 reproduction=[]
 for test in sorted((C/'tests').glob('reproduction-*.json')):
  x=load(test);assert x['exit_code']==0;x['valid']=load(pathlib.Path(x['directory'])/'raw'/('replay-'+x['task']+'-'+x['arm'])/'episode.json')['valid'];assert x['valid'];points[x['task'],x['arm']]+=1;reproduction.append(x)
 assert reproduction,'At least one actual isolated replay reproducer required';assert max(points.values())<=3,points
 for task in ['code-archive','math-inventory','text-websocket','mixed-chinook']:
  rr=[r for r in main if r['task']==task];assert len(rr)==12 and len({r['work_sha256'] for r in rr})==len({r['initial_state_sha256'] for r in rr})==1
  for arm in ['REPLAY_CURRENT','ORACLE_FULL','ORACLE_IN_HISTORY_TC','ORACLE_IN_LOGISTIC_TC']:assert points[task,arm]==3
 for r in rows:
  p=C/'raw'/r['label'];cfg=load(p/'config.json');assert cfg['binary_sha256']==identity['binary_sha256'] and cfg['source_sha']==identity['source_sha']
  assert cfg['env']['STRATA_Q4_VICTIM_THRESHOLD']=='0.5' and cfg['env']['STRATA_Q4_POST_USE_EVENTS']=='0';assert cfg['env']['STRATA_POOL_SPIN_US']=='100'
 original=C.parents[1]/'builds/control/strata';assert sha(original)=='eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d'
 snapshot=load(C/'references/preservation-inventory.json');changed=[]
 with Heartbeat('prior evidence and launcher preservation audit',5):
  for x in snapshot:
   p=pathlib.Path(x['path'])
   if not p.exists() or p.stat().st_size!=x['bytes'] or sha(p)!=x['sha256']:changed.append(str(p))
 assert not changed,changed
 owned=[]
 for record in [C/'owned-process.json',*(C/'raw').glob('*/raw/native-process.json')]:
  if not record.exists():continue
  x=load(record);pid=x['pid'];created=x.get('created',x.get('create_time'));
  try:
   proc=psutil.Process(pid)
   if created is not None and abs(proc.create_time()-created)<.1 and proc.status()!=psutil.STATUS_ZOMBIE:owned.append({'pid':pid,'command':proc.cmdline(),'record':str(record)})
  except psutil.NoSuchProcess:pass
 assert not owned,owned
 required=['GOAL.md','README.md','STATUS.md','DECISIONS.md','protocol.md','reproduce.md','artifact-manifest.json','configs/dependencies.json','results/transaction-schema.json','results/queue-and-timing-diagnostics.json','results/protection-opportunity-costs.json','results/primary-table.csv','patches/cumulative-from-original.diff','report.md']
 assert all((C/x).is_file() for x in required)
 first_smoke=load(C/'raw/smoke-math-rational-LOGISTIC_TC/episode.json');assert first_smoke['valid'];first_smoke_end=next(x for x in [__import__('json').loads(s) for s in (C/'attempt-ledger.jsonl').read_text().splitlines()] if x.get('message')=='Live attempt END' and x.get('label')=='smoke-math-rational-LOGISTIC_TC')['utc'];offline_start=next(x['utc'] for x in [__import__('json').loads(s) for s in (C/'attempt-ledger.jsonl').read_text().splitlines()] if x.get('message')=='Offline point complete');assert first_smoke_end<offline_start;first_offline_issue=datetime.datetime.fromtimestamp(min(p.stat().st_mtime for p in (W/'raw/offline').glob('*/protocol.json')),datetime.timezone.utc).isoformat();assert first_smoke_end<first_offline_issue
 elapsed=time.monotonic()-clock['start_monotonic_s'];assert elapsed<clock['hard_budget_s'];conc=load(C/'results/conclusion.json')
 audit={'campaign_complete':True,'primary':conc['primary'],'scorer':conc['scorer'],'start_utc':clock['start_utc'],'deadline_utc':clock['deadline_utc'],'audit_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_s':elapsed,'deadline_reset':False,'main_valid_attempts':[48,48],'independent_valid_attempts':[8,8],'development_valid_attempts':[5,5],'isolated_reproduction_valid_attempts':[len(reproduction),len(reproduction)],'attempt_cap':{'maximum':max(points.values()),'point_counts':[{'task':k[0],'arm':k[1],'attempts':v} for k,v in sorted(points.items())]},'common_binary':identity,'preservation':{'verified_small_original_campaign_and_launcher_files':len(snapshot),'changed':changed,'original_binary_sha256':sha(original),'model_backing':'Pinned previous hashes plus unchanged size/mtime/inode attestation; large weights not rehashed during campaign','owned_processes_alive':owned,'GPU_compute_apps':subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()},'sequencing':{'compiled_end_to_end_smoke_before_offline_competition':True,'smoke_end':first_smoke_end,'first_offline_complete':offline_start,'first_offline_protocol_creation':first_offline_issue},'passed_evidence':['Every main/independent route/work/coefficient/shape/initial-state and main/MTP accounting check','Generation-specific ordinary-copy byte conservation and runtime service/first-use/distinct-use/eviction parity','Original Phase1 mechanism reconciliation across all24 oracle runs','Inherited full/OFF simulator parity across all8 development/calibration tapes','Real-copy lifecycle and existing oracle/policy/cost guards','Information fixture repaired invocation with610 reference decisions and suffix/role invariance','Frozen logistic4000 predictions and prefix300 batches','Nine targeted native tests','Continuous natural capture and four-arm independent full-tape replay','Actual isolated historyTC replay reproducer','No owned GPU work and original artifacts preserved'],'deviations':['Initial information fixture invocation lacked required tape environment; retained failure, corrected invocation passed with no source/binary change','Initial build heartbeat helper collided on ETA keyword; retained failure and resumed monitoring','Offline harness syntax error was corrected before any policy point executed','Independent context-occupancy metadata corrected5516→5515; unchanged tape/work/policy','Early development telemetry lacks explicit swap snapshot; common main sampler includes snapshots','Final diagnostics initially required every release to follow first use; retained assertion failure, separated legitimate expiry releases before later use from first-use releases; no runtime/policy change','Read-only independent watcher initially used system Python without psutil; pinned environment repaired, native runner unaffected','History effective-config descriptive policy label is inherited Native current residency; authoritative environment selects causal native/history correctly'],'unmeasured_or_skipped':['Full unrelated native test suite','Exclusive CPU latency per routed entry;160us is assumed guard setting','DMA-only bandwidth and exact exposed planner/publication stall attribution','Full native adaptation planning outside host routed-plan interval','Individual rejected proposal linkage and initial suggested victim before publication re-selection','Exact preventable competing admission counterfactual regret','Native intended target, staging and independent unpublished-completion marker','MTP residency path subdivision','Natural output quality and bitwise CPU/GPU equivalence','Second independent source and128K/256K optional checks','Independent persistent backup for irreplaceable raw captures; local-host-loss recovery gap remains'],'publication':{'local_commit_required':True,'push':'Routine repository commit/push follows AGENTS.md; no goal-specific prohibition','pull_request':'No PR created by this campaign'}}
 previous=load(C/'completion-audit.json') if (C/'completion-audit.json').exists() else {}
 for key in ['requirements','recovery_tests','counter_scope']:
  if key in previous:audit[key]=previous[key]
 audit['recovery_tests']['actual_isolated_replay']=str(next((C/'tests').glob('reproduction-*.json')).relative_to(C))
 audit['recovery_tests']['result_consistency']='tests/final-result-consistency.json'
 audit['deviations'].append('Administrative ledger-write snippet syntax error before execution; corrected snippet recorded without changing scientific evidence')
 audit['source_snapshot_note']='Exact cumulative source snapshot includes inherited host-only .venv symlink metadata, no environment payload; explicit build does not require it and portable exclusion is documented.'
 save(C/'completion-audit.json',audit);save(C/'results/cleanup-proof.json',audit['preservation']);print('AUDIT_COMPLETE',elapsed,flush=True)
