# Actual source-specific side cleanup

The pinned public PR36 construction (icekylinx, commit
`11817ccacb564bb7f98789c20dc11d3fece207e3`) assigns a side output for
target T = {i,a,b} to `U_i intersect {x_a+x_b=0}`. The form is
`H = I-J/9`, so `H(t_T,x)=x_i+x_a+x_b-sum(x)/3=0` on that space.
The construction's ordinary endpoint is the actual target hyperplane
`t_T^perp`, rather than the common center hyperplane U_i. The reverse
frame statement in `notes/paired-construction.tex` explicitly retains
these source-specific physical X lines and Y complements.

Therefore the actual common-basis growth matrix for side projector P_side
is `M = I-P_T-P_side`, of rank h-1-r. Here P_T is the normalized actual
source projector, with `xi_T p_T = 1`; H orthogonality gives
`P_T P_side = P_side P_T = 0`. The difference is an idempotent even though
the ambient form is indefinite. Exact integer-minor bounds and complete
NE-rank profiling therefore apply to this matrix with that rank upper bound.

Replacing it by `P_Ui-P_side` changes the endpoint. Correcting U_i to
`t_T^perp` generally has rank two, so one paid rank-one correction cannot
justify the substitution. The existing additional rank-one call must remain
charged, with its original scalar read and cleanup timing. The public PR36
histogram contains `z^(h-1-r)+z` for a side. Profiling the first actual
matrix in place of its conservative singleton expansion preserves that
rank mass; it does not authorize removing the second call.

The PR37 exact physical contraction controls (rohanarun, commit
`cb86e50e9a07685068874d8e4174b2e6c209b95c`) multiply the h23 corner by
nonzero row/column factors `v_B[i]` and `nu_B[j+delta]`, and the h25 corner
by `p_A[r_i]` and `xi_A[c_j]`. At any basis satisfying all seven nonzero
gates, these are invertible diagonal scalings and preserve every NE rank.
This applies after constructing the actual conjugated common-basis matrix.
Changing the common basis itself is not NE-rank invariant.

Geometry's bounded combinatorial discriminator
`../geometry/results/side-terminal-rank-discriminator-20261008T1618.json`
checks all 5313 h23 and 6900 h25 selected positive side outputs. Each has
rank h-2, its target triple exists in the input table, and the omitted
signed symbols are opposite or zero. Their actual cleanup has rank one,
so no new width saving is available on these current selected axes.
No full terminal-matrix sweep was needed. This remains a reusable interface
for future genuine side frames of smaller rank.
