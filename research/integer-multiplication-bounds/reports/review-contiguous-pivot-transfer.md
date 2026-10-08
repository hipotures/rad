# Independent transfer review: contiguous Bruhat pivots

The h51 bit network with 502,265 auxiliary roles supports the primitive
interchange exponent `tau=1-a` with

`a=5293423/10^15`.

This is a changed physical recursive construction, not a reinterpretation
of the old sum of ranks. Consecutive pivots in the existing lower/lower
factorization share one recursive interchange of their concatenated fields.
The affine updates still act separately modulo the original field range.
Two disjoint families of physical edges give a proved lower bound on the
resulting rank-log moment. Every other edge remains unchanged. The finite
network, rational frames, scalar pointwise XOR gates, odd prime, endpoint
identity and total rank sum are retained. A fresh downstream composition is
required before asserting an integer-multiplication saving kappa.

The review uses the original manuscript at commit
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`, sections 03 and 04, and the
independently accepted [h51 finite witness](review-odd51.md). The campaign
started at 2026-10-07 22:25:21 UTC. Its historical deadline was
2026-10-08 08:25:21 UTC; the explicit user extension sets the active
deadline to 10:00:00 UTC without restarting the campaign.

## Physical grouped interchange

Let the fixed rational edge matrix have its original lower/lower
factorization `A=E1 Pi E2`. The H fields precede the D fields, and each
field contains b radix-q digits. A pivot `(i,j)` requires `H_i += D_j`
modulo `q^b`. The original implementation is

```text
D_j <- D_j + H_i
interchange H_i and D_j
D_j <- H_i - D_j
```

For a run of pivots `(i+k,j+k)`, `0<=k<r`, perform the first update on
each of its r original fields, interchange the two contiguous rb-digit
chunks once, then perform the last update separately on each field. The
result is exactly the r original additions. The partial permutation has
distinct row and column indices, so distinct groups do not conflict.
Offdiagonal increasing runs also qualify, though the count proof below
only needs diagonal runs. The original earlier-control affine stream
operations implement all the first/last updates in O(V) time because their
number is fixed.

Carry resets at each b-digit boundary are essential. For q=3, b=1,
`H=(2,0), D=(1,0)`, componentwise addition gives `(0,0)`, whereas one
addition modulo `3^2` gives `(0,1)`. The independent checker preserves this
counterexample. An arbitrary permutation of pivots cannot be concatenated:
reversed column order requires an additional adapter, which is not used
here. There must be no spectator between the fields *inside* either run.
At every recursive invocation, the two selected contiguous chunks are
partitioned into consecutive equal fields, so this condition is inherited.
All fields outside the selected chunks, including any field between those
chunks, remain spectators under the original interchange contract.

The triangular factors, inverses and fixed prime are exactly the original
ones. A lower change of rows used later to prove a profile bound is not
executed as a new gate or used to change the finite rational coefficient
table. No gather of arbitrary pivots is assumed.

## Arbitrary integer widths and fixed tapes

For any e>=m, write `e=m*b+t`, with `b=floor(e/m)` and `0<=t<m`.
Use the original finite-network shear on the two mb-digit main chunks;
the short H tail between the main chunks is an allowed spectator. The two
outer componentwise affine updates turn this shear into a main interchange,
as in original section 04. Interchange the remaining t corresponding
radix-q digits individually. These use the original fixed-digit stream
operations, not a growing integer-address sorting routine. Since m and q
are fixed, the tail costs O(V). Widths e<m are the same fixed-size base
case. No extra address records are introduced, and the completed operation
preserves the logical order of all main, tail and spectator coordinates.

At a node, split complete preceding rows into the W original role streams.
Each stream has logical volume V/W. A grouped child of r pivots acts on
`r*floor(e/m)` digits within one such stream; its volume remains V/W.
The original fixed-tape depth-first parking schedule applies verbatim:
park the W-1 inactive streams, reuse the fixed I/O and role tapes, and
restore the parked streams on return. The fixed number of batches, affine
updates, splits, gates, merges and descriptor operations costs O(V) per
node. Original full chunk ranges remain present as spectators at deeper
nodes, so the descriptor amortization has the same complete-volume lower
bound. A fixed number of tapes, however large its constant, is sufficient.

If n_r denotes the actual number of grouped child calls of width factor r,
including all ungrouped pivots as r=1, the uniform recurrence is

```text
F(e) <= sum_r (n_r/W)*F(r*floor(e/m)) + C.
sum_r n_r*r = s.
```

Every selected r is below m. If `tau>0` and
`gamma=sum_r n_r*r^tau/(W*m^tau)<1`, induction with a sufficiently large
fixed constant proves `F(e)=O(e^tau)`, for every integer e. The constant
absorbs `C/(1-gamma)` and the fixed base cases. This proof does not use a
real-valued recursive field width or pad e to a power of m.

## Canonical lower/lower profile and a low-rank bound

The canonical profile is obtained by taking the topmost nonzero active
row and its rightmost nonzero active column. Its partial permutation Pi is
uniquely determined by the ranks of all north-east corner submatrices.
Invertible lower multiplication on the left mixes each row prefix within
itself; lower multiplication on the right mixes each column suffix within
itself. Both preserve these corner ranks and hence preserve Pi. Row-only
rightmost elimination yields the same profile as full isolation of the
pivot by lower row and lower column operations.

For an n-dimensional matrix `A=I-U V^T` with `rank(U)<=d`, construct an
invertible lower matrix S which concentrates SU into at most d rows M.
This can be done chronologically: subtract previous independent rows from
the current row of U, and retain a row exactly when it adds a new direction.
Then `S*A=S-(S*U)V^T`. Every row outside M is lower triangular with a
nonzero diagonal before rightmost elimination.

Such a row stays lower during elimination. A previous pivot at a column
below its own index only subtracts entries in that column prefix. A pivot
above its index finds a zero entry and does nothing. Its diagonal remains
nonzero unless an earlier modified row has already pivoted in that column.
There are at most d such stolen unmodified rows J. A stolen row is strictly
lower after that elimination, so it cannot steal a later diagonal itself.
All rows outside `M union J` therefore pivot at their own diagonal. This
union has size at most 2d; it already includes every zero row, so zero rows
must not be added a second time. Consequently A has at least `n-2d`
diagonal pivots, in at most `2d+1` consecutive runs.

The bound applies to a general low-rank perturbation; its proof does not
require a positive definite ambient form. The stronger assertion that
every rank pivot is diagonal is false. Nor is an offdiagonal bound d valid
for every rank-d update. Those assertions are not used.

## Two disjoint physical families

Write `h=51`, `v=C(h,3)=20825`, `m=h^3=132651`, and `R=502265`.
Original section 03 gives the stage and axis labels in the fixed coordinate
order of `F tensor F tensor F`.

The final middle-stage auxiliary endpoint is
`F tensor F tensor line(t_B)` before it reaches the full sink. Its residual
is `I tensor I tensor (I-P_tB)`. This supplies h^2 consecutive blocks for
each B. There are `(R+h)*v` copies per B: the h centers belong to the bit
network, and are not the h+1 centers of the separate complex construction.

For a triple with least coordinate a, let u be its indicator and let
`v_j=(2 if j is in the triple else -1)/6`. Under the rational form
`I-J/9`, `P_t=u*v^T`, `v^T*u=1` and every `v_j` is nonzero. The rightmost
profile of `I-u*v^T` consists of diagonals i<a, the pivot `(a,h-1)`,
diagonals `a<i<h-1`, and a zero last row. Clear below the pivot using
`u_i/u_a`; the remaining rows become `e_i-(u_i/u_a)e_a`, and the final
coefficient vanishes by `v^T*u=1`. Thus the positive diagonal runs have
lengths a and `h-a-2`, with one separate offdiagonal pivot. Exactly
`C(h-a-1,2)` triples have least coordinate a. The total old rank of this
family is

`T_middle=(R+h)*v^2*h^2*(h-1)=28330705423416375000`.

The shared first/third auxiliary joins have residual
`A=I-P_E-P_K`, where E and K are orthogonal nondegenerate h-dimensional
spaces. There are `J=(R+h)*v^2=217844716827500` such physical joins.
Their rank is `m-2h`. Apply the preceding lemma with d=2h: each has at
least `t=m-4h=132447` diagonal pivots in at most `g=4h+1=205` runs.
These joins and middle terminal edges are disjoint. Their combined old
rank is below s; all other old pivots remain individual.

For actual positive diagonal lengths r_i, convexity gives
`sum r_i*log(r_i)>=t*log(t/g)`. If there are more than t diagonal pivots,
the same lower bound holds because `x*log(x/g)` increases for x/g>1.
This is a bound on the actual histogram; no fictitious Jensen histogram
is executed or charged as a circuit.

## Kernel holes and recursion depth

The joined residual annihilates each
`u_i=e_i tensor t_A tensor t_B`: it belongs to E, and E is orthogonal to K.
In the fixed tensor order, let `a=h*min(A)+min(B)`. The earliest support
column of u_i is `j_i=i*h^2+a`; every other support column is strictly
later. The resulting exact kernel relation expresses column j_i in the
span of strictly later columns. Therefore the full suffix rank does not
increase when column j_i is added. In the canonical profile, column
occupancy is exactly this suffix-rank increment, so j_i is never a pivot.
This argument also covers later columns that have already been eliminated.

The h forbidden columns are spaced by h^2. The gaps before the first,
between them, and after the last contain at most h^2-1 columns. Every
increasing contiguous pivot run thus has length at most h^2-1=2600.
The middle runs have length at most h-2, and all other calls have r=1.
Consequently every nonbase child has width
`r*floor(e/m)<e/h`, and depth is at most `ceil(log_h(e))`.

Rational intersection-one matching is essential here. A disjoint matched
triple does not make E orthogonal to K under `I-J/9`; the independent
negative control produces a nonzero kernel residual. The binary complex
even-intersection interface cannot be substituted into this proof.

## Complete row reservations and original guard

Reserve a preceding complete row range divisible by `W^D`, where
`D=ceil(log_h(e))`. If the available row range R0 satisfies `R0>=W^D`,
rounding it up to a multiple of `W^D` enlarges volume by at most two.
Every original role split is then exact, including arbitrary row-prefix
cardinalities. Padded rows and the active bitmap are restored only at the
completed interchange boundary. The proof does not inspect the bitmap
during scalar gates.

The retained routing/layout invocations have `e<=C*p` for a fixed constant
C; there is not yet a supplied uniform numerical proof of e<=2p for every
padded bulk layout. Here W<2^49. For p>=max(2,C),

```text
log2(W^D) <= 49*(log2(p)+log2(C)+1) <= 100*log2(p).
```

The untouched reservoir supplies at least `2^ell` complete rows, with
`ell>=p^(1-epsilon)/2` eventually. The sufficient condition
`p^(1-epsilon)>200*log2(p)` is eventual for every fixed epsilon<1 and can
be checked by the same compressed exponential cutoffs used by the accepted
bulk layout. The finite C and fixed prime/table setup thresholds remain
separate eventual thresholds. An exact composed numeric cutoff must
include this condition before publication.

Grouping changes the bit address recursion, not the complex arithmetic
network or its fixed factors. It introduces no new complex arithmetic
gates, numerical truncations, constants, or rational frames. The accepted
semantic child guard and its C0/C1 remain applicable to the separate
complex transform.

## Exact saving certificate and evidence

For the accepted finite input,

```text
N = 9031399015625
W = 453752231686250
L = 3384009916875
D = N-2L = 2263379181875
s = W*m-D = 60190685022033566875.
```

Let M_lower be the exact middle rank-log moment lower bound plus
`J*t*log(t/g)_lower`, and let `L_upper=log(m)_upper`. The true first
moment is at most `Lambda=s*L_upper-M_lower`. For the displayed a,
`a*L_upper<1`, and

```text
sum n_r*r*exp(a*log(m/r))
 <= s + a*Lambda + a^2*s*L_upper^2/(2*(1-a*L_upper))
 < W*m.
```

The first inequality follows from
`exp(x)<=1+x+x^2/(2*(1-x))`, for 0<=x<1. The second is an exact rational
strict inequality using independent 48-term logarithm enclosures. It is
equivalent to the required characteristic bound at `tau=1-a`.
The certificate compares a against an independent upper enclosure of the
old ungrouped primitive saving, and passes strictly. It also checks middle
only and conservative h^2-capped variants. A later fine-grid producer
witness needs its own audit; this report only promotes the displayed
conservative a.

The [main independent source](../code/review_pivot_batching.py), SHA256
`661dd9337c601c6a791815bd022c35faed27f1f68753a4f544bdc8ee5dafc7ca`,
and [run](../runs/20261008T0439Z-review-pivot-batching/protocol.json)
check 36 reconstructed general rational LAR factors, 45 low-rank
concentration/profile cases, all 20,825 h51 triple minimum frequencies,
145 explicit rank-one profiles, 8,019 complete modular-ring addresses,
and 66,339 complete odd-radix main/tail addresses. Carry and noncontiguous
pivot counterexamples are retained. This run used Python 3.14.7, one CPU
worker, no swap, 0.81 seconds elapsed and 22,184 KiB peak RSS.

The independent [kernel followup](../code/review_pivot_forbidden.py),
SHA256 `1f6f2dceaac903e0dd15cd9fb9862dbc27b25917ff0222beecabb9e4fed0f37e`,
and [run](../runs/20261008T0443Z-review-pivot-forbidden/protocol.json)
construct three full exact rational joined matrices at h6/h8 with varied
supports. They independently verify every kernel relation, rank, forbidden
pivot column, diagonal bound and maximum-run bound. A nonorthogonal
matching fails as intended. This run used Python 3.14.7, one CPU worker,
no swap, 1.14 seconds elapsed and 35,268 KiB peak RSS.

The selected h51 giant joined matrices and a full multiplication machine
were not materialized. Their all-size claims follow from the proved
projection/profile and stream-interface arguments above. The small exact
controls discriminate field arithmetic and proof hypotheses; they do not
replace these arguments. Recovery commands, pinned input identities,
source hashes, timeouts, admission and reservation release are in the two
protocols. Execute those commands with fresh output paths. Original source
and result bytes are unchanged; parent publication owns their commit and
remote verification.
