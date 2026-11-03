# Phase D benchmark finalization and persistent weight-swap evaluation: completion report (2026-11-03)

Goal: finalize the Phase D benchmark (Workstream A), build a persistent vLLM evaluator with in-place candidate
transitions (B), and integrate both into a multi-candidate evaluation pipeline (C). Then state readiness for the
four-parent experiment. The four-parent experiment itself was **not** run.

## Completion gates

| gate | status | evidence |
|---|---|---|
| Benchmark executable and justified | **met**. Five families (F1–F3 hardened MLP repair, F4 MinAtar policy repair, F5 algorithmic transformers as transfer family), four tiers (T0 balanced rotations, T1/T2 regex-constrained, T2P with a budgeted probe pass), five baseline kinds. 595 instances; regeneration is byte-identical. Tests: 14 pass. | [pilot report](../runs/20261103T-phaseD-v2-pilot/report.md), `code/wse/pd2_*.py`, `code/tests/test_phaseD_v2.py` |
| Gold, p50c and baselines measured | **met**. Pilot: E0 −0.06, p50c − E0 −0.005 [−0.019, 0.010]. Dev and select: E0 −0.12 / −0.11. Improved heuristic 0.68–0.75; oracle 1.0. | [pilot results](../runs/20261103T-phaseD-v2-pilot/results/editor_results_pilot.json), [e2e](../runs/20261103T-phaseD-v2-e2e/report.md) |
| Splits, tiers and thresholds frozen | **met**. The pre-registered rule was applied mechanically: 15 primary cells, F4/T2 excluded (validity 0.43). Splits: pilot, dev, select public; test and transfer behind a secret salt with a committed sha256; the evaluator refuses held-out splits without `--allow-heldout`. | [protocol_v2_frozen.json](../configs/phaseD_v2/protocol_v2_frozen.json), [manifests](../configs/phaseD_v2/manifests/) |
| Persistent evaluation without restart; transitions and restores pass integrity tests | **met**. Direct and reload are bit-identical to fresh engines on greedy, sampled and constrained cases, over Gold→A→Gold→B→A→Gold sequences and 32 random transitions (20/20 revisits). Full Gold audits pass; memory is constant. Condition: the prefix cache is reset before every batch. | [swap report](../runs/20261103T-persistent-swap-evaluator/report.md) |
| Throughput measured vs restart; two-GPU setup validated | **met**. Full cycle on 13 candidates: direct 3.63/min (109/GPU-h), reload 3.55/min, restart 2.18/min (66/GPU-h). Two GPUs give 1.59× one GPU. | [e2e report](../runs/20261103T-phaseD-v2-e2e/report.md) |
| Integration: registry, multi-candidate, per-family/tier results, rankings, lineage, queue | **met**. Editor registry (`configs/phaseD_v2/editors.json`) with patch lineage (`editor_population.json`). File queue for jobs. Per-cell statistics, a paired primary endpoint with Holm correction, resource-normalized ranking and strengths/weaknesses (`pd2_report`). | `code/wse/pd2_eval.py`, `code/wse/pd2_report.py` |
| Documented and pushed | **met** with this commit. | README, reproduce.md §10, manifests |

## Main findings

1. **Gold has no repair ability on these tasks, and fixed patches do not change that.** E0 is at or below no-op
   in almost every cell; 12 of 16 core pilot cells are flagged as floor cells. None of the 12 fixed patches differs from E0 on the
   select split. p25c looked significant on dev (+0.023, Holm p 0.006) but did not replicate on select (+0.0005).
   This false positive shows that the dev → select → test discipline is needed. Rule for parents: a candidate's
   effect must be confirmed on select before any held-out test.
2. **There is large headroom with non-agent references in place.** The improved probe-search heuristic reaches
   0.35–0.97 per family, and the oracle 1.0. A parent-built candidate must beat E0 and should be compared with the
   improved heuristic at matched probe evaluations; the heuristic uses about 7–20 probe evaluations, the editor in
   T2P uses 1.
3. **Persistent swapping is exact and cheap.** Restart is never needed for correctness. Restart costs 19–28 s per
   candidate; a direct patch costs 0.04–3 s depending on patch density. One sampling-determinism trap was found
   and fixed: vLLM output depends on prefix-cache state. Batch invariance is unavailable for Qwen3.5's GDN
   attention in vLLM 0.33.
4. **The CPU scorer is the next bottleneck.** Two-GPU scaling efficiency is 0.80, with per-job GPU paths and
   scoring both slower under two workers. A third GPU would need scorer capacity: fewer F4 episodes per probe, or
   a dedicated scoring host.

## Readiness for the four-parent experiment

**Verdict: technically ready.** The benchmark, protocol, evaluator and queue are frozen and validated. The
remaining prerequisites are non-technical, plus the operational gaps and rules below.

- **Operator approval** (design §9 item 4): parent budget (sessions, tokens, cost cap), provider terms for
  model-generated edits, and which frontier model and effort level acts as parent. Record these in `configs/`
  before launch.
- **Back up the secret salt** (`work/benchmarks/phaseD-v2/secret_salt.txt`) to private persistent storage. Its loss
  invalidates the committed held-out manifests; see artifact-manifest.json.
- **Parent interface rules:**
  - Parents see dev-split material and the per-cell dev metrics only, through `pd2_eval submit` on `--split dev`.
  - Select is used once per candidate by the operator side for confirmation.
  - Test is used once at the end with `--allow-heldout`.
  - Parents never receive select, test or transfer outputs.
- **Expected cost on the evaluator side:** 4 parents × 30 dev passes ≈ 33 min of 2-GPU time in direct mode. That
  is not limiting; the parent sessions dominate cost.
- **Expected outcome.** Starting from the floor, a credible positive result needs a select-confirmed and
  test-confirmed positive paired difference that exceeds the random-patch null. The random-patch null measured here
  spans about ±0.01 around E0.

## Artifact index

- Code: `code/wse/{pd2_bench,pd2_mlp,pd2_policy,pd2_algo,pd2_scorer,pd2_eval,pd2_report,pd2_throughput,pd2_figures,pd2_freeze,swap_engine,vllm_ext,swap_test,swap_analyze,determinism_probe,editor_population,edit_dsl}.py`;
  scripts `code/scripts/run_{swap_tests,determinism_probe,pd2_workers,pd2_throughput_modes}.sh`.
- Configuration: `configs/phaseD_v2/` (benchmark plan, draft and frozen protocol, manifests, editor registry and
  population).
- Runs: `runs/20261103T-persistent-swap-evaluator/`, `runs/20261103T-phaseD-v2-pilot/`,
  `runs/20261103T-phaseD-v2-e2e/`.
- Row-level evidence: `evidence/20261103T-{persistent-swap-evaluator,phaseD-v2-*}/`.
