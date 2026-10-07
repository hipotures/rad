#!/usr/bin/env python3
"""Exact saved IQ3 sanity requests and tokenizer-sized upstream needle methodology."""
import json,copy,hashlib,importlib.util,random,shutil
from pathlib import Path
import run as r
import topology as t
import workloads as w

KEYS=['A-coding-debug','B-mathematical-reasoning','C-repository-architecture']

def sanity():
 sel=json.loads((r.ROOT/'raw/kv-selection.json').read_text());sources={'FINAL-A-INT8':sel['best_int8'],'FINAL-A-ALT-KV':sel['best_alternative']}
 for mode,source in sources.items():
  if source is None:
   r.c.save(r.ROOT/'quality'/mode/'status.json',{'status':'UNSUPPORTED_BY_CURRENT_UPSTREAM','reason':'No viable alternative KV'});continue
  label='QUALITY-'+mode;done=r.ROOT/'quality'/mode/'done.json'
  if done.exists():continue
  # Preserve final selected topology/CPU/MTP/prefill, change only KV mode/streaming according to tested variant.
  cfg=t.clone(label,'FINAL-A');kv_cfg=json.loads((r.ROOT/'configs'/f'{source}.json').read_text())
  for flag in ['--kv','--kv-resident']:
   value=kv_cfg['args'][kv_cfg['args'].index(flag)+1] if flag in kv_cfg['args'] else None;cfg['args']=r.setarg(cfg['args'],flag,value)
  r.c.save(r.ROOT/'configs'/f'{label}.json',cfg);rows=[]
  with r.Session(label,cfg) as s:
   for key in KEYS:
    original=json.loads((r.BASE/'results/raw'/f'IQ3_S-quality-{key}-request.json').read_text())
    opts={k:v for k,v in original.items() if k not in ['model','messages','max_tokens']}
    rec=w.request(s,original['messages'],original['max_tokens'],key,opts,reuse=True,kind='quality')
    actual=json.loads((r.ROOT/'raw'/f'{label}-{key}-request.json').read_text())
    assert {k:v for k,v in actual.items() if k!='model'}=={k:v for k,v in original.items() if k!='model'}
    dest=r.ROOT/'quality'/mode;dest.mkdir(parents=True,exist_ok=True);full=rec['text']
    if rec.get('reasoning'):full+='\n\n[Reasoning returned by API]\n'+rec['reasoning']
    if rec.get('tool_call_events'):full+='\n\n[Structured tool-call events returned by API; not executed]\n'+json.dumps(rec['tool_call_events'],indent=2,ensure_ascii=False)
    (dest/(key+'.txt')).write_text(full);r.c.save(dest/(key+'.json'),rec);rows.append(rec)
  r.c.save(done,{'status':'OK','runs':rows,'source_kv':source,'note':'Exact previous messages/system prompt/sampling/output cap; no LLM judge or automatic quality ranking.'})
 # Retain original evidence, rather than regenerating IQ3.
 dest=r.ROOT/'quality/IQ3_S-existing';dest.mkdir(parents=True,exist_ok=True)
 for key in KEYS:
  for ext in ['.txt','.json']:
   src=r.BASE/'results/quality/IQ3_S'/(key+ext)
   assert src.exists();shutil.copy2(src,dest/src.name)
  shutil.copy2(r.BASE/'results/raw'/f'IQ3_S-quality-{key}-request.json',dest/(key+'-request.json'))
 # Output identity is a mechanical difference flag, never a quality rating.
 comparison=[]
 for key in KEYS:
  a=r.ROOT/'quality/FINAL-A-INT8'/(key+'.txt');b=r.ROOT/'quality/FINAL-A-ALT-KV'/(key+'.txt')
  if a.exists() and b.exists():comparison.append({'prompt':key,'byte_identical':a.read_bytes()==b.read_bytes(),'INT8_sha256':hashlib.sha256(a.read_bytes()).hexdigest(),'alternate_sha256':hashlib.sha256(b.read_bytes()).hexdigest()})
 r.c.save(r.ROOT/'quality/kv-output-differences.json',{'comparisons':comparison,'note':'Different output does not determine which is better. Manual review only.'})

def needle():
 done=r.ROOT/'quality/needle-done.json'
 if done.exists():return
 path=r.c.REPO/'tools/needle_bench.py';spec=importlib.util.spec_from_file_location('needle_upstream',path);u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)
 label='NEEDLE-FINAL-A';cfg=t.clone(label,'FINAL-A');rnd=random.Random(7);rows=[]
 with r.Session(label,cfg) as s:
  for target in [31400,127000,259500]:
   # Upstream haystack and words/depths/question exactly retained; replace char estimate with verified count.
   text=u.haystack(target*12)
   for depth in [10,50,90]:
    word=f'{rnd.choice(u.WORDS)}-{rnd.choice(u.WORDS)}-{rnd.randint(100,999)}'
    def make(n):
     body=text[:n];cut=int(len(body)*depth/100);cut=body.rfind('\n',0,cut)+1 or cut
     prompt=body[:cut]+f'\nThe secret code word for this text is: {word}. Remember it.\n'+body[cut:]+'\n\nWhat is the secret code word mentioned in the text above? Reply with the code word only.'
     return [{'role':'user','content':prompt}]
    lo,hi=0,len(text);best=None
    while lo<=hi:
     mid=(lo+hi)//2;msg=make(mid);n=s.run.count(msg)
     if n<=target:best=(msg,n);lo=mid+1
     else:hi=mid-1
    assert best and target-8<=best[1]<=target
    tag=f'{target}-depth{depth}';rec=w.request(s,best[0],40,tag,{'temperature':0,'chat_template_kwargs':{'enable_thinking':False}},reuse=True,kind='needle')
    row={'target':target,'depth':depth,'word':word,'found':word in rec['text'],'actual_prompt_tokens':rec['actual_prompt_tokens'],'answer':rec['text'],'wall_s':rec['total_wall_s'],'request':str(r.ROOT/'raw'/f'{label}-{tag}-request.json')};rows.append(row)
    r.c.save(r.ROOT/'quality/needle-progress.json',rows)
 r.c.save(done,{'status':'COMPLETED','results':rows,'methodology':'Existing upstream tools/needle_bench.py haystack/seed7/word lists/depths/question/max output40/greedy; external adaptation only tokenizer sizing and common streaming telemetry. No new needle test invented.'})

if __name__=='__main__':sanity();needle()
