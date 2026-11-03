# Weight-Space Evolution

**Status:** Phase D bootstrap study completed: four frontier-parent sessions, 53 dev passes, four distinct sealed candidates; none improved the frozen test endpoint or showed confirmed transfer.

This directory is the working root for Codex Sol research into **direct weight-space programming** of neural networks and the longer-term possibility of population-based recursive improvement through model-to-model edits.

Start here:
- [Agent instructions](AGENTS.md) — roles, harness requirements, scientific and operational constraints.
- [Current execution goal](GOAL.md) — Phase D parent-to-editor bootstrap; [completed initial brief](reports/initial_goal_completed.md).

## Research questions

1. Can a model-driven editor diagnose and improve a network by directly rewriting a constrained subset of its weights, without gradient-based training?
2. Can a frontier model impart a usable **weight-editing skill** to a much smaller model through edits to that model's weights alone?
3. Do different small candidates develop narrow specializations detectable across independent repair tasks?
4. Can a population of such editors improve its *editing capability* across generations without requiring one general-purpose editor?

Questions 2–4 are hypotheses for later investigation. Do not presume they have been demonstrated.

## Primary evidence

- Article: https://rikiyat.github.io/blog/weight-space-programming/
- Released logs/code/weight patches: https://github.com/RikiyaT/lm_understand-logs
- Pinned upstream commit: `4d09ba6d6a7e891dd8063974dfe81b3d78e3494f`

The first task is to inspect and reproduce the published edit mechanism, then establish a bounded harness and test a small, objectively scorable weight edit using Codex Sol.

All research code, reports and documentation are written in English. All work, including model downloads and experiments, takes place inside this directory. Large checkpoints, dependencies and transient execution payloads live in ignored `work/` here (outside **Git tracking**, not outside the working directory).

## Current state (2026-11-03)

| Phase | Status | Evidence |
|---|---|---|
| A — upstream audit | Done. p10c/p25c/p50c rebuild bit-exactly from public Gold (independent tool + upstream tool agree). p50c is a rank-1 removal of a "loop" direction from 64 MLP columns in layers 15/19; upstream strata indicate it mainly rescues truncated (looping) answers. | [audit](reports/phaseA_upstream_audit.md), [run](runs/20261103T-p50c-reconstruction/report.md) |
| A — behavioural check | Done (bounded): MATH-500 100 problems × 2 samples — Gold 6.5% (95% cut), reconstructed p50c 47.5% (33.5% cut); upstream on the same problems 6.2% / 45.0%, full published 7.9% / 48.1%. Partial reproduction of the published effect. | [run](runs/20261103T-p50c-math500-bounded-r2/report.md) (first attempt [interrupted](runs/20261103T-p50c-math500-bounded/report.md)) |
| B — harness | Done: read-only Gold registry, content-addressed validated patches with lineage, bubblewrap sandbox (fail-closed self-test), budgeted lab, MinAtar forward-pass service (validated vs published exp5 scores), held-out verifier with matched (active-weight) controls, joint multi-candidate comparison; 17 tests. | [`code/wse/`](code/wse/), [validation](runs/20261103T-minatar-evaluator-validation/report.md) |
| C — bounded edits (v1) | Ran end to end. Submitted 2-entry edit: held-out +1.83 ± 1.89 (1,000 ep.), re-verified −2.97 ± 1.32 (2,000 ep., active controls). **No improvement.** | [report](runs/20261103T-phaseC-seaquest-v1-e1/report.md), [re-verification](runs/20261103T-phaseC-seaquest-v1-e1-activecontrols/report.md) |
| C — bounded edits (v2, 3 sessions) | Two sessions converged on v1's 2-entry edit again (held-out +0.19, −0.65; no effect). Session e3 submitted a 146-entry edit (stronger "hunting" + diver-attraction gating): **held-out +9.90 [7.45, 12.49]**, joint 4,000-episode test +10.93 ± 0.95 (Holm p ≈ 5e−30), far above size-matched random edits. **Protocol deviation:** e3 re-implemented the game from the supplied source inside the sandbox and selected among ~8 variants with it. Post-hoc ablation: both components help (+4.4, +5.8). | [report](runs/20261103T-phaseC-seaquest-v2/report.md) |
| C — v3: environment model S vs N (preregistered, 3+3 sessions) | Source + self-simulation (S): **3/3 sessions succeed** on held-out (+18.97 [16.7, 21.3], +4.07, +3.96); prose rules only (N): 1/3 (+4.54 [2.4, 6.6]; others +0.77, +0.12). Joint 4,000-episode test: best edit (42 entries, sticky-action lookahead veto) +18.2 ± 0.9, Gold 53 → 71. n = 3 per condition: descriptive (Fisher p = 0.2). Sandbox CPU-limit bug found (≈ 31 s effective) and fixed after the round. | [report](runs/20261103T-phaseC-seaquest-v3/report.md) |
| D — bootstrap gate | Designed, gate not executed. **Pilot done** (prerequisites 1–3, no parents): target generator F1–F3, edit DSL, tiers T0–T2. E0 (Qwen3.5-0.8B) is at floor on free-form editing (T2: 0% valid) and only above chance on F3/T0 (+0.37 vs +0.05); thinking mode truncates 100% at 4k tokens. p50c raises answer availability in thinking mode (truncation 87.5%) but not edit quality. A 3-rule heuristic solves F1/F2 (0.98/1.00), so they must be hardened before a gate run. With grammar-constrained decoding outputs become valid (≥ 88% on T2) but mostly harmful on F1/F2; F3 is the only family with E0 signal (T0 +0.41, T2 +0.12 [0.04, 0.20]). | [design](reports/phaseD_bootstrap_gate_design.md), [pilot](runs/20261103T-phaseD-pilot-e0/report.md), [constrained](runs/20261103T-phaseD-pilot-constrained/report.md) |
| Infra — vLLM 32K tuning | Done (2026-11-03): offline `LLM` benchmark of Qwen3.5-0.8B BF16 on 2× RTX 4090 (tensor-unlocked), 47 engine configurations, workloads A–F + exact Phase D pilot (reproduced bit-for-bit). Defaults are near-optimal (async scheduling, full CUDA graphs and prefix caching are the big levers and are on by default). Semantics-preserving tuning: FlashInfer attention + `max_num_seqs` ≥ 576 gives Phase D editor +7–16%, 32K single request +2%; FP8 KV +27–43% batched 32K throughput but changes outputs; MTP and TP=2 slower. In-place `reload_weights` swaps candidates in 0.2 s (vs 19–27 s restart), bit-exact. Opt-in profiles; defaults unchanged. | [report](runs/20261103T-vllm-perf-32k/report.md), [profiles](configs/vllm_perf/profiles/) |
| D — benchmark v2 (frozen) | Done (2026-11-03). F1–F3 hardened (simple heuristic 0.22–0.35, was 0.98–1.00), F4 MinAtar policy repair, F5 algorithmic transformers (transfer family); tiers T0 (4 balanced rotations), T1/T2 (regex-constrained), T2P (one probe pass); no-op / matched-random / simple / improved-heuristic / oracle baselines; dev/select public, test/transfer behind a committed secret salt. Pilot: E0 −0.06, p50c − E0 −0.005 [−0.019, 0.010]; T0 position bias neutralised. Pre-registered rule froze 15 primary cells (F4/T2 excluded, validity 0.43). | [pilot](runs/20261103T-phaseD-v2-pilot/report.md), [frozen protocol](configs/phaseD_v2/protocol_v2_frozen.json) |
| Infra — persistent swap evaluator | Done. One vLLM engine per GPU, candidates applied by sparse direct patching (hash-verified, rollback) or `reload_weights`; outputs bit-identical to fresh engines on greedy/sampled/constrained over long random transition sequences (prefix cache reset before every batch is required). Transition 0.09 s direct / 0.25 s reload vs 19–28 s restart. Full cycle, 13 candidates: direct 3.63/min, reload 3.55/min, restart 2.18/min; 2 GPUs = 1.59× one GPU. | [swap tests](runs/20261103T-persistent-swap-evaluator/report.md), [e2e](runs/20261103T-phaseD-v2-e2e/report.md) |
| D — fixed-patch population as editors | 12 fixed patches (upstream + random controls) vs Gold on dev and select: no confirmed effect. p25c +0.023 on dev (Holm p 0.006) did **not** replicate on select (+0.0005) — a false positive caught by the split discipline. | [e2e](runs/20261103T-phaseD-v2-e2e/report.md), [readiness](reports/phaseD_v2_readiness.md) |

Goal summary (completion criteria, reproduced vs untested): [reports/summary.md](reports/summary.md).

Reproduction: [reproduce.md](reproduce.md); inputs/artifacts: [input-manifest.json](input-manifest.json),
[artifact-manifest.json](artifact-manifest.json). Payloads live in the ignored `work/` directory.

**Phase D result:** the completed [parent-to-editor bootstrap study](runs/20261103T-phaseD-bootstrap-execution/report.md)
found no confirmed gain from four independent gpt-6.1-sol / medium parents. The best test delta was +0.004645
[−0.001639, +0.011901], Holm p 0.748. None of the four test confidence intervals excluded zero; transfer also
showed no confirmed improvement. This is a bounded negative result, not a general impossibility claim.

## Completed Phase D execution

- [Final report](runs/20261103T-phaseD-bootstrap-execution/report.md), [complete per-domain analysis](runs/20261103T-phaseD-bootstrap-execution/results/final_analysis.json), [parent reports](runs/20261103T-phaseD-bootstrap-execution/parent_reports/).
- [Execution goal](GOAL.md), [four session specifications](configs/phaseD_bootstrap/sessions.json), [configuration and authorization](configs/phaseD_bootstrap/budget.json).
- [All 46 proposals and parent tool histories](evidence/20261103T-phaseD-bootstrap-parent-provenance/), [dev rows](evidence/20261103T-phaseD-bootstrap-dev/), [final rows](evidence/20261103T-phaseD-bootstrap-final/).

The frozen benchmark is unchanged. All 46 archived patches were recovered with identical tensor hashes in a
fresh registry. Dev repeats exposed occasional cross-GPU output differences; final primary comparisons used one
GPU and passed a 1,664-sample Gold repeat before held-out scoring. Both GPUs were shut down cleanly. The
held-out salt's private backup location remains an explicit recovery gap.

The next useful investigation is the dev repeat variability and a different bounded parent mechanism, before
any larger population or recursive experiment.
