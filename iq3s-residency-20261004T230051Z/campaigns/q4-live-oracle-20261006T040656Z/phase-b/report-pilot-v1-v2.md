# Phase B — feasible logical scheduling, first full-scope pilot

## Physical mechanism

The common isolated oracle runtime covers all 48 main layers and every routed Q4 byte class. GPU0 owns layers0..23, GPU1 layers24..47. Five existing class-compatible slots are withdrawn inside timed decode: GPU0 one each3.072/3.584/3.9936MB, GPU1 one each3.072/3.584MB. The original allocator/cache bytes, dense weights, INT8 KV, MTP and scratch are unchanged; oracle active residency is lower by five experts. No extra expert VRAM or P2P/remote execution.

A copy runs from immutable full-RAM arena through pinned staging on a nonblocking device stream. The victim remains resident until copy completion. At a legal routed-layer planning boundary the worker publishes the new device mapping; host ownership then changes, and the evicted slot becomes the next same-class spare. Current full T-by-10 demand protects all lanes. Native exchange is retained without modification in REPLAY_CURRENT. Oracle takes sole exchange authority during its timed decode scope while causal native heat/usage tracking continues. End-of-request drain and five-slot restoration are charged in request-comparable wall time.

Candidates use logical event index verifier_window*48+layer. Actual event/copy/staging durations update a rolling physical slack estimate. No action is fired at a recorded elapsed millisecond. Deadline policy selects useful missing upcoming demands and farthest-next-use safe victims. Reuse-amortized policy is a predeclared materially different alternative, requiring repeat benefit within a16-window utility interval. Both are heuristics, not optimizers or upper bounds.

## Offline results

Native-policy simulation initially reset the cumulative adapt window counter and did not reproduce all counters. Repair: warmup contributes25windows; source's counter persists between requests. The corrected simulation exactly matches the recorded32K main local/CPU/mapped demand and native adaptation traffic. The earlier incorrect simulation remains preserved.

Current: 1,972,893 local,196,292CPU,31,135mapped entries;27,893native copies,87.418GB. Capacity-only future simulation reaches zero nonlocal demand with215.698GB exchanges; timing is relaxed and no speed claim follows. Transfer-aware modeled full-deadline simulation yields2,579nonlocal entries and217.438GB. Reuse-amortized simulation yields121,381nonlocal entries and41.277GB. These use explicit modeled staging25GB/s,copy13.2GB/s,publication45us and event570us, not measured GPU execution. No simulated tok/s is reported.

Bounded horizons1/4/16/64 restrict both admissions and victim queries. Unknown future victim use beyond H falls back to causal heat, not guaranteed absence. H1 cannot meet even the minimum lead with this substrate; H4/H16/H64 cause much higher churn than full-future. See preserved JSON in phase-b and horizon-definition.json. Only full future plus at most one informative short horizon will receive live confirmation.

## Actual v1 pilot, not final full-work A/B

Same common binary/tape, fresh server, warmup4096input/64output, benchmark28378input/4096output. REPLAY_CURRENT102.6replay-equivalent tok/s; full-deadline130.4. Current local1,972,893/2,200,320=89.664%; oracle local2,188,225=99.450%,CPU10,620,mapped1,475. Oracle issued66,097actual copies,208.019GB,all published;66,089before intended target and8late,1,088,818subsequent local uses,9,588victim-absent entries. Native-current87.418GB versus oracle208.019GB. Median staging0.1253ms, copy with host completion wait0.2412ms; planner4.719s includes publicationwait2.110s. Drain~0ms; restoration1.427ms. CPU timestamps include scheduling and are not pure DMA duration.

This pilot improved locality and time despite extra copies, but native arithmetic diverged (first head atwindow15), and QSA selection was not frozen. It is excluded from final full-work tables. Version2 freezes sparse-attention selection after computing native top-k, and checks initial adaptation phase explicitly. Final arms use the same v2 binary and tape.

## Safety

Production worker/publication methods passed the ten-group real-CUDA fixture: all classes/devices, exact copied bytes, duplicate refusal, protected victim, already-resident suppression, delayed fallback, repeated spares, cancellation/drain/restoration, next request and pending shutdown. Version2 QSA override kernel passes record/replay/OFF for T1..4 and all12QSA layers on both4090s. Native suite66PASS/2SKIP/4known missing-fixture/mlock-limit failures; no new correctness failure. Evidence remains in tests/.

## Limitations

Full-future policy can exploit known finite tape end; no guard tail exists. We disclose censored tail victims and cleanup. First pilot is one workload trajectory and one timing pair, not task diversity/statistical proof. Main scope is full; MTP cache residency remains normal. Expert numerical execution is unchanged, but CPU/GPU summation can differ. Forced output equality is not correctness evidence. Version2 final matrix and a fresh natural/replay overhead comparison remain required.
