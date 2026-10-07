#!/usr/bin/env python3
"""Inspect request evidence; never equate script existence with campaign completion."""
from pathlib import Path
import json,statistics,subprocess,csv,re,hashlib
R=Path(__file__).resolve().parent
checks=[]
def read(p):
 p=Path(p)
 return json.loads(p.read_text()) if p.exists() else None
def check(name,ok,evidence):checks.append({'requirement':name,'proven':bool(ok),'evidence':evidence})
def config_arg(label,flag):
 d=read(R/'configs'/f'{label}.json') or {};a=d.get('args',[])
 return a[a.index(flag)+1] if flag in a and a.index(flag)+1<len(a) else None
def valid_speed_row(x,target,output=256):
 return bool(x and x.get('status')=='OK' and abs(x.get('actual_prompt_tokens',0)-target)<=8 and x.get('generated_tokens')==output and x.get('cache_reused_tokens')==0 and not x.get('abort'))
def measured(label,n,target,output=256,warmup=False):
 d=read(R/'raw'/f'{label}-done.json');rr=d.get('runs',[]) if d else []
 ok=bool(d and d.get('status')=='OK' and len(rr)==n and all(x.get('status')=='OK' and abs(x.get('actual_prompt_tokens',0)-target)<=8 and x.get('generated_tokens')==output and x.get('cache_reused_tokens')==0 for x in rr))
 if warmup:
  wu=read(R/'raw'/f'{label}-warmup.json');ok=ok and bool(wu and wu.get('kind')=='warmup' and abs(wu.get('actual_prompt_tokens',0)-target)<=8 and wu.get('generated_tokens')==output)
 check(label,ok,{'path':str(R/'raw'/f'{label}-done.json'),'status':d.get('status') if d else 'MISSING','measured_runs':len(rr)})
 return d

def main():
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd='/srv/ai/strata',text=True).strip()
 dirty=subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd='/srv/ai/strata',text=True).strip()
 env=read(R/'raw/environment.json');check('frozen clean checkout',env and (env['head'].get('stdout','').strip() if isinstance(env['head'],dict) else env['head'])==head and not dirty,{'head':head,'tracked_status':dirty})
 check('native pack without experts.bin',not Path('/srv/ai/models/strata/packs/ud-q4_k_xl/experts.bin').exists(),'Existing native GGUF pack; model identity in environment/integrity artifacts')
 diagnostic=read(R/'raw/prefill-diagnostic-done.json')
 diagnostic_run=diagnostic.get('run') if diagnostic else None
 check('separate upstream prefill phase diagnostic',diagnostic and diagnostic.get('status')=='OK' and diagnostic.get('instrumentation')=='STRATA_PREFILL_TIMING=1' and diagnostic.get('timing_lines') and valid_speed_row(diagnostic_run,127000) and diagnostic_run.get('kind')=='diagnostic',str(R/'raw/prefill-diagnostic-done.json'))
 recovery=read(R/'raw/interrupted-driver-20261001/interruption.json')
 if recovery:
  before=read(R/'raw/interrupted-driver-20261001/raw/FINAL-A-startup.json')
  after=read(R/'raw/FINAL-A-startup.json')
  fields=['max_context','kv','kv_resident','expert_slots','expert_slots_primary','expert_cache_mib','expert_cache_primary_mib','spec','mtp_max','pool_workers','pcie_frac','spec_min_p','arena_mib']
  check('FINAL-A restart runtime matches retained cells',before and after and all(before['metrics']['engine'].get(k)==after['metrics']['engine'].get(k) for k in fields),{'fields':fields,'archive':'raw/interrupted-driver-20261001'})
 for stage in ['tuning','contexts','extended','quality']:
  d=read(R/'raw'/f'phase-{stage}-terminal.json');check('phase '+stage,d and d.get('exit_code')==0,d or 'MISSING')
 measured('T0-control',1,63400);measured('T1-arena',3,63400,warmup=True);measured('T2-auto',3,63400,warmup=True)
 selection=read(R/'raw/layer-sweep-selection.json');screens=[]
 for k in [16,20,22,24,26,28,32,12,36]:screens.append(measured(f'T3-K{k}',1,63400))
 confirms=[read(p) for p in sorted((R/'raw').glob('T3-K*-confirm-done.json'))]
 check('manual TOP3 confirmations',len(confirms)==3 and all(x and x.get('status')=='OK' and len(x.get('runs',[]))==3 and all(valid_speed_row(y,63400) for y in x['runs']) for x in confirms),[x.get('candidate') for x in confirms if x])
 native=read(R/'raw/remote-native-capacity-selection.json');cap=read(R/'raw/remote-native-capacity.json')
 check('helper exact native safe capacity',native and native.get('status')=='OK' and cap and len(cap.get('candidate_slots',[]))==4,cap or 'MISSING')
 if cap:
  for mode in ['stripe','layer']:
   for slots in cap['candidate_slots']:measured(f'T4-{mode}-{slots}',1,63400)
 if native:
  top2=native.get('top2_screen',[])
  check('helper native TOP2 selected',len(top2)==2,[x.get('candidate') for x in top2])
  for item in top2:measured(item['candidate']+'-confirm',3,63400,warmup=True)
 for label in ['adapt-static','adapt-adaptive','tune-best-confirm']:measured(label,3,63400,warmup=True)
 cal=read(R/'raw/calibration.json');cpu=read(R/'raw/cpu-pcie-selection.json');check('upstream calibrator and local checks',cal and cpu and cpu.get('local_tests') and cpu.get('confirmed',{}).get('status')=='OK',{'calibration':bool(cal),'local_tests':len(cpu.get('local_tests',[])) if cpu else 0})
 for spec in [2,3,4,5]:measured(f'MTP-spec{spec}',2,63400,1024,True)
 mtp=read(R/'raw/mtp-selection.json');top2=[x for x in mtp.get('results',[]) if re.fullmatch(r'MTP-spec\d+-confirm',x['candidate'])] if mtp else []
 check('MTP TOP2 confirmations',len(top2)==2 and all(x.get('status')=='OK' and len(x.get('runs',[]))==3 and all(y.get('generated_tokens')==1024 for y in x['runs']) for x in top2),[x['candidate'] for x in top2])
 check('MTP OFF supported or explicit source limitation',mtp and mtp.get('MTP_OFF',{}).get('status')=='UNSUPPORTED_BY_CURRENT_UPSTREAM',mtp.get('MTP_OFF') if mtp else 'MISSING')
 control=read(R/'raw/post-tuning-control-selection.json')
 check('Same1024-token default control and anti-regression selection',control and control.get('status')=='OK' and len(control.get('default_control',{}).get('runs',[]))==3 and control.get('chosen_for_KV'),str(R/'raw/post-tuning-control-selection.json'))
 for label in ['KV-int8-stream','KV-int8-full','KV-k8v4','KV-q4_0']:
  d=read(R/'raw'/f'{label}-done.json');rr=d.get('runs',[]) if d else []
  completed=bool(d and d.get('status')=='OK' and len(rr)==4 and all(len([x for x in rr if valid_speed_row(x,target)])==2 and valid_speed_row(read(R/'raw'/f'{label}-{target}-warmup.json'),target) for target in [127000,259500]))
  ok=bool(d and (d.get('status')=='UNSUPPORTED_BY_CURRENT_UPSTREAM' or completed))
  check(label,ok,{'status':d.get('status') if d else 'MISSING','runs':len(rr)})
  check(label+' legal fixed-context config',config_arg(label,'--max-context')=='262144' and (label!='KV-k8v4' or config_arg(label,'--kv-resident') is None),{'max_context':config_arg(label,'--max-context'),'kv_resident':config_arg(label,'--kv-resident')})
 pre=read(R/'raw/prefill-selection.json');check('prefill five screens and TOP2 confirmations',pre and len(pre.get('screen',[]))>=7 and len(pre.get('confirmed',[]))==2 and all(x.get('status')=='OK' and len(x.get('runs',[]))==3 for x in pre['confirmed']),{'selection':str(R/'raw/prefill-selection.json')})
 if pre:
  for chunk in ['auto',8192,6144,4096,2048]:
   d=read(R/'raw'/f'prefill-{chunk}-done.json');rr=d.get('runs',[]) if d else []
   check(f'prefill {chunk} actual128K screen',bool(d and (d.get('status')=='UNSUPPORTED_BY_CURRENT_UPSTREAM' or (len(rr)==1 and valid_speed_row(rr[0],127000)))),str(R/'raw'/f'prefill-{chunk}-done.json'))
  for item in pre.get('confirmed',[]):
   label=item['candidate'];measured(label,3,127000,warmup=False)
   check(label+' actual128K warmup',valid_speed_row(read(R/'raw'/f'{label}-127000-warmup.json'),127000),str(R/'raw'/f'{label}-127000-warmup.json'))
   base=label.removesuffix('-confirm');d=read(R/'raw'/f'{base}-256K-done.json');rr=d.get('runs',[]) if d else []
   check(base+' TOP2 actual256K confirmation',len(rr)==1 and valid_speed_row(rr[0],259500) and valid_speed_row(read(R/'raw'/f'{base}-256K-259500-warmup.json'),259500),str(R/'raw'/f'{base}-256K-done.json'))
 for label in ['FINAL-A','FINAL-B']:
  d=read(R/'raw'/f'{label}-done.json');rr=d.get('runs',[]) if d else []
  check(label+' fixed max262144',config_arg(label,'--max-context')=='262144',str(R/'configs'/f'{label}.json'))
  for target in [31400,63400,127000,259500]:
   xs=[x for x in rr if abs(x.get('actual_prompt_tokens',0)-target)<=8]
   check(f'{label} actual{target}',len(xs)==3 and all(valid_speed_row(x,target) and x.get('actual_prompt_tokens')==x.get('actual_prompt_tokens_tokenizer') for x in xs),{'runs':len(xs),'PP':statistics.median(x['pp_tps'] for x in xs) if xs else None,'TG':statistics.median(x['tg_tps'] for x in xs) if xs else None})
   warmup=read(R/'raw'/f'{label}-{target}-warmup.json')
   check(f'{label} actual{target} warmup excluded',valid_speed_row(warmup,target) and warmup.get('kind')=='warmup',str(R/'raw'/f'{label}-{target}-warmup.json'))
  requests=[read(R/'raw'/f'{label}-{target}-run{i}-request.json') for target in [31400,63400,127000,259500] for i in range(1,4)]
  hashes=[hashlib.sha256(json.dumps(x['messages'],sort_keys=True,ensure_ascii=False).encode()).hexdigest() for x in requests if x and 'messages' in x]
  check(label+' twelve unique prompts',len(hashes)==12 and len(set(hashes))==12,hashes)
 A=read(R/'configs/FINAL-A.json');B=read(R/'configs/FINAL-B.json')
 def topology_signature(c):
  if not c:return None
  args=c.get('args',[])
  return (str(c.get('gpu')),str(c.get('layer_split')),tuple(args[args.index(flag)+1] if flag in args else None for flag in ['--expert-cache-device1','--expert-cache-remote-placement','--resident-budget-gib']))
 check('finalists distinct topology',A and B and topology_signature(A)!=topology_signature(B),{'A':topology_signature(A),'B':topology_signature(B)})
 long=read(R/'raw/long-decode-done.json');rr=long.get('runs',[]) if long else []
 check('long sampled4K/8K and greedy actual lengths',len(rr)==4 and all(x.get('length_completed') and x.get('generated_tokens')==x.get('requested_output') for x in rr),[(x.get('actual_prompt_tokens'),x.get('generated_tokens'),x.get('requested_output')) for x in rr])
 import trace_acceptance
 trace_checks=[]
 for record in rr:
  path=Path(record.get('acceptance_trace_file',''))
  saved=read(path) if path.is_file() else None
  try:
   fresh=trace_acceptance.reconstruct(Path(saved['source']).read_text(),record) if saved else None
   valid=bool(fresh and saved.get('status')=='VERIFIED_AGAINST_REQUEST_END_COUNTERS' and saved['rows']==fresh['rows'] and saved['draft_offered']==record['draft_tokens'] and saved['draft_accepted']==record['accepted_tokens'])
  except (AssertionError,KeyError,OSError,TypeError):valid=False
  trace_checks.append({'path':str(path),'verified':valid})
 check('long normal draft acceptance evolution',len(trace_checks)==4 and all(x['verified'] for x in trace_checks),trace_checks)
 for target in [63400,127000]:
  d=read(R/'raw'/f'AGENT-{target}-done.json');rr=d.get('runs',[]) if d else []
  check(f'agentic eleven turns start{target}',len(rr)==11 and abs(rr[0].get('actual_prompt_tokens',0)-target)<=8 and rr[0].get('generated_tokens')==1024 and all(x.get('cache_reused_tokens',0)>0 and 500<=x.get('new_tool_tokens',0)<=2000 and 256<=x.get('requested_generated_tokens',0)<=1024 and 256<=x.get('generated_tokens',0)<=1024 for x in rr[1:]),{'turns':len(rr),'first_output':rr[0].get('generated_tokens') if rr else None})
  history=read(R/'raw'/f'AGENT-{target}-history.json');history_ok=bool(history and len(history)==23 and len(rr)==11 and history[-1]=={'role':'assistant','content':rr[-1]['text']})
  if history_ok:
   for turn in range(11):
    req=read(R/'raw'/f'AGENT-{target}-turn{turn}-request.json')
    history_ok=history_ok and bool(req and req.get('messages')==history[:2+2*turn] and history[2+2*turn]=={'role':'assistant','content':rr[turn]['text']})
  check(f'agentic complete saved history start{target}',history_ok,str(R/'raw'/f'AGENT-{target}-history.json'))
 compact=read(R/'raw/COMPACTION-FINAL-A-done.json');rr=compact.get('runs',[]) if compact else []
 check('compaction real127K and250K <=4096 output',len(rr)==2 and all(any(abs(x.get('actual_prompt_tokens',0)-target)<=8 and x.get('generated_tokens',99999)<=4096 and x.get('history_sources') for x in rr) for target in [127000,250000]),[(x.get('actual_prompt_tokens'),x.get('generated_tokens')) for x in rr])
 keys=['A-coding-debug','B-mathematical-reasoning','C-repository-architecture']
 for mode in ['FINAL-A-INT8','FINAL-A-ALT-KV']:
  done=read(R/'quality'/mode/'done.json');ok=bool(done and done.get('status')=='OK')
  for key in keys:
   orig=read(R.parent/'results/raw'/f'IQ3_S-quality-{key}-request.json');actual=read(R/'raw'/f'QUALITY-{mode}-{key}-request.json')
   ok=ok and bool(orig and actual and {k:v for k,v in orig.items() if k!='model'}=={k:v for k,v in actual.items() if k!='model'} and (R/'quality'/mode/(key+'.txt')).exists())
  check('exact saved quality '+mode,ok,str(R/'quality'/mode))
 needle=read(R/'quality/needle-done.json');rr=needle.get('results',[]) if needle else []
 check('upstream needle 3contexts3depths',len(rr)==9 and {(round(x['actual_prompt_tokens']/100)*100,x['depth']) for x in rr}=={(t,d) for t in [31400,127000,259500] for d in [10,50,90]},str(R/'quality/needle-done.json'))
 reuse=read(R/'raw/IQ3_S-reuse-verification.json');check('IQ3 existing12run verified reuse',reuse and reuse.get('status')=='VERIFIED_REUSE' and reuse.get('head')==head,str(R/'raw/IQ3_S-reuse-verification.json'))
 csvpath=R/'summary.csv'
 required='topology gpu_count layer_split remote_cache_mode remote_cache_slots resident_mode host_expert_source KV_mode KV_streaming prefill_chunk spec spec_min_p pool_workers pcie_frac actual_prompt_tokens output_tokens PP_tps TG_tps TTFT_s wall_s MTP_accept GPU0_cache_slots GPU1_cache_slots GPU0_hit_count GPU1_hit_count CPU_misses expert_file_reads expert_file_MB RAM_used MemAvailable VRAM0 VRAM1 GPU0_util GPU1_util GPU0_power GPU1_power'.split()
 columns=next(csv.reader(csvpath.open())) if csvpath.exists() else [];check('required summary columns',set(required)<=set(columns),{'missing':sorted(set(required)-set(columns))})
 # Proven requests remain mandatory even if plot files already exist.
 manifest=read(R/'plots/source-manifest.json')
 phases={1:'contexts',2:'contexts',3:'contexts',6:'tuning',7:'tuning',8:'contexts',9:'contexts',10:'contexts',11:'extended',12:'extended',13:'extended',14:'extended',15:'extended'}
 for n in range(1,16):
  term=read(R/'raw'/f"phase-{phases[n]}-terminal.json") if n in phases else read(R/'raw/topology-selection.json')
  ready=bool(term and (term.get('exit_code')==0 if n in phases else term.get('status')=='TOPOLOGIES_MEASURED'))
  source_complete=bool(manifest and manifest.get('final_matrix_rows')==24 and manifest.get('long_decode_rows')==4 and manifest.get('agentic_rows')==22 and manifest.get('compaction_rows')==2)
  check(f'plot{n:02d} final data artifact',ready and source_complete and any(p.stat().st_size>1000 for p in (R/'plots').glob(f'{n:02d}-*.png')),{'manifest':str(R/'plots/source-manifest.json'),'required_phase_terminal':ready,'source_complete':source_complete})
 report=(R/'report.md').read_text();check('final20answers report',all(re.search(rf'^### {n}\. ',report,re.M) for n in range(1,21)),'report.md must include all20 numbered evidence-backed answers')
 for model in ['Q4','IQ3_S']:check(model+' ready config/launcher',all((R/'configs'/name).exists() for name in [f'{model}-best-runtime.json',f'run-{model}-best.sh']),str(R/'configs'))
 result={'status':'AUDIT_PASSED' if all(x['proven'] for x in checks) else 'INCOMPLETE','checks':checks,'warning':'Artifact checks alone do not prove final rendered plots or report interpretation; human current-state audit required before goal completion.'}
 (R/'raw/completion-audit-machine.json').write_text(json.dumps(result,indent=2)+'\n')
 print(result['status'],sum(x['proven'] for x in checks),'/',len(checks),'proven')
 print('Pending: '+', '.join(x['requirement'] for x in checks if not x['proven']))
if __name__=='__main__':main()
