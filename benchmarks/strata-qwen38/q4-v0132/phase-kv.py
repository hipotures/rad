"""Legal full-resident KV formats at real128/256K; rotated INT8 separately tagged."""
import run as r,json,copy,time,statistics,math
assert json.loads((r.ROOT/'raw/phase-mtp-terminal.json').read_text())['status']=='COMPLETE'
selected=json.loads((r.ROOT/'raw/mtp-selection.json').read_text());source=json.loads(r.Path(selected['config']).read_text())

def make(label,kv):
 cfg=copy.deepcopy(source);cfg['args']=r.setarg(cfg['args'],'--max-context',262144);cfg['args']=r.setarg(cfg['args'],'--kv-resident',None);cfg['args']=r.setarg(cfg['args'],'--kv','int8' if kv=='rotated-int8' else kv);cfg['environment_overrides']={'STRATA_KV_ROT':'1'} if kv=='rotated-int8' else {};cfg['log']=str(r.ROOT/'logs'/f'{label}-engine.log');return cfg

def measure(label,cfg,kv,target,n):
 done=r.ROOT/'raw'/f'{label}-done.json'
 if done.exists():return json.loads(done.read_text())
 assert not list((r.ROOT/'raw').glob(label+'-run*.json')),'Partial KV candidate requires preservation/review'
 r.c.save(r.ROOT/'configs'/f'{label}.json',cfg);state=json.loads((r.ROOT/'STATUS.json').read_text());state['running']={'phase':'KV128/256K','candidate':label,'n':n};state['next_exact_action']='Finish KV screens n2eachcontext, TOP2n3eachcontext, then review final Q4 default/opt-in configuration before finalmatrix.';(r.ROOT/'STATUS.json').write_text(json.dumps(state,indent=2));(r.ROOT/'STATUS.md').write_text('# v0.1.32 IN_PROGRESS\n\nRunning: '+json.dumps(state['running'])+'\n\nNext: '+state['next_exact_action']+'\n\nFull state: STATUS.json.\n')
 rows=[]
 try:
  with r.Session(label,cfg) as session:
   sm=session.request(8000,64,'smoke','smoke');assert sm['text'].strip() and sm['draft_tokens']>0
   session.request(target,256,'warmup','warmup')
   for i in range(1,n+1):rows.append(session.request(target,256,f'run{i}'))
  for row in rows:assert abs(row['actual_prompt_tokens']-target)<=8 and row['actual_prompt_tokens']==row['actual_prompt_tokens_tokenizer'] and row['generated_tokens']==256 and row['cache_reused_tokens']==0 and not row['abort']
  result={'status':'COMPLETE','candidate':label,'kv':kv,'target':target,'runs':rows,'median_PP':statistics.median(x['pp_tps'] for x in rows),'median_TG':statistics.median(x['tg_tps'] for x in rows)}
 except Exception as e:
  log=r.Path(cfg['log']);text=log.read_text(errors='replace') if log.exists() else ''
  result={'status':'UNSUPPORTED_BY_CURRENT_UPSTREAM' if 'does not support' in text or 'needs --' in text else 'FAILED','candidate':label,'kv':kv,'target':target,'runs':rows,'error':repr(e)}
 result['classification']='ROTATED_INT8_OPT_IN' if kv=='rotated-int8' else 'DEFAULT_KV_FORMAT_OPTION'
 r.c.save(done,result);return result
screens=[]
for kv in ['int8','k8v4','q4_0','rotated-int8']:
 for target in [127000,259500]:
  label=f'KV-{kv}-{target}-screen';screens.append(measure(label,make(label,kv),kv,target,2))
rank=[]
for kv in ['int8','k8v4','q4_0','rotated-int8']:
 rows=[x for x in screens if x['kv']==kv]
 if len(rows)==2 and all(x['status']=='COMPLETE' for x in rows):rank.append({'kv':kv,'geometric_TG':math.prod(x['median_TG'] for x in rows)**.5,'geometric_PP':math.prod(x['median_PP'] for x in rows)**.5})
rank.sort(key=lambda x:(x['geometric_TG'],x['geometric_PP']),reverse=True);assert len(rank)>=2,'Fewer than two legal stable KV candidates'
confirmed=[]
for candidate in rank[:2]:
 for target in [127000,259500]:
  label=f"KV-{candidate['kv']}-{target}-confirm";confirmed.append(measure(label,make(label,candidate['kv']),candidate['kv'],target,3))
assert all(x['status']=='COMPLETE' for x in confirmed),'KV confirmation failure retained; inspect before final selection'
r.c.save(r.ROOT/'raw/kv-selection.json',{'status':'COMPLETE','screens':screens,'rank':rank,'confirmed':confirmed,'selection_rule':'Geometricmean TG128/256 primary, PPsecondary; finalproductionchoice needs review including memory/opt-in parity. NoK8V4 streaming, allmaxcontext262144.'})
r.c.save(r.ROOT/'raw/phase-kv-terminal.json',{'status':'COMPLETE','ended':time.time()})
s=json.loads((r.ROOT/'STATUS.json').read_text());s['running']=None;s['completed'].append('KV4formats128/256K n2screens and TOP2n3');s['pending']=[x for x in s['pending'] if not x.startswith('INT8/K8V4')];s['excluded_runs'] += [{'candidate':x['candidate'],'status':x['status']} for x in screens if x['status']!='COMPLETE'];s['next_exact_action']='Review confirmed KV/opt-in parity and final topology/tuning; choose FINAL-v0132-Q4 and run contextmatrix n3.';(r.ROOT/'STATUS.json').write_text(json.dumps(s,indent=2))

import importlib.util
_spec=importlib.util.spec_from_file_location('status_render',Path(__file__).resolve().parent/'status-render.py' if 'Path' in globals() else r.ROOT/'status-render.py');_module=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_module);_module.render()
