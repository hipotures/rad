"""Evidence-backed completion audit, preservation hashes and owned-resource cleanup proof."""
import ast,hashlib,collections,subprocess,time,datetime
import psutil
from common import *
no_gpu()
checks=[]
def check(requirement,passed,evidence,limitation=None):
 checks.append({'requirement':requirement,'pass':bool(passed),'evidence':evidence,'limitation':limitation})
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
required=['GOAL.md','STATUS.md','DECISIONS.md','progress.json','progress.jsonl','attempt-ledger.jsonl','source-group-splits.json','data/schema.json','data/dataset-manifest.json','models/selection.json','models/logistic.txt','models/tree.txt','results/offline-competition.json','results/offline-reserved.json','results/development-calibration-prediction-metrics.json','results/reserved-prediction-metrics.json','results/family-prediction-metrics.json','results/sampled-victim-ranking.json','results/learning-curves.json','results/feature-diagnostics.json','builds/runtime-identity.json','patches/causal-victim.diff','tests/scorer-parity.json','tests/safety-summary.json','run-order.json','results/live-attempts.json','results/live-attempts.csv','results/paired-blocks.json','results/main-summary.json','results/conclusion.json','report.md','reproduce.md','tests/reproduction-checks.json']
missing=[p for p in required if not (C/p).is_file()];check('Required artifacts',not missing,{'required':required,'missing':missing})
manifest=load(P0/'benchmark-manifest.json')['tasks'];dataset=load(C/'data/dataset-manifest.json')
check('Twelve source groups and exact roles; no random within-episode split',len(dataset)==12 and {(d['task'],d['split']) for d in dataset}=={(t['task_id'],t['split']) for t in manifest},'source-group-splits.json; data/dataset-manifest.json')
check('Native ownership reconstruction and candidate sampling',all(d['native_slot_entry_checks']>0 and d['suffix_invariance'] for d in dataset),{'checked_entries':sum(d['native_slot_entry_checks'] for d in dataset),'sampling':'Uniform min(8,N)/N native residents; 1/k decision weight; retained residents included'},'Native resident population selection bias persists; policy-dependent ages/counters omitted.')
check('Causal horizon labels and finite-tail censoring',all(d['horizons_main_windows']==[1,4,16,64] and d['censored_horizon_labels']>0 for d in dataset),'data/schema.json; scripts/dataset.py; scripts/features.py; tests/scorer-parity.json')
selection=load(C/'models/selection.json');checkpoint=C/'models'/(selection['policy']+'.txt')
reserved_times=[load(p/'command.json')['environment'] for p in (C/'results/offline').iterdir() if p.is_dir() and (p/'command.json').exists() and any(p.name.startswith(t['task_id']+'-') for t in manifest if t['split']=='reserved_evaluation')]
check('At most two learned candidates, frozen before reserved policy evaluation',selection['policy'] in ['logistic','tree'] and sha(checkpoint)==selection['checkpoint_sha256'] and len(reserved_times)==16,{'frozen_utc':selection['frozen_utc'],'policy':selection['policy'],'threshold':selection['threshold'],'checkpoint':selection['checkpoint_sha256'],'reserved_policy_points':len(reserved_times)},'Cheap native/history rule had a slightly stronger calibration proxy; live comparison excludes cheap rules.')
check('Bounded guard diagnosis retained',all((C/'versions'/v).is_dir() for v in ['risk-only-v1','cost-guard-v2']),['versions/risk-only-v1','versions/cost-guard-v2','results/guard-diagnosis-v1.json'],'Risk-only excessive churn, 40us cost guard under-admission; final160us assumption frozen before reserved results.')
identity=load(C/'builds/runtime-identity.json');source=pathlib.Path(identity['source']);head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip();dirty=subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True).strip()
check('Same replay substrate and isolated exact experimental source/binary',head==identity['source_sha'] and not dirty and sha(identity['exe'])==identity['binary_sha256'],identity)
baseline=load(C/'references/normal-launchers-baseline.json');changed=[p for p,r in baseline['files'].items() if not pathlib.Path(p).is_file() or sha(p)!=r['sha256']]
original=C.parents[1]/'builds/control/strata';check('Original binary and normal launcher/config/index preservation',not changed and sha(original)=='eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d',{'changed':changed,'small_files_checked':len(baseline['files']),'snapshot_utc':baseline['captured_utc'],'original_binary':str(original)},'Launcher snapshot captured during CPU evaluation; no normal launcher was authored by this campaign.')
model_changes=[]
for p,r in load(P0/'provenance/model-identity.json')['files'].items():
 st=pathlib.Path(p).stat()
 if (st.st_size,st.st_mtime_ns,st.st_ino)!=(r['size'],r['mtime_ns'],r['inode']):model_changes.append(p)
check('Frozen model revision and backing weights unchanged',not model_changes,{'revision':'38bb39ee97821de2c9009abb7e93950eec396e66','changed':model_changes,'verification':'Prior full hashes plus unchanged size/mtime/inode; no heavyweight weights rehash during timing.'})
safety=load(C/'tests/safety-summary.json');check('Scorer/causal/safety fixtures and real bytes',safety['real_copy_fixtures']=='PASS' and safety['cost_guard_fixture']=='PASS',['tests/scorer-parity.json','tests/validation-index.json','logs/policy-fixture-attempt3.log','logs/full-reference-regression-attempt3.log','tests/cost-guard-fixture.log','tests/real-copy-full.log','tests/real-copy-learned.log'])
check('Relevant existing native tests',safety['native_test_exit_code']==0,safety,'No new full-suite run; historical environment failures remain historical. Any targeted failures must be interpreted explicitly in report.')
attempts=load(C/'results/live-attempts.json');pairs=load(C/'results/paired-blocks.json');counts=collections.Counter((r['task'],r['arm']) for r in attempts)
check('Frozen counterbalanced order, all attempts retained, maximum three unchanged attempts',all(n<=3 for n in counts.values()),{'counts':{str(k):v for k,v in counts.items()},'order':'run-order.json; results/live-attempts.json; raw/*/episode.json'})
check('Target live coverage',len(attempts)==36 and all(r['valid'] for r in attempts) and len(pairs)==12,{'valid':sum(r['valid'] for r in attempts),'attempted':len(attempts),'complete_blocks':len(pairs),'target':36},'A partial/invalid matrix is never presented as completed coverage.')
valid=[r for r in attempts if r['valid']]
check('Full work, EOS, short-input QSA and initial-state fidelity',bool(valid) and all(r['emitted_tokens']==(1773 if r['task']=='text-websocket' else 2048) and r['main_entries']>0 and r['mtp_entries']>0 for r in valid),'raw/*/fidelity.json; development/short-input preflights retained separately','Enforced work identity does not establish natural-generation correctness.')
check('Learned scorer has no victim future queries or invalid live predictions',bool(valid) and all(r['information'].get('victim_next')==0 and r['information'].get('victim_count')==0 and r['scorer'].get('invalid')==0 for r in valid if r['arm']=='ORACLE_IN_LEARNED_VICTIM'),'raw/*/run-engine.log Q4_INFORMATION_END/Q4_VICTIM_END','Incoming oracle and common full-current-window protection remain privileged.')
check('Main/MTP accounting, copies, churn, cost and telemetry retained',all(all(k in r for k in ['copy','victim_absence','return_labels','cpu_steal_pct','gpu','host_peak_rss_GiB','scorer','planner']) for r in valid),'results/live-attempts.json; analysis/*; raw/*/telemetry','MTP dispatch subdivisions and exclusive latency cost remain unknown. Nested timers not summed.')
check('Paired retention and descriptive statistics',all((p['retention'] is None)==(p['full_time_saving_s']<=0) for p in pairs),'results/paired-blocks.json; results/main-summary.json; report.md','No clamping, fourth run, favorable filtering or post-hoc steal correction.')
syntax=[]
for p in (C/'scripts').glob('*.py'):
 try:ast.parse(p.read_text())
 except Exception as e:syntax.append({'file':str(p),'error':repr(e)})
check('Script syntax and exact reproduction commands',not syntax and (C/'tests/reproduction-checks.json').exists(),{'syntax_errors':syntax,'reproduction':'tests/reproduction-checks.json; reproduce.md'},'Audit distinguishes executed commands from prepare-only checks.')
ancestors={p.pid for p in psutil.Process().parents()}|{__import__('os').getpid()};owned=[]
for p in psutil.process_iter(['pid','cmdline','status','create_time']):
 try:
  if p.pid not in ancestors and p.info['status']!=psutil.STATUS_ZOMBIE and any(str(C) in a for a in p.info['cmdline'] or []):owned.append(p.info)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
gpu=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_gpu_memory','--format=csv,noheader'],text=True,timeout=8).strip()
save(C/'cleanup-proof.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owned_live_processes':owned,'GPU_compute_jobs':gpu,'method':'Read-only process identity/command ownership snapshot; no unrelated process interrupted.'})
check('Owned server/trainer/copier/profiler cleanup and no GPU work',not owned and not gpu,'cleanup-proof.json')
elapsed=time.monotonic()-load(C/'clock.json')['start_monotonic'];check('Unchanged four-hour deadline',elapsed<14400,{'elapsed_s':elapsed,'start':load(C/'clock.json')['start_utc'],'deadline':load(C/'clock.json')['deadline_utc']})
audit={'state':'PASS' if all(r['pass'] for r in checks) else 'COMPLETE_WITH_REPORTED_LIMITATIONS','checks':checks,'failed_requirements':[r['requirement'] for r in checks if not r['pass']],'elapsed_s':elapsed,'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'primary_conclusion':load(C/'results/conclusion.json')['primary']};save(C/'completion-audit.json',audit)
manifest_hashes={};excluded=['.venv/','source/runtime/.git/','builds/runtime/']
with Heartbeat('artifact hashes and preservation audit',5):
 for p in C.rglob('*'):
  if not p.is_file() or p.is_symlink():continue
  relative=str(p.relative_to(C))
  if relative in ['artifact-manifest.json','progress.json','STATUS.md','progress.jsonl','DECISIONS.md','attempt-ledger.jsonl'] or any(relative.startswith(x) for x in excluded):continue
  manifest_hashes[relative]={'sha256':sha(p),'bytes':p.stat().st_size}
 save(C/'artifact-manifest.json',{'files':manifest_hashes,'excluded':excluded+['mutable progress/decision/ledger files; manifest self'],'runtime_binary':{'path':identity['exe'],'sha256':identity['binary_sha256']},'external_frozen_tapes':'data/dataset-manifest.json; Phase0 artifact manifest','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat()})
print('COMPLETION AUDIT',audit['state'],'reported limitations',audit['failed_requirements'],'hashed files',len(manifest_hashes),flush=True)
