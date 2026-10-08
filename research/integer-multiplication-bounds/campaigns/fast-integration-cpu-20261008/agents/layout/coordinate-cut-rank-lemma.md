# Coordinate-cut rank obstruction for a C-only compiler

## Question and exact compiler class

Can a native complex frame compiler remove its BIT basis changes by replacing
them with coordinate-aligned smaller C children and shared whole-address H
children, while retaining a strictly saving recursive moment?

The following scoped obstruction applies to exact linear semantics over the
complex numbers. Fix e ORIGINAL selected physical coordinate bits, a complete
cube of size N=2^e, and R target role copies. The required endpoint is
`I_R tensor C^tensor e`, where C has nonzero off-diagonal entries and is
invertible. Native `C=((1+i)I+(1-i)X)/2` satisfies these conditions.

Allowed recursive child j applies C or H to a coordinate subset A_j of size
f_j, on r_j complete role copies; all remaining coordinates are spectators.
The role volume ratio is gamma_j=r_j/R. Temporary scalar wire/role operations,
address-diagonal phases, parking and copying are allowed only when they
preserve every original selected-coordinate cut. Physical row-stock selectors
must satisfy that condition as well. This restriction is essential.

No selected-bit basis change, CNOT, gather mixing selected bits with stock,
or noncoordinate directional C_v is granted as free overhead. Native current
BIT basis changes are explicitly outside the allowed class. The claim does
not exclude arbitrary nonlinear machines or rounded circuits without a
corresponding exact linear contract.

## Rank proof

For each original coordinate i, split the input and output by its zero/one
value and write an operator's off-diagonal block as T_01. For compatible
operators, including rectangular copy/delete stages,

`(AB)_01=A_00 B_01+A_01 B_11`,

so `rank((AB)_01)<=rank(A_01)+rank(B_01)`. Every permitted cut-preserving
overhead stage has zero off-diagonal block. Introducing and later deleting
temporary roles does not change this inequality.

The required target has rank `R N/2` on each of the e cuts. A coordinate child
j contributes zero on i outside A_j and at most `r_j N/2` on a cut inside
A_j. For C and H this upper bound is attained: the block is a nonzero scalar
times an invertible tensor operator on the other coordinates. Summing the
subadditive bounds across all e cuts gives

`R e N/2 <= sum_j r_j f_j N/2`, hence

`sum_j gamma_j (f_j/e) >= 1`.

For every tau<1 and0<f_j/e<=1, `(f_j/e)^tau>=f_j/e`. Therefore

`sum_j gamma_j (f_j/e)^tau >= 1`.

The usual child-dimension moment cannot be strictly below one in this exact
coordinate-only compiler class. This conclusion allows shared and cancelled
whole-H calls; it does not merely count a literal replacement of every
existing basis wrapper.

For uniform role banks, s children of width e/m and t whole-e children give
`s/m+t>=R`. A coupled recurrence would require `s/(R-t)<m` for a saving,
which is the contradictory inequality `s/m+t<R`. A small number of classical
coordinate kernels does not bypass the accounting: each is another charged
child of its actual coordinate support. A linear number of such kernel-volume
units restores the corresponding linear work.

## Why the current native directions escape this bound

One directional kernel `aI+bX_v` has residual dimension one, but its
off-diagonal block is full rank on EVERY coordinate where v is nonzero.
Its summed cut-rank contribution can be `weight(v) N/2`, rather than N/2.
Consequently residual dimension cannot be substituted for coordinate-support
size in this proof. The native phase-frame change P_M implements exactly this
distinction; its actual BIT cost remains charged.

The proof uses one common physical basis throughout. Relabelling selected
coordinates or changing a basis in the middle is not a cut-preserving scalar
operation. A new compiler with an independently paid noncoordinate mechanism
remains open. The user's complete research campaign is not excluded by this
scoped lemma.

## Verification and status

The proof was independently criticized by the campaign inverse agent, who
confirmed rectangular-copy subadditivity and the need for fixed original
cuts. It is a written finite linear-algebra lemma, not formal verification or
external peer review. An approximate operator transfer needs its own charged
singular-gap error argument; it is not inferred from finite PASS labels.

The separate literal-wrapper front-count obstruction belongs to the inverse
and scout reports. This argument does not rely on those numerical gate counts.
Whole-H routing remains a valid exact coordinate-permutation construction;
this lemma explains why its coordinate-only recursive self-compilation cannot
by itself create the desired complex rank saving.

`code/check_coordinate_cut_ranks.py` checks45 exact finite-field cases at
e=2--6 and up to3 roles, including coordinate C, coordinate H, dense
directional C_v and rectangular role-copy operators. All stated ranks pass.
The prime65537 maps i to256, so nonzero modular Gaussian-rational determinants
are exact nonzero witnesses. The receipt `results/coordinate-cut-ranks.json`
takes0.118 seconds. Dense one-dimensional residual directions explicitly
contribute on multiple named cuts, demonstrating the scope boundary.
