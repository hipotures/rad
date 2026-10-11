# Goal: frontier batch of 2026-10-11

## Brief

The user chose all three directions from the
[mechanism comparison](../../runs/20261011T1945Z-upstream-mechanism-comparison/report.md).
For resource reasons the work runs as an offline batch: the agent writes and
smoke-tests the code; the operator runs each job on the shared host
(16 cores, 160 GB RAM, 2 x RTX 4090) one after another; the agent analyzes the
results only after all jobs have finished. A job that turns out unproductive
still runs to completion, so every job must be designed to finish cleanly,
record per-part failures and use the hardware well: all cores for CPU work,
large batches on GPU. Results stay on the host until the agent decides what to
pack, commit and push.

## Objectives

1. **Cross-copy hosting (#448 lineage).** Decide whether splitting one dirty
   helper residual across two data families is a valid program under the
   templates' own execution model. In that model each register is bound to one
   physical stream, and streams form a direct sum.
2. **Independent replay of the frontier.** Rerun the authors' own verifiers
   for 39 pinned open claims in fresh worktrees and fresh output directories.
   The claims span the E8, whole-residual hosting and cross-copy tiers. Record
   pass/fail, the reported kappa versus the title claim, resources and the
   produced templates for later independent audit.
3. **Lattice screen.** Test whether another root system or lattice line system
   could replace E8 in PR #370's five-stage bit-word template. Use exact
   invariants: n_cent, the deficit, and an upper bound on the saving.

## Completion criteria

- Each job writes a run directory with `protocol.json`, logs and compact
  results under `RAD_WORK_ROOT/runs/`.
- The agent's analysis report states measured outcomes, limits and the
  recommended next step. Evidence is packed with `pack.sh`, committed and
  pushed only after review.

## Constraints

- Inputs are pinned by commit SHA; open PR heads move every hour.
- No changes to upstream or forks; no publication.
- The conclusions of earlier campaigns are not carried over as assumptions.
