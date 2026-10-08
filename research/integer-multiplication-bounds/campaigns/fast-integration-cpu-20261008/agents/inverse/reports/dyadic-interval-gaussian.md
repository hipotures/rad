# Rigorous dyadic cyclic Gaussian residual certificates

Status: five finite positive certificates, three matched failures to certify,
and a frozen-word replay. This replaces floating residual estimates for these
particular runs by exact enclosures. It does not change the campaign's
multiplication exponent or instantiate its full fixed-tape analytic theorem.

The authored checker is
[dyadic_interval_gaussian.py](../code/dyadic_interval_gaussian.py). It requires
only the Python standard library. Decimal LU proposes a solution, whose
rounded integer words are preserved in the receipt. Certification does not
trust that proposal, Decimal's accuracy or a numerical exponential function.
On replay it takes the frozen words directly and skips LU entirely.

## Exact coefficient and tail enclosures

The physical lifted coefficient is the same as the separately retained
cyclic reference API:

```
q_j = floor(t*j/s+1/2), beta_j = t*j/s-q_j,
n = q_(i+h)-q_i,
a_(i,h) = exp(-pi*u*n*(n+2*beta_(i+h))).
```

Selectors and the exponent's rational numerator/denominator are computed
with integers. Pi is enclosed by Machin's identity
16 arctan(1/5)-4 arctan(1/239), using alternating series and an explicit
next-term remainder. Every reciprocal term is rounded down/up on a dyadic
grid. The Gaussian exponential is range-reduced to exp(-x/2^k), with its
argument at most one half. Its positive Taylor terms have directed integer
lower/upper bounds, with signs applied by exchanging those endpoints.
The alternating remainder is bounded by the last retained positive term.
Directed squaring k times gives an enclosure of exp(-x). Known bounds
0<=exp(-x)<=1 permit the stated clamps; they never discard a true value.

For |h|>=1, monotone selectors give |n|>=|h|. Centered phases then give
n(n+2 beta)>=|h|(|h|-1). Therefore ALL omitted displacements |h|>w have
row sum at most

```
T_w = 2 exp(-pi*u*w*(w+1)) /
      (1-exp(-2*pi*u*(w+1))).
```

The same directed oracle bounds its numerator above and denominator below.
This includes every remote periodic image and all omitted diagonal aliases.
The retained |h|<=w coefficients are folded to column (i+h) mod s, including
both actual cyclic corners. We require s>4w, so distinct retained offsets
do not collide. No cyclic coefficient is silently made zero.

## A posteriori inverse error

Let x be the exact frozen dyadic proposal and b the exact sixteenth-grid
input. Directed integer products enclose each retained row of Nx-b. Let R
bound that retained maximum residual, X=||x||_infinity and T the tail above.
The true full cyclic residual is at most R+TX.

The true diagonal is at least one. A conservative strict row gap is

```
g = min_i(1-sum_(0<|h|<=w) upper(a_(i,h))-T).
```

Counting positive omitted diagonal aliases as if they were off-diagonal
only weakens this lower bound. If g>0, choose a coordinate of maximum
error in N(x-N^-1 b). The triangle inequality gives

```
||x-N^-1 b||_infinity <= (R+TX)/g.
```

The checker stores this upper bound as an exact integer ratio and compares
it to 2^-Q by cross-multiplication. A positive verdict therefore uses no
floating arithmetic. Failure to certify is a failed sufficient bound,
not by itself a proof that the actual error exceeds the target.

## Completed finite controls

All cases use seed202610081735 and independently generated exact RHS words.
The reported powers below are conservative integer inequalities for the
stored exact upper error ratio, not logarithms evaluated numerically.

| Run | Source / target | alpha | Q | Exact error upper < | Verdict |
| --- | --- | ---: | ---: | ---: | --- |
| [near127](../runs/20261008T1740Z-interval-near127/protocol.json) | 127 / 128 | 2 | 128 | 2^-189 | Certified |
| [near251](../runs/20261008T1740Z-interval-near251/protocol.json) | 251 / 256 | 2 | 256 | 2^-317 | Certified |
| [admissible257](../runs/20261008T1740Z-interval-admissible257/protocol.json) | 257 / 264 | 8 | 384 | 2^-447 | Certified |
| [admissible509](../runs/20261008T1740Z-interval-admissible509/protocol.json) | 509 / 512 | 16 | 512 | 2^-574 | Certified |
| [near1021](../runs/20261008T1740Z-interval-near1021/protocol.json) | 1021 / 1024 | 2 | 384 | 2^-443 | Certified |

The two admissible cases have u*theta>=1 and 0<theta<=1/4. The other
three explicitly lie outside the global-locality lemma's u*theta condition;
their finite certificates instead use their independently proved positive
row gaps. This is allowed by the finite cyclic reference interface.

Three matched controls use the SAME near127 input and Q=128:

- [Drop wrap](../runs/20261008T1740Z-interval-drop-wrap127/protocol.json)
  proposes a solution after omitting cyclic corners, but verifies it against
  the full cyclic matrix. Its stored upper bound is only below 2^-16.
- [Low precision](../runs/20261008T1740Z-interval-low-precision127/protocol.json)
  retains only 112 fractional solution bits. Its upper bound is below 2^-110.
- [Narrow band](../runs/20261008T1740Z-interval-narrow-band127/protocol.json)
  retains w=1 and charges all omitted coefficients. Its upper bound is
  below 2^-33; the tail cannot be dropped to manufacture a target verdict.

All three return RIGOROUS_TARGET_NOT_CERTIFIED as predeclared. They constrain
the necessary corner, precision and tail interfaces without rewriting their
failed bounds as rigorous error lower bounds. Maximum coefficient interval
width is at most three final grid units; every assertion completed.
The full near127 frozen-word replay also certifies below the same target.
Execution times range from0.01 to2.20 seconds in this bounded Python model.
They are not fixed-tape operation counts or practical multiplication speeds.

## Reproduction and scope

Each run freezes both the checker and one-slot controller, exact flags,
source hashes, original RHS words and dyadic proposal words. For example:

```sh
python3 code/dyadic_interval_gaussian.py --source 127 --target 128 --alpha 2 --target-bits 128 --mode complete --seed 202610081735 --output <fresh-ignored-work>/certificate.json
python3 code/dyadic_interval_gaussian.py --verify-certificate results/certificate.json --output <fresh-ignored-work>/replay.json
```

Use a run's frozen code directory and exact protocol for its variation.
The default direct proposal uses dense Decimal LU and is intended only for
bounded periods. The replay can verify any supplied vector without trusting
a solution algorithm. The proof relies on the written lifted Gaussian
coefficient formula and elementary alternating-series/tail inequalities,
not on the older numerical residual receipt. The scout independently
reviewed the source and written interval directions, signed products,
Gaussian tail and diagonal-alias row-gap treatment, finding them sound.
That review is analytic criticism, not a second execution or formal proof.
