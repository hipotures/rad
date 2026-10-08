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

## Accepted finite pair and stronger transfer control

The immutable accepted pair and complete costs are in
`runs/20261008T1854Z-accepted-future-horizon/`; exact word gzip hashes and
independent profile inputs are in its protocol and the preceding exact-pair run.
Use the independent scout recovery commands for a complete replay from archived
words. The root bounded arithmetic reproduction below compares the changed
38-row CPU ledger against the actual rejecting public47 checker.
It deliberately reports an open transfer obligation.

```bash
python3 -B joint-frame/code/check_cpu_transfer.py --native joint-frame/runs/20261008T1854Z-accepted-future-horizon/complete-moment.json --literal-ledger joint-frame/runs/20261008T1854Z-accepted-future-horizon/root-independent-ledger.json --public-assembly work/joint-frame/inputs/pr58-tested-bc2f7ed4c20dc18898305ab17165c0c995cbb804/references/frame-compiler/pr48/research/copied-fixed/balanced_assembly.py --output work/joint-frame/fresh-cpu38-control.json
```

## Global causal region orders

Run one persistent worker with all ten distinct configured schedules; a fresh
output is mandatory. Repeatable `--completed-queue` paths skip exactly completed
configurations during recovery, while original partial outputs remain intact.
Each attempt freezes source, configuration and source-certificate hashes,
recomputes legal future carries, and verifies the entire literal dirty word.

```bash
env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B joint-frame/code/run_region_queue.py --source-root work/joint-frame/inputs/pr58-tested-bc2f7ed4c20dc18898305ab17165c0c995cbb804 --output work/joint-frame/fresh-causal-region-queue
```

The first h23/h25 rank-reversed schedules and recovered rank-pressure variants
were exercised, including full scalar/dirty word checks and controller profiles.
The remaining configured cases run asynchronously; no uncompleted case is
reported as verified. Independent twelve-prime physical/profile review and
complete changed all-size acceptance are required for any new improvement.
