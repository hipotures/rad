# Active dependency model and trace interpretation

Verified against parent f3b4f19157b39ae017e2fd91814c8f5728e3b1cc before tracing.
The Phase 3 chronology correction is prior context: generation/vector position
identifies records, while actual event/timestamp state determines ordering.

The host oracle hook checks all five workers, including workers on the other
GPU. A completed weight copy is required before publication validation. The
worker's state-4 command submits two four-byte residency metadata copies,
synchronizes its existing CUDA event, then stores state 5, notifies and unlocks.
Only after the condition-variable acknowledgment does the host commit ownership,
generation and spare-slot state. The same hook then accounts demand and plans
incoming copies. Native plan construction follows the oracle hook; a fence and
flag A publish that native plan before fetch/CPU work. The actual compute stream
waits A, computes resident experts, waits B, computes mapped experts, waits CPU,
then joins shared work and combines. Worker subphases nest inside host ack.

Under K=24, the first stage writes mapped portable pinned handoff data, completes
its compute stream and only then calls the next verifier's run. This is a serial
stage dependency, not a peer-expert helper or concurrent peer flag. Shared expert
fork/join is active by default (STRATA_SH_STREAM unset); STRATA_VERIFY_PROFILE
must remain unset. Device-plan and all-resident shortcuts are inactive at partial
residency, and no remote/helper expert option is enabled. Live counts and native
environment must attest those facts before quantitative interpretation.

TRACE retains A/B/CPU begin/end in the existing timed wait kernels. Version 1
added five per-layer stamp launches (shared begin/end, prejoin/postjoin, combine
end), despite an early prose count of six. The first pair failed the symmetric
gross timing gate. The one substantive repair, version 2, removes all five
per-layer launches and records shared final-scale and combine math brackets in
existing kernels using a conditional block barrier/device fence/completion
counter. These endpoints precede kernel retirement; they are not exact CUDA
join/event completion. Shared fork begin and independent prejoin/postjoin
coverage are unsupported in v2. Two per-window boundary stamps remain.

CONTROL allocates the same buffers but omits detailed stores. No critical-path
writes to disk or new device-wide synchronization. Existing metadata completion
synchronization is unchanged. The v2 timing gate still failed due to large
individual changes in both directions; structural attribution is retained while
quantitative neutrality is not established. See report.md for the complete gate.

Two fixed calibration stamps per verifier/request bracket start and end on the
already-safe request boundaries, in both arms. Submission plus ordered async
readback is completed there; this adds boundary work charged to completion wall.
Host brackets bound each GPU stamp separately. Interpolation assumes affine clock
mapping; only two boundary samples cannot prove absence of interior drift.
Report this unsupported uncertainty explicitly and keep conservative intervals.

Per-kind request-local ordinal plus ring identifies window and layer; counters
are reset before decode. Replaying a captured graph increments device counters
rather than reusing a captured host index. Kind counts over capacity expose
overflow. Warmup is flushed/reset separately, and only the tape-selected measured
request writes the trace files. Admission generation is captured locally in the
worker before acknowledgment; reuse of worker.index cannot alias later records.

Calibration explicitly uses an ordered readback plus compute-stream synchronization
at already-safe request boundaries in both arms. No routed-event or device-wide
barrier was added. This is nevertheless an extra calibration completion barrier;
the strict no-convenience-barrier wording was not fully met. Charge boundary
work and retain this deviation, rather than asserting perfect neutrality.
