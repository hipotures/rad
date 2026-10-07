"""External prompt and streaming helpers. Engine source remains untouched."""
import json,time,urllib.request,uuid
import run as r
ACTIVE=None

def stream(url,payload,api_key,timeout):
 global ACTIVE
 if ACTIVE:payload.update(ACTIVE.get('sampling',{}));r.c.save(ACTIVE['request_file'],payload)
 req=urllib.request.Request(url+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
 start=time.perf_counter();first=None;text=[];reason=[];usage={};events=[];raw_chunks=[];tool_call_events=[]
 with urllib.request.urlopen(req,timeout=timeout) as resp:
  for raw in resp:
   line=raw.decode('utf-8',errors='ignore').strip()
   if not line.startswith('data:'):continue
   data=line[5:].strip()
   if data=='[DONE]':break
   try:chunk=json.loads(data)
   except json.JSONDecodeError:continue
   raw_chunks.append(chunk)
   if chunk.get('usage'):usage=chunk['usage']
   for ch in chunk.get('choices') or []:
    delta=ch.get('delta') or {};piece=delta.get('content') or '';rp=delta.get('reasoning_content') or ''
    if delta.get('tool_calls'):tool_call_events.append({'elapsed_s':time.perf_counter()-start,'tool_calls':delta['tool_calls']})
    if piece or rp or delta.get('tool_calls'):
     now=time.perf_counter()
     if first is None:first=now
     events.append({'elapsed_s':now-start,'text':piece,'reasoning':rp})
    text.append(piece);reason.append(rp)
 end=time.perf_counter()
 if ACTIVE:r.c.save(ACTIVE['stream_file'],{'events':events,'raw_chunks':raw_chunks,'tool_call_events':tool_call_events,'usage':usage,'t_start_monotonic_s':start,'t_first_monotonic_s':first or end,'t_end_monotonic_s':end,'ttft_s':(first or end)-start,'total_s':end-start,'note':'Events are emitted text chunks, not guaranteed one token each; offline tokenizer counts will supply token axis.'})
 return {'t_start':start,'t_first':first or end,'t_end':end,'text':''.join(text),'reasoning':''.join(reason),'usage':usage,'chunks':len(events)}

def exact(run,target,task,nonce=None):
 body,_=r.c.upstream.build_text(run.parts,target*12)
 nonce=nonce or uuid.uuid4().hex
 def make(n):return [{'role':'system','content':f'[bench run {nonce}] You are a coding agent working in the repository shown below.'},{'role':'user','content':'Repository files and coding-agent history:\n\n'+body[:n]+'\n\nTask: '+task}]
 lo,hi=0,len(body);best=None
 while lo<=hi:
  mid=(lo+hi)//2;messages=make(mid);count=run.count(messages)
  if count<=target:
   best=(messages,count)
   if count==target:break
   lo=mid+1
  else:hi=mid-1
 assert best and target-8<=best[1]<=target
 return best[0]

def request(session,messages,output,tag,sampling=None,reuse=False,kind='workload'):
 global ACTIVE
 name=session.label+'-'+tag
 assert session.run.count(messages)+output+16<=int(session.cfg['args'][session.cfg['args'].index('--max-context')+1]),'Requested context exceeds capacity'
 ACTIVE={'sampling':sampling or {},'request_file':r.ROOT/'raw'/f'{name}-request.json','stream_file':r.ROOT/'raw'/f'{name}-stream.json'}
 original=r.c.upstream.post_stream;r.c.upstream.post_stream=stream
 pss_before=r.capture_pss(session.proc.pid)
 try:rec=session.run.request(messages,output,name,'quality')
 finally:r.c.upstream.post_stream=original;ACTIVE=None
 pss_after=r.capture_pss(session.proc.pid)
 stream_record=json.loads((r.ROOT/'raw'/f'{name}-stream.json').read_text())
 rec.update({k:stream_record[k] for k in ['t_start_monotonic_s','t_first_monotonic_s','t_end_monotonic_s'] if k in stream_record})
 rec['tool_call_events']=stream_record.get('tool_call_events',[])
 rec['finish_reasons']=[choice['finish_reason'] for chunk in stream_record.get('raw_chunks',[]) for choice in chunk.get('choices',[]) if choice.get('finish_reason')]
 rec.update(pss_before=pss_before,pss_after=pss_after,pss_note='Outside timed request')
 rec.update(candidate=session.label,kind=kind,sampling=sampling or {'temperature':0},config=str(r.ROOT/'configs'/f'{session.label}.json'))
 if not reuse:assert rec['cache_reused_tokens']==0,'Unexpected cache reuse'
 assert rec['actual_prompt_tokens']+output+16<=int(session.cfg['args'][session.cfg['args'].index('--max-context')+1])
 r.c.save(r.ROOT/'raw'/f'{name}.json',rec)
 (r.ROOT/'raw'/f'{name}-response.txt').write_text(rec['text'])
 return rec

LONG_TASK='This is an offline review of the complete repository excerpts already supplied above. No tools are available. Produce the answer directly; do not announce exploration, request tools, or output tool-call markup. Produce a detailed repository maintenance plan in 40 numbered sections. For each section, identify a distinct component from the supplied code, explain its responsibilities, propose a concrete change with a full unified diff and at least two verification cases. Continue until all 40 sections are complete; include enough detail for another engineer to implement them. Do not summarize early.'
