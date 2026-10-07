"""Readable final synthesis, generated only from completed raw-derived summaries."""
import datetime, pathlib
from lab import ROOT, load, save
campaign=pathlib.Path(load(ROOT/'active-campaign.json')['path'])
p0=load(ROOT/'experiments/E026-pool-generalization/summary.json')
p1=load(ROOT/'experiments/E027-pool-baseline/summary.json')
p2=load(ROOT/'experiments/E029-persistent-runtime/summary.json')
assert p2['state']=='COMPLETE_BOUNDED_PERSISTENT_RESIDENCY'
end=load(campaign/'end-state.json');assert end['state']=='PASS_IDLE_OWNED_PROCESSES'
recommend=p2['decision'];name='persistent-v2-on' if recommend=='USE_PERSISTENT_RESIDENCY' else 'p1-baseline'
folder=ROOT/'variants'/name;cfg=load(folder/'32k.json')
def median(cell,key):
 value=cell['metrics'][key];return value['median'] if value else None
def cell(cells,profile,role,family=None):
 return next(c for c in cells if c['profile']==profile and c['role']==role and (family is None or c['family']==family))
lines=['# IQ3_S: CPU-pool validation and persistent residency', '',
 f'Completed {datetime.datetime.now(datetime.timezone.utc).isoformat()}. The bounded P0/P1/P2 protocol is complete before the 10-hour upper bound. The prior campaign and all raw data remain preserved. This does not mean every possible residency algorithm was exhausted.', '',
 '## P0: independent workload validation', '',
 '**1. Generalization:** fixed 100 µs helped the three tested workload families: a different repository/storage audit, exact interpolation and numerical reasoning, and an RFC-based operations handbook. There were 36 valid 4096-output requests: three families × two context profiles × two policies × three paired fresh starts. Math at 128K was approximately neutral; the other cells showed useful latency/TG gains.', '',
 '| Family | Context | Default TG | 100 µs TG | Paired median TG Δ | Paired median wall Δ | VM CPU default / 100 µs |',
 '|---|---|---:|---:|---:|---:|---:|']
for delta in p0['paired_deltas']:
 family,profile=delta['family'],delta['profile'];a=cell(p0['cells'],profile,'default',family);b=cell(p0['cells'],profile,'sleep100us',family)
 lines.append(f'| {family} | {profile} | {median(a,"TG"):.1f} | {median(b,"TG"):.1f} | {delta["TG_delta_pct"]["median"]:+.2f}% | {delta["wall_delta_pct"]["median"]:+.2f}% | {median(a,"CPU_VM_mean_pct"):.1f}% / {median(b,"CPU_VM_mean_pct"):.1f}% |')
lines += ['', 'TG columns are independent cell medians. Delta columns are medians of the three paired ratios; these need not equal the ratio of cell medians.', '', '**2. Workload characteristics:** parking idle workers reduces host contention when execution is mostly local. This mechanism is an inference from identical output/routing and lower CPU/staging costs, not isolation of every scheduler effect. The advantage shrinks when CPU-positive work and wakeup latency matter more.', '',
 '**3. Cost under CPU-positive execution:** selected 32K math layers had median completion waits of about 5–6 µs by default versus 61–71 µs at 100 µs parking. Their p95 increased from roughly 98–160 to 293–387 µs. All-local completion floors stayed near 4–5 µs. One preserved math128 pair had TG −3.35% and wall +1.56%; one prose128 pair had wall +0.25%. End-to-end request latency, rather than lower CPU use alone, determined the decision. Extreme all-CPU and concurrent workloads are not certified.', '',
 '**4. Correctness:** all 18 pairs retained identical actual input/output IDs, MTP, normal routing counters and capacities. Wait diagnostics were separate from headline binaries. See [P0 report](experiments/E026-pool-generalization/report.md).', '',
 '## P1: frozen CPU-pool baseline', '',
 '**5–6. Policy:** fixed `STRATA_POOL_SPIN_US=100`. The CURRENT source and executable are unchanged; no adaptive synchronization subsystem was needed and no dense threshold sweep was performed.', '',
 '**7–8. Fresh-start standard-workload confirmation:**', '',
 '| Context | Pool policy | PP median | TG median | TTFT median s | Wall median s | Decode VM CPU |',
 '|---|---|---:|---:|---:|---:|---:|']
for profile in ['32k','128k']:
 for role in ['default','sleep100us']:
  c=cell(p1['cells'],profile,role)
  lines.append(f'| {profile} | {role} | {median(c,"PP"):.1f} | {median(c,"TG"):.1f} | {median(c,"TTFT_s"):.3f} | {median(c,"wall_s"):.3f} | {median(c,"CPU_VM_mean_pct"):.1f}% |')
lines += ['', 'Exactly three valid measured runs per point. The earlier 178.5/154.0 numbers came from a different shared-server protocol and remain historical. The fresh-start confirmation is not forced to match them. Min/median/max and all raw paths are in the CSV/JSON summaries.', '',
 '**9. Stress/correctness:** 8000 targeted batches and 67,200 jobs covered bursts, idle periods, alternating CPU/local work, and repeated pool construction/destruction; outputs were checked. Original pool stress ran 20 seconds per policy, and real IQ native expert parity passed at layers 0/1/2/12. No lost jobs or deadlock was observed. No CPU-pool synchronization primitive changed; the tests are not a proof of all interleavings.', '',
 '**10. Launch readiness:** the actual 128K launcher bound to `0.0.0.0`, became healthy, generated 64 tokens, and stopped cleanly. Exact launch commands appear below. See [P1 report](experiments/E027-pool-baseline/report.md).', '',
 '## P2: persistent same-device expert residency', '',
 '**11. Implementation:** completed in separate worktrees/builds, disabled by default. Admission retains experts across future demand; there is no immediate swap/restore. It keeps the original per-device variable-size physical slots and immutable RAM arena. Copies run asynchronously at the existing safe end-of-verify boundary and publish only after completion events. No experts or weights are substituted.', '',
 '**12. Signals:** the existing native GPU gate/top10 at horizon eight, combined with observed EMA heat, recency, resident age, a byte-aware transfer penalty and a replacement margin. Predictions cover five target layers out of 48. Normalized gate confidence is not calibrated future probability. The final policy uses the predeclared 64-window utility horizon and 64 MiB/device batch budget; only one repair of the initial conservative policy was tested.', '',
 '**13. Replay headroom:** the old future-informed placement reference reached 4/3 nonlocals versus CURRENT 36,776/45,276 at fixed capacity, but it is neither deployable prediction nor free latency savings. The corrected causal warmup replay of our policy produced 73,926/79,719 nonlocals and 3.941/4.809 GB of promotions. Modeled waits were 1.537/1.948 s at 1.8 GB/s and 0.027/0.053 s at 12.6 GB/s. These are sensitivities on a fixed trajectory, not TG forecasts.', '',
 'H8 current-window any-branch membership was 35.2%/42.4%; membership in the next 16 windows was 60.1%/61.8%. These are different metrics from the prior next-layer prediction result. Warmup state, prediction heat, recency, pending reservations and byte constraints were explicitly audited.', '',
 '**14–19. Live confirmation: same modified binary, OFF versus ON, identical inputs/settings/capacities, warmup 64 output, three fresh measured starts per cell, 4096 output:**', '',
 '| Context | Residency | PP median | TG median | TTFT s | Wall s | CPU entries | PCIe entries | Decode VM CPU |',
 '|---|---|---:|---:|---:|---:|---:|---:|---:|']
for c in p2['cells']:
 lines.append(f'| {c["profile"]} | {c["role"]} | {median(c,"PP"):.1f} | {median(c,"TG"):.1f} | {median(c,"TTFT_s"):.3f} | {median(c,"wall_s"):.3f} | {median(c,"cpu_fallback_entries"):.0f} | {median(c,"offloaded_entries"):.0f} | {median(c,"CPU_VM_decode_mean_pct"):.1f}% |')
lines += ['', '| Context | Admissions | Copied GB | Useful | Repeated use | Wasted | Ready for future use | Late for future use | Victim entries |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for profile in ['32k','128k']:
 c=cell(p2['cells'],profile,'on');m=lambda key:median(c,'residency_'+key)
 lines.append(f'| {profile} | {m("promotions"):.0f} | {m("bytes")/1e9:.3f} | {m("useful"):.0f} | {m("repeated"):.0f} | {m("wasted"):.0f} | {m("ready"):.0f} | {m("late"):.0f} | {m("victim_entries"):.0f} |')
lines += ['', 'Each counter column is independently median-reduced across three runs; useful plus wasted medians need not equal the admissions median. Ready/late here refers to the first **subsequent** use after admission. The current-window target already executed before the safe copy boundary; those opportunities are not counted as early hits. Up to three admissions were still pending at the output cutoff in individual clean runs; they were not counted as ready or useful. The next request drains pending copies before prefill/decoding. Detailed prediction, enqueue, completion observation, lifetime, reuse and victim CSVs are preserved in the separate diagnostic experiment. Publication is a checked upper-bound observation of GPU completion; the exact GPU completion timestamp is unavailable.', '']
for x in p2['comparisons']:
 lines.append(f'- {x["profile"]}: TG median ratio {x["TG_delta_medians_pct"]:+.2f}%, wall median ratio {x["wall_delta_medians_pct"]:+.2f}%; paired median TG {x["paired_delta_TG_median_pct"]:+.2f}%, paired wall {x["paired_delta_wall_median_pct"]:+.2f}%.')
lines += ['', '**20. Why replay headroom did not turn into speed:** fewer promotion bytes came with more CPU/mapped expert work. The predictor is limited, the utility is approximate, capacity is fixed, and safe boundary admission cannot catch the first current-window target demand. Placement changes CPU/GPU rounding and the free-generation/MTP trajectory. The same-input comparison does not isolate a fixed-trace kernel speedup.', '',
 'Copy submission/staging, exposed adaptation-thread join, and completion-event waits were measured separately with a diagnostic binary. They overlap and must not be summed into a fabricated TG forecast. Short pending-event waits alone do not establish cheap copies.', '']
for x in p2['copy_diagnostic']['rows']:
 st=x['diagnostic_stats'];life=x['lifetimes'];lines.append(f'- {x["profile"]}: {x["state"]}; enqueue/staging {st.get("enqueue_ms")} ms, exposed join {st.get("join_ms")} ms, pending publication {st.get("pending_ms")} ms. Only {life["admissions_with_recorded_prediction"]}/{st["promotions"]} admissions had a recorded router prediction; most admissions were driven by observed demand. Of these, {life["predicted_useful_but_current_miss_preceded_enqueue"]} already missed after prediction and before enqueue. Median enqueue-to-checked-publication was {life["enqueue_to_publication_us"]["median"]:.0f} µs. Useful admissions had median {life["uses_per_useful_admission"]["median"]:.1f} routed entries of reuse.')
lines += ['', 'The initial conservative policy was rejected after one preserved 32K screen: 142.7 versus 179.7 TG and 18.9% longer request wall time. The repaired policy was frozen before the final matrix. No tuning continued until a favorable result appeared. See [replay report](experiments/E028-persistent-replay/report.md), [live report](experiments/E029-persistent-runtime/report.md), and [source safety](experiments/E029-persistent-runtime/analysis/source-safety.md).', '',
 '## BEST REAL-PROMPT CANDIDATE', '',
 f'**21–22. Variant:** `{name}`. Binary: `{cfg["exe"]}`. SHA256: `{cfg["binary_sha256"]}`. Source: `{cfg["source_sha"]}` in `{cfg["cwd"]}`.', '',
 f'Model revision: `{cfg["model_revision"]}`. Existing IQ3_S GGUF/pack, PLE and MTP remain unchanged. Full frozen configurations: [32K](variants/{name}/32k.json), [128K](variants/{name}/128k.json).', '',
 'Environment: `'+ ' '.join(k+'='+str(v) for k,v in cfg['env'].items())+'`.', '',
 'Both RTX 4090, K=25, PCIe fraction 0.28, workers=15, normal MTP spec=4/min-p=0.5, INT8 KV, kv-resident=32768 where applicable, prefill=auto, suffix lookup OFF, reuse OFF, greedy serial execution. Total limits are 32768/131072, with about 28.38K/126.72K actual input plus the 4096-output budget and reserve. No 64K/256K test was run.', '',
 '```bash',str(folder/'start-32k.sh')+' --host 0.0.0.0 --port 8080', '# Stop the first server before starting the other profile:',str(folder/'stop.sh'),str(folder/'start-128k.sh')+' --host 0.0.0.0 --port 8080','```','',
 'These new research launchers leave normal user launchers unchanged. `reproduce.sh --experiment UNIQUE_NEW_DIRECTORY --attempt v1 --reproduction` replays saved requests after campaign completion, refuses overwrite, and does not extend the active deadline.', '',
 '## PERFORMANCE', '',
 'The defensible CPU-pool gain is the P1 default→100 µs paired comparison on the unchanged executable. P2 is a separate same-binary OFF/ON comparison. Timing variation between campaigns is preserved; a newer OFF result is not attributed to a source improvement without a controlled comparison. Full PP/TG ranges, MTP, CPU/GPU, VRAM, RAM and raw paths are in [summary.csv](summary.csv) and [summary.json](summary.json).', '',
 '## CORRECTNESS', '',
 'P0: 18/18 exact paired outputs/MTP/routing. P1: 6/6 exact pairs. P2: scoped finite-head/math/JSON checks passed, but '+str(sum(x['same_output_IDs'] for x in p2['correctness']['pairs']))+'/10 short-battery outputs are exactly identical; all differences and first diverging tokens are retained. Live promoted expert weights matched RAM exactly for 1793/2472 expert readbacks at 32K/128K. Slot owner/size/reservation invariants passed. Native suite: 62 PASS, 2 SKIP; four known fixture/environment failures explicitly excluded. Repaired v2 targeted suite: 15 PASS. No general quality judge or proof of every possible interleaving is claimed.', '',
 '## NEGATIVE RESULTS', '',
 '**23. Paths not to repeat without new evidence:** conservative v1 underadmission; this completed v2 traffic/nonlocal tradeoff, which was slower in decode; prior temporary swap/restore; bounded Expert-Jev, frequency, Markov and low-rank variants. Source validation and patch-anchor failures were preserved and repaired in separate versions before inference. No failed attempt is hidden.', '',
 '**24. Strongest future direction:** persistent causal admission with broader calibrated demand/lifetime utility, measured exposed miss/copy costs, and a safe earlier promotion mechanism that avoids CPU CUDA calls inside a spinning verify graph. This experiment does not close all persistent residency. Cross-GPU redesign and new learned scorers are deferred research directions, not unfinished mandatory work.', '',
 '## UNFINISHED DUE TO DEADLINE', '',
 'None in the bounded P0/P1/P2 protocol. The campaign converged before its upper bound; no branch was started merely to consume time.', '',
 '## Preserved evidence and end state', '',
 '[P0](experiments/E026-pool-generalization/report.md), [P1](experiments/E027-pool-baseline/report.md), [P2](experiments/E029-persistent-runtime/report.md), [launch index](launch-index.md), [previous report]('+str(campaign/'previous-root/report.md')+'), [end state]('+str(campaign/'end-state.json')+').', '',
 'All raw, invalid and diagnostic data remain preserved. Owned Strata/training/profiling processes are stopped and both GPU compute-process lists are empty. Model/source provenance and previous archived report hashes were verified. No push, PR, driver/global configuration change, or model change occurred.', '',recommend,'']
text='\n'.join(lines)
# Absolute artifact links work from both copies of the report.
import re
text=re.sub(r'\]\((experiments/[^)]+|variants/[^)]+|summary\.csv|summary\.json|launch-index\.md)\)',lambda m:']('+str(ROOT/m[1])+')',text)
(ROOT/'report.md').write_text(text);(campaign/'report.md').write_text(text)
save(campaign/'final-candidate.json',{'recommendation':recommend,'variant':name,'source':cfg['source_sha'],'binary':cfg['exe'],'binary_sha256':cfg['binary_sha256'],'env':cfg['env'],'configs':[str(folder/(p+'.json')) for p in ['32k','128k']],'launchers':[str(folder/x) for x in ['start-32k.sh','start-128k.sh','stop.sh','reproduce.sh']],'phases':{'P0':p0['state'],'P1':p1['state'],'P2':p2['state']},'P2comparisons':p2['comparisons'],'endstate':str(campaign/'end-state.json')});print(recommend,flush=True)
