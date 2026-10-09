# Nonlex scan flux and native boundaries

## Model and exact cross-cut lemma

This is a separate algebraic discriminator for one-bank scan products.
The Boolean zeta target retains its original address labels. Each factor
is an inclusive prefix or adjacent difference in an arbitrary address
order, with nonzero address-diagonal gauges. Independent endpoint
permutations require their own cut-rank charge. Dirty-bank shears,
projections, and arbitrary non-diagonal amplitude wrappers are outside
the result.

For a coordinate bit `b`, cut rows at `b=1` and columns at `b=0`. For
an arbitrary complete order `pi`, let `r_b(pi)` be the number of adjacent
`0 -> 1` changes of bit `b` along the order. Both scan kinds have cross
rank exactly `r_b(pi)` over every field.

For a prefix, every 1-run after a positive transition has one nested
row pattern. Initial 1-runs give zero cross rows and final 0-runs give
zero cross columns. Assign a row to its latest positive transition and
a column to its next positive transition. The whole cross matrix is
`E L_r F`, with selection/replication matrices `E,F`. Choosing the first
1-row and immediately preceding 0-column at each transition gives a
unit lower-triangular minor. For a difference, only those adjacent
transition pairs survive, and the same minor is `-I_r`. This also covers
`r=0`, orders beginning in a 1-run, and orders ending in a 0-run.

Nonzero diagonal gauges preserve cross ranks. For any two matrices in
the same fixed cut, `(AB)10=A10 B00+A11 B10`, so the product cross rank
is at most the sum of the factor cross ranks. Every zeta coordinate cut
is a unit smaller-zeta matrix of rank `N/2`, where `N=2^f`. A word with
scan orders `pi_1,...,pi_s` must therefore satisfy

```
sum_i r_b(pi_i) >= N/2   for every bit b,
sum_i sum_b r_b(pi_i) >= f N/2.
```

The second inequality is an arbitrary-order flux obstruction, not a
lexicographic assumption. It allows cancellation, arbitrary nonzero
gauges, and every field. Independent permutations at either boundary
can change the target cuts and are not silently free factors.

The coordinator's independently written source binds the same lemma,
including initial/final-run edge cases:
[scan_order_cut_rank.py](../../code/obstructions/scan_order_cut_rank.py).
This report's finite engine does not import that source.

## Orders with bounded Hamming jumps

Let `d_H` denote Hamming distance. Telescoping individual coordinate
changes gives

```
2 sum_b r_b(pi) = sum_j d_H(pi[j],pi[j-1])
                  + weight(pi[N-1]) - weight(pi[0]).
```

If each adjacent jump has distance at most `H`, one scan has total flux
at most `(H(N-1)+f)/2`. Thus a word of such scans needs

```
s >= f N / (H(N-1)+f).
```

For fixed `H`, the count is linear in `f`. In particular Gray paths have
`H=1`, requiring at least `f` scans: for `f>=2`, the displayed ratio is
strictly above `f-1`, since `2^f>(f-1)^2`. This is a support/rank bound,
not a tape-time lower bound.

For an axis-permuted lexicographic order, a bit at position `t` from the
most significant end has rank `2^(t-1)`. The sum is `N-1`, giving the
separate lexicographic bound `s > f/2`. Dense Hamming jumps are a real
escape from that order-specific obstruction.

## An exact high-flux order

Define the involutive binary linear map

```
P(x) = x XOR ((x AND 1) * (2^f-2)).
```

It toggles every higher bit when the low bit is one. Use the order
`pi[j]=P(j)`. Its endpoints are zero and one. Consecutive even-to-odd
steps complement all `f` bits; the intervening steps restore much of
that change. Its total Hamming path length and positive flux are exactly

```
path_length = N(f-1)+1,
positive_flux = N(f-1)/2+1.
```

The individual cross ranks are `N/2` for bit zero and
`N/2 - (N/2)/2^b` for bit `b>=1`. This leaves constant-count scan words
plausible under the aggregate flux condition. It is a structural escape
from low-flux orders, not a found zeta word.

## Finite evidence and field scope

Twenty-five complete order profiles at widths `f=1,...,5` check natural,
bit-reversal, Gray, the complement shear, and a seeded arbitrary order.
For every profile and both scan kinds, exact rational elimination agrees
with the positive-transition count and the complete unit minor. The
random seed is `20261009222`.

A separate four-worker exact `F_3` search checked 128 three-scan cases
whose orders are natural or complement-shear:

| Width | Cases | Exhaustive finite exclusions | Finite positives |
| --- | ---: | ---: | ---: |
| `f=2` | 64 | 56 | 8 |
| `f=3` | 64 | 64 | 0 |

Because real units `+/-2^k` reduce nonzero modulo three, the finite
negatives exclude those units for these chosen orders. They exclude
neither Gaussian coefficients nor more general address orders. A finite
positive alone is not a characteristic-zero lift. The selected
natural/bit-reversal characteristic-zero proof is retained separately
in [the three-scan report](three-ordered-scans-and-dyadic-lift.md).

Evidence:
[high-flux run](../../runs/20261009T102814Z-synthesis-nonlex-scan-flux/report.md).
Source:
[nonlex_scan_flux_probe.py](../../code/synthesis/nonlex_scan_flux_probe.py).

## Native and precision obligations

The address shear has concise binary metadata, but a formal coordinate
rename is not automatically a paid payload route. A paired complete-slot
linear-mask word can conditionally implement `P` and `P^-1` using an
immutable donor and a restored companion; that supplies neither a
selected-orbit prefix layout nor the whole scan's native endpoint.
Every complete record, guard plane, permutation, exceptional correction,
scratch accumulator, and inverse route remains charged.

The whole prefix `L_N` has maximum row `L1` norm `N=2^f`. Large support
at linear scalar work may require `f` additional magnitude bits even
before other stages. Diagonal scales can increase magnitude or dyadic
grid height further. A normalized complex-transform conjugation must
bind every prefix, full record width, common grid, and local arithmetic
temporary; target zeta's own large norm is not by itself an exclusion.
No high-flux scan supplier, recursive moment, or kappa is asserted here.

The useful next discriminator is an explicit multipath/bank word or a
native high-flux ordered endpoint with paid record motion and precision.
Expanding the already excluded chosen-order finite family would not
answer that question.

## Reproduction

From the research worktree, use a fresh output path:

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/nonlex_scan_flux_probe.py --workers 4 --output research/integer-mult-breakthrough/work/synthesis/FRESH-flux/results
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_three_scan_components.py --component flux
```

The bounded standard-library wrapper regenerates all finite cases and
order profiles, reconstructs an actual corrupted-rank cut for rejection,
and freezes its complete imported source closure. Its optional `--output`
must name a fresh file. The readable run summary states omitted row data
and links the unchanged original full evidence for publication.
