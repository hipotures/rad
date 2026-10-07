# Exact parameter optimization and the Gaussian dimension boundary

Campaign `20261007T222521Z`, immutable start 2026-10-07 22:25:21 UTC,
deadline 2026-10-08 08:25:21 UTC. This continues the reviewed
[weighted Gaussian](downstream-weighted-gaussian.md) and
[blocked convolution](downstream-blocked-gaussian.md) improvements.
It optimizes their parameters; it does not introduce another scalar
construction or claim an unrestricted optimum.

## Strict composed witnesses

The [exact certificate](../runs/20261007T230416Z-downstream-parameter-optimum/results/certificate.json)
supports these rational savings in the same fixed finite-alphabet,
fixed-tape conditional model:

| Physical side roles at h=50 | Supported kappa | Ratio to advertised 2^-59, rounded downward |
|---|---|---|
| 509194, unchanged upstream graph | `4394450262707/10^30` | `2.533228104400` |
| 494250, aligned global pair ordering | `1163435943033/(25*10^28)` | `2.682700635910` |
| 487650, retained controllers | `4775622313539/10^30` | `2.752958831579` |

The last composition takes the parent branch's independently verified
physical-role count. Its scalar restoration, frame inclusion,
nondegeneracy, endpoint, and rank certificates remain separate requirements.
The count formula uses the actual physical roles `R`, not an assertion that
every construction has `R=additions+outputs`.

The unchanged finite graph row isolates the substantive downstream mechanism.
The larger composed rows also incorporate independently changed circuits.
Within each row, using tighter primitive logarithms and moving parameters
toward their strict optimum spends existing mathematical margin. It should
not be mislabeled a new Gaussian or circuit construction.

## Exact primitive saving, not decimal rounding

For the h=50 bit graph, `v=19600`, `m=125000`, and

```text
N=v^3,
W=2N+2v^2(R+50),
D=N-6v^2*50^2,
s=Wm-D,
eta=D/(Wm).
```

The primitive exponent saving is `-log(1-eta)/log(m)`.
The checker encloses its numerator with eight terms of the rational atanh
series and its denominator with 24 terms after reduction to `[1,2]`.
Both error tails are bounded rationally. The chosen saving is the exact
lower enclosure multiplied by `1-2^-128`, providing an explicitly positive
primitive gap. No decimal is used for acceptance. The retained complex
network is treated by the same exact logarithm procedure, rather than keeping
its convenient earlier saving `1/10^11`.

The certificate also verifies the complex construction's positive spare
coordinate condition and `2<=s_complex<m^5` for the stopped guard.
The starting upstream revision remains
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.

## Balance the packed and leaf costs exactly

Write `a=1-tau` for the bit saving, `b=1-sigma` for the complex saving,
`x=1-beta`, and `q=1-lambda_prime`. For a fixed stopping exponent, the
original audited layer inequalities imply

```text
q < a-(1-a)c/beta,
q < b*(1-beta),
final saving <= epsilon*min(a*c,q).
```

Balancing the first two terms in the final minimum gives
`c=a*beta/(1-a+a*beta)` and
`M(beta)=a^2*beta/(1-a+a*beta)`. This increases with `beta`, whereas
the leaf cap `b*(1-beta)` decreases. Their unique intersection in `(0,1)`
is determined by the smaller root

```text
a*b*x^2-(b+a^2)*x+a^2=0.
```

The checker encloses this root by 128 rational bisections. It chooses `x`
at the upper endpoint, so the leaf inequality has strict slack, and takes
`c=(1-2^-32)*a*beta/(1-a+a*beta)` to make the packed inequality strict.
Set `q=a*c`, `lambda_prime=1-q`, and put `lambda` halfway between
`lambda_prime` and `(1-a)*(1+c/beta)`. This supplies a concrete rational
parameter witness, rather than asserting attainment of a strict supremum.

The dimension and scalar parameters are

```text
epsilon=(1-2^-20)/2,
delta=(1/2-epsilon)/4=2^-23,
C1=2.
```

The final kappa is the largest multiple of `10^-30` strictly below the
exact minimum margin. Its absorption gap is positive. Every remaining
Gaussian, guard, prime, prefix, leaf, layout, and scalar constraint is checked
exactly. The fixed positive gap absorbs all retained logarithmic factors.

The refined dimension needs a new Gaussian cutoff
`b_input>=2^16777216` (here `b_input=ceil(log2 n)`, distinct from the complex
saving denoted `b` above). Since
`1/2-epsilon=2^-21` and `184<2^8`, this proves
`46*b_input^(epsilon+1/2)<=b_input/4`. All other retained eventual
cutoffs still apply. These are asymptotic witnesses; the enormous cutoff is
not a practical performance claim.

## A scoped upper bound and what tuning cannot improve

Within the original packed recurrence and this Gaussian model, the exact
parameter supremum for given primitive savings is
`b*x_star/2`, where `x_star` is the smaller balance root above. It is
unattained because the inequalities are strict. The checker uses the upper
primitive saving enclosures and an upper root enclosure to bound the entire
parameter family. For each of the three fixed graphs it verifies that this
ceiling lies below `2^-57`. This excludes that next dyadic target only for
these graphs and the retained analysis, not other circuits or inverse methods.

A simpler upper bound is `kappa<a^2/2`. Indeed, if `c<=a`, then
`a*c<=a^2`; if `c>=a`, the packed inequality gives
`q<a-(1-a)c/beta<a^2`. The Gaussian dimension is below `1/2`.

The dimension restriction is stronger than the prime-interval or guard
requirements alone. It follows from retained Gaussian normalization even
if all axes use different widths and prime ratios. Let
`theta_i=t_i/s_i-1>0`. The source capacity requires

```text
T/S=product_i(1+theta_i)<2.
```

Expanding the product gives `sum(theta_i)<1`. If every inverse retains
the contraction condition `alpha_i^2*theta_i>1`, Cauchy's inequality gives

```text
sum_i alpha_i^2 > sum_i 1/theta_i
                   >= d^2/sum_i theta_i > d^2,
gamma=2sum_i alpha_i^2 > 2d^2.
```

Thus `gamma=o(p)` requires `d^2=o(p)`, so a power law
`d=Theta(p^epsilon)` necessarily has `epsilon<1/2`. Allowing nonuniform
prime gaps or Gaussian widths does not evade this obstruction. Any fixed
source-volume ratio `T/S<C` gives the same quadratic power restriction,
with a different constant. This is a scoped normalization obstruction,
not a lower bound on all multiplication algorithms.

## Guard and prime estimates considered

The guard's use of a square-root piece count is loose. The exact stopped
one-piece depth is bounded by `d^(5-4beta)` using `s_complex<m^5`;
the base-m piece count is `O(log d)`. Therefore, for every fixed positive
`zeta`, a changed fixed constant supports guard exponent
`C1=5-4beta+zeta`, approaching one as `beta` approaches one.
This is a valid possible precision refinement, but it cannot increase
kappa while the Gaussian scaling obstruction above remains active.

Likewise the current prime proof's condition `log(r)>8d` forces
`epsilon<1/2` only because it invokes a convenient quantitative interval
bound. It is not a general obstacle to finding the needed primes.
Baker, Harman and Pintz's primary result gives a prime in intervals
of length `x^(0.525)` for all sufficiently large `x`. Since
`x=2^Theta(p^(1-epsilon))` and `d` is polynomial in `p`, for every fixed
`epsilon<1` the requested interval of length `x/(4d)` eventually contains
more than `d` disjoint short intervals of that form. Their primes are
distinct. A deterministic trial-division scan still costs `n^o(1)`.
Replacing the convenient interval lemma therefore could relax prime
selection, but does not remove the independent Gaussian normalization limit.

Primary reference: R. C. Baker, G. Harman, and J. Pintz, *The Difference
Between Consecutive Primes, II*, Proceedings of the London Mathematical
Society 83(3), 532–562 (2001), Theorem 1;
[publisher record](https://londmathsoc.onlinelibrary.wiley.com/doi/10.1112/plms/83.3.532)
and [paper PDF](https://www.cs.umd.edu/~gasarch/BLOGPAPERS/BakerHarmanPintz.pdf),
checked 2026-10-07. The paper's primary theorem was inspected; this is a
prospective replacement dependency, not one needed by the current witness.

## Reproduction and next question

```sh
python3 -B research/integer-multiplication-bounds/code/downstream_parameter_optimum.py \
  --upstream /path/to/pinned/integer-mult-bounds \
  --roles 509194 494250 487650 \
  --output /tmp/downstream-parameter-optimum.json
```

The exact code is
[downstream_parameter_optimum.py](../code/downstream_parameter_optimum.py).
It uses the standard library, deterministic rational bisection, and exact
series bounds. No solver or random seed is involved. The physical-role
input is accepted only as a count; its mathematical realization is certified
by the separate finite branch.

The next consequential analytic question is whether a different Gaussian
inverse or normalization can reduce the total source amplification below
the retained `2*sum(alpha_i^2)`, with a compatible fast numerical algorithm.
Guard and prime tuning alone are now known to leave that boundary intact.
