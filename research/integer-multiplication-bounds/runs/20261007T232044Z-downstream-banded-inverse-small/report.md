# Reusable banded Gaussian inverse: finite audit

Campaign clock: 2026-10-07 22:25:21 UTC to 2026-10-08 08:25:21 UTC.

128140 exact exponent comparisons, 3 rigorous Gaussian inverse cases, exact band/cyclic/residual checks, signed gap2^-20 test and exact O(p)-precision bounds. Elapsed time: 2.183645147946663 seconds. One CPU worker; 16 GiB configured memory budget.

All acceptance uses exact fractions and rational exponential intervals. Finite work precision is 56–72 bits, not the full asymptotic P=256p. These checks support the written proof and do not establish a complete multiplication machine.

The sharp row bound, factor error proof, prime/guard replacements and exact composition are in [the cross-run report](../../reports/downstream-reusable-banded-inverse.md). The full transfer is submitted for independent review.

```sh
python3 -B research/integer-multiplication-bounds/code/downstream_banded_inverse.py --upstream /srv/ai/work/rad/integer-multiplication-bounds/20261007T222521Z/repos/upstream-reference --skip-large --output research/integer-multiplication-bounds/runs/20261007T232044Z-downstream-banded-inverse-small/results/certificate.json
```

Independent follow-up review passed the full analytic transfer and exact assembly. See [the review](../../reports/review-reusable-banded-inverse.md). The preserved candidate JSON retains its generation-time pending-review status.
