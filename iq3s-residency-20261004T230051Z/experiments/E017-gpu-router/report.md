# E017: native GPU next-gate signal

The bounded diagnostic passed: all actual output IDs, MTP windows, true router IDs, execution paths, initial/final heat and residency match the fresh control diagnostics. Both full benchmark first heads are bit-identical (KL0). The extra prediction never substitutes actual expert routing.

The existing BF16 GPU gate/top10/publication path costs16–19us median, versus hundreds of microseconds for the CPUfullgate. GPU and freshCPUfullgate predicted top10 memberships agree100% on these recorded activations. Five same-device pairs only;24→25 excluded.

| Task | Precision% | Tailrecall% | Ready tail12.6GB/s% | Ready tail1.8GB/s% | Score/publishus | Leadus | False nonresident proposals |
|---|---:|---:|---:|---:|---:|---:|---:|
| 32k | 71.23 | 64.71 | 64.29 | 7.14 | 16.38 | 243.51 | 266 |
| 128k | 68.71 | 42.07 | 42.36 | 1.39 | 19.46 | 246.93 | 359 |
| dev-code | 69.26 | 55.83 | 55.83 | 3.33 | 16.38 | 237.83 | 463 |
| dev-math | 72.16 | 47.09 | 47.09 | 0.00 | 16.38 | 241.10 | 381 |
| cal-prose | 70.43 | 66.54 | 66.35 | 2.08 | 18.43 | 252.48 | 593 |
| hold-code | 70.63 | 55.45 | 54.95 | 1.49 | 16.38 | 239.73 | 411 |
| hold-structured | 65.99 | 46.83 | 46.83 | 0.98 | 16.38 | 248.20 | 405 |
| hold-math | 70.21 | 53.76 | 53.76 | 2.02 | 16.38 | 243.33 | 489 |

The readiness columns are optimistic independent one-blob estimates: ignore queuecompetition/fullslots/victims/inflightreaders, and use CPUobserved targetrouter time ratherthan an exactGPUdeadline. They are neither TGgains nor a feasible complete policy. Contended1.8GB/s leaves only0–7.14% ready-tail recall in this sample; isolated12.6GB/s often covers40–66%, so the CPUnegative alone was insufficient.

Memory:320explicitGPUbytes/device,864mappedCPUbytes/device, no duplicate gate, reused expired current-logits scratch. CUDAallocation/eventinternal costs not assumedzero; actual VRAM telemetry retained. Expertphysicalclasses/capacities matchcontrolbothprofiles. No cleanthroughput measurement or instrumentationoverheadcertificate.

Retained v1 build failure: duplicate GEMV widthargument. Separatev2 removes onlythatargument. Targeted13native tests and realIQparity pass.

Reproduce: `variants/diagnostic-gpu-router-v2/diagnose-profiles.sh` / `diagnose-episodes.sh`; originalattempts refuseoverwrite. Analysis: `scripts/analyze_gpu_router.py`, `analyze_gpu_router_episodes.py`, `consolidate_gpu_router.py`. Identity/rawrefs in summary.json.

Decision: bounded queue/victim feasibility next; no unconditional fullgatepromotion/live winner claim.
