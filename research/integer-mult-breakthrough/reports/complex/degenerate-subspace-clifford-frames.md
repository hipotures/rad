# Degenerate spans admit shortest-path Clifford helper frames

Status: **EXACT MATHEMATICAL LEMMA AND INDEPENDENTLY REVIEWED FINITE PHYSICAL COMPONENT**.
There is no complete multiplication
motif, new characteristic certificate or exponent claim.

## Subspace embedding and its scope

Use the binary symplectic convention `(z,x)`, with pairing
`z dot x' + x dot z'`. The zero frame is the computational Z subspace;
the full frame is `{(b,b)}`. For ANY subspace E of an n-dimensional binary
ambient space, including a degenerate subspace, define

```text
L_E = {(a+b,b) : a in Eperp, b in E}.
```

The displayed space has dimension n and is isotropic.
Its intersections with the two transverse endpoint spaces have dimensions
`n-dim(E)` and `dim(E)`. For any E,F, direct decomposition in these two
endpoint spaces gives

```text
d(L_E,L_F) = dim(E)+dim(F)-2dim(E intersect F),
d(zero,L_E) = dim(E),   d(L_E,full) = n-dim(E).
```

Consequently nested subspaces give transitions of rank `dim(F)-dim(E)`.
When E is nondegenerate, L_E is the graph of its orthogonal projector.
When E is degenerate, it can have a vertical direction and lies outside
the symmetric graph chart. This changes the phase model explicitly.
The embedding does not assert a rational projector for degenerate E.

If `r=dim(E intersect Eperp)`, then
`dim(L_E intersect L_Eperp)=2r`. Thus complementary labels need not be
transverse. No product identity `F_E F_Eperp=C^tensor n` is assumed.
The literal example below rejects that false identity.

The [geometry checker](../../code/complex/degenerate_frame_geodesics.py)
checks all 256 ordered subspace pairs at n=3, all 4489 at n=4, 4096 seeded
pairs at n=5 and 1024 at n=8. Four workers complete these checks in under
half a second in [the recorded run](../../runs/20261008T223658Z-complex-degenerate-geodesics/).
Seeds, exact commands, source hashes and per-process memory limits are
retained. The mathematical formulas apply beyond these finite cases.

The earlier h=8 weighted-tree witness has source span `[151,87,12]`,
downstream target span `[211,31]` and vector 204 in the old forbidden
intersection. Let H be the target span's perpendicular. Now
`L_zero -> L_U -> L_H -> L_full` has ranks `[3,3,2]`, totaling eight.
The vertical direction `204<<8` is allowed. This removes that witness's
nondegenerate nested-frame obstruction; it does not validate the entire
weighted circuit or improve its expensive role count.

## Complete branching component

Take n=4, source directions 1 and 7, target directions 8 and 14.
Then `U=span(1,7)=[6,1]`, `Uperp=[8,6]` and
`L_U=[96,17,8,6]`. Both U and Uperp have a one-dimensional radical.
Use three auxiliary roles a,b,p and scalar mixers
`a <- a+b`, then `p <- p+a`. Copy the two sources into a,b;
inject a into the first target and p into the second.

The transparent scalar word is

```text
L, -J, L^-1, V, L, J, L^-1, V^-1.
```

It adds the sum of both source values to both targets and restores all
three arbitrary dirty auxiliary values in virtual coordinates. Every
incidence, including retirement of b, is counted:

| Role | Successive transition ranks | Total |
| --- | --- | ---: |
| a | 1,1,0,1,1 | 4 |
| b | 1,1,2 | 4 |
| p | 2,1,1 | 4 |

The twelve ranks equal the helper endpoint capacity `3*n`. Enumerating
ALL 1024 squared choices of symmetric graph frames for the two mixers
gives a minimum of fourteen for the same complete local helper ledger.
This is a branching component, not an isolated gate with omitted outputs.

The [literal implementation](../../code/complex/degenerate_branching_component.py)
chooses

```text
F_U = C_bit0 * (S C S)_bit1 * CNOT_(1->2),
S C S = (1+i)/2 * [[1,1],[1,-1]].
```

In the `i^phase X^x Z^z` convention, the exact inverse Pauli-Z images have labels/phases
`(17,1),(96,0),(6,0),(8,0)` and span L_U.
For a norm-one direction t use
`C_t=((1+i)I+(1-i)X_t)/2`; use `C^tensor4` as the full anchor and
`C^tensor4 C_s^-1` as a target kernel anchor. Initial source arrays are
`C_t x_virtual`, targets are `y_virtual`, and helpers are `z_virtual`.
The early echo uses frame I. The copies use C_t, middle mixers use F_U,
injections use the corresponding target kernel, and cleanup uses the full
anchor. Retired b moves directly from F_U to the full anchor before the
later scalar cleanup consumes it.

The final sources are `C^tensor4 x_virtual`, targets are the kernel
anchor applied to `y_virtual+x0_virtual+x1_virtual`, and helpers are
`C^tensor4 z_virtual`. This is the required phase endpoint restoration,
not unchanged physical auxiliary bytes. Four external source/target
transitions of rank three are separately charged: helper rank twelve
plus external rank twelve. The complementary negative-shear component
swaps physical bits zero and three and uses the same paid schedule.
It is independently specified rather than justified by a false
complementary-frame product.

EACH actual 16-by-16 Gaussian-dyadic edge is reconstructed entry by entry
as retained affine routing, unit quadratic chirps, and exactly one
`C^tensor rank` child. Its actual rank matches the Lagrangian distance.
The maximum rank is three, a strict contraction of this four-slot example.
Four workers in [the literal run](../../runs/20261008T224156Z-complex-degenerate-branching/)
cover one/two columns, one/two-bit chunks and both selected positions.
All four payload fields are transformed over their complete ranges.
There are 43,904 exact forward and undo values. Omitting b's retirement
edge changes the actual dirty cleanup. Seven
[bounded tests](../../code/complex/test_degenerate_frames.py)
also check all 112 physical role/address basis inputs, corrupted chirps
and the shortest-path characterization below.

The transfer track's [independent literal review](../transfers/degenerate-branching-independent-review.md)
imports none of this producer. It reconstructs the complete 112-dimensional
dirty physical operator and its inverse, all fourteen actual phase edges,
the graph minimum fourteen and another 43,904 complete payload values.
Its `i^phase Z^z X^x` convention records phase three on label seventeen;
this equals phase one in the XZ convention above. The signed orientation,
retirement, affine offsets, per-column unit phases and false complementary
product all have discriminating negative controls. This is independent
team review of finite algebra, not external peer review or formal proof.

## Compiler invariant and remaining boundary

Store a role as `F_current * virtual_value`. Before a scalar multi-role
gate, transition every participant by `F_common F_current^-1`.
A pointwise linear scalar gate commutes with the same common address
operator on all participants. This preserves the invariant through an
arbitrary dirty scalar word. Initial and final anchors determine its
physical operator; common frames cancel algebraically between them.
This observation permits independent forward/complementary labels.

Clifford normal-form context is Dehaene and De Moor,
[The Clifford group, stabilizer states, and linear and quadratic operations over GF(2)](https://arxiv.org/abs/quant-ph/0304125v1),
18 April 2003. The retained component is original finite evidence.
Fixed-tape routing, tensor-prefix/suffix embedding, recursive guard
precision and a favorable complete child ledger are separate obligations.

There is also an exact limit on the zero-extra-rank strategy. Every full
Lagrangian on a shortest zero-to-full path is SOME L_E above. Indeed,
equality in the endpoint distance forces
`L=(L intersect zero) directsum (L intersect full)` because the endpoints
are transverse. Isotropy forces the coordinate components to be Eperp,E.
Consecutive such frames preserve shortest-path cost only if E is nested.
Full Clifford frames therefore remove nondegeneracy, but zero-extra helper
paths still require monotone source-span/target-kernel containment at the
specified scalar ports. Changed chronology or paid nonmonotone transitions
are needed when actual cancellations violate it.

## Reproduction

```sh
python3 -B research/integer-mult-breakthrough/code/complex/test_degenerate_frames.py
python3 -B research/integer-mult-breakthrough/code/complex/degenerate_frame_geodesics.py \
  --n 4 --mode exhaustive --output /tmp/fresh-geodesics.json
python3 -B research/integer-mult-breakthrough/code/complex/degenerate_branching_component.py \
  --columns 2 --chunk-width 1 --output /tmp/fresh-degenerate-component.json
```

Only task-owned Python source and the standard library are required.
Use fresh output paths. This report supplies an exact local escape and
its limits; it supplies no new kappa.
