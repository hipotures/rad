# Initial exact partial product tensor

Status: **EXACT FINITE PASS**. The direct signed tensor, literal C/product/inverse word and named three-product recursion agree at f=1,2,4,6. 1032 counted Gaussian component fields pass; exact products3,9,81,729. Real conjugacy and all character rows pass. The half-volume pack was not present in this source version.

The immutable [protocol](results/protocol.json) pins actual launch time, command, source and scope. The [certificate](results/certificate.json) is a complete copy of the retained compact certificate; no rows in that certificate were omitted. Ancillary per-case calculations which the source did not serialize are reproducible from the deterministic generator, not claimed to be retained raw data. [Cross-run analysis](../../reports/complex/partial-gaussian-product-fusion.md) separates finite arithmetic and analytical deductions from native and exponent obligations.

Original execution files remain unchanged under `work/complex/20261009T043532Z-complex-partial-product-first/`; that ignored local directory is not promised in a Git clone. [Persistence](results/persistence.json) records identities and recovery. No external dependency or downloaded input is needed for these controls. Each new execution must use a fresh optional output filename.

This first successful source preceded the real half-volume extension. Apply `fixtures/complex/partial-product-original-recovery.patch` to the current source in an isolated directory to recover its exact bytes. The later bounded recovery run tests both the hash and execution.

```sh
python3 -B research/integer-mult-breakthrough/code/complex/partial_kernel_product_algebra.py --workers 1 --bounded
```
