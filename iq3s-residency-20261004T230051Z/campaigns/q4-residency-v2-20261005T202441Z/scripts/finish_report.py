"""Consolidate completed evidence; the reviewed decision is a separate explicit artifact."""
from campaign import C,R,load,save,status
import csv,datetime,json,statistics,shutil,time

def f(value,d=2):return 'unavailable' if value is None else f'{value:.{d}f}' if isinstance(value,(int,float)) else str(value)
def median(cell,key):
    value=cell['stats'].get(key);return value['median'] if value else None

def main():
    live=load(C/'phase-c/summary.json');a=load(C/'phase-a/summary.json');b=load(C/'phase-b/summary.json')
    independent=load(C/'phase-c/independent-summary.json');ablation=load(C/'phase-c/prediction-ablation.json')
    history=load(C/'phase-c/history-transactions.json');decision=load(C/'decision.json')
    historical=load(C/'analysis/historical-control-compatibility.json')
    assert decision['recommendation'] in ['USE_Q4_RESIDENCY_V2','KEEP_Q4_100US_BASELINE','WORKLOAD_DEPENDENT','PROMISING_NEEDS_MORE_WORK','INCONCLUSIVE']
    assert live['state']=='COMPLETE_PRIMARY' and len(live['cells'])==9
    assert load(C/'phase-c/cancellation-test.json')['PASS']
    assert load(C/'phase-c/advertised-launch-smokes.json')['count']==9
    assert load(C/'phase-c/final-audit.json')['PASS']
    live.update(recommendation=decision['recommendation'],decision=decision,phase_a=str(C/'phase-a/report.md'),phase_b=str(C/'phase-b/report.md'),independent=independent,
        prediction_ablation=ablation,history_transactions=history,model=load(C/'git/model.json'),baseline=load(C/'git/frozen-identity.json'),
        deadline=load(C/'deadline.json'),historical_control_compatibility=historical,completed_epoch=time.time())
    file_counters = [{'variant':r['variant'],'profile':r['profile'],'replicate':r['replicate'],
                      'file_blobs':r.get('logical_file_blobs_decode'),'reported_decimal_MB':r.get('logical_file_MB_reported_decode')}
                     for r in live['runs'] if r['variant'] in ['control','history-v2','early-v1']]
    live['expert_file_reads_decode'] = file_counters
    assert len(file_counters) == 27
    assert all(row['file_blobs'] == 0 and row['reported_decimal_MB'] == 0.0 for row in file_counters)
    save(C/'summary.json',live);shutil.copy2(C/'phase-c/summary.csv',C/'summary.csv')
    rows=['# Phase C — live Q4 residency validation','',decision['recommendation']+' — '+decision['reason'],'',
        'The primary27-point matrix is complete; two separate4096-output OFF guards, nine independent1024-output held-out application requests and diagnostic prediction/history cases are preserved separately. No fourth primary repetition or performance-based retry. Three attempts are not a statistical significance test.','',
        'A fixed 4096-token output ending with finish_reason=length means the budget was exhausted. It is not proof that the application produced a complete usable answer. The raw application_status, text, IDs and finish reasons remain preserved; no automatic quality ranking is inferred from throughput.', '',
        '|Total limit|Variant|Valid/attempts|Actual input median|PP|TG min/median/max|TTFT s|Wall s|Decode VM CPU %|All-demand local %|CPU/mapped entries|Reported promotion GB|Victim damage|Predictor/selection cost|',
        '|---:|---|---:|---:|---:|---|---:|---:|---:|---:|---|---|---|---|']
    for cell in live['cells']:
        tg=cell['stats']['TG'];variant=cell['variant']
        promotion=median(cell,'Q4_HISTORY_bytes') if variant=='history-v2' else median(cell,'Q4_EARLY_bytes') if variant=='early-v1' else None
        promotion_text=f(promotion/1e9) if promotion is not None else 'unavailable clean'
        if variant=='early-v1':promotion_text='+'+promotion_text+' predictive; native unavailable'
        cost=median(cell,'Q4_HISTORY_selector_ms') if variant=='history-v2' else median(cell,'Q4_EARLY_scoring_ms') if variant=='early-v1' else None
        cost_text=f(cost)+'ms/request' if cost is not None else 'native; unavailable clean'
        rows.append('|'+ '|'.join([str(cell['context']),variant,f"{cell['valid']}/{cell['attempts']}",f(median(cell,'actual_input_tokens'),0),f(median(cell,'PP'),1),
            '/'.join(f(tg[k],1) for k in ['min','median','max']) if tg else 'unavailable',f(median(cell,'TTFT_s')),f(median(cell,'wall_s')),
            f(median(cell,'CPU_VM_pct'),1),f(median(cell,'local_vram_share_all_pct')),f(median(cell,'cpu_fallback_entries'),0)+'/'+f(median(cell,'nonlocal_gpu_entries'),0),
            promotion_text,'diagnostic only',cost_text])+'|')
    rows+=['','History bytes include native history-selector exchanges; early bytes are additional staged copies and exclude native adaptive traffic plus6.144MB request-end reserve restoration. Clean speed has no per-admission victim counter. Unknown values remain unavailable, not zero. Raw paths, ranges, capacity checks, MTP and system phases are in summary.json/CSV.','',
        '## Paired request ratios','',
        '|Variant|Total limit|Pairs|TG ratio min/median/max|Wall ratio min/median/max|Identical output pairs|','|---|---:|---:|---|---|---:|']
    for item in live['paired_ratios']:
        def value(key):
            s=item['ratios'][key];return '/'.join(f(s[k],4) for k in ['min','median','max']) if s else 'unavailable'
        rows.append(f"|{item['variant']}|{item['profile']}|{item['n']}|{value('TG')}|{value('wall_s')}|{item['same_output_pairs']}|")
    rows += ['', '## Coarse decode progression', '',
        '|Variant|Total limit|0–512 tok/s|512–1024|1024–2048|2048–4096|',
        '|---|---:|---:|---:|---:|---:|']
    for cell in live['cells']:
        selected = [run for run in live['runs'] if run['variant'] == cell['variant'] and run['profile'] == cell['profile']]
        interval_values = []
        for lower, upper in [(0,512),(512,1024),(1024,2048),(2048,4096)]:
            values = [entry['TG_estimate'] for run in selected for entry in run['progression']['intervals']
                      if entry['start'] == lower and entry['end'] == upper and entry['TG_estimate'] is not None]
            interval_values.append(statistics.median(values) if values else None)
        rows.append('|' + '|'.join([cell['variant'], str(cell['context']), *[f(value,1) for value in interval_values]]) + '|')
    rows += ['', 'These are medians of per-run interpolated actual-ID counter intervals at about 1 Hz. The first boundary uses TTFT and the final boundary includes request cleanup. They are diagnostic progression estimates, not exact native-window timings or separate headline repetitions.', '',
        '## System telemetry', '',
        '|Variant|Total limit|Decode CPU %|GPU0 decode %|GPU1 decode %|GPU0 decode W|GPU1 decode W|RSS GiB|',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for cell in live['cells']:
        keys = ['CPU_VM_pct','GPU0_decode_util_pct','GPU1_decode_util_pct','GPU0_decode_power_w','GPU1_decode_power_w','RSS_sum_GiB']
        rows.append('|' + '|'.join([cell['variant'], str(cell['context']), *[f(median(cell,key),1) for key in keys]]) + '|')
    rows += ['', 'All 27 primary requests report zero logical expert-file blobs and 0.0 decimal MB during decode. These are request deltas taken after prefill; the native MB field is rounded to one decimal place. An exact file-byte counter is unavailable. These counters describe logical expert-file reads, not aggregate OS I/O. Direct full-arena CPU/mapped accesses are not all counted by the CS-T RAM-blob counter: zero RAM blobs does not mean zero RAM expert work. See summary.json/expert_file_reads_decode.', '']
    rows+=['','Ratios pair the same preserved input IDs.256K controlrep1 was completed earlier in Phase A; it is compatible but not temporally counterbalanced. The other two256K pairs are fresh/interleaved. Output/MTP can diverge after placement changes, so these are application-level free-generation ratios, not pure fixed-trajectory cache speedups.3% is a practical materiality aid, not a statistical test.','',
        '## Independent held-out application','',
        'hold-code is a complete independent inventory/SQL task excluded from development/calibration,72 actual input IDs,1024-output common budget,32K total limit. It is not a second128K document benchmark.','',
        '|Variant|Completed1024 / attempts|PP|TG min/median/max|Wall median s|VM CPU %|','|---|---:|---:|---|---:|---:|']
    for cell in independent['cells']:
        tg=cell['stats']['TG'];rows.append(f"|{cell['variant']}|{cell['fixed1024_valid']}/{cell['attempts']}|{f(median(cell,'PP'),1)}|{'/'.join(f(tg[k],1) for k in ['min','median','max'])}|{f(median(cell,'wall_s'))}|{f(median(cell,'CPU_VM_pct'),1)}|")
    rows+=['','## Transaction outcomes and matched scheduler ablation','',
        '|Diagnostic|Issued|Published|Copy GB|Unpublished GB|Local entries after admission|Victim-absent entries*|','|---|---:|---:|---:|---:|---:|---:|']
    for item in ablation:
        rows.append(f"|{item['variant']}|{item['issued']}|{item['published']}|{item['issued_GB']:.2f}|{item['unpublished_GB']:.2f}|{item['observed_local_entries_after_admission']}|{item['victim_absent_entries_descriptive']}|")
    hs=history['summary']
    rows+=['',f"History diagnostic: {hs['promotions']} promotions, {hs['bytes']/1e9:.2f}GB; {hs['useful_promotions']} observed used and {hs['unused_promotions']} not observed used before trace end; {hs['repeated_use_windows']} used across multiple windows; {hs['victim_entries_while_absent']} victim-absent entries. Exact demand/class/slot evolution validates against the buffered trace; clean/diagnostic parity is recorded rather than presumed.",
        '', '*Victim absence is descriptive, not an exclusive causal latency counter. Near-end unused copies are right-censored. Early event tracking can miss native eviction/readmission between observations and excludes demand damage from the two initial spare withdrawals; that damage is unavailable separately and remains included in whole-request routing/latency. Reactive copies issue after their original miss; later ready publication is not prefetch of that earlier demand. Prediction-enabled readiness proves copy completion before target-plan release, not an exact GPU deadline timestamp. Equal warmup budgets/capacities do not imply identical warmed resident sets after ON divergence. The pilot covers five of48 layers, only3.072MB class. Details and clock/readiness distributions are in prediction-ablation.json/history-transactions.json.','',
        '## Correctness, footprint and progression','',
        'Both existing68-case suites have62PASS,2SKIP and the same four known fixture/environment failures as the original: ple_parity,platform_memory_test,expert_parity,pool_test. Relevant native Q4_K/Q5_1,Q4_K/Q8_0,Q5_K/Q8_0,router/cache/pool_stress tests pass. This is not an entirely green suite. Thirty seeded selector C++/Python states pass. The ordering proof runs200cycles/device with an active graph waiting on a separate host planner, concurrent main-thread stream synchronization, independent pinned copies/metadata and byte readback.','',
        'Failure details are retained in JUnit: ple_parity requires an unavailable legacy Q2_0 GGUF fixture; expert_parity and pool_test require unavailable pack/full/experts.bin fixtures; platform_memory_test cannot mlock its resident allocation under the existing memlock limit. No fixture model download or global limit change was made.', '',
        'Each candidate in OFF mode matches original input/output IDs, MTP and routing on four short prompts and its separate 4096-output guard. ON first divergences are preserved; no logits/KL/top-1 harness or universal bitwise/quality claim. Exact sampled promoted backing bytes pass, including forced-wrong predictions. Predictions delayed by 5000 us remain safely late and unpublished. Intentional client cancellation drains and a subsequent fixed 64-output request succeeds.','',
        'Physical slot classes and per-GPU ownership stay fixed. Early worker resources are created before auto sizing, existing verifier scratch/gates are reused, and one existing3.072MB spare/device is charged during decode. No virtual48GiB pool or remote execution. Current-demand victims are protected; publication follows completion. Reserve setup affects TTFT and restoration affects request wall outside the native decode timer.','',
        'Progression is derived from1Hz actual generated-ID counters, never SSE-message count. Interpolated0–512/512–1K/1K–2K/2K–4K rates have sampled timing uncertainty and a request-wall endpoint including cleanup. Exact interval hit/MTP counters are unavailable. Aggregate PCIe samples cannot attribute individual expert transfers or prove saturation. See analysis/live-run-details.json.','',
        '## Repaired and negative results','',
        'Patch-application failures and analysis/parser preflights remain preserved. Healthy zero-non-finite summaries were initially misclassified by a substring checker; analysis was repaired without replaying any request or changing runtime. Reproducer preflight also found a one-server loop inconsistent with the primary protocol; it was corrected to a fresh server and fixed warmup for each of three attempts before any reproduction was run. No headline request was repeated for either repair. A negative run or outlier is never excluded for low TG. Learned linear/MLP/temporal finite-capacity under-admission and the narrow five-layer projection are evaluated as implemented, not proof that all learned residency policies fail.','',
        '## Decision','',decision['reason'],'',decision['recommendation']]
    (C/'phase-c/report.md').write_text('\n'.join(rows)+'\n')
    root=['# Q4 Residency v2 — admission, eviction and causal prefetch','',decision['recommendation']+' — '+decision['reason'],'',
        '## Verified baseline and protocol','',
        'Qwen3.8-Flash-Next UD-Q4_K_XL, revision38bb39ee97821de2c9009abb7e93950eec396e66. Frozen Strata0.1.39 source6f32ec070f23ced9f50e704d854d775da52591ab; original binaryeca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d. K24,PCIe0.28,workers15,pool100us,spec4/min-p0.5,INT8,kv-resident32768 where valid,prefillauto,lookup/reuse0,greedy/serial.2×409024GiB,PHB/noNVLink/noP2P,16vCPU7950X3D,~161GiB/no swap. Model/pack/profile/PLE/MTP provenance and actual native commands/environments are retained under git/,configs/ and every raw attempt. Shared existing expert-profile is verified baseline input, not claimed Q4-exclusive training.','',
        'Fresh server per attempt, identical4096-input/64-output warmup, three rotated paired attempts per profile with4096 output.32/128 inputs preserve prior pool-study families;256 input leaves output/reserve rather than using259K input. Exact actual input IDs/hashes are checked with the real service tokenizer. Sources/builds are isolated; normal user launchers and weights remain untouched.','',
        'The older multi-GPU campaign used one server with sequential measured requests. The immediately preceding pool-spin study instead used the same fresh-process and fixed 4096-input/64-output warmup protocol as this campaign. Its six 100 us controls have exactly matching input/output IDs, MTP/window/routing counters, startup capacities, binary, model, launch arguments and relevant environment. Therefore the timing difference below cannot be assigned to a warmup-protocol difference. Its cause remains unassigned; identical visible counters do not identify an exclusive environmental cause. No historical median is used as a controlled residency speed comparison. The 256K 100 us setting is carried forward, not independently established as a spin optimum.','',
        '|Total limit|Previous pool study PP|Current control PP|Previous TG|Current TG|Previous wall s|Current wall s|',
        '|---:|---:|---:|---:|---:|---:|---:|',
        *[f"|{32768 if item['profile']=='32k' else 131072}|{f(item['prior_medians']['PP'],1)}|{f(item['current_medians']['PP'],1)}|{f(item['prior_medians']['TG'],1)}|{f(item['current_medians']['TG'],1)}|{f(item['prior_medians']['wall_s'])}|{f(item['current_medians']['wall_s'])}|" for item in historical['summaries']],
        '', 'This is historical sensitivity, not a controlled residency A/B. Contemporaneous controls were interleaved with the live candidates; no pool sweep was repeated. The compatible Phase A 256K control was retained, so no fourth primary control attempt was added. Full six-pair comparison: [historical-control-compatibility.json](analysis/historical-control-compatibility.json).','',
        '## Phase A — measured headroom','',
        'All nine Q4 traces reconcile every routed entry and exact current-selector slot evolution. All-demand includes rejected MTP branches,CPU,mapped and local work. Routed RAM arena77,017,907,200bytes/71.73GiB;24576 experts with native3.072/3.584/3.9936MB classes. Original resident allocation is roughly11.4K experts, not a universal configured constant. Decode logical expert-file reads are separately recorded, not inferred from aggregate disk counters.','',
        '|Profile|Actual input|All-demand local %|CPU entries|Mapped entries|Diagnostic promotion GB|Victim-absent entries*|','|---|---:|---:|---:|---:|---:|---:|']
    for row in a['rows']:root.append(f"|{row['context']}|{row['actual_input']}|{row['local_pct']:.2f}|{row['CPU_entries']}|{row['mapped_entries']}|{row['promotion_GB']:.2f}|{row['victim_entries']}|")
    root+=['','*Descriptive observed absence, not an exclusive latency oracle. Capacity-only clairvoyance can eliminate misses with relaxed timing and hundreds ofGB of replacements; transfer-aware next-use is a feasible modeled heuristic, not an optimum/bound. Newly measured existing pinned-batch copies support~13.2GB/s/device. Original modeled joins3.055/3.641/3.409s are~6–7% below observed3.269/3.863/3.615s. Earlier separate staging must charge CPU memcpy/queues/publication; its rate is not free. Selected exposed CPU-positive waits and mapped execution are measured without summing overlapping timers or multiplying three layers by48. Full sensitivity/reuse/cost tables: [Phase A](phase-a/report.md).','',
        '## Phase B — complete family ledger','',
        '|Family|Status|Disposition|','|---|---|---|']
    for name,family in b['families'].items():
        reason=family.get('reason') or family.get('note') or family.get('disposition') or 'Retained per-episode results; see Phase B for measured tradeoff and limits.'
        root.append('|'+ '|'.join([name,family['status'],reason])+'|')
    root+=['','The local Expert-Jev-inspired linear,32-unit MLP and bounded16-window temporal extension were trained CPU-only on complete dev-code/dev-math episodes, calibrated on cal-prose and evaluated on untouched hold-code/hold-math/hold-structured. Normalization/calibration never fit holdout. Targets are nonexclusive future counts with censored trace ends; joint finite-byte incoming/victim utility uses explicitly approximate costs, not a fabricated request-time oracle. Checkpoints,seeds,learning curves and inference/selection costs are retained. Cost-free held-out coverage does not predict finite-admission latency.','',
        'Learned policies reduced traffic by under-admitting and increased nonlocal work. Cheap history reduced long-trace copies with some extra misses; native H1 was often too late,H8 less accurate, andH4 had enough lead but a high conditional wrong-copy rate. The chosen live early pilot combines native H4 with CPU-only linear ranking/guarded victims, not a fully calibrated optimal transaction solver.','',
        'Basal semantic prior is NOT_ATTEMPTED: six short traces do not justify a semantic-to-Q4-expert map or large checkpoint download; its CPU EagerBackend shared path still flattens full forwards. No Polish/translation or published Jev-checkpoint benefit claimed. Primary sources pinned via gh/local material with licenses under sources/: Open-Jev,Fate,SpecMD/Least-Stale,Basal. Full decisions: [Phase B](phase-b/report.md).','',
        '## Phase C — controlled live results','',*rows[6:],'',
        '## Runnable handoff','',
        'The unchanged control and both safe experimental finalists have separate verified foreground launchers. All nine advertised32/128/256 paths actually reachedhealth/current native identity and generated the same64-output smoke; one wildcard-host override is exercised. They refuse hash/model/port/GPU conflicts and never rebuild/update.','',
        '```bash',f"cd {C}/launchers/{decision['launcher_variant']}",'./start-32k.sh','./start-128k.sh --host 0.0.0.0 --port 8080','./start-256k.sh','./stop.sh','./reproduce.sh --profile 128k --port 18140','```','',
        'Exact per-profile source/binary/env/config is in launchers/<variant>/*.json; logs and UI snapshots are under manual/. Reproduction starts three fresh servers, each with the same fixed warmup, and cannot add active-campaign repetitions. Experimental ON variants may diverge and are not universal production recommendations.','',
        '## Limits and next research','',decision['strongest_next_experiment'],'',
        'Completed negatives remain in the ledger; optional untested semantic/longer-learning/alternate allocator directions are not disproven. No helper/pool retuning,weight change,driver/global change,push or PR. No experiment added to fill remaining time.','',
        f"Start {load(C/'deadline.json')['started_utc'] if 'started_utc' in load(C/'deadline.json') else load(C/'deadline.json').get('start_utc')}; total elapsed {(time.time()-load(C/'deadline.json')['start_epoch'])/3600:.2f}h; hard deadline unchanged. Final audit confirms no owned serving/training/profiling GPU process remains. Raw/invalid/failure evidence and previous data are preserved.",'',decision['recommendation']]
    inventory = ['## Frozen identities and memory envelope', '',
        '|Variant|Source SHA|Binary SHA256|', '|---|---|---|']
    for variant in ['control','history-v2','early-v1']:
        cfg = load(C/'launchers'/variant/'128k.json')
        inventory.append(f"|{variant}|`{cfg['source_sha']}`|`{cfg['binary_sha256']}`|")
    exported = load(C/'phase-b/learned/export.json')
    inventory += ['', f"The CPU-only linear checkpoint is `checkpoints/linear.npz`, SHA256 `{exported['checkpoint_sha256']}`. Exported coefficient-header SHA256: `{exported['header_sha256']}`. Exact commands, environment, compiler/CUDA flags, source patches and dependency locks remain under configs/, git/ and sources/.", '',
        '|Profile|GPU0 physical slots|GPU0 cache GiB|GPU1 physical slots|GPU1 cache GiB|',
        '|---|---:|---:|---:|---:|']
    for row in a['rows']:
        first, second = row['capacities']
        inventory.append(f"|{row['context']}|{first['slots']}|{first['bytes']/1024**3:.3f}|{second['slots']}|{second['bytes']/1024**3:.3f}|")
    inventory += ['', 'These exact baseline slot classes come from the validated traces. Clean startup capacities are checked per attempt. History preserves active capacity; early reserves one existing 3,072,000-byte slot on each owner GPU during decode, so active resident capacity is two experts lower. CUDA worker resources are initialized before auto sizing. Total-context limits include input plus output; they are not actual input counts.', '',
        'Model pack: `/srv/ai/models/strata/packs/ud-q4_k_xl-v0132`; local UD-Q4_K_XL shards under `/srv/ai/models/strata/models/UD-Q4_K_XL/`. The pack-directory suffix does not select the runtime. Existing PLE, MTP and shared profile dependencies are explicit in each launcher config and `git/model.json`. The main model remains native GGUF; no new main-model experts.bin.', '']
    handoff = root.index('## Runnable handoff')
    root[handoff:handoff] = inventory
    (C/'report.md').write_text('\n'.join(root)+'\n')
    save(C/'phase-c/decision.json',decision)
    status('COMPLETE_'+decision['status'],phase='C',running=None,phases={'A':'COMPLETE_MIXED','B':'COMPLETE_MIXED','C':'COMPLETE_'+decision['status']},
        completed=['Frozen provenance and9 exact traces','Measured costs/queue validation/headroom','All required causal families includinglinear/MLP/temporal','27 primary attempts plusOFF/heldout/diagnostic/cancel','All9 advertised launcher paths smoked','Reports/reproducibility audit/ownedGPU cleanup'],pending=[],next_exact_action='Stop research; review report before authorizing next experiment',recommendation=decision['recommendation'])
    record={'id':'E032-q4-live-residency','status':'COMPLETE_'+decision['status'],'report':str(C/'report.md'),'campaign':str(C),'recommendation':decision['recommendation'],'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    for ledger in [C/'ledger.jsonl',R/'experiments.jsonl']:
        with ledger.open('a') as file:file.write(json.dumps(record)+'\n')
    print('REPORT_COMPLETE',decision['recommendation'],flush=True)

if __name__=='__main__':main()
