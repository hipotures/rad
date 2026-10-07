# E003: buffered demand and dependency traces

Question: are residual costs explained by policy/admission, capacity, or coordination? Collect actual `(request, window, token/branch, layer, expert)` dispatch, including rejected MTP drafts. Record disjoint local/mapped/CPU paths and current slot identity, per-layer blob bytes, initial heat/residency, promotions and observed publication readiness. Record CPU-host reach/pool brackets and window accepted/output progression. CPU clocks are one steady_clock domain; transfer completion is observed after existing event waits, not fabricated GPU timestamp accuracy.

Default-off trace hooks use bounded buffered numeric records and flush after engine decode timing. No per-event CUDA synchronization, expert replacement or router changes. Trace memory is host RAM and diagnostic-only. Each variant gets its own checkout/build and launch config. Preserve patch/build failures before repairs.

Finite workloads: fresh diagnostic server/profile, saved4096/64warmup then one4096 repository request at each of32k/128k. Separately use six frozen independent short task episodes for development/calibration/holdout, at32k capacity, max1024 output each. Natural EOS is allowed for predictor episodes, not fixed-length speed claims. Benchmark workload and nonce siblings are not independent predictor holdouts.

Overhead: compare diagnostic-enabled saved workload to clean control with matching configuration and output/MTP evidence. Free generation may confound an exact percent; supplement with same-binary trace OFF/ON short fixed workload if needed. Diagnostic numbers never replace clean headline results. Validate entry sums against native footer and API counts, slot-byte/resource invariants, window/group/token indices, actual input/output IDs, and publication only after completion.

Completion: replayable traces with schema and provenance, accounting check and overhead limitation, timing/path analysis, then policy/learned-scorer replay. No expensive training/analysis while clean speed measurements run.
