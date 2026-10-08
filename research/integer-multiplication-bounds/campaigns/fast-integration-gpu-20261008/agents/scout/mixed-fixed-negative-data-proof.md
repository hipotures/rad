# Mixed I+J23 / negative25 complete DATA interface

The [independent audit](gpu-parameter-results/mixed-fixed23-negative25-data-input-audit-20261008T1800.json)
passes for all4,073,300 retained actual source pairs, all47 rational rank cuts
and all22 exact-Q unlucky-field controls. It reuses the campaign geometry
worker's **fresh mixed-family** complete nonvanishing run; it does not reuse
the169 negative×negative classes or replay an unchanged baseline.

The retained inputs are
`../geometry/code/fixed23_negative25_data_pairs.cpp`, SHA256
`5e295eff1ed2388e13a0b3e7caa822031c2694cc198701e2c3487f048ed5e0fb`,
and `../geometry/results/fixed23-negative25-data-pairs.json`.
The audit binds the latter's full hash, the geometry input manifest and the
pinned PR40/PR34 universal-cut source. Its independent implementation is
[retained](code/audit_mixed_fixed_negative_data.py).
The complete native run enumerates lexical combinations23 choose3 times25
choose3, with S varying fastest, and asserts exactly4,073,300 pairs,
191,445,100 nonzero prefixes and346 ordered-zero observations per pair.
4,073,278 pairs succeed wholly at F1000003;22 are replayed wholly at
F2147483647. There are no unresolved pairs. A field is never assembled from
prefixes of different primes.

## Exact source products and actual order

For beta23=-1 (I+J), inverse source coordinate products are18/31 inside T
and-24/5 outside. For beta25=-1/3 (the conjugate negative basis), they are
7/6 inside S and-14 outside. The same products hold for conjugate choices
beta23=5/108 and beta25=1/21 respectively. All four product combinations
therefore give exactly the same normalized DATA matrix. Actual source and
center coordinates and changed local flags remain separately checked basis
interfaces; transposed local flags are not identified with their originals.

The actual first47 left-coordinate labels are
`[0,...,22,22,0,...,22]`; the actual last47 are
`[0,...,22,0,0,...,22]`. Right labels are i mod25 and(528+j) mod25.
These are the inherited PR54 endpoint labels already bound by
[the exact authorized-source compatibility check](pr54-data-basis-compatibility.md).
The normalized corner is

```
M[(r,b),(c,d)] = delta(r,c)*x[r] + delta(b,d)*y[b] -1.
```

It depends only on these actual endpoints and source products. Changing
scalar producer/controller/matching graphs while retaining the complete
triple family and this physical order does not change M. No per-source
basis choice or free gather is introduced. This is the precise reuse gate
for the new public54-derived enlarged graphs.

## Upper ranks are universal rational incidence bounds

Let F and G have49 columns. Each row of F contains a one at its left label,
a one at23 plus its right label, and a one at48; G is defined likewise from
the actual column endpoints. Then, for arbitrary rational coefficients,

```
M = F * diag(x[0],...,x[22],y[0],...,y[24],-1) * transpose(G).
```

For each expected rightmost rook pivot q at row i, James Chang's PR34
coordinate split S proves

```
rank M[:i+1,q+1:] <= rank F[:i+1,S] + rank G[q+1:,complement(S)]
                         <= number of preceding pivots greater than q.
```

The audit independently computes those small incidence ranks over Q at
all47 cuts. This coefficient-free bound supplies universal ordered zeros
for the mixed specialization. The retained full-pair modular witnesses
supply all nonzero ordered prefix minors over Q. Together they force the
same complete rational rook profile for every pair: **nine singletons,
width21, width17, and the unchanged middle width481**.
One data front therefore has histogram1=9N,17=N,21=N,481=N for N=4,073,300.
The two-front construction charges twice this histogram.

The modular ordered-zero observations are not an upper-rank proof. The22
fallbacks are not a universal-zero certificate. No minor CRT product is
needed here because the upper bound is a proved rational factorization and
rank inequality for all weights; it is not a finite-field zero inference.

This DATA audit is complete within its stated retained-run scope. The
compiler, source-frame scalar normalization, paid copy timeline, physical
local profiles, bridge/restriction construction and eventual characteristic
exclusions remain separate composition obligations. No new kappa is claimed
by this note.

Reproduce the bounded audit with Python3 from the repository root:

```sh
python3 research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008/agents/scout/code/audit_mixed_fixed_negative_data.py --pr40-snapshot <immutable-pr40-root> --output <fresh-json>
```

It passed in0.429 seconds in the original audit. The full native mixed
nonvanishing run was performed by the geometry worker and is attributed
there, rather than described as a second scout execution.
