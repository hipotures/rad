# Reproduction

From a clone of hipotures/rad on the GPU research branch, set `CAMPAIGN=research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008`. Python3.11+ and C++17 suffice for the exact producer and assembly paths. Source snapshots are pinned in the scout/graph input manifests; retrieve their GitHub commits via `gh api repos/<owner>/<repo>/tarball/<sha>` into external task-owned storage. Preserve the Apache2 licenses and all inherited notices.

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B "$CAMPAIGN/code/exact_composition.py" --axes "$CAMPAIGN/fixtures/axes-left23-left25.json" --phase "$CAMPAIGN/fixtures/phase-pr36.json" --assembly "$CAMPAIGN/code/adopted_pr37_balanced_assembly.py" --output /tmp/rad-left-composition.json
```

Expected first candidate: a3941743329/10^14, κ3941587961/10^14,47strict constraints and rowdegree2000. This exact representative path was exercised during the campaign. Changed producer reconstruction and separate finite acceptance live in [graph reproduction](agents/graph/reproduce.md); [geometry report](agents/geometry/report.md) identifies geometry tests and negatives.

Optional GPU discovery needs Python3.14.7, CuPy14.2.0, NumPy2.5.3 and a CUDA-compatible NVIDIA driver. Use a task-owned `CUPY_CACHE_DIR`; run `code/gpu_corner_discovery.py --device 0 --seed 2026100800 --seconds 120 --output <fresh-external-dir>` and the corresponding distinct device1 seed2026100801. CPU/GPU integer eliminations agree on the baseline; discovered candidate001 fails an independent second-prime control. Finite-field samples are discovery, not universal rational rank certificates. The campaign stopped this family when information value diminished.

Reports preserve scope and eventual limitations. Completed text evidence is gzip-published before final commit; binary graphs, dependencies, environments and CUDA caches remain external and regenerable. No live service, host configuration or independent CPU campaign is needed.

The strongest accepted combination as of the ongoing extension uses the freshly optimized original-envelope I+J axis23 and the new negative-basis axis25. Its complete source-family receipt covers all4,073,300 source pairs. Recompute its exact assembly with:

```sh
python3 -B "$CAMPAIGN/code/explicit_profile_composition.py" --axes "$CAMPAIGN/fixtures/best-mixed-negative-axis-profiles.json" --phase "$CAMPAIGN/fixtures/phase-pr36.json" --assembly "$CAMPAIGN/code/adopted_pr37_balanced_assembly.py" --geometry "$CAMPAIGN/agents/geometry/results/fixed23-negative25-data-pairs.json" --output /tmp/rad-best-mixed-negative.json
```

Expected bit saving1031979409/25000000000000, kappa825549449/20000000000000, W177092019 and47strict assembly constraints. The corresponding both-negative family has192,596 exceptions in169 exact profiles; its full heterogeneous assembly is reproduced by adding `--data "$CAMPAIGN/fixtures/both-negative-data-profile.json"`, selecting `fixtures/best-negative-original-axis-profiles.json` and the geometry receipt `agents/geometry/results/both-negative-data-input-audit.json`. It gives the slightly smaller kappa2063858677/50000000000000. Both exact representative assembly paths were exercised. Full producer/matching/local-frame reconstruction is in the graph and geometry reproduction files; independent finite input/rank-product review is in the scout classification review.

Complete selected use maps are gzip-published under `evidence/checkpoint-1457-selected/`. To materialize a specifically named original, decompress its full `<campaign-relative-path>.gz` to a fresh task-owned destination and pass that path to the verifier, or recover its original campaign-relative path when reproducing the historical commands. The manifest records original and compressed hashes. Full completed discovery/control logs and root producer cohorts are retained under `evidence/checkpoint-1504/`; originals remain external. The capacity336-case full payload exceeded the single gzip10MiB limit and was retained externally without splitting; the compact summary and regeneration source remain in Git.

The campaign was extended indefinitely by the user. The original120-minute deadline is a historical scheduling field; ongoing monitors omit their optional `--deadline`. New attempts always use fresh external directories. `code/producer_order_queue.py` runs a bounded worker pool using a pinned PR36 source and compiled binaries regenerated as documented by graph reproduction; exact configurations are under `configs/`. GPU changed-basis discovery accepts explicit source triples and basis modes. Its xorshift zero-state correction prevents an otherwise infinite mutation rejection loop; the interrupted original attempts and repaired distinct source-pair attempts are preserved separately. A finite-field discovery remains separate from a complete conditional construction certificate.
