#!/usr/bin/env python3
import run as r
import workloads as w
import topology as t
import json,sys,statistics,subprocess,time,copy

def batch(label,cfg,target,output,repeats,warmup=True):
 done=r.ROOT/'raw'/f'{label}-done.json'
 if done.exists():return json.loads(done.read_text())
 rows=[]
 try:
  with r.Session(label,cfg) as s:
   s.request(8000,64,'smoke','smoke')
   if warmup:
    warm=w.request(s,w.exact(s.run,target,w.LONG_TASK),output,'warmup',kind='warmup');assert warm['generated_tokens']==output,'MTP warmup output shorter than requested'
   for n in range(repeats):
    rec=w.request(s,w.exact(s.run,target,w.LONG_TASK),output,f'run{n+1}',kind='candidate');assert rec['generated_tokens']==output,'MTP measured output shorter than requested';rows.append(rec)
  res={'candidate':label,'status':'OK','runs':rows,'median_tg':statistics.median(x['tg_tps'] for x in rows),'median_pp':statistics.median(x['pp_tps'] for x in rows)}
 except Exception as e:res={'candidate':label,'status':'FAIL','error':repr(e),'runs':rows}
 r.c.save(done,res);return res

def select_best(rows):
 valid=t.top(rows,1)
 if not valid:raise RuntimeError('No viable candidates')
 return valid[0]['candidate']

def main():
 # Max_blob-only capacity is conservative for mixed native layer sizes; complete requested safe-capacity arms first.
 subprocess.run([str(r.c.REPO/'.venv/bin/python'),str(r.ROOT/'helper-capacity.py')],check=True)
 selection=json.loads((r.ROOT/'raw/topology-selection.json').read_text())
 confirmed=[x for x in selection['ranking'] if x['candidate'].endswith('confirm')]
 auto=json.loads((r.ROOT/'raw/T2-auto-done.json').read_text())
 best=select_best(confirmed+[auto]);best_layer=select_best([x for x in confirmed if x['candidate'].startswith('T3-')]+[auto]);r.c.save(r.ROOT/'raw/tuning-initial-selection.json',{'best_topology':best,'best_layer_topology':best_layer})
 # static/default adaptive; same topology, two separately started processes
 ad=[]
 for mode,every in [('static',0),('adaptive',4)]:
  label='adapt-'+mode;cfg=t.clone(label,best_layer,adapt_every=every);ad.append(r.candidate(label,cfg,3,True))
 adaptive_best=select_best(ad)
 prior=t.top(confirmed+[auto],1)[0]
 if not best.startswith('T4-') or t.top(ad,1)[0]['median_tg']>=prior['median_tg']:best=adaptive_best
 r.c.save(r.ROOT/'raw/adaptive-selection.json',{'tested_layer_source':best_layer,'results':ad,'chosen_for_next_tuning':best})
 # Upstream calibrator, no setup.py and no persistent setup config mutation.
 calfile=r.ROOT/'raw/calibration.json'
 if not calfile.exists():
  cfg=t.clone('calibration',best)
  script="import sys,json;sys.path[:0]=['/srv/ai/strata','/srv/ai/strata/tools'];from calibrate import run;from pathlib import Path;c=json.loads(Path(sys.argv[1]).read_text());res=run(c);Path(sys.argv[2]).write_text(json.dumps(res,indent=2))"
  with (r.ROOT/'logs/calibration-driver.log').open('w') as f:
   p=subprocess.Popen([str(r.c.REPO/'.venv/bin/python'),'-c',script,str(r.ROOT/'configs/calibration.json'),str(calfile)],cwd=r.c.REPO,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
   with r.c.Sampler(p.pid,'calibration') as sampler:
    while p.poll() is None:
     if sampler.abort:raise RuntimeError(sampler.abort)
     time.sleep(1)
   if p.returncode:raise RuntimeError('Calibrator failed; inspect log')
 cal=json.loads(calfile.read_text());cfg=t.clone('calibrated-base',best)
 for flag,val in cal['settings'].items():cfg['args']=r.setarg(cfg['args'],flag,val)
 r.c.save(r.ROOT/'configs/calibrated-base.json',cfg)
 info=json.loads((r.ROOT/'raw'/f'{best}-startup.json').read_text())['metrics']['engine']
 vals=lambda flag,default:float(cfg['args'][cfg['args'].index(flag)+1]) if flag in cfg['args'] else float(default)
 cw=int(vals('--pool-workers',info['pool_workers']));cf=vals('--pcie-frac',info['pcie_frac']);cp=vals('--spec-min-p',info['spec_min_p'])
 reference='calibrated-base';tested=[]
 for group,flag,values in [('workers','pool_workers',sorted(set([cw,cw-4,cw+4,8,12,16]))),('pcie','pcie_frac',sorted(set([cf,max(0,cf-.2),min(1,cf+.2)]))),('minp','spec_min_p',sorted(set([cp,.3,.5,.7])))]:
  stage=[]
  for value in values:
   if flag=='pool_workers' and not 1<=value<=16:continue
   label=f'tune-{group}-{value:g}';cc=t.clone(label,reference,**{flag:value});stage.append(r.candidate(label,cc,1));tested.append(stage[-1])
  reference=select_best(stage)
 label='tune-best-confirm';cc=t.clone(label,reference);confirmed=r.candidate(label,cc,3,True)
 r.c.save(r.ROOT/'raw/cpu-pcie-selection.json',{'calibrator':cal,'initial_runtime_defaults':info,'local_tests':tested,'confirmed':confirmed})
 reference=label
 specs=[]
 for spec in [2,3,4,5]:
  label=f'MTP-spec{spec}';cc=t.clone(label,reference,spec=spec,spec_min_p=cp);specs.append(batch(label,cc,63400,1024,2))
 for row in t.top(specs,2):
  label=row['candidate']+'-confirm';cc=t.clone(label,row['candidate']);specs.append(batch(label,cc,63400,1024,3))
 bestspec=select_best([x for x in specs if x['candidate'].endswith('confirm')])
 local_cfg=json.loads((r.ROOT/'configs'/f'{reference}.json').read_text());local_minp=float(local_cfg['args'][local_cfg['args'].index('--spec-min-p')+1])
 if local_minp!=cp:
  label='MTP-best-local-minp-confirm';cc=t.clone(label,bestspec,spec_min_p=local_minp);specs.append(batch(label,cc,63400,1024,3));bestspec=select_best([x for x in specs if x['candidate'].endswith('confirm')])
 r.c.save(r.ROOT/'raw/mtp-selection.json',{'results':specs,'best':bestspec,'MTP_OFF':{'status':'UNSUPPORTED_BY_CURRENT_UPSTREAM','reason':'native pack guard requires spec>=2, and serve guard requires MTP path; generate.cpp1740/3613. No raw non-MTP TG claimed.'}})
 r.c.save(r.ROOT/'raw/tuned-selection.json',{'best':bestspec,'topology_source':best,'status':'CPU_PCIE_MTP_TUNED'})
if __name__=='__main__':main()
