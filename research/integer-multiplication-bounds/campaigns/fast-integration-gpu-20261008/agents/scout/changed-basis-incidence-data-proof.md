# Complete changed-basis DATA certificates from structural cuts

Four new source-product families at the inherited physical order now have
exact uniform DATA profiles:

| beta23 | beta25 | complete whole-field witnesses at 65521 | at 1000003 | uncovered pairs |
|---|---|---:|---:|---:|
| 1/51 | -1/3 | 4,073,020 | 4,073,280 | 0 |
| 1/51 | -1 | 4,072,946 | 4,073,284 | 0 |
| 5/3 | -1 | 4,073,026 | 4,073,276 | 0 |
| 5/3 | -1/3 | 4,072,972 | 4,073,290 | 0 |

Each row covers all 4,073,300 lexical source pairs. Every successful
whole-field witness supplies all 47 prescribed nonzero ordered prefixes.
The two unsuccessful-index sets are disjoint in each family. Complete
retained pivot/status arrays were independently hashed and checked, not
only their aggregate summaries. Targeted controls independently rebuild
the matrices and elimination over Q and in both fields.

The zero proof is independent of those modular observations. Write

`M=F diag(x_0,...,x_22,y_0,...,y_24,-1) G^T`,

where row `(r,b)` of `F` has ones at coordinates `r`, `23+b` and `48`,
and row `(c,d)` of `G` has ones at `c`, `23+d` and `48`. For each required
pivot `(i,q)`, a fixed coordinate split `A` gives

`rank_Q M[:i+1,q+1:] <= rank_Q F[:i+1,A] + rank_Q G[q+1:,A^c]`,

and the right side is at most the number of earlier required pivots to
the right of `q`. All 47 cuts are recomputed directly over Q in
[the independent auditor](code/audit_basis_full_family_incidence.py).
These inequalities hold for arbitrary rational diagonal weights at the
same actual corner rows and columns. They do not establish nonvanishing
at an arbitrary beta, a fixed pivot sequence after specialization, or a
uniform profile outside the separately covered families.

Combining those upper inequalities with a successful complete prescribed
sequence in at least one denominator-safe prime field establishes the
exact Q rook sequence. Every pair in each listed family therefore has one
front consisting of nine singletons, one width-21 block, one width-17
block and the complementary width-481 block. Both actual DATA fronts
are charged in a complete construction. The one-front histogram is
`{1:9N,17:N,21:N,481:N}`. No large prime-product replay is needed for these
structurally known zero cuts.

The complete receipts are:

- [half23/negative25](gpu-parameter-results/half23-negative25-uniform-data-certificate-20261008T1835.json)
- [half23/I+J25](gpu-parameter-results/half23-fixed25-uniform-data-certificate-20261008T1837.json)
- [5/3 with I+J25](gpu-parameter-results/five3-fixed25-uniform-data-certificate-20261008T1837.json)
- [5/3 with negative25](gpu-parameter-results/five3-negative25-uniform-data-certificate-20261008T1837.json)

The source/center normalization and conjugate-root transfer are bound in
[the interface audit](gpu-parameter-results/new-joint-basis-source-center-interfaces-20261008T1846.json).
The complete common-basis source family and actual physical order must be
preserved or explicitly relabeled by a proven bijection. New local frame
profiles, scalar words, compiler recovery and complete moment/semantic
assembly remain separate gates. These DATA certificates alone claim no
new multiplication bound.
