#!/usr/bin/env python3
"""Finalist long decode, uninterrupted sessions and compaction of saved history."""
import json,copy,uuid,statistics,hashlib,os
from contextlib import contextmanager
from pathlib import Path
import run as r
import topology as t
import workloads as w
import trace_acceptance

SAMPLE={'temperature':1.0,'top_p':.95,'top_k':20}
AGENT_OFFLINE='No tools are available in this simulated session. Use only the supplied repository excerpts and tool outputs. Answer directly with your analysis and proposed diffs; do not announce exploration, request tools or emit tool-call markup. '
REVIEW_FILES=[
 ('CMakeLists.txt','build flags and dependency isolation'),
 ('serve/server.py','stream cancellation and request metrics'),
 ('src/program/generate.cpp','context bounds and startup failure recovery'),
 ('src/core/expert_source.cpp','RAM residency and file-read accounting'),
 ('src/core/expert_cache.cpp','cache allocation and expert slot ownership'),
 ('src/prefill/prefill.cpp','prompt buffer loans and failure rollback'),
 ('src/spec/draft_policy.cpp','acceptance bookkeeping and window selection'),
 ('tools/iq_pack.py','GGUF tensor validation and compatibility packing'),
 ('tools/needle_bench.py','prompt sizing and recall-test methodology'),
 ('include/strata/core/session.hpp','session state and prefix reuse correctness')]

@contextmanager
def upstream_window_trace():
 previous=os.environ.get('STRATA_TRACE')
 os.environ['STRATA_TRACE']='1'
 try:yield
 finally:
  if previous is None:os.environ.pop('STRATA_TRACE',None)
  else:os.environ['STRATA_TRACE']=previous

def long_decode():
 done=r.ROOT/'raw/long-decode-done.json'
 if done.exists():return json.loads(done.read_text())
 label='LONG-FINAL-A';cfg=t.clone(label,'FINAL-A');rows=[]
 with upstream_window_trace(),r.Session(label,cfg) as s:
  s.request(8000,64,'smoke','smoke')
  for target,n,sampling,tag in [(63400,4096,SAMPLE,'64K-4096-sampled'),(127000,4096,SAMPLE,'128K-4096-sampled'),(127000,8192,SAMPLE,'128K-8192-sampled'),(63400,4096,{'temperature':0},'64K-4096-greedy')]:
   msg=w.exact(s.run,target,w.LONG_TASK)
   rec=w.request(s,msg,n,tag,sampling,kind='long_decode')
   rec.update(requested_output=n,length_completed=rec['generated_tokens']==n)
   rec['acceptance_trace_file']=str(trace_acceptance.save(r.ROOT,label+'-'+tag,rec))
   r.c.save(r.ROOT/'raw'/f'{label}-{tag}.json',rec);rows.append(rec)
   if rec['generated_tokens']<n:print('LONG EARLY_EOS',tag,rec['generated_tokens'],'of',n,flush=True)
 r.c.save(done,{'status':'OK','runs':rows,'note':'Natural EOS respected. Full requested lengths must be verified, not inferred from max_tokens. Normal acceptance reconstructed from upstream STRATA_TRACE windows and verified against aggregate counters; combines MTP and suffix lookup. Trace overhead included. Tier/cache evolution remains request-end-only.'});return rows

def tool_text(s,turn,target):
 source,focus=REVIEW_FILES[turn-1]
 # Distinct real files and review tasks avoid copying earlier capped answers to the same CMake question.
 part=next(p for p in s.run.parts if p.startswith('### '+source+'\n'))
 body=part.split('```\n',1)[1].rsplit('\n```',1)[0]
 header=f'Tool output turn {turn}, snapshot {uuid.uuid4().hex}, source {source}:\n```\n'
 tail='\n```\n'+AGENT_OFFLINE+f'Review focus for this turn: {focus}. Produce a detailed engineering review in six numbered sections: (1) exact code evidence and assumptions; (2) a concrete failure scenario with inputs; (3) a complete proposed unified diff; (4) three verification cases with commands and expected results; (5) rollout and rollback; (6) remaining questions and tradeoffs. For each section, develop at least three distinct findings with code evidence, a detailed implementation proposal, and verification cases. This is a long-form maintenance review: complete all eighteen findings before concluding. Work directly from this supplied file and the earlier repository context. Do not repeat a prior answer or claim that proposed tests or patches were executed.'
 lo,hi=0,len(body);best=None
 while lo<=hi:
  mid=(lo+hi)//2;text=header+body[:mid]+tail;n=len(s.run.tok.encode(text,parse_special=True))
  if n<=target:best=(text,n);lo=mid+1
  else:hi=mid-1
 assert best and 500<=best[1]<=2000
 return best

def agentic(target):
 label=f'AGENT-{target}';done=r.ROOT/'raw'/f'{label}-done.json'
 if done.exists():return json.loads(done.read_text())
 cfg=t.clone(label,'FINAL-A');rows=[]
 with r.Session(label,cfg) as s:
  messages=w.exact(s.run,target,AGENT_OFFLINE+'Analyze the repository architecture, then propose a detailed implementation plan with concrete diffs for six components and validation steps. Explain each part fully.')
  rec=w.request(s,messages,1024,'turn0',SAMPLE,kind='agentic');rec.update(turn=0,new_tool_tokens=0)
  rows.append(rec);r.c.save(r.ROOT/'raw'/f'{label}-turn0.json',rec)
  assert rec['generated_tokens']==1024,'Initial agentic output shorter than required1024; preserve failed attempt and inspect task before a new complete session'
  for turn in range(1,11):
   messages.append({'role':'assistant','content':rec['text']})
   text,n=tool_text(s,turn,[650,1000,1500,1900][(turn-1)%4]);messages.append({'role':'user','content':text})
   cap=1024
   rec=w.request(s,messages,cap,f'turn{turn}',SAMPLE,reuse=True,kind='agentic')
   rec.update(turn=turn,new_tool_tokens=n,tool_source_file=REVIEW_FILES[turn-1][0],review_focus=REVIEW_FILES[turn-1][1],existing_prefix_reused=rec['cache_reused_tokens'],new_prompt_tokens_processed=rec['timings'].get('prompt_n'),total_context_tokens=rec['actual_prompt_tokens'])
   assert rec['cache_reused_tokens']>0,'Expected ordinary prompt cache reuse'
   assert 256<=rec['generated_tokens']<=1024,'Agentic natural EOS outside required256–1024output range; preserve attempt and inspect before new session'
   r.c.save(r.ROOT/'raw'/f'{label}-turn{turn}.json',rec);rows.append(rec)
  # The last answer was not followed by another request, but remains part of the recorded session.
  messages.append({'role':'assistant','content':rec['text']})
  r.c.save(r.ROOT/'raw'/f'{label}-history.json',messages)
 result={'status':'OK','runs':rows,'history':str(r.ROOT/'raw'/f'{label}-history.json'),'definition':'One running engine; initial repo/code prompt followed by ten tool-output turns; no reset or restart within session. Output cap1024 each turn; actual outputs256–1024 required. Sampling temperature1/top_p0.95/top_k20. Source tool additions500–2000 tokenizer tokens. Earlier greedy incomplete sessions retained separately, including abrupt EOS within code.'}
 r.c.save(done,result);return result

SUMMARY_TASK='Compress this coding-agent history into a concise handoff summary of at most4096 tokens. Preserve user goals, constraints, repository architecture, code changes, decisions, errors, verification results, pending tasks and exact relevant paths/commands. Separate observed facts from proposals. Do not implement new code; output only the summary.'

def compaction():
 label='COMPACTION-FINAL-A';done=r.ROOT/'raw'/f'{label}-done.json'
 if done.exists():return json.loads(done.read_text())
 sources=[r.ROOT/'raw/AGENT-63400-history.json',r.ROOT/'raw/AGENT-127000-history.json']
 text=''
 for path in sources:
  messages=json.loads(path.read_text());text+='\n\n=== ACTUAL RECORDED SESSION '+path.name+' ===\n'
  for msg in messages:text+='\n['+msg['role']+']\n'+msg['content']+'\n'
 # Extend the available source with actual generated review output, never fabricate tool success or execution.
 for path in sorted((r.ROOT/'raw').glob('LONG-FINAL-A-*-request.json')):
  request=json.loads(path.read_text());text+='\n\n=== ACTUAL RECORDED REVIEW REQUEST '+path.name+' ===\n'
  for msg in request['messages']:text+='\n['+msg['role']+']\n'+msg['content']+'\n'
  answer=path.with_name(path.name.replace('-request.json','-response.txt'))
  if answer.exists():text+='\n[assistant]\n'+answer.read_text()
  sources.append(path)
 cfg=t.clone(label,'FINAL-A');rows=[]
 with r.Session(label,cfg) as s:
  for target in [127000,250000]:
   def make(n):return [{'role':'system','content':f'[compaction {uuid_seed}] You are a careful coding-agent history summarizer.'},{'role':'user','content':text[:n]+'\n\n'+SUMMARY_TASK}]
   uuid_seed=uuid.uuid4().hex;lo,hi=0,len(text);best=None
   if s.run.count(make(hi))<target:raise RuntimeError(f'Actual saved history insufficient for{target}tokens; gather additional real coding-agent tool/history first')
   while lo<=hi:
    mid=(lo+hi)//2;msg=make(mid);n=s.run.count(msg)
    if n<=target:best=(msg,n);lo=mid+1
    else:hi=mid-1
   assert best and target-8<=best[1]<=target
   rec=w.request(s,best[0],4096,str(target),kind='compaction');rows.append(rec)
   rec.update(history_sources=[str(x) for x in sources],history_note='Flattened actual saved simulated-agent sessions plus actual generated review responses. No claim that proposed patches were executed. Source prefix cut verified by tokenizer.');r.c.save(r.ROOT/'raw'/f'{label}-{target}.json',rec)
 result={'status':'OK','runs':rows};r.c.save(done,result);return result

if __name__=='__main__':
 long_decode();agentic(63400);agentic(127000);compaction()
