# Weight-Space Evolution

**Status:** Research laboratory initialized; empirical claims remain unverified in this repository.

This directory is the working root for Codex Sol research into **direct weight-space programming** of neural networks and the longer-term possibility of population-based recursive improvement through model-to-model edits.

Start here:
- [Agent instructions](AGENTS.md) — roles, harness requirements, scientific and operational constraints.
- [Current execution goal](GOAL.md) — the initial laboratory build and controlled reproduction.

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
| D — bootstrap gate | Designed, not executed. | [design](reports/phaseD_bootstrap_gate_design.md) |

Reproduction: [reproduce.md](reproduce.md); inputs/artifacts: [input-manifest.json](input-manifest.json),
[artifact-manifest.json](artifact-manifest.json). Payloads live in the ignored `work/` directory.

**Next useful step:** Phase C v3 with the environment-model question pre-registered: condition S (source supplied,
budgeted self-simulation allowed) vs condition N (prose rules only, no source), 3 sessions each, joint held-out test.
Then implement the Phase D target generator and edit DSL and pilot the small Gold editor. For GPU evaluations use the
problem-sharded launcher (`code/scripts/run_math500_sharded.sh`).
