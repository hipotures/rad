# Complex-track first discriminators

Date: 2026-10-08. Author: the complex research agent, with OpenAI Codex
assistance. This is a new campaign; historical schedules are not active.

The first decisive result is an **EXACT FINITE CHARACTERISTIC CERTIFICATE**:
the frozen PR36 complex root satisfies

    71744621/10^12 < b_root < 71744622/10^12.

The certificate `717/10^7` is therefore within 0.06224% of the true root.
Re-certifying its last digits cannot approach the required
`b > 20/189981` in the frozen beta=1/20 balanced assembly. The complete
moment at that target is rigorously greater than one. Approximately 46.7%
more component saving must come from a changed construction or ledger.

## Complete frozen profile and provenance

The input is the unchanged local axis histogram from RaD commit
`16895f7676d32c1ba9455b4bf6f668cc088b271b`, blob path
`research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008/fixtures/phase-pr36.json`.
It describes icekylinx's copied-center PR36 at upstream revision
`11817ccacb564bb7f98789c20dc11d3fece207e3` in
`CrocSwap/integer-mult-bounds`. Source notices credit Paureel's two-stage
topology, Zhihao Chen's assembly, RaD's semantic transfer and other retained
contributions; no priority is claimed for inherited constructions.

The complete characteristic is independently rebuilt from
[`pr36-local-axis.json`](../../fixtures/complex/pr36-local-axis.json) and
the pinned upstream `notes/copied-centers-complex.tex` and
`scripts/copied_centers_network.py`, read through GitHub's API.
The copied local histogram changes only `H_1 += h`, `H_h -= h` and
retains all rank-(h-1) center transforms.

At h=28, v=3276, R=78790:

| Family | Multiplicity | Width |
| --- | ---: | ---: |
| Auxiliary exterior | 2vR | 756 |
| Interstage data macro | 2v^2 | 729 |
| Copied local histogram | 2v H'_r | r |
| Physical data fronts | 4v^2 | 27 |
| Paid endpoint correction | v^2 | 1 |

The resulting m=784, W=537696432, s=421548223824 and deficit=5778864
match the pinned construction. Rational atanh logarithm tails and Taylor
exponential tails provide outward moment bounds. Only final interval
endpoints are rounded outward to a 2^-192 grid. Decimal root-finding selects
the candidate interval; exact arithmetic proves both signs.

The first run's arithmetic completed, but serialization of unrounded
rationals exceeded Python's integer-string limit. Its separate failure
record is retained. The fresh repair uses compact outward bounds and
changes no moment. Independent agent C replayed both root endpoints with
a separately implemented exact enclosure and confirmed the bracket.
This is internal agent review, not formal verification or human review.

## Wider-block scalar exclusion: refuted as the immediate route

**FINITE NEGATIVE EVIDENCE.** A new cancellation-free weighted deletion
recursion partitions each surviving source edge by its exact intersection
with the surviving vertices of touched point blocks. Blocks of size 3-5
reduce recursive ground size, but create many more retained parts.

Four workers ran scientifically distinct block sizes at h=20, base=3,
d=19, with exact formal-support checks:

| Block size | Active D additions | Relative to pair blocks |
| --- | ---: | ---: |
| 2 | 17792 | 1.000 |
| 3 | 26053 | 1.464 |
| 4 | 37330 | 2.098 |
| 5 | 47440 | 2.666 |

A second four-worker comparison at h=28 found 56770 additions for pair
blocks/base2/balanced, 57562 for pair/base3/balanced, 60942 for
pair/base2/serial, and 83862 for triple/base3/balanced. These counts are
for D alone, before E and center circuits; they are not physical-role
counts or accepted phase networks. The wider-block family is retained
as an exact reusable scalar generator but is not being swept further.

The first degree-generalization test found a real bookkeeping bug:
residual hyperedge degree and remaining omission order coincide for pair
blocks but differ for wider blocks. Two surviving vertices may belong
to one touched block. The corrected recursion reduces omission order by
the number of touched blocks, and degree by the number of chosen vertices.
Direct query-support tests for all omission sizes preserve this boundary.

## Scoped triple-center obstructions

**ANALYTICAL RESULT WITH FINITE EXACT CONTROLS.** Two simple ways of reducing
center cost cannot improve the triple construction under their stated
representation assumptions; see [the proof note](triple-center-restrictions.md).

For even h>=8, every nonzero affine incidence gather feature supported
inside a proper binary hyperplane has support span dimension h-1.
Nondegenerate possibilities are precisely a point-exclusion sum D_i or
a point-star sum G_i, up to scalar and permutation. Signed pair features
also span hyperplanes, but those hyperplanes are degenerate and require
the full h-dimensional completion in this model. A rank-h center map
using independent affine gathers therefore costs at least h(h-1) at
the retained-center return frontier. This does not cover changed shared
frontiers, nonsymmetric nonlinear features, or global phase synthesis.

For a permutation-invariant rational fitting matrix on triples with
f(1)=0 and f(3)=1, minimum rank is h for h>=7 except h=9, where it is
h-1. The h=9 frozen two-stage deficit is negative. Changing only the
two symmetric off-diagonal coefficients cannot reduce useful center rank.
This is not a min-rank lower bound for unrestricted nonsymmetric maps.

## Live weight-five hypothesis

**HYPOTHESIS WITH EXACT SCALAR AND FRAME LEMMAS.** Independent exploration
by the coordinator and this track converged on weight-five binary labels
and the dyadic fitting polynomial `(t-1)(t-3)/8`. Its odd off-diagonal
zeros permit side support at even intersections 0,2,4. A new mixed-pair
center construction eliminates singleton and total retained centers;
see [the mechanism and envelope](five-subset-mixed-pair.md).

Even a maximally optimistic internal child distribution requires roughly
R/v<32.5 at the best tested axis h=22 for the target complex saving.
The naive tenfold E2 triple-exclusion circuit is far too expensive.
Continuation requires a genuinely shared even-intersection side circuit
or a changed phase architecture. No degree-five network or larger b has
been accepted.

The first jointly weighted tree circuit reduces scalar additions compared
with separate intersection classes, but still exceeds the optimistic role
cap. Exact nodewise radicals also obstruct its monotone nested-frame
interpretation; see [the weighted-tree screen and frame witnesses](weighted-tree-and-frame-obstruction.md).

## Reproduction and verification

All commands run from the new research-branch checkout and require only
Python's standard library. Outputs must be fresh paths.

```sh
python3 -B research/integer-mult-breakthrough/code/complex/test_complex.py
python3 -B research/integer-mult-breakthrough/code/complex/characteristic.py \
  --input research/integer-mult-breakthrough/fixtures/complex/pr36-local-axis.json \
  --output /tmp/fresh-complex-root.json
python3 -B research/integer-mult-breakthrough/code/complex/block_exclusion.py \
  --n 20 --block-size 3 --base 3 --central-disjoint 19 \
  --output /tmp/fresh-block-exclusion.json
python3 -B research/integer-mult-breakthrough/code/complex/center_obstructions.py \
  --output /tmp/fresh-center-obstructions.json
python3 -B research/integer-mult-breakthrough/code/complex/five_subset_envelope.py \
  --output /tmp/fresh-five-envelope.json
```

Thirteen bounded tests exercise root signs, corrupted rank mass, negative
multiplicity, omitted paid center loss, exact wider-block query supports,
corrupted outputs, affine signed-feature boundary cases and direct
harmonic eigenvalue controls, dyadic mixed-pair recovery, optimistic role
budgets, a failed triple-polynomial substitution on five-subset labels,
an exact five-side query/corrupted-output control, independently checked
weighted-tree queries, and positive/negative nested-frame radical controls.
CI registration is assigned to the coordinator.
These checks do not certify a new all-size multiplication exponent.

The first eight attempt directories used manually allocated UTC-style names.
Those names identify attempts, not measured wall-clock start times; exact
initial starts were not instrumented. Later tree and frame attempt names
were generated from UTC at launch. Reported elapsed times use perf_counter.
