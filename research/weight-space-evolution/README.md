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
- Pinned upstream commit: \`4d09ba6d6a7e891dd8063974dfe81b3d78e3494f\`

The first task is to inspect and reproduce the published edit mechanism, then establish a bounded harness and test a small, objectively scorable weight edit using Codex Sol.

All research code, reports and documentation are written in English. Large checkpoints and execution payloads stay outside Git according to the parent repository policy.
