# Contiguous Bruhat pivots change the bit recurrence

This is a new structural investigation within campaign `20261007T222521Z`.
The accepted multiplication witness at this checkpoint still uses the
uniform h51 recurrence. The alternative recurrence below requires its own
complete tape, row-padding and assembly review before promotion.

For a rational lower/lower Bruhat factorization `A = E1 Pi E2`, consider a
run of pivots `(i+t,j+t)` for `0 <= t < r`. Its source and destination runs
are physically contiguous. Execute the original preliminary affine gate
on each field, exchange the two contiguous `r*b`-digit blocks with one
recursive call, and execute the original final affine gate on each field.
The surrounding fields remain spectators. Addition must reset its carry
at each `b`-digit boundary: replacing the segmented operations with one
addition modulo `q^(r*b)` is incorrect. Noncontiguous runs cannot use this
argument without an additional gathering construction.

This retains the original rational matrices and coefficients. It does not
introduce new prime exclusions, factorization denominators, or complex
precision constants. For arbitrary digit width `e`, use `b=floor(e/m)`
and leave the fewer than `m` remaining digits as a spectator during the
main exchange. Exchange corresponding tail digits separately at fixed
elementary cost. This avoids padding to a larger recursive tensor volume.

If `n_r` counts the resulting contiguous calls of width `r*b`, the
normalized recurrence becomes

`F(e) <= (1/W) sum_r n_r F(r*floor(e/m)) + O(1)`.

The original rank identity remains `sum_r n_r*r = s = W*m-D`. A saving
`a` is sufficient when `sum_r n_r*r^(1-a) < W*m^(1-a)`. Consequently the
distribution of pivot-run lengths matters, rather than just their sum.

## Two dominant edge families

The terminal middle-bank edges have residual
`I_(h^2) tensor (I_h-P_t)` and exactly `(R+h)*v` copies per triple `t`.
For minimum triple coordinate `j`, the rank-one complement has diagonal
runs of lengths `j` and `h-j-2`, and one isolated off-diagonal pivot.
The frequency of that minimum is `binomial(h-j-1,2)`. These profiles give
an exact contribution to `sum n_r*r*log(r)`.

The first/third shared-bank joins have residual `I-P_E-P_K`, with two
orthogonal rank-h projectors. There are `(R+h)*v^2` such edges. A general
rank-d update of the identity has at least `m-2d` diagonal pivots in at
most `2d+1` runs. To see this, first concentrate the update's row space
into at most d rows using an invertible lower triangular operation.
An unmodified row retains its diagonal unless an earlier modified row
already claimed that column. At most d more rows can lose their diagonal
this way. Outside these two exceptional sets, the canonical pivot is
diagonal. Lower triangular changes preserve the relevant northeast ranks.
For the joined residual, `d=2h`; convexity then gives the lower moment
`(m-4h)*log((m-4h)/(4h+1))` per edge.

The joined residual also annihilates every vector
`e_i tensor t_A tensor t_B`. The first nonzero coordinate of this vector
is `i*h^2 + h*min(A) + min(B)`. Its column is a linear combination of
strictly later columns, so it cannot be a rightmost Bruhat pivot.
These h equally spaced forbidden columns bound every diagonal run by
`h^2-1`. Thus the uncapped moment estimate is compatible with at least
h-fold shrinkage of all batched children. Small off-diagonal pivots can
remain separate calls. The maximum recursion depth is therefore
`ceil(log_h(e))`; its larger row-padding requirement must be included.

## New exact controls and status

- [Initial pivot controls](../runs/20261008T042300Z-diagonal-bruhat-small/)
  check 18 rank-one complements and two joined matrices over the rationals.
- [General low-rank controls](../runs/20261008T043500Z-lowrank-bruhat-bound/)
  check 360 exact updates of dimensions 4 through 24. A rank-one upper
  shear provides a counterexample to the stronger false claim that only
  d pivots can be off diagonal.
- [Joined kernel controls](../runs/20261008T044500Z-joined-bruhat-holes/)
  check 54 h6/h7/h8 matrices, all kernel equations, forbidden columns,
  rank, diagonal counts, run counts and strict child shrinkage.
- [Independent pivot audit](../runs/20261008T0439Z-review-pivot-batching/)
  includes general rational factorizations, h51 triple frequencies,
  segmented arithmetic, arbitrary-width addresses and negative controls.
- [Independent forbidden-column audit](../runs/20261008T0443Z-review-pivot-forbidden/)
  reconstructs fresh joined matrices and a nonorthogonal negative control.

The prospective two-family exact saving is
`1058685652786963/(2*10^23)`, approximately `5.293428263934815e-9`.
It is a recurrence candidate, not the published multiplication exponent
at this checkpoint. Complete tape scheduling, row padding and final
conditional assembly are being reviewed separately. Optional additional
data edges have separate exploratory certificates and have not been
silently folded into this value.
