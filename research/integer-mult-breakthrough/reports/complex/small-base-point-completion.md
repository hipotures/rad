# A cheaper point-center completion is valid only at small h

Status: **EXACT SCALAR COMPONENT WITH A CONSTRUCTIVE DYADIC BASIS AND A
STRUCTURAL NEGATIVE CONTROL**. No favorable native circuit or exponent is
claimed. This component was suggested independently by the synthesis track.

## Different central topology

At h=7 or 8, two distinct five-subsets cannot intersect in one point. The
only distinct odd intersection is three. Therefore

    K'(S,T)=(|S intersect T|-3)/2

has diagonal one and all required odd off-diagonal zeros. Its rank is h,
compared with q=binom(h,2) for the earlier quadratic completion. At h=8 this
changes 28 pair features into eight point features. It is a different fitting
completion, rather than a new basis for the same matrix.

Let Gi sum sources containing point i and T sum all sources. Replace G0 by
D0=T-G0. Then

    T=(sum_i>0 Gi-D0)/4,
    G0=T-D0,
    K' target=(1/2)sum_i in target Gi-(3/2)T.

All substituted coefficients have denominator at most eight. The denominator
five from the unmodified point bank is not silently inverted.

## Dyadic completion and scalar word

At h=6, select the six five-of-six source columns. With the column missing
point zero first, D0 is a unit row and the remaining block is J5-I5:

    M6=[[1,0],[ones,J5-I5]],  det(M6)=4.

For each new point j>=6 add the pivot source `{0,1,2,3,j}`. The new point row
vanishes on all preceding columns and has entry one on the new column. Thus
the full pivot minor has determinant four for every h>=6. Keeping all other
source coordinates again gives an invertible dyadic center/null basis. The
point-basis existence is all-size; validity of this linear fitting matrix is
not all-size.

The [literal source](../../code/complex/point_center_basis.py) factors J5-I5
using the retained scalar word, adds the old point-zero pivot to each other
base output, adds the three future-pivot cross terms, and gathers nonpivot
source features. Its exact inverse restores every arbitrary input. The word
uses existing data banks with no clean or additional banks.

The total feature incidences are `6v-2binom(h-1,4)`. The complete word has
that number plus `3-h` additions, three explicit bank swaps and two scales.

| h | v | Additions | Linear fitting matrix valid? | det(2K'_pivot) |
| --- | ---: | ---: | --- | ---: |
| 6 | 6 | 23 | Yes | 7 |
| 7 | 21 | 92 | Yes | 4 |
| 8 | 56 | 261 | Yes | 1 |
| 10 | 252 | 1253 | No | -5 |

The scaled central pivot determinant is exactly 25-3h: the original point-
incidence pivot has determinant five and each column sums to five, so the
rank-one correction factors as I-(3/25)J. This nonzero minor and the h-feature
factorization certify rank h for the listed matrices. At h=10 the central
matrix still has rank h, but a distinct intersection-one pair has coefficient
-1, violating the required zero pattern. That counterexample is preserved.

Four workers completed all four full operators, inverses and four arbitrary
dyadic fields in under one second, with complete source hashes and commands
in the [protocol](../../runs/20261009T001522Z-complex-point-centers/protocol.json).
There are 134234 forward/inverse basis values and 67117 central entries across
the cases. These are exact finite payload checks, not a tape benchmark.

## Frame geometry and leverage limits

At h=7 ordinary point-star spans have dimension six and a one-dimensional
radical. D0 has a nondegenerate six-dimensional span. At h=8 all eight feature
spans have nondegenerate dimension seven. The degenerate h=7 spans require the
paid general-frame interface; a singleton normal or old projector cannot be
chosen without verifying its geometry. The scalar basis does not supply those
frame transitions.

The inherited copied-center loss h(h-1) is already 56 at h=8, whereas v is
only 56. Under that ledger the rank deficit v-2L0 is negative before any side
cost. The smaller scalar quotient alone therefore cannot cross kappa=1e-4.
A new shared release chronology would have to lower its actual center charge,
with every source/sink transition and dirty continuation paid. Simply using
the same basis on both banks with paired middle copies remains blocked by the
synthesis track's full-stock triangle argument.

The synthesis track owns a separate, stronger rank-five color completion at
h=7 and its complete incidence search. This point component supplies a distinct
h=8 test and a simple exact dyadic basis; it does not duplicate that color word
or assert that rank h is an optimal central completion.

## Reproduction

```sh
python3 -B research/integer-mult-breakthrough/code/complex/test_point_center_basis.py
python3 -B research/integer-mult-breakthrough/code/complex/point_center_basis.py \
  --h 8 --seed 20261008 --output /tmp/fresh-point-center.json
```

Only the standard library is required. All output paths must be fresh. Tests
include the odd-intersection scope failure, degenerate-star control and omitted
nonpivot-shear negative. Actual native compilation and independent literal
review are still required before promoting any characteristic improvement.
