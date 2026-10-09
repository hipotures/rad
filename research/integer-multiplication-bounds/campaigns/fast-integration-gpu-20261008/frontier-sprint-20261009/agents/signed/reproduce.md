# Reproduce the signed output-fusion comparison

Prerequisites are Python 3.11 or later, the immutable upstream source snapshot
at `d14e29157bc905be1ced0776dd893d0714013f3a`, the durable exact baseline
checker, and this lane's retained independent rational kernel. No third-party
Python package or GPU is required.
The coordinator acquires the snapshot using GitHub CLI/Git and checks its
pins. Do not infer its head from `git rev-parse` inside an exported directory:
the enclosing RaD checkout is a different repository.

Run from the sprint root. The commands work with another exported snapshot
path when `--tree` is changed. Each output directory must be fresh.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
python3 agents/signed/code/screen_signed_fusion.py \
  --tree work/repos/pr161-d14e291 \
  --exact-audit agents/baseline/code/exact_aliased_core.py \
  --output work/signed/reproduce-unaliased --workers 4

OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
python3 agents/signed/code/screen_signed_fusion.py \
  --tree work/repos/pr161-d14e291 \
  --exact-audit agents/baseline/code/exact_aliased_core.py \
  --output work/signed/reproduce-fresh-physical --workers 4 --fresh-physical

python3 agents/signed/code/enclose_profiles.py \
  --batch work/signed/reproduce-unaliased \
  --interval-code agents/signed/code/interval_moments.py \
  --output work/signed/reproduce-unaliased/exact-intervals.json

python3 agents/signed/code/enclose_profiles.py \
  --batch work/signed/reproduce-fresh-physical \
  --interval-code agents/signed/code/interval_moments.py \
  --output work/signed/reproduce-fresh-physical/exact-intervals.json
```

Both complete four-variant construction paths and both interval-audit paths
were exercised, with a final-source bounded fresh-physical w02 rerun matching
every scientific field. Source corruption and both optimized-mode controls
were also tested. Expected checks: every scalar/geometry/dirty/cleanup check
passes, all four unaliased histograms match exactly, fresh physical programs
have 2,970 late aliases, and all profiles rigorously reject both pinned trial
savings. Numerical roots and exact rational brackets are in `report.md`.
The fresh edge-pair histogram differs from its control by
`{15:+3,16:-3,19:-3,20:+3}`. No final integer multiplication exponent follows.

The driver verifies every pinned source fingerprint and the exact core checker
before executing candidate modules, as well as its w02 control binding.
`input-manifest.json` also records the retained rational kernel's provenance.
Preserve these hashes when reconstructing the input.
The complete raw graph/frame/selection records are ignored execution data;
the coordinator can preserve them as gzip text evidence using the repository
archive tool. The compact results do not claim those raw files are in Git.
