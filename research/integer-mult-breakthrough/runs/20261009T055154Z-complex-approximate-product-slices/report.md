# Coefficient-robust product slice controls

Status: **PASS EXACT FINITE CONTROLS**. Four workers verify twelve seeded
Gaussian perturbed slices: packet axes 1, 2, 4 and 6, with each of the two
input families and the output family. Complete matrices reach order 64.
Every perturbed determinant is nonzero, every Gaussian Bareiss division
is exact, and each inverse-error row norm is at most one half. Source
seconds are 0.300480; this is a finite arithmetic checker timing.

The coefficient complex-L1 error is 1/(2D^2). The analytical norm lemma
in the [cross-run report](../../reports/complex/product-slice-wire-boundary.md)
applies to all fixed coefficient errors strictly below 1/D^2. Low-accuracy
zero slices at error 1/D are singular, as required. Finite cases do not
enumerate every perturbation or coordinate. Input-dependent rounding,
shared circuits, record products and native costs remain outside. No kappa
is asserted.

Reproduce with Python standard library:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/approximate_product_slice_floor.py --workers 4
```

The immutable certificate retains every case and exact determinant.
Full matrices regenerate from fixed seeds and local tensor factors. There
are no imports from the earlier producers. Protocol, environment, command
and original source hashes are pinned beside the result; ignored raw
logs/source copies remain immutable.
