# Phase 1 diagnosis

Exact totals across 12 learned main requests: 740,876,492,800 ordinary completed bytes, 367,455,641,600 with no observed routed service. 367,449,497,600 bytes were published and re-evicted before their first intended target: 99.998328% of unused bytes. 6,144,000 bytes were published late. Terminal partition is generation-specific, disjoint and conserves completed bytes in every request. Raw service uses exactly reproduce the original uses counter.

| Explanation | Status | Evidence |
|---|---|---|
| Re-eviction before first target/use | Confirmed sequence | generation+slot+publication+next withdrawal+service journal |
| Newly admitted looks cold | Strong mechanism from implementation | scorer has no admission state; no heat added by copy; low-risk resident can be selected immediately |
| Late publication | Confirmed, tiny learned fraction | two unused 3.072MB admissions |
| Target mismatch | Unsupported in retained runs | zero targets without actual supplied demand |
| Service map mismatch | Unsupported in retained runs | uses match actual local slot journal |
| Duplicate/native admissions | Unsupported in oracle runs | no duplicate retired bytes; native adaptation disabled |
| End censoring | Zero learned terminal bytes; present full reference | survivors accounted separately |
| Bandwidth saturation | Unresolved | aggregate payload rate cannot identify saturation |

Native `unused_bytes` includes all issued zero-use payload, even incomplete/unpublished. In the retained main oracle runs every issued transfer completed, so it equals unused-completed bytes. Mandatory restoration (17,305,600 bytes/request), initial reserve withdrawal and sampled D2H identity reads are separate. Host use counter is observed just before plan service; journal parity verifies actual required local service under that generation. Counts are routed entries, not distinct batches; reconstruction records both.

## Cost and timer audit

E64 is routed-layer invocations. Risk horizons1/4/16/64 are main windows of48 invocations. Copy entry cost=(unique payload/25GB/s+payload/13.2GB/s)/160us. Incoming count to current+768 is compared once with that copy cost, then p16 * max(1,16*prefix rate) victim term. Victim score minimizes p1+.5p4+.25p16+.125p64. Near-target guard uses p1 through one window, interpolating toward p4 thereafter. 160us is assumed, not measured CPU-exclusive latency; victim term is an expected loss proxy, not observed latency.

Thresholds0.2/0.5 had equal retained accounting. Prior combined rejections do not distinguish cost and risk; new counters separate cost, victim cost, risk, protection and cap. Their equality does not establish risk calibration improvement.

Feature/model are nested inside selection and oracle planner. Publication coordination is also inside planner. Prefix history update is outside that oracle planner and charged in request time. Native planning is measured separately by existing pool-plan stage totals; current oracle-hook is not full native planning. CPU monotonic copy interval includes driver/scheduling/completion wait, not DMA-only duration. New enumeration includes nested scoring; do not sum nested timers.

## Intervention and safety

Minimal common treatment protects a generation until first actual local routed-layer service and the next verifier milestone, or target+48 invocation expiry. Current target is earliest supplied future demand, so an opportunistic earlier actual use can satisfy it. Full current-window privilege is unchanged. Active protection limited to16 per device/class. All-protected returns NO_SWAP and required CPU/mapped execution persists. Publication reselects actual compatible victim and rechecks protection. Late intent past target+48 safely aborts completed copy; cap at publication also safely aborts. Existing five spares and serialized class queues bound pending copies.

Verifier `seq` milestone is raised after preceding layer GPU work/post dependencies, then calls host pool (verify.cpp run/batch_poll); release at later milestone preserves previous required readers. No new CUDA synchronization is used for progress. Same-event lease changes increment ownership generation; cached selection cannot survive them. Minimal real-copy/smoke precedes sweep.
