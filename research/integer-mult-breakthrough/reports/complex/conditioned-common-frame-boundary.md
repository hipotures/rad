# A finite boundary for nonunitary diagonal common frames

**EXACT FINITE CERTIFICATES / REFUTED WITHIN STATED SCOPE.** A complete
three-bit screen found no recursive-rank improvement from the specified
nonunitary right diagonal perturbations of Clifford common frames. The
screen allows more than unit phase gauges: every admitted row and column
scale is explicitly a Gaussian-dyadic unit, with a retained inverse.

## Question and intended leverage

The current complex characteristic cannot reach the target by improving its
root certification alone. A common-frame mechanism that lowers several paid
edge widths at once could change the recursive child distribution. Existing
Lagrangian results cover unitary Clifford frames; they do not rule out
nonunitary frames. This experiment asks whether simple conditioned frames
can supply such a change before investing in a larger synthesis search.

For each of the 135 three-bit Clifford representatives `F`, form `F D`.
The diagonal `D` changes selected records by one of `1+i`, `(1+i)^(-1)`,
`2`, or `1/2`. Four record predicates are screened independently: the
singleton address 7, the conjunction of address bits 0 and 1, odd address
parity, and address bit 0. The 64 terminal frames are the symmetric binary
graph-phase operators. Thus there are 2,160 candidates and 138,240 directed
candidate-to-terminal edges.

## Exact edge interface

A recognized edge is a disjoint sum of Walsh-equivalent blocks. Each block
of size `2^r` uses one literal `C^tensor(r)` child. Input/output permutations
and scales are recorded separately. A scale must be a unit of
`Z[i,1/2]`, exactly `i^s (1+i)^e`; a nonzero arbitrary rational or Gaussian
number is not accepted merely because it has a rational inverse.

Recognition checks the actual coefficients, disjoint square support blocks,
power-of-two sizes, all dephased cross ratios, the complete binary Walsh row
group, explicit row/column address labels, and exact reconstruction. Both
negative valuations and nontrivial fourth-root factors are retained.

The classifier permits nonuniform block ranks. In this complete experiment,
all admitted profiles happen to be uniform: eight scalar blocks, four rank
one blocks, two rank two blocks, or one rank three block. This observation is
specific to the screened finite family.

## Results

| Conditioning predicate | Exact edges | Admitted edges | Candidates with a single Clifford dominator |
| --- | ---: | ---: | ---: |
| Singleton address | 34,560 | 792 | 540 / 540 |
| Two-bit conjunction | 34,560 | 1,824 | 540 / 540 |
| Odd parity | 34,560 | 7,680 | 540 / 540 |
| One address bit | 34,560 | 7,680 | 540 / 540 |
| Total | 138,240 | 17,976 | 2,160 / 2,160 |

Every candidate has at least one admitted endpoint. For each candidate, a
retained certificate gives one existing Clifford frame whose rank is no
greater at **every** admitted terminal. Consequently this family cannot
improve the sum of ranks for any terminal multiset. Since the ranks are
uniform, the comparison also orders finite tensor widths directly: `f r`
is at least `f r_old` on every edge. No mean-rank or asymptotic concentration
argument is needed for this particular result.

This remains an optimistic rank comparison. It already fails before paying
the new scalings, their intermediate precision, any nonlinear router, and
any complete dirty scalar chronology. Adding those costs cannot reverse
the dominance result. The screen does not exclude other nonunitary
operators, several children per edge, or jointly changed source geometry.

## Controls, failure, and independent review

Three bounded tests pass. They check 100 canonical Gaussian-unit round trips,
24 independently written literal forward/inverse block pairs, 768 complete
arbitrary-dirty field values, and deliberate missing-inverse, nonunit-entry,
and invalid-Walsh corruptions. The oracle constructs each coefficient as a
product of rational `(1+i)/2` or `(1-i)/2` factors; it does not use the
producer's dephased formula to define the expected matrix.

The initial implementation had the wrong fourth-root sign for denominator
powers. Its first control and screen stopped immediately. The correct
identity is `2^(-d) = i^d (1+i)^(-2d)`. The failed source and log remain
unchanged; the zero-context recovery patch reproduces its exact source hash
in an isolated copy. A first recovery-command attempt used an absolute
`git apply --directory` and was rejected before applying anything. The
relative-directory reproduction passed.

The [independent import-free review](../transfers/conditioned-frame-independent-review.md)
accepts all 16 literal fixtures, arbitrary dirty inverses and the exact phase
controls. It also independently audits all 2,160 dominance rows and their
17,976 admitted edges; it does not reclassify all 138,240 producer edges.
These remain scoped finite certificates with internal mathematical review.
There is no native compiler or exponent claim.

## Reproduction and provenance

Run from the repository root:

```bash
python3 research/integer-mult-breakthrough/code/complex/test_conditioned_frames.py
python3 research/integer-mult-breakthrough/code/complex/conditioned_frame_screen.py \
  --family singleton --output /tmp/fresh-conditioned-singleton.json
```

Repeat the second command with `pair-control`, `parity`, and `bit`, always
using a fresh output. The implementation uses Python standard-library exact
integer Gaussian dyadics and fractions; no floating point or external
solver is involved. The four discovery workers completed in 2.20–3.64
seconds each on this host.

The [run protocol](../../runs/20261009T002708Z-complex-conditioned-frames/protocol.json)
pins every effective authored dependency, commands, worker allocation,
Python version, and input family. The [compact results](../../runs/20261009T002708Z-complex-conditioned-frames/results/summary.json)
state exactly which complete dominance rows were omitted and record their
unchanged original hashes. The [literal fixture](../../fixtures/complex/conditioned-frame-cases.json)
retains forward/inverse matrices and normal forms at each rank for every
predicate. The [failed attempt](../../runs/20261009T0025Z-complex-conditioned-phase-failed/report.md)
and [recovery patch](../../fixtures/complex/conditioned-phase-failure-recovery.patch)
preserve the phase-convention failure. Complete ignored outputs are
regenerable by the pinned commands; publication archives are indexed by the
coordinator.

## Consequence for the next hypothesis

Changing only these diagonal conditioning factors has no mathematical
leverage toward the target. A useful replacement must alter actual
operators or shared source/center chronology, rather than repeat this
family with more scalar exponents.
