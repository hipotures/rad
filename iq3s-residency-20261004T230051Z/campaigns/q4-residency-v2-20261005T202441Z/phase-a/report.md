# Phase A — Q4 ground truth, costs and headroom

**COMPLETE_MIXED — proceed to causal Phase B.** All nine new Q4 traces reconcile every routed entry, exact physical slot class, issue/publication and current-selector ordering. All three long traces match the original frozen executable in input/output integer IDs, MTP aggregates and routing. Current replay matches observed nonlocal counts and copy bytes; no simulator-only TG is claimed.

|Context|Actual input|All-demand local %|CPU entries|Mapped entries|Promotions|Promotion GB|Unused GB*|Victim entries*|
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|32k|28378|89.66|196292|31135|27893|87.42|11.04|151049|
|128k|126715|88.90|231342|36617|31627|99.37|11.49|185345|
|256k|257781|90.09|213972|32924|30670|96.48|11.93|168745|

*Unused near the end is right-censored; victim entries describe observed absence after the latest eviction, not a proven latency penalty. Every incoming promotion is immutable native Q4 data, retained without copying back to RAM. Most incoming experts are reused, but rapid changing demand exposes eviction damage.

## Fixed bytes and ownership

77,017,907,200 bytes /71.73GiB routed RAM arena,48×512 experts. Native blob classes:3,072,000bytes Q4_K/Q5_1;3,584,000bytes Q4_K/Q8_0;3,993,600bytes Q5_K/Q8_0. K24 fixes GPU ownership. Each original physical slot class is retained; no two-GPU virtual pool, size-only victim packing or added VRAM capacity. Full exact budgets are in summary.json and trace files. Expert file reads during decode are zero; mapped RAM and PCIe work are not SSD streaming.

## References and limitations

|Context|Reference|Link GB/s|Nonlocal entries|Promotion GB|Modeled join wait s|
|---|---|---:|---:|---:|---:|
|32k|future-feasible|1.8|39|275.22|149.599|
|32k|future-utility-wide|1.8|497088|4.09|1.590|
|32k|future-feasible|12.6|39|275.22|18.637|
|32k|current|6.8|227427|87.42|11.910|
|32k|future-capacity-free|relaxed|0|494.81|0.000|
|32k|future-feasible|6.8|39|275.22|37.220|
|32k|future-utility-wide|6.8|342210|84.78|11.522|
|32k|future-utility|6.8|430947|19.60|1.848|
|32k|static|6.8|587167|0.00|0.000|
|32k|current|13.2|227427|87.42|3.055|
|32k|future-feasible|13.2|39|275.22|9.341|
|32k|future-utility-wide|13.2|341222|93.98|2.919|
|128k|future-feasible|1.8|36|270.01|146.096|
|128k|future-utility-wide|1.8|514975|7.45|3.224|
|128k|future-feasible|12.6|36|270.01|17.708|
|128k|current|6.8|267959|99.37|13.522|
|128k|future-capacity-free|relaxed|0|503.42|0.000|
|128k|future-feasible|6.8|36|270.01|35.868|
|128k|future-utility-wide|6.8|371904|100.08|13.630|
|128k|future-utility|6.8|471620|23.47|2.260|
|128k|static|6.8|626660|0.00|0.000|
|128k|current|13.2|267959|99.37|3.641|
|128k|future-feasible|13.2|36|270.01|8.776|
|128k|future-utility-wide|13.2|370327|112.72|3.564|
|256k|future-feasible|1.8|109|282.18|152.903|
|256k|future-utility-wide|1.8|494338|5.74|2.383|
|256k|future-feasible|12.6|109|282.18|18.759|
|256k|current|6.8|246896|96.48|13.120|
|256k|future-capacity-free|relaxed|0|518.54|0.000|
|256k|future-feasible|6.8|109|282.18|37.735|
|256k|future-utility-wide|6.8|377524|101.65|13.933|
|256k|future-utility|6.8|452541|24.66|2.506|
|256k|static|6.8|590326|0.00|0.000|
|256k|current|13.2|246896|96.48|3.409|
|256k|future-feasible|13.2|109|282.18|9.182|
|256k|future-utility-wide|13.2|374645|118.69|3.872|

The capacity-only reference relaxes timing and copy issue restrictions. The future next-use schedule charges serialized per-device/shared-link queues, victim withdrawal and next-window publication, but keeps observed nonpromotion work fixed. It is feasible within that modeled queue, not an optimum or hardware latency oracle.1.8GB/s is a conservative interference scenario,6.8GB/s the existing staged-expert envelope,12.6GB/s an isolated optimistic pinned limit. Newly measured contended copies below refine rather than replace these sensitivity cases.

The narrow32MiB/device forecast reference misses more despite strong future knowledge: insufficient replenishment makes a poor heuristic, not a proof that prediction cannot help. The wide160MiB/device/96-exchange reference also has limitations from a short4-window objective. Phase B must score longer resident utility/victim reuse rather than equate gate probability with net benefit.

## Selected exposed costs

The three-layer GPU event sample reports resident computation, mapped execution and exposed CPU-done wait separately. Phase0 also includes host-plan wait and mapped activation copy; phase3 can overlap upstream CPU execution. They are never added or multiplied by48. Exact sample distributions and conditional CPU-positive versus all-local-or-mapped results are in cost-analysis.json.

### 128k

Native router pilot targets [13, 20, 33, 40, 46], same-window membership 34.03%, next-window target-demand coverage 28.71%. Five of48 layers only; raw gate confidence is not calibrated future demand. GPU gate/top10 span median 0.01946ms. Original-target host lead median 3.3451ms, not an exact GPU demand deadline. Actual adaptive copies issue after verification, so current-window target lead does not make them early prefetch.

- GPU0 3072000bytes: sampled copy median 0.2328ms, median effective 13.19GB/s; host enqueue median 0.0018ms.
- GPU0 3584000bytes: sampled copy median 0.2711ms, median effective 13.22GB/s; host enqueue median 0.0018ms.
- GPU0 3993600bytes: sampled copy median 0.3015ms, median effective 13.24GB/s; host enqueue median 0.0017ms.
- GPU1 3072000bytes: sampled copy median 0.2330ms, median effective 13.19GB/s; host enqueue median 0.0023ms.
- GPU1 3584000bytes: sampled copy median 0.2711ms, median effective 13.22GB/s; host enqueue median 0.0021ms.

### 256k

Native router pilot targets [13, 20, 33, 40, 46], same-window membership 34.56%, next-window target-demand coverage 28.41%. Five of48 layers only; raw gate confidence is not calibrated future demand. GPU gate/top10 span median 0.01946ms. Original-target host lead median 3.3607ms, not an exact GPU demand deadline. Actual adaptive copies issue after verification, so current-window target lead does not make them early prefetch.

- GPU0 3072000bytes: sampled copy median 0.2329ms, median effective 13.19GB/s; host enqueue median 0.0018ms.
- GPU0 3584000bytes: sampled copy median 0.2710ms, median effective 13.22GB/s; host enqueue median 0.0017ms.
- GPU0 3993600bytes: sampled copy median 0.3017ms, median effective 13.24GB/s; host enqueue median 0.0018ms.
- GPU1 3072000bytes: sampled copy median 0.2330ms, median effective 13.19GB/s; host enqueue median 0.0020ms.
- GPU1 3584000bytes: sampled copy median 0.2710ms, median effective 13.23GB/s; host enqueue median 0.0020ms.

### 32k

Native router pilot targets [13, 20, 33, 40, 46], same-window membership 29.79%, next-window target-demand coverage 24.65%. Five of48 layers only; raw gate confidence is not calibrated future demand. GPU gate/top10 span median 0.01843ms. Original-target host lead median 3.7338ms, not an exact GPU demand deadline. Actual adaptive copies issue after verification, so current-window target lead does not make them early prefetch.

- GPU0 3072000bytes: sampled copy median 0.2328ms, median effective 13.19GB/s; host enqueue median 0.0027ms.
- GPU0 3584000bytes: sampled copy median 0.2710ms, median effective 13.22GB/s; host enqueue median 0.0027ms.
- GPU0 3993600bytes: sampled copy median 0.3016ms, median effective 13.24GB/s; host enqueue median 0.0026ms.
- GPU1 3072000bytes: sampled copy median 0.2331ms, median effective 13.18GB/s; host enqueue median 0.0028ms.
- GPU1 3584000bytes: sampled copy median 0.2713ms, median effective 13.21GB/s; host enqueue median 0.0027ms.

## Correctness and baseline scope

Diagnostic build source8d542977631b6f015115ed1f09acc1c336070ab8, binaryc5f39fb7bba7ce9113d122c787414f654d0db0073c997a6ad61c82331ea3af84. Native suite62pass,2skip,4known previous fixture/environment failures: ple_parity,platform_memory_test,expert_parity,pool_test. Full errors are preserved; this is not a falsely green suite. Relevant native Q4_K/Q5_1,Q4_K/Q8_0,Q5_K/Q8_0 and pool/router/cache tests pass.

The practical control remains the original eca9d0d... executable, source6f32ec0...,0.1.39, K24/.28,100us,15workers,spec4/min-p0.5,INT8,kv-resident32768,prefillauto,suffix/reuseOFF. Fresh64-output warmups do not fully warm full-length prefill: this protocol intentionally differs from the old one-server/three-request Q4 campaign. Reused latest pool controls32/128 are compatible; a new original256K run was collected before compiling. Preserve this chronology in final paired interpretation.

## Primary references and branch plan

[Open-Jev](https://github.com/Zefan-Cai/Open-Jev) pinnedbd411888...,MIT: independent discriminative candidate scoring with LoRA/backbone; our numeric count models are Expert-Jev-inspired, not its checkpoint. [Basal](https://github.com/rkinas/basal) pinnedc3cab778...,Apache2: typed decisions/shared state; EagerBackend CPU run_shared actually flattens full forwards, so efficient CPU SOAM cannot be assumed. [Fate](https://arxiv.org/abs/2502.12224) and [SpecMD/Least-Stale](https://arxiv.org/abs/2602.03921) pinned originalv1 HTML: inspect exact stale/prefetch semantics before claiming reproduction. Borrowed code/license manifests remain under sources/.

Meaningful expensive miss/transfer/churn headroom remains plausible. Proceed with bounded cheap history/Markov/stale, native router H1/H4/H8, required local linear/32-unit MLP and temporal scorer, then hybrid. Incoming and victim expected demand are scored together. Basal is optional and needs a bounded semantic-to-Q4-demand hypothesis; do not download a large checkpoint by default. No live residency policy has been enabled at this gate.
