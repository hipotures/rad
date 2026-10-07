"""Normal MTP sweep on identical saved long offline task; actual1024 output required."""
import run as r,workloads as w,json,copy,time,statistics
assert json.loads((r.ROOT/'raw/phase-calibration-terminal.json').read_text())['status']=='COMPLETE'
import review_calibration
review_calibration.review()
selection=json.loads((r.ROOT/'raw/calibration-selection.json').read_text());source=json.loads(r.Path(selection['config']).read_text())

def batch(label,cfg,n):
 path=r.ROOT/'raw'/f'{label}-done.json'
 if path.exists():return json.loads(path.read_text())
 assert not list((r.ROOT/'raw').glob(label+'-run*.json')),'Partial candidate requires explicit preservation/review'
 r.c.save(r.ROOT/'configs'/f'{label}.json',cfg)
 state=json.loads((r.ROOT/'STATUS.json').read_text());state['running']={'phase':'MTP64K1024','candidate':label,'n':n};state['next_exact_action']='Complete spec2/3/4/5 n2 and TOP2n3, retain native OFF unsupported proof; then KV matrix.';(r.ROOT/'STATUS.json').write_text(json.dumps(state,indent=2));(r.ROOT/'STATUS.md').write_text('# v0.1.32 IN_PROGRESS\n\nRunning: '+json.dumps(state['running'])+'\n\nNext: '+state['next_exact_action']+'\n\nFull state: STATUS.json.\n')
 rows=[]
 try:
  with r.Session(label,cfg) as session:
   smoke=session.request(8000,64,'smoke','smoke');assert smoke['text'].strip() and smoke['draft_tokens']>0
   for i in range(1,n+1):
    row=w.request(session,w.exact(session.run,63400,w.LONG_TASK),1024,f'run{i}',kind='candidate');rows.append(row)
    assert row['generated_tokens']==1024,'Natural early EOS invalidates fixed1024 speed candidate; retain output'
    assert row['cache_reused_tokens']==0 and abs(row['actual_prompt_tokens']-63400)<=8 and row['actual_prompt_tokens']==row['actual_prompt_tokens_tokenizer']
  out={'status':'COMPLETE','candidate':label,'runs':rows,'median_PP':statistics.median(x['pp_tps'] for x in rows),'median_TG':statistics.median(x['tg_tps'] for x in rows)}
 except Exception as e:out={'status':'FAILED','candidate':label,'runs':rows,'error':repr(e)}
 r.c.save(path,out);return out
screens=[]
for spec in [2,3,4,5]:
 label=f'MTP-spec{spec}-screen-v0132';cfg=copy.deepcopy(source);cfg['args']=r.setarg(cfg['args'],'--spec',spec);cfg['log']=str(r.ROOT/'logs'/f'{label}-engine.log');screens.append(batch(label,cfg,2))
valid=sorted([x for x in screens if x['status']=='COMPLETE'],key=lambda x:(x['median_TG'],x['median_PP']),reverse=True);assert len(valid)>=2,'Fewer than two viable fixed1024 MTP candidates'
confirmed=[]
for row in valid[:2]:
 label=row['candidate'].replace('-screen-','-confirm-');cfg=json.loads((r.ROOT/'configs'/f"{row['candidate']}.json").read_text());cfg['log']=str(r.ROOT/'logs'/f'{label}-engine.log');confirmed.append(batch(label,cfg,3))
assert all(x['status']=='COMPLETE' for x in confirmed),'TOP2 confirmation failure retained; inspect before proceeding'
best=max(confirmed,key=lambda x:(x['median_TG'],x['median_PP']))
r.c.save(r.ROOT/'raw/mtp-selection.json',{'status':'COMPLETE','screens':screens,'confirmed':confirmed,'winner':best['candidate'],'config':str(r.ROOT/'configs'/f"{best['candidate']}.json"),'MTP_OFF':{'status':'UNSUPPORTED_BY_CURRENT_UPSTREAM','source':'/srv/ai/strata-v0.1.32/src/program/generate.cpp:1836,3784','reason':'Nativepack needs spec>=2; serve requires spec>=2 and MTP. No engine patch or altered model. No OFF throughput invented.'},'note':'Same exact saved LONG_TASK across specs, unique nonce per request;1024 actual output. Normal metrics acceptance includes suffix drafts where runtime reports combined values.'})
r.c.save(r.ROOT/'raw/phase-mtp-terminal.json',{'status':'COMPLETE','ended':time.time()})
s=json.loads((r.ROOT/'STATUS.json').read_text());s['running']=None;s['completed'].append('MTP specs2/3/4/5 n2actual1024 and TOP2n3; OFF unsupported documented');s['pending']=[x for x in s['pending'] if not x.startswith('MTPoff')];s['current_winners']['MTP']={'candidate':best['candidate'],'TG':best['median_TG'],'PP':best['median_PP'],'config':str(r.ROOT/'configs'/f"{best['candidate']}.json")};s['excluded_runs'] += [{'candidate':x['candidate'],'status':x['status']} for x in screens if x['status']!='COMPLETE'];s['next_exact_action']='KV fullINT8/K8V4/Q4_0/rotatedINT8 legal matrix128K/256K n2 and TOP2n3; no K8V4 kvresident.';(r.ROOT/'STATUS.json').write_text(json.dumps(s,indent=2))

import importlib.util
_spec=importlib.util.spec_from_file_location('status_render',Path(__file__).resolve().parent/'status-render.py' if 'Path' in globals() else r.ROOT/'status-render.py');_module=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_module);_module.render()
