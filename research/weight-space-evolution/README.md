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

## Current state (2026-11-03, interrupted by a host restart)

- Phase A: [audit](reports/phaseA_upstream_audit.md); p10c/p25c/p50c rebuild bit-exactly ([run](runs/20261103T-p50c-reconstruction/report.md)).
- Phase B: harness in [`code/wse/`](code/wse/) (14 tests pass); MinAtar evaluator validated against published exp5 scores ([run](runs/20261103T-minatar-evaluator-validation/report.md)).
- Phase C: editor session `phaseC-seaquest-v1-e1` was in progress (2 of 6 dev passes, 1 candidate, not submitted) when the host was restarted; its lab state and log persist in `work/sessions/`, but the editor conversation is lost. Not yet evaluated.
- Bounded MATH-500 check of Gold vs p50c (`code/scripts/run_p50c_math500_bounded.sh`) was interrupted before writing results; must be re-run.
- Phase D: [bootstrap gate design](reports/phaseD_bootstrap_gate_design.md) (not executed).
- Reproduction: [reproduce.md](reproduce.md); inputs/artifacts: [input-manifest.json](input-manifest.json), [artifact-manifest.json](artifact-manifest.json). Payloads live in ignored `work/`.
