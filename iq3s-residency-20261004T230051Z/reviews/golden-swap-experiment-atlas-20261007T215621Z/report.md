# Golden Swap Experiment Atlas: visual findings

This review makes the retained residency trajectories inspectable. It preserves prior timing conclusions and adds no headline performance experiment. The interactive dashboard contains 12 experiment namespaces, 335 indexed run records, 102 selected trajectories and 3,615,449 generation records. Every selected trajectory passed slot/service and aggregate reconciliation; the lossless browser representation covers 156,180,000 main routed lane entries.

## Startup is a ranked-file prefix, followed by adaptation

The frozen Q4 `expert-profile.bin` supplies a total order. Runtime load preserves that order, filters by K24 device ownership and fills sequential device-local slots using actual aligned per-layer sizes until the byte cap stops the prefix. It does not sort current heat, randomly choose experts or first-fit around an oversized next candidate. Profile-save ranking is a separate inactive path. The exact source excerpts and qualification of the unknown original profile-training dataset are in [startup-selection.md](provenance/startup-selection.md).

The common 32K physical capacity is 6,031 GPU0 + 5,510 GPU1 slots, across three and two active size classes respectively. Five spares withdraw existing residents after the attested decode initial state; they add no VRAM or experts. The tape boundary follows fixed warmup/native prefill. On the selected Phase 2 CURRENT trajectories, 415 process-fill identities had already changed before decode; the process/decode Jaccard was 93.06%. This is an inferred prefix-to-snapshot difference, not an observed prefill routing trace.

| Selected CURRENT task, block 1 | Initial identities demanded by W1 / W16 / W64 | Demanded during full tape | Initial generations surviving W64 / end |
|---|---|---:|---|
| code-archive, 769 windows | 3.81% / 37.80% / 65.83% | 93.28% | 90.95% / 43.62% |
| math-inventory, 766 windows | 3.82% / 34.47% / 59.67% | 88.87% | 86.99% / 40.22% |
| text-websocket, 636 windows | 3.89% / 44.15% / 71.07% | 94.92% | 89.26% / 49.05% |
| mixed-chinook, 548 windows | 3.77% / 36.63% / 62.87% | 86.92% | 86.69% / 35.79% |

These counts show a request-dependent mismatch and substantial continuing turnover. They do not establish a universal initial mass-correction burst: most initial generations survive the first 64 windows, while many are replaced later. Archive's first 64 windows have 1,044 published native admissions out of 10,822 overall; its final uninterrupted survivor fraction is 43.62%. The interface distinguishes an initial identity returning from its original generation surviving.

The early usefulness percentages are **identity-demand coverage**, not hit percentages. Actual local service before initial eviction is a separate curve/table. Full-tape frequency-selected static sets offer an equal layer/class-capacity reference with expert-ID tie breaks; they do not model a feasible dynamic oracle. The initial list is not proven nonsensical globally: 87–95% of initial identities are requested on these finite tapes, with very different first-use distances.

## Future knowledge can buy useful traffic rather than fewer swaps

The exact early lineage has several meanings: IQ3_S E004's corrected v6 replays recorded demand under assumed transfers and fixed observed compute; Q4 v2 adds future-feasible, capacity-free and utility schedules; Q4 live-oracle v3 later executes the same full native tape with real copies and fidelity/capacity checks. They are not one oracle experiment.

On Q4 v2's 32K recorded trace, future-feasible makes 87,476 publications / 275.22 GB and leaves 39 modeled nonlocal lane entries. Timing-relaxed capacity-free makes 157,409 publications / 494.81 GB and leaves zero modeled nonlocal entries. Those are high-churn reference schedules. The retained future-feasible model also has substantial modeled join wait; zero fallback is not a latency win. CPU/mapped subdivision of alternative modeled schedules is unknown.

The following are **observed block-1 trajectories**, not a new timing comparison or independent policy retune. Bytes are ordinary completed payload, excluding the oracle's 17,305,600-byte mandatory restoration.

| Archive trajectory | Publications | Copy GB | CPU + mapped entries | Evicted without use GB | No-use resident at end GB |
|---|---:|---:|---:|---:|---:|
| Phase 1 CURRENT | 10,822 | 34.1276 | 70,827 | 2.9804 | 1.8902 |
| Phase 1 full oracle | 19,455 | 61.7646 | 2,987 | 0.0553 | 0.0276 |
| Phase 1 learned, no TC | 17,678 | 56.3139 | 41,952 | 27.9491 | 0 |
| Phase 2 full oracle | 19,872 | 63.0446 | 1,685 | 0.0276 | 0.0061 |
| Phase 2 history + TC | 9,682 | 30.5855 | 39,962 | 0.0031 | 0 |
| Phase 2 logistic + TC | 9,266 | 29.1624 | 40,945 | 0 | 0 |

The real full oracle can copy considerably more than CURRENT while almost every copied generation serves required work. The no-treatment learned arm also copies more, but many generations disappear unused. This difference is visible in intervals, repeats and terminal outcomes, rather than inferred from total copied bytes. End-censored native copies remain separate from evicted-without-use copies.

The dashboard's whole-model future-reference similarity uses same-source, same-campaign sets at every verifier-window end. For Phase 2 archive, mean identity Jaccard is 0.7344 CURRENT, 0.7333 history+TC and 0.7301 logistic+TC against full oracle. CURRENT being fractionally closer does not make its schedule more useful: it has much more nonlocal work. Identity similarity weights all residents equally; a few missed imminent experts can matter more than the large stable overlap. The page ranks each task/reference group separately rather than declaring one cross-domain winner.

## AUC survives as ranking evidence, then meets a different state distribution

The Atlas reproduces all 48 frozen-logistic weighted AUC values from saved predictions and masked native-resident labels to within `1e-10`. It retains 96 original logistic/tree metric rows, calibration bins/Brier and sampled-victim ranking. These data substantiate predictive signal in the original conditional native distribution. They do not measure a new admission's useful residency, physical copy readiness or exposed request latency.

Phase 2's generation-linked diagnosis attributes **99.998328%** of Phase 1 learned no-observed-use payload to re-eviction before its intended first target. The Atlas preserves the actual generations and targets. For archive layer 0, the no-TC learned arm has 872 published generations, median observed lifetime 0.0417 windows and median distinct service count zero; expert 122 is admitted 41 times. Its used generations wait a median 0.8958 windows to first service. Many admitted residents therefore disappear long before their intended use.

With the common minimal TC, archive layer 0 history has 314 published generations, all observed used, median distinct service count 13 and median observed lifetime 243.34 windows. Logistic has 292, all observed used, median distinct count 11 and median observed lifetime 217.97 windows. These lifetime summaries include right-censored survivors and describe one layer/block. They are a strong mechanism illustration, not a universal lifetime distribution or a scorer-quality proof.

The frozen predictor omitted policy-dependent admission age. First-use control repairs this external state problem for both scorers. The matched cheap rule already had a slightly better calibration cost proxy; Phase 1 did not include it in its main live matrix. Phase 2's direct paired history/logistic results do not establish a learned benefit. The decision funnel displays risk/feature calls, cost veto, protection/cap exclusions, actual copies, service and victim absence with their own units. Enumeration counts are repeated visits, not unique admissions; they are not added to transaction totals.

In Phase 2 archive history block 1, cost veto is 1,749,071, protection exclusion 9,992, cap veto 4,255 and risk veto zero. The calibration 0.2/0.5 settings retain identical action hashes. Changing a nonbinding threshold is not policy evidence. Protection cap exposure includes 1,859 nonlocal lane entries on this run, but neither eligibility nor copier readiness is held counterfactually fixed; that count is not proven avoidable regret.

For archive block 1, avoided nonlocal entries per completed GB are approximately 513 for Phase 1 learned, 1,009 for Phase 2 history+TC and 1,025 for Phase 2 logistic+TC, relative to their respective CURRENT work. This is an accounting efficiency, not exclusive latency saved per byte. The system overlaps CPU, mapped, GPU, staging and planning; the old 160-us guard was an assumption. Feature/model timers nest inside selection/planner. CURRENT's tiny oracle-hook timer is not total native planning.

The dashboard retains the same-binary development OFF/ON lifecycle ablation and the original paired timing outcomes. Phase 2's confirmed scope remains inventory/Chinook; Phase 3 memoization removes repeated query work without a confirmed >3% incremental practical gain. Phase 3's corrected chronology is retained without vector-position causal inference. Phase 4's symmetric perturbation gate failed, so acknowledgment overlap is not asserted to be completion-path saving. None of these prior conclusions was rewritten.

## Lease evidence favors state-aware questions, not a universal TTL

Archive layer 0's observed inter-demand gaps have median 6 windows and maximum 535, across local and nonlocal service. The same tape has fleeting unused admissions, long repeated-use residents, idle intervals and end-censored survivors. The scatter shows initial observations as diamonds because their age before decode is unknown. Copy timing is a host bracket; it is not pure DMA or an exact break-even threshold against logical gaps.

This spread supports inspecting expert-specific retention and do-not-admit hypotheses. It does not establish natural clusters, optimal pinned experts or a TTL length. Phase 2's uniform 48-event soft post-use extension had already lost useful competing admissions and was rejected. Merely preserving every useful expert longer can exhaust a device/class pool. The exploratory labels in the UI deliberately retain censoring and competing-demand qualifications.

The highest-information follow-up would be a bounded **offline opportunity-cost analysis of selective post-use retention**, using the now-visible generation/reuse patterns, fixed oracle incoming and measured class capacities. Compare an explicit NO_SWAP baseline, minimal first-use TC and one coarse selective extension on development data; charge missed competing admissions and copy work. First establish which long gaps belong to repeatedly costly reloads. The Atlas implements none of this. It provides no new justification for a larger victim model or automatic transition to causal incoming prediction.

## Validation and limits

All 102 trajectories reconcile windows, main lane counts, slot ownership, generations and ordinary byte partitions. Seven representative oracle lifecycles were checked back to E/LC/replacement records. The compact encoder round-trips every normalized service row. A fresh bounded regeneration recreates all 48 layer files and the summary byte-for-byte. Browser tests cover all ten pages, selectors, linked zoom/pan/hover, exact compact decoding, same-tape CURRENT/full-oracle comparison, difference/time units, provenance and image export through HTTP. A missing favicon in the first browser pass was repaired; the earlier receipt remains retained.

Unknowns include prefill/warmup per-expert routing, original profile-training provenance, IQ3_S process fill, MTP expert-path subdivisions, per-event veto timelines, exact live same-state scorer disagreement, pure DMA time and exclusive CPU latency. The 256K native diagnostic has 96 unobserved publications / 0.3018 GB with unknown completion. Observation ends are finite; absence of later demand is censoring. Aggregate-only natural or timing repetitions receive no invented events.

Selected normalized evidence and all display assets are in Git; original binary captures remain outside it with hashes and explicit local-only recovery gaps. The server remains running on `0.0.0.0:8765`. No new GPU benchmark, predictor fit, residency policy, production launcher or model-weight modification occurred.

Pre-publication checks preserved two additional findings: generated CSV CRLF endings needed LF normalization, and three large row-level JSON documents needed the repository's complete gzip path. Their full bytes and the failed audit receipt were retained; small readable references now point to those complete archives. This changed publication format only. A fresh bounded reproduction and HTTP browser validation checked the archived configuration/data paths.
