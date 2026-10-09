# Ballot center review and target-level role budget

The integral ballot construction is a sound scalar alternative to a
highest-degree feature basis. Its small base words and full center/null
maps were produced and checked independently by the transfer track;
see [that report](../transfers/ballot-integral-center-completion.md).
This receipt is an analytical review of its block induction and a new
complete-moment sensitivity calculation. It is not a second literal
replay of the transfer track's scalar word.

For `k=2r+1`, the subset-closed ballot family of sizes at most r has
`q=choose(h,r)` rows. Splitting features and source pivots by the new
point produces a block-upper-triangular minor. The lower-left block is
zero because those new features contain the new point and the old pivots
do not. Removing the point from the new feature and pivot yields the
claimed smaller diagonal minor. Old and new pivots are disjoint. At the
base, complement Möbius inversion and the unimodular Bier incidence
matrix give an integral minor. These steps justify the all-h determinant
induction without an odd division.

The full basis `[[M,G_nonpivot],[0,I]]` preserves the original arbitrary
dirty nonpivot coordinates. Its decoder `K_pivot*M^-1` is dyadic because
M has an integer inverse. A rational span identity alone would not prove
that property; the integral minor is essential. The forward chronology
reads the new original pivots before their diagonal basis word, so its
stated positive-incidence forward magnitude bound is also coherent.
An all-h inverse prefix bound and an actual frame chronology remain open.

## Hypothetical full profile

The [new budget source](../../code/complex/ballot_role_budget.py) asks how
many physical helpers a seven-subset proposal could afford at
`b_target=20/189981`, before constructing a large scalar word. The profile
is explicitly hypothetical. Let

```text
v=choose(h,k), q=choose(h,r), m=h^2, N=v^2,
W=2N+2vR, L0=2qh.
```

The closed center cost L0 replaces the old center cost. The fixed children
are `2vR` at width `m-h`, `2N` at `(h-1)^2`, `4N` at `h-1` and N at
one. Local residuals have total rank `2v(hR+L0)`. The conservative placement
puts that rank at width one; the optimistic placement puts it at width h.
The complete rank is `Wm-N+2vL0`. Neither placement is a compiler output.

The exact threshold follows from the moment
`Phi_b(R)=sum count*(width/m)^(1-b)/W`. Its numerator is affine in R, as
is W. A high-precision calculation proposes the integer threshold; the
published exact rational logarithm/exponential enclosures then verify
that the last allowed integer has moment strictly below one and the
next integer strictly above one.

| h,k | Max R/v, rank-one residuals | Max R/v, optimistic width-h residuals | Direct gather gate lower/v |
| --- | ---: | ---: | ---: |
| 22,7 | 5.0590 | 8.9183 | 42.5257 |
| 26,7 | 13.2256 | 23.4017 | 47.3991 |
| 30,7 | 14.3485 | 25.4870 | 50.4715 |
| 36,7 | 13.0741 | 23.3327 | 53.4103 |
| 30,5 | 11.7653 | 20.9007 | 13.8158 |
| 48,3 | 4.1830 | 7.5205 | 3.8043 |

The gate lower bound is deliberately generous. There are
`choose(h,j)-choose(h,j-1)` size-j ballot features and each belongs to
`choose(h-j,k-j)` sources. Thus the whole gather has

```text
I=sum_(j=0..r) (choose(h,j)-choose(h,j-1))*choose(h-j,k-j)
```

nonzero incidences. Removing every possible incidence in the q pivot
columns costs at most q squared. At least `I-q^2` nonpivot unit gathers
therefore remain, before all pivot-word and sign gates. An independent
complete h10,k7 incidence enumeration checks this formula against all
14,400 entries, finding5,461 nonzeros.

The four-worker [run](../../runs/20261009T022538Z-complex-ballot-role-budget/report.md)
completed in0.260 seconds and proves exact thresholds for all six rows.
Even the optimistic width-h placement fails the target at this direct-gather
gate lower bound for every tested k7 row. The one-worker
[bounded run](../../runs/20261009T022651Z-complex-ballot-role-ci/report.md)
passes the h26,k7 threshold and complete incidence control in0.142 seconds.

## Interpretation and continuation

A transplant allocating one distinct helper to every scalar gate cannot
use this direct k7 gather in the stated old master. At h26 or30 it needs
about twice as much reuse as the optimistic role budget permits, and over
three times relative to the conservative budget. A shared zeta word,
birth reuse, different retained stock or a different master may reduce
physical R independently of this scalar gate count. The gate bound is
not a physical-role lower bound for those alternatives.

The mixed-degree ballot basis remains a plausible structural component:
its integral completion and dyadic decoder avoid a real odd-denominator
problem. The next useful test is a paid reuse or shared-gather chronology,
with physical roles distinguished from scalar operations. Larger h sweeps
of the existing direct gather are unwarranted before that interface changes.
The successful k3/k5 capacity comparisons are likewise unattained
profiles, not new multiplier results.

Reproduce the bounded finite discriminator with standard Python:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/ballot_role_budget.py --workers 1 --bounded
```

The two-source closure is this budget source and the pinned published
`characteristic.py`. Discovery uses four workers without bounded mode.
No native fixed-tape implementation, complete precision guard or kappa
is certified. This is internal AI-assisted mathematical review and finite
interval arithmetic, not external peer review or formal verification.
