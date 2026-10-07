"""Actualcontext prefillscreens andTOP2confirmation; separateupstreamprocesses."""
import run as r,json,copy,time,statistics,re

def clone(label,source,chunk):
 cfg=json.loads((r.ROOT/'configs'/f'{source}.json').read_text());cfg['args']=r.setarg(cfg['args'],'--max-context',262144);cfg['args']=r.setarg(cfg['args'],'--prefill',chunk);cfg['log']=str(r.ROOT/'logs'/f'{label}-engine.log');r.c.save(r.ROOT/'configs'/f'{label}.json',cfg);return cfg

def status(label,detail):
 p=r.ROOT/'STATUS.json';s=json.loads(p.read_text());s['running']={'phase':'prefill','candidate':label,**detail};s['next_exact_action']='Finish currentprefillcandidate; TOP2byPPthree actual127K/259500 runs. Readactualchunk/loan logs; excludedOOM/unsupported retained.';p.write_text(json.dumps(s,indent=2))
 (r.ROOT/'STATUS.md').write_text('# v0.1.32 — IN_PROGRESS\n\nRunning: '+json.dumps(s['running'])+'\n\nNext: '+s['next_exact_action']+'\n\nFullcompleted/pending/winners/exclusions: STATUS.json; scope: PLAN.md.\n')

def measure(label,cfg,target,n,warm):
 done=r.ROOT/'raw'/f'{label}-done.json'
 if done.exists():
  d=json.loads(done.read_text())
  if d['status']=='COMPLETE':
   assert len(d['runs'])==n and all(x['generated_tokens']==256 and x['cache_reused_tokens']==0 and abs(x['actual_prompt_tokens']-target)<=8 for x in d['runs'])
  return d
 assert not list((r.ROOT/'raw').glob(label+'-run*.json')),'Partialcandidate needs preservation/review before restart'
 rows=[]
 try:
  with r.Session(label,cfg) as s:
   smoke=s.request(8000,64,'smoke','smoke');assert smoke['text'].strip() and smoke['draft_tokens']>0
   if warm:s.request(target,256,'warmup','warmup')
   for i in range(1,n+1):rows.append(s.request(target,256,f'run{i}'))
  result={'status':'COMPLETE','candidate':label,'target':target,'runs':rows,'median_PP':statistics.median(x['pp_tps'] for x in rows),'median_TG':statistics.median(x['tg_tps'] for x in rows),'prefill_argument':cfg['args'][cfg['args'].index('--prefill')+1],'actual_allocation_evidence':str(r.ROOT/'logs'/f'{label}-engine.log'),'note':'Configuredprefillargument mayshrink throughnormalupstreamallocation; finalparsermust readactualresolvedchunk, stage-specific loans. Normalserve expertfilecounters are decodeonly.'}
 except Exception as e:
  log=r.ROOT/'logs'/f'{label}-engine.log';text=log.read_text(errors='replace') if log.exists() else ''
  outcome='UNSUPPORTED_BY_CURRENT_UPSTREAM' if any(x in text for x in ['does not support','requires --','needs --']) else 'OOM_OR_RESOURCE_ABORT' if any(x in text.lower() for x in ['out of memory','cudaerrormemoryallocation']) or 'MemAvailable' in str(e) else 'FAILED'
  result={'status':outcome,'candidate':label,'target':target,'error':repr(e),'runs':rows,'log':str(log),'note':'Noenginepatch, noforcedunsafeallocation; failurepreserved.'}
 r.c.save(done,result);return result

assert json.loads((r.ROOT/'raw/phase-pp-control-terminal.json').read_text())['status']=='COMPLETE'
source=json.loads((r.ROOT/'raw/topology-selection.json').read_text())['winner'];screens=[]
for arg in ['auto','auto:32768','8192','16384','32768']:
 label='PREFILL-'+arg.replace(':','-')+'-screen';cfg=clone(label,source,arg);status(label,{'target':127000,'n':1,'prefill_argument':arg});screens.append(measure(label,cfg,127000,1,False))
valid=sorted([x for x in screens if x['status']=='COMPLETE'],key=lambda x:(x['median_PP'],x['median_TG']),reverse=True);assert len(valid)>=2,'Fewerthantwolegalsafeprefillcandidates'
confirmed=[]
for screen in valid[:2]:
 for target in [127000,259500]:
  label=screen['candidate'].replace('-screen',f'-confirm-{target}');cfg=clone(label,source,screen['prefill_argument']);status(label,{'target':target,'n':3,'prefill_argument':screen['prefill_argument']});confirmed.append(measure(label,cfg,target,3,True))
assert all(x['status']=='COMPLETE' for x in confirmed),'TOP2confirmation failed; inspect andpreserve before deciding'
r.c.save(r.ROOT/'raw/prefill-selection.json',{'status':'COMPLETE','source_topology':source,'screens':screens,'TOP2_screen':[x['candidate'] for x in valid[:2]],'confirmed':confirmed,'selection_rule':'PPprimary; actualresolution andTG mustbe reviewed before finalpolicy recommendation'})
r.c.save(r.ROOT/'raw/phase-prefill-terminal.json',{'status':'COMPLETE','exit_code':0,'ended':time.time(),'screen_requests':len([x for x in screens if x['status']=='COMPLETE']),'confirmation_requests':12})
s=json.loads((r.ROOT/'STATUS.json').read_text());s['running']=None;s['completed'].append('Prefill5screens/TOP2x3 at128/256K completed orunsupported documented');s['excluded_runs'] += [{'candidate':x['candidate'],'status':x['status'],'result':str(r.ROOT/'raw'/f"{x['candidate']}-done.json")} for x in screens if x['status']!='COMPLETE'];s['pending']=[x for x in s['pending'] if not x.startswith('prefillauto/')];s['next_exact_action']='Reviewactualprefillallocation/TOP2confirmation, choosepolicy, then default vsSPLIT_OWN/no-borrow64/128K screens.';(r.ROOT/'STATUS.json').write_text(json.dumps(s,indent=2))
print('Prefillphase COMPLETE',flush=True)
