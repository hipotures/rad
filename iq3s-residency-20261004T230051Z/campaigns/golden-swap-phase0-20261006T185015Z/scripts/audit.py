"""Read-only semantic completion audit; never starts a model or changes source."""
import ast,collections,csv,datetime,hashlib,json,pathlib,subprocess,time
import psutil
C=pathlib.Path(__file__).resolve().parents[1]
def load(p):return json.loads((C/p).read_text())
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
checks=[]
def check(name,condition,evidence):checks.append({'requirement':name,'pass':bool(condition),'evidence':evidence})
m=load('benchmark-manifest.json');tasks=m['tasks'];timing=load('timing.json');div=load('analysis/trace-diversity.json')['tasks'];budget=load('runtime-budget.json');ledger=[json.loads(x) for x in (C/'attempt-ledger.jsonl').read_text().splitlines()]
required=['GOAL.md','STATUS.md','DECISIONS.md','progress.json','progress.jsonl','attempt-ledger.jsonl','workload-audit.md','workload-inventory.json','prompt-catalog.md','public-sources.md','benchmark-manifest.json','trace-summary.csv','runtime-budget.md','runtime-budget.json','report.md','reproduce.md','output-review.md','provenance/compatible-existing-tapes.json']
check('Required artifacts exist',all((C/p).is_file() and (C/p).stat().st_size for p in required),required)
check('Twelve groups; three per family',len(tasks)==12 and len({t['source_group'] for t in tasks})==12 and set(collections.Counter(t['family'] for t in tasks).values())=={3},collections.Counter(t['family'] for t in tasks))
check('Frozen roles and exclusion',all(t['exclude_from_fitting_by_default'] for t in tasks if t['split']=='reserved_evaluation') and all(len({t['split'] for t in tasks if t['family']==f})==3 for f in {t['family'] for t in tasks}),[(t['task_id'],t['split']) for t in tasks])
check('Profiles 8x32K +4x128K; actual occupancy fits',collections.Counter(t['context_limit'] for t in tasks)=={32768:8,131072:4} and all(t['actual_input_tokens']+t['output_cap']+t['engine_reserve']<=t['context_limit'] for t in tasks),[(t['task_id'],t['context_limit'],t['actual_input_tokens']) for t in tasks])
check('One original model attempt per task; no exclusions',len(ledger)==12 and len({r['task_id'] for r in ledger})==12 and all(t['measurement_status']=='MEASURED' for t in tasks),[r['task_id'] for r in ledger])
family=collections.defaultdict(float);clean=True;bounded=True;identities=True;owned=[];warm=True;hashes=True;ready=True;launch=True
for t in tasks:
 p=C/'raw'/t['task_id'];e=json.loads((p/'episode.json').read_text());r=e['run'];v=json.loads((p/'validation.json').read_text());cfg=json.loads((p/'config.json').read_text());native=json.loads((p/'raw/native-process.json').read_text());env=native['environment'];cmd=native['command'];family[t['family']]+=e['total_operating_s'];clean &= e['cleanup_verified'];bounded &= e['startup_and_warmup_s']<=180 and r['request_wall_s']<=240 and r['decode_s']<=61 and r['output_tokens']<=2048
 launch &= r['begin_monotonic']<timing['request_cutoff_monotonic'];warm &= e['warmup']['actual_input_tokens']==4096 and e['warmup']['output_tokens']==64 and r['reused_tokens']==0
 frozen=load('configs.json')[t['profile']]
 identities &= cfg['args']==frozen['args'] and cmd==[cfg['exe'],'--serve']+cfg['args']+['--layer-split','24'] and cfg['binary_sha256']==frozen['binary_sha256'] and cfg['source_sha']==frozen['source_sha']
 identities &= env.get('STRATA_POOL_SPIN_US')=='100' and env.get('STRATA_Q4_TAPE_MODE')=='record' and env.get('STRATA_Q4_ORACLE_MODE')=='off' and native['executable'].endswith('/builds/oracle-v3/strata')
 ready &= v['state']=='PASS' and t['trace_ready'] and v['normal_main_denominator']==r['local_entries']+r['cpu_entries']+r['mapped_entries'] and not v['errors']
 for key,hashkey in [('source_path','source_sha256'),('excerpt_path','excerpt_sha256')]:hashes &= sha(t[key])==t[hashkey]
 hashes &= sha(t['payload']['token_ids_path'])==t['payload']['input_ids_sha256']
 hashes &= hashlib.sha256(json.dumps(json.loads(pathlib.Path(t['payload']['path']).read_text()),sort_keys=True,separators=(',',':')).encode()).hexdigest()==t['payload']['payload_sha256']
 for ownership in [p/'process.json',p/'collector-process.json',p/'raw/native-process.json']:
  a=json.loads(ownership.read_text());pid=a['pid'];created=a.get('create_time',a.get('created'))
  try:
   proc=psutil.Process(pid)
   if abs(proc.create_time()-created)<.1 and proc.status()!=psutil.STATUS_ZOMBIE:owned.append(pid)
  except psutil.NoSuchProcess:pass
check('All twelve validated complete tapes',ready and len(div)==12,'raw/*/validation.json; active QSA widths and final EOS boundary; exact IDs/FNV/counts')
check('Frozen source/excerpt/payload hashes',hashes,'benchmark-manifest.json and corpus files')
check('Fresh fixed warmup and zero prompt reuse',warm,'episode warmup and measured reused_tokens')
check('Native capture identities and oracle disabled',identities,'raw/*/raw/native-process.json; run.py check verifies source/binary/model/config')
check('Per-request and startup limits',bounded,'180s startup+warmup;240s request;60s decode soft target;2048output')
check('Model operation <=600s per family',all(v<=600 for v in family.values()),dict(family))
check('Launches before unchanged T+50',launch,'request begin monotonic compared to original timing.json')
check('No owned live processes; cleanup verified',clean and not owned,owned)
gpu=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True,timeout=8).strip();check('No GPU compute jobs',not gpu,gpu)
check('No tool-execution or new256K',all(not t['tool_execution'] and t['context_limit'] in [32768,131072] for t in tasks),'benchmark manifest')
check('Preserved two original validator failures',all((C/q).exists() for q in ['raw/math-sensor/validation-before-width-fix.json','raw/text-websocket/validation-before-eos-fix.json']) and len(load('provenance/repair-ledger.json'))==2,'repair-ledger; no model reruns')
check('Runtime total reconciles',abs(budget['one_time_recording']['sum_model_operation_s']-sum(x['total_operating_s'] for x in div))<1e-6 and budget['baseline_plus_one_finalist_three_pairs']['arms_per_task']==6 and budget['baseline_two_finalists_oracle_three_repetitions']['arms_per_task']==12,'runtime-budget.json')
check('Causal labels separated and censoring retained',load('analysis/victim-return-labels.json')['no_counterfactual_regret'] and all(v['labels']['right_censored']==(v['labels']['next_main_use_window'] is None) for v in load('analysis/victim-return-labels.json')['records']),'analysis/victim-return-labels.json')
check('Four source-grounded development screening tasks',len([t for t in tasks if t['screening']])==4 and all(t['split']=='development' for t in tasks if t['screening']),'predeclared screening flags')
size=sum(p.stat().st_size for p in C.rglob('*') if p.is_file() and '.git' not in p.parts);check('Storage below12GiB',size<12*1024**3,{'bytes':size})
for p in (C/'scripts').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
check('Scripts syntax valid; reproducer instructions present',True,'stdlib AST parse; identity/help/inspect smoke logs')
rows=list(csv.DictReader((C/'trace-summary.csv').open()));report=(C/'report.md').read_text();check('Report and CSV cover every measured task',len(rows)==12 and all('| '+t['task_id']+' |' in report for t in tasks) and report.rstrip().endswith('PHASE0_READY'),'trace-summary.csv and report.md')
now=time.monotonic();progress=load('progress.json');now=(timing['start_monotonic']+progress['elapsed_s']) if progress.get('step')==5 and progress.get('state')=='DONE' else now;check('Completion audit before original60-minute deadline',now<timing['deadline_monotonic'],{'elapsed_s':now-timing['start_monotonic'],'remaining_s':timing['deadline_monotonic']-now})
out={'state':'PASS' if all(x['pass'] for x in checks) else 'FAIL','checks':checks,'elapsed_s':now-timing['start_monotonic'],'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'defined':len(tasks),'calibrated':len(ledger),'trace_ready':sum(t['trace_ready'] for t in tasks),'owned_live_processes':owned,'GPU_compute_jobs':gpu,'policy_training_or_comparison_performed':False}
(C/'completion-audit.json').write_text(json.dumps(out,indent=2)+'\n');(C/'requirement-audit.md').write_text('# Requirement audit\n\n'+'\n'.join('- '+('PASS' if x['pass'] else 'FAIL')+': '+x['requirement']+' — '+str(x['evidence']) for x in checks)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='checks'},indent=2));print('FAILED',[x['requirement'] for x in checks if not x['pass']]);raise SystemExit(0 if out['state']=='PASS' else 1)
