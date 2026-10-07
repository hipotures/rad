"""Evidence-backed completion audit, preservation hashes and owned-resource cleanup proof."""
import ast,hashlib,collections,subprocess,time,datetime
import psutil
from common import *
no_gpu()
checks=[]
def check(requirement,passed,evidence,limitation=None):
 checks.append({'requirement':requirement,'pass':bool(passed),'evidence':evidence,'limitation':limitation})
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  while chunk:=f.read(8*1024*1024):h.update(chunk)
 return h.hexdigest()
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
safety=load(C/'tests/safety-summary.json');check('Scorer/causal/safety fixtures and real bytes',safety['real_copy_fixtures']=='PASS' and safety['cost_guard_fixture']=='PASS',['tests/scorer-parity.json','tests/validation-index.json','logs/policy-fixture-attempt3.log','logs/full-reference-regression-attempt3.log','tests/cost-guard-fixture-attempt2.log','tests/real-copy-full-attempt2.log','tests/real-copy-learned-attempt2.log'],'Initial learned fixture failure preserved; fixture event advancement repaired with runtime/checkpoint unchanged.')
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
repro=load(C/'tests/reproduction-checks.json')
check('Script syntax and exact reproduction commands',not syntax and repro['state']=='PASS' and all(r['state']=='PASS' for r in repro['checks']) and {r['arm'] for r in repro['checks'] if 'arm' in r}=={'REPLAY_CURRENT','ORACLE_FULL','ORACLE_IN_LEARNED_VICTIM'}, {'syntax_errors':syntax,'reproduction':'tests/reproduction-checks.json; reproduce.md; references/reproduction-artifacts.json'},'Audit distinguishes executed commands from prepare-only checks.')
all_counts=collections.Counter(counts)
for r in load(C/'phase-a/preflight-summary.json'):all_counts[r['task'],r['arm']]+=1
for r in repro['checks']:
 if 'arm' in r:all_counts[r['task'],r['arm']]+=1
check('Attempt cap includes matching preflights and reproductions',all(n<=3 for n in all_counts.values()),{'combined_counts':{str(k):v for k,v in all_counts.items()},'main_requests':36,'preflights':4,'development_reproduction_requests':3})
references=load(C/'references/reproduction-artifacts.json');bad_repro=[]
for ref in references:
 for relative,stamp in ref['files'].items():
  p=pathlib.Path(ref['directory'])/relative
  if not p.is_file() or sha(p)!=stamp['sha256']:bad_repro.append(str(p))
check('External isolated reproduction evidence preserved',len(references)==3 and not bad_repro,{'manifest':'references/reproduction-artifacts.json','changed':bad_repro})
episode_identity_errors=[]
for r in attempts:
 e=load(C/'raw'/r['label']/'episode.json');run=e['run'];config=run['full_config']
 if run['source_sha']!=identity['source_sha'] or run['binary_sha256']!=identity['binary_sha256'] or config['model_revision']!='38bb39ee97821de2c9009abb7e93950eec396e66':episode_identity_errors.append(r['label'])
check('Every main request has the same frozen measurement identity',not episode_identity_errors,{'errors':episode_identity_errors,'base_configs_sha256':identity['base_configs_sha256'],'frozen_selection_sha256':identity['frozen_selection_sha256']})
check('Finite completion and charged host/spares',all(r['copy']['pending_at_end']==0 and r['copy']['native_pending_bytes']==0 and r['scorer']['host_bytes']==2163920 and r['planner']['active_spares']==(0 if r['arm']=='REPLAY_CURRENT' else 5) for r in attempts),'results/live-attempts.json; results/final-diagnostics.json','Prefix-history update time has no separate counter; charged in decode/wall. No GPU scorer buffers.')
table_errors=[];lines=(C/'report.md').read_text().splitlines();width=None
for number,line in enumerate(lines,1):
 if not line.startswith('|'):width=None;continue
 cells=line.count('|')-1
 if width is None:width=cells
 elif width!=cells:table_errors.append({'line':number,'expected':width,'actual':cells})
check('Report tables align and primary interpretation is preserved',not table_errors and 'MECHANISM_IMPROVED_NO_CONFIRMED_LATENCY_GAIN' in (C/'report.md').read_text(),{'table_errors':table_errors,'report':'report.md'})
# Verify the authoritative prior campaign against its existing immutable-artifact hashes.
prior_changes=[];prior=load(P0/'artifact-manifest.json')['files']
with Heartbeat('verify preservation of Phase0 artifacts',5):
 for stamp in prior:
  p=P0/stamp['relative_path']
  if not p.is_file() or p.stat().st_size!=stamp['bytes'] or sha(p)!=stamp['sha256']:prior_changes.append(str(p))
check('Prior Phase0 datasets/results/source artifacts preserved',not prior_changes,{'checked_files':len(prior),'changed':prior_changes,'authority':str(P0/'artifact-manifest.json')})
ancestors={p.pid for p in psutil.Process().parents()}|{__import__('os').getpid()};owned=[]
for p in psutil.process_iter(['pid','cmdline','status','create_time']):
 try:
  if p.pid not in ancestors and p.info['status']!=psutil.STATUS_ZOMBIE and any(str(C) in a for a in p.info['cmdline'] or []):owned.append(p.info)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
gpu=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_gpu_memory','--format=csv,noheader'],text=True,timeout=8).strip()
save(C/'cleanup-proof.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owned_live_processes':owned,'GPU_compute_jobs':gpu,'method':'Read-only process identity/command ownership snapshot; no unrelated process interrupted.'})
check('Owned server/trainer/copier/profiler cleanup and no GPU work',not owned and not gpu,'cleanup-proof.json')
elapsed=time.monotonic()-load(C/'clock.json')['start_monotonic'];check('Unchanged four-hour deadline',elapsed<14400,{'elapsed_s':elapsed,'start':load(C/'clock.json')['start_utc'],'deadline':load(C/'clock.json')['deadline_utc']})
coverage={
 '1':{'state':'complete','evidence':'GOAL.md; report.md; results/conclusion.json'},
 '2':{'state':'complete','evidence':'clock.json; progress.jsonl; STATUS.md; unchanged original clock'},
 '3':{'state':'complete','evidence':'references/*; runtime identity; prior artifact and launcher preservation checks'},
 '4':{'state':'complete','evidence':'source-group-splits.json; dataset manifests'},
 '5':{'state':'complete','evidence':'data/schema.json; native ownership checks; sampling probabilities; scorer parity'},
 '6':{'state':'complete_with_documented_ordering_deviation','evidence':'censoring masks; schema; data/math-rational-smoke-manifest.json; compiled smoke after bounded fit; report.md'},
 '7':{'state':'complete','evidence':'two retained models; fixed seed/dependencies; learning curves and feature diagnostics'},
 '8':{'state':'complete','evidence':'source patch; matched guards/controls; real NO_SWAP and zero victim future queries'},
 '9':{'state':'complete','evidence':'offline results; frozen selection; negative v1/v2 diagnosis preserved'},
 '10':{'state':'complete','evidence':'same binary/source; five charged spares; host bytes; safety fixtures'},
 '11':{'state':'complete','evidence':'all fidelity JSON; scorer/copy/ownership/cancellation tests; nine native tests'},
 '12':{'state':'complete','evidence':'36 valid requests; four reserved tasks; three adjacent blocks each; optional TLS unmeasured'},
 '13':{'state':'complete','evidence':'combined attempt-cap audit; serial run ledger; finite owned-process cleanup'},
 '14':{'state':'complete_with_explicit_unknowns','evidence':'per-arm raw logs, timings/copies/telemetry; final diagnostics; missing exclusive costs and MTP subdivisions explicitly unknown'},
 '15':{'state':'complete','evidence':'negative/inconsistent latency result retained; limitations and strongest next experiment in report'},
 '16':{'state':'complete','evidence':'artifact manifest; exact tested reproducers; report; cleanup proof'}
}
audit={'state':'COMPLETE_WITH_DOCUMENTED_PROTOCOL_DEVIATION' if all(r['pass'] for r in checks) else 'AUDIT_FAILED','checks':checks,'failed_requirements':[r['requirement'] for r in checks if not r['pass']],'requirement_sections':coverage,'protocol_deviations':['Dataset/state smoke preceded fit, but first compiled scorer/policy end-to-end smoke followed the larger bounded fit. Ordering cannot be retroactively repaired and is disclosed.'],'elapsed_s':elapsed,'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'primary_conclusion':load(C/'results/conclusion.json')['primary']};save(C/'completion-audit.json',audit)
manifest_hashes={};excluded=['.venv/','source/runtime/.git/','builds/runtime/']
with Heartbeat('artifact hashes and preservation audit',5):
 for p in C.rglob('*'):
  if not p.is_file() or p.is_symlink():continue
  relative=str(p.relative_to(C))
  if relative in ['artifact-manifest.json','progress.json','STATUS.md','progress.jsonl','DECISIONS.md','attempt-ledger.jsonl'] or any(relative.startswith(x) for x in excluded):continue
  manifest_hashes[relative]={'sha256':sha(p),'bytes':p.stat().st_size}
 save(C/'artifact-manifest.json',{'files':manifest_hashes,'excluded':excluded+['mutable progress/decision/ledger files; manifest self'],'runtime_binary':{'path':identity['exe'],'sha256':identity['binary_sha256']},'external_frozen_tapes':'data/dataset-manifest.json; Phase0 artifact manifest','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat()})
print('COMPLETION AUDIT',audit['state'],'reported limitations',audit['failed_requirements'],'hashed files',len(manifest_hashes),flush=True)
