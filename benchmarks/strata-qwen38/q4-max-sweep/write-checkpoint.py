from pathlib import Path
import json,hashlib,statistics,re,subprocess,time,shutil
R=Path(__file__).resolve().parent
rows=[]
for p in sorted((R/'raw').glob('*.json')):
 try:d=json.loads(p.read_text())
 except Exception:continue
 if isinstance(d,dict) and 'actual_prompt_tokens' in d and 'tg_tps' in d and 'timings' in d:
  rows.append((p,d))
patterns=[('single GPU resident',r'T0-control'),('single GPU full arena',r'T1-arena'),('2 GPU auto split',r'T2-auto'),('manual K screening',r'T3-K\d+$'),('TOP3 K confirmations',r'T3-K\d+-confirm'),('helper stripe/layer and capacity',r'T4-.*'),('static/adaptive',r'adapt-.*'),('worker screening',r'tune-workers-.*'),('PCIe fraction screening',r'tune-pcie-.*'),('min-p screening',r'tune-minp-.*'),('local confirmation',r'tune-best-confirm'),('MTP and matched control',r'MTP-.*'),('KV matrix',r'KV-.*'),('prefill chunk',r'prefill-.*'),('final matrices',r'FINAL-[AB]'),('long decode',r'LONG-FINAL-A'),('agentic',r'AGENT-.*'),('compaction',r'COMPACTION-.*'),('quality',r'QUALITY-.*'),('needle',r'NEEDLE-.*')]
phases=[]
for name,pat in patterns:
 selected=[(p,d) for p,d in rows if re.fullmatch(pat,d.get('candidate',d.get('model','')))]
 measured=[(p,d) for p,d in selected if d.get('kind') not in ['smoke','warmup','diagnostic_smoke','diagnostic']]
 groups={}
 for p,d in measured:
  if d.get('status')=='OK' and not d.get('abort'):
   key=(d.get('candidate',d.get('model')),round(d['actual_prompt_tokens']/1000),d['generated_tokens'])
   groups.setdefault(key,[]).append((p,d))
 results=[]
 for (label,ctx,out),rr in groups.items():
  results.append({'candidate':label,'actual_prompt_tokens':[d['actual_prompt_tokens'] for p,d in rr],'output_tokens':out,'n':len(rr),'PP_median':statistics.median(d['pp_tps'] for p,d in rr),'TG_median':statistics.median(d['tg_tps'] for p,d in rr),'TTFT_median':statistics.median(d['ttft_s'] for p,d in rr),'raw_results':[str(p) for p,d in rr],'raw_requests':[str(p.with_name(p.stem+'-request.json')) for p,d in rr if p.with_name(p.stem+'-request.json').exists()]})
 results.sort(key=lambda d:d['TG_median'],reverse=True)
 status='COMPLETE'
 if name=='agentic':status='PARTIAL' if measured else 'NOT_EXECUTED'
 if name in ['compaction','quality','needle'] and not measured:status='NOT_EXECUTED'
 phases.append({'phase':name,'status':status,'all_request_count':len(selected),'measured_request_count':len(measured),'smoke_warmup_count':len(selected)-len(measured),'best_observed_by_TG':results[0] if results else None,'results':results,'scope_note':'Different output lengths/context/tasks are separate groups; ranking is descriptive, not controlled A/B.'})
excluded=[]
for folder,reason in [('pss-1s-excluded','EXCLUDED_TELEMETRY_PSS'),('mtp-original-task-excluded','EXCLUDED_INCOMPLETE_OUTPUT'),('agentic-short-eos-excluded','EXCLUDED_INCOMPLETE_AGENTIC_SESSION'),('agentic-distinct-files-short-eos-excluded','EXCLUDED_INCOMPLETE_AGENTIC_SESSION'),('interrupted-driver-20261001','EXCLUDED_EXTERNAL_DRIVER_INTERRUPTION')]:
 base=R/'raw'/folder;rr=[]
 for p in base.rglob('*.json'):
  try:d=json.loads(p.read_text())
  except Exception:continue
  if isinstance(d,dict) and 'actual_prompt_tokens' in d and 'timings' in d:rr.append(str(p))
 excluded.append({'status':reason,'path':str(base),'request_count':len(rr),'raw_results':rr,'note':'Preserved. 1Hz PSS scans of ~73GiB arena took ~0.65s, perturbing timing.' if folder=='pss-1s-excluded' else 'See archived reason/logs; not a completed candidate.'})
pending=[
 {'item':'Agentic multi-turn','goal':'11 uninterrupted turns from actual~64K and~128K, prefix reuse; initial1024 then256–1024 actual output, additions500–2000','candidates':['FINAL-A AGENT-63400 COMPLETE, do not rerun v0.1.31','FINAL-A AGENT-127000 not begun'],'repetitions':'one full session per starting context','dependencies':'current candidate terminal/boundary; no engine patch','repeat_v0132':True},
 {'item':'Compaction','goal':'Summarize actual saved coding-agent history at127000/250000 input to<=4096 output','candidates':['127000','250000'],'repetitions':'one per context','dependencies':'completed saved agentic histories plus actual long requests/answers','repeat_v0132':True},
 {'item':'Quality parity','goal':'Exact three saved IQ3 requests; full outputs, no judge','candidates':['FINAL-A INT8 streaming','FINAL-A k8v4','IQ3 existing copies'],'repetitions':'three exact prompts per Q4 config','dependencies':'saved requests and selected configs','repeat_v0132':True},
 {'item':'Needle','goal':'Existing upstream harness with tokenizer-sized prompt','candidates':['31400','127000','259500'],'repetitions':'depth10/50/90 each, seed7,9requests','dependencies':'selected final config','repeat_v0132':True},
 {'item':'Prefill phase diagnostic','goal':'Use upstream STRATA_PREFILL_TIMING, excluded from speed ranking','candidates':['8K smoke64output','127K256output'],'repetitions':'one each','dependencies':'all timed stages done/no engine; currently NOT_EXECUTED','repeat_v0132':True},
 {'item':'Final summaries/plots/report and audit','goal':'Regenerate full artifacts,15required plots+acceptance/resources,20answers and ready configs; inspect against raw evidence','candidates':['summarize.py','plots.py','render_report.py','audit.py'],'repetitions':'one final generation and requirement audit','dependencies':'remaining measurements; old artifacts preliminary','repeat_v0132':True}]
repo=Path('/srv/ai/strata')
def cmd(a):return subprocess.check_output(a,cwd=repo,text=True).strip()
version={'HEAD':cmd(['git','rev-parse','HEAD']),'tracked_git_status':cmd(['git','status','--porcelain','--untracked-files=no']),'version':'0.1.31','version_evidence':str(R/'raw/T2-auto-startup.json'),'engine_sha256':hashlib.sha256((repo/'engine/strata').read_bytes()).hexdigest(),'build_info':{'CMakeCache':str(repo/'build/CMakeCache.txt'),'type':'Release','CUDA_arch':'89','CUDA_compiler':'/usr/local/cuda/bin/nvcc'},'environment_evidence':str(R/'raw/environment.json'),'CUDA':cmd(['/usr/local/cuda/bin/nvcc','--version']),'driver':cmd(['nvidia-smi','--query-gpu=driver_version','--format=csv,noheader'])}
plan=R/'checkpoint-plan';plan.mkdir(exist_ok=True);(plan/'scripts').mkdir(exist_ok=True)
scripts={}
for p in sorted(R.glob('*.py')):
 if p.name=='write-checkpoint.py':continue
 text=p.read_text();scripts[p.name]={'sha256':hashlib.sha256(text.encode()).hexdigest(),'lines':len(text.splitlines()),'functions':re.findall(r'^def (\w+)',text,re.M)}
 shutil.copy2(p,plan/'scripts'/p.name)
for p in [R/'objective.txt',R/'completion-audit.md',R/'architecture-notes.md',R/'flag-evidence.md']:
 shutil.copy2(p,plan/p.name)
cal=json.loads((R/'raw/calibration.json').read_text())
data={'status':'CHECKPOINT_V0131_NO_FURTHER_AUTOMATIC_PHASES','created':time.time(),'version':version,'phase_inventory':phases,'calibrator':{'status':'COMPLETE','path':str(R/'raw/calibration.json'),'settings':cal.get('settings')},'excluded':excluded,'pending':pending,'scripts_read_and_frozen':scripts,'original_objective':str(plan/'objective.txt'),'audit_scope':'Measured rows read from standalone raw request results, not copied from narrative logs. Stored aggregate selection files alone are not counted as requests. Smoke/warmup separated. No quality ranking.','limitations':['Physical host SSD traffic invisible behind virtiofs; logical expert file counters are not physical SSD proof.','Warm filesystem only; no safe physical cold-cache claim.','MTP OFF unsupported by current native serve guard.','Separate per-GPU routed hit/time-resolved cache/adaptive maps unavailable.','Existing summary/report/plots are preliminary and campaign incomplete.'],'safe_boundary':json.loads((R/'raw/v0131-safe-boundary.json').read_text()) if (R/'raw/v0131-safe-boundary.json').exists() else {'status':'WAITING_CURRENT_AGENT_63400_SESSION'}}
(R/'V0131-CHECKPOINT.json').write_text(json.dumps(data,indent=2,ensure_ascii=False))
lines=['# Strata v0.1.31 checkpoint','',f"Status: {data['safe_boundary']['status']}. No new v0.1.31 phase authorized. All results preserved; this is not a completed campaign.",'','## A. Version',json.dumps(version,indent=2),'','## B. Actually performed','| Phase | Status | Measured / all requests | Best observed TG / PP | Raw evidence |','|---|---|---:|---|---|']
for p in phases:
 b=p['best_observed_by_TG'];best=f"{b['candidate']} n={b['n']} out={b['output_tokens']}: {b['TG_median']:.2f} / {b['PP_median']:.2f}" if b else '—';ev=b['raw_results'][0] if b else 'Missing'
 lines.append(f"| {p['phase']} | {p['status']} | {p['measured_request_count']} / {p['all_request_count']} | {best} | {ev} |")
lines+=['','Calibrator COMPLETE: '+str(R/'raw/calibration.json')+' settings '+str(cal.get('settings')),'','All per-candidate counts, medians, actual context/output and raw request paths are in V0131-CHECKPOINT.json. Best TG across distinct tasks is not a controlled A/B. T5 is the same supported ArenaExpertSource as T1/T2, not an additional duplicated run.','', '## C. Excluded preserved results']
for e in excluded:lines.append(f"- **{e['status']}**: {e['path']}; {e['request_count']} request results. {e['note']}")
lines+=['','## D. Verified winners']
for name in ['TOP3 K confirmations','helper stripe/layer and capacity','static/adaptive','MTP and matched control','KV matrix','final matrices']:
 p=next(p for p in phases if p['phase']==name)
 for b in p['results']:
  if (name=='helper stripe/layer and capacity' and not b['candidate'].endswith('confirm')):continue
  lines.append(f"- {b['candidate']}: actual {b['actual_prompt_tokens']}, output {b['output_tokens']}, n={b['n']}; PP {b['PP_median']:.2f}, TG {b['TG_median']:.2f}, TTFT {b['TTFT_median']:.3f}s. {b['raw_results'][0]}")
lines+=['','## E. Remaining plan','Worker/PCIe/min-p, MTP, KV, prefill, final matrices and four long requests are already executed. They are not pending. The original completion audit has stale narrative entries; standalone raw evidence above takes precedence. Completed phases should be re-evaluated on v0.1.32 because runtime/kernel changes can change the optimum. No new v0.1.31 stages will start.']
for p in pending:lines+=['',f"### {p['item']}",p['goal'],f"Candidates: {p['candidates']}; repeats: {p['repetitions']}; dependencies: {p['dependencies']}; repeat on v0.1.32: {p['repeat_v0132']}."]
lines+=['','## Evidence and limitations']+['- '+x for x in data['limitations']]+['','Original objective, audit, and every campaign Python script are preserved in checkpoint-plan/. SHA256 inventory is in JSON. Existing models, checkout and packs remain untouched.']
(R/'V0131-CHECKPOINT.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'rows':len(rows),'phases':[(p['phase'],p['measured_request_count'],p['status']) for p in phases]},indent=2))
