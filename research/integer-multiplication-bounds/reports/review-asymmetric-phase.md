# Independent audit of unequal motifs composed with the phase inverse

The selected `p=52,q=48` phase composition passes independent count,
logarithm, recurrence, guard, numerical-scaling and cutoff checks. It is
uniquely best within the supplied 121-pair grid, even when every other
pair is compared against a favorable analytic guard-family ceiling.
This is a conditional conclusion using the separately reviewed finite
tensor transfer and phase-cell inverse. It is not a global optimum over
circuits or a new proof of the original complete multiplication theorem.

The campaign clock remains 2026-10-07 22:25:21 UTC to
2026-10-08 08:25:21 UTC. Pinned reference:
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.

## Independent selected-witness audit

The input is the completed repaired root composition
`20261008T000209Z-asymmetric-phase-repaired/certificate.json`, SHA-256
`0822291caa6c85f689bbfbcb9f4356eabab3acfb59792d1134c691fb380c1d52`.
The first producer attempt's integer/string metadata comparison repair
does not alter any equation. Its original source/log are retained
separately by the parent.

The finite counts are independently derived by
[review_asymmetric_motif.py](../code/review_asymmetric_motif.py), and
the complete rational tensor joining is proved in
[review-asymmetric-motifs.md](review-asymmetric-motifs.md).
The analytic inverse, precision, tape and guard transfer is reviewed in
[review-phase-cell-inverse.md](review-phase-cell-inverse.md).
This fresh checker reads the composed certificate without importing its
producer. It recomputes the counts and primitive logarithms, checks
balance-root signs, derives all 32 strict parameter conditions, every
exponent margin and the strict 10^-30-grid absorption, and recomputes
all four explicit cutoffs.

The optimized witness gives

```text
kappa = 1923817389583 / (2*10^29)
      > 5.545026098467 * 2^-59
      > 11 / 2^60.
```

Its counts remain `W=435202334195200`, `L=3192459212800`,
`N-2L=2062620934400`, `m=129792`, and
`s=56485779297242464000`, with side roles `Rp=549120,Rq=426624`.
The selected conservative phase row also passes, with
`kappa=1731441236329/(2*10^29)>2^-57`.

| Optimized explicit requirement on `log2 b` | Cutoff |
|---|---:|
| Sublinear Gaussian scale | 4,339,682 |
| Logarithmic alpha prerequisite | 6,149,507,232,401 |
| Full guard constant | 436,207,616 |
| End-cell/interior separation | 19 |
| Common maximum | 6,149,507,232,401 |

The BHP prime theorem and retained original interfaces have additional
eventual thresholds. These statements are asymptotic; they do not imply
practical performance. The root's eight uniform phase regressions were
already independently checked in the frozen phase audit. This new
checker confirms that their successful reports are present and separately
audits the two selected unequal rows; it does not rerun those eight
producer regressions.

## A ranking certificate independent of sorting

Let `a,b` be the bit and complex primitive savings. At the original
packed/leaf balance root `x=1-beta`,

```text
bx = a^2(1-x)/(1-ax).
```

Since `1-ax>=1-a`,

```text
x <= a^2/[b(1-a)+a^2].
```

The phase-guard objective at its balance is bounded by
`bx/(1+4x)`. This expression increases with `x`; the optimization
objective also increases with either primitive saving, by pointwise
comparison of the packed and leaf terms before taking their supremum.
Therefore independent upper enclosures `a_up,b_up` give the conservative
ceiling

```text
x_up = a_up^2/[b_up(1-a_up)+a_up^2],
candidate_kappa < b_up*x_up/(1+4*x_up).
```

This deliberately neglects the positive guard, recurrence and absorption
slacks. The checker independently encloses the logarithmic saving of
all 121 supplied motifs, then compares the selected actual rational
kappa to that ceiling for every other pair. All 120 comparisons are
strict. The closest is uniform `(50,50)` with supplied role count
486200; the selected-to-competitor-ceiling ratio minus one is strictly
above `1355383223/10^12`, about 0.13554%.

Thus no delicate monotonicity assumption about the producer's root
rounding, rational truncation or sorting is needed. The conclusion applies
to this supplied grid. A newly calibrated graph, such as a smaller
physical role count at `h=50`, is a different finite input and must be
rescored; it is not excluded by this certificate.

## Evidence and reproduction

Fresh checker: [review_asymmetric_phase.py](../code/review_asymmetric_phase.py).
Protocol and compact result:
`runs/20261008T000519Z-review-asymmetric-phase`.
Executed interpreter: CPython 3.14.4. The earlier successful compact-result
attempt is retained externally; its final form replaces a long exact ratio
with a smaller strict rational lower bound, with arithmetic unchanged.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/integer-multiplication-bounds/code/review_asymmetric_phase.py \
  --certificate "$ASYMMETRIC_PHASE_CERTIFICATE" --output "$OUT"
```

No large individual circuit or floating-label search is repeated by this
parameter audit. The separately reviewed finite and analytic obligations
remain the explicit proof dependencies of the composed statement.
