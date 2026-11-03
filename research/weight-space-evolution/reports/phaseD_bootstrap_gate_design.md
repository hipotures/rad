# Phase D — Bootstrap gate design (not executed)

**Gate question.** Can a large parent, using **only direct weight edits**, create at least one variant of a small
Gold language model that **edits other neural networks** more effectively than (a) Gold and (b) appropriate non-agent
baselines, on held-out target networks, at matched resources?

Status: design only. No population, cross-editing or recursive generation is run under this goal. This document is
meant to be pre-registered (frozen in Git) before the next goal executes it.

## 1. Roles and objects

| Object | Definition |
|---|---|
| `E0` (Gold editor) | Small LM, pinned (default: Qwen3.5-0.8B @ `2fc06364…`, the Phase A Gold, already registered read-only). |
| `C_j` (candidate editors) | `E0` + a WSE patch produced by parent session *j*. Patches only; no LoRA/SFT/gradients. |
| Parent | Frontier model session (one per candidate, independent), operating through the WSE lab: weight inspection of `E0`, sandboxed analysis, and a budgeted **editor-evaluation pass** (below). |
| Target network `T` | A small, objectively scored network with a measured deficiency. Targets are benchmark items; they may be created by any recorded means (including ordinary training) — the direct-edit constraint applies to editors and their outputs, not to building the test set. |
| Editor episode | `E` (E0 or C_j) receives a fixed-format description of `T` (+ optional bounded probe results) and must output an edit in the **edit DSL**; the harness applies it to a copy of `T` and scores it. |

The key separation: a candidate's **own task score** (e.g. its MATH-500 or general benchmark score) is *not* the
endpoint. The endpoint is the **change it induces in other networks**.

## 2. Target task matrix

Families (each with many independently generated instances; a family is a defect type × architecture):

| Family | Architecture | Deficiency | Score | Ceiling |
|---|---|---|---|---|
| F1 dead-unit | MLP classifier (synthetic, ~10k params) | k hidden units zeroed/saturated | accuracy | pre-damage accuracy |
| F2 swapped-output | MLP classifier | two output rows/biases swapped | accuracy | pre-damage |
| F3 bias-shift | MLP classifier | one layer's bias shifted | accuracy | pre-damage |
| F4 policy-gap | MinAtar 600-32-32-6 policies (exp5 hand networks, injected-defect variants) | weak behaviour (e.g. never surfaces) | mean score (Phase C evaluator) | best known network |
| F5 algorithmic | 1–2 layer transformer on modular addition/copy | one head/neuron ablated or rotated | exact-match | pre-damage |

Splits (decided before any parent session, by seeded generator, recorded in the input manifest):
- **dev instances** of F1–F4: the parent's editor-evaluation passes use these.
- **held-out instances** of F1–F4: final scoring only (fresh seeds; generated after candidates are frozen, as in
  Phase C `wse.heldout`).
- **held-out family** F5: never seen by any parent; measures transfer.

## 3. Editor protocol (identical for every editor)

- Input: architecture text, tensor shapes, per-tensor statistics, a fixed list of probe results (e.g. per-unit
  activation rates on 64 fixed inputs, confusion summary or episode summary), all as text within a fixed token cap.
- Output: an **edit DSL** block (statements like `W2[:, 17] = 0`, `b3[5] += 0.8`, `swap W3[2,:] W3[4,:]`), with a
  cap on statements and edited entries; parsed and validated by `wse.patch` policy.
- Decoding: fixed sampling, `k` samples per instance (k = 4), seeds fixed per instance; each sample is scored
  independently (no best-of-k selection on test). Forward budget: the editor gets no rollouts (single shot) in the
  first gate; a later variant may give it 1–2 probe passes.
- Three difficulty tiers, so that `E0` has non-zero signal: **T0 select** (pick which of 4 given edits repairs the
  defect), **T1 parameterize** (fill index/value into a given edit template), **T2 free-form** (write the DSL edit).
  A pilot measures `E0` on all tiers first; tiers where `E0` and all baselines are at floor or ceiling are dropped
  before parents start (recorded).

## 4. Measures (per editor × instance × sample)

- `valid`: edit parsed and accepted by policy (reported separately; **format compliance is not editing skill**).
- `Δ = score(T + edit) − score(T)`; `recovery = Δ / (ceiling − score(T))`; `regression = Δ < −ε`.
- Edit size (entries, L2), editor tokens generated, wall time, GPU-seconds.
- Resource-normalized: mean recovery per 1k generated tokens and per GPU-second, and recovery at a matched token cap.

## 5. Baselines

1. `E0` (unedited small model) — the primary comparator.
2. No-op (Δ = 0 by construction; sanity check).
3. **Matched random edits**: same number of entries and L2 as each editor output, random locations (Phase C controls).
4. **Constant-edit baseline**: for each candidate, its most frequent dev edit applied blindly to every held-out
   instance (detects a parent smuggling a fixed "universal patch" into the editor's outputs).
5. **Format-fixed E0**: `E0` with grammar-constrained decoding of the DSL (separates format repair from insight).
6. **Non-agent heuristic repairer** with the same budget: e.g. reset outlier/dead units to layer medians; swap-test
   of output rows; best-of-k random edits chosen on the instance's own dev probes.
7. Upper reference: the parent model itself acting as editor under the same protocol (not a gate criterion).

## 6. Parent process (bootstrap)

- `N` = 4 independent parent sessions (separate conversations, same brief, different session seeds); each produces
  one candidate `C_j`. No specialization is assigned.
- Parent budget per session (to be confirmed with the operator before running): ≤ 30 editor-evaluation passes, each
  = one candidate editor run on ≤ 64 dev instances × 4 samples, returning the §4 metrics only (not the held-out set);
  ≤ 200 sandbox runs; token/cost cap recorded in `configs/` before launch.
- Allowed parent edits: direct numerical edits to `E0` tensors via `wse.patch` (embeddings/LM head/final norm and
  uniform scaling refused, as upstream), no gradients, no fitting of weights to pass results.

## 7. Primary endpoint and decision rule (pre-registered)

- For each `C_j`: paired difference in mean `recovery` vs `E0` over held-out F1–F4 instances (pairing by
  instance × sample seed), with instance-level bootstrap CI.
- **Gate passes** iff at least one `C_j` satisfies all of:
  1. recovery(`C_j`) − recovery(`E0`) > 0 with Holm-corrected p < 0.05 across the `N` candidates;
  2. recovery(`C_j`) exceeds every non-agent baseline (3–6) by a pre-set margin (e.g. 0.05 absolute) at matched
     tokens;
  3. the gain persists when restricted to `valid` outputs (not only a format effect), and the constant-edit
     baseline does not reproduce ≥ 50% of the gain;
  4. no more than a pre-set regression on `E0`'s own general benchmark (secondary safety check, reported separately).
- **Transfer** (secondary): the same comparison on held-out family F5.
- **Specialization** (exploratory, discovered after evaluation): candidate × family interaction in recovery
  (permutation test on held-out instances). A candidate is called specialized only if its family profile differs
  significantly from the others' and from `E0`'s.

## 8. Expected costs (to be re-measured in a pilot)

- `E0` inference: 0.8B on one RTX 4090 with vLLM; an editor run of 256 instances × 4 samples × ≤ 1k tokens is
  minutes. Two GPUs: one serves the editor under test, the other the next candidate (producer/evaluator split).
- Target scoring is CPU-cheap (Phase C: 1,000 Seaquest episodes ≈ 11 s on 4 workers; MLP classifiers ≪ 1 s).
- Dominant cost: the parent sessions (frontier tokens). Record a per-session cap before launching.

## 9. Prerequisites before the gate run

Status 2026-11-03: items 1-3 piloted for F1-F3 ([pilot report](../runs/20261103T-phaseD-pilot-e0/report.md)). Required
revisions before freezing: F1/F2 are solved by a 3-rule heuristic (0.98/1.00 recovery) and must be hardened; T2 is at
floor for E0 (0% valid) and needs format-constrained decoding; thinking mode truncates at 4k tokens; F4/F5 are not yet
implemented. Constrained-decoding follow-up ([report](../runs/20261103T-phaseD-pilot-constrained/report.md)): format fixed,
edits mostly harmful on F1/F2; F3/T2 constrained (E0 0.12, heuristic 0.47, oracle 1.0, 92% valid) is the usable primary
cell so far; T0 needs position balancing (E0 picks D/C in 85% of answers).

1. Implement the target generator (F1–F5) with seeds and a manifest; verify ceilings and defect severities.
2. Implement the edit DSL parser on top of `wse.patch` and the editor-evaluation pass in `wse.lab`.
3. Pilot `E0` and baselines on all tiers (no parent). Freeze tiers and thresholds in Git.
4. Operator approval of parent budgets and provider terms for model-generated edits.

## 10. Lessons carried over from Phases A–C

- p50c shows that a frontier editor can unblock an existing capability of a 0.8B model with a small, mechanistically
  targeted edit, but it is one run per budget, with protocol knowledge; the gate therefore requires several
  independent parents and held-out targets.
- Phase C shows that development feedback in RL-like targets is noisy (Seaquest SD ≈ 40/episode); the gate's
  targets favour low-noise scores (classification accuracy) for the primary endpoint.
- Random matched-size edits are cheap and must be part of every comparison; they can coincide with the edit under
  test for tiny tensors, so control positions exclude the tested edit's own entries.
- Phase C v2: three independent sessions of the same editor model converged on the identical 2-entry edit, which
  had no effect. Several sessions with one brief are not independent searches. The gate needs diverse briefs or
  strategies per parent and must count distinct candidates, not sessions.
- Phase C v2: the one successful edit (+10 held-out) came from a session that rebuilt the environment from the supplied
  source and simulated it, outside the dev-pass budget. A sandbox cannot prevent this once source-level dynamics are
  supplied. Editor protocols must either withhold source-level dynamics or allow self-simulation as an explicit,
  budgeted resource, and must count simulated steps in the resource-normalised measures (section 4).
- Size-matched random edits must be restricted to live weights. Otherwise many controls are no-ops in sparse
  hand-written networks.
- Phase C v3 (preregistered, n = 3 per condition): editors with the environment source and a self-written simulator
  succeeded 3/3 (best +18 points, +35%), prose-only editors 1/3. Executable environment models are the main lever for
  locating failure mechanisms; Phase D editors (and the small Gold editor) should get a budgeted simulator of each
  target task, with simulated steps counted as a resource.
