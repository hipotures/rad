"""Requirement-specific completion audit; missing evidence is never PASS."""
import hashlib,subprocess,psutil,collections
from common import *

def sha(p):return hashlib.file_digest(pathlib.Path(p).open('rb'),'sha256').hexdigest()
if __name__=='__main__':
 no_gpu();clock=load(C/'clock.json');elapsed=time.monotonic()-clock['start_monotonic_s'];assert elapsed<clock['hard_budget_s'],'Original campaign deadline exceeded';identity=load(C/'configs/runtime-identity.json');runs=load(C/'results/live-attempts.json');pairs=load(C/'results/paired-blocks.json');assert len(runs)==42 and len(pairs)==14
 assert len([x for x in runs if x['kind']=='main'])==36 and len([x for x in runs if x['kind']=='independent'])==6
 assert all(x['valid'] and x['victims']['state']=='PASS' and x['transactions']['reconciled_generations']>=0 for x in runs)
 for x in runs:
  f=load(C/'raw'/x['label']/'fidelity.json');assert f['state']=='PASS'
 counts=collections.Counter((x['task'],x['arm']) for x in runs);assert all(v<=3 for v in counts.values())
 for task in ['code-archive','math-inventory','text-websocket','mixed-chinook']:
  assert sum(x['task']==task for x in pairs)==3
  assert len({x['work_sha256'] for x in runs if x['task']==task})==1;assert len({x['initial_state_sha256'] for x in runs if x['task']==task})==1
 assert sha(identity['exe'])==identity['binary_sha256'];assert sha(C/'models/logistic.txt')==identity['checkpoint_sha256'];assert subprocess.check_output(['git','status','--porcelain'],cwd=identity['source'],text=True).strip()==''
 assert sha(identity['phase2']['exe'])==identity['phase2']['binary_sha256']
 control=INPUT_PARENT.parent/'builds/control/strata';assert sha(control)=='eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d'
 for path,frozen in load(P0/'provenance/model-identity.json')['files'].items():
  st=pathlib.Path(path).stat();assert (st.st_size,st.st_mtime_ns,st.st_ino)==(frozen['size'],frozen['mtime_ns'],frozen['inode'])
 assert len(load(C/'tests/deterministic-parity.json'))==26 and all(x['state']=='PASS' for x in load(C/'tests/deterministic-parity.json'));assert len(load(C/'tests/frozen-phase2-off-parity.json'))==16
 assert load(C/'tests/archive-tools-outcome.json')['exit_code']==0 and load(C/'tests/archive-tools-outcome.json')['tests']==26
 assert all(x['same_required_work'] and x['publication_visibility_changed_before_first_incoming_selection_divergence'] for x in load(C/'results/live-trajectory-diagnostics.json'))
 assert len(load(C/'input-manifest.json')['inputs'])==13 and all(x['phase3_prior_evaluation_exposure'] and not x['phase3_pristine_holdout'] for x in load(C/'input-manifest.json')['inputs'])
 assert all(x['wall_s']<240 and x['startup_s']+x['warmup_s']<180 for x in runs)
 for x in runs:
  assert sum(v['bytes'] for v in x['transactions']['partition'].values())==x['transactions']['completed_bytes']
  assert len(x['wait'])==2 and all(w['plan_count']==24*x['windows'] for w in x['wait'])
  if x['arm']!='REPLAY_CURRENT':
   assert x['information']['victim_next']==x['information']['victim_count']==0
   assert x['tc']['post_use_events']==0 and x['tc']['cap_per_device_class']==16
 assert not any(x['optimization_gain_criterion'] for x in load(C/'results/main-summary.json') if x['kind']=='main')
 assert len(load(C/'configs/conclusion.json')['answers'])==12
 assert load(C/'tests/development-guard.json')['state']=='PASS';assert all(x['exit_code']==0 for x in load(C/'tests/safety-outcomes.json'));assert load(C/'tests/native-outcome.json')['exit_code']==0
 changed=[]
 with Heartbeat('preservation audit',5):
  for p,x in load(C/'inputs/preservation.json').items():
   if pathlib.Path(p).stat().st_size!=x['bytes'] or sha(p)!=x['sha256']:changed.append(p)
 assert not changed
 owned=[]
 for p in psutil.process_iter(['pid','cmdline']):
  try:
   cmd=p.info['cmdline'] or []
   if any(str(SOURCE) in x or str(BUILD) in x for x in cmd):owned.append({'pid':p.pid,'cmdline':cmd})
  except psutil.Error:pass
 assert not owned
 checks=load(C/'tests/reproduction-checks.json');assert checks['prepare_only']['exit_code']==0 and checks['live']['exit_code']==0
 assert load(C/'tests/source-recovery-summary.json')['state']=='PASS'
 import gzip
 recovered=json.loads(gzip.open(C/'evidence/fixtures-text-v1/source-recovery.json.gz','rt').read());assert recovered['state']=='PASS' and len(recovered['files'])==load(C/'tests/source-recovery-summary.json')['checked_files']
 assert sha(C/'tests/source-recovery.json')==load(C/'tests/source-recovery-summary.json')['full_inventory_original_sha256']
 assert len(load(C/'results/text-publication.json'))==4 and all(all(o['exit_code']==0 for o in r['outcomes']) for r in load(C/'results/text-publication.json'))
 required=['GOAL.md','clock.json','STATUS.md','progress.json','progress.jsonl','attempt-ledger.jsonl','DECISIONS.md','README.md','report.md','reproduce.md','input-manifest.json','artifact-manifest.json','run-order.json','configs/conclusion.json','results/planner-dependencies.md','results/existing-data-analysis.json','results/phase0-reuse-reference.json','results/main-summary.json','results/paired-blocks.json','results/live-attempts.json','results/primary-table.csv','results/live-trajectory-diagnostics.json','tests/development-guard.json','tests/deterministic-parity.json','tests/frozen-phase2-off-parity.json','tests/scorer-parity.json','tests/reproduction-checks.json','tests/source-recovery-summary.json','evidence/completed-text-v1/archive-manifest.jsonl.gz','evidence/runner-logs-v1/archive-manifest.jsonl.gz','evidence/reproduction-text-v1/archive-manifest.jsonl.gz','evidence/fixtures-text-v1/archive-manifest.jsonl.gz','results/text-publication.json','results/phase-resource-diagnostics.json','results/relative-mechanism.json','tests/archive-tools-outcome.json']
 assert all((C/p).is_file() for p in required),[p for p in required if not (C/p).is_file()]
 result={'campaign_complete':False,'scientific_and_reproduction_checks_complete':True,'publication_pending':True,'primary':load(C/'configs/conclusion.json')['primary'],'start_utc':clock['start_utc'],'deadline_utc':clock['deadline_utc'],'elapsed_s':elapsed,'deadline_reset':False,'main_valid_attempts':[36,36],'independent_valid_attempts':[6,6],'development_valid_attempts':[6,7],'attempt_cap':{'unchanged_primary_max':max(counts.values()),'development_OPT':{'failed_before_warmup':1,'compiled_smoke_valid':1,'isolated_reproduction_valid':1,'total':3}},'required_artifacts':required,'identity':identity,'requirements':{'step1':'56 retained Phase2 journals analyzed; four primary tasks plus RFC8259, lifetime/reuse/slack/queue/cap/scans; missing fields explicit','step2':'Narrow immutable-query memo, exact boundary/reset/rewind invalidation; complete mutable policy checks retained; finite-information fallback; host memory and counters retained','step3':'26 deterministic candidate/admission/ownership/work pairs;16 inherited OFF accounting hashes; real copy/ownership/lease/wait/scorer/prefix fixtures;9 native tests; compiled integration and two overhead guard pairs before headline','step4':'36 primary +6 continuous independent-source full-tape requests in frozen counterbalanced adjacent blocks; same binary/settings/work, complete charged wall; no steal correction; all observations retained','step5':'Paired ratios/signs/ranges, nested/exposed semantics, explicit12 answers, resources, failures and recovery material; tested actual replay/prepare/analysis, source reconstruction, gzip identity/readback checks; indexed audit and commit/push remain final gates'},'preservation':{'changed_files':changed,'verified_files':len(load(C/'inputs/preservation.json')),'owned_processes_alive':owned,'GPU_apps':'none','ordinary_launchers_unchanged':True},'deviations':['Initial simulator SHA parity used an unmodeled host issue timestamp; retained failure and normalized only that field, no repeated policy evaluation','Initial scorer parity environment lacked sklearn; repaired with frozen Phase1 environment before native parity ran','Initial subprocess wrapper timeout argument order failed before process start','First smoke startup reached readiness but missing payload manifest prevented warmup/request; retained invalid startup and fresh repaired attempt2','Initial heartbeat field retention omitted block; completed counts plus frozen order preserve identity, corrected future runners/quick status', 'Continuation lost the original observation handle; PID/create-time/command/child evidence confirmed the same live parent, attached read-only monitor without restarting', 'First analysis regeneration referenced prefill_s rather than measured pp_s; repaired reader only, original failed log retained and no inference rerun', 'First source reconstruction compared declared CRLF Windows checkout bytes with LF Git blobs; exact checkout plus canonical-filtered blob verification repaired the comparator, no source/binary change', 'Inherited descriptive variant label called history arms Native current residency; clarified subsequent metadata while retaining original configs and actual authoritative STRATA environment unchanged', 'Initial staged publication audit rejected full source-file inventory as ordinary row-level JSON; unchanged original remains local and its complete verified gzip is published, compact summary links to it'], 'unmeasured_or_skipped':['Full unrelated native test suite','Live logistic sensitivity: optional, offline parity complete','Exact attribution of all plan A delay to oracle CPU or whole-request critical path; shared/peer overlap gives bounds','Exclusive per-entry nonlocal service economics,160us remains an assumption','DMA-only H2D duration or peak bus saturation','Full native adaptation CPU outside routed host plan','Fresh independent source: reused previously evaluated RFC8259, no new-generalization claim','Natural-generation output quality or bitwise CPU/GPU equivalence','Longer context/model or production deployment','Independent off-host backup for irreplaceable raw binary tapes/journals']}
 save(C/'completion-audit.json',result);print('SCIENTIFIC AUDIT PASS; commit/push pending',flush=True)
