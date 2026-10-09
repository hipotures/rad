# An integral triple-total alternative

**EXACT SCALAR COMPONENT / ALL-H SCALAR GUARD / CONDITIONAL CAPACITY.**
The total-replacement construction has a simpler triple-subset version.
Its basis and inverse are integral, and all scalar gates are unit shears or
three negations. A declared closed-release envelope crosses the required
complex saving, with less root margin than the five-subset variant. Actual
native chronology is still decisive.

## Unimodular basis

For triple sources, let `G_i` sum sources containing point `i`, and let `T`
sum all sources. Retain the total and `G_1,...,G_(h-1)`. Since each source
contains three points,

```text
G_0 = 3T-sum_{i=1}^{h-1} G_i.
```

No division by three occurs. At `h=4`, order source pivots as the triples
missing points `0,1,2,3`. Sum the last three data banks into the first to
produce the total. Then each other bank becomes `total-original_bank`,
using one negation and one addition. This is a complete invertible word:
six unit additions and three negations, with no zero initialization,
exchanges or fractional scales. Its determinant has absolute value one.

For a new point `j>=4`, append source pivot `{0,1,j}` and feature row `G_j`.
The diagonal border is one, the lower-left block is zero, and the new column
adds once to the older total and `G_1`. Thus all-h determinant remains a unit.
Append the remaining original source coordinates unchanged. Each contributes
once to the total and once to every retained point that it contains.
The complete basis and its inverse are integral for every `h>=4`.

The scalar word uses existing arbitrary data banks. Both directions require
all mixed banks to have identical actual address operators. The unimodular
proof supplies no free synchronization between the initial source frames.

## Central map and counts

For target triple `S`, scatter coefficients with denominator two are

```text
total:    3[0 in S]-1,
point i:  [i in S]-[0 in S],  i>=1.
```

Substitution gives `(intersection(S,T_source)-1)/2`, so the diagonal is one
and every distinct odd intersection has central coefficient zero. Both the
central fit and scalar basis are checked on every ordered entry and complete
input column at `h=4,6,8`, with four arbitrary dyadic fields per size.

Let `v=binom(h,3)`. The source feature nonzero count is
`4v-binom(h-1,2)`. The complete word has

```text
unit additions = 4v-binom(h-1,2)-h-3,
negations = 3,
scalar proxy R = 4v-binom(h-1,2)-h.
```

This is a proxy for the scalar word, not an upper bound on auxiliaries in a
complete unbuilt native algorithm. Central scatter, side cancellation,
source/sink transitions, echoes, physical routing and children must also be
paid. The total feature spans the full binary label space; the retained
ordinary stars have dimension `h-1` at the relevant even dimensions.
They cannot all inherit the total's or a source line's frame for free.

## Complete scalar prefix guard

Both directions preserve the input dyadic grid because all coefficients
are integers. Every forward partial coefficient is zero, one, or a single
temporarily negated original coordinate. The complete forward coefficient
row-L1 norm is at most `v`, including multiplication temporaries.

For the inverse, first unlink the nonpivot inputs. Each retained center has
coefficient minus its incidence on every nonpivot source. When withdrawing
future pivots, put `k=number of source points>=4` and `delta_i=[i in source]`.
The total coefficient on a nonpivot source becomes `k-1`; the `G_1`
coefficient becomes `k-delta_1`. These are at most two and three respectively.
The remaining base stars have coefficient `-delta_i`.

The inverse base then forms `T-G_3,T-G_2,T-G_1`. Their coefficients are
`k-1+delta_3`, `k-1+delta_2`, and `delta_1-1`; since the source has only three
points, their magnitudes are at most two. Subtracting these reconstructed
coordinates from the total, in order `3,2,1`, keeps every coefficient within
`[-2,2]`. The first `h` coordinate-column coefficients are at most two by the
same explicit base word. Untouched nonpivot rows have coefficient one.

Thus every complete inverse prefix coefficient has magnitude at most three,
giving the all-h bound `3v` for every row-L1 norm. Each coefficient-times-source
temporary has scalar coefficient `+1` or `-1`, so it obeys the same bound.
Endpoint coefficients are at most two; endpoint norm is at most `2v`.
These are analytical scalar bounds on arbitrary dirty fields, not free
normalization or bounds for intervening recursive phase children.

Four complete symbolic checks, at `h=16,32,48,64`, verify all final scalar
columns, inverse composition and every partial coefficient/temporary.

| h | v | Forward prefix norm | Inverse prefix norm | Inverse endpoint norm |
| --- | ---: | ---: | ---: | ---: |
| 16 | 560 | 560 | 1,171 | 820 |
| 32 | 4,960 | 4,960 | 12,587 | 8,556 |
| 48 | 17,296 | 17,296 | 46,531 | 31,396 |
| 64 | 41,664 | 41,664 | 115,291 | 77,532 |

The four-worker check took about 0.65 seconds. The initial inverse prefix
assertion incorrectly reused the endpoint coefficient cap of two. It failed:
nonpivot source `{4,5,6}` has coefficient three in `G_1` during future-pivot
withdrawal. The original source/log are unchanged and recoverable; the
repaired cap three and separate endpoint cap two pass. This failure does not
change the basis, decoder, counts, or previously completed capacity moments.

## Target-level capacity and boundary

Declare the same two-axis complete profile as the five-subset comparison,
but with `v=binom(h,3)`. Use `m=h^2`, `N=v^2`, `W=2N+2vR`; fixed children
are `2vR` at `m-h`, `2N` at `(h-1)^2`, `4N` at `h-1`, and `N` at one.
Place all further local rank `2v(hR+L0)` at width one. Complete rank is exactly
`Wm-N+2vL0`.

With the scalar proxy above and center cost **replaced** by conservative
closed release `L0=2h^2`, exact outward root intervals are

| h | R / v | Complex root interval |
| --- | ---: | --- |
| 44 | 3.928496 | `(0.000109391922,0.000109391923)` |
| 48 | 3.934725 | `(0.000110455647,0.000110455648)` |
| 52 | 3.939955 | `(0.000109350808,0.000109350809)` |
| 56 | 3.944408 | `(0.000107025125,0.000107025126)` |

All exceed `20/189981`; the best has about 4.9% root margin. Adding that
release to the older copied-frame analogy instead fails, with roots around
`3.41e-5` to `6.36e-5`. One full traversal and the copied-frame analogy are
retained as separate optimistic hypotheses.

This alternative is slightly weaker in the declared moment than the
five-subset total basis. Its leverage is cleaner scalar precision and a much
simpler exact word, which may matter for a paid native compiler. Identical
basis changes on paired source/sink banks still obey the synthesis track's
crossed-endpoint obstruction. The simpler matrix does not invalidate it.
No actual child profile, whole dirty phase compiler, binary transfer or
larger kappa is accepted.

## Reproduction

The sources are [triple_total_centers.py](../../code/complex/triple_total_centers.py)
and [triple_total_guard.py](../../code/complex/triple_total_guard.py). The
bounded closure checks the complete scalar word and decoder, a literal
coefficient-three negative to the old guard, and the closed versus additive
moment comparison. All use Python's standard library and exact arithmetic.

```bash
python3 research/integer-mult-breakthrough/code/complex/test_triple_total_centers.py
python3 research/integer-mult-breakthrough/code/complex/triple_total_centers.py \
  --h 48 --output /tmp/fresh-triple-total-capacity.json
python3 research/integer-mult-breakthrough/code/complex/triple_total_guard.py \
  --workers 4 --output /tmp/fresh-triple-total-guard.json
```

The run protocols distinguish literal columns, symbolic guard checks and
unattained profile moments; source identities, seeds, configurations, failed
attempt and exact recovery are retained. Independent scalar/native review
is requested before promoting this alternative.
