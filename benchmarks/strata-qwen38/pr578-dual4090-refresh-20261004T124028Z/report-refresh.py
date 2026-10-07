#!/usr/bin/env python3
"""Render only the refreshed campaign's measured data; historical data is explicitly separated."""
import json,pathlib,statistics,sys
R=pathlib.Path(__file__).resolve().parent
S=json.loads((R/'summary.json').read_text());C=S['cells'];runs=S['runs']
def load(n,default=None):
 p=R/n;return json.loads(p.read_text()) if p.exists() else default
def cell(name,ctx=31400):return next((x for x in C if x['config']==name and x['actual_prompt']==ctx),None)
def fmt(v,d=2):return 'UNAVAILABLE' if v is None else str(v) if isinstance(v,str) else f'{v:.{d}f}'
def metric(x,k):return fmt(x.get(k)) if x else 'UNAVAILABLE'
def delta(a,b,k='tg_tps'):return fmt(100*(b[k]/a[k]-1))+'%' if a and b and a.get(k) and b.get(k) is not None else 'UNAVAILABLE'
matrix_policy=load('matrix-retry-policy.json',{});matrix_labels=matrix_policy.get('final_labels',{});matrix_contexts=[31400,63402,127002,259507] if matrix_labels else [31400,63400,127000,259500]
def final_name(src,ctx=31400):return matrix_policy.get('cell_overrides',{}).get(src,{}).get(str(ctx),matrix_labels.get(src,src+'-FINAL'))
def is_final(name):return name in set(matrix_labels.values())|{v for z in matrix_policy.get('cell_overrides',{}).values() for v in z.values()} if matrix_labels else name.endswith('-FINAL')
sel=load('selection.json',{});ls=sel.get('best_layer_split',{});opt=sel.get('best_optimized_helper',{});old=cell('H-OLD')
head=load('git/main.json',{}).get('sha');integration=load('git/integration.json',{});correct=load('correctness/summary.json',[])
L=['# IQ3_S / PR #578 controlled dual RTX 4090 campaign','',f'Frozen upstream main: `{head}`. Runtime release: v0.1.39. Model revision: `ed59f92082b1e93c0e96d60a8b11aab089b52f09`.','',
'PR #578 was integrated upstream manually at `4d20d25925374a9a3da7bb0e37e2aa4868d7e7bd`, although GitHub closes it without a merge marker. Both fresh checkouts use the same main; optimized expert-helper is selected by `--remote-expert-opt`. No second merge and no conflict resolution were necessary. Existing #646/#650 verifier changes are preserved.','',
'Default-off boundary diagnostics exist on separate local commits, but headline runs use preserved UNMODIFIED upstream binaries. The predeclared3-fresh-server diagnostic ON/OFF study observed3.43% lower median ON, so debug instrumentation is excluded from final speed results. This difference is observational and does not prove causal overhead; all failed gates and raw data remain. Full cache progression dumps are separate diagnostic runs.','',
'Primary/final speed results require three valid requests after equal warmup within each phase (primary64 output tokens; secondary lookup retry32 output tokens), MTP4/min-p0.5, INT8 KV, kv-resident32768, 15 pool workers, max context262144, greedy sampling, zero prefix reuse and suffix lookup OFF. Each 256-token replay retains the saved literal payload. Historical32K IDs and effective current-API higher-context IDs are checked against their saved hashes before submission; see the tokenizer-correction section. Invalid requests remain in raw and are omitted from valid medians.','',
'## Primary 32K results','',
'| Config | PP median | TG median | TG min/max | TTFT | MTP accepted/window | suffix accepted | CPU fallback entries | helper entries | cache overlap | CPU % | GPU0 % | GPU1 % | PCIe GPU0 RX / GPU1 RX MB/s |',
'|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for name in ['LS-A','LS-B','PR-LS','H-OLD','H-OPT','H-OPT-FIXED']:
 x=cell(name)
 if not x:L.append(f'| {name} | UNAVAILABLE | | | | | | | | | | | | |');continue
 if x['valid_runs']!=3:
  L.append(f"| {name} INCOMPLETE ({x['valid_runs']}/3 valid) | UNAVAILABLE | UNAVAILABLE | partial valid TG {metric(x,'tg_tps_min')}/{metric(x,'tg_tps_max')} | UNAVAILABLE | | | | | | | | | |");continue
 complete='' if x['valid_runs']==3 else f" INVALID/INCOMPLETE: {x['valid_runs']} valid"
 L.append('| '+name+complete+' | '+' | '.join([metric(x,'pp_tps'),metric(x,'tg_tps'),metric(x,'tg_tps_min')+'/'+metric(x,'tg_tps_max'),metric(x,'ttft_s'),metric(x,'mean_accepted_length'),metric(x,'suffix_accepted'),metric(x,'cpu_fallback_entries'),metric(x,'helper_entries'),metric(x,'cache_overlap'),metric(x,'decode_cpu_system_pct'),metric(x,'gpu0_decode_util_pct'),metric(x,'gpu1_decode_util_pct'),metric(x,'gpu0_decode_pcie_rx_MBps')+'/'+metric(x,'gpu1_decode_pcie_rx_MBps')])+' |')
L+=['','CPU fallback entries come from exact native decode cache lookups-minus-hits, verified against existing multi_entries counters in36 diagnostic requests and the source. This requires no debug instrumentation. Rounded distinct-miss and per-window estimates are retained separately in JSON. SplitDrive shares these counters across all stage GPUs; helper dispatch counts remain separately reported. Helper entries are exact reported dispatch counts where available. Hardware dmon PCIe is sparse at1Hz for short decode; returned bytes from helper logs are a separate logical transport measure. CPU system % spans all16 vCPU; process CPU % uses100% per core. UNAVAILABLE is never replaced by zero.','',
'## Initial-cache fairness and progression','',
'| Config | Primary physical capacity | Helper capacity | Initial GPU resident count | Initial overlap | Primary CLI budget | Frozen helper PCIe fraction |','|---|---:|---:|---:|---:|---:|---:|']
for name in ['H-OLD','H-OPT','H-OPT-FIXED']:
 d=load(f'raw/{name}-layout.json',{});c=load(f'configs/{name}.json',{});args=c.get('args',[]);pcie=args[args.index('--pcie-frac')+1] if '--pcie-frac' in args else None
 L.append('| '+name+' | '+' | '.join(fmt(d.get(k),0) for k in ['primary','helper','initial_resident_expert_count','initial_overlap','primary_cli_uniform_budget'])+' | '+fmt(pcie)+' |')
L+=['','Layer-split allocation is unchanged in LS-A, LS-B, PR-LS and the final layer-split matrix: K25, GPU0 layers0-24 with10112 expert slots, GPU1 layers25-47 with8377 slots (18489 total). Auto predicted capacity is not substituted for actual startup allocation. Helper topology has8586+11796=20382 GPU-resident experts at startup. Both use the preloaded46.84GiB full expert arena in RAM.','']
L+=['','| Diagnostic config | Startup overlap | After warmup overlap | After run1 / run2 / run3 overlap |','|---|---:|---:|---:|']
for name in ['H-OLD-DIAG','H-OPT-FIXED-DIAG']:
 d=load(f'raw/{name}-layout.json',{});a=load(f'raw/{name}-32K-warmup.json',{});sn=a.get('cache_snapshots',[]);progress=[]
 for i in [1,2,3]:
  q=load(f'raw/{name}-32K-run{i}.json',{}).get('cache_snapshots',[]);progress.append(fmt(q[-1]['overlap'],0) if q else 'UNAVAILABLE')
 L.append(f"| {name} | {fmt(d.get('initial_overlap'),0)} | {fmt(sn[-1]['overlap'],0) if sn else 'UNAVAILABLE'} | {' / '.join(progress)} |")
L+=['','Net ID-set changes are saved in cache-progression.json. Original helper keeps its initial helper set fixed while primary adaptation creates overlap; optimized helper replaced204/55/86 helper IDs across measured runs and held primary ID set unchanged in these diagnostics. These are boundary net replacements, not complete swap counts. Original after-warmup overlap571(4.84%), after-run3 overlap2072(17.57%); optimized zero at every observed boundary.','']
dold=cell('H-OLD-DIAG');dopt=cell('H-OPT-FIXED-DIAG')
L += [f'In separate diagnostics, CPU activation quantization median dropped from {metric(dold,"cpu_activation_quant_ms")} ms to {metric(dopt,"cpu_activation_quant_ms")} ms per256-output request. Exact skipped-token count is unavailable; diagnostic timings are not headline speed.','']
L+=['','Clean speed capacities are logged before warmup and checked for equality. Initial resident count/zero overlap follows the deterministic cache constructor with the identical complete profile/model/capacities, independently observed in paired startup diagnostics. Clean speed ID sets are NOT directly dumped; reference hashes belong to separate diagnostics, and initial_layout_basis explicitly distinguishes them. A capacity mismatch stops the candidate before warmup. Full-snapshot diagnostics show progression and are excluded from headline speed.','',
'## Final context matrix','',
'| Config | Actual context | PP median (min/max) | TG median (min/max) | TTFT | CPU fallback entries | helper entries | overlap | CPU % | GPU0 % | GPU1 % |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for x in C:
 if not is_final(x['config']):continue
 L.append('| '+x['config']+' | '+str(x['actual_prompt'])+' | '+metric(x,'pp_tps')+' ('+metric(x,'pp_tps_min')+'/'+metric(x,'pp_tps_max')+') | '+metric(x,'tg_tps')+' ('+metric(x,'tg_tps_min')+'/'+metric(x,'tg_tps_max')+') | '+' | '.join(metric(x,k) for k in ['ttft_s','cpu_fallback_entries','helper_entries','cache_overlap','decode_cpu_system_pct','gpu0_decode_util_pct','gpu1_decode_util_pct'])+' |')
L+=['','## Steady decode and secondary lookup','',
'| Config | Output request | Valid runs | PP | TG median | TG min/max | TTFT | suffix accepted |','|---|---:|---:|---:|---:|---:|---:|---:|']
for x in C:
 if '-STEADY2048' not in x['config'] and '-LOOKUP-ON' not in x['config']:continue
 L.append('| '+x['config']+' | '+('2048' if '-STEADY2048' in x['config'] else '256')+' | '+str(x['valid_runs'])+' | '+' | '.join([metric(x,'pp_tps'),metric(x,'tg_tps'),metric(x,'tg_tps_min')+'/'+metric(x,'tg_tps_max'),metric(x,'ttft_s'),metric(x,'suffix_accepted')])+' |')
L+=['','Lookup ON results are secondary and never combined with lookup OFF medians. An original-helper64-token warmup stopped naturally at51; its raw negative is preserved. All three secondary candidates were restarted with equal32-token warmup (LOOKUP-ON-W32). Therefore primary-to-secondary is not a controlled suffix-only A/B; compare configurations within each phase. Steady2048 uses explicitly disabled prompt cache, the same saved input and three requests per configuration. It is a separate workload, not a historical256-output A/B.','',
'## Correctness and tests','',
'Existing native/Python test results and actual failure classification are retained in environment.json, test-review.json, diagnostic-test-review.json and logs/. Any environmental skips/failures must be read with those records; this report does not claim every test passed when fixtures or memlock prevent execution.', '',
 f'Paired correctness cases recorded: {len(correct)}. Malformed-output flags: {sum(bool(x.get("malformed_output")) for x in correct)}. Input-token mismatches: {sum(not x.get("input_identical",False) for x in correct)}. Full outputs/token IDs, first divergence and finish reasons: correctness/. Floating-point summation changes do not require bitwise parity. Free-generation positional token equality is not teacher-forced top1 agreement; KL/logits metrics are UNAVAILABLE unless a usable logits trace was actually captured.','',
'## Concrete interpretation','',
f'Best complete32K layer split: {ls.get("config","UNAVAILABLE")}, TG {metric(ls,"tg_tps")} tok/s, PP {metric(ls,"pp_tps")}. Best complete optimized helper: {opt.get("config","UNAVAILABLE")}, TG {metric(opt,"tg_tps")}, PP {metric(opt,"pp_tps")}. Original helper TG: {metric(old,"tg_tps")}. Optimized-helper TG change vs best layer split: {delta(ls,opt)}; vs original helper: {delta(old,opt)}. These comparisons use warmup-matched, suffix-OFF data.','',
'Primary/helper complementarity and post-warmup overlap must be assessed using the diagnostic table; startup overlap alone does not prove sustained complementarity. CPU quantization skips and per-run adaptation swap totals are UNAVAILABLE where upstream has no exact counter. Returning one weighted vector/token is confirmed in source and logical returned-byte statistics (footer rounded to0.1MiB), while total PCIe can include other runtime traffic. Higher helper hit count can increase total returned bytes even when reduction lowers bytes for the same helper work.','',
'With only one helper, stripe/layer placement uses the same assignment path: the actual multi-helper placement branch is only active with at least two helpers. It is therefore not a meaningful A/B on this machine. Auto versus fixed capacities are compared using H-OPT and H-OPT-FIXED; primary CLI budget and resulting physical capacity are distinct quantities.','',
'The replay/steady speed workload is code-agent repository material. Short math/prose correctness prompts do not establish stable mixed/math throughput; no cross-workload speed recommendation is inferred from them. The author’s reported dual4090 Mixed/Code rates are different workloads and are not controlled A/B with ours. No exact author benchmark scripts/payloads were available in the PR file list.','',
'Author publication, retained separately from our measurements ([PR578](https://github.com/Niko1221/Strata/pull/578), saved git/pr.json):','',
'| Author dual4090 v0.1.37 topology | Mixed TG | Code TG |','|---|---:|---:|',
'| Original helper | 88.07 | 85.15 |','| Auto layer split | 126.86 | 146.95 |','| Optimized helper | 143.35 | 197.58 |','',
'These are author-reported values for other workloads/configurations, not our raw runs or a controlled comparison against our code-agent prompts. Our matched-capacity original/optimized comparison is reported separately above.','',
'Historical v0.1.31/v0.1.38 replay and the preserved earlier PR578 campaign are HISTORICAL / NOT_CONTROLLED_A_B relative to this same-main experiment. See references/ and the unchanged ../pr578-dual4090/report.md. Their values are never counted as new repetitions.','',
'## API tokenizer correction and preserved retry','',
'The first matrix attempt completed32K, then failed the harness count assertion at64K: direct legacy tokenizer63400 versus API63402. This entire attempt is preserved separately and superseded. The harness now calls frozen upstream Service.encode_prompt, including#537 plain-text escaping of literal thinking tags. Payload text is unchanged; effective counts are31400/63402/127002/259507. Historical32K token IDs are unchanged; larger-context IDs reflect official API escaping and are saved identically for both finalists. The full matrix restarts under FINAL-TOKFIX labels. See tokenizer-review.json, api-tokenization-provenance.json, matrix-retry-policy.json and the negative provenance sidecar. No engine or weights changed.','',
'Background-analysis review: a2.08-second summary-analysis invocation overlapped0.744s of helper32K-run1 decode and0.051s of run2 prefill. All three original helper32K requests are conservatively excluded/superseded; the complete32K cell is remeasured after the full matrix on a fresh server with the exact same context-prefixed warmup. Other context requests remain separate. See background-analysis-exclusions.json.','',
'## Expert storage counter interpretation','',
'The IQ3_S native expert arena is fully preloaded in RAM. ArenaExpertSource::blob is pointer arithmetic into that RAM and performs no file read. However, DONE/API ram_blobs/file_blobs/file_mb belong to the unused mmap/complement source and explicitly remain zero with arena; they are not an independent arena SSD read measurement. Logical expert file-read counts during arena decode are UNAVAILABLE. See expert-io-provenance.json and startup arena logs. Other PLE/model traffic is distinct from routed-expert streaming.','',
'## Negative and excluded records','']
invalid=[x for x in runs if not x.get('valid')];diags=[x for x in runs if 'DIAG' in x.get('candidate','')]
L += [f'Invalid recorded requests in summary: {len(invalid)}. Diagnostic-only requests in summary: {len(diags)}. Full raw request/stream/log/config files remain preserved. A cell with fewer than three valid repetitions is explicitly incomplete, and no three-run headline median is presented.','',
'']
ls_steady=cell(ls.get('config','')+'-STEADY2048');opt_steady=cell(opt.get('config','')+'-STEADY2048')
ls_final=[cell(final_name(ls.get('config',''),ctx),ctx) for ctx in matrix_contexts]
opt_final=[cell(final_name(opt.get('config',''),ctx),ctx) for ctx in matrix_contexts]
complete=all(x and x.get('valid_runs')==3 for x in [ls_steady,opt_steady]+ls_final+opt_final)
if not complete:
 recommendation='NEED_MORE_DATA';reason='The steady/context battery is incomplete; available screening data alone does not justify a production change.'
elif all(a['tg_tps']>b['tg_tps']*1.05 for a,b in zip([ls_steady]+ls_final,[opt_steady]+opt_final)):
 recommendation='KEEP_LAYER_SPLIT';reason='Layer split wins both steady2048 decode and all four actual-context cells by more than5%, with higher PP and lower TTFT. Optimized helper improved the primary short32K batch over original helper, but regressed on steady2048 decode; it does not replace layer split for these measured workloads.'
elif all(b['tg_tps']>a['tg_tps']*1.05 for a,b in zip([ls_steady]+ls_final,[opt_steady]+opt_final)):
 recommendation='USE_PR578_HELPER';reason='Optimized helper reproducibly wins steady2048 and the complete actual-context matrix; evaluate its PP/TTFT tradeoff for the target workload.'
else:
 recommendation='NEED_MORE_DATA';reason='Steady/context results give a mixed or near-tied result; the preferred topology depends on workload and latency requirements.'

L+=['## Answers to the requested questions','',
'1. Integration: already integrated on the frozen current main. Both binaries use the same source base; original/optimized helper is an OFF/ON flag A/B.',
'2. Conflicts: none; no second merge was applied. Local default-off diagnostic patch is recorded separately and excluded from final speed.',
'3. Tests: native72 each:66 passed,2 skipped,4 environmental failures (missing Q2_0 fixtures and memlock permission). Python268 each:OK,7 skipped after adding the same optional jsonschema dependency. This is not an all-tests-pass claim.',
'4. Stability: inspect the preserved negative records below. Selected finalists require3 valid requests/cell; no OOM/crash may be hidden.',
'5. Correctness:10 identical-input pairs,4 exact outputs and6 free-generation divergences; no nonfinite/garbled output. Both JSON cases valid. Two budget-limited code cases were extended to natural stop; binary-search examples and edge tests passed. No LLM judge or numerical logits-parity claim.',
f'6. Primary32K median decode: layer split {metric(ls,"tg_tps")}, original helper {metric(old,"tg_tps")}, optimized helper {metric(opt,"tg_tps")} tok/s.',
f'7. Optimized helper vs layer split: {delta(ls,opt)} TG; vs original helper {delta(old,opt)}. Same initial helper capacities and identical MTP/warmup within the primary phase.',
'8. Context progression: the final matrix and PP/TG ranges are printed above; each row is keyed by actual token count, not configured maximum.',
f'9. Primary32K CPU fallback entries: original {metric(old,"cpu_fallback_entries")}, optimized {metric(opt,"cpu_fallback_entries")}; change {delta(old,opt,"cpu_fallback_entries")}. These are routed entries, not distinct experts.',
'10. Complementarity: verified directly in separate diagnostic ID snapshots; headline runs do not enumerate ID sets.',
'11. Startup/after-warmup/after-run3 overlap: see exact diagnostic table. Percent denominator is helper resident count11796, not the combined cache.',
f'12. Returned logical bytes32K: original {metric(old,"helper_returned_bytes")}, optimized {metric(opt,"helper_returned_bytes")}; change {delta(old,opt,"helper_returned_bytes")}. Do not call this a total PCIe reduction: optimized helper handles more entries. The printed full-rows hypothetical includes all routed entries, including entries not computed by the helper. Hardware dmon RX/TX is separate and sparse.',
f'13. CPU32K mean whole-VM utilization: split {metric(ls,"decode_cpu_system_pct")}%, original {metric(old,"decode_cpu_system_pct")}%, optimized {metric(opt,"decode_cpu_system_pct")}%. Peak values and process utilization appear in the system table. Process100% is one vCPU, not the entire16-vCPU VM.',
f'14. GPU32K mean utilization0/1: split {metric(ls,"gpu0_decode_util_pct")}/{metric(ls,"gpu1_decode_util_pct")}%; original {metric(old,"gpu0_decode_util_pct")}/{metric(old,"gpu1_decode_util_pct")}%; optimized {metric(opt,"gpu0_decode_util_pct")}/{metric(opt,"gpu1_decode_util_pct")}%.',
f'15. Best complete32K topology: {ls.get("config") if ls.get("tg_tps",0)>opt.get("tg_tps",0) else opt.get("config")}; production recommendation also requires the steady/context battery.',
'16. Workload dependence: measured speed uses saved code-agent/repository inputs. Short math/prose correctness cases are insufficient to choose a mixed/math throughput winner.',
'17. Stripe/layer: one helper follows the same placement path; a distinct A/B is not meaningful on this two-card system.',
f'18. Auto/fixed optimized helper: auto TG {metric(cell("H-OPT"),"tg_tps")}, fixed {metric(cell("H-OPT-FIXED"),"tg_tps")}; identical physical capacities. This small difference is not evidence that manually resizing the cache wins.',
'19. Candidate future optimization: prioritize helper ownership before assigning primary PCIe-mapped misses, so helper-resident experts are not consumed by the primary mapped path. The current controlled campaign does not implement this algorithm change; a separate preserved-original A/B and correctness check would be required.',
'20. Recommendation: '+recommendation+'. '+reason,'',
'## System and transport metrics','',
'| Config/context | CPU VM mean/peak % | Process mean/peak % | GPU0/1 power W | RSS GiB | RAM used GiB | VRAM0/1 GiB | Helper returned bytes/token | Helper wait ms |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for x in C:
 if x['config'] not in ['LS-B','H-OLD','H-OPT-FIXED'] and not (is_final(x['config']) or x['config'].endswith('-STEADY2048')):continue
 L.append('| '+x['config']+'/'+str(x['actual_prompt'])+' | '+' | '.join([metric(x,'decode_cpu_system_pct')+'/'+metric(x,'decode_cpu_system_pct_peak'),metric(x,'decode_cpu_process_pct')+'/'+metric(x,'decode_cpu_process_pct_peak'),metric(x,'gpu0_decode_power_w')+'/'+metric(x,'gpu1_decode_power_w'),metric(x,'peak_rss_gib'),metric(x,'peak_ram_used_gib'),metric(x,'peak_vram0_gib')+'/'+metric(x,'peak_vram1_gib'),metric(x,'helper_returned_bytes_per_generated_token'),metric(x,'helper_wait_ms')])+' |')
L+=['','Each memory value is the median of per-request sampled peaks; raw records retain individual peaks. RSS is the server/engine process tree, RAM used is VM-wide. Short decode only has a few1Hz samples; steady2048 is more representative. Dmon totals are not a causal bus-traffic decomposition.','', '']
L+=['## Speculative-decode progression','',
'| Config/context | MTP drafted | MTP accepted | Acceptance % | Accepted/window | Verify windows | Mean window ms |','|---|---:|---:|---:|---:|---:|---:|']
for x in C:
 if x['config'] not in ['LS-B','H-OLD','H-OPT-FIXED'] and not (is_final(x['config']) or x['config'].endswith('-STEADY2048')):continue
 L.append('| '+x['config']+'/'+str(x['actual_prompt'])+' | '+' | '.join(metric(x,k) for k in ['draft_tokens','accepted_tokens','acceptance_pct','mean_accepted_length','verify_windows','mean_verify_window_latency_ms'])+' |')
L+=['','Primary32K and final-matrix32K are separate batches and are not pooled. Matrix warmups add a context-specific nonce to the saved warmup; each finalist follows the same context/warmup order. Greedy outputs can diverge after floating-point/cache routing differences, so MTP acceptance and TG can change with the output trajectory even for identical input IDs. These are end-to-end speculative decode results, not a fixed-output kernel-only speed comparison.','']
L+=['## Steady-decode bottleneck evidence','',
'| Config | TG | GPU-reach wait ms/window | CPU work ms/window | PCIe experts/layer-window | GPU0 RX MB/s | GPU1 RX MB/s |','|---|---:|---:|---:|---:|---:|---:|']
for name in [ls.get('config','')+'-STEADY2048','H-OLD-STEADY2048',opt.get('config','')+'-STEADY2048']:
 x=cell(name)
 L.append('| '+name+' | '+' | '.join(metric(x,k) for k in ['tg_tps','GPU_reach_wait_ms_per_window','CPU_work_ms_per_window','pcie_experts_per_layer_window','gpu0_decode_pcie_rx_MBps','gpu1_decode_pcie_rx_MBps'])+' |')
L+=['','Optimized-helper CPU misses fall, but primary GPU reach-wait and mapped-RAM PCIe work grow; GPU1 remains lightly utilized. This supports a primary dispatch/host-memory path limitation rather than expert SSD streaming. It does not prove the PCIe link is continuously saturated or that CPU utilization equals useful GEMV work; worker spinning and GPU coordination can contribute. The existing hardware campaign measured PHB/no P2P, approximately12.6GB/s pinned one-way GPU0 transfer, and approximately26.7GB/s aggregate dualH2D; those are distinct microbenchmarks. Our topology choice is supported by direct inference results, not by treating utilization alone as a bottleneck proof.','']
L+=['## Frozen finalist configurations','',
'Exact server/engine command, environment and binary SHA are stored in configs/LS-B-FINAL-TOKFIX.json and configs/H-OPT-FIXED-FINAL-TOKFIX.json and in every canonical raw record. The layer-split candidate uses auto(K25), explicitpcie-frac0.28, expert-cache auto, prefill auto, MTP4/min-p0.5, suffix-draft0, INT8/kv-resident32768, workers15 and max-context262144. The helper uses primaryCLI6567/result8586 slots, helper11796 slots, pcie-frac0.37 and remote-expert-opt, with the same remaining settings. No resident-budget mode, speed projection, weight conversion or algorithm patch is enabled in headline runs.','']
L += ['## RECOMMENDATION','',recommendation,'',reason,'', 'All numbers in tables come from summary.json, whose raw_paths link canonical request records. Reproduce with analyze.py, then report-refresh.py; inspect independent audit-refresh.json for completion and fairness checks.']
(R/'report.md').write_text('\n'.join(L)+'\n');(R/'recommendation.json').write_text(json.dumps({'recommendation':recommendation,'reason':reason},indent=2)+'\n')
print(R/'report.md')
