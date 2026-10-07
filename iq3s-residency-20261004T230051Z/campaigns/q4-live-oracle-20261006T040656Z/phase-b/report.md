# Phase B — feasible full-scope logical oracle scheduling

This final phase handoff supersedes the preserved pilot report. The final common source is 117bc89b3bacbf263379c336557e6c8aa07aff5e; binary SHA256 is 30a31432b5aff51bcd4340900c13cad0c8487a832bfdb22d05f9157b88d5bdb3. Final matrix results and paired timing live in ../report.md.

## Physical contract

All 48 main routed layers and all three physical classes (3.072, 3.584 and 3.9936 MB) are eligible. GPU0 owns layers 0–23 and GPU1 owns 24–47. Five existing slots become class-compatible spares after timed decode begins. Allocated expert/dense/KV/MTP VRAM is unchanged; active residents decrease by five, and restoration of 17,305,600 bytes is charged. MTP stays on its original all-resident expert path.

Immutable host-RAM weights pass through pinned staging and real nonblocking H2D streams. One transaction per device/class has exclusive ownership. Completed copy is published only at a safe routed-layer boundary; the old victim slot becomes the next spare. Current full-window batches protect readers. Victims are chosen at publication using the same future knowledge as admissions. No temporary swap/restore, remote experts, P2P or SSD source is used.

REPLAY_CURRENT retains native adaptation. REPLAY_ORACLE_FULL is the sole exchange authority for main decode while causal heat updates continue. Native and oracle traffic, initial spare loss, online planning/publication wait, mandatory drain and restoration are reported separately. Copies are issued from logical milestones, never recorded wall-clock offsets.

## Information and heuristic

Full future supplies victim next-use and incoming future demand/lifetime. The rolling incoming issue frontier is 64 main routed-layer invocations; one invocation is the entire T-by-10 batch, not a generated token or verifier window. Measured event progress and staging/copy duration update lead estimates. Late work uses safe CPU/mapped fallback. This is a feasible next-use/slack heuristic with same-layer victims, not an optimal variable-size scheduler or upper bound.

## Offline models

The warmup counter correction (25 native adaptation rounds carried into request 2) exactly reproduces 32K native local/CPU/mapped counts and native traffic. Capacity-only full future reaches zero nonlocal entries using 215.698 GB of exchanges under relaxed transfer timing; no measured TG follows. Modeled full-deadline transfer replay yields 2,579 nonlocal entries and 217.438 GB. The alternative reuse-amortized strategy yields 121,381 nonlocal entries and 41.277 GB. Explicit modeled costs remain assumptions, separate from live timing.

Offline horizons 1, 4, 16 and 64 constrain both admissions and victim queries. An early version leaked full current-window protection beyond short horizons; strict_offline.py repairs it and preserves the old results as safety-privileged diagnostics. Beyond the bound is unknown and uses causal heat, not guaranteed absence. The live H64 does not have this leak because all remaining current-window layers are inside 64.

## Live result

| Profile | Current decode s | Full-future decode s | Median paired TG gain |

|---|---:|---:|---:|

| 32k | 38.969 | 33.303 | 17.01% |

| 128k | 49.808 | 40.597 | 22.69% |

| 256k | 52.033 | 43.372 | 14.51% |



The single H64 confirmation took 42.7656 s (95.78 replay-equivalent tok/s), with 317.525 GB copies and 85,392 victim-absent entries. Full-future attempt 1 used 207.126 GB with 10,036 victim-absent entries. This repaired bounded heuristic demonstrates harmful churn, not a universal impossibility result.

The primary full-future schedule improved readiness/locality and measured replay decode at every profile, so a second live full-future heuristic was not needed. Independent substantive source content confirms a separate paired benefit. All primary counts, ownership, copies and work hashes passed. See phase-c/ and ../analysis/ for admission funnels, residual misses and distinct persistent reuse.

## Safety and interpretation

The real-CUDA scheduler fixture checks all physical classes, exact bytes, duplicate/inflight refusal, protected victims, became-resident suppression, delayed fallback, repeated spares, cancellation/drain/restoration, next request and pending shutdown. QSA record/replay overrides and initial-state sidecar tests pass. Actual Q4 expert math passes against dequant reference. CPU/GPU quantization and summation can differ; forced token equality is not model-quality proof.

The full oracle exploits finite tape-end knowledge, has no guard tail and cannot establish a deployment bound. Remaining nonlocal work is dominated by victim absence; copied traffic is substantially greater than native adaptation. A practical predictor must learn incoming readiness/lifetime jointly with valuable victim protection and queue cost.

The unchanged Q4/100us serving baseline remains the real-use configuration.
