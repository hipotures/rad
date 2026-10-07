# Exact tuned composition with retained controllers

The [certificate](results/certificate.json) verifies all primitive logarithm,
balance-root, recurrence, leaf, guard, Gaussian, layout, and absorption
inequalities with exact rational arithmetic. The strongest supplied physical
count is `R=487650`; it supports

```text
kappa=4775622313539/10^30,
kappa/(2^-59)>2.752958831579.
```

This uses the parent branch's separately certified retained-controller
construction, the reviewed weighted and blocked Gaussian transfer, and the
original computational model and upstream assumptions. The primitive savings
are full exact logarithm enclosures rather than rounded decimals. Parameter
tuning is distinguished from the substantive new Gaussian estimates.

The proof and scoped ceiling are in
[downstream-parameter-optimum.md](../../reports/downstream-parameter-optimum.md).
The tested source and exact run settings are in the [protocol](protocol.json).
The strongest parameters approach the stated model ceiling to within roughly
one part per million; this is not an unrestricted optimum or a global novelty
claim. The Gaussian cutoff changes to `b>=2^16777216`.
