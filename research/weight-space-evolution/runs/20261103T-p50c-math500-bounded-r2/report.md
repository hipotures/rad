# Bounded MATH-500 check, Gold vs reconstructed p50c — report

**Outcome: the published behaviour change reproduces on a bounded sample.** The checkpoint rebuilt from public Gold
weights plus the released p50c diff behaves like the published p50c, and Gold like the published unedited model.

## Results (100 problems = MATH-500 rows[::5], 2 samples each; upstream numbers on the same 100 problems, 4 samples)

| Model | Ours: accuracy (95% CI) | Upstream, same problems | Upstream, full 500 | Ours: cut at 32,768 | Upstream full: cut | Ours: mean tokens |
|---|---|---|---|---|---|---|
| Gold | **6.5%** (2.5–11.0) | 6.2% (3.0–10.0) | 7.9% | 95.0% | 93.0% | 31,366 |
| p50c | **47.5%** (39.0–56.0) | 45.0% (36.8–53.0) | 48.1% | 33.5% | 33.1% | 23,067 |
| **p50c − Gold** (paired by problem) | **+41.0 pp** (33.0–49.0) | +38.75 pp (31.5–46.0) | +40.2 pp | | | |

- Problem-level agreement with upstream: correlation of per-problem accuracy 0.75 (Gold) and 0.72 (p50c).
- Ours − upstream on the same problems: +0.3 pp (Gold), +2.5 pp (p50c), well inside sampling error.
- p50c: 16 of 200 answers finished without a `\boxed{}` answer; Gold: 0 (its failures are almost all truncations).

## Resources (RTX 4090 × 2, one model per GPU)

| | Gold (GPU0) | p50c (GPU1) |
|---|---|---|
| Generated tokens | 6.27 M | 4.61 M |
| Generation time | 2,129 s | 1,334 s |
| Aggregate decode throughput | 2,947 tok/s | 3,458 tok/s |
| Device memory (nvidia-smi) | 21.9 GiB | 21.9 GiB |
| Mean utilization over the run | 95.9% | 62.0% (idle after p50c finished) |

The per-model GPU split left GPU1 idle for ~13 min. `code/scripts/run_math500_sharded.sh` now splits by problem
(each GPU runs Gold then p50c on its half), so both GPUs carry the same mix; smoke-tested on 5 problems × 256 tokens.

## Interpretation and limitations
- **Measured:** reconstructed p50c ≈ published p50c and Gold ≈ published unedited on this subset; the gain comes with a
  drop in truncation from 95% to 34%, matching the upstream mechanism (loop suppression).
- This is a **reduced-sample partial reproduction** (100/500 problems, 2/4 samples, MATH-500 only); other benchmarks
  (GSM8K, AMC23, ...) were not re-run. Exact token-level reproduction is not expected (vLLM version/batching differ).
- Classification: an edit that unblocks an existing capability of the 0.8B model (see the Phase A audit), not
  evidence of new mathematical capability.

## Evidence
- `results/{gold,p50c}_summary.json`, `results/*_per_problem.json`, `results/comparison_vs_upstream.json`
- Full generated texts, vLLM logs and nvidia-smi samples: `../../evidence/20261103T-p50c-math500-bounded-r2/` (gzip).
