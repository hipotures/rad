# Reproduction

Run from the parent CPU campaign directory. Download the exact public source
URLs in joint-frame/input-manifest.json into a fresh ignored work directory,
verify tar SHA256, extract without changing the immutable originals. Python3
and a C++17 compiler suffice for the initial finite word/profile runs; use
one OpenMP/BLAS thread per worker.

```bash
env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B joint-frame/code/strip_window_family.py --source-root work/joint-frame/inputs/pr58-tested-bc2f7ed4c20dc18898305ab17165c0c995cbb804 --dimension 23 --config joint-frame/configs/strip-window-experiments.json --output work/joint-frame/fresh-strip-h23
```

Repeat with dimension25 and a new output directory. The script recompiles the
unchanged public profile backend, verifies the scalar graph and frame paths,
checks the complete binary word on every source/dirty basis vector in both
orientations, independently reconstructs word transitions, and encloses the
full controller moment with the unchanged opposite PR58 axis. It records the
actual complete wrapped XOR count. Its FINITE PASS is not a full all-size
transfer certificate. Both axis paths are being exercised in actual runs.

Independent public baseline and new-policy recovery commands are maintained
under agents/scout and agents/layout. Baseline inputs stay unchanged; building
public focused scripts requires a fresh writable execution copy. Do not run
the entire inherited repository verification repeatedly. New mechanism
acceptance also requires an independent source/causality/physical-word review
and every all-size transfer charge under agents/inverse.
