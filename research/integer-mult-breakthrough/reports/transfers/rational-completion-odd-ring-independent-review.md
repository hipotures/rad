# Rational completion, odd-ring reduction and the actual interface boundary

Status: **INDEPENDENT ANALYTICAL REVIEW AND EXACT FINITE GEOMETRY**. The
rational minimum/maximum completion theorem and fixed-neighbor concavity
argument are sound as stated. A concrete minimum completion has a small,
uniform Gram determinant and survives good odd-prime-power reduction. A
separate exact counterexample rules out applying the rational Lorentz
radical bound to arbitrary finite-field or odd-ring subspaces.

These are geometric statements. This report supplies no scalar word, bit
permutation, Gaussian phase frame, native routing or improved exponent.
The first 32 fixed-neighbor cuts in the other track found no strict ideal
improvement; connected-block changes are a separate experiment.

## Independent theorem review

The reviewed [rational theorem and paid-chain note](../synthesis/rational-frame-completion-and-paid-chains.md)
has SHA256 `08cc24041bb7eeb391d077906506477b35676476efc122d31005cd3bd891d150`.
Its constructor is SHA256
`8a35ffa3b5b354b4e0ec83ee75a19d76a497d47c883121d4c7a289836fd88f4c`;
the endpoint source is SHA256
`de9c2080bb6fb8d08903c3149b3b31be5b3fe917038ec8ff39107582a12f8eb2`.
This is source/proof review, not a rerun of those producers.

For a symmetric rational form B and V contained in U, any containing
nondegenerate F must have V intersect rad(U) equal to zero. If R=rad(V),
pairing with F/V must separate every direction of R, so dim F is at least
dim V+dim R. Conversely, split V into a nondegenerate N and its radical R.
The absence of the shared obstruction lets us choose directions in U dual
to R. Subtracting their projections onto N preserves those pairings. On
the added hyperbolic block the Gram matrix is [[0,I],[I,A]], whose
determinant is (-1)^dim R. This proves attainability of the lower bound.
The argument also applies when the full ambient form is singular.

A complement of rad(U) inside U can be chosen to contain V precisely
because the shared intersection is zero. Every such complement is
nondegenerate, and no nondegenerate F has dimension larger than the
quotient U/rad(U). This proves the maximum dim U-dim rad(U).

For G_h=I-J/9 over the rationals and h>9, the real signature is (h-1,1).
A totally isotropic real subspace projects injectively onto the one
negative coordinate, so dim rad(V)<=1. This is a statement about rational
subspaces before reduction. It does not constrain arbitrary subspaces
over an odd finite field.

With both neighboring role frames fixed, the sum of costs
(d-a_i)^p+(b_i-d)^p is concave in d for 0<p<1. Its minimum lies at one of
the two attainable endpoint dimensions. A frame change at several adjacent
gates changes those neighbors too; independent local endpoint choices are
not a global optimizer. A paid prime/fallback or representation fee can
change which endpoint is preferable.

## A uniform explicit good reduction

Take three disjoint triple indicator vectors v0,v1,v2 on the first nine
coordinates, target t=e0+e3+e6, and w=t+6e9. This requires h>=10. Their
common future cap is U={x:(3t-1) dot x=0}=t-perp under G_h. All four
directions lie in U. The three-vector Gram matrix is 3I-J, with radical
r=v0+v1+v2. Its pairing with w is -6. The complete integer Gram matrix is

    [ 2 -1 -1 -2 ]
    [-1  2 -1 -2 ]
    [-1 -1  2 -2 ]
    [-2 -2 -2 30 ],

with determinant -108, independent of h. Thus F=span(v0,v1,v2,w) has the
minimum dimension four. No large determinant is introduced by this
particular completion.

At any odd prime power q=p^k with p!=3, this integer frame reduces to a
free nondegenerate rank-four module. Its projector

    P_F=A(A^T G_h A)^-1 A^T G_h

is defined over Z/q, fixes all four columns, is idempotent and G_h
self-adjoint. The cap projector is I-t(3t-1)^T/6. Both nesting products
P_F P_U and P_U P_F equal P_F. Consequently I-2P_F is an involutive
G_h-isometry of the complete coordinate module. These identities concern
linear coordinate maps, not physical Gaussian operators or a tape bill.

If the intended full primitive additionally requires invertible ambient
G_h, primes dividing h-9 must also be excluded, since det G_h=(9-h)/9.
They are not required for the abstract rational completion theorem. The
finite probe deliberately retains that separate ambient exclusion.

For an isometry g satisfying g^T G_h g=G_h, the Gram matrix of gA equals
the same fixed Gram matrix. Also P_(gF)=g P_F g^-1. Thus this frame's Gram
exclusions do not multiply with the number of group vertices. Computing
those vertices, routes and actual primitive representatives still costs
work. This invariance does not prove their implementation is cheap.

## Exact finite-ring negative control

At q=5^k, choose an integer i with i^2=-1 modulo q. In each disjoint
four-coordinate block put the vector (1,-1,i,-i). It has coordinate sum
zero and squared norm zero modulo q. With r=floor(h/4), these vectors
span a free totally isotropic rank-r module for G_h. Their pairings with
the first coordinate vector in each block form I_r. Adding those r dual
directions gives a nondegenerate 2r-dimensional completion with Gram
[[0,I],[I,A]]. Reducing modulo 5 proves that fewer than r added
directions cannot suffice.

The identical integer vectors over the rationals have Gram
2(1+i^2)I_r, which is positive and nondegenerate. Their rational minimum
completion dimension is only r. The rational projector cannot be reduced
at this prime as a unit-denominator interface. Thus rational positivity
does not make every reduction safe; the failing prime is visible in the
Gram charge. The finite controls use k=1,2,3 and retain all r directions,
ranging from two at h=10 to twelve at h=48.

The joint cap of all 27 targets formed by one coordinate from each
triple gives a different obstruction. Differences between cap equations
force constancy within each triple, and one equation forces the outside
coordinate sum to zero. The explicit basis has dimension h-7 and contains
r. Every vector in it pairs to zero with r. Hence no nondegenerate
containing frame inside that joint cap exists over the rationals. This
excludes that particular common-cap chronology, not every circuit.

## Evidence, reproduction and remaining costs

The import-free [independent source](../../code/transfers/rational_completion_modular_review.py)
has SHA256 `6297988b996bb76dc4e307abbf0dbef252e088b4c257866e381f2170a6c404fd`.
It independently constructs the vectors, Gram matrices and coordinate
operators; it imports no producer or external dependency. The first
four-worker run began at `2026-10-09T08:37:44.313345+00:00` and passed in
0.8852 seconds. At h=10,12,24,48 it checks 54 good prime powers and 38,220
complete coordinate entries, twelve finite-ring negative cases and four
joint-cap witnesses. These are complete matrix identities at those
finite parameters; the general claims are the algebraic proofs above.

Original evidence remains in ignored
`work/transfers/20261009T083744Z-transfer-rational-modular-first/`.
Compact unchanged exports and source pins are retained in the corresponding
durable run. The bounded reproduction uses h=10:

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/rational_completion_modular_review.py --workers 1 --bounded
```

For all four deterministic cases use `--workers 4`; optional `--output`
must name a new directory. Python standard library is the whole runtime
closure. The configuration is not a runtime dependency.

The remaining integration obligations include every new Gram/coordinate
denominator and admissible prime, actual coordinate bases and address
representation, full phase or bit-frame transitions, scalar coefficients,
bad-class fallback, row stock, all dirty endpoints, routing, precision and
all-size setup. No existing public characteristic is changed by this
review. The constructive completion is potentially useful because it
can avoid a large local frame without hiding a large Gram determinant in
this example; its benefit requires a complete legal chronology.

Authored with OpenAI Codex assistance. The initiating completion example
and rational theorem are credited to the independent synthesis track in
the linked note; the modular controls and orbit-fee argument are this
track's separate review.
