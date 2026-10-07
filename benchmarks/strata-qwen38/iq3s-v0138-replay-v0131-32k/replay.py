import run as r,workloads as w,json,time,hashlib,subprocess,traceback
R=r.ROOT;label='IQ3S-replay32';cfg=json.loads((R/'configs/IQ3S-replay32.json').read_text());rows=[];error=None;state='RUNNING'
def status(action):
 r.c.save(R/'STATUS.json',{'status':state,'running':action if state=='RUNNING' else None,'completed':[f'exact old measured payload{i+1}' for i in range(len(rows))],'pending':[f'exact old measured payload{i+1}' for i in range(len(rows),3)],'next_exact_action':action})
 (R/'STATUS.md').write_text('# IQ3_S literal old32K replay onv0.1.38\n\n'+json.dumps(json.loads((R/'STATUS.json').read_text()),indent=2)+'\n')
try:
 status('load v0.1.38, unchanged prior config,2GPUauto')
 with r.Session(label,cfg) as session:
  payloads=[('old-warmup',json.loads((R/'references/IQ3_S-warmup-request.json').read_text()))]+[(f'run{i}',json.loads((R/'references'/f'IQ3_S-32K-{i}-request.json').read_text())) for i in [1,2,3]]
  for tag,payload in payloads:
   status('replay '+tag+' without prompt/sampling changes');target=4096 if tag=='old-warmup' else 31400
   assert session.run.count(payload['messages'])==target
   print('START',tag,time.strftime('%H:%M:%S',time.gmtime()),flush=True)
   a=w.request(session,payload['messages'],payload['max_tokens'],tag,kind='warmup' if tag=='old-warmup' else'measured',exact_payload=payload)
   assert json.loads((R/'raw'/f'{label}-{tag}-request.json').read_text())==payload
   a.update(exact_payload_replayed=True,source_payload=str(R/'references'/('IQ3_S-warmup-request.json' if tag=='old-warmup' else f'IQ3_S-32K-{tag[-1]}-request.json')),actual_token_target=target)
   r.c.save(R/'raw'/f'{label}-{tag}.json',a)
   reasons=[]
   if a['status']!='OK' or a['generated_tokens']!=256 or a['cache_reused_tokens']!=0 or a['actual_prompt_tokens']!=target or a['abort'] or a['finish_reasons']!=['length']:reasons.append('INVALID_REPLAY_REQUEST')
   if reasons:raise RuntimeError(str(reasons)+' '+tag+'; preservedraw, no regeneratedoldprompt')
   if tag!='old-warmup':rows.append(a)
   print('FINISH',tag,'PP',a['pp_tps'],'TG',a['tg_tps'],'MTPaccept',a['acceptance_pct'],'accepted/window',a['mean_accepted_length'],flush=True)
 state='COMPLETE'
except BaseException as e:
 error=repr(e);state='FAIL';(R/'logs/exception.txt').write_text(traceback.format_exc());print('STOP',error,flush=True)
finally:
 r.c.save(R/'terminal.json',{'status':state,'error':error,'runs':rows,'GPU_apps_after':subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'],text=True)});status('Generate old/new/replay comparison' if state=='COMPLETE' else'Read preservedblocker')
if state!='COMPLETE':raise SystemExit(1)
