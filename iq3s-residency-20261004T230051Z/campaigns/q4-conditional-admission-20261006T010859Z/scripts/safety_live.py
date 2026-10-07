"""Small OFF/ON/cancel battery after unit/native tests; never headline timing."""
from campaign import C,load,save,Session,guard,status
from lab import api
import json,re,time,socket,urllib.request,hashlib
from pathlib import Path
def nonfinite(text):
 lines=[]
 for line in text.splitlines():
  if 'non-finite' not in line:continue
  nums=re.findall(r'(\d+) non-finite \(max \|x\|',line)
  if not ('strata dbg: prompt end:' in line and nums and all(int(x)==0 for x in nums)):lines.append(line)
 return lines
def battery():
 results=[]
 for variant in ['control','conditional-off','conditional']:
  path=C/'tests/live'/variant
  if (path/'results.json').exists():results.append(load(path/'results.json'));continue
  assert not path.exists(),'Preserve unfinished attempt; explicit diagnosis required'
  cfg=load(C/'configs'/f'{variant}-32k.json');cfg['env']['STRATA_DBG_NAN']='1'
  if variant=='conditional':cfg['env'].update(STRATA_Q4_EARLY_DIAGNOSTIC='1',STRATA_Q4_EARLY_LOG=str(path/'events'))
  with Session(C,cfg,path,'32k',port=18144) as s:
   warm=s.request('warmup','warmup','warmup');assert warm['state']=='VALID' and warm['actual_output_tokens']==64
   runs=[]
   for task in ['safety-code-1','safety-math-1']:
    r=s.request(task,task,'correctness');assert r['state']!='FAILED' and r['actual_engine_input_verified'] and r['reuse']==0;runs.append(r)
   text=(path/'logs/engine.log').read_text();assert not nonfinite(text) and 'Q4_EARLY_FATAL' not in text and 'Q4_EARLY_WORKER_FAIL' not in text
   save(path/'results.json',{'variant':variant,'warmup':warm,'runs':runs,'headline':False,'readbacks':'PASS ifreported; fullcanonicalarena bytes16cap/request forON','scope':'Sameexactinput IDs,256output correctness, debughead/routing counters; no logitsKL/noautomaticqualityjudge'})
  results.append(load(path/'results.json'))
 ref=results[0];pairs=[]
 for res in results[1:]:
  ps=[]
  for a,b in zip(ref['runs'],res['runs']):
   x=load(a['actual_output_ids_path']);y=load(b['actual_output_ids_path']);first=next((i for i,(u,v) in enumerate(zip(x,y)) if u!=v),None)
   if first is None and len(x)!=len(y):first=min(len(x),len(y))
   p={'task':b['payload']['path'],'same_input':a['actual_engine_input']==b['actual_engine_input'],'same_output':x==y,'first_diverging_token':first,'MTP_same':all(a[k]==b[k] for k in ['mtp_proposed','mtp_accepted','verify_windows']),'routing_same':all(a[k]==b[k] for k in ['local_vram_entries','cpu_fallback_entries','nonlocal_gpu_entries','all_routed_entries'])};ps.append(p)
   if res['variant']=='conditional-off':assert p['same_input'] and p['same_output'] and p['MTP_same'] and p['routing_same'],p
  pairs.append({'variant':res['variant'],'pairs':ps})
 save(C/'phase-c/small-correctness.json',{'PASS':True,'pairs':pairs,'limitations':'ON residency may change FP rounding/output trajectories; sampledfullcopiedbytes andnativekernelparity supportmath, notuniversalqualityequivalence'})
def cancellation():
 path=C/'tests/live/cancel';assert not path.exists()
 cfg=load(C/'configs/conditional-32k.json');cfg['env'].update(STRATA_Q4_EARLY_DIAGNOSTIC='1',STRATA_Q4_EARLY_LOG=str(path/'events'),STRATA_Q4_EARLY_DELAY_US='5000');cfg['headline_instrumentation']='DIAGNOSTIC_ONLY cancel/latecopy/drain/restoration'
 with Session(C,cfg,path,'32k',port=18144) as s:
  warm=s.request('warmup','warmup','warmup');assert warm['state']=='VALID'
  payload=load(C/'inputs/warmup.json');payload['max_tokens']=4096;save(path/'raw/cancel-request.json',payload);s.capture_requests+=1
  req=urllib.request.Request(s.url+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'});start=time.time();chunks=[]
  with urllib.request.urlopen(req,timeout=120) as response:
   for line in response:
    if not line.startswith(b'data:') or line[5:].strip()==b'[DONE]':continue
    chunks.append(json.loads(line[5:]))
    if len(chunks)>=16:response.fp.raw._sock.shutdown(socket.SHUT_RDWR);break
  save(path/'raw/cancel-stream-prefix.json',chunks);until=time.time()+60;idle=False
  while time.time()<until:
   metrics=api(s.url,'/metrics') or {}
   if (metrics.get('live') or {}).get('state')=='idle':idle=True;break
   time.sleep(.2)
  assert idle,'Cancel drain timeout';after=s.request('warmup','after-cancel','warmup');assert after['state']=='VALID' and after['actual_output_tokens']==64 and after['actual_engine_input_verified'];assert (path/'events-request2.jsonl').exists()
  text=(path/'logs/engine.log').read_text();assert 'Q4_EARLY_FATAL' not in text and 'Q4_EARLY_WORKER_FAIL' not in text
  result={'PASS':True,'warmup':warm,'next':after,'drain_observed_s':time.time()-start,'SSE_messages':len(chunks),'cancelled_output_ID_count':len(load(path/'raw/output-ids-request2.json')),'scope':'Disconnectafter16SSEmessages, not16tokens. Nativeworker mayfinishbeforecancel; engine drain/restoration/nextrequest observed. No headline timing.'};save(path/'results.json',result)
 save(C/'phase-c/cancellation.json',result);print('HTTP_CANCEL_DRAIN_NEXT_PASS',flush=True)
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('action',choices=['battery','cancel']);a=p.parse_args();guard()
 import os,psutil,sys,signal
 signal.signal(signal.SIGTERM,lambda *_:(_ for _ in ()).throw(KeyboardInterrupt('Owned safety timeout')))
 save(C/'logs'/f'safety-{a.action}-driver-pid.json',{'pid':os.getpid(),'create_time':psutil.Process().create_time(),'command':sys.argv,'timeout':'Caller-owned shell timeout600/1200 plus absolute deadline','cleanup':'Owned Session context'})
 if a.action=='battery':battery()
 else:cancellation()
if __name__=='__main__':main()
