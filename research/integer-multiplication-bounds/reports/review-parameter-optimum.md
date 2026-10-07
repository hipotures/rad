# Independent exact audit of the parameter balance

The saved parameter witness passes an independent arithmetic and analytic
audit. This review reads the saved certificate without importing its
producer, re-derives the bit and retained complex network counts, encloses
the logarithms with longer exact rational series, and evaluates all retained
layer and revised assembly inequalities.

Campaign interval: 2026-10-07 22:25:21 UTC to 2026-10-08 08:25:21 UTC.
Reference revision: `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.
The numerical mechanism and its precision/tape proof are separately reviewed
in [review-gaussian.md](review-gaussian.md). This parameter audit does not
turn the upstream conditional theorem into an unconditional result.

## Analytic balance and root orientation

Let `a` be the bit primitive saving, `b` the complex primitive saving,
`beta` the stopping exponent, and `q=1-lambda_prime`. The retained
inequalities bound the final saving by

```text
epsilon*min(a*c, a-(1-a)c/beta, b(1-beta)).
```

For a fixed `beta`, the first term increases with `c` and the second
decreases. Their balance gives
`c=a*beta/(1-a+a*beta)` and
`M(beta)=a^2*beta/(1-a+a*beta)`. This function increases with `beta`,
while `b(1-beta)` decreases, so there is exactly one maximizer of their
minimum. Writing `x=1-beta`, its equation is

```text
a*b*x^2-(b+a^2)*x+a^2=0.
```

For the actual small primitive savings, this polynomial decreases on
`[0,1]`, is positive at zero, and negative at one. The certificate brackets
the unique root, chooses `x` at the upper endpoint, and reduces `c` by
the factor `1-2^-32`. Thus the leaf and packed inequalities are strict.
The chosen `lambda` lies strictly between the packed threshold and
`lambda_prime`. The checker independently verifies these exact signs.

The optimizer is monotone in either primitive saving: for each fixed
`beta`, `M(beta)` increases with `a`, and the leaf term increases with
`b`; maximization preserves this order. Using the upper primitive
enclosures therefore gives a valid upper bound on the entire stated
parameter family. Its supremum is `b*x_star/2`, because the revised
Gaussian cost restricts `epsilon<1/2`. This is a scoped model ceiling,
not a limit for other circuits or inverse algorithms.

## Evidence and strict witnesses

The authored checker
[review_parameter_audit.py](../code/review_parameter_audit.py) reads
`runs/20261007T230416Z-downstream-parameter-optimum/results/certificate.json`.
The exact source certificate SHA-256 is
`2a6e09c391321e57f5aca2d8a883b2c6ed97e669d2162180403862be3623df05`.
It encloses the deficit logarithms with 20 terms and integer logarithms
with 48 terms, compared with the producer's 8 and 24 terms. It checks
29 retained strict inequalities for every row, recomputes all seven final
margins, and verifies the largest decimal-grid rational strictly below
their minimum.

| Physical roles | Independently accepted kappa |
|---:|---|
| 509,194 | `4394450262707/10^30` |
| 494,250 | `1163435943033/(25*10^28)` |
| 487,650 | `4775622313539/10^30` |

All rows retain strict absorption, correct root orientation, and a scoped
upper saving below `2^-57`. The enormous eventual cutoff
`b_input>=2^16777216` is arithmetically sufficient for the refined
Gaussian normalization constants. It is an asymptotic witness, with no
practical speed claim. Physical role inputs require their separate mixer,
frame, endpoint, and rank certificates.

## Scope of the normalization boundary

The report's nonuniform-width argument is correct under its explicit
sublinear-normalization requirement. From `product(1+theta_i)<2`,
`alpha_i^2 theta_i>1`, and Cauchy's inequality one obtains
`gamma=2sum(alpha_i^2)>2d^2`. Hence `gamma=o(p)` excludes power-law
dimension `d=Theta(p^epsilon)` with `epsilon>=1/2`.

The bound `gamma>2d^2` alone does not exclude `d=c sqrt(p)` under only
`gamma<=p/24`: a sufficiently small fixed `c` can fit that linear budget.
This caveat does not change the accepted witnesses or their scoped
ceiling, because the current Gaussian cost inequality independently
requires `epsilon<1/2` for a positive exponent saving. An inverse change
that lowers the contraction requirement would need a new normalization
and assembly analysis.

Reproduce from the repository root:

```sh
python3 -B research/integer-multiplication-bounds/code/review_parameter_audit.py \
  --certificate research/integer-multiplication-bounds/runs/20261007T230416Z-downstream-parameter-optimum/results/certificate.json \
  --output "$OUT"
```

The fresh `review-parameter-audit` run records interpreter version, exact
input and source hashes, and the compact outcomes. No optimization solver,
floating-point acceptance threshold, or random seed is used.
