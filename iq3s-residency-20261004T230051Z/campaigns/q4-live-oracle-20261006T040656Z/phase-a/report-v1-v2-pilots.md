# Phase A — fixed-work replay

PASS for the32K/4096 trajectory:1289windows,61872main routed invocations,3563real MTP full steps. All prompt IDs, shapes, routes, float32 coefficients, proposals, acceptance and commit dependencies reconcile with native counters. Replay-current has zero native router/coefficient disagreements and no native-head divergence. Initial11541resident identities/slots and native heat match exactly. Real dense/attention/KV/PLE/head and rejected speculative work execute.

Short development natural/replay execution uses the same binary and produces identical actual outputs, MTP and route service counters. One fresh pair shows3.0%longer replay decode and1.1%wall; this is provisional overhead evidence, not an exact isolated kernel-cost estimate. Confirm on the final same-binary substrate. Recording is diagnostic and excluded from speed claims.

Scope limitation: all main/MTP decode work is frozen; prefill executes normally from exact input IDs. Initial resident state and successful native numerical trajectory are audited. Attention sparse indices/hidden tensors are not forced; their launch shapes are determined by positions and fixed commit schedule. Selected finite activations are saved. Kernel/numerical safety checks precede oracle benchmarking.

Failures preserved: relative tape launcher path repaired to absolute path; offline malformed-shape validator fixed to reject before indexing. No model or production source changes.

## Version2 fidelity repair

The earlier sparse-attention limitation above is resolved in schema2. After computing native QSA scores/top-k, both replay arms force exactly the recorded selections before KV resolution/attention. All12QSA selections/window and the initial native adaptation round counter are recorded/checked. Version2 capture32K passes complete conservation (1289windows,61872main,3563MTP,2,200,320main entries); identical natural emitted IDs/MTP/service counts to v1. Replay-current attempt1 has no native main-head divergence and no router/coefficient or QSA selection disagreements. Initial slot identities/native heat match bitwise. Work SHA237ee8e7d981129238afaa1a754453d3ecee8087af0c9c1a3f2fc950f9b36fd9;528.120MB tape. Capture99.8, fresh replay-current104.4replay-equivalent tok/s; recording excluded from speed claims.

Logical kernel shapes (T/positions/48layers/per-expert token assignments) are frozen. Physical local/CPU/mapped grouping counts necessarily change when residency changes; this is the intended service variable and remains recorded, not silently claimed identical. Each mathematical expert-demand batch is preserved and runtime legal concurrency remains intact. Selected eight-component activation observations are diagnostic, not substituted.
