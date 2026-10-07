# Independent audit of the weighted Gaussian estimate

Campaign `20261007T222521Z`, immutable interval 2026-10-07 22:25:21 UTC
to 2026-10-08 08:25:21 UTC. This reviews
`downstream-weighted-gaussian.md` independently against the definitions in
the pinned upstream manuscript and the constructive numerical proofs of
Harvey and van der Hoeven.

## Weighted estimate

The proposed identity is correct. Write `rho=1+theta`,
`beta_j=rho*j-q_j`, and
`g=q_(j+delta)-q_j-delta`. Then
`theta*delta=beta_(j+delta)-beta_j+g`. Substituting this equality and
expanding proves

```text
phi(j,delta) - (beta_(j+delta)^2-beta_j^2)/theta
 = rho [delta^2+g(g+2 beta_(j+delta))/theta].
```

The right-hand correction is nonnegative for integral `g` and the nearest
rounding interval `[-1/2,1/2)`. With
`W_j=exp(pi alpha^2 beta_j^2/theta)`, the correct similarity orientation
is `W^-1 E W`. Periodic aliases, including nonzero multiples of `s`, are
legitimate terms and obey the same identity. They cannot be dropped from
the diagonal of `E`.

The row-sum estimate and condition-number comparison give an unweighted
power bound, not merely convergence in a different norm. Since `W` is a
proof device only, no exponential weight is stored or applied in the
algorithm. There is therefore no added implementation precision cost from
its condition number.

The replacement cutoff `ceil(1/theta)+ceil(p/alpha^2)` gives the required
strict tail bound. For the corrected width
`alpha=ceil((32b)^(1/4))`, `p=6b`, `d<=b^(1/4)`, and
`theta>1/(4d)`, the stated quadratic inequality gives
`k<=alpha^2<p` in the claimed eventual range. The earlier width
`ceil(p^(1/4))` would establish only `k=O(alpha^2)`, not the strict
integer inequality needed to retain the displayed old numerical constant.
The corrected constant resolves that issue.

## Constructive numerical interface

The primary source is David Harvey and Joris van der Hoeven,
*Integer multiplication in time O(n log n)*, Annals of Mathematics
193(2), 563–617 (2021), DOI
[10.4007/annals.2021.193.2.4](https://doi.org/10.4007/annals.2021.193.2.4),
checked against its
[45-page author manuscript](https://www.texmacs.org/joris/nlogn/nlogn.pdf),
Sections 4.1–4.3, on 2026-10-07.

Lemma 4.11's one-step truncation and grid estimates use `alpha>=2`,
`alpha<sqrt(p)`, and the retained contraction estimate. Its window is
`ceil(sqrt(p)/(2alpha))`, and its scaled error is below `p/3` for `p>100`.
The source proof bounds the relevant exponent below by
`(|delta|-1)^2`; no stronger width inequality is needed for this step.

Lemma 4.12 propagates the one-step error through the contracting `E` map,
so completed approximate iterates remain in the disk grid and their scaled
error is below `2p/3`. The exact signed sum accumulates at most
`(2/3)kp+1` scaled error once the Neumann tail is below `2^-p`.
For `k<=p` and `p>100`, this is below `3p^2/4`. The norm bound on `J'`
then retains the disk output margin. The proof uses `alpha^4 theta>p`
to bound the old iteration count; replacing that count and proving
`k<=alpha^2` preserves both the numerical bound and its time estimate.

The manuscript must replace its lemma hypotheses and cutoff explicitly.
The original verifier still checks the original Gaussian margin; changing
only a certificate field would not establish this result. The changed
assembly margin `1/4-delta-epsilon` follows from the changed width and
retained line cost, conditional on the same imported Gaussian identities,
network transfer, and multiplication interfaces.

## Independent blocked-convolution audit

The separate construction in `downstream-blocked-gaussian.md` passes the
targeted proof audit. Its local identity is an exact expansion of a square.
It explicitly restricts the new scalar interface to `1<t/s<2` and line
lengths superpolynomial in `p`. This matters: with the proposed block
length, the `T` kernel exponent could otherwise grow as `O((t/s)p)`.
The assembly's prime intervals give `t/s<4/3` and the needed large lengths.

Only the input and output diagonal factors are normalized by `2^-sigma`;
the middle kernel is already at most one. Restoration therefore uses
`2sigma` scale bits. Folding the original `D` map into the input factor
adds no third normalization. The report's `512p` exponent bound follows
from its explicit block/window ranges. With `sigma=4096p`, normalized
coefficients lie in the unit interval. Source Lemmas 2.13 and 2.14 compute
them to the required absolute error: the positive case meets both its
value bound and `sigma<=2P` with `P=32768p`.

At most `16p` terms contribute to an output. Expanding the three factor
errors gives `O(p)*2^-P`; the report's conservative
`128p^2*2^(2sigma-P)` bound absorbs rational normalization and remains
well below the original grid unit. Exact signed integer convolution keeps
guard bits and all fractional product bits, so cancellation creates no
unstated accuracy assumption. The folded `D` tail is at most a constant
times `exp(-pi*(p-alpha^2/4))`, which is small enough for `alpha^2<p`.

Packed convolution uses a fixed number of unsigned products with digit
width exceeding the two coefficient widths plus the fan-in logarithm.
Extraction can read the integer product in the reverse direction, buffer
one coefficient, and emit increasing coordinates. Building operands,
unpacking coefficients, and clearing local work all take `O(Lp)` tape
steps. Consecutive windows overlap by `O(L)` records. A single initial
line scan can retain the needed periodic prefix/suffix; no per-block full
line traversal is needed. The unconditional 2021 multiplier is invoked
only on `O(Lp)` local bits, not the stronger bound under investigation.

The authored checker `review_chirp.py` independently checks 54,392 exact
factor identities over 11 boundary blocks at `p=128`, `s=127`, `t=151`,
and `alpha=2,10`. It uses signed complex inputs, repeated periodic input
indices, two unsigned packed products per component, and direct
high-precision truncated Gaussian comparisons. Every rounded coordinate
matches the direct reference; the largest scaled final error is 0.662.
This is numerical supporting evidence, not a rigorous all-size interval
certificate. The downstream agent separately retains rational interval
tests. An initial diagnostic mixed Python complex conversion with arbitrary
precision and reported invalid error magnitudes; a fresh retained rerun
uses `mpmath.mpc` throughout. The factor and carry checks were unaffected.

The weighted cutoff extends to `epsilon<1/2` because `d<=sqrt(b)` still
gives `alpha^4-4d alpha^2-6b>0`. The fast `E` call repeated at most
`alpha^2=O(sqrt(p))` times yields the report's line cost
`O(t*p^(3/2+delta))`, and tensor cost exponent
`1/2+delta+epsilon`. At `epsilon=499/1000`, the previous finite
Gaussian cutoff is inadequate. The replacement `b>=2^8000` suffices for
`gamma<=b/4`, using `184^1000<2^8000`; retained eventual cutoffs still
apply. This is an explicit asymptotic construction with an extremely large
initial threshold, not a practical integer-multiplication benchmark.

Compact independent numerical evidence, code hashes, dependency versions,
and reproduction instructions are in
`runs/20261007T225100Z-review-chirp/`. No exhaustive priority claim is made
for the Gaussian factorization or blocking method.
