#!/usr/bin/env python3
"""Explicit phases for the fresh same-main campaign. Run only after hardware audit and test review."""
import json,copy,statistics,subprocess,hashlib,shutil,sys,traceback,re
from pathlib import Path
import bench as b,run as r
R=b.R

def persisted(label,c,mode='startup',required=None):
 policy=R/'headline-instrumentation-policy.json'
 clean=policy.exists() and 'DIAG' not in label and not label.startswith(('CORRECT','UPSTREAM')) and not label.endswith('DISCOVERY')
 if clean:
  mode=None;c['exe']=str(Path(c['cwd'])/'build-default/strata-original');c['Strata_HEAD']=r.FROZEN_MAIN;c['build_variant']=Path(c['cwd']).name+'-unmodified-upstream'
  c['binary_sha256']=hashlib.sha256(Path(c['exe']).read_bytes()).hexdigest();c['headline_instrumentation']='OFF';c['initial_layout_policy']=str(policy)
 else:
  c['headline_instrumentation']='DIAGNOSTIC_ONLY_EXCLUDED_FROM_SPEED';c.pop('initial_layout_policy',None)
  c['exe']=str(Path(c['cwd'])/'build-default/strata');c['Strata_HEAD']=subprocess.check_output(['git','-C',c['cwd'],'rev-parse','HEAD'],text=True).strip();c['binary_sha256']=hashlib.sha256(Path(c['exe']).read_bytes()).hexdigest();c['build_variant']+='-boundary-diagnostics-default-off'
 c['extra_env']={'STRATA_BENCH_CACHE_SNAPSHOT':mode} if mode else {}
 if required:c['required_initial_layout']=required
 b.save(R/'configs'/f'{label}.json',c)
 return c

def cloned(src,label,lookup=False,diag=False):
 c=json.loads((R/'configs'/f'{src}.json').read_text());c['log']=str(R/'logs'/f'{label}-engine.log')
 c['args']=r.setarg(c['args'],'--suffix-draft',3 if lookup else 0)
 return persisted(label,c,'1' if diag else 'startup',c.get('required_initial_layout'))

def gate():
 hw=Path('/srv/ai/benchmarks/qwen-hardware-characterization/run-20261004T104353Z/final-audit.json')
 assert hw.exists() and json.loads(hw.read_text())['status']=='PASS','Hardware measurements/audit must finish first'
 review=R/'test-review.json'
 assert review.exists() and json.loads(review.read_text()).get('benchmark_allowed') is True,'Read actual test failures and explicitly save review before inference'

def select():
 import analyze
 cells=analyze.summarize();labels=['LS-A','LS-B','PR-LS','H-OLD','H-OPT','H-OPT-FIXED']
 valid=[x for x in cells if x['config'] in labels and x['valid_runs']==3 and x['actual_prompt']==31400]
 ls=max((x for x in valid if x['config'] in ['LS-A','LS-B']),key=lambda x:x['tg_tps'])
 opts=[x for x in valid if x['config'] in ['H-OPT','H-OPT-FIXED']]
 assert opts,'No optimized helper has three valid literal replays; preserve negatives and review before selection'
 opt=max(opts,key=lambda x:x['tg_tps']);ranked=sorted(valid,key=lambda x:x['tg_tps'],reverse=True)
 d={'best_layer_split':ls,'best_optimized_helper':opt,'top2':ranked[:2],'top2_within5pct':len(ranked)>1 and ranked[0]['tg_tps']/ranked[1]['tg_tps']<1.05}
 b.save(R/'selection.json',d);return d

def warmup(s,tag='warmup'):
 a=b.request(s,copy.deepcopy(b.warm),tag,kind='warmup');assert a['valid'],'Incomplete 64-token warmup; stop before measurement'

phase=sys.argv[1]
try:
 gate()
 if phase in ['instrumentation-ab','sweep32','diagnostics','secondary','fresh','steady','matrix']:
  assert (R/'correctness/review.json').exists() and json.loads((R/'correctness/review.json').read_text()).get('benchmark_allowed') is True,'Review paired correctness before speed'
 if phase=='pilot':
  for variant in ['control','optimized']:
   repo=Path('/srv/ai/strata-pr578-refresh-20261004-'+variant)
   src=repo/'build-default/strata';dst=repo/'build-default/strata-original'
   if not dst.exists():shutil.copy2(src,dst)
   assert hashlib.sha256(src.read_bytes()).hexdigest()==hashlib.sha256(dst.read_bytes()).hexdigest()
  label='UPSTREAM-PR-AUTO-PILOT';c=b.cfg(label,'optimized','helper',opt=True,original=True)
  with r.Session(label,c) as s:
   st=b.startup(s);b.save(R/'clean-auto-capacities.json',st);warmup(s)
   a=b.request(s,b.oldpayload(1),'32K-run1',kind='pilot');b.save(R/'raw'/f'{label}-done.json',{'label':label,'layout':st,'runs':[a]})
  b.status('Original upstream PR pilot preserved; apply boundary-only diagnostic patch',['original upstream pilot'])
 elif phase=='diagnostic-build':
  # No algorithm or dispatch changes. Clean binaries and pilot were saved first.
  assert (R/'clean-auto-capacities.json').exists()
  for variant in ['control','optimized']:
   repo=Path('/srv/ai/strata-pr578-refresh-20261004-'+variant)
   if subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()==r.FROZEN_MAIN:
    subprocess.run(['git','-C',str(repo),'apply',str(R/'git/boundary-debug-v0139-proposed.diff')],check=True)
    if variant=='control':subprocess.run(['git','-C',str(repo),'switch','-c','local/pr578-refresh-control-diagnostics'],check=True)
    subprocess.run(['git','-C',str(repo),'add','include/strata/core/remote_experts.hpp','src/program/generate.cpp'],check=True)
    subprocess.run(['git','-C',str(repo),'-c','user.name=Local benchmark','-c','user.email=benchmark@localhost','commit','-m','Add default-off boundary cache snapshots for local benchmark'],check=True)
   cmd=[str(repo/'.venv/bin/cmake'),'--build',str(repo/'build-default'),'-j','6']
   with (R/'logs'/f'{variant}-diagnostic-build.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
   with (R/'logs'/f'{variant}-diagnostic-ctest.log').open('w') as f:
    p=subprocess.run([str(repo/'.venv/bin/ctest'),'--test-dir',str(repo/'build-default'),'--output-on-failure','-j','1'],stdout=f,stderr=subprocess.STDOUT)
   b.save(R/'git'/f'{variant}-diagnostic-build.json',{'command':cmd,'HEAD':subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip(),'binary_SHA256':hashlib.sha256((repo/'build-default/strata').read_bytes()).hexdigest(),'ctest_returncode':p.returncode})
  b.status('Review diagnostic builds/tests, then discover frozen helper topology',['boundary-only diagnostics build'])
 elif phase=='discovery':
  assert (R/'diagnostic-test-review.json').exists() and json.loads((R/'diagnostic-test-review.json').read_text()).get('benchmark_allowed') is True,'Review diagnostic rebuild tests before inference'
  # Freeze PCIe after the clean startup probe, to remove startup calibration variance from helper A/B.
  clean=json.loads((R/'clean-auto-capacities.json').read_text());pcie=clean['primary_pcie_probe_fraction_reported'];assert pcie is not None
  label='H-OPT-DISCOVERY';c=persisted(label,b.cfg(label,'optimized','helper',opt=True,pcie=pcie))
  with r.Session(label,c) as s:
   st=b.startup(s);assert st.get('snapshot') and st['helper']>0
   st['frozen_pcie_frac']=pcie;b.save(R/'auto-capacities.json',st)
  b.status('Frozen initial helper layout saved; correctness next',['fresh helper auto sizing'])
 elif phase=='correctness':
  st=json.loads((R/'auto-capacities.json').read_text());p,h=st['primary_cli_uniform_budget'],st['helper'];assert p and h
  results=[];rows=[]
  for label,variant,opt in [('CORRECT-H-OLD','control',False),('CORRECT-H-OPT','optimized',True)]:
   c=persisted(label,b.cfg(label,variant,'helper',primary=p,helper=h,opt=opt,pcie=st['frozen_pcie_frac']),required=st)
   rows.append(b.battery(label,c))
  for i,(x,y) in enumerate(zip(*rows)):
   u,v=x['generated_token_ids'],y['generated_token_ids'];n=min(len(u),len(v));div=next((j for j in range(n) if u[j]!=v[j]),n if len(u)!=len(v) else None)
   text=y['text'];bad=x.get('non_finite_head_diagnostic',False) or y.get('non_finite_head_diagnostic',False) or not text.strip() or '\ufffd' in text or bool(re.search(r'(?i)\b(?:nan|infinity)\b',text));parsed=None
   if i>=8:
    try:parsed=json.loads(text)
    except ValueError:bad=True
   results.append({'case':i+1,'category':x['category'],'input_identical':x['input_ids_sha256']==y['input_ids_sha256'],'first_diverging_token':div,'equal_position_tokens':sum(u[j]==v[j] for j in range(n)),'positions_compared':n,'teacher_forced_top1_agreement':None,'malformed_output':bad,'non_finite_head_control':x.get('non_finite_head_diagnostic'),'non_finite_head_optimized':y.get('non_finite_head_diagnostic'),'structured_output':parsed,'control_finish':x['finish_reasons'],'optimized_finish':y['finish_reasons']})
  b.save(R/'correctness/summary.json',results)
  assert not any(z['malformed_output'] or not z['input_identical'] for z in results),'Correctness gate failed; inspect outputs before speed'
  b.status('Correctness passed; primary 32K sweep next',['10 paired correctness prompts'])
 elif phase=='sweep32':
  assert (R/'headline-instrumentation-policy.json').exists() or ((R/'instrumentation-overhead.json').exists() and json.loads((R/'instrumentation-overhead.json').read_text())['within_1pct']),'Unmodified headline policy or <=1% instrumentation proof required'
  assert (R/'correctness/summary.json').exists()
  st=json.loads((R/'auto-capacities.json').read_text());p,h,pcie=st['primary_cli_uniform_budget'],st['helper'],st['frozen_pcie_frac']
  a=persisted('LS-A',b.cfg('LS-A'));b.sweep('LS-A',a)
  k=json.loads((R/'raw/LS-A-layout.json').read_text())['layer_split_K'];assert k
  pr=b.cfg('PR-LS','optimized');pr['layer_split']=str(k)
  configs=[('LS-B',persisted('LS-B',b.cfg('LS-B',pcie=.28))),('PR-LS',persisted('PR-LS',pr)),('H-OLD',persisted('H-OLD',b.cfg('H-OLD','control','helper',primary=p,helper=h,pcie=pcie),required=st)),('H-OPT',persisted('H-OPT',b.cfg('H-OPT','optimized','helper',opt=True,pcie=pcie),required=st)),('H-OPT-FIXED',persisted('H-OPT-FIXED',b.cfg('H-OPT-FIXED','optimized','helper',primary=p,helper=h,opt=True,pcie=pcie),required=st))]
  for label,c in configs:b.sweep(label,c)
  select();b.status('32K sweep complete; inspect caches and valid finalists',['primary 32K sweep'])
 elif phase=='instrumentation-ab':
  st=json.loads((R/'auto-capacities.json').read_text());p,h,pcie=st['primary_cli_uniform_budget'],st['helper'],st['frozen_pcie_frac']
  for enabled in [False,True]:
   label='H-OPT-STARTUP-DIAG-ON' if enabled else 'H-OPT-STARTUP-DIAG-OFF'
   c=persisted(label,b.cfg(label,'optimized','helper',primary=p,helper=h,opt=True,pcie=pcie),mode='startup' if enabled else None,required=st if enabled else None)
   b.sweep(label,c)
  med={}
  for enabled in ['OFF','ON']:
   d=json.loads((R/'raw'/f'H-OPT-STARTUP-DIAG-{enabled}-done.json').read_text());rs=[a for a in d['runs'] if a['valid']]
   assert len(rs)==3,'Instrumentation timing comparison lacks three valid runs'
   med[enabled]=statistics.median(a['tg_tps'] for a in rs)
  overhead=1-med['ON']/med['OFF']
  b.save(R/'instrumentation-overhead.json',{'TG_median':med,'estimated_loss_fraction':overhead,'within_1pct':overhead<=.01,'scope':'same algorithm/binary, startup-only cache snapshot before warmup; no per-request ID enumeration or hot-loop counter; three distinct literal replay prompts','warning':'Non-interleaved A/B can contain runtime noise; a >1% loss requires investigation before headline timing.'})
  assert overhead<=.01,'Startup diagnostics comparison exceeds 1%; review and confirm before final speed runs'
  b.status('Startup diagnostics overhead comparison passed',['startup-only instrumentation A/B'])
 elif phase=='diagnostics':
  for src in ['H-OLD','H-OPT-FIXED']:
   label=src+'-DIAG';b.sweep(label,cloned(src,label,diag=True))
  b.status('Separate cache progression diagnostics complete',['cache progression diagnostics'])
 elif phase=='secondary':
  d=select()
  for src in [d['best_layer_split']['config'],'H-OLD',d['best_optimized_helper']['config']]:
   label=src+'-LOOKUP-ON-W32';c=cloned(src,label,lookup=True);c['warmup_output_tokens']=32;b.save(R/'configs'/f'{label}.json',c);b.sweep(label,c)
  b.status('Secondary lookup ON complete',['secondary lookup ON'])
 elif phase=='fresh':
  d=select()
  if d['top2_within5pct']:
   for x in d['top2']:
    for i in [1,2,3]:
     src=x['config'];label=src+'-FRESH'+str(i);done=R/'raw'/f'{label}-done.json'
     if done.exists():continue
     with r.Session(label,cloned(src,label)) as s:
      st=b.startup(s);warmup(s);a=b.request(s,b.oldpayload(i),f'32K-run{i}');a.update(context_label='32K',initial_layout=st,fresh_server_replicate=i);b.save(R/'raw'/f'{label}-32K-run{i}.json',a)
     b.save(done,{'label':label,'layout':st,'runs':[a]})
  b.status('Fresh-server confirmation decision completed',['fresh-server confirmations or documented >5% gap'])
 elif phase=='matrix':
  d=select()
  for src in [d['best_layer_split']['config'],d['best_optimized_helper']['config']]:
   policy=R/'matrix-retry-policy.json';labels=json.loads(policy.read_text())['final_labels'] if policy.exists() else {}
   label=labels.get(src,src+'-FINAL');b.sweep(label,cloned(src,label),contexts=('32K','64K','128K','256K'))
  b.status('Final context matrix complete',['final context matrix'])
 elif phase=='steady':
  d=select();p=json.loads((R/'references/steady2048-request.json').read_text())
  for src in [d['best_layer_split']['config'],'H-OLD',d['best_optimized_helper']['config']]:
   label=src+'-STEADY2048';done=R/'raw'/f'{label}-done.json'
   if done.exists():continue
   c=cloned(src,label);c['args']=r.setarg(c['args'],'--prompt-cache',0);b.save(R/'configs'/f'{label}.json',c)
   with r.Session(label,c) as s:
    st=b.startup(s);warmup(s);rows=[]
    for i in [1,2,3]:
     a=b.request(s,p,f'steady-run{i}',kind='steady');a.update(context_label='steady2048',initial_layout=st);b.save(R/'raw'/f'{label}-steady-run{i}.json',a);rows.append(a)
   b.save(done,{'label':label,'layout':st,'runs':rows})
  b.status('2048-token steady decode complete',['steady decode'])
 else:raise ValueError(phase)
except BaseException:
 (R/'logs'/f'refresh-{phase}-exception.txt').write_text(traceback.format_exc());raise
