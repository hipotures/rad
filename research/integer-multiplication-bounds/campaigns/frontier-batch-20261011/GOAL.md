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

## Follow-up objectives (added 2026-10-11)

4. **Job 4.** Repair replays of the five packages that failed job 2 only
   because their manifests list an absent `.gitattributes`.
5. **Job 5.** After the upstream author retitled #448, #480 and #494 as not
   established, the open frontier without cross-copy moved to nine newer
   packages: #484 and #495-#502. Rerun their authors' verifiers fresh, record
   which complex supplier each claim binds to, and give the agent's post-hoc
   audit the emitted templates. The audit checks the new hosting admissions
   per call: footprint sharing (#471, #498, #500) and pooled cross-replica
   owners (#496, #501, #502).

## Constraints

- Inputs are pinned by commit SHA; open PR heads move every hour.
- No changes to upstream or forks; no publication.
- The conclusions of earlier campaigns are not carried over as assumptions.
