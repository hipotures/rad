import run as r,json,time,uuid,copy
from pathlib import Path
label='PP-CONTROL';cfg=copy.deepcopy(r.SEED);r.c.save(r.ROOT/'configs'/f'{label}.json',cfg)
plan=json.loads((r.ROOT.parent.parent/'controls-request-plan.json').read_text());rows=[]
with r.Session(label,cfg) as s:
 s.request(8000,64,'smoke','smoke')
 for cell in plan['cells']:
  target=cell['target']
  messages,count,_=s.run.exact_prompt(target,cell['warmup_nonce']);import workloads as w
  warm=w.request(s,messages,256,f'{target}-warmup',kind='warmup');assert warm['generated_tokens']==256
  for i,nonce in enumerate(cell['nonces'],1):
   messages,count,_=s.run.exact_prompt(target,nonce);rec=w.request(s,messages,256,f'{target}-run{i}',kind='controlled_version_AB')
   assert rec['actual_prompt_tokens']==rec['actual_prompt_tokens_tokenizer'] and abs(rec['actual_prompt_tokens']-target)<=8 and rec['generated_tokens']==256 and rec['cache_reused_tokens']==0
   rows.append(rec)
r.c.save(r.ROOT/'raw/control-done.json',{'status':'COMPLETE','runs':rows,'plan':str(r.ROOT.parent.parent/'controls-request-plan.json'),'note':'Samepairedmessages andsettings, frozenoldcodecorpus. Ownversion-specific directory; preservedoldengine only, no originalcampaignrestart.'})
print('ControlledPP matrix COMPLETE',flush=True)
