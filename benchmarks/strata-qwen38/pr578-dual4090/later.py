import bench as b,run as r,workloads as w,json,copy,statistics,sys,traceback
from pathlib import Path
R=b.R

def configs():
 st=json.loads((R/'auto-capacities.json').read_text());p,h=st['primary_cli_uniform_budget'],st['helper'];return p,h

def selection():
 import analyze
 cells=analyze.summarize();main=[x for x in cells if x['config'] in ['LS-A','LS-B','PR-LS','H-OLD','H-OPT','H-OPT-FIXED','H-OLD-FAIR64','H-OPT-FAIR64','H-OLD-FAIR64-RETRY1','H-OPT-FAIR64-RETRY1'] and x['valid_runs']==3]
 ls=max((x for x in main if x['config'] in ['LS-A','LS-B']),key=lambda x:x['tg_tps'])
 opt=next((x for x in main if x['config']=='H-OPT-FAIR64'),None) or next((x for x in main if x['config']=='H-OPT-FAIR64-RETRY1'),None) or max((x for x in main if x['config'] in ['H-OPT','H-OPT-FIXED']),key=lambda x:x['tg_tps'])
 ranked=sorted(main,key=lambda x:x['tg_tps'],reverse=True)
 d={'best_layer_split':ls,'best_optimized_helper':opt,'top2':ranked[:2],'top2_within5pct':len(ranked)>1 and (ranked[0]['tg_tps']/ranked[1]['tg_tps']-1)<.05};b.save(R/'selection.json',d);return d

def fromsaved(source,label,**changes):
 c=json.loads((R/'configs'/f'{source}.json').read_text());c['log']=str(R/'logs'/f'{label}-engine.log')
 c['extra_env']={}
 for k,v in changes.items():
  if k=='suffix':c['args']=r.setarg(c['args'],'--suffix-draft',3 if v else 0)
  if k=='instrument':c['extra_env']={'STRATA_BENCH_CACHE_SNAPSHOT':'1'} if v else {}
 b.save(R/'configs'/f'{label}.json',c);return c

if __name__=='__main__':
 phase=sys.argv[1]
 try:
  if phase=='fair64':
   b.warm=copy.deepcopy(b.warm);b.warm['max_tokens']=64
   p,h=configs()
   for label,c in [('H-OLD-FAIR64',b.cfg('H-OLD-FAIR64','control','helper',primary=p,helper=h,instrument=False)),('H-OPT-FAIR64',b.cfg('H-OPT-FAIR64','optimized','helper',primary=p,helper=h,opt=True,instrument=False))]:b.sweep(label,c)
  elif phase=='diagnostics':
   b.warm=copy.deepcopy(b.warm);b.warm['max_tokens']=64
   p,h=configs()
   for label,c in [('H-OLD-DIAG',b.cfg('H-OLD-DIAG','control','helper',primary=p,helper=h)),('H-OPT-DIAG',b.cfg('H-OPT-DIAG','optimized','helper',primary=p,helper=h,opt=True))]:b.sweep(label,c)
  elif phase=='secondary':
   b.warm=copy.deepcopy(b.warm);b.warm['max_tokens']=64
   # Preserve invalid tool-like early stop; repeat literal three payloads once on freshservers.
   fair=json.loads((R/'raw/H-OPT-FAIR64-done.json').read_text())
   if any(not a.get('valid') for a in fair['runs']):
    for src in ['H-OLD-FAIR64','H-OPT-FAIR64']:
     label=src+'-RETRY1';b.sweep(label,fromsaved(src,label))
   d=selection()
   for src in [d['best_layer_split']['config'],'H-OLD-FAIR64',d['best_optimized_helper']['config']]:
    label=src+'-LOOKUP-ON';b.sweep(label,fromsaved(src,label,suffix=True))
  elif phase=='fresh':
   d=selection()
   if d['top2_within5pct']:
    for x in d['top2']:
     for i in [1,2,3]:
      src=x['config'];label=src+'-FRESH'+str(i);c=fromsaved(src,label);done=R/'raw'/f'{label}-done.json'
      if done.exists():continue
      with r.Session(label,c) as s:
       st=b.startup(s);b.save(R/'raw'/f'{label}-layout.json',st);b.request(s,b.warm,'32K-warmup',kind='warmup');a=b.request(s,b.oldpayload(i),f'32K-run{i}');a.update(context_label='32K',fresh_server_replicate=i,initial_layout=st);b.save(R/'raw'/f'{label}-32K-run{i}.json',a)
      b.save(done,{'label':label,'layout':st,'runs':[a]})
  elif phase=='matrix':
   b.warm=copy.deepcopy(b.warm);b.warm['max_tokens']=64
   d=selection()
   for src in [d['best_layer_split']['config'],d['best_optimized_helper']['config']]:
    label=src+'-FINAL';b.sweep(label,fromsaved(src,label),contexts=('32K','64K','128K','256K'))
  elif phase=='steady':
   b.warm=copy.deepcopy(b.warm);b.warm['max_tokens']=64
   d=selection()
   sources=[d['best_layer_split']['config'],d['best_optimized_helper']['config']]
   prompt_file=R/'references/steady2048-request.json'
   for src in sources:
    label=src+'-STEADY2048';c=fromsaved(src,label);c['args']=r.setarg(c['args'],'--prompt-cache',0);done=R/'raw'/f'{label}-done.json'
    if done.exists():continue
    with r.Session(label,c) as s:
     st=b.startup(s);b.request(s,b.warm,'steady-warmup',kind='warmup')
     if prompt_file.exists():p=json.loads(prompt_file.read_text())
     else:
      messages=w.exact(s.run,31400,w.LONG_TASK,nonce='PR578-STABLE-STEADY2048-20261003')
      p={'model':c['model_name'],'messages':messages,'max_tokens':2048,'stream':True,'stream_options':{'include_usage':True},'temperature':0,'reasoning_effort':'none'};b.save(prompt_file,p)
     rows=[]
     for i in [1,2,3]:
      b.status(label+f' steady2048 run{i}/3')
      a=b.request(s,p,f'steady-run{i}',kind='steady');a.update(context_label='steady2048',initial_layout=st);b.save(R/'raw'/f'{label}-steady-run{i}.json',a);rows.append(a)
     # Exact repeated input requires explicitly disabling engine prefix reuse (prompt-cache0).
    b.save(done,{'label':label,'layout':st,'runs':rows})
  else:raise ValueError(phase)
  b.status(phase+' complete; choose next phase',[phase])
 except BaseException:
  (R/'logs'/f'{phase}-exception.txt').write_text(traceback.format_exc());raise
