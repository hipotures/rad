# Goal: Establish the Weight-Space Evolution Research Laboratory

## Mission

Build a reproducible, executable research environment for **direct neural-network weight programming**, using **Codex Sol** as the initially available model-driven investigator and weight editor.

The long-term hypothesis is that a frontier-model parent might directly edit the weights of small (e.g. 0.8B) language models so that they become specialized **editors of other neural networks**, and that a diverse population of such editors might improve itself through cross-editing and selection. This is not an established result.

The **current task is an initial laboratory and feasibility study**, not a claim of bootstrapped or recursive self-improvement.

## Required context

Read local \`AGENTS.md\`, \`README.md\`, and applicable parent-repository instructions. Work from the current directory; do not assume a fixed local path.

Primary research article:
https://rikiyat.github.io/blog/weight-space-programming/

Upstream public artifacts:
https://github.com/RikiyaT/lm_understand-logs

Pin the upstream source to commit:
\`4d09ba6d6a7e891dd8063974dfe81b3d78e3494f\`

Priority source material:
- \`exp8_math/\` — Qwen3.5-0.8B Gold, p50c weight patch, reconstruction scripts, test conditions and full interaction logs
- \`exp4_fix_car/\` — one-shot weight repair on a small network
- \`exp5_write_from_scratch/\` — generating small network weights
- \`exp6_go_from_scratch/\` — constrained direct edits with feedback
- \`harness/\` — example sandbox and model-facing Codex setup

The original repo contains scripts and experimental records, but **not** the complete live server/harness for Experiment 8.

## Explicitly out of scope

- LoRA, QLoRA, fine-tuning, SFT, gradient descent, backward passes, optimizer-based training.
- Creation of ten 0.8B candidates before the basic laboratory is verified.
- Claims that a small model gained weight-editing expertise merely because its ordinary benchmark scores improved.
- Heavy open-ended paid-model experiments without bounded budgets.
- Building a production MoE/router, JEPA/basal selector, or answer-synthesis system.

## Phase A — Reference and reproducibility audit

1. Inspect the upstream repository at the pinned commit, including license information.
2. Inventory available scripts, datasets, logged interactions, weight diffs, and evaluation code.
3. Review how p50c was proposed, applied, tested and evaluated. Clearly identify what was visible to the editor and what remained held out.
4. Reconstruct the published p50c edit from the pinned Qwen3.5-0.8B public base revision. If weights or hardware are unavailable, provide an executable, verified prerequisite check and document the exact blocker.
5. Check the patch manifest, tensor names, shapes, affected parameter counts and expected hashes. A hash-valid reconstruction is not automatically a reproduced MATH-500 score.

## Phase B — Minimal edit harness

Implement a small, modular harness with:
- read-only Gold registration;
- versioned and validated patch application;
- bounded tensor inspection/edit API;
- isolated sandbox for editor-submitted Python;
- controlled forward-pass/evaluation API with explicit budgets;
- provenance and candidate-lineage manifests;
- unbiased baseline-versus-candidate test comparisons;
- development/test separation and clear controls.

Build only what is needed to execute a first controlled experiment. Avoid unnecessary frameworks.

## Phase C — First executable experiment

Use a small, objectively evaluated network (prefer a well-documented upstream example where practical).

- Record baseline behavior and define the defect or improvement objective.
- Give Codex Sol a **bounded** opportunity to inspect permitted weights, propose a direct numerical edit, and observe development-feedback results.
- Apply the proposal only to a candidate, never to Gold.
- Evaluate success against unchanged Gold and at least one naive or random edit control on independent cases.
- Record measured quality, patch size, resource use, tool/forward-pass count, failures, and remaining uncertainty.
- If model calls or evaluation facilities cannot be exercised, run the non-model portions and document the exact unverified components.

## Phase D — Design the bootstrap gate (no population run yet)

Specify the first falsifiable study for the next goal:

Can a large parent using **only direct weight edits** create at least one variant of a small Gold language model that edits *other neural networks* more effectively than Gold and appropriate non-agent baselines?

Design it to compare several independently generated candidates on a task matrix and identify *measured* specializations after evaluation, rather than imposing them in advance. Plan for later cross-editing/recursive comparison only if this bootstrap gate passes.

Crucially, distinguish **the target task score** from **the editor's ability to improve target models**. Use held-out target models/problems and explicit resource-normalized measures.

## Deliverables

Within this topic directory, produce and maintain as appropriate:
- \`README.md\` — research index/current state
- \`GOAL.md\` — this mission, updated only to reflect genuine changes in scope
- \`reproduce.md\` — precise acquisition/setup/run/recovery commands
- \`code/\` — working authored harness, tests and utilities
- \`configs/\` — pinned settings/budgets
- \`input-manifest.json\` and \`artifact-manifest.json\` when relevant
- \`runs/<id>/\` — compact protocol, metrics and a report
- \`reports/\` — cross-run findings and next-step recommendation

Use English for all artifacts. Put large checkpoints, source clones, caches, datasets, environments and raw logs outside Git in storage discovered from this machine and recorded in the manifest, without hard-coding an absolute path into project instructions.

Carry out meaningful implementation and verification in this session. If a phase is blocked, preserve its exact status and proceed with feasible work. Persist resulting source, methodology and compact evidence using the normal repository commit/push workflow.

## Completion criteria

Success for this initial goal requires:
1. A verified upstream audit and pinned provenance.
2. A functioning minimal patch/harness flow with tests.
3. At least one executed bounded validation case, or a precise, reproducible external blocker.
4. A factual report distinguishing reproduced results, partial reproductions and untested hypotheses.
5. Durable committed and pushed source, results and reproduction instructions.
