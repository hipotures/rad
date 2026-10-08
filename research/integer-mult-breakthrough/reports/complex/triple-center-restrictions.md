# Scoped restrictions of affine and invariant triple centers

These arguments apply to the stated representations. They do not obstruct
arbitrary nonsymmetric fitting matrices, changed shared frontiers, wider
complex primitives, or a new physical transfer. Codex-assisted derivations.

## Affine gather support and binary frames

Let h>=8 be even, and write a triple-incidence gather coefficient as
`f(T)=sum(u_i : i in T)` with rational or complex u_i. An additional
constant is already in this span because each triple has size three.
If the nonzero source support lies in a binary hyperplane w^perp, then
f(T)=0 for every triple whose intersection with supp(w) is odd.
Permutation symmetry makes only the normal weight k relevant.

Solving those equations gives the following nonzero possibilities:

| k | Coefficients up to nonzero scalar | Source support |
| --- | --- | --- |
| 1 | -2 at i, 1 elsewhere | All triples avoiding i |
| 2 | -2 at a,b, 1 elsewhere | Triples meeting {a,b} in 0 or 2 points |
| h-2 | 1 at a, -1 at b, 0 elsewhere | Triples meeting {a,b} in one point |
| h-1 | 1 at i, 0 elsewhere | All triples containing i |

For 3<=k<=h-3, triples with one point inside and two outside force the
inside coefficients to be equal and the outside coefficients to be equal.
Triples with three inside then force both values to zero. At k=1 or 2,
all outside coefficients equal c, and inside coefficients are -2c.
At k=h-2, triples wholly inside force all inside coefficients to zero;
the two outside coefficients sum to zero. At k=h-1, only the outside
coefficient is free. At k=h, every triple is constrained and f=0.
The argument works over characteristic zero; no modular-rank inference
is used.

Each displayed support spans exactly the indicated binary hyperplane.
For point exclusion, weight-three vectors on the remaining h-1 coordinates
span the whole coordinate space: differences generate all even vectors,
and one odd vector supplies the last dimension. For the point star,
differences generate the even subspace outside i and one source adds i.
For the k=2 case, disjoint triples span all outside coordinates and a
triple containing a,b adds their sum. For k=h-2, differences span the even
inside subspace, swapping a,b adds e_a+e_b, and one source adds the final
dimension. Thus every proper support span has rank h-1.

A hyperplane in standard F2^h is nondegenerate exactly when its normal
has odd norm. Therefore only the point-exclusion and point-star types
are nondegenerate for even h. The signed pair types have an isotropic
normal and require the full space as a nondegenerate containing frame.

The usual center matrix `K_ST=(|S intersect T|-1)/2` has rational rank h
when h!=9. A factorization using r affine gather features must have r>=h.
If every retained feature returns once and return charge equals its frame
dimension, its total loss is at least h(h-1). Existing mixed D/G centers
attain this lower bound. This conclusion depends explicitly on that
return rule; it does not apply to a different simultaneous return program.

The first finite checker incorrectly omitted the signed difference case
k=h-2. It found nullity one there and forced this corrected classification.
The failed attempt and correction are preserved rather than hidden.

## Permutation-invariant fitting matrices

Let K_ST=f(|S intersect T|), f(1)=0, f(3)=1, for all triples S,T.
Expand in the four inclusion Gram matrices `B_j(S,T)=binom(|S intersect T|,j)`:

    c0=-c1, c3=1-2c1-3c2.

The degree-l inclusion-harmonic spaces have dimensions

    1, h-1, binom(h,2)-h, binom(h,3)-binom(h,2).

Counting inclusion pairs on their nested quotients gives the B_j
eigenvalue `binom(3-l,j-l)*binom(h-j-l,3-j)` for j>=l, and zero otherwise.
The four eigenvalues of K are consequently

    lambda0=c0*binom(h,3)+3c1*binom(h-1,2)+3c2*(h-2)+c3,
    lambda1=c1*binom(h-2,2)+2c2*(h-3)+c3,
    lambda2=c2*(h-4)+c3,
    lambda3=c3.

For h>=7 the degree-two and degree-three dimensions both exceed h.
Any rank<=h fitting matrix must therefore have lambda2=lambda3=0.
This forces c2=c3=0 and c1=1/2. Its lambda1 is positive, while lambda0
equals `binom(h,3)*(9/h-1)/2`. Its rank is h except at h=9, where it is
h-1. The h=9 rank reduction does not give positive frozen two-stage
phase deficit: `v^2-2v*h*(h-1)<0` for v=84.

The executable checker independently multiplies the direct B_j matrices
by nonzero harmonic vectors of all four degrees at h=7 and 8, and finds
every intersection of eigenvalue-zero lines for h=7,8,9,10,12,16,28.
It also checks affine hyperplane nullities by exact rational elimination
and binary support ranks at h=8,10,12,16,28.

The all-h argument above is a written analytic proof with finite controls;
it is not a formal proof package. The conclusion concerns only
permutation-invariant fitting matrices, not arbitrary rational min-rank.
