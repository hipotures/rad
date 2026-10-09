# Exact real half-volume extension

Status: **EXACT FINITE PASS**. The original tensor controls and new pack/transform/product/inverse/unpack all agree for f=1,2,4,6. 1204 counted Gaussian component fields pass, with1,2,8,32 packed Gaussian products. Packed inputs span arbitrary Gaussian fields, so this does not permit repeated free real restriction.

The immutable [protocol](results/protocol.json) pins actual launch time, command, source and scope. The [certificate](results/certificate.json) is a complete copy of the retained compact certificate; no rows in that certificate were omitted. Ancillary per-case calculations which the source did not serialize are reproducible from the deterministic generator, not claimed to be retained raw data. [Cross-run analysis](../../reports/complex/partial-gaussian-product-fusion.md) separates finite arithmetic and analytical deductions from native and exponent obligations.

Original execution files remain unchanged under `work/complex/20261009T043835Z-complex-real-partial-product/`; that ignored local directory is not promised in a Git clone. [Persistence](results/persistence.json) records identities and recovery. No external dependency or downloaded input is needed for these controls. Each new execution must use a fresh optional output filename.

```sh
python3 -B research/integer-mult-breakthrough/code/complex/partial_kernel_product_algebra.py --workers 1 --bounded
```
