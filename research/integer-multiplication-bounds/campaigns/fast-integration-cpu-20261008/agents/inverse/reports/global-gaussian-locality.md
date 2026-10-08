# Physical Gaussian locality of the cyclic correction inverse

Status: new written general lemma within the retained Gaussian correction
interface. The exact weighted Gaussian identity is inherited from completed
RaD work; the spatial row-algebra inversion and phase-square cancellation
below are new to the selectively inspected RaD record. This is not a claim of
worldwide novelty. The campaign scout independently checked the identity,
orientation, phase inequality, kernel closure and periodic-alias treatment.

## Setting and inherited identity

Let `0<theta<=1/4`, `rho=1+theta=t/s`, `u=alpha^2>=4`, and
`u*theta>=1`. Extend source indices to all integers with

```
q_j=floor(rho*j+1/2), beta_j=rho*j-q_j in [-1/2,1/2).
```

Both `beta` and the physical rows are periodic with period `s`.
The correction is the periodic restriction of

```
(N x)_j = sum_(h in Z) exp(-pi*u*phi(j,h))*x_(j+h),
phi(j,h)=(rho*h+beta_j)^2-beta_(j+h)^2.
```

The `h=0` term is one. Every nonzero period-multiple alias remains part of
`E=N-I`; it is never silently dropped from the diagonal. Completed RaD's
[weighted Gaussian report](../../../../../reports/downstream-weighted-gaussian.md)
proved, for `W_j=exp(pi*u*beta_j^2/theta)`, that the lifted kernel
`F=W^-1 E W` satisfies

```
0<=F_(j,h)<=exp(-pi*u*rho*h^2), h!=0.
```

The proof uses `g=q_(j+h)-q_j-h` and the nonnegative integer expression
`g*(g+2*beta_(j+h))`. This identity is inherited, not rediscovered here.

## A lifted spatial kernel algebra

For periodic-coefficient kernels `A_(j,h)`, define

```
||A||_a = sup_j sum_h |A_(j,h)|*exp(a*|h|).
```

Kernel composition is `(AB)_(j,h)=sum_k A_(j,k)B_(j+k,h-k)`.
The triangle inequality `|h|<=|k|+|h-k|` proves
`||AB||_a<=||A||_a||B||_a`. No translation invariance is assumed.

Choose `a=pi*u*rho-ln(4)>0`. Then

```
||F||_a
 <=2*sum_(h>=1)4^-h*exp(-pi*u*rho*h*(h-1))
 <2*sum_(h>=1)4^-h = 2/3.
```

The absolutely convergent lifted inverse
`K=(I+F)^-1=sum_(k>=0)(-F)^k` therefore has norm below three, and

```
|K_(j,h)| <=3*exp(-a*|h|).
```

Restricting the operator to periodic sequences folds coefficients over
`h` congruent to the same physical displacement. Folding commutes with
composition by absolute convergence. Since `W` is itself periodic, the
physical inverse entries are the corresponding alias sums of

```
B_(j,h)=W_j*K_(j,h)/W_(j+h).
```

This construction includes paths through arbitrary wraps and all aliases.

## Exact phase-square cancellation

Put `v=theta*|h|`. For `0<=v<=1`, centered rounding gives

```
beta_j^2-beta_(j+h)^2 <=v*(1-v).
```

For positive displacement, write `beta_(j+h)=beta_j+v-k` with
`k` either zero or one. If `k=0`, the difference is
`-2*beta_j*v-v^2<=v-v^2`. If `k=1`, it is
`(1-v)*(2*beta_j+v-1)<=v*(1-v)`. Negative displacement follows by
the same calculation with the reversed interval. The estimate holds across
a phase wrap; treating `beta` as an unwrapped affine variable would miss it.

Thus, whenever `1<=|h|<=1/theta`,

```
|B_(j,h)|
 <=3*exp[-pi*u*theta*(h^2+|h|)+ln(4)*|h|]
 <=3*exp(-pi*u*theta*h^2).
```

The last inequality uses `u*theta>=1`, `pi>3` and `ln(4)<2`.
For `|h|>1/theta`, use `beta_j^2-beta_(j+h)^2<=1/4` instead:

```
|B_(j,h)|<=3*exp[-a*|h|+pi*u/(4theta)]<=3*exp(-u*|h|).
```

Indeed, `pi*u/(4theta)<(pi*u/4)|h|`, and
`(3/4)pi*u+pi*u*theta-ln(4)>u` for `u>=4`.

For an integer `1<=R<=1/(2theta)`, summing both regimes gives the
uniform row-tail bound

```
sum_(|h|>R)|B_(j,h)| <24*exp(-3*u*theta*R^2).
```

To check the constants, the short sum is bounded by a geometric series
with ratio at most `exp(-pi*u*theta)<1/2`; it contributes at most
`12 exp(-3u theta R^2)`. The long sum contributes at most
`12 exp(-u/theta)`, which is smaller because
`3u theta R^2<=3u/(4theta)<u/theta`. Circular-window tails only retain
a subset of these lifted displacements, so the same bound applies after
folding. The long-image terms are explicitly included.

## Local principal windows approximate the global inverse

The same weighted proof survives restricting all paths to any selected
physical set `I` and its periodic images. Its principal inverse `A_I^-1`
has lifted weighted kernel norm below three. The boundary operator
`A_I^-1 N_(I,I^c)` has weighted norm at most `3*(2/3)=2`.

Let every core row have circular distance greater than `R` from `I^c`.
Every destination of this boundary operator then has lifted displacement
greater than `R`. Repeating the phase-square argument and tail sum with
constant two gives boundary row norm below
`16 exp(-3u theta R^2)`.

For arbitrary input `x`, with `y=N^-1 x`, the exact equation is

```
y_I-A_I^-1*x_I = -A_I^-1*N_(I,I^c)*y_(I^c).
```

The inherited physical contraction bound gives `||N^-1||<2`; hence

```
||y_core-(A_I^-1*x_I)_core||
 <32*exp(-3*u*theta*R^2)*||x||.
```

This is a general principal-window locality result for the same cyclic
Gaussian matrix. It does not require treating the similarity weights as
computed global data, merging cells across a physical period cut, or using
a generic row-norm Neumann radius. Actual local inversion still needs the
paid structured solver, its setup, roundoff and tape layout.

## Sharper regular-phase tails

If a core row has `|beta_j|<=1/2-delta`, then for
`|h|<=delta/theta` no wrap occurs before that displacement and

```
beta_j^2-beta_(j+h)^2
 <=(1-2delta)*theta*|h|-(theta*h)^2.
```

The physical kernel is therefore bounded by
`3 exp(-2pi*u*delta*|h|-pi*u*theta*h^2)`. If `u*delta>=1`,
`delta/theta>=2`, and `R<=delta/(2theta)`, splitting the tail at
`delta/theta` yields

```
inverse row tail
 <12*exp(-6u*delta*R)+24*exp[-3u*delta^2/(4theta)],
local principal-window error
 <16*exp(-6u*delta*R)+32*exp[-3u*delta^2/(4theta)].
```

The farther term uses the global Gaussian bound at
`floor(delta/theta)>=delta/(2theta)`. In the candidate regime
`u=Theta(Q/d)`, `delta=d^-4`, `theta=Theta(d^-16)`, the regular radius
`R=Theta(d^5)` gives an exponent proportional to `Q`, while the farther
term has exponent proportional to `Q*d^7`. The exceptional radius is
`Theta(sqrt(Q/(u*theta)))=Theta(d^(17/2))` at `Q=Theta(d^18)`.

## Scope, attribution and verification status

The result sharpens the physical inverse/local-window radius and supports
an analytically consistent regular/exception split. It does not establish
fast halo assembly, packed tensor multiplication, exact setup tables, full
Gaussian precision accounting or a new complete exponent. Those require
separate implementation and paid fixed-tape arguments.

Identity credit: completed RaD weighted Gaussian analysis, with the original
Gaussian correction definition inherited from Harvey and van der Hoeven's
resampling framework. Spatial algebra and phase-square cancellation:
this CPU campaign's inverse branch, independently criticized by its scout.
General inverse-decay tools are established; no literature priority claim
is made. The scout specifically checked the completed historical report and
found the weighted-power estimate, but no spatial inverse-tail statement.

## Independent bounded controls

`../code/global_locality_controls.py` imports no producer. The completed run
`../runs/20261008T1320Z-global-locality/results/certificate.json` records
1,494,462 exact integer comparisons on five rational `(s,t)` pairs. These
check the inherited exponent identity, new phase gain, regular-phase gain,
nearest-entry lower bound and far-entry lower bound. Displacements include
both signs, the phase horizon, physical period multiples and long aliases.

At 160 decimal digits, the checker constructs cyclic matrices of sizes 61,
113 and 257, retaining period images -1, 0 and 1 and bounding omitted images
separately. It factors each matrix independently and solves all 431 basis
inputs. Three original-matrix residual rows are checked for every basis solve,
including the physical first/last rows. Every tested maximum circular inverse
row tail at radii 1, 2, 3, 4, 6 and 8 (when the stated horizon permits it)
is below the new general bound. This was a targeted changed-interface check,
not an unchanged full multiplication baseline. One CPU worker was active;
the complete run took approximately 42 seconds.

Reproduce from the repository root with Python 3.9 or newer:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B \
  research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/inverse/code/global_locality_controls.py \
  --max-size 257 --digits 160 --output /tmp/global-locality.json
```

The exact source hash is retained in the result certificate. Decimal controls
are numerical evidence, not directed interval certificates. The general lemma
rests on the written inequalities above, not on the finite PASS label.
