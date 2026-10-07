"""Separate opt-in prompt modes; phase launched after reviewed prefill selection."""
import run as r,json,copy,time,statistics

def mark(phase,label):
 p=r.ROOT/'STATUS.json';s=json.loads(p.read_text());s['running']={'phase':phase,'candidate':label};s['next_exact_action']='Finish current candidate, compare prompt-mode screening, confirm >5% gains, then adaptive/static control.';p.write_text(json.dumps(s,indent=2));(r.ROOT/'STATUS.md').write_text('# v0.1.32 IN_PROGRESS\n\nRunning: '+json.dumps(s['running'])+'\n\nNext: '+s['next_exact_action']+'\n\nComplete state: STATUS.json.\n')

def measure(label,cfg,target,n=1,warm=False):
 path=r.ROOT/'raw'/f'{label}-done.json'
 if path.exists():return json.loads(path.read_text())
 assert not list((r.ROOT/'raw').glob(label+'-run*.json')),'Partial candidate: preserve/review before restart'
 mark('prompt-path AB',label);r.c.save(r.ROOT/'configs'/f'{label}.json',cfg);rows=[]
 try:
  with r.Session(label,cfg) as sess:
   sm=sess.request(8000,64,'smoke','smoke');assert sm['text'].strip() and sm['draft_tokens']>0
   if warm:sess.request(target,256,'warmup','warmup')
   for i in range(1,n+1):rows.append(sess.request(target,256,f'run{i}'))
  for row in rows:assert row['cache_reused_tokens']==0 and row['actual_prompt_tokens']==row['actual_prompt_tokens_tokenizer'] and abs(row['actual_prompt_tokens']-target)<=8
  out={'status':'COMPLETE','candidate':label,'target':target,'runs':rows,'median_PP':statistics.median(x['pp_tps'] for x in rows),'median_TG':statistics.median(x['tg_tps'] for x in rows)}
 except Exception as e:out={'status':'FAILED','candidate':label,'target':target,'runs':rows,'error':repr(e)}
 out['classification']='NON_BIT_IDENTICAL_OPT_IN' if cfg.get('environment_overrides',{}).get('STRATA_SPLIT_OWN')=='1' else 'DEFAULT' if '--no-prefill-borrow' not in cfg['args'] else 'NO_PREFILL_BORROW_SEPARATE_CONFIGURATION'
 r.c.save(path,out);return out

if __name__=='__main__':
 assert json.loads((r.ROOT/'raw/phase-prefill-terminal.json').read_text())['status']=='COMPLETE'
 policy=json.loads((r.ROOT/'raw/prefill-policy-reviewed.json').read_text());source=json.loads(r.Path(policy['config']).read_text());screens=[];configs={}
 for mode in ['default','split-own','no-borrow']:
  for target in [63400,127000]:
   label=f'PROMPT-{mode}-{target}-screen';cfg=copy.deepcopy(source);cfg['environment_overrides']={} if mode!='split-own' else {'STRATA_SPLIT_OWN':'1'}
   if mode=='no-borrow':cfg['args'] += ['--no-prefill-borrow']
   cfg['log']=str(r.ROOT/'logs'/f'{label}-engine.log');configs[mode,target]=cfg
   row=measure(label,cfg,target);row['mode']=mode;screens.append(row)
 assert all(x['status']=='COMPLETE' for x in screens if x['mode']=='default'),'Default reference failed'
 confirmations=[]
 for row in screens:
  if row['mode']=='default' or row['status']!='COMPLETE':continue
  baseline=next(x for x in screens if x['mode']=='default' and x['target']==row['target'])
  row['screen_delta_PP_pct']=100*(row['median_PP']/baseline['median_PP']-1);row['screen_delta_TG_pct']=100*(row['median_TG']/baseline['median_TG']-1)
  if max(row['screen_delta_PP_pct'],row['screen_delta_TG_pct'])>5:
   # Confirm both reference and candidate, so a noisy screening does not decide production.
   for mode in ['default',row['mode']]:
    label=f"PROMPT-{mode}-{row['target']}-confirm";cfg=copy.deepcopy(configs[mode,row['target']]);cfg['log']=str(r.ROOT/'logs'/f'{label}-engine.log');d=measure(label,cfg,row['target'],3,True);d['mode']=mode;confirmations.append(d)
 r.c.save(r.ROOT/'raw/prompt-modes-selection.json',{'status':'COMPLETE','screens':screens,'confirmations':confirmations,'note':'Opt-in results remain separately classified; no automatic merge with default production measurements.'})
 r.c.save(r.ROOT/'raw/phase-prompt-modes-terminal.json',{'status':'COMPLETE','ended':time.time()})
 s=json.loads((r.ROOT/'STATUS.json').read_text());s['running']=None;s['completed'].append('Prompt-path default/SPLIT_OWN/no-borrow64/128K screening and applicable confirmations');s['pending']=[x for x in s['pending'] if not x.startswith('split-own/no-borrow')];s['excluded_runs'] += [{'candidate':x['candidate'],'status':x['status']} for x in screens+confirmations if x['status']!='COMPLETE'];s['next_exact_action']='Review prompt mode results separately; run adaptive vs static on default reviewed prefill policy.';(r.ROOT/'STATUS.json').write_text(json.dumps(s,indent=2))

 if __name__=='__main__':
  import importlib.util
  spec=importlib.util.spec_from_file_location('status_render',r.ROOT/'status-render.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.render()
