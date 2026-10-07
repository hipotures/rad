"""Freeze the selected launchers, render the report and audit preserved evidence."""
import argparse, datetime, hashlib, json, pathlib, shutil, subprocess, time
import psutil
from lab import load, save
from pool_spin import C, POLICIES, status, verify_model

def fmt(x,n=1):return 'N/A' if x is None else f'{x:.{n}f}'
def median(c,k):return c['stats'][k]['median'] if c['stats'].get(k) else None
def table(headers,rows):return '| '+' | '.join(headers)+' |\n|'+ '|'.join(['---']*len(headers))+'|\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in rows)

def render():
 s=load(C/'summary.json');d=load(C/'decision.json');assert s['state']=='COMPLETE_24_VALID'
 assert d['recommendation'] in ['USE_100US','USE_500US','USE_2000US','USE_DEFAULT_20MS','CONTEXT_DEPENDENT']
 for profile in ['32k','128k']:
  policy=d['policies'][profile];assert policy in POLICIES;cfg=load(C/'configs'/f'{policy}-{profile}.json');save(C/'launchers'/f'{profile}.json',cfg)
  p=C/'launchers'/f'start-{profile}.sh';p.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec '+shlexquote(cfg['python'])+' '+shlexquote(str(C/'scripts/pool_spin.py'))+' start --profile '+profile+' "$@"\n');p.chmod(0o755)
 p=C/'launchers/stop.sh';python=load(C/'configs/100us-32k.json')['python']
 p.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec '+shlexquote(python)+' '+shlexquote(str(C/'scripts/pool_spin.py'))+' stop\n');p.chmod(0o755)
 main=[];ranges=[];gpu=[];wait=[]
 for c in s['cells']:
  main.append([c['policy'],c['profile'],fmt(median(c,'PP')),fmt(median(c,'TG')),fmt(median(c,'TTFT_s'),2),fmt(median(c,'wall_s'),2),fmt(median(c,'CPU_VM_pct')),fmt(median(c,'local_vram_share_all_pct')),fmt(median(c,'cpu_fallback_entries'),0),fmt(median(c,'nonlocal_gpu_entries'),0),fmt(median(c,'mtp_acceptance_pct'))])
  ranges.append([c['policy'],c['profile']]+[' / '.join(fmt(c['stats'][k][st],1 if k in ['PP','TG'] else 2) for st in ['min','median','max']) for k in ['PP','TG','TTFT_s','wall_s']])
  gpu.append([c['policy'],c['profile'],f"{c['primary_slots']}/{c['GPU1_slots']}",fmt(median(c,'CPU_process_one_core100'))]+[' / '.join(fmt(median(c,f'GPU{g}_{phase}_{k}')) for g in [0,1]) for phase,k in [('prefill','util_pct'),('decode','util_pct'),('decode','power_w'),('decode','vram_mib')]])
  wait.append([c['policy'],c['profile']]+[fmt(median(c,k),3 if k.endswith('_ms') else 2) for k in ['CPU_completion_ms','GPU_reach_wait_ms','CPU_distinct_experts_per_layer_window','CPU_entries_per_layer_window','window_ms']])
 pairs=[]
 for p in s['paired']:pairs.append([p['policy'],p['profile']]+[fmt(p['ratios'][k]['delta_pct'],2) for k in ['TG','wall_s','PP','CPU_VM_pct']])
 parity=s['parity'];same=sum(x['identical_output_ids'] for x in parity);mtpsame=sum(all(x['counter_equal'][k] for k in ['mtp_proposed','mtp_accepted','verify_windows']) for x in parity);routesame=sum(all(x['counter_equal'][k] for k in ['local_vram_entries','cpu_fallback_entries','nonlocal_gpu_entries','all_routed_entries']) for x in parity)
 inputs={p:[r['performance']['actual_input_tokens'] for r in s['runs'] if r['policy']=='100us' and r['profile']==p] for p in ['32k','128k']}
 commands='cd '+str(C/'launchers')+'\n./start-32k.sh --host 0.0.0.0 --port 8080\n# or, one server at a time\n./start-128k.sh --host 0.0.0.0 --port 8080\n./stop.sh'
 text='# Q4 layer-split: controlled CPU-pool spin comparison\n\n**24/24 valid measured requests**; each4096 output, zero reuse, suffix lookup OFF. Four policies × two total context limits × three preserved payloads. Every measured request has a fresh process and the same4096-input/64-output warmup. No extra measured repetitions, tuning, rebuild or engine/model change.\n\n'+table(['Spin policy','Context','PP tok/s','TG tok/s','TTFT s','Wall s','CPU VM %','VRAM/all hit %','CPU entries','PCIe entries','MTP accept %'],main)
 text+='\nAll cells show medians of three runs. CPU% is median of request decode sample means, across16vCPUs. VRAM denominator is **all routed entries**, including CPU and mapped/PCIe; the UI local/(local+CPU) statistic is not used for the headline. PCIe entries are logical mapped expert entries, not sampled physical bytes.\n\n'
 text+='## Run ranges\n\n'+table(['Policy','Context','PP min / median / max','TG min / median / max','TTFT min / median / max','Wall min / median / max'],ranges)+'\nEvery numeric metric also has min/median/max in summary.csv and summary.json; the individual run measurements remain linked from summary.json.\n\n'
 text+='## Paired ratios to100us\n\n'+table(['Policy','Context','TG delta %','Wall delta %','PP delta %','CPU delta %'],pairs)+'\nThese are medians of per-input paired ratios, not ratios of separately aggregated medians. Three samples are insufficient for narrow confidence intervals; the predeclared meaningful margin is3%, with inconsistent direction/overlapping variability treated conservatively. No favorable-run retry.\n\n'
 text+='## Selection and answers\n\n'+d['analysis_text']+'\n\nFrozen selection: **'+d['recommendation']+'**. Policies: '+json.dumps(d['policies'])+'. This is the CPU-pool prerequisite for Q4 residency-v2; no residency research was started.\n\n'
 text+='## CPU, GPU and completion waits\n\n'+table(['Policy','Context','Slots GPU0/GPU1','Process CPU %','Prefill GPU0/GPU1 %','Decode GPU0/GPU1 %','Decode power GPU0/GPU1 W','Decode VRAM GPU0/GPU1 MiB'],gpu)+'\nProcessCPU100%=one core; it cannot be compared directly to VMCPU100%=all16cores. Capacity is identical for every policy within a context. Source-defined default is `kSpinBeforeSleep{20}` in include/strata/kernels/cpu/pool.hpp; the default engine environment was verified to omit STRATA_POOL_SPIN_US, not assume a numerical override.\n\n'
 text+=table(['Policy','Context','CPU completion ms','GPU-reach wait ms','CPU experts/layer-window','CPU entries/layer-window','Decode window ms'],wait)+'\nThe unchanged binary exposes aggregate request-scoped CPU completion time, including overlapped compute/wait. **Conditional CPU-positive completion waits, all-local wait floor, exact worker sleep/wake counts and exclusive spin/compute split are unavailable.** They are null, never replaced with zero. CPU% alone does not identify useful work. No new hot-path instrumentation, PSS polling or profiler was used.\n\n'
 text+='## Correctness and protocol\n\nActual tokenizer/engine input-ID hashes match in all18 policy-vs100us pairs. Actual input counts: '+json.dumps(inputs)+'. Output IDs identical in **'+str(same)+'/18** pairs; aggregate offered/accepted/windows identical in **'+str(mtpsame)+'/18**; local/CPU/mapped/all routing counters identical in **'+str(routesame)+'/18**. First divergence and each counter delta are preserved in analysis/parity.json. Full per-window MTP trajectory is not available; matching aggregates alone do not prove trajectory parity. All output ID arrays contain4096 IDs, finish_reason=length. Warmup inputs/counts are identical for all24starts; warmup output hashes are also retained. No crash, OOM, invalid request or early EOS occurred. No concurrency.\n\n'
 text+='Fresh start before each measured request deliberately removes cross-request adaptive-cache history. This differs from the prior Q4 campaign, which used one server and three sequential measured requests per cell. Its PP/TG values therefore are **historical, not the control for this pool experiment**. The first full-length prefill is timed in every new run; PP is not made artificially warm by treating another full request as warmup.\n\n'
 text+='## Provenance and reproducibility\n\nBinary: `'+s['provenance']['binary_realpath']+'`; SHA256 `'+s['provenance']['binary_sha256']+'`; clean source `'+s['provenance']['source_sha']+'`; engine0.1.39 verified in every startup/API. No rebuild. Hardware/topology records are under git/. Model: existing Unsloth UD-Q4_K_XL, revision38bb39ee97821de2c9009abb7e93950eec396e66, four native shards plus compat-BF16 pack. Pack directory suffixv0132 identifies model data, not an old executable. Complete model sizes/mtimes/prior verified SHA and current pack/profile/MTP hashes are in git/model.json. Routed arena77,017,907,200bytes stays in RAM; request expert-file counters are retained.\n\nCommon settings: K24/.28, pool15, spec4/minp.5, INT8, kv-resident32768, prefillauto, greedy, same MTP/profile/tokenizer, CVD0,1. At32K the effective streamed KVresident reports0 because the full context fits; the argument is unchanged. Existing lightweight STRATA_SPLIT_TIMING/STRATA_DECODE_TIMING are equal in all arms. Only the pool override is intentionally varied. Complete commands/configs, actual child environments and capacities are preserved per request.\n\n'
 text+='## Launch commands\n\n```bash\n'+commands+'\n```\n\nLaunchers verify frozen binary/source/model paths, retain the selected explicit pool policy (or explicitly scrub/unset the default), print complete resolved settings, refuse activeGPU/Strata processes and port collisions, and stream live logs. Each start creates a separate timestamped manual directory. Previous Q4/IQ3 launchers remain untouched. `--check` validates without inference. `scripts/reproduce-analysis.sh` recomputes analysis/report/audit without benchmarking.\n\nFinal cleanup/provenance audit: analysis/audit.json. All raw data remain preserved. No push, PR, model change, residency, helper,256K or unrelated experiment.\n\n'+d['recommendation']+'\n'
 for old,new in [
  ('each4096','each 4096'),('same4096','same 4096'),('input/64-output','input / 64-output'),
  ('across16vCPUs','across 16 vCPUs'),('to100us','to 100us'),('is3%','is 3%'),
  ('CPU100%','CPU 100%'),('16cores','16 cores'),('source0.1.39','source 0.1.39'),
  ('ofthree','of three'),
  ('all18','all 18'),('all24starts','all 24 starts'),('contain4096','contain 4096'),
  ('engine0.1.39','engine 0.1.39'),('revision38bb','revision 38bb'),
  ('arena77,017','arena 77,017'),('200bytes','200 bytes'),('K24/.28','K=24 / PCIe=0.28'),
  ('pool15','workers 15'),('spec4/minp.5','spec=4 / min-p=0.5'),
  ('kv-resident32768','kv-resident=32768'),('prefillauto','prefill=auto'),
  ('At32K','At 32K'),('reports0','reports 0'),('helper,256K','helper, 256K'),
  ('approximately45','approximately 45'),('than2%','than 2%'),('100us,500us','100us, 500us'),
  ('14.45ms','14.45 ms'),('ProcessCPU','Process CPU'),('VMCPU','VM CPU'),
  ('all16','all 16'),('vs100us','vs 100us'),('suffixv0132','suffix v0132'),
  ('CVD0,1','CUDA_VISIBLE_DEVICES=0,1'),('KVresident','KV resident'),('activeGPU','active GPU')
 ]:text=text.replace(old,new)
 (C/'report.md').write_text(text)
 (C/'launchers/README.md').write_text('# Selected frozen Q4 CPU-pool baseline\n\n'+d['recommendation']+'\n\n```bash\n'+commands+'\n```\n\nUse one server at a time. Ctrl-C or stop.sh stops the identified owned process. --check prints/verifies config without starting inference. Source0.1.39, K24/.28, frozen binarySHA verified; model data pathv0132 does not select an old runtime. Logs are streamed and persisted under manual/.\n')
 (C/'README.md').write_text('# Q4 pool-spin bounded campaign\n\nSee report.md, summary.json/csv and STATUS.md. Original24-request matrix is complete; do not run it again. Reproduce analysis only with scripts/reproduce-analysis.sh. Stop serving first: the reproduction audit requires idle GPUs and the unchanged frozen source/model. Analysis reproduction after the original deadline is allowed; it starts no inference. Selected launchers are in launchers/.\n')
 python=load(C/'configs/100us-32k.json')['python'];p=C/'scripts/reproduce-analysis.sh';p.write_text('#!/usr/bin/env bash\nset -euo pipefail\n'+shlexquote(python)+' '+shlexquote(str(C/'scripts/analyze_pool.py'))+'\n'+shlexquote(python)+' '+shlexquote(str(C/'scripts/finish_pool.py'))+' render\n'+shlexquote(python)+' '+shlexquote(str(C/'scripts/finish_pool.py'))+' audit\n');p.chmod(0o755)
 print('REPORT AND LAUNCHERS',d['recommendation'])

def shlexquote(x):
 import shlex
 return shlex.quote(x)

def audit():
 s=load(C/'summary.json');assert len(s['runs'])==24 and s['state']=='COMPLETE_24_VALID';verify_model(load(C/'configs/100us-32k.json'),full=True)
 for path,h in load(C/'git/protected-files.json').items():assert hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()==h,('PREVIOUS_FILE_CHANGED',path)
 old=pathlib.Path(load(C/'protocol.json')['old_campaign']);old_inventory=load(old/'git/artifact-sha256.json')
 for rel,h in old_inventory.items():assert hashlib.sha256((old/rel).read_bytes()).hexdigest()==h,('PREVIOUS_ARTIFACT_CHANGED',rel)
 for x in s['runs']:
  r=load(x['raw']);assert r['state']=='VALID' and r['actual_output_tokens']==4096 and r['reuse']==0 and r['finish_reason']=='length';assert len(load(r['actual_output_ids_path']))==4096
  cfg=r['full_config'];verify_model(cfg);expected=cfg['env'].get('STRATA_POOL_SPIN_US');env=x['environment'];assert env['environment'].get('STRATA_POOL_SPIN_US')==expected
  assert env['pool_override_present']==(expected is not None);assert r['mtp_proposed']>0 and r['mtp_accepted']>0
  assert r['source_sha']==s['provenance']['source_sha'] and r['binary_sha256']==s['provenance']['binary_sha256'];assert x['resource']['split_K']==24
  assert r['all_routed_entries']==r['local_vram_entries']+r['cpu_fallback_entries']+r['nonlocal_gpu_entries'],'Routed denominator mismatch'
  assert abs(r['local_vram_share_all_pct']-100*r['local_vram_entries']/r['all_routed_entries'])<1e-9
  args=r['full_engine_commands'][0]
  for k,v in {'--layer-split':'24','--pcie-frac':'.28','--pool-workers':'15','--spec':'4','--spec-min-p':'0.5','--kv':'int8','--kv-resident':'32768','--prefill':'auto','--suffix-draft':'0','--prompt-cache':'0','--max-context':str(cfg['max_total_context'])}.items():assert args[args.index(k)+1]==v,(k,args)
  assert '--remote-expert-opt' not in args and '--expert-cache-device1' not in args
  assert env['environment']['CUDA_VISIBLE_DEVICES']=='0,1'
  info=load(C/'inputs/manifest.json')['payloads'][x['profile']+'-run'+str(x['replicate'])];assert hashlib.sha256(json.dumps(load(info['token_ids_path']),separators=(',',':')).encode()).hexdigest()==x['input_sha256']
 for profile in ['32k','128k']:
  p=subprocess.run([str(C/'launchers'/f'start-{profile}.sh'),'--check'],capture_output=True,text=True);(C/'logs'/f'launcher-check-{profile}.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 gpu=subprocess.check_output(['nvidia-smi','--query-gpu=index,name,memory.used,utilization.gpu','--format=csv'],text=True);assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
 remaining=[]
 for p in psutil.process_iter(['pid','exe','cmdline']):
  try:
   words=p.info['cmdline'] or []
   if p.info['exe'] and pathlib.Path(p.info['exe']).resolve()==pathlib.Path(s['provenance']['binary_realpath']).resolve():remaining.append(p.info)
   elif any(str(C) in w for w in words) and any(z in words for z in ['matrix','--engine']):remaining.append(p.info)
  except psutil.Error:pass
 assert not remaining,remaining
 now=time.time();d=load(C/'deadline.json');prior=load(C/'analysis/audit.json') if (C/'analysis/audit.json').exists() else None
 # Future raw-only reproductions must retain the original campaign completion
 # timestamp. They do not extend the experiment deadline or start inference.
 completed=prior['completed_epoch'] if prior else now
 assert completed<d['deadline_epoch'],'Two-hour limit exceeded'
 evidence={'state':'PASS','valid_measured':24,'fixed_warmups':24,'all_outputs4096':True,'inputs_paired':True,'all_capacities_equal_by_context':True,'binary_source_model_unchanged':True,'all_previous_campaign_artifacts_unchanged':True,'GPU_idle':True,'GPU_snapshot':gpu,'remaining_owned_processes':remaining,'completed_epoch':completed,'ended_utc':datetime.datetime.fromtimestamp(completed,datetime.timezone.utc).isoformat(),'elapsed_seconds':completed-d['started_epoch'],'deadline_met':True,'no_rebuild_push_PR_model_changes':True}
 if prior:save(C/'analysis'/('revalidation-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+'.json'),dict(evidence,revalidated_epoch=now))
 else:save(C/'analysis/audit.json',evidence)
 scripts={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (C/'scripts').glob('*') if p.is_file()};save(C/'git/harness-sha256.json',scripts)
 inventory={str(p.relative_to(C)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(C.rglob('*')) if p.is_file() and p.name not in ['artifact-sha256.json','STATUS.md','STATUS.json'] and '__pycache__' not in p.parts};save(C/'git/artifact-sha256.json',inventory)
 status('COMPLETE',current=None,pending=[],completed=['24valid requests','24identical warmup-counts','paired input/output/counters audit','policy selection','report/summary','separate launchers checked','previous artifacts unchanged','owned processes stopped; bothGPUsidle'],next_exact_action='user review; no automatic residency campaign')
 print('AUDIT PASS24',len(inventory),'artifacts','GPUsidle; deadline met')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['render','audit']);a=p.parse_args();render() if a.action=='render' else audit()
