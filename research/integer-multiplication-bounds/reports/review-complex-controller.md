# Independent review of nonalternating complex controller reuse

The new h28 complex-controller construction passes independent finite and
transfer review. Its side role count is **92,309**, compared with 97,586
for the same logical D/E graph without retained controllers. All endpoint,
phase, auxiliary-bank and guard interfaces remain valid. A convenient
strict complex primitive saving is **4003/10^11**, above the previously
accepted 3794/10^11. This is a new physical construction; it does not by
itself change a multiplication headline whose complex saving is inactive.
Fresh downstream composition remains a separate obligation.

The campaign started 2026-10-07 22:25:21 UTC. Its historical deadline is
2026-10-08 08:25:21 UTC; the user extended the same campaign to 10:00 UTC.
The original reference remains `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`;
the compact-control reference is `6e564879f51ae16f23d392e9e196c605f36d90df`.

## Exact characteristic criterion

Let U and V be nondegenerate subspaces of the standard binary dot-product
space, with U contained in V. Set E=V intersect U-perp. Orthogonal direct
decomposition gives `P_E=P_V+P_U`. For any vector x over F2,
`x dot x=x dot 1`. Hence E is alternating exactly when
`P_E 1=0`, or equivalently `chi(V)=chi(U)`, where `chi(U)=P_U 1`.

For a nonzero residual, differing characteristics therefore characterize
the existence of an orthonormal residual basis. Choose a coordinate i
where chi(E) is one. The vector `w=P_E e_i` lies in E and has norm one:
idempotence and self-adjointness give
`w dot w=e_i dot P_E e_i=chi(E)_i`. The last identity also follows from
`P_E,ii=sum_j P_E,ij^2=sum_j P_E,ij` in characteristic two. This is an
explicit witness, not a floating rank condition. The reversed inclusion
`V-perp contained in U-perp` has the identical residual E and witness.
Zero residuals are allowed even when distinct frame tags denote the same
subspace.

The independent checker constructs every projector as
`B (B^T B)^-1 B^T` from explicit binary basis columns. It inverts the Gram
matrices by binary elimination and checks range membership, orthogonality
and idempotence on every coordinate column. It imports none of the new
producer's closed-form projector, containment or admissibility functions.
All 63,602 distinct h28 frames receive this generic check, comprising
1,780,856 projector columns. Original node frames are reconstructed from
independent source unions, intersections and designated output targets.
The source lines, orthonormal pair helpers, coordinate subspaces and
triple kernels are unchanged.

An exact negative control at h10 uses the pair helper with anchors {0,1}
and leaves {2,3,4,5,6}, inside the kernel of {7,8,9}. Both spaces are
nondegenerate, of dimensions five and nine, but their residual has
dimension four and is alternating: both characteristics are 127. The
checker rejects this inclusion. A line on {0,1,2} and the one-leaf pair
helper on the same support are accepted as a zero-residual inclusion.
These controls distinguish the new predicate from containment alone and
from an overly strict requirement that characteristics always differ.

## Physical scalar computation and phase transfer

The unchanged fixed-graph flow planner and compiler run under the generic
Gram predicate. They independently recover all 9,918 admissible links,
select 5,277 retained-controller links and reproduce compiled SHA256
`d9fae1f5a927a34822c569cf407efbfc2fabbc39717cef692101ce885d737ce3`.
The matching constraints permit at most one retained argument per gate;
the other argument terminates its chain and supplies the result pivot.
Thus no gate loses a pivot, and chronological controller chains are acyclic.

The independent scalar replay uses disjoint formal coefficient unions,
not characteristic-two cancellation. It checks each physical argument
against its exact original child, permitting the compiler's reversed
pivot choice, then checks every new copy target is zero. It verifies all
7,780,500 nonzero D/E coefficients and all required zeros, 91,034 physical
additions, 89,033 fresh copies and all 6,552 designated outputs. There are
3,854 swapped result pivots. The resulting mixer is a fixed invertible
sequence of ordinary scalar additions and copies over Gaussian dyadics.
The binary field is used for addresses and frames, not for these scalars.

Every touched physical role is checked on the full timeline, including
nonpivot controllers and all copies. Every proper increase, fresh entry
and final complementary frame has an explicit norm-one witness. The
reverse audit starts at every final role, including scratch, and reverses
the stored timeline exactly. It covers 274,377 transitions in each
orientation, with 212,597 distinct physical transitions. Independent
binary elimination additionally checks 256 h28 frame pairs, including
selected links and unrelated pairs, and verifies that forward and
reverse complementary residual spaces agree. This sampled elimination
supplements the complete generic projector audit; it is not the basis
for the complete inclusion claim.

Insert the new middle mixer into the previously reviewed transparent
schedule `L,-J,L^-1,-R0,V,G,R0,L,J,L^-1,-G,-V`. Its contribution is
`-JLz+JL(z+Vx)=JLVx`, while the central increment is `R0Gx`. Reversing
the mixers and source copies restores arbitrary dirty scratch. The
independent complete h8 rational matrix checks all **951 coordinates**,
both data banks, all 830 side registers and all nine central registers,
in both orientations. It checks 7,472 elementary operations. A separate,
independently coded integer schedule executes all 9,408 shared h8
invocations, with seed619, 175,616 coordinates per data bank and 5,262,208
dirty auxiliary coordinates. The reversed and inverted middle chronology
gives `(-Y,X)` and restores every dirty bank; the retained sign correction
gives the required exchange. No whole h28 array of size v^3 is claimed
to have been materialized.

The all-size phase proof follows the accepted common-frame construction.
Tensoring a nonzero local residual with the fixed outer norm-one triple
lines preserves its norm-one witness. New roles enter from the broad base;
retired roles grow to the broad final frame. The reverse invocation uses
complementary labels with the same residual. The original data and central
frames, source and sink weights, phase corrections, and scalar signs are
unchanged. Thus each residual basis vector still contributes exactly one
forward or inverse C-child. Central returns remain the only decreases.

The complete first/third bank matching is also unchanged. Partner flip
pi is an orthogonal involution on triples. Match bank `(A,B)` to
`(B,pi(A))`, preserving every local side and central role index. The joined
labels have dimensions h and m-h, with residual dimension m-2h. A middle
coordinate outside `A union pi(A)` supplies a norm-one tensor witness.
This replaces separate residuals of total length 2(m-h) and removes
exactly m phase ranks and one role per identification. Arbitrary scratch
restoration proves scalar reuse. The h28 involution is checked on all
3,276 triples: 2,912 have intersection zero and 364 intersection two.

## Counts and the corrected gate bound

The independently recomputed h28 quantities are

```text
v = 3276, m = 21952, N = 35158608576, R = 92309
W = 2N+2v^2(R+h+1) = 2052292552128
L = 3v^2(h+1)h = 26143580736
D = 2N-2L = 18030055680
s = Wm-D = 45051908074258176
eta = D/(Wm) = 15/37480688.
```

Retaining physical roles does not reduce the fixed logical node count c.
Four mixer passes use at most `4(c+v)` grouped gates. The two source and
two target groups add `4v`, and four central groups add four. Hence the
valid gate bound is

```text
G = 3v^2[4(c+v)+4v+4] = 12567850311744,
```

using c=91,034 and the original `c+2v=97,586`. Substituting the smaller
R into `4R+4` would be wrong. In particular **G<6W is false** for this
construction. Saved-input evaluation still costs at most `2W^2`
coefficient operations per grouped gate. The exact required depth is

```text
2GW^2+4s+4W+4 = 105869176084512411784870195769346724612
E = 64(W+m+1)^3 = 553219901666280129303891715161764700224
E-depth = 447350725581767717519021519392417975612 > 0.
```

Thus the same additive guard constant E remains valid by its exact gate
bound. The already reviewed semantic completed-child proof applies with
`B=s+E`, `C0=32mB^2` and `C1=1`. Controller reuse changes no completed
child map, truncation boundary, scalar coefficient type, fixed tape model
or growing descriptor interface. All motif tables are fixed finite data.

Longer independent rational logarithm enclosures, using 20 deficit-series
and 48 radix-log terms, prove
`4003/10^11 < -log(1-eta)/log(m)`. The independent interval is strictly
inside the producer's shorter interval. The old complex primitive remains
a valid fallback; no stronger overall kappa is inferred from this result
without recomposing the active margins and cutoffs.

## Evidence and reproduction

[review_complex_controller.py](../code/review_complex_controller.py) has
SHA256 `f3727945664f1ae923b2213892a57200f770df122dce0b97f260fc2a09725a3f`.
The [completed run](../runs/20261008T0415Z-review-complex-controller/)
records exact input/dependency hashes, one-worker admission and release,
seed619 and Python3.14.7. Execution took **25.76 seconds** with **578,416
KiB peak RSS**, no swap, one BLAS/OMP thread, a 16GiB address-space cap and
a 300-second bound. The result SHA256 is
`75da935de23b61947cc96acffb39d2069703644016efb54aa67daf6fd65f896b`.
Full logs remain under the recorded external campaign review log path;
they are not represented as files inside this source tree.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B \
  research/integer-multiplication-bounds/code/review_complex_controller.py \
  --certificates \
  research/integer-multiplication-bounds/runs/20261008T034400Z-finite-complex-reuse-small/results/certificate.json \
  research/integer-multiplication-bounds/runs/20261008T034800Z-finite-complex-reuse28/results/certificate.json \
  --h 8 28 --exchange-h8 --seed 619 --output "$FRESH_RESULT"
```

The [original complex transfer review](review-complex-transfer.md) supplies
the retained tensor/phase/bank argument; the [semantic child review](review-semantic-child-guard.md)
supplies the linear guard estimate. This review replaces their unreused
middle mixer by the independently certified retained-controller program
and replaces the guard's six-W shortcut by the actual-G inequality. It is
a conditional mathematical transfer review with exact finite evidence,
not a formal proof of the complete multiplication machine or a broad
literature novelty claim.
