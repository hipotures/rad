# Zero-excess common-frame transport has an orthogonality boundary

Status: **ANALYTICAL SCOPED LEMMA WITH EXACT FINITE CONTROLS**.
No quantitative global rank deficit or multiplication exponent is asserted.

## Contract and question

There is one fixed logical scalar basis of physical banks. Scalar linear gates
mix participating banks at a common actual address frame; every phase transition
has rank equal to the Lagrangian distance. The source bank with odd binary label
t starts at L_span(t) and ends at full. A sink with odd label s starts at zero
and ends at L_(s-perp). Every dirty helper starts at zero and ends at full.
Source/sink anchors and all wire transitions are retained. Independent changes
of virtual address basis, uncharged residual adapters and other endpoint
geometries are outside the statement.

Can a nonzero scalar coefficient travel from t to s when t dot s equals one,
while every wire follows a shortest path between its prescribed endpoints?
The answer is no. This identifies a boundary of the zero-extra-rank strategy,
rather than excluding a circuit with some paid backtracking.

## Geodesic intervals

For any binary subspace E, define L_E={(a+b,b): a in E-perp, b in E} in the
binary symplectic space (z,x). This is Lagrangian even if E is degenerate.
The complex track's [subspace embedding](../complex/degenerate-subspace-clifford-frames.md)
gives d(L_E,L_F)=dim(E)+dim(F)-2dim(E intersect F).

For E0 contained in E1, the entire Lagrangian geodesic interval from L_E0
to L_E1 consists precisely of L_E with E0 contained in E contained in E1.
To see this, the common endpoint intersection is the direct sum of
(E1-perp,0) and {(b,b): b in E0}. Equality in the rank-distance triangle
forces every intermediate Lagrangian to contain that intersection. Quotient
by it. The endpoint spaces become transverse, and equality forces the
intermediate space to split into its intersections with the endpoints.
Isotropy identifies the two components as E-perp and E. Pulling back yields
the claimed nested interval. Conversely the distance formula proves equality.

One can verify the equality step directly: if endpoints A,B intersect in c
dimensions and L has dimension h, let p=dim(A intersect L), q=dim(B intersect L).
Geodesic equality says p+q=h+c. Their common subspace has dimension at most c,
while their sum has dimension at most h. Both bounds must therefore be equal.
Thus A intersect B is contained in L and L splits as the sum of its endpoint
intersections. This uses ordinary subspace identities, not finite enumeration.

Consequently a shortest source path has nested E containing t, a shortest sink
path has nested E contained in s-perp, and a shortest helper path has nested E
between zero and the whole address space. This classification includes all
full Lagrangians on those intervals, not just symmetric projector graphs.

## Transport invariant

For each source t and each bank currently at L_E, maintain the statement:
if the coefficient of that source in the bank is nonzero, then t belongs to E.
It holds initially. A geodesic transition enlarges E, preserving the statement.
At a scalar gate all participating banks have the same E. A linear combination
cannot create a coefficient whose value is zero in every participant.
Cancellations can remove a coefficient but cannot create a forbidden one.
The statement therefore holds after every gate, including inverses and dirty
echoes. At sink s, E is contained in s-perp, so a nonzero coefficient requires
t dot s=0. Arbitrary initial dirty values do not change the source-column proof.

The zero-to-full endpoint capacity for R helpers and v source/sink pairs is
(R+2v)h-2v. A nonzero forbidden coefficient requires some extra rank above
this endpoint bound. The lemma does **not** show that the extra rank is 2v,
that the full stock capacity (R+2v)h is unavoidable, or that each sink requires
its own independent release. Within the L_E chart every closed dimension
backtrack costs an even number of ranks; full off-geodesic Clifford paths
need not obey that restricted parity observation.

The synthesis agent independently reviewed the source/sink classification and
transport induction. It identified why per-output penalties cannot be added:
for three-subset labels, C(T,U)=(|T intersect U|-1)/2 has rank at most h+1
over the rationals, while I-C is supported at orthogonal label pairs. A small
shared central feature bank can therefore contribute to many diagonal entries.
The number of nonzero diagonal entries alone does not bound its paid releases.

## Exact positive and negative controls

The [independent checker](../../code/obstructions/geodesic_transport.py) implements
binary elimination, perpendiculars by bounded enumeration, and all isotropic
Lagrangians by extension. It imports no producer. Complete nested intervals
are checked in dimensions one through three; 32 seeded nested intervals are
checked against all 2,295 Lagrangians in dimension four. Random dyadic scalar
words verify every source coefficient at every intermediate frame. These words
test the necessary invariant; they do not promise dirty restoration.

A separate three-bank exact word does restore arbitrary dirty inputs:
y-=z; z+=x at the source line; move z back to zero; y+=z; move x,z to full;
z-=x. It produces y+=x for an odd self label. Every source, sink and dirty
column is checked. Its single helper decrease is paid: total rank 3h versus
endpoint bound 3h-2. Omitting that decrease would falsely permit the forbidden
flow at zero excess. A direct transfer between orthogonal labels saturates
its two-bank endpoint bound, demonstrating that the condition has a real
positive boundary rather than banning every scalar transfer.

Run the bounded controls with:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/geodesic_transport.py --workers 1 --bounded
```

Full run protocols retain the seed, source hash, independent four-worker cases
and exact outcome. This lemma is not formalized in Lean and has no native tape,
precision or favorable recursive moment attached. The next question is the cost
of a shared nongeodesic release modulo matrices supported on orthogonal pairs.

The first four-worker run passed 82539 complete frame-interval checks,
16 seeded scalar words, and every charged positive/negative control in
2.806 seconds. Its [protocol](../../runs/20261008T232210Z-geodesic-transport/protocol.json)
and [complete result](../../runs/20261008T232210Z-geodesic-transport/results/full.json) retain exact seeds,
counts and source hash. The complex agent independently accepted the full nested-interval argument,
including quotient isotropy and consecutive-path nesting. Its review stresses
that equal Lagrangian labels alone do not authorize mixing different actual
affine/phase gauges. The stated actual-common-frame condition is essential.
Finite checks alone do not prove the all-size statement; the analytical proof
and internal independent reviews are separate evidence.
