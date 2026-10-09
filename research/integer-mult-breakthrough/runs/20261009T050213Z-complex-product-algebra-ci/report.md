# Bounded product controls and source recovery

Status: **EXACT FINITE PASS**. The current partial-product and dyadic-quotient bounded entrypoints pass with one worker. Isolated git apply --unidiff-zero recovers SHA35067f7e5d408009ba931ba0a2a1cf519bf402d70974000c9b4e463b22ebff4f exactly, and the original source bounded entrypoint also passes. Current source hashes are unchanged.

The immutable [protocol](results/protocol.json) pins actual launch time, command, source and scope. The [certificate](results/certificate.json) is a complete copy of the retained compact certificate; no rows in that certificate were omitted. Ancillary per-case calculations which the source did not serialize are reproducible from the deterministic generator, not claimed to be retained raw data. [Cross-run analysis](../../reports/complex/partial-gaussian-product-fusion.md) separates finite arithmetic and analytical deductions from native and exponent obligations.

Original execution files remain unchanged under `work/complex/20261009T050213Z-complex-product-algebra-ci/`; that ignored local directory is not promised in a Git clone. [Persistence](results/persistence.json) records identities and recovery. No external dependency or downloaded input is needed for these controls. Each new execution must use a fresh optional output filename.

Bounded CI reproduction:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/partial_kernel_product_algebra.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/dyadic_quotient_channel_capacity.py --workers 1 --bounded
```
