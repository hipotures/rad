#!/usr/bin/env python3
"""Run required controller/store diagnostics only after the core supervisor is terminal."""
import importlib.util, json, os, pathlib, shutil, subprocess, sys, time
ROOT=pathlib.Path(__file__).resolve().parent
run=pathlib.Path(sys.argv[1]).resolve();core_pid=int(sys.argv[2])
# The transient scope worker is reparented to the user manager. Include its actual
# PID through our unique owned scope, instead of reporting only systemd-run RSS.
_original_snapshot=None
spec=importlib.util.spec_from_file_location('campaign',ROOT/'campaign.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
config=json.loads((run/'campaign_config.json').read_text());deadline=config['created_wall']+config['max_campaign_seconds']
_original_snapshot=m.snapshot
_scope=pathlib.Path('/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/app.slice')/('hwchar-monitor-'+run.name+'.scope')
def scope_worker_snapshot(pids=()):
 actual=[];quota=None
 try:
  for pid in map(int,(_scope/'cgroup.procs').read_text().split()):
   if pathlib.Path('/proc/'+str(pid)+'/exe').readlink()==ROOT/'operations':actual.append(pid)
  quota=(_scope/'cpu.max').read_text().strip()
 except (FileNotFoundError,ProcessLookupError,PermissionError):pass
 row=_original_snapshot(sorted(set(pids)|set(actual)))
 if actual:row['owned_scope']={'path':str(_scope),'worker_pids':actual,'cpu_max':quota}
 return row
m.snapshot=scope_worker_snapshot
cases=[]
def add(id,args,**kw):cases.append({'id':id,'family':kw.pop('family','I'),'args':args,'seconds':kw.pop('seconds',20),'warmup':15,'repeats':kw.pop('repeats',3),'headline':False,'binary':kw.pop('binary','operations'),**kw})
for op in ['inclusive','pack','exchange']:add('immutable-store-'+op,['--mode','store','--op',op])
add('rolling-monitor-ranked',['--mode','monitor'])
add('rolling-monitor-cooperative',['--mode','monitor','--op','cooperative'],nice=10)
add('rolling-monitor-cgroup25',['--user','--scope','--quiet','--collect','--expand-environment=no','--unit=hwchar-monitor-'+run.name,'-p','CPUQuota=25%',str(ROOT/'operations'),'--mode','monitor'],binary='systemd-run',cpu_quota='25000 100000')
for arm in ['A','B']:add('rolling-monitor-interference-'+arm,['--mode','ram','--op','triad','--threads','8','--bytes',str(1<<30)],pair='rolling-monitor',arm=arm,**({'sidecar':['--mode','monitor','--op','cooperative']} if arm=='B' else {}))
for storage in ['virtiofs','ext4']:add('pipeline-stage-diagnostic-'+storage,['--mode','pipeline-stages','--bytes',str(3<<20),'--buffers','3'],family='G',storage=storage,instrumented=True)
add('burst-timeseries-diagnostic',['--mode','gemm','--op','small','--rate',str(100<<20),'--burst',str(3000<<20)],family='H',seconds=60,repeats=1,instrumented=True)
for storage in ['virtiofs','ext4']:add('reverse-active-'+storage,['--mode','reverse','--bytes',str(3<<20)],family='G',storage=storage,write=True,instrumented=True)
cases.append({'id':'ram-read-t1','family':'B','args':['--mode','ram','--op','read','--threads','1','--bytes',str(1<<30)],'seconds':20,'warmup':15,'repeats':1,'replacement_repetition':3,'binary':'hwbench','headline':False})
# Two extra unchanged-binary paired repetitions investigate noisy small-dispatch results.
core_cases={c['id']:c for c in json.loads((run/'plan.json').read_text())['scenarios']}
for extra_rep in [4,5]:
 for arm in ['A','B']:
  extra=dict(core_cases['interference-dispatch-524288000-'+arm],repeats=1,replacement_repetition=extra_rep,binary='hwbench',anomaly_followup=True)
  cases.append(extra)
# Fix duplicate keyword above through a simple setter-friendly helper.
plan={'scenarios':cases,'estimated_seconds':sum((c['seconds']+c['warmup']+4)*c['repeats'] for c in cases)+180,'deadline_wall':deadline,'core_pid':core_pid,'ordering':'build/smoke only when core PID is absent and progress is terminal; then sequential scenarios; no performance pooled across binary hashes'}
m.atomic(run/'followup-plan.json',plan);progress={'status':'WAITING_CORE','core_pid':core_pid,'followup_pid':os.getpid(),'completed':[],'pending':cases};m.atomic(run/'followup-progress.json',progress)
while True:
 if m.STOP:raise SystemExit(130)
 try:os.kill(core_pid,0);live=True
 except ProcessLookupError:live=False
 if not live:break
 if time.time()>deadline:raise RuntimeError('campaign deadline before core completion')
 print('Waiting for verified live core PID '+str(core_pid),flush=True);time.sleep(10)
core=json.loads((run/'progress.json').read_text())
if core['status']!='MEASUREMENTS_COMPLETE':raise RuntimeError('core did not complete safely: '+core['status'])
m.atomic(run/'core-progress-snapshot.json',core)
if m.sha(ROOT/'hwbench')!=config['code_hash'] or m.sha(ROOT/'campaign.py')!=config['python_hash']:raise RuntimeError('frozen core identity changed')
progress['status']='BUILDING';m.atomic(run/'followup-progress.json',progress)
cmd=['/usr/local/cuda/bin/nvcc','-O3','-std=c++17','-arch=sm_89','-Xcompiler=-fopenmp','-Xcompiler=-pthread',str(ROOT/'src/operations.cu'),'-lcublas','-o',str(ROOT/'operations')]
p=subprocess.run(cmd,capture_output=True,text=True,timeout=180);m.atomic(run/'raw/followup-build.json',{'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0
ops_config=dict(config,code_hash=m.sha(ROOT/'operations'),source_hash=m.sha(ROOT/'src/operations.cu'),followup_orchestrator_hash=m.sha(pathlib.Path(__file__)),frozen_common_source_hash=m.sha(ROOT/'src/hwbench.cu'),instrumented_common_source_hash=m.sha(ROOT/'src/operations-common.cuh'))
m.atomic(run/'followup-config.json',ops_config)
for f in ['operations','src/operations.cu','src/operations-common.cuh','followup.py']:shutil.copy2(ROOT/f,run/'code'/pathlib.Path(f).name)
for args in [['--mode','monitor'],['--mode','store','--op','pack'],['--mode','store','--op','exchange'],['--mode','pipeline-stages','--file',config['scratch']['ext4']+'/corpus.bin','--bytes',str(3<<20),'--buffers','3']]:
 cmd=[str(ROOT/'operations')]+args+['--seconds','.5','--warmup','.1'];p=subprocess.run(cmd,capture_output=True,text=True,timeout=30);path=run/'raw'/('followup-smoke-'+args[1]+('-'+args[3] if args[1]=='store' else '')+'.json');m.atomic(path,{'status':'SMOKE','command':cmd,'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0
jobs=[(c,r) for c in cases for r in range(1,c['repeats']+1)]
jobs.sort(key=lambda cr:(0 if not cr[0].get('pair') else 1,cases.index(cr[0]) if not cr[0].get('pair') else min(i for i,c in enumerate(cases) if c.get('pair')==cr[0]['pair']),cr[0].get('replacement_repetition',cr[1]),0 if cr[0].get('arm')==('A' if cr[0].get('replacement_repetition',cr[1])%2 else 'B') else 1))
existing=[json.loads(x) for x in (run/'results.jsonl').read_text().splitlines()]
successful={(x['scenario_id'],x['repetition'],x.get('software_identity')) for x in existing if x['status']=='OK' and (x.get('cohort')=='controller-store-diagnostics' or x.get('cohort') in ['core-replacement','core-anomaly-repeat'])}
for case,repetition in jobs:
 if m.STOP:raise SystemExit(130)
 rep=case.get('replacement_repetition',repetition)
 expected_hash=config['code_hash'] if case['binary']=='hwbench' else ops_config['code_hash']
 if (case['id'],rep,expected_hash) in successful:continue
 progress.update(status='RUNNING',running={'scenario_id':case['id'],'repetition':rep});m.atomic(run/'followup-progress.json',progress)
 if time.time()+case['seconds']+case['warmup']+5>deadline:record={'scenario_id':case['id'],'repetition':rep,'case':case,'status':'SKIPPED_TIME_BUDGET','reason':'shared campaign deadline'}
 else:
  m.BIN=pathlib.Path('/usr/bin/systemd-run') if case['binary']=='systemd-run' else ROOT/case['binary'];effective=config if case['binary']=='hwbench' else ops_config
  record=m.run_one(run,effective,case,rep)
  record['cohort']='core-anomaly-repeat' if case.get('anomaly_followup') else 'core-replacement' if case['binary']=='hwbench' else 'controller-store-diagnostics'
  record['followup_orchestrator_hash']=ops_config['followup_orchestrator_hash']
 with open(run/'results.jsonl','a') as f:f.write(json.dumps(record)+'\n');f.flush();os.fsync(f.fileno())
 progress['completed'].append({'id':case['id'],'repetition':rep,'status':record['status']});progress['running']=None;progress['pending']=[{'id':c['id'],'repetition':r} for c,r in jobs if not any(x['id']==c['id'] and x['repetition']==c.get('replacement_repetition',r) and x['status']=='OK' for x in progress['completed'])];m.atomic(run/'followup-progress.json',progress)
 if record['status'] in ['VERIFICATION_FAILED','SKIPPED_SAFETY','CONTAMINATED','INTERRUPTED']:raise RuntimeError('followup stopped: '+record['status'])
progress.update(status='MEASUREMENTS_COMPLETE',pending=[],running=None);m.atomic(run/'followup-progress.json',progress)
core['followup_status']='MEASUREMENTS_COMPLETE';m.atomic(run/'progress.json',core)
print('FOLLOWUP_MEASUREMENTS_COMPLETE',flush=True)
