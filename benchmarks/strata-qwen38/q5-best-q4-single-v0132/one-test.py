import run as r,workloads as w,json,time,hashlib,subprocess
from pathlib import Path
R=r.ROOT
plan=json.loads((R/'plan.json').read_text());cfg=json.loads((R/'configs/resident-baseline-seed.json').read_text());label='Q5-BEST-Q4'
def phase(name):
 d=json.loads((R/'STATUS.json').read_text());d.update(status='RUNNING',running=name,next_exact_action=name);r.c.save(R/'STATUS.json',d)
def check(rec,expected,cap):
 assert rec['status']=='OK' and rec['actual_prompt_tokens']==rec['actual_prompt_tokens_tokenizer']==expected and rec['generated_tokens']==cap
 assert rec['cache_reused_tokens']==0 and rec['abort'] is None and rec['min_mem_available_gib']>=12
result={'status':'RUNNING','plan':plan}
try:
 assert r.c.psutil.virtual_memory().available/r.c.GIB>=plan['routed_expert_GiB']+24
 assert not list((R/'raw').glob(label+'-measured.json')),'Never overwrite measured result'
 phase('startup')
 with r.Session(label,cfg) as s:
  phase('smoke')
  smoke=s.request(8000,64,'smoke','smoke');check(smoke,8000,64);assert smoke['text'].strip() and smoke['draft_tokens']>0
  r.c.save(R/'raw/smoke-reviewed.json',{'status':'PASS','generated_tokens':64,'text':smoke['text'],'MTP_draft_tokens':smoke['draft_tokens'],'actual_prompt_tokens':smoke['actual_prompt_tokens'],'note':'Correct nonempty repository explanation; normalMTP; no forced EOS/sampling change.'})
  phase('warmup')
  payload=json.loads((R/'raw/source-warmup-payload.json').read_text());warm=w.request(s,payload['messages'],256,'warmup',kind='warmup',exact_payload=payload);check(warm,31400,256)
  phase('one measured request')
  payload=json.loads((R/'raw/source-measured-payload.json').read_text());rec=w.request(s,payload['messages'],256,'measured',kind='measured',exact_payload=payload);check(rec,31400,256)
  result.update(status='COMPLETE',measured=rec,smoke_status='PASS',warmup_status='PASS',n_measured=1)
 # Engine has stopped before summaries / offline integrity inspection.
 ref=json.loads((R/'raw/Q4-reference.json').read_text());result.update(Q4_reference={'PP':ref['pp_tps'],'TG':ref['tg_tps'],'TTFT':ref['ttft_s']},delta_percent={'PP':(rec['pp_tps']/ref['pp_tps']-1)*100,'TG':(rec['tg_tps']/ref['tg_tps']-1)*100},comparison_classification='HISTORICAL_BEST_SINGLE_RUN_NOT_CONTROLLED_A_B')
 assert hashlib.sha256(Path(plan['Q4_reference']).read_bytes()).hexdigest()==plan['Q4_reference_sha256']
 src=json.loads((R/'raw/source-measured-payload.json').read_text());assert json.loads((R/'raw'/f'{label}-measured-request.json').read_text())==src
 log=(R/'logs'/f'{label}-engine.log').read_text(errors='replace');result['arena_log_lines']=[x for x in log.splitlines() if any(k in x.lower() for k in ['arena','cudahostregister','layer split','device 0','device 1','gpu0','gpu1','expert cache'])]
 result['model_pack_no_experts_bin']=not Path(cfg['args'][cfg['args'].index('--pack')+1],'experts.bin').exists()
 print(json.dumps({'status':'COMPLETE','actual_prompt_tokens':rec['actual_prompt_tokens'],'output_tokens':rec['generated_tokens'],'PP':rec['pp_tps'],'TG':rec['tg_tps'],'TTFT':rec['ttft_s'],'RAM':rec['peak_ram_used_gib'],'MemAvailable_min':rec['min_mem_available_gib'],'expert_tiers':rec['expert_tiers']},indent=2),flush=True)
except BaseException as e:
 result.update(status='FAIL',error=repr(e));print('FAIL',repr(e),flush=True)
finally:
 r.c.save(R/'summary.json',result);status={'status':result['status'],'running':None,'completed':['Q5 pack prepared','one candidate attempted'],'pending':[],'next_exact_action':'Read summary.json / report.md; no further request authorized'};r.c.save(R/'STATUS.json',status)
 report=['# Q5 single test — historical fastest Q4 configuration','',f'Status: {result["status"]}','',plan['comparison_limitation'],'']
 if result['status']=='COMPLETE':
  q=result['measured'];ref=result['Q4_reference'];report += ['| Model | Actual prompt | Output | PP tok/s | TG tok/s | TTFT s |','|---|---:|---:|---:|---:|---:|',f'| Q4 historical fastest | 31400 | 256 | {ref["PP"]:.1f} | {ref["TG"]:.1f} | {ref["TTFT"]:.3f} |',f'| Q5 single measured run | {q["actual_prompt_tokens"]} | {q["generated_tokens"]} | {q["pp_tps"]:.1f} | {q["tg_tps"]:.1f} | {q["ttft_s"]:.3f} |','',f'RAM peak physical(system total minus available): {q["peak_ram_used_gib"]:.2f}GiB; MemAvailable min {q["min_mem_available_gib"]:.2f}GiB; GPU0/1 peak {q["peak_vram0_gib"]:.2f}/{q["peak_vram1_gib"]:.2f}GiB.',f'Normal logical expert counters: {q["expert_tiers"]}. Physical SSD traffic behind virtiofs not attributable from these counters.','', 'One measured request, not a median or quality comparison. Exact saved Q4 payload except model alias. Same defaultv0132/K24/INT8/spec4/minp.5/prefillauto/max262144/MTP source; independent Q5 pack. One smoke8K64, one warmup31400256 excluded. PSS outside request clocks only; cheap telemetry1Hz; RAM abort12GiB. Full response and stream saved. No engine patch, weights change, model downloads, sweeps or production server left running.']
 else:report += [result.get('error','Unknown error'),'','See startup / engine logs; no extra candidate or fallback tested.']
 (R/'report.md').write_text('\n'.join(report)+'\n')
 import importlib.util
 spec=importlib.util.spec_from_file_location('status_render',R/'status-render.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.render()
if result['status']!='COMPLETE':raise SystemExit(1)
