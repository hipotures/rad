# A bare three-shear exchange cannot exploit the new frame median gap

Status: **SCOPED ANALYTICAL OBSTRUCTION AND EXACT FINITE REPLAY**. This is
a statement about the declared two-role rank metric, not a lower bound for
helper circuits or integer multiplication.

## Fixed endpoints and complete charges

Let the selected coordinate dimension be n, and write G(A) for the
Lagrangian graph of a symmetric binary matrix A. Define

`d(L,M)=n-dim(L intersect M)`.

This is the usual subspace metric restricted to n-dimensional Lagrangians.
For graph frames, `d(G(A),G(B))=rank(A+B)`. The broader Clifford-frame
hypothesis uses this distance as its edge Fourier-rank charge; a paid tape
implementation and the complete native ledger remain separate obligations.

Take a binary norm-one vector u and its rank-one projector P=uu^T. A bare
signed exchange uses three in-place shears on two data roles, with common
frames B1, B2 and B3. Its sources are G(P) and G(0); its physical sinks are
G(I) and G(I+P). Both input and both output continuations are required.
The full proposed rank charge is

```text
d(G(P),B1)+d(G(0),B1)
  +2*d(B1,B2)+2*d(B2,B3)
  +d(B3,G(I))+d(B3,G(I+P)).
```

All Lagrangians are allowed for the common frames, including those outside
the symmetric graph chart. No stationarity or projector condition is imposed
on them.

## Exact minimum for all n

Pair the first source with the opposite sink. The triangle inequality gives

```text
d(G(P),B1)+d(B1,B2)+d(B2,B3)+d(B3,G(I+P)) >= n,
d(G(0),B1)+d(B1,B2)+d(B2,B3)+d(B3,G(I))     >= n.
```

Both right sides are n because the crossed graph differences are I.
Adding the two inequalities proves a lower bound of 2n on the complete
charge. It is attained by B1=B2=G(P) and B3=G(I): the source and sink charges
are each one, and the doubled internal charge is 2(n-1). Thus the exact
minimum is 2n in both the graph and full Lagrangian models.

This analytical result is universal under its declared endpoints and
three-shear word. It does not follow from enumerating a few dimensions.
It also does not exclude a scalar word with branching, helper roles,
different port continuation, or a changed source representation.

## Independent finite evidence

The independently authored [checker](../../code/obstructions/lagrangian_exchange.py)
enumerates isotropic subspaces by extension and binary elimination. It
imports no complex or synthesis implementation. Four worker cases check
dimensions 1, 2 and 3, including the noncoordinate source line u=111.
The complete Lagrangian counts are 3, 15 and 135; the symmetric graph counts
are 2, 8 and 64.

Every first/last common-frame pair is evaluated. The middle frame is
eliminated exactly by the triangle inequality, with B2=B1 attaining the
minimum; it is not omitted as a heuristic restriction. All four cases give
the exact minimum 2n. A claimed saving of one rank is rejected. Dropping one
required output charge admits a smaller cost and is retained as a negative
control showing why that continuation cannot be ignored.

The complete finite operator/routing meaning of Lagrangian edge ranks is
being developed independently by the other tracks. This replay is a metric
certificate, not a fixed-tape compiler or formal proof package.

## Implication and reproduction

The complex track's four-port gate has a real local rank gap between graph
and general Clifford frames. The result here identifies a concrete boundary:
plugging such frames into the bare three-shear two-bank exchange cannot by
itself produce a global rank deficit. A helper or different network structure
must turn the local gap into a complete saving.

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/lagrangian_exchange.py \
  --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/exchange/results.json
```

For bounded CI use `--workers 1 --bounded` without an output. All inputs are
generated deterministically, and only standard-library Python is required.
This proof and checker were prepared with AI assistance. The primary Clifford
quadratic-form context is Dehaene and De Moor,
[arXiv:quant-ph/0304125v1](https://arxiv.org/abs/quant-ph/0304125v1),
18 April 2003. No external novelty or exponent claim is made.
