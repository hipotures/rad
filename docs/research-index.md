# RaD research index

RaD combines the historical benchmark work and later residency investigations.
The [benchmark archive](../benchmarks/README.md) indexes earlier Qwen phases,
runtime/MTP studies, hardware characterization, Strata campaigns and retained
source/configuration/results. The [starter index](../launchers/README.md) links
the user launchers and every preserved 128K laboratory starter. The
[workspace map](workspaces.md) explains original execution paths and Git copies.

The table below covers the residency branch of this wider research record.

The investigation covers expert placement, CPU/GPU coordination and real-copy
scheduling in frozen Strata/Qwen environments. Campaign reports define their
own work, settings and limitations; results from different runtimes or replay
contracts are not interchangeable. Timestamps identify preserved episodes.

All paths below are relative to this repository. Existing campaign files are
imported verbatim. Historical top-level STATUS/report files describe earlier
stages; use the campaign report for the result of a later study.

| Investigation | Record | Role |
|---|---|---|
| Golden Swap Phase 1 | [Report](../iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/report.md), [reproduction](../iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/reproduce.md), [audit](../iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/completion-audit.json) | Latest study: causal victim return risk with oracle incoming; 36 valid main requests, no confirmed latency gain. |
| Golden Swap Phase 0 | [Report](../iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/report.md), [manifest](../iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/benchmark-manifest.json) | Twelve source groups, frozen roles, natural tapes and victim-return labels. |
| Oracle information decomposition | [Report](../iq3s-residency-20261004T230051Z/campaigns/q4-oracle-decomposition-20261006T100032Z/report.md) | Separates incoming and victim information; motivates the return-risk study. |
| Live oracle feasibility | [Report](../iq3s-residency-20261004T230051Z/campaigns/q4-live-oracle-20261006T040656Z/report.md) | Fixed-work live residency schedules and real-copy/fidelity constraints. |
| Conditional admission v3 | [Report](../iq3s-residency-20261004T230051Z/campaigns/q4-conditional-admission-20261006T010859Z/report.md) | Bounded admission/gating and negative timing evidence. |
| Q4 residency v2 | [Report](../iq3s-residency-20261004T230051Z/campaigns/q4-residency-v2-20261005T202441Z/report.md) | Earlier live residency comparison. |
| Pool/runtime follow-up | [Report](../iq3s-residency-20261004T230051Z/campaigns/pool-persistent-20261005T094800Z/report.md) | Pool and persistent-runtime investigation. |
| Q4 multi-GPU baseline | [Report](../iq3s-residency-20261004T230051Z/campaigns/q4-multigpu-20261005T164628Z/report.md) | Preserved Q4 baseline/configuration work. |
| Q4 pool spin | [Report](../iq3s-residency-20261004T230051Z/campaigns/q4-pool-spin-20261005T184831Z/report.md) | Scoped pool-spin measurements. |
| Upstream issue 921 validation | [Report](../iq3s-residency-20261004T230051Z/campaigns/upstream-921-spin-validation-20261006T131023Z/report.md) | Separate upstream runtime validation, not a Phase 1 engine migration. |
| Original IQ3_S laboratory | [Report](../iq3s-residency-20261004T230051Z/report.md), [experiments](../iq3s-residency-20261004T230051Z/experiments.jsonl) | Historical E001–E029 work, controls, failures and bounded follow-ups. |

The [launcher index](../iq3s-residency-20261004T230051Z/launch-index.md)
retains exact serving/replay identities. Launcher availability on this host is
different from a portable clone being immediately runnable: builds, weights and
tapes are intentionally external to Git.

Small configurations and per-request validation/episode records are retained
even when their parent payload directory is otherwise ignored. Raw binary
evidence remains in the [local storage catalog](local-artifacts.json), with
original hash manifests retained in each campaign. Negative results and
unsuccessful bounded versions remain part of the record.
