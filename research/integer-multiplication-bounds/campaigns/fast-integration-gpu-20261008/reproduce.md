# Reproduction

From a clone of hipotures/rad on the GPU research branch, set `CAMPAIGN=research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008`. Python3.11+ and C++17 suffice for the exact producer and assembly paths. Source snapshots are pinned in the scout/graph input manifests; retrieve their GitHub commits via `gh api repos/<owner>/<repo>/tarball/<sha>` into external task-owned storage. Preserve the Apache2 licenses and all inherited notices.

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B "$CAMPAIGN/code/exact_composition.py" --axes "$CAMPAIGN/fixtures/axes-left23-left25.json" --phase "$CAMPAIGN/fixtures/phase-pr36.json" --assembly "$CAMPAIGN/code/adopted_pr37_balanced_assembly.py" --output /tmp/rad-left-composition.json
```

Expected first candidate: a3941743329/10^14, κ3941587961/10^14,47strict constraints and rowdegree2000. This exact representative path was exercised during the campaign. Changed producer reconstruction and separate finite acceptance live in [graph reproduction](agents/graph/reproduce.md); [geometry report](agents/geometry/report.md) identifies geometry tests and negatives.

Optional GPU discovery needs Python3.14.7, CuPy14.2.0, NumPy2.5.3 and a CUDA-compatible NVIDIA driver. Use a task-owned `CUPY_CACHE_DIR`; run `code/gpu_corner_discovery.py --device 0 --seed 2026100800 --seconds 120 --output <fresh-external-dir>` and the corresponding distinct device1 seed2026100801. CPU/GPU integer eliminations agree on the baseline; discovered candidate001 fails an independent second-prime control. Finite-field samples are discovery, not universal rational rank certificates. The campaign stopped this family when information value diminished.

Reports preserve scope and eventual limitations. Completed text evidence is gzip-published before final commit; binary graphs, dependencies, environments and CUDA caches remain external and regenerable. No live service, host configuration or independent CPU campaign is needed.
