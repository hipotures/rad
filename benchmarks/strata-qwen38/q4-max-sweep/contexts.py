#!/usr/bin/env python3
"""Long-context KV/prefill gates and final matrices; all outside upstream."""
import json,statistics,copy,subprocess
import run as r
import topology as t

def measure(label,cfg,targets,repeats=2,warmup=True):
 done=r.ROOT/'raw'/f'{label}-done.json'
 if done.exists():return json.loads(done.read_text())
 rows=[]
 retained={}
 if label in ['FINAL-A','FINAL-B']:
  # A detached-driver restart can retain fully completed cells. Partial cells require explicit review.
  for target in targets:
   paths=[r.ROOT/'raw'/f'{label}-{target}-run{n+1}.json' for n in range(repeats)]
   existing=[json.loads(p.read_text()) for p in paths if p.exists()]
   if existing:
    assert len(existing)==repeats,'Partial finalist cell requires archive/review before restart'
    assert all(x.get('status')=='OK' and abs(x.get('actual_prompt_tokens',0)-target)<=8 and x.get('actual_prompt_tokens')==x.get('actual_prompt_tokens_tokenizer') and x.get('generated_tokens')==256 and x.get('cache_reused_tokens')==0 and not x.get('abort') for x in existing),'Invalid saved finalist cell'
    retained[target]=existing
 try:
  with r.Session(label,cfg) as s:
   smoke=s.request(8000,64,'smoke','smoke')
   assert smoke['text'].strip() and smoke.get('draft_tokens',0)>0
   for target in targets:
    if target in retained:
     rows.extend(retained[target]);print('RETAIN VERIFIED CELL',label,target,len(retained[target]),flush=True);continue
    if warmup:s.request(target,256,f'{target}-warmup','warmup')
    for n in range(repeats):
     rec=s.request(target,256,f'{target}-run{n+1}')
     assert rec['generated_tokens']==256,'Unexpected EOS in fixed-length speed request'
     rows.append(rec)
  res={'candidate':label,'status':'OK','runs':rows,'retained_completed_cells':list(retained),'by_context':{str(target):{'median_pp':statistics.median(x['pp_tps'] for x in rows if abs(x['actual_prompt_tokens']-target)<9),'median_tg':statistics.median(x['tg_tps'] for x in rows if abs(x['actual_prompt_tokens']-target)<9)} for target in targets}}
 except Exception as e:
  log=(r.ROOT/'logs'/f'{label}-engine.log').read_text(errors='replace') if (r.ROOT/'logs'/f'{label}-engine.log').exists() else ''
  res={'candidate':label,'status':'UNSUPPORTED_BY_CURRENT_UPSTREAM' if any(x in log for x in ['does not support','requires --','needs --']) else 'FAIL','error':repr(e),'runs':rows}
 r.c.save(done,res);print('CONTEXT DONE',label,res['status'],flush=True);return res

def kv():
 source=json.loads((r.ROOT/'raw/tuned-selection.json').read_text())['best'];rows=[]
 # Keep max_context fixed at262144; k8v4 must not use streaming. Include full-VRAM INT8 control.
 for name,kv,resident in [('int8-stream','int8',32768),('int8-full','int8',None),('k8v4','k8v4',None),('q4_0','q4_0',None)]:
  label='KV-'+name;cfg=t.clone(label,source,kv=kv,kv_resident=resident,max_context=262144);rows.append(measure(label,cfg,[127000,259500],2,True))
 valid=[x for x in rows if x['status']=='OK']
 assert valid,'All KV candidates failed'
 rank=sorted(valid,key=lambda x:(x['by_context']['259500']['median_tg'],x['by_context']['127000']['median_tg']),reverse=True)
 ints=[x for x in rank if x['candidate'].startswith('KV-int8')];alts=[x for x in rank if not x['candidate'].startswith('KV-int8')]
 r.c.save(r.ROOT/'raw/kv-selection.json',{'results':rows,'best':rank[0]['candidate'],'best_int8':ints[0]['candidate'] if ints else None,'best_alternative':alts[0]['candidate'] if alts else None,'interpretation':'Speed ranking only. KV output/quality equivalence is not assumed; exact quality responses saved later.'})

def prefill():
 source=json.loads((r.ROOT/'raw/kv-selection.json').read_text())['best'];rows=[]
 for chunk in ['auto',8192,6144,4096,2048]:
  label=f'prefill-{chunk}';cfg=t.clone(label,source,prefill=chunk);rows.append(measure(label,cfg,[127000],1,False))
 valid=sorted([x for x in rows if x['status']=='OK'],key=lambda x:(x['by_context']['127000']['median_pp'],x['by_context']['127000']['median_tg']),reverse=True)
 assert len(valid)>=1
 confirmed=[]
 for item in valid[:2]:
  label=item['candidate']+'-confirm';cfg=t.clone(label,item['candidate']);confirmed.append(measure(label,cfg,[127000],3,True))
  label=item['candidate']+'-256K';cfg=t.clone(label,item['candidate']);rows.append(measure(label,cfg,[259500],1,True))
 rank=sorted([x for x in confirmed if x['status']=='OK'],key=lambda x:(x['by_context']['127000']['median_pp'],x['by_context']['127000']['median_tg']),reverse=True)
 assert rank
 r.c.save(r.ROOT/'raw/prefill-selection.json',{'screen':rows,'confirmed':confirmed,'best':rank[0]['candidate']})

def finalists():
 A=json.loads((r.ROOT/'raw/prefill-selection.json').read_text())['best'];topology=json.loads((r.ROOT/'raw/topology-selection.json').read_text())
 helpers=[x for x in topology['ranking'] if x['candidate'].startswith('T4-') and x['candidate'].endswith('-confirm')]
 arena=json.loads((r.ROOT/'raw/T1-arena-done.json').read_text());resident=json.loads((r.ROOT/'raw/T0-control-done.json').read_text())
 # The comparator must offer a different topology. Prefer best helper if it is actually better than single arena.
 B=helpers[0]['candidate'] if helpers and helpers[0]['median_tg']>arena['median_tg'] else 'T1-arena'
 if arena['status']!='OK':B='T0-control'
 candidates={}
 for name,source in [('FINAL-A',A),('FINAL-B',B)]:
  cfg=t.clone(name,source,max_context=262144)
  if name=='FINAL-B':
   cfg['args']=r.setarg(cfg['args'],'--kv','int8');cfg['args']=r.setarg(cfg['args'],'--kv-resident','32768');r.c.save(r.ROOT/'configs'/f'{name}.json',cfg)
  candidates[name]=measure(name,cfg,[31400,63400,127000,259500],3,True)
 r.c.save(r.ROOT/'raw/finalists.json',{'source_A':A,'source_B':B,'reason_B':'Best significantly different helper or single full-arena topology; INT8 KV streaming retained as standard comparator. Original single-budget control remains available.','results':candidates})

if __name__=='__main__':
 subprocess.run([str(r.c.REPO/'.venv/bin/python'),str(r.ROOT/'post-tuning-control.py')],check=True)
 kv();prefill();finalists()
