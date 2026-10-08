# Independent review: two disjoint protected central rows

The two-center construction has a valid all-size bit transfer for h>=4,
h not equal to9 or10. It changes the scalar central basis **over F2
payload**, while rational address projectors are reduced in a separately
chosen admissible odd prime field. These fields cannot be interchanged.
The central rank loss becomes `L=3v²(h²-2)`; all three credited generic
boundary families and the separate complex numerical guard remain unchanged.
A full multiplication parameter composition is a separate boundary.

This review checks the frozen producer
[proof](downstream-two-disjoint-centers.md),
[source](../code/downstream_disjoint_centers.py) and
[certificate](../runs/20261008T083232Z-downstream-disjoint-centers-repair/results/certificate.json).
It imports none of that producer code. Its fresh
[independent source](../code/review_two_disjoint_centers.py) and
[protocol](../runs/20261008T0859Z-review-two-disjoint-centers-admission-repair/protocol.json)
provide separate rational, scalar, sparse native and exact combinatorial
controls. The fresh
[certificate](../runs/20261008T0859Z-review-two-disjoint-centers-admission-repair/results/certificate.json)
is terminal PASS, SHA256
`1d51d8d31e3aa9512d5d06c1faa66fd768f80ae5eef423982ba0a9fdbf32a27a`.
The independently checked construction and all-size transfer are accepted.

## Scalar basis and the two distinct fields

Let Inc be the h-by-v point/triple incidence matrix. Over F2 define T by
the ordered rows

`e0, sum_(j>=1)e_j, e2, ..., e_(h-1)`.

The integer T is unimodular; its inverse replaces the second row by
`e1-sum_(j>=2)e_j`. Let `G'=T Inc`, `R'=Inc^T T^-1`, reducing the scalar
coefficients modulo2. Thus `R'G'=Inc^T Inc` **over F2**. The first gather
row has support on triples containing0. The second has support on triples
excluding0, since a triple has three points and `3=1` in F2. These supports
are disjoint and cover every triple. The remaining point2,...,h-1 rows
touch every triple because no triple fits inside the two-point set{0,1}.

The scatter coefficients at target S are

`[0 in S]C0 + [1 in S]C1 + sum_(j>=2)([j in S] XOR [1 in S])Cj`.

Every center has a nonempty scatter support and every data target receives
at least one center coefficient. Both scatters remain single grouped gates
at their old full common frames. No runtime central/address basis adapter
is inserted: the construction directly uses these new fixed scalar gate
coefficients and orders.

Arbitrary dirty centers are restored by the four scatter/gather operations.
The forward increment is `R'G'X`; reversal of the scalar chronology and
exchange of data banks gives the same symmetric shear. The inverse does
not transpose G' or R'. The unchanged side correction therefore gives the
original identity shear over F2 on arbitrary dirty payload registers.

This disjoint-support program is not an ordinary rational payload identity.
The actual fixed 0/1 G' and R' matrices have diagonal `(R'G')_SS=1` in the
h4 fixture, while the ordinary integer incidence Gram diagonal is3. They
have the same parity. Using T Inc and Inc^T T^-1 over Q would preserve the
integer Gram, but the second gather row would have coefficients2 or3 and
would no longer have the claimed disjoint support. The fresh checker
retains this exact counterexample to the incorrect cross-field claim.

## Rational frames and native chart chronology

Use the original metric `H=I-J/9`. It is nondegenerate for h!=9. The
protected frames are

`E0={x: sum(x)=3x0}`, `E1={x:x0=0}`.

Both have dimension h-1. The relevant source triples lie in their assigned
frame. E0 has norm `sum_(j!=0)x_j²` on its restriction and is positive.
E1 has determinant `(10-h)/9`, so it is nondegenerate for h!=10 and has
one negative direction when h>10. Positivity of E1 is not required by the
rational bit compiler. Replacing this premise by binary orthonormal frame
admissibility would be a different interface.

Exact normal representatives and their H-norms are

`z0=6/(9-h)1-3e0`, `norm(z0)=36/(9-h)`,

`z1=e0+1/(9-h)1`, `norm(z1)=(10-h)/(9-h)`.

With covectors n0=1-3e0 and n1=e0, the normal projectors are
`z_i n_i^T/norm(z_i)`. Their idempotence and H-self-adjointness follow from
`H z_i=n_i` and `n_i^T z_i=norm(z_i)`. A source triple t in E_i has norm2;
its line is nondegenerate. Therefore E_i intersect t^perp and the
corresponding normal inside t^perp are nondegenerate. At h10 the E1 norm
vanishes even though the whole H is nonsingular; that shape is explicitly
excluded. At h9 the ambient metric itself is singular.

The first high gather is split into three groups: row0 at E0, row1 at E1,
then rows2,...,h-1 at F. Each data source participates in exactly one of
the protected groups. Its line is contained in that E_i, followed by F;
no source is forced through the incomparable E0 and E1. The two protected
centers start at the old low frame, pass through their own E_i, return to
the old low scatter frame, and finish at F in the **full late cleanup**.
That late cleanup touches every data source and every center. All original
external frames are therefore retained.

In the reversed middle invocation, the old full low cleanup gather comes
first. Then the high scatter takes every center to F. The protected low
gather is reversed: remaining rows at the old low frame, then row1 at the
normal line E1^perp, then row0 at E0^perp. These normal lines are contained
in the target triple kernels because their corresponding supports remain
disjoint. The last high scatter returns all centers to F. Using E_i in
place of its complementary normal on this reversed path would violate the
required chart and is not the construction.

The original tensor-prefix and future-line spectators multiply these
local frames exactly as in the accepted one-center proof. They add no
dimension factor to the protected rank loss: the active prefix/future
line is rank1. Orthogonal direct sums and tensoring with the fixed
nondegenerate spectators preserve every inclusion and restricted
nondegeneracy. The actual complete late/interstage/terminal frames are
unchanged.

For any fixed D-address fiber, a native chart translates H-addresses by
`P_U D` in the odd field. A grouped scalar operation touches participants
at one common chart and therefore commutes with that common address
permutation. The change-of-chart permutations telescope to the same
boundary-gauged scalar operator. This exact algebra holds for all D fibers
and tensor spectators, beyond the bounded enumerated fixtures. Payload
addition is XOR throughout; rational/odd-field address addition is not
silently interpreted as payload addition.

## Rank, fixed table and compositional boundary

Each protected center loses h-1 active dimensions at its return instead
of h. The other centers lose h. The data paths split monotone increments
without changing their endpoints. Consequently each invocation's old
h² loss becomes h²-2, and globally

`W=2N+2v²(R+h)`, `L_two=3v²(h²-2)`,

`D_two=N-2L_two=D_old+12v²`, `s_two=Wm-D_two`.

W, side-role R and all source corrections are unchanged. Two extra fixed
grouped bit gates per invocation affect the fixed work constant. Their
native edge ranks are already included in the changed telescoped s; they
do not create uncharged additional recurring full-width operations.

The three credited generic families retain the exact old endpoint matrices:
final middle and shared joined banks each have `(R+h)v²` copies with
kernel dimensions h² and2h; the two stage3 data first-edge families have
2N copies with kernel dimension h²+h-1. All new internal center matrices
remain individual-pivot children. The same rational generic-isometry
existence theorem can conjugate every new nondegenerate assigned frame.
The useful flag family and maximum grouped child do not change.

This is a new fixed bit program and native triangular-factor table. A
shared odd prime must avoid the new normal-projector and factor-table
denominators as well as all existing exceptional factors. Existence follows
because the table is fixed and finite, not because the old prime is known
to work. The giant table/prime remain constructively computable eventual
setup. The separate complex scalar program, grouped G, numerical E/C0 and
semantic precision recurrence are unchanged. Any complete h53 whole-complex
composition must still verify its changed rank characteristic, product
row stock, stopping/guard/compact inequalities and final exact kappa.

## A scoped all-size limit on disjoint protected rows

For h>=5, two independent nonzero point-linear F2 gather rows with disjoint
triple supports must be pointwise complements. Therefore three independent
point-linear rows cannot have pairwise-disjoint triple supports.

To prove this, classify each point by the pair `(u_i,v_i)` in
{00,01,10,11}. A triple is forbidden when the XOR of its point types is11.
Three11 points are forbidden. If an11 point exists, two points of any one
other type are forbidden, so each other type occurs at most once and11
occurs at most twice. The triple00,01,10 is also forbidden; hence at most
two other types occur. There are at most four points, contradicting h>=5.
Thus11 is absent. Nonzero independent rows require both01 and10. Their
presence forbids00 by the same triple condition. Every point is01 or10,
which proves `v=1+u`.

A third independent row disjoint from u would have to equal1+u=v, which
is impossible. This obstruction concerns the specific disjoint-support,
point-linear central-basis model. It does not rule out overlapping but
compatible frame chronologies, composite-stage boundaries, extra centers,
or non-point-linear scalar factorizations.

The threshold is sharp. At h4 the four rows `1-e_i` each select exactly
one triple, have disjoint supports, and form an invertible F2 matrix.
Exact exhaustive pair checks at h4 through h9 distinguish this exception
from all h>=5 fixtures.

## Independent evidence and preserved first failure

The successful fresh checker compares complete scalar dirty bases at
h4,6,8,12; exact rational source/normal/projector formulas at
h4,6,8,12,51,53; and sparse native dirty bases at h4 on q7 andq11, two
nonzero D fibers, ordinary and reflected ambient charts, and both physical
orientations. Each native fixture is compared against an independent
boundary-gauged **original incidence Gram** operator. Omitting the second
protected frame transition gives different coordinates in every fixture.
Sparse address samples are reported explicitly and are not described as
full q^h enumeration.

Separately, the frozen producer executes 230,496 complete basis probes
over every q7/h4 H-address, the same two physical orientations and two
ambient charts, with two named nonzero D fibers. Its source was read and
its exact basis/field/chronology coverage checked; that full enumeration
is retained rather than repeated. Neither control enumerates all D fibers
at large h or instantiates the giant generic table. The all-size gauge
identity supplies those mathematical extensions.

The [first independent attempt](../runs/20261008T0854Z-review-two-disjoint-centers/protocol.json)
passed its scalar, rational and native checks but rejected an incorrectly
expected h5 exception in the new disjoint-row theorem. The preserved
[v1 source](../code/review_two_disjoint_centers_v1.py) and full log show that
failure. Accounting for the additional forbidden triple00,01,10 reduces
the possible11-point case from at most five to at most four points. The
fresh repair strengthens the theorem to h>=5 and retains the actual h4
exception; it changes no two-center operator, frame or rank construction.
All attempts retain their original source/input identities and timestamps.

The [first repair admission](../runs/20261008T0857Z-review-two-disjoint-centers-repair/protocol.json)
timed out after180 seconds before launching a scientific child: sixteen
earlier chunk workers were still active. The next attempt waited for its
own distinct slot using the current 085400 checkpoint. It entered at
fourteen active chunk workers and two reserved slots, then released only
its own reservation in a locked finally block. No existing worker was
interrupted or silently oversubscribed.

The frozen successful source SHA256 is
`7fe73fa4d743cbceac744044d093c1f85623bfe26a3d812811196d1f22a6caf9`.
The executed producer source and certificate hashes are
`947a84af79dbf2f7497bbb4fcb32c38e77545473329e748674975f1773557fa3`
and `95e97f9d7a57938dc5ccbea02ce105eb14ffac0f58b9a0e5d2be2f08c1ad77d1`.
The exact producer report reviewed here has SHA256
`9f2438736601b0ae0e0bc69bb352e124d1f3de7fc57f5ac5682f047d05cc7a96`.

Fresh execution passed 3,264 sparse native dirty basis probes across all
named cases and all 630 central-only scalar basis coordinates in each
orientation. The scalar basis size is `2v+h` and excludes all side mixer
scratch; the compound h53 finite review separately exercises complete
dirty invocations including that scratch. Actual execution was
2026-10-08T08:58:51.628000Z through 08:58:52.665404Z, Python3.14.7,
one worker, GNU-time wall0.91 seconds, maximum RSS23,892 KiB and zero swap.
The all-size metric/table setup and a final parameter composition remain
separate from this bounded native proof evidence.
