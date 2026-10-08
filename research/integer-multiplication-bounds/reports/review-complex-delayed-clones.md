# Independent review of delayed binary complex clones

The new **h28, R=88,377** complex side circuit passes independent construction,
phase-transfer and finite-witness review. The changed graph contains 3,932
explicit delayed clones and the supplied feasible plan contains 13,141
retained-controller links. It preserves the accepted D/E scalar correction,
source and target frames, full-bank matching, and exact dirty-scratch
restoration. A strict uniform complex primitive saving is
`4175113646023/10^20`. A final multiplication parameter assembly is a separate
obligation. The later proposal to group an entire residual rank into one
larger child is not used in this acceptance.

The campaign started on 2026-10-07 at 22:25:21 UTC. Its historical deadline
is 2026-10-08 at 08:25:21 UTC; the user extended the same campaign to
10:00 UTC. The original source remains pinned to
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`, and the compact-control source to
`6e564879f51ae16f23d392e9e196c605f36d90df`. This review concerns a new physical
complex circuit, with binary address frames and Gaussian dyadic scalar
payloads. Rational positive-envelope rules are not used for these frames.

## The binary interval criterion and its composition

Let U be contained in V, with both subspaces nondegenerate for the standard
binary dot product. The residual E=V intersect U-perp is nondegenerate and
has projector `P_E=P_V+P_U`. Its characteristic is
`c(E)=P_E 1=c(V)+c(U)`. Since `x dot x=x dot 1` over F2, a nonzero E is
nonalternating exactly when `c(E)` is nonzero. A zero residual is allowed.
Thus the correct admitted-interval predicate is

```text
U contained in V, and either dim U=dim V or c(U) != c(V).
```

This also supplies an exact norm-one witness. Choose an index i with
`c(E)_i=1` and set `w=P_E e_i`. Self-adjointness and idempotence give
`w dot w=(P_E)ii=c(E)_i=1`. The equality between the diagonal and row sum
follows by taking the diagonal of `P_E^2=P_E` in characteristic two. The
characteristic vector itself need not have norm one. The checker covers
693 cases in which a nonzero residual characteristic has norm zero and
still constructs a norm-one projector column.

For U contained in V contained in W, the two successive residuals
`V intersect U-perp` and `W intersect V-perp` are orthogonal and have
disjoint images. Their characteristics therefore cannot cancel unless both
are zero. Consequently **two admitted nested intervals compose to an
admitted interval**. This is stronger than the producer's deliberate choice
not to assume transitivity. It does not make every finer interval valid:
an admitted coarse inclusion may contain an alternating proper increment.
Every actual physical interval remains an independent check.

Reverse complements have exactly the same residual projector:
`P_(U-perp)+P_(V-perp)=P_U+P_V`. The witness, nonalternating condition and
rank are therefore identical in both orientations.

The independent source enumerates every nondegenerate subspace of F2^3,
F2^4 and F2^5, constructing projectors from explicit binary Gram inverses.
It checks 2,139 nested pairs, 9,084 nested triples, 7,720 pairs of admitted
successive increments, and 1,677 explicit norm-one units. Two discriminating
controls are retained. The line on `111` inside F2^3 and the full ambient
space are both nonalternating, but their even-parity residual is alternating.
In F2^4, `U=span(1000)`, `V=span(1000,0011,0101)` and W equal to the full
space give an admitted U-to-W interval and an alternating U-to-V interval.
Thus neither nonalternating endpoint labels nor a single coarse check can
replace the actual chronology.

## Delayed clone capacity and frame proof

An original sum P=A+B has an unused controller capacity and at least two
complete output-controller chains. Move one whole chain to a new identical
sum P'. Insert P' immediately before the moved chain's first gate F and give
P' F's existing frame. Choose an earlier unused Q-controller carrying B.
The unused A-controller at P and this B-controller are retained at P',
adding the two links `P_A -> P'_A` and `Q_B -> P'_B`.

The source scalar coefficients of P' are identical to P. The old P-to-F
interval is admitted, so P's source span is contained in the inherited F
frame. Every later frame on the moved chain contains F. The individual new
Q-to-F and A-to-F intervals are checked. Existing source-child-to-P
increments followed by P-to-F are admitted by the composition lemma above.
Original nodes retain their original frames; a clone's assigned frame is
not equated with the canonical frame of its formal support.

The exact job and link checks enforce a distinct unused capacity for every
provider, at most one retained argument at every scalar gate, a terminating
other argument that supplies its result pivot, and chronological acyclicity.
Moving a whole chain preserves its old links. One clone adds one sum and
two links, giving a one-role saving under `R=c+q-links`. There is no claim
that the supplied plan is optimal.

Designated D/E output frames remain their exact triple target kernels.
An enlarged internal clone cannot feed a narrower terminal frame: every
actual transition is required to be an inclusion. Direct output assignments
are checked separately. All source lines, fresh physical entries, assigned
gate frames, actual retained-controller changes, final complements and
target orthogonality are audited by explicit Gram projectors. This retains
the characteristic-two orthonormal residual interface in the original
complex proof.

## Complete changed-witness checks

The executed independent source is
[review_complex_delayed.py](../code/review_complex_delayed.py), SHA256
`d13b0c233ce830dbafb0cdf944204dbcb5aad53a466b90e0ca4fea0aa45e924a`.
It imports neither the new cloner nor its selector or closed-form binary
frame predicates. Accepted original logical graph generation is a pinned
input. The checker independently allocates the changed DAG, reads the
3,932 explicit jobs and 13,141 saved links, assigns each first-consumer
frame through an independent Gram implementation, and verifies every new
mapping, descriptor and order identity before compiling the actual plan.
The accepted original physical program is not replayed.

The changed h28 circuit has 94,966 additions, 98,242 logical frames and
6,552 designated outputs. Its complete output support equality checks all
21,464,352 coefficients, including 7,780,500 nonzero coefficients and every
required zero. The physical replay checks 85,101 fresh copies, 94,966
additions, all output coefficients and all copy targets, including 6,691
swapped result pivots. It checks 278,309 actual frame transitions in each
orientation, with 218,176 distinct physical transitions, and supplies a
norm-one witness for every positive residual. The compiled SHA256 is

```text
e7512bae1752999735d0478c295b89dd1d5ddc5b36e9b5de577f66b46598403f
```

The explicit reconstruction artifact's identity is
`b75db80cc0d4e9c4a0a9620a2842a76f9e67cbf227d7448b2c69b80cd9db9336`.
All 3,932 assigned clone frames are equal to their declared original
first-consumer frames. They increase the old local dimension by between
one and 22. Actual role timelines telescope to precisely `hR=2,474,556`
forward phase ranks when their terminal complements are included.

A fresh changed h8 program is checked on its complete **939-coordinate**
Gaussian dyadic basis: both data banks, all 818 side registers and nine
central registers. Forward and inverse identity shears are exact on every
basis coordinate. An independently coded literal shared-bank schedule then
executes all 9,408 invocations, covering 175,616 coordinates per data bank
and 5,186,944 dirty auxiliary coordinates at seed709. It produces the
required data exchange and restores every dirty auxiliary value. The
middle chronology is explicitly reversed and inverted. This supplements
the complete h28 local witness; a whole h28 array of size v^3 is not
claimed to have been materialized.

## Phase, counts and actual scalar guard

Insert the changed cancellation-free side mixer into the accepted transparent
dirty schedule. Its two contributions are `-JLz+JL(z+Vx)=JLVx`; inverse
mixers and source copies restore the arbitrary initial scratch. The central
gather/scatter correction and its scalar signs are unchanged. Tensoring a
local residual witness with the fixed outer norm-one triple lines preserves
that witness. Complementary reverse labels give the identical residual.

The even-ground orthogonal involution and full first/third bank matching
are unchanged. The checker verifies the h28 matching on all 3,276 triples:
2,912 partners have intersection zero and 364 have intersection two. A
coordinate outside the relevant two triple supports gives the joined
norm-one witness. All enlarged local frames remain in the corresponding
outer tensor ambient, so matching does not depend on their being the
formal source-span frames.

The exact recomputed quantities are

```text
v=3276, m=21952, N=35158608576, R=88377
W=2N+2v^2(R+h+1)=1967894720064
L=3v^2(h+1)h=26143580736
D=2N-2L=18030055680
s=Wm-D=43199206864789248.
```

The changed logical additions must appear in the grouped gate bound; using
the reduced role count in their place would be invalid. With c=94,966,

```text
G=3v^2[4(c+v)+4v+4]=13074237304128
E=64(W+m+1)^3=487736851028968488321153678560340410432
2GW^2+4s+4W+4=101262834558282155716282623424898413828
E-depth=386474016470686332604871055135441996604>0.
```

The exact guard inequality holds although the shortcut `G<6W` is false.
With `B=s+E`, the already accepted semantic completed-child guard gives
`C0=32mB^2, C1=1` for the retained individual-rank recursion. All table
constants are fixed finite data. No growing random-access, truncation or
new scalar oracle is introduced.

Independent longer rational logarithm bounds enclose
`-log_m(1-D/(Wm))` and certify the strict saving stated above. The original
complex recursive transfer therefore accepts this physical construction.
Native binary payload adapters, whole-rank grouped children, and their
variable-width recurrence remain separate new proposals.

## Evidence and reproduction

The frozen run is
[20261008T0700Z-review-complex-delayed28](../runs/20261008T0700Z-review-complex-delayed28/report.md),
with the exact command, input/dependency hashes, Python3.14.7 identity,
reservation admission and release in
[protocol.json](../runs/20261008T0700Z-review-complex-delayed28/protocol.json).
The complete compact certificate is
[results/certificate.json](../runs/20261008T0700Z-review-complex-delayed28/results/certificate.json),
SHA256 `67eb3d68e59355861444069f8839706884d5f44cb3e6464c41dd2b1cf6eab854`.
Execution took 23.22 seconds, with 681,404 KiB peak RSS and zero swap.
One owned math slot was released on terminal completion.

The original large producer input and selected-link artifact are immutable
under the campaign work root. Their exact paths, hashes and regeneration
dependencies are recorded in the protocol. In particular the export is
`derived/finite/20261008T065000Z-finite-complex-delayed28-export/certificate.json`,
SHA256 `8b446f3f4fa558887dccd2ac2e712d764fae21b56a2171de8d1a8f93471287ab`.
Run the protocol command from the topic directory with its published source
dependencies and `OPENBLAS_NUM_THREADS=OMP_NUM_THREADS=MKL_NUM_THREADS=1`.
Write to a fresh output path. The exact mathematical certificate is
deterministically regenerable; historical timing and process records are
observational evidence.

Confidence is high for this explicit finite circuit and its retained
individual-child transfer. The result does not establish optimizer
optimality, a standalone complex exponent below the bit-movement exponent,
or the correctness of any later multiplication composition.
