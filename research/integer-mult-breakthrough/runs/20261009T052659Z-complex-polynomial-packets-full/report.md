# Complete negacyclic polynomial product packets

Status: **EXACT FINITE PASS**. Four workers pass four complete polynomial packet tasks. All260 counted endpointreal/imaginary fields and2394 decoded real coefficients agree. Integer products9,9,81,243, maximumwhole operands19,88,246,36 signedbits. The insufficient carryguard negative is rejected. Python integer timings are arithmetic-reference timings, not native tape measurements.

[Protocol](results/protocol.json) preserves actual time, source and command/scope. [Packet analysis](../../reports/complex/partial-product-packet-prefix.md) keeps packetaxes, native selectedwidth, polynomialrecordprecision and all-size transfer separate. No dirtyGaussian word, native orbitlayout or newkappa is certified.

Originalfiles under `work/complex/20261009T052659Z-complex-polynomial-packets-full/` remain unchanged and ignored; they are not claimed in a Gitclone. [Persistence](results/persistence.json) pins recovery.

```sh
python3 -B research/integer-mult-breakthrough/code/complex/partial_polynomial_product_packets.py --workers 1 --bounded
```

Use four workers without `--bounded` for the complete retained finite tasks. Fresh output paths are required.
