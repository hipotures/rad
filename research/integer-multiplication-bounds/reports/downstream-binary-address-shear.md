# Alternate binary address-shear interface and a naive recursive negative

Campaign `20261007T222521Z`, immutable start/deadline
`2026-10-07T22:25:21Z` / `2026-10-08T08:25:21Z`.

This is a new representation of the reviewed Gaussian-scalar/binary-label
complex network, considered as a possible route to cheaper movement. It
does not supply an improved movement algorithm or kappa. The original
reviewed source and runs remain unchanged.

For a nondegenerate binary label U, let P_U be its orthogonal projector
and define the address permutation on two binary vector banks

```
D_U(xi,upsilon) = (xi, upsilon+P_U*xi).
```

These lower-triangular shears are involutions and commute. If V=U
perpendicular E, then `D_V D_U^-1=D_E`. They act independently on each
of f address columns. The Gaussian scalar gates still commute with a
common address permutation on all touched roles, so the unchanged
common-frame telescoping lemma applies to this representation.

At a data X source the label is its norm-one tensor triple line U_a;
at its corresponding Y sink the label is U_a^perp. Since
`P_(U_a^perp)+P_(U_a)=I`, their endpoint product is D_F. The other bank
and all auxiliary roles have endpoints 0/F and also give D_F. Undoing
the original signed scalar bank exchange therefore gives full bitwise
XOR of the two address banks on every role, conditional on execution of
the directional residual shears. No weight-modulo-four source signs
are needed for this particular representation.

If a residual E has basis a_i with inverse Gram matrix G^-1, define the
dual vectors b_i by G^-1. Then
`P_E=sum_i a_i*b_i^T`; the corresponding commuting address shears
factor into exactly dim(E) rank-one controlled-XOR factors. A complete
basis adapted to E and E^perp conjugates them to coordinate word-XOR
operations on f-bit banks. This representation even permits an
alternating nondegenerate residual, since it uses dual bases rather than
the orthonormal bases required by the phase interface. The executable
preserves a genuinely alternating rank-two control.

The expensive issue is implementing these binary basis changes. A naive
scheme recursing on word-XOR to perform every basis row addition uses
additional recursive children beyond the residual rank budget. Each
forward invocation has v source-line growth edges; the reversed stage
has at least v. Their rank-one directions are tensor triple indicators
of support 27, so they are not coordinate directions in the standard
address basis. An independent per-edge basis-conjugation compiler must
spend at least one additional recursive basis child for each such edge,
unless it introduces a separate nonrecursive movement method or combines
basis work across edges.

There are at least 3v^3=3N such source-line edges over the full network.
The accepted residual count is `s=Wm-2N+2L`, whose spare is
`D=2N-2L<2N`. Charging even one extra child on each of these 3N edges gives

```
s_new >= s+3N = Wm+N+2L > Wm.
```

With the existing equal-volume row splitter, the normalized recursive
branching is then at least m, so it supplies no sublinear movement
exponent. This is a bounded negative for this naive per-edge recursive
compiler. It is not a lower bound for a jointly amortized basis schedule,
a different scalar/label construction, or another movement algorithm.
The actual basis changes on both address banks usually cost much more
than this deliberately small lower charge.

The exact checker verifies projectors, complementary endpoints, nested
projection differences and rank-one factorizations over binary arithmetic
on 128 independently generated nested-frame cases of dimensions 4/6/8/10,
plus an alternating plane. Matrix identities certify all addresses;
2,048 joint-address vector probes supplement them. The child-budget
inequality is evaluated exactly from the immutable h=50 shared complex
certificate. These controls verify the written algebra, not a complete
new tape procedure or precision transfer.

Source: [downstream_binary_shear_interface.py](../code/downstream_binary_shear_interface.py).
Run: [20261008T010515Z-downstream-binary-shear](../runs/20261008T010515Z-downstream-binary-shear/).
Reproduction uses a fresh output path and the accepted immutable complex
certificate as an explicit input. Source/input hashes and exact command
are retained by its run protocol. No external literature or new download
is needed for this direct consequence of the preserved common-frame
identity. Novelty is unclaimed.
