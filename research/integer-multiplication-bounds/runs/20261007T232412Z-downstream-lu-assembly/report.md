# Exact reusable-LU assembly candidates

Campaign clock: 2026-10-07 22:25:21 UTC to 2026-10-08 08:25:21 UTC.

All three exact composed candidates passed the seven-margin, strict recurrence, primitive logarithm, guard, scaling, Gaussian and replacement-prime constraints. The full analytic transfer remains conditional on the written proof and independent review, plus the unchanged upstream assumptions and separate finite circuit certificates.

- Physical side roles 509194: kappa 366204013939/62500000000000000000000000000; ratio to2^-59 at least 3.377635861948.
- Physical side roles 494250: kappa 6204988737403/1000000000000000000000000000000; ratio to2^-59 at least 3.576932475597.
- Physical side roles 487650: kappa 636749338179/100000000000000000000000000000; ratio to2^-59 at least 3.670610025153.

Elapsed time: 0.15500441507901996 seconds. One CPU worker.

[Full proof and reproduction](../../reports/downstream-reusable-banded-inverse.md).

```sh
python3 -B research/integer-multiplication-bounds/code/downstream_lu_assembly.py --upstream /srv/ai/work/rad/integer-multiplication-bounds/20261007T222521Z/repos/upstream-reference --roles 509194 494250 487650 --output research/integer-multiplication-bounds/runs/20261007T232412Z-downstream-lu-assembly/results/certificate.json
```

Independent follow-up review passed the full analytic transfer and exact assembly. See [the review](../../reports/review-reusable-banded-inverse.md). The preserved candidate JSON retains its generation-time pending-review status.
