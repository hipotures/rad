#!/usr/bin/env python3
import run as r, workloads as w,json,hashlib,copy,subprocess,os,re,time,traceback
R=r.ROOT

def save(p,d):r.c.save(p,d)
def status(action,completed=None):
 s=json.loads((R/'STATUS.json').read_text());s['running']=action;s['next_exact_action']=action;s['status']='RUNNING'
 if completed:s['completed'].append(completed);s['pending']=[x for x in s['pending'] if x!=completed]
 save(R/'STATUS.json',s)
 import status_render
 status_render.render()

def request(s,p,tag,kind='measured'):
 status(s.label+' '+tag)
 ids=s.run.encode_messages(p['messages']);key=hashlib.sha256(json.dumps(p['messages'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 a=w.request(s,p['messages'],p['max_tokens'],tag,kind=kind,exact_payload=p)
 a.update(input_token_provenance=json.loads((R/'tokenization.json').read_text())[s.cfg['encoder_variant']][key],payload_sha256=hashlib.sha256(json.dumps(p,sort_keys=True,separators=(',',':')).encode()).hexdigest(),finish_reason=a['finish_reasons'][-1] if a['finish_reasons'] else None)
 a['valid']=a['status']=='OK' and a['generated_tokens']==p['max_tokens'] and a['actual_prompt_tokens']==len(ids) and a['cache_reused_tokens']==0 and not a.get('abort') and not a['tool_call_events']
 a['exclusion']=None if a['valid'] else 'INVALID_FIXED_LENGTH_OR_REQUEST'
 a['output_text_sha256']=hashlib.sha256((a['reasoning']+a['text']).encode()).hexdigest()
 save(R/'raw'/f'{s.label}-{tag}.json',a)
 print('RESULT',s.label,tag,'VALID' if a['valid'] else 'INVALID',a.get('generated_tokens'),a.get('tg_tps'),flush=True)
 return a

def layout(s):
 log=Path(s.cfg['log']).read_text();m=r.c.api('/metrics')
 st={'engine':m.get('engine'),'startup_log':s.cfg['log'],'primary_slots':int(re.search(r'expert cache (\d+) slots,',log)[1]),'helper_slots':int(re.search(r'CUDA1: (\d+) additional experts',log)[1]) if re.search(r'CUDA1: (\d+) additional experts',log) else None,'layer_slots':{x[0]:int(x[1]) for x in re.findall(r'layer split: CUDA(\d+) runs layers .*?expert cache (\d+) slots',log)},'K':s.cfg.get('layer_split'),'initial_overlap':None,'initial_overlap_note':'Not enumerated by clean speed binary; existing historical diagnostics are separate evidence'}
 save(R/'raw'/f'{s.label}-layout.json',st)
 info=m['engine'];assert info['spec']==4 and float(info['spec_min_p'])==.5 and info['lookup']==0 and info['pool_workers']==15 and info['max_context']==262144 and info['kv']=='int8'
 if s.cfg['encoder_variant']=='HELPER':assert st['primary_slots']==8586 and st['helper_slots']==11796
 return st
from pathlib import Path
warm=json.loads((R/'payloads/warmup.json').read_text())

def cell(variant,ctx,mode,validation=False):
 label=f'{variant}-{ctx}'+('-VALIDATION' if validation else '')
 done=R/'raw'/f'{label}-done.json'
 if done.exists():return json.loads(done.read_text())
 cfg=json.loads((R/'configs'/f'{variant}.json').read_text());cfg['log']=str(R/'logs'/f'{label}-engine.log');save(R/'configs'/f'{label}.json',cfg)
 result={'variant':variant,'context':ctx,'mode':mode,'runs':[]}
 with r.Session(label,cfg) as s:
  st=layout(s);result['layout']=st
  wa=request(s,warm,'warmup','warmup');assert wa['valid'],'Fixed64 warmup failed'
  for i in [1,2,3]:
   p=json.loads((R/'payloads'/(f'{ctx}-'+('long-' if mode=='long' else '')+f'run{i}.json')).read_text())
   a=request(s,p,f'run{i}')
   if a['valid']:result['runs'].append(str(R/'raw'/f'{label}-run{i}.json'))
   elif validation:
    result['status']='SHORT_WORKLOAD_EARLY_STOP';break
   else:
    # Identical deterministic replacements for all configurations; no prompt tuning.
    for attempt in [2,3]:
     a=request(s,p,f'run{i}-attempt{attempt}')
     if a['valid']:result['runs'].append(str(R/'raw'/f'{label}-run{i}-attempt{attempt}.json'));break
    else:raise RuntimeError('Systematic early stop: preserve negatives and review workload, no favourable prompt search')
  result.setdefault('status','COMPLETE' if len(result['runs'])==3 else 'PARTIAL')
 save(done,result);status('Completed '+label,variant+' '+ctx+' 4096' if result['status']=='COMPLETE' else None)
 return result

if __name__=='__main__':
 try:
  validation=cell('CURRENT','32K','original',True)
  mode='original' if validation['status']=='COMPLETE' else 'long'
  save(R/'workload-policy.json',{'selected':mode,'reason':'Preserved 256-output workload completed4096' if mode=='original' else 'Preserved short-answer workload naturally terminated before4096; shared pre-existing40-section steady-decode task used for all cells. No source trimming for round token count.','validation':validation})
  for ctx in ['32K','128K']:
   for variant in ['CURRENT','V0138','HELPER']:
    if mode=='original' and ctx=='32K' and variant=='CURRENT':continue
    cell(variant,ctx,mode)
  status('Primary matrix complete; analyze outside request timing')
 except BaseException:
  save(R/'failure.json',{'error':traceback.format_exc(),'time':time.time()});status('Failure preserved; diagnose and resume at next incomplete cell');raise
