"""Derive the completed27-request comparison solely from frozen raw artifacts."""
import argparse, csv, datetime, hashlib, json, math, pathlib, re, shutil, statistics, subprocess
from lab import ROOT, load, save
from q4_multigpu import status
ap=argparse.ArgumentParser();ap.add_argument('--campaign',type=pathlib.Path,required=True);a=ap.parse_args();C=a.campaign
methods=['layer-split','original-helper','optimized-helper'];profiles=['32k','128k','256k']
def med(v):
 v=[x for x in v if x is not None];return statistics.median(v) if v else None
def stats(v):
 v=[x for x in v if x is not None];return {'min':min(v),'mean':statistics.mean(v),'median':statistics.median(v),'max':max(v)} if v else None
def f(x,n=1):return 'N/A' if x is None else f'{x:.{n}f}'
def pcie_phases(r):
 p=pathlib.Path(r['telemetry']['path']).with_name('pcie-dmon.log');rows=[]
 for line in p.read_text().splitlines():
  t=line.split()
  if len(t)!=5 or t[0].startswith('#'):continue
  try:rows.append({'epoch':datetime.datetime.strptime(t[0]+' '+t[1],'%Y%m%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc).timestamp(),'GPU':int(t[2]),'RX_MBps':float(t[3]),'TX_MBps':float(t[4])})
  except ValueError:continue
 start=r['started_epoch'];first=start+r['TTFT_s'];end=start+r['wall_s'];out={}
 for name,lo,hi in [('prefill',start,first),('decode',first,end)]:
  out[name]={str(i):{k:stats([x[k] for x in rows if x['GPU']==i and lo<=x['epoch']<hi]) for k in ['RX_MBps','TX_MBps']} for i in [0,1]}
 return out
def phases(r):
 s=[json.loads(l) for l in pathlib.Path(r['telemetry']['path']).read_text().splitlines()];start=r['started_epoch'];first=start+r['TTFT_s'];end=start+r['wall_s'];out={}
 for name,lo,hi in [('prefill',start,first),('decode',first,end)]:
  rows=[x for x in s if lo<=x['wall_time']<hi];q={'samples':len(rows),'CPU_system_pct':stats([x['system_cpu_pct'] for x in rows]),'CPU_process_pct_one_core100':stats([sum(p['cpu_pct'] for p in x['processes']) for x in rows if x['processes']]),'RSS_sum_GiB':stats([sum(p['rss_gib'] for p in x['processes']) for x in rows if x['processes']]),'RAM_used_GiB':stats([x['ram_used_gib'] for x in rows]),'RAM_available_GiB':stats([x['mem_available_gib'] for x in rows]),'gpus':{}}
  for device in [0,1]:
   gs=[g for x in rows for g in x.get('gpus',[]) if g['index']==device];hw=[g for x in rows for g in ((x.get('metrics') or {}).get('hardware') or {}).get('gpus',[]) if g['index']==device]
   q['gpus'][str(device)]={k:stats([g.get(k) for g in gs]) for k in ['util_pct','power_w','vram_mib','sm_mhz']}
   temps=[g.get('temp') for g in hw]
   if device==0 and not hw:temps=[((x.get('metrics') or {}).get('hardware') or {}).get('gpu_temp') for x in rows]
   temp_path=C/'telemetry/temperature-dmon.log';extra=[]
   if temp_path.exists():
    for line in temp_path.read_text().splitlines():
     t=line.split()
     if len(t)!=6 or t[0].startswith('#'):continue
     try:
      epoch=datetime.datetime.strptime(t[0]+' '+t[1],'%Y%m%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc).timestamp()
      if int(t[2])==device and lo<=epoch<hi:extra.append(float(t[4]))
     except ValueError:continue
   q['gpus'][str(device)]['temp_C']=stats(temps) if any(t is not None for t in temps) else stats(extra)
   q['gpus'][str(device)]['temp_sampling']='cachedMonitor' if any(t is not None for t in temps) else 'additional1HzNVML' if extra else 'UNAVAILABLE'
   q['gpus'][str(device)]['temp_samples']=len([t for t in temps if t is not None]) or len(extra)
  q['sampled_aggregate_PCIe_RX_MBps']=stats([((x.get('metrics') or {}).get('hardware') or {}).get('gpu_pcie_rx_mb') for x in rows]);q['sampled_aggregate_PCIe_TX_MBps']=stats([((x.get('metrics') or {}).get('hardware') or {}).get('gpu_pcie_tx_mb') for x in rows]);out[name]=q
 return out
rows=[];runs=[];warmups=[]
for method in methods:
 for profile in profiles:
  base=C/'raw'/method/profile;rs=load(base/'results.json');assert len(rs)==3 and all(r['state']=='VALID' and r['actual_output_tokens']==4096 and r['reuse']==0 and r['actual_engine_input_verified'] for r in rs)
  resource=load(base/'raw/resource-check.json');warm=load(base/'raw/warmup.json');assert warm['actual_output_tokens']==64 and warm['actual_engine_input_verified'];warmups.append({'method':method,'profile':profile,'input':warm['actual_input_tokens'],'output':warm['actual_output_tokens'],'input_hash':warm['actual_engine_input']['sha256']})
  for i,r in enumerate(rs,1):
   x={'method':method,'profile':profile,'run':i,'raw_path':str(base/'raw'/f'run{i}.json'),'performance':{k:r.get(k) for k in ['actual_input_tokens','actual_output_tokens','PP','TG','TTFT_s','wall_s','pp_s','decode_s','finish_reason','reuse','mtp_proposed','mtp_accepted','mtp_acceptance_pct','mtp_accepted_per_window','verify_windows','hit_rate_pct','local_vram_entries','cpu_fallback_entries','nonlocal_gpu_entries','nonlocal_gpu_share_pct','all_routed_entries','local_vram_share_all_pct','cpu_share_all_pct']},'system':phases(r),'stage_timings':r['stage_timings'],'remote':r['remote_counters'],'output_ID_hash':r.get('actual_output_ids_sha256'),'input_hash':r['actual_engine_input']['sha256']}
   # The existing unmodified decode timing line is request-scoped, unlike cumulative stage logs.
   log=(base/'raw'/f'run{i}-engine.log').read_text();m=re.search(r'(strata decode timing: .*?)\n',log);x['decode_timing_line']=m[1] if m else None
   timing=x['decode_timing_line'] or '';x['decode_timing_components']={}
   for name,pattern in {
    'window_ms':r'([\d.]+) ms/window',
    'GPU_reach_wait_ms':r'GPU-reach wait ([\d.]+)',
    'host_ms':r'per-layer host ([\d.]+)',
    'activation_quantization_ms':r'actq ([\d.]+)',
    'CPU_completion_ms':r' CPU ([\d.]+)\]',
    'CPU_distinct_experts_per_layer_window':r'CPU experts ([\d.]+)',
    'CPU_entries_per_layer_window':r'CPU experts [\d.]+ \(([\d.]+) entries\)',
   }.items():
    found=re.search(pattern,timing);x['decode_timing_components'][name]=float(found[1]) if found else None
   x['remote_wait_ms']=[float(m[1]) for m in re.finditer(r'host [\d.]+ ms staging\+launching, ([\d.]+) ms waiting',log)]
   x['PCIe_dmon']=pcie_phases(r)
   x['KV_streaming_primary_cumulative']=[{'hit_pct':float(m[1]),'block_reads':int(m[2]),'RAM_read_MiB':float(m[3])} for m in re.finditer(r'KV streaming: ([\d.]+)% of (\d+) block reads hit VRAM, ([\d.]+) MiB read from RAM',log)]
   x['returned_MiB']=sum(z['returned_MiB'] for z in r['remote_counters']) if r['remote_counters'] else None
   x['full_row_MiB']=sum(z['full_row_MiB'] for z in r['remote_counters']) if r['remote_counters'] else None
   # Existing engine-DONE fields exposed in metrics requests provide request I/O if available.
   metrics=load(base/'raw'/f'run{i}-metrics.json');matches=[z for z in metrics.get('requests',[]) if z.get('prompt_tokens')==r['actual_input_tokens'] and z.get('output_tokens')==r['actual_output_tokens']];x['metrics_request']=matches[0] if matches else None
   runs.append(x)
  rr=runs[-3:]
  row={'method':method,'context':int(profile[:-1])*1024,'profile':profile,'n':3,'actual_input':med([r['actual_input_tokens'] for r in rs]),'PP':med([r['PP'] for r in rs]),'PP_min':min(r['PP'] for r in rs),'PP_max':max(r['PP'] for r in rs),'TG':med([r['TG'] for r in rs]),'TG_min':min(r['TG'] for r in rs),'TG_max':max(r['TG'] for r in rs),'TTFT_s':med([r['TTFT_s'] for r in rs]),'wall_s':med([r['wall_s'] for r in rs]),'pp_s':med([r['pp_s'] for r in rs]),'decode_s':med([r['decode_s'] for r in rs]),'displayed_hit_pct':med([r['hit_rate_pct'] for r in rs]),'local_VRAM_all_pct':med([r.get('local_vram_share_all_pct') for r in rs]),'PCIe_or_remote_share_pct':med([r.get('nonlocal_gpu_share_pct') for r in rs]),'CPU_entries':med([r.get('cpu_fallback_entries') for r in rs]),'CPU_share_pct':med([r.get('cpu_share_all_pct') for r in rs]),'CPU_system_decode_pct':med([x['system']['decode']['CPU_system_pct']['mean'] for x in rr]),'CPU_process_decode_pct_one_core100':med([x['system']['decode']['CPU_process_pct_one_core100']['mean'] for x in rr]),'GPU0_decode_pct':med([x['system']['decode']['gpus']['0']['util_pct']['mean'] for x in rr]),'GPU1_decode_pct':med([x['system']['decode']['gpus']['1']['util_pct']['mean'] for x in rr]),'GPU0_prefill_pct':med([x['system']['prefill']['gpus']['0']['util_pct']['mean'] for x in rr]),'GPU1_prefill_pct':med([x['system']['prefill']['gpus']['1']['util_pct']['mean'] for x in rr]),'MTP_accept_pct':med([r['mtp_acceptance_pct'] for r in rs]),'accepted_per_window':med([r['mtp_accepted_per_window'] for r in rs]),'primary_slots':resource['primary_slots'],'secondary_slots':resource['helper_or_stage1_slots'],'resident_fraction_pct':100*resource['initial_resident_count']/24576,'cache_primary_MiB_reported':resource['cache_MiB_primary'],'cache_secondary_MiB_reported':resource['cache_MiB_total']-resource['cache_MiB_primary'],'split_K':resource['split_K'],'pcie_frac':resource['engine']['pcie_frac'],'helper_returned_MiB':med([x['returned_MiB'] for x in rr]),'helper_wait_ms':med([sum(x['remote_wait_ms']) if x['remote_wait_ms'] else None for x in rr]),'raw_paths':[x['raw_path'] for x in rr],'resources':resource}
  rows.append(row)
  for device in ['0','1']:
   row[f'GPU{device}_decode_power_W']=med([x['system']['decode']['gpus'][device]['power_w']['mean'] for x in rr])
   row[f'GPU{device}_peak_VRAM_MiB']=max(x['system'][p]['gpus'][device]['vram_mib']['max'] for x in rr for p in ['prefill','decode'])
   row[f'GPU{device}_decode_temp_C']=med([x['system']['decode']['gpus'][device]['temp_C']['mean'] if x['system']['decode']['gpus'][device]['temp_C'] else None for x in rr])
   row[f'GPU{device}_decode_PCIE_RX_MBps']=med([x['PCIe_dmon']['decode'][device]['RX_MBps']['mean'] if x['PCIe_dmon']['decode'][device]['RX_MBps'] else None for x in rr])
   row[f'GPU{device}_decode_PCIE_TX_MBps']=med([x['PCIe_dmon']['decode'][device]['TX_MBps']['mean'] if x['PCIe_dmon']['decode'][device]['TX_MBps'] else None for x in rr])
  row['peak_RAM_used_GiB']=max(x['system'][p]['RAM_used_GiB']['max'] for x in rr for p in ['prefill','decode'])
  row['peak_sum_RSS_GiB']=max(x['system'][p]['RSS_sum_GiB']['max'] for x in rr for p in ['prefill','decode'])
  row['min_RAM_available_GiB']=min(x['system'][p]['RAM_available_GiB']['min'] for x in rr for p in ['prefill','decode'])
  row['expert_file_blobs_request_median']=med([(x['metrics_request'] or {}).get('file_blobs') for x in rr])
  row['expert_file_MB_request_median']=med([(x['metrics_request'] or {}).get('file_mb') for x in rr])
assert len(runs)==27
for profile in profiles:
 old=next(x for x in rows if x['method']=='original-helper' and x['profile']==profile);opt=next(x for x in rows if x['method']=='optimized-helper' and x['profile']==profile)
 assert (old['primary_slots'],old['secondary_slots'])==(opt['primary_slots'],opt['secondary_slots']),'unfair helper capacities'
 for i in [1,2,3]:assert len({x['input_hash'] for x in runs if x['profile']==profile and x['run']==i})==1
assert len({w['input_hash'] for w in warmups})==1
comparisons=[]
for profile in profiles:
 for i in [1,2,3]:
  ref=load(C/'raw/layer-split'/profile/'raw'/f'output-ids-request{i+1}.json')
  for method in ['original-helper','optimized-helper']:
   other=load(C/'raw'/method/profile/'raw'/f'output-ids-request{i+1}.json');first=next((j for j,(u,v) in enumerate(zip(ref,other)) if u!=v),None)
   comparisons.append({'profile':profile,'run':i,'reference':'layer-split','other':method,'identical_output_ids':ref==other,'first_diverging_output_ID':first,'positionwise_agreement_pct':100*sum(u==v for u,v in zip(ref,other))/max(len(ref),len(other)),'scope':'Greedy trajectories after a first divergence are not tokenwise model correctness tests; summation order may differ.'})
winners={}
for profile in profiles:
 cells=[r for r in rows if r['profile']==profile];winners[profile]={'decode':max(cells,key=lambda r:r['TG'])['method'],'prefill':max(cells,key=lambda r:r['PP'])['method'],'request_wall':min(cells,key=lambda r:r['wall_s'])['method']}
overall=min(methods,key=lambda m:sum(math.log(next(r['wall_s'] for r in rows if r['method']==m and r['profile']==p)) for p in profiles))
recommendations={'layer-split':'USE_LAYER_SPLIT','original-helper':'USE_ORIGINAL_HELPER','optimized-helper':'USE_OPTIMIZED_HELPER'}
recommendation=recommendations[overall] if len({v['request_wall'] for v in winners.values()})==1 else 'CONTEXT_DEPENDENT'
est=[]
for method in methods:
 for name,input_n,output_n,profile in [('8K+2K',8192,2048,'32k'),('32K+4K',32768,4096,'32k'),('128K+4K',131072,4096,'128k'),('256K+4K',262144,4096,'256k')]:
  r=next(x for x in rows if x['method']==method and x['profile']==profile);est.append({'method':method,'workload':name,'input_tokens':input_n,'output_tokens':output_n,'estimated_s':input_n/r['PP']+output_n/r['TG'],'source_profile':profile,'methodology':'P/PP+G/TG, extrapolation not measured latency. Full32K/128K/256K inputs plus4K need a larger admission limit than the tested total profiles.8K especially has unmeasured smaller-prompt PP.'})
summary={'state':'COMPLETE_27_VALID','recommendation':recommendation,'overall_practical_method':overall,'winners':winners,'cells':rows,'runs':runs,'warmups':warmups,'output_comparisons':comparisons,'request_time_estimates':est,'provenance':load(C/'git/environment.json'),'model':load(C/'git/model.json'),'layer_selection':load(C/'analysis/layer-selection.json'),'limitations':['3serial runs after64-output warmup per fresh server/cell, not3independent server replicas.','Different architecture may change floating summation/output/MTP; same input/config controlled, trajectory differences quantified.','Displayed hit denominator excludes PCIe/helper entries; all-routed local residency reported separately.','1Hz metrics/dmon are sampled aggregate traffic, not logical expert bytes or exclusive critical-path time.','Per-thread CPU computation vs synchronization not independently profiled on headline binary.','No per-expert overlap/capacity-ID instrumentation or expensivePSS.']}
save(C/'summary.json',summary);save(C/'analysis/run-details.json',runs);save(C/'analysis/output-parity.json',comparisons);save(C/'analysis/request-time-estimates.json',est)
flatkeys=[k for k,v in rows[0].items() if k not in ['resources','raw_paths']]
with (C/'summary.csv').open('w') as out:
 w=csv.DictWriter(out,fieldnames=flatkeys);w.writeheader();w.writerows({k:r[k] for k in flatkeys} for r in rows)
# Preserve exact source scripts used to derive and reproduce the artifacts.
# A later reproduction from the snapshot must not import newer laboratory utilities.
frozen_run=pathlib.Path(__file__).resolve().parent==(C/'scripts').resolve()
if not frozen_run:
 for name in ['init_q4_multigpu.py','q4_multigpu.py','analyze_q4_multigpu.py','render_q4_report.py','audit_q4_multigpu.py']:
  shutil.copy2(ROOT/'scripts'/name,C/'scripts'/name)
 # Freeze the existing harness dependencies too; only its filesystem root is made explicit.
 labsource=(ROOT/'scripts/lab.py').read_text();frozenlab=labsource.replace('ROOT=pathlib.Path(__file__).resolve().parents[1]','ROOT=pathlib.Path('+repr(str(ROOT))+')')
 (C/'scripts/lab.py').write_text(frozenlab)
 for name in ['serve_capture.py','record_ui_metrics.py']:shutil.copy2(ROOT/'scripts'/name,C/'scripts'/name)
 save(C/'git/harness-freeze.json',{'original_lab_sha256':hashlib.sha256(labsource.encode()).hexdigest(),'snapshot_lab_sha256':hashlib.sha256(frozenlab.encode()).hexdigest(),'change':'filesystem ROOT made explicit in harness copy only; no engine change','files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (C/'scripts').glob('*.py')}})
else:
 for name,h in load(C/'git/harness-freeze.json')['files'].items():
  assert hashlib.sha256((C/'scripts'/name).read_bytes()).hexdigest()==h,('Frozen harness changed',name)
launch=[]
for profile in profiles:
 selected=winners[profile]['request_wall'] if recommendation=='CONTEXT_DEPENDENT' else overall
 cfg=load(C/'configs'/f'{selected}-{profile}.json');cfg['server_entrypoint']=str(C/'scripts/serve_capture.py');save(C/'launchers'/f'{profile}.json',cfg)
 p=C/'launchers'/f'start-{profile}.sh';p.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec "'+cfg['python']+'" "'+str(C/'scripts/q4_multigpu.py')+'" --campaign "'+str(C)+'" start --profile '+profile+' "$@"\n');p.chmod(0o755);launch.append({'profile':profile,'method':selected,'path':str(p),'config':str(C/'launchers'/f'{profile}.json')})
p=C/'launchers/stop.sh';p.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec "'+str(ROOT/'src/control/.venv/bin/python')+'" "'+str(C/'scripts/q4_multigpu.py')+'" --campaign "'+str(C)+'" stop\n');p.chmod(0o755)
save(C/'launchers/index.json',launch)
(C/'launchers/README.md').write_text('# Frozen current Strata Q4 launchers\n\nBinary: `'+summary['provenance']['binary_realpath']+'`\n\nSHA256: `'+summary['provenance']['binary_sha256']+'`\n\nSource: `'+summary['provenance']['source_sha']+'` (0.1.39).\n\nSelected method: **'+overall+'**. Each JSON preserves the complete model/MTP/cache/KV/pool configuration. The model pack directory name containing v0132 is only a historical data path.\n\nRun one launcher at a time, for example:\n\n```bash\n./start-128k.sh --host 0.0.0.0 --port 8080\n```\n\nUse start-32k.sh or start-256k.sh for the other total context limits. `--check` prints and verifies the resolved configuration without starting inference. The foreground launcher streams server and engine logs, persists UI Monitor metrics, verifies the expected executable SHA and clean source HEAD, checks available RAM and refuses an occupied port or conflicting GPU/Strata processes. Ctrl-C or `./stop.sh` stops only the identified owned server. Each manual start writes a new timestamped manual/ directory; no previous launchers or results are modified.\n')
(C/'launch-index.md').write_text('# Q4 controlled campaign launch index\n\n'+''.join('- '+x['profile']+': ['+pathlib.Path(x['path']).name+']('+x['path']+'), '+x['method']+', [resolved config]('+x['config']+')\n' for x in launch)+'\nStop: [stop.sh]('+str(C/'launchers/stop.sh')+').\n\nUse `--host 0.0.0.0 --port 8080` for LAN serving. Run one configuration at a time. Existing IQ3_S P1 launchers remain untouched.\n')
text='# Q4 UD-Q4_K_XL: current0.1.39 dualRTX4090\n\nComplete:27 valid measured requests, each4096 output,9 identical64-output warmups. All input hashes match across methods. No engine rebuild/patch, model change, push or PR. The old0.1.32 Q4 is `INVALID_AS_CURRENT_CONTROL`.\n\n'
text+='Frozen binary `'+summary['provenance']['binary_realpath']+'`, SHA256 `'+summary['provenance']['binary_sha256']+'`; source `'+summary['provenance']['source_sha']+'`. Common settings: pool100µs/workers15/spec4/minp0.5/INT8/KVresident32768/prefillauto/suffix0/promptcache0/greedy/serial. Q4revision38bb39e, full71.73GiB RAM arena.32K KV reportsresident0 because the whole32K fits; larger profiles stream with32768 resident cells.\n\n'
text+='|Method|Totalcontext|Actualinput|PP|TG|TGmin–max|TTFTs|Walls|Displayedhit%|Local/all%|PCIe/helper%|CPUVMdecode%|GPU0%|GPU1%|\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n'
for r in rows:text+='|'+r['method']+'|'+r['profile']+'|'+str(int(r['actual_input']))+'|'+f(r['PP'])+'|'+f(r['TG'])+'|'+f(r['TG_min'])+'–'+f(r['TG_max'])+'|'+f(r['TTFT_s'],2)+'|'+f(r['wall_s'],2)+'|'+f(r['displayed_hit_pct'])+'|'+f(r['local_VRAM_all_pct'])+'|'+f(r['PCIe_or_remote_share_pct'])+'|'+f(r['CPU_system_decode_pct'])+'|'+f(r['GPU0_decode_pct'])+'|'+f(r['GPU1_decode_pct'])+'|\n'
text+='\nEvery number is a median of3; CPU/GPU cells are medians of per-request decode sample means. All raw paths are in summary.json. Displayed hit%=local/(local+CPU), excludesmapped/helper work; local/all is the safer residency metric. PCIe/helper share is logical entries, not sampled bandwidth.\n\n## BEST DECODE / BEST PREFILL / BEST OVERALL\n\n'
for p,v in winners.items():text+=f'- {p}: decode **{v["decode"]}**, prefill **{v["prefill"]}**, measured full-request wall **{v["request_wall"]}**.\n'
text+='\nOverall geometric-mean request-time winner: **'+overall+'** for this offline repository-maintenance workload. This is not a universal quality/workload claim.\n\n## CPU / RESIDENCY\n\n|Method|Profile|SlotsGPU0/GPU1|Residentfraction%|CacheMiB0/1|CPUentries|CPUshare%|MTPaccept%|Accepted/window|HelperreturnMiB|Helperwaitms|\n|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n'
for r in rows:text+='|'+r['method']+'|'+r['profile']+'|'+str(r['primary_slots'])+'/'+str(r['secondary_slots'])+'|'+f(r['resident_fraction_pct'])+'|'+str(r['cache_primary_MiB_reported'])+'/'+str(r['cache_secondary_MiB_reported'])+'|'+f(r['CPU_entries'],0)+'|'+f(r['CPU_share_pct'])+'|'+f(r['MTP_accept_pct'])+'|'+f(r['accepted_per_window'],2)+'|'+f(r['helper_returned_MiB'])+'|'+f(r['helper_wait_ms'],0)+'|\n'
text+='\nOriginal/optimized helper initial capacities match exactly perprofile. Startup overlap0 is justified by allocator ownership exclusion, not a runtime ID dump. Overlap after adaptation is unavailable; original primary can duplicate fixed helper experts, optimized excludes them. Do not assume postwarmup overlap0. Cache MiB are rounded engine counters. Remote returned bytes and waits are requestscoped including any prompt-tail work; sampled dmon RX/TX is separate undertelemetry.\n\nIQ3_S P1 reference:32K10240+8477 slots (76.16%),128K10183+8437(75.76%) from `analysis/control-budgets-v2.json`. Q4slots in the table use actual Q4 byte classes; the arena totals77,017,907,200bytes for24,576 experts.\n\nCPUentries derive from requestdecode lookups minus localhits. They prove useful expert fallback remains, but neither CPU% nor pool completion waits establish an exclusive CPUcompute/spin attribution. The same100µs spin setting is enforced in all arms. Request-scoped existing decode timing lines and cumulative stage timings are preserved in analysis/run-details.json; cumulative stage averages are not per-request independent kernel times.\n\n## 256K\n\n'
for m in methods:
 a=next(x for x in rows if x['method']==m and x['profile']=='128k');b=next(x for x in rows if x['method']==m and x['profile']=='256k');text+=f'- {m}: TG128K→256K {a["TG"]:.1f}→{b["TG"]:.1f} ({100*(b["TG"]/a["TG"]-1):+.1f}%), TTFT{a["TTFT_s"]:.2f}→{b["TTFT_s"]:.2f}s; displayedhit{a["displayed_hit_pct"]:.1f}→{b["displayed_hit_pct"]:.1f}%.\n'
text+='\nThe256K input is257.78K, not259K:4096 output and a fixedreserve fit the262144total limit. Different input corpus prefixes/output trajectories and MTP mean this is not isolatedKVcost.\n\n## Practical request-time estimates\n\n|Method|8K+2K|32K+4K|128K+4K|256K+4K|\n|---|---:|---:|---:|---:|\n'
for m in methods:text+='|'+m+'|'+ '|'.join(f(next(e['estimated_s'] for e in est if e['method']==m and e['workload']==n),2) for n in ['8K+2K','32K+4K','128K+4K','256K+4K'])+'|\n'
text+='\nSeconds=P/PP+G/TG; modeled, not additional measurements.8Kprefill is extrapolated from32K. A full32Kinput+4Koutput needs a total limit above32768, likewise other nominalfullinputs; actual measured admissible inputs are in the main table. Client wall includes frontend/tokenization/transport, which the simple model omits.\n\n## FUTURE RESIDENCY RESEARCH\n\n'
for r in rows:
 if r['method']=='layer-split':text+=f'- {r["profile"]}: {r["resident_fraction_pct"]:.1f}% of experts resident, {100-r["local_VRAM_all_pct"]:.1f}% of routedentries nonlocal; CPU{r["CPU_share_pct"]:.1f}%, mapped/remote{r["PCIe_or_remote_share_pct"]:.1f}%.\n'
text+='\nThis quantifies placementheadroom but does not establish a latencygain from prediction. A hypothetical50% reduction in CPU entries removes50% of that logical CPU share, not50% of request time. Bytecost and victim damage must be charged; Q4 experts are3.072–3.994MB each. No predictor was implemented. FullRAMarena means mappedexpert demand is RAM/PCIe, not evidence of pertok SSDexpert streaming. Physical diskread metrics may includePLE; expertIO attribution is limited to explicit runtime counters.\n\n## Provenance, correctness and limitations\n\n'
text+=f'{sum(c["identical_output_ids"] for c in comparisons)}/{len(comparisons)} helper-versus-layer paired greedy outputs match all4096 IDs; firstdivergences and output hashes are in analysis/output-parity.json. FPorder/adaptation differences may change trajectories and MTP, so TGdiff is not claimed purelyarchitectural. No LLMjudge or quant-qualityranking.\n\n'
for s in summary['limitations']:text+='- '+s+'\n'
text+='\nExploratoryselection and all failures remain separate inexploratory; selectedsplit'+str(summary['layer_selection']['K'])+'/PCIe'+summary['layer_selection']['pcie_frac']+'. Only four bounded layer points, no dense tuning. No local helperpriority patch. New launchers do not alter IQ3_S or old Q4launchers.\n\n## LAUNCH COMMANDS\n\n```bash\n'
for l in launch:text+=l['path']+' --host 0.0.0.0 --port 8080\n'
text+=str(C/'launchers/stop.sh')+'\n```\n\nRun one launcher at a time. It verifiesbinary/source/hash, refuses activeGPUcompute/frontend/port collisions, printsfullresolvedconfiguration, streamslogs, and persistsMonitorAPI.\n\n'+recommendation+'\n'
(C/'report.md').write_text(text);(C/'launchers/README.md').write_text('Selected frozen Q4 currentruntime launchers. See ../report.md and index.json. One server at a time; CtrlC orstop.sh stops only the PIDidentified campaign process. NoIQ3launcher modified.\n')
status(C,'REPORT_READY',running=None,completed=['provenance','bounded layer screening','27valid final requests','pairedID/fairness audit','analysis/report','winner launchers'],pending=['launcher audit','artifact hashes','finalGPU/process cleanup'],current_winners=winners,recommendation=recommendation,next_exact_action='verify launchers and artifact hashes; confirm bothGPUs free')
print(json.dumps({'recommendation':recommendation,'winners':winners,'cells':[{k:r[k] for k in ['method','profile','PP','TG','wall_s','CPU_system_decode_pct']} for r in rows]},indent=2))
