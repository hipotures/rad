# Independent algebra review of the newly selected local basis

Reviewed 2026-10-08 13:56 UTC by the GPU campaign scout. The geometry worker
requested this review after its finite t-sweep found a matrix-moment gain.
This document independently derives the formulas; it neither executes the
new full profiles/data check nor certifies an improved multiplication bound.
The general rank-one basis parameterization is already in the credited
PR32/38/40 lineage. The selected parameter and changed-graph integration
belong to this campaign's geometry search.

For h>9 set

```
t=-4/[3(h+3)],
L=I+tJ,
L^-1=I-4J/(h-9).
```

The nontrivial eigenvalue and determinant of L are
`(9-h)/[3(h+3)]`, which are nonzero. A negative eigenvalue is harmless:
L is a rational change of basis, not a new positive quadratic form.
The original actual label spaces remain nondegenerate under `H=I-J/9`.

## Actual source lines and retained-center complements

For each triple indicator a, the original normalized projector has pair
`a, a^T H/2`. For general t its conjugated pair is

```
p'=a+3t*1,
xi'=a^T/2-(1+9t)*1^T/[6(1+ht)].
```

At the selected parameter this is exactly

```
p'=a-4*1/(h+3),
xi'=(a^T+1^T)/2.
```

Every primal and dual coordinate is nonzero. The products are
`(h-1)/(h+3)` inside the triple and `-2/(h+3)` outside. Their sum is one:
`3(h-1)-2(h-3)=h+3`. Thus at h23 the products are11/13 and-1/13,
and at h25 they are6/7 and-1/14. These are the new actual data weights;
the PR40 I+J weights cannot be reused.

For a retained center `U_i=ker(1^T-3e_i^T)`, the original normalized
complement pair is

```
p_i=e_i+2*1/(h-9),
xi_i=(h-9)*1^T/12-(h-9)*e_i^T/4.
```

Direct multiplication by L and L^-1 gives

```
p'_i=e_i-2*1/(h+3),
xi'_i=-(h-1)*1^T/4-(h-9)*e_i^T/4.
```

The primal center coordinate is `(h+1)/(h+3)` and each exterior coordinate
is `-2/(h+3)`. The dual center coordinate is `-(h-5)/2` and each exterior
coordinate is `-(h-1)/4`. All are nonzero for h>9. Their dot product is

```
[(h-1)^2-(h+1)(h-5)]/[2(h+3)]=1.
```

These formulas cover all48 centers at23/25. The copy replacement still
removes exactly h original identity cleanups and adds h rank-one complements,
while retaining the actual newly profiled rank-(h-1) copied transforms.

## Independent original-envelope derivation

Let C be a core of size c=1 or2, O the outside support of size n, and put
`u=1_C`, `o=1_O`, `s=3-c`, `d=s^2+(c-1)n`. A Gram basis for the original
envelope is `e_j+u/s` for j in O. Its H-Gram matrix is
`I+(c-1)J/s^2`, whose inverse is `I-(c-1)J/d`. Multiplying the basis,
inverse Gram and H-dual basis gives the exact untransformed projector

```
P=D_O+[s*o*(u-1/3*1)^T+s*u*o^T
       +n*u*(u-1/3*1)^T-(c-1)*o*o^T]/d.
```

Conjugating this expression by general `I+tJ`, including the transformed
diagonal mask rather than leaving it unchanged by assumption, reorganizes
it into

```
P_t=D_O+[s*o*z_t^T+s*w_t*o^T+n*w_t*z_t^T-(c-1)*o*o^T]/d,
w_t=u+3t*1,
z_t=u-(1+9t)*1/[3(1+ht)].
```

For the selected t, `w=u-4*1/(h+3)` and `z=u+1`, exactly as proposed by
the worker. The correction factors as

```
[o,w] * [[-(c-1),s],[s,n]] * [o,z]^T / d,
```

so its rank is at most two. Clearing `(h+3)d` leaves an integer matrix.
Source lines clear `2(h+3)`. Same-core envelope differences retain the
rank-two correction bound; source growth has correction rank at most three;
a core-two to core-one difference has correction rank at most four.
These statements concern the correction to the nested zero-one mask, not
the full rank of the physical residual. Fresh integer magnitude bounds and
an adequate prime product must accompany the complete new profiles.

The same-core bound can be checked directly, rather than subtracting two
unrelated rank-two formulas. At c1, d4 and w,z fixed, a nested difference
has correction `[2*delta_o*z^T+2*w*delta_o^T+delta_n*w*z^T]/4`, of rank at
most two. At c2 the exact identity is

```
P_O=D_O+w*z^T-(o-w)*(o-z)^T/(n+1).
```

The common `w*z^T` cancels between the two envelopes, leaving the difference
of two rank-one terms, again rank at most two. The mask difference is the
new outside-coordinate mask because the covers are nested.

## Changed-family proof gates

The source primal/dual coordinates and complements remain nonzero, so the
unchanged controlled-permutation arbitrary-matrix transfer identities apply
to every actual new local fixed profile by nonzero diagonal scaling.
The inherited all-weight data rank cuts still prove ordered zeros. The two
unchanged boundary restriction trees still supply full rank47 and middle481.
The full ordered nonzero prefix claim, including the21 and17 blocks, must
be established again for all4073300 NEW source pairs. PR40's successful
nonzero-prefix residues concern different weights and cannot certify this
specialization. A complete bad-prime fallback or exact-Q witness scheme is
valid, with every pair and every prefix retained.

Subsequent complete computation showed192596 exceptions to the former
uniform17-block. The geometry worker instead retained their exact169 run
profiles and audited all source indices and histogram frequencies. The
[classification review](new-data-classification-review.md) records the
independent CRT rank argument and links the complete input audit; it closes
this data gate without claiming that the old uniform profile survives.

Each modular reduction must avoid actual denominator factors. In addition
to profile denominators and source weights, the rational basis requires
avoiding the factors of `3(h+3)(h-9)`. The eventual address prime is separate
from the finite witness primes and must avoid all newly fixed nonzero-minor
numerators as well. No generic-basis existence proof is needed once this
explicit specialization passes its finite gates.

The new actual original-envelope matching, full CRT profile, copied streams,
literal scalar/dirty timeline, physical role volumes, characteristic and
assembly remain required. The scout's algebra acceptance does not replace
those checks or any inherited analytic/tape/prime/cutoff hypothesis.

## Optional continued parameter search

Writing `z=u+rho*1` reparameterizes the credited general family as

```
t=-(1+3rho)/[3(h*rho+3)],
p_source=a-(1+3rho)*1/(h*rho+3),
xi_source=(a^T+rho*1^T)/2,
p_center=e_i-(rho+1)*1/(h*rho+3),
xi_center=-(2+rho*(h-3))*1^T/4-(h-9)*e_i^T/4.
```

The selected basis is rho1. Positive rational rho keeps these source and
center coordinates nonzero at h>9 and keeps L invertible. Other rho values
may have different ordered zero minors, so they require new profiles and
data certificates. This is a structured search parameter, not an asserted
additional gain or new priority claim for the general I+tJ family.
