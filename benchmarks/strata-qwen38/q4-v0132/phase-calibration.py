"""Upstream calibration, then sequential local actual64K screens; no Cartesian product."""
import run as r,json,copy,time,subprocess,os,signal
assert json.loads((r.ROOT/'raw/phase-placement-terminal.json').read_text())['status']=='COMPLETE'
policy=json.loads((r.ROOT/'raw/prefill-policy-reviewed.json').read_text());base=json.loads(r.Path(policy['config']).read_text());base['environment_overrides']={};base['args']=r.setarg(base['args'],'--max-context',65536)

def mark(phase,label):
 s=json.loads((r.ROOT/'STATUS.json').read_text());s['running']={'phase':phase,'candidate':label};s['next_exact_action']='Complete upstream calibration then sequential actual64K workers/PCIe/min-p screens; best warmup+3.';(r.ROOT/'STATUS.json').write_text(json.dumps(s,indent=2));(r.ROOT/'STATUS.md').write_text('# v0.1.32 IN_PROGRESS\n\nRunning: '+json.dumps(s['running'])+'\n\nNext: '+s['next_exact_action']+'\n\nFull state: STATUS.json.\n')

calfile=r.ROOT/'raw/calibration.json'
if not calfile.exists():
 assert not list((r.ROOT/'raw').glob('calibrator-native-request-*.json')),'Partial calibration requires preservation before rerun'
 assert r.c.psutil.virtual_memory().available>=100*r.c.GIB
 cfg=copy.deepcopy(base);cfg['log']=str(r.ROOT/'logs/calibration-engine.log');r.c.save(r.ROOT/'configs/calibration.json',cfg);mark('upstream calibrator','calibration')
 with (r.ROOT/'logs/calibration-driver.log').open('w') as f:
  env=dict(os.environ,CUDA_VISIBLE_DEVICES='0,1')
  for k in ['STRATA_SPLIT_OWN','STRATA_KV_ROT','STRATA_REFILL_SERIAL','STRATA_SPEC_COUPLED']:env.pop(k,None)
  p=subprocess.Popen([str(r.c.REPO/'.venv/bin/python'),str(r.ROOT/'calibrator-adapter.py'),str(r.ROOT/'configs/calibration.json')],cwd=r.c.REPO,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,env=env,start_new_session=True)
  r.c.save(r.ROOT/'calibrator-process.json',{'pid':p.pid,'started':time.time()})
  try:
   with r.c.Sampler(p.pid,'calibration') as sampler:
    while p.poll() is None:
     if sampler.abort:raise RuntimeError(sampler.abort)
     time.sleep(1)
   assert p.returncode==0,'Upstream calibrator failed'
  finally:
   if p.poll() is None:
    os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(timeout=25)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
cal=json.loads(calfile.read_text());cfg=copy.deepcopy(base)
for flag,value in cal['settings'].items():cfg['args']=r.setarg(cfg['args'],flag,value)
info=cal['report']['default'];cw=int(cal['settings'].get('--pool-workers',info['pool_workers']));cf=float(cal['settings'].get('--pcie-frac',info['pcie_frac']));cp=float(cal['settings'].get('--spec-min-p',info['spec_min_p']))
screens=[];reference=cfg
for group,flag,values in [('workers','--pool-workers',sorted({8,cw,cw-2,cw+2})),('pcie','--pcie-frac',sorted({cf,0.0,max(0,cf-.2) if cf>.1 else min(1,cf+.2)})),('minp','--spec-min-p',sorted({.3,.5,.7,cp}))]:
 rows=[]
 for value in values:
  if flag=='--pool-workers' and not 1<=value<=16:continue
  label=f'CAL-{group}-{value:g}-screen';cc=copy.deepcopy(reference);cc['args']=r.setarg(cc['args'],flag,value);cc['log']=str(r.ROOT/'logs'/f'{label}-engine.log');r.c.save(r.ROOT/'configs'/f'{label}.json',cc);mark('local sequential '+group,label)
  result=r.candidate(label,cc,1);screens.append(result);rows.append(result)
 viable=[x for x in rows if x['status']=='OK'];assert viable,f'No viable {group} candidate'
 best=max(viable,key=lambda x:(x['median_tg'],x['median_pp']));reference=json.loads((r.ROOT/'configs'/f"{best['candidate']}.json").read_text())
label='CAL-best-confirm';reference['log']=str(r.ROOT/'logs'/f'{label}-engine.log');r.c.save(r.ROOT/'configs'/f'{label}.json',reference);mark('combined confirmation',label);confirmed=r.candidate(label,reference,3,True);assert confirmed['status']=='OK' and len(confirmed['runs'])==3
old=json.loads((r.ROOT.parent/'q4-max-sweep/raw/calibration.json').read_text())
r.c.save(r.ROOT/'raw/calibration-selection.json',{'status':'COMPLETE','upstream':cal,'old_upstream_settings':old['settings'],'screens':screens,'confirmed':confirmed,'winner':label,'config':str(r.ROOT/'configs'/f'{label}.json'),'note':'Previous workers8 included; sequential tuning has no Cartesian product. Upstream calibrator uses its original short prompts; local64K validation separate.'})
r.c.save(r.ROOT/'raw/phase-calibration-terminal.json',{'status':'COMPLETE','ended':time.time()})
s=json.loads((r.ROOT/'STATUS.json').read_text());s['running']=None;s['completed'].append('Upstream calibrator plus workers/PCIe/minp sequential64K screens and best warmup+3');s['pending']=[x for x in s['pending'] if not x.startswith('calibrator and')];s['current_winners']['CPU_PCIe_minp']={'candidate':label,'config':str(r.ROOT/'configs'/f'{label}.json'),'PP':confirmed['median_pp'],'TG':confirmed['median_tg']};s['next_exact_action']='MTP specs2/3/4/5 at64K actual1024 output two each then TOP2three; OFF unsupported native serve guard.';(r.ROOT/'STATUS.json').write_text(json.dumps(s,indent=2))

import importlib.util
_spec=importlib.util.spec_from_file_location('status_render',Path(__file__).resolve().parent/'status-render.py' if 'Path' in globals() else r.ROOT/'status-render.py');_module=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_module);_module.render()
