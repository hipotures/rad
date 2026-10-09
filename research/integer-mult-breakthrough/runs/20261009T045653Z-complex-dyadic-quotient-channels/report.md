# Exact dyadic quotient channel discriminator

Status: **EXACT FINITE PASS**. Four workers pass14 tasks:19530 complete monic-polynomial decisions,185 CRT idempotent pairs,4680 direct reduced Gaussian product coefficients and1620 denominator controls. The complete coefficient degree floor is analytical; no native time or exponent is certified.

The immutable [protocol](results/protocol.json) pins actual launch time, command, source and scope. The [certificate](results/certificate.json) is a complete copy of the retained compact certificate; no rows in that certificate were omitted. Ancillary per-case calculations which the source did not serialize are reproducible from the deterministic generator, not claimed to be retained raw data. [Cross-run analysis](../../reports/complex/dyadic-quotient-channel-volume.md) separates finite arithmetic and analytical deductions from native and exponent obligations.

Original execution files remain unchanged under `work/complex/20261009T045653Z-complex-dyadic-quotient-channels/`; that ignored local directory is not promised in a Git clone. [Persistence](results/persistence.json) records identities and recovery. No external dependency or downloaded input is needed for these controls. Each new execution must use a fresh optional output filename.

```sh
python3 -B research/integer-mult-breakthrough/code/complex/dyadic_quotient_channel_capacity.py --workers 1 --bounded
```
