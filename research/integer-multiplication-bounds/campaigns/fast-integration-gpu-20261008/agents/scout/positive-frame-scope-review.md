# Signed positive-frame projector and exact-profile review

Reviewed 2026-10-08 15:24 UTC. The reviewed native source is
[positive_frame_profiles.cpp](../geometry/code/positive_frame_profiles.cpp),
SHA256 `faf3568d17020f649c02d01bd0cdf3260a7c6a0fa6341bf59654e6af3ec819e1`.
This is an independent algebra, arithmetic and source review. No native
profile sweep or complete Fraction Gram replay was run by the scout.

Let F be the forced coordinates, f=|F|=1 or2, s=3-f. Let a_c be signed
indicator vectors with pairwise disjoint supports outside F, k_c their
positive support sizes and sigma_c their coordinate sums. For
`H=I-J/9`, take basis vectors `B_c=a_c+(sigma_c/s)1_F`. Their Gram matrix is

```
G=diag(k_c)+(f-1)/s^2 * sigma*sigma^T.
```

It is positive definite, including balanced signed classes sigma_c=0.
Consequently the actual space has rank equal to its number of classes.
Put

```
D=sum a_c*a_c^T/k_c,
u=sum sigma_c*a_c/k_c,
v=sum sigma_c^2/k_c,
d=s^2+(f-1)v.
```

Sherman–Morrison inversion of G, followed by `B G^-1 B^T H`, gives the
original orthogonal projector. Conjugation by `L=I-beta J` reorganizes it as

```
P_beta=D+[s*u*z^T+s*w*u^T+v*w*z^T-(f-1)*u*u^T]/d,
w=1_F-3*beta*1,
z=1_F+gamma*1,
gamma=(9*beta-1)/[3(1-h*beta)].
```

This independently reproduces the native negative specialization
`beta=4/[3(h+3)]`, with `w=1_F-4*1/(h+3), z=1_F+1`, and its I+J
specialization beta=-1. The f3 source-line case is treated separately and
matches the previously reviewed rank-one formula. Zero and identity have
their explicit separate native matrices.

For K=lcm(k_c), the native u array is K*u, vn is K*v, and
`dnum=s^2*K+(f-1)*vn=K*d`. Clearing negative denominator
`(h+3)*K*dnum` multiplies every term, including the rational block D,
correctly. The I+J denominator is `3(h+1)*K*dnum`. The gcd reduction over
every numerator and the denominator changes no rational matrix.

The native code deliberately uses a full integer difference and its exact
entry maximum Z. D is a rational signed block projector, so the original
diagonal-mask correction-rank shortcut would be unjustified here.

For a VALIDATED nested transition V subset W, the H-orthogonal projectors
commute with product P_V. Hence `P_W-P_V` is idempotent of rank
`r=dim(W)-dim(V)`. After clearing the exact lcm denominator, every minor of
order e<=r has absolute value at most `r^ceil(r/2)*Z^r`. Proven distinct
primes, avoiding the denominators, have a product greater than this bound.
For each NE corner, the maximum modular rank is therefore its exact rational
rank: all next-order minors vanish by CRT and the bound, while an attained
rank has a nonzero minor in one field. If that rank equals r, its upper bound
comes directly from the nested-space theorem. Mixed differences of corner
ranks recover the exact rook pivots; the code does not union modular pivots.

The source's modular arithmetic is safe. Values are below a31-bit prime,
products fit uint64, and `a+p-b` stays below2^32. Corner ranks fit uint8 for
h<=35. Its integer projector construction also fits its types under the
input contracts: K<=531441, vn<=hK, dnum<=36K; fixed denominators are
below2^50. Summing absolute values of the unreduced numerator terms gives
less than2^53, traces stay below2^59, and zero-rank cross-products stay
below2^106, within signed128-bit comparison. Intermediate lcm products are
bounded because disjoint class sizes sum to at most h. Arbitrary-precision
integers hold difference denominators, Z, minor bounds and prime products.

The native checks rank order, trace and modular ranks; these do not by
themselves prove every supplied physical space is nested or bind the labels
to the scalar producer. Acceptance therefore requires the complete actual
positive-frame witness/compiler audit on BOTH axes, including forced/class
disjointness, incidence containment, selected links, all paid copied
transitions and timeline. The separately reported direct Fraction Gram
controls validate the projector implementation, rather than replacing
that source/physical binding. All-field profile checks are finite exact
evidence, not formal verification or the inherited analytic/tape theorem.
