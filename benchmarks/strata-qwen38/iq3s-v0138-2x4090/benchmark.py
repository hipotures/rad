import run as r,workloads as w,json,re,time,uuid,statistics,traceback,hashlib,subprocess
from pathlib import Path
R=r.ROOT; label='IQ3S-v0138';cfg=json.loads((R/'configs/IQ3S-v0138.json').read_text());targets=[31400,63400,127000,259500];valid=[];excluded=[];warmups=[];current=None

def save_status(state,action):
 r.c.save(R/'STATUS.json',{'status':state,'running':current if state=='RUNNING' else None,'completed':[f'{t}: {sum(a["target_prompt_tokens"]==t for a in valid)} valid measured runs' for t in targets],'pending':[f'{t}: {3-sum(a["target_prompt_tokens"]==t for a in valid)} measured runs remaining' for t in targets if sum(a['target_prompt_tokens']==t for a in valid)<3],'excluded_runs':excluded,'next_exact_action':action})
 (R/'STATUS.md').write_text('# IQ3_S v0.1.38 2×4090\n\n'+json.dumps(json.loads((R/'STATUS.json').read_text()),indent=2)+'\n')

def layout():
 text=Path(cfg['log']).read_text();k=re.search(r'layer split auto: K=(\d+)',text);a=re.search(r'expert cache (\d+) slots, ([\d.]+) GiB of VRAM',text);b=re.search(r'CUDA1 runs layers .*?expert cache (\d+) slots \(([\d.]+) GiB\)',text)
 return {'selected_layer_split_K':int(k[1]) if k else None,'GPU0_slots':int(a[1]) if a else None,'GPU1_slots':int(b[1]) if b else None,'GPU0_expert_cache_gib':float(a[2]) if a else None,'GPU1_expert_cache_gib':float(b[2]) if b else None,'note':'Startup cache capacity; prompt path can borrow slots temporarily. Not a per-request residency gauge.'}

def annotate(a,target,tag):
 a.update(target_prompt_tokens=target,repeat_tag=tag,**layout())
 ss=[json.loads(line) for line in Path(a['telemetry_file']).read_text().splitlines()]
 begin=a['t_start_monotonic_s'];first=a['t_first_monotonic_s'];end=a['t_end_monotonic_s']
 def aggregate(samples):
  def avg(xs):return statistics.mean(xs) if xs else None
  return {'samples':len(samples),'system_cpu_pct_mean':avg([s['system_cpu_pct'] for s in samples]),'system_cpu_pct_peak':max([s['system_cpu_pct'] for s in samples],default=None),'process_cpu_pct_mean':avg([sum(p['cpu_pct'] for p in s['processes']) for s in samples]),'process_cpu_pct_peak':max([sum(p['cpu_pct'] for p in s['processes']) for s in samples],default=None),'CPU_note':'Process CPU uses 100% per logical CPU; system CPU is normalized over 16 vCPUs. Decode256 is short: only a few1Hz samples. TTFT divides phases approximately.', 'GPU':{str(i):{'util_pct_mean':avg([g['util_pct'] for s in samples for g in s.get('gpus',[]) if g['index']==i]),'power_w_mean':avg([g['power_w'] for s in samples for g in s.get('gpus',[]) if g['index']==i])} for i in [0,1]}}
 a['telemetry_aggregates']={phase:aggregate([s for s in ss if lo<=s['monotonic']<=hi]) for phase,lo,hi in [('request',begin,end),('prefill',begin,first),('decode',first,end)]}
 a['logical_expert_file_reads_decode']=a.get('expert_tiers');a['PCIe_telemetry_file']=str(R/'telemetry'/f'{label}-pcie-dmon.log');a['PCIe_note']='Continuous nvidia-smi dmon PCIe RX/TX; raw timestamps permit phase alignment; unsupported counters remain unavailable.'
 reasons=[]
 if a.get('status')!='OK':reasons.append('REQUEST_FAILED')
 if a.get('generated_tokens')!=256:reasons.append('OUTPUT_NOT_256')
 if a.get('cache_reused_tokens')!=0:reasons.append('REUSE_NOT_ZERO')
 if abs((a.get('actual_prompt_tokens') or 0)-target)>8 or a.get('actual_prompt_tokens')!=a.get('actual_prompt_tokens_tokenizer'):reasons.append('TOKEN_COUNT_MISMATCH')
 if a.get('abort'):reasons.append(str(a['abort']))
 if a.get('tool_call_events'):reasons.append('TOOL_LIKE_STOP')
 if a.get('finish_reasons')!=['length']:reasons.append('UNEXPECTED_FINISH_REASON')
 a['valid_measured']=not reasons;a['invalid_reasons']=reasons
 r.c.save(R/'raw'/f'{label}-{tag}.json',a)
 return not reasons

state='RUNNING';error=None
try:
 assert subprocess.check_output(['git','status','--porcelain'],cwd=r.c.REPO,text=True).strip()==''
 assert hashlib.sha256(Path(cfg['exe']).read_bytes()).hexdigest()==json.loads((R/'environment.json').read_text())['engine_sha256']
 assert (R/'evidence/IQ3_S-SHA256SUMS').read_text().count('\n')==2,'Hash audit not finished'
 with r.Session(label,cfg) as session:
  assert layout()['selected_layer_split_K'] is not None and layout()['GPU1_slots'] is not None,'TwoGPU split/cache not confirmed'
  r.c.save(R/'startup-layout.json',layout())
  for target in targets:
   for kind,repeat in [('warmup',0),('measured',1),('measured',2),('measured',3)]:
    completed=False
    for attempt in range(1,4):
     tag=f'{target}-{kind}{repeat}-attempt{attempt}';current=tag;save_status('RUNNING',f'Finish {tag}; requests are sequential')
     if attempt==1:messages,count,_=session.run.exact_prompt(target,uuid.uuid4().hex)
     else:messages=w.exact(session.run,target,w.LONG_TASK)
     print('START',tag,time.strftime('%H:%M:%S',time.gmtime()),flush=True)
     a=w.request(session,messages,256,tag,kind=kind)
     if annotate(a,target,tag):
      if kind=='measured':valid.append(a)
      else:warmups.append(a)
      completed=True;break
     excluded.append({'raw':str(R/'raw'/f'{label}-{tag}.json'),'reasons':a['invalid_reasons']});print('INVALID preserved',tag,a['invalid_reasons'],flush=True)
     if any(x not in ['OUTPUT_NOT_256','UNEXPECTED_FINISH_REASON','TOOL_LIKE_STOP'] for x in a['invalid_reasons']):raise RuntimeError('Non-prompt invalid condition; stop without engine change')
    if not completed:raise RuntimeError(f'{target} still invalid after3prompt attempts')
    r.c.save(R/'progress.json',{'valid':valid,'warmups':warmups,'excluded':excluded})
    print('FINISH',tag,'PP',a['pp_tps'],'TG',a['tg_tps'],'TTFT',a['ttft_s'],flush=True)
 state='COMPLETE'
except BaseException as e:
 state='FAIL';error=repr(e);(R/'logs/exception.txt').write_text(traceback.format_exc());print('STOP',error,flush=True)
finally:
 r.c.save(R/'terminal.json',{'status':state,'error':error,'valid':valid,'warmups':warmups,'excluded':excluded,'layout':layout() if Path(cfg['log']).exists() else {},'GPU_apps_after':subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'],text=True),'git_status_after':subprocess.check_output(['git','status','--porcelain'],cwd=r.c.REPO,text=True)})
 current=None;save_status(state,'Generate report from saved raw results' if state=='COMPLETE' else 'Review preserved error/negative; no engine patches')
if state!='COMPLETE':raise SystemExit(1)
