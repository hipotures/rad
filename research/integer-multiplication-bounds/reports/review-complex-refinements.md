# Independent promoted composition and central-channel refinement

Campaign clock: 2026-10-07 22:25:21 UTC to 2026-10-08 08:25:21 UTC.
Pinned input: `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.

The independently promoted 485,237-role bit circuit and accepted shared
629,617-role complex circuit compose to the strict conditional witness

`kappa = 12053467103858103170301 / (125 * 10^37)`.

The value exceeds `5.558680571643687 * 2^-59`. Independent exact counts,
longer logarithm enclosures, all 30 strict conditions per row, guards, and
parameter cutoffs pass for both conservative and tight witnesses. A separate
complex central-channel reduction is also valid and improves its finite
deficit, while leaving the earlier tight exponent unchanged.

## Promoted bit composition

The thin producer is
[downstream_promoted_complex_composition.py](../code/downstream_promoted_complex_composition.py).
Its [input result](../runs/20261008T005845Z-downstream-promoted-485237/results/certificate.json)
uses the immutable candidate and
[independent finite promotion](review-singleton-positions.md).
The adapter checks complete finite metadata, reference and source hashes,
and three exact regressions of the accepted previous assembly before
substituting the new bit role count. It preserves the accepted shared
complex construction; the reduced-center construction below is a separate
case and is excluded from this promoted headline.

The [fresh independent arithmetic reviewer](../code/review_complex_refinements.py)
retains the already reviewed derivation from `review_complex_assembly.py`
and makes the bit role count and complex central-channel count explicit
inputs. The frozen original reviewer is untouched. It recomputes finite
counts, independently encloses the logarithms more accurately than the
producer, reconstructs all margins and strict conditions, and checks the
exact decimal floor used for kappa. The input promotion SHA and compiled
program SHA must match the adapter's retained inputs.

| Promoted tight witness | Independently checked value |
|---|---:|
| Bit side roles | 485,237 |
| Complex side roles | 629,617 |
| Complex central channels | 51 |
| Active limiting family | Prefix |
| Gamma cutoff, `log2 b` | 4,508,447,825 |
| Full guard cutoff, `log2 b` | 12,665,554,117,709 |
| Phase-cell cutoff, `log2 b` | 19 |
| Common parameter cutoff, `log2 b` | 6,637,094,462,284,810,001 |

The [completed independent result](../runs/20261008T010040Z-review-complex-refinements/results/promoted485237.json)
passes 680 complete stopped decaying recurrences and all 30 strict
conditions for each of the two rows. These controls preserve the distinction
between the decaying and growing recurrence branches. The all-size proof is
the previously reviewed [complex transfer](review-complex-transfer.md) and
[phase inverse transfer](review-phase-cell-inverse.md).

The displayed cutoff combines four explicit parameter constraints. The
retained prime theorem thresholds and strict recurrence/logarithm-absorption
thresholds are additionally eventual; it is not a complete-machine input
cutoff. The result remains conditional on the pinned upstream multiplication
and unaffected lifting interfaces.

## Eliminating one complex central channel

The original central gather stores
`C_i = sum(T contains i) x_T` and `C_* = sum(T) x_T` for h point channels
plus one total channel. Their new increments satisfy
`sum_i C_i = 3 C_*`, because every source is a triple. Retain `C_*` and
`C_i` for `i != 0` and eliminate the zero channel by

`C_0 = 3 C_* - sum(i != 0) C_i`.

Substitution into the central scatter
`(sum(i in S) C_i - C_*) / 2` gives:

* If `0 in S`: `C_* - sum(i outside S) C_i / 2`.
* If `0 not in S`: `(sum(i in S) C_i - C_*) / 2`.

These equations are exact for every source column and every target row.
All scalar coefficients are `0`, `+/-1`, or `+/-1/2`, which preserves the
Gaussian-dyadic scalar interface without dividing by3.

Arbitrary initial dirty central registers need not satisfy the increment
relation. The early negative scatter and later positive scatter cancel their
initial values identically. Only the new gather increments enter the net
map, where the relation is exact. Gathering and its inverse restore all
retained dirty central registers. All central channels use the same common
frame at each stage, so changing their gather/scatter coefficients does not
alter any side frame, residual orthonormality condition, target label, or
shared-bank join.

The removed channel lowers the shared role count by `2 v^2` and the
central rank loss by `3 v^2 h`. For h50 the revised exact counts are:

| Reduced-center complex quantity | Value |
|---|---:|
| W | 498,844,821,440,000 |
| L | 2,881,200,000,000 |
| D | 9,296,672,000,000 |
| s | 62,355,593,383,328,000,000 |

The producer's fresh [central refinement](../code/downstream_complex_reduced_center.py)
checks all 19,600 gather columns and all 19,600 scatter rows at h50. Its
h8 control checks the complete 1,018-coordinate scalar basis in both
directions, including both data banks and all side/central dirty registers,
plus six signed dirty probes. Those finite measurements are producer
controls; this review independently derives the factorization and the
arbitrary-dirty argument above and recomputes the resulting counts and
parameters. It does not claim another full h50 side replay.

The [independent reduced-center arithmetic result](../runs/20261008T010040Z-review-complex-refinements/results/reduced-center.json)
also passes 680 stopped recurrences and two rows of 30 strict conditions.
With the earlier 485,360-role bit circuit, its tight kappa is exactly the
previous `96380770761102682050463 / 10^40`. The prefix constraint still
limits that row; the improved complex deficit supplies additional guard
headroom. No new exponent gain is attributed to the central reduction.
The grouped-gate guard remains valid because the central gather/scatter
operations are each a grouped matrix operation at a uniform frame; removing
one channel changes their coefficients, without adding grouped phases.

## Reproduction

The [run protocol](../runs/20261008T010040Z-review-complex-refinements/protocol.json)
records source and input hashes, actual Python3.14.4, exact commands, and
scope. Each exact-arithmetic check took less than0.02 seconds. No graph
worker or unsuccessful attempt was involved.

```sh
python3 -B research/integer-multiplication-bounds/code/review_complex_refinements.py \
  --certificate "$PROMOTED" --bit-roles 485237 \
  --promotion "$INDEPENDENT_FINITE" --output "$FRESH_PROMOTED"

python3 -B research/integer-multiplication-bounds/code/review_complex_refinements.py \
  --certificate "$REDUCED_CENTER" --bit-roles 485360 \
  --central-channels 50 --output "$FRESH_REDUCED"
```
