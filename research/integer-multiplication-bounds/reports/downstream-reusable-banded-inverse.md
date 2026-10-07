# A reusable banded Gaussian inverse and dimension below two thirds

Campaign `20261007T222521Z`: immutable start 2026-10-07 22:25:21 UTC,
deadline 2026-10-08 08:25:21 UTC. The pinned starting input is
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`. This branch follows the
[weighted estimate](downstream-weighted-gaussian.md),
[blocked Gaussian evaluator](downstream-blocked-gaussian.md), and
[exact parameter optimization](downstream-parameter-optimum.md).

## Result and status

The argument below replaces the scalar inverse, improves the stopped guard,
and changes the prime-interval proof. It supports transform dimension
`epsilon<2/3`, instead of the previous `epsilon<1/2`. The
[exact assembly certificate](../runs/20261007T232412Z-downstream-lu-assembly/results/certificate.json)
gives these fixed finite-alphabet, fixed one-dimensional tape witnesses:

| h50 physical side roles | Exact conditional kappa | Ratio to advertised 2^-59, rounded downward |
|---|---|---|
| 509194, unchanged input graph | `366204013939/(625*10^26)` | `3.377635861948` |
| 494250, aligned pair ordering | `6204988737403/10^30` | `3.576932475597` |
| 487650, retained controllers | `636749338179/10^29` | `3.670610025153` |

These are mathematical transfer claims with finite exact and rigorous
interval checks. The retained complete multiplication theorem and unaffected
tape interfaces remain assumptions. The composed finite graphs require
their separate scalar, rational frame, restoration, endpoint, and rank
certificates. The full analytic transfer and exact assembly passed the
independent [campaign review](review-reusable-banded-inverse.md). The exact
assembly checker cannot establish the analytic interfaces itself; the saved
candidate JSON reflects its earlier, pending-review generation time.

This is a substantive estimate and algorithm change. The logarithm and
packed/leaf parameter tightening are separately classified as spending
existing margin. The use of banded LU is not claimed as a discovery:
Harvey and van der Hoeven explicitly proposed it in section 4.4.2, while
leaving the more intricate error analysis aside. The new work here is the
small-separation contraction, reusable exact-rational precomputation with
O(p)-bit online factors, cyclic correction and residual audit, and the
growing-dimension transfer. Priority and broader novelty remain unclaimed.

Primary source: D. Harvey and J. van der Hoeven, *Integer multiplication in
time O(n log n)*, Annals of Mathematics 193(2), 563–617 (2021),
DOI 10.4007/annals.2021.193.2.4;
[author manuscript](https://www.texmacs.org/joris/nlogn/nlogn.pdf),
sections 4.2–4.4.2 and Lemmas 2.13–2.14, inspected 2026-10-07.

## The row estimate keeps one large neighbour

Retain the exact Gaussian definitions and permutations. Write
`rho=t/s=1+theta`, `0<theta<1`, `u=alpha^2`, and

```text
q_j=floor(rho*j+1/2), beta_j=rho*j-q_j in [-1/2,1/2),
q_(j+s)=q_j+t, beta_(j+s)=beta_j,
phi(j,delta)=(rho*delta+beta_j)^2-beta_(j+delta)^2.
```

The matrix `N=C T D=I+E` includes every periodic alias. For `delta=1`,
`g=q_(j+1)-q_j-1` is zero or one. If it is zero then
`phi(j,1)=1+2theta+2beta_j`. If it is one, nearest rounding requires
`beta_j+theta>=1/2`, and the exponent exceeds or equals that expression.
The analogous argument for `delta=-1` gives

```text
phi(j,1)>=1+2theta+2beta_j,
phi(j,-1)>=1+2theta-2beta_j.
```

Convexity in `beta_j` bounds the sum of the corresponding two weights by
`exp(-2pi*u*theta)*(1+exp(-2pi*u))`. For every nonzero integer delta,

```text
phi(j,delta)>=rho^2*delta^2-rho*abs(delta)
             >=delta^2-abs(delta).
```

The tails for `abs(delta)>=2` are bounded geometrically. For `u>=4`,
the deliberately loose consequence is

```text
||E|| < exp(-2pi*u*theta)+5exp(-2pi*u).
```

This bound does not put two worst neighbouring terms in the same row.
It applies to the original periodic matrix, not a conjugated norm.

Suppose `p>100`, `theta>1/(4p)`, and
`u>=ceil(log2(8p))`. Put `x=u*theta` and `mu=min(x,1)/4`.
Since pi>3 and e>2, the second term is less than
`5*2^(-6u)<=5/(8p)^6<1/(4p)<=min(x,1)/4`.
For `0<x<=1`, `1-exp(-2pi*x)>x/2`; for `x>=1`, it exceeds one half.
Therefore

```text
||E||<1-mu, mu>=1/(4p), ||N^-1||<1/mu<=4p.
```

The old hypothesis `u*theta>1` is thus replaced by a logarithmic lower
bound on u. A Neumann series still proves invertibility; the algorithm
below does not evaluate its p-scale number of terms.

## Truncation and a downward dyadic matrix

Let `P=256p`, `eta=2^(-P)`, and
`w=ceil(sqrt(16p/u))+2`. The assembly line length grows faster than every
polynomial in p, so eventually `s>2w`. Retain only `abs(delta)<=w`, with
the diagonal exactly one. The omitted periodic lattice terms have maximum
row sum less than

```text
4*2^(-3u*w*(w+1)) < 2^(-46p).
```

All exponents are positive for nonzero delta. Lemma 2.13 of the primary
paper computes their real exponential to error below two P-grid units.
Subtract two such units and clip at zero. The resulting real dyadic
coefficient is at most its true value, and its error is below four units.
Call the resulting circular-banded matrix `H0`. Downward approximation
preserves the row-diagonal-dominance gap mu exactly; it is not necessary
to assume a perturbed gap or infer it from finite tests. Hence

```text
||H0^-1||<=4p,
||H0-N||<8w*eta+2^(-46p),
||H0^-1-N^-1||<128p^3*eta+16p^2*2^(-46p).
```

The rational exponent numerator and denominator have O(p) bits: rho and
beta have that length, delta is polynomial in p, and u<p. Thus the
exponential interface has its stated bit complexity.

## Exact precomputation is reused across tensor lines

Remove the wrap entries of H0 to obtain a noncyclic band matrix A with
half bandwidth w. Its diagonal is one, row norm below two, and row
diagonal-dominance gap at least mu. Factor `A=L U` without pivoting.

The necessary elimination invariants are elementary. Let `g_i` denote
the gap in a current Schur row, and eliminate pivot k. Positivity of
the diagonal and the triangle inequality give

```text
g_i_new >= g_i + abs(a_ik)*g_k/a_kk,
row_norm_i_new <= row_norm_i-abs(a_ik)*g_k/a_kk.
```

In particular every Schur diagonal remains positive, every pivot is at
least mu, and every Schur row norm stays below two. L and U retain the
original lower and upper bandwidth w. Consequently, using `w<=p`,

```text
||U||<2, ||L||<=1+2w/mu<=9p^2,
||L^-1||=||U A^-1||<=8p,
||U^-1||=||A^-1 L||<=36p^3.
```

The wrap rows are among the first and last w indices. Let B be the matrix
of those `r=2w` standard basis columns, and V contain the removed wrap
rows, so `H0=A+B V`, `||B||=1`, and `||V||<1`. Precompute

```text
Z=A^-1 B, K=I_r+V Z, K_inverse=I_r-V H0^-1 B.
```

The last identity establishes both nonsingularity and the useful bound
`||K_inverse||<=1+4p`; also `||Z||<=4p`. The resulting application is

```text
x0=A^-1 b,
x=x0-Z K_inverse V x0.
```

This is the Woodbury formula with the stated orientation. It is not
necessary to solve a long cyclic recurrence on each input line.

The precomputation is performed once for each tensor axis, independent
of its input values. It can use exact rational arithmetic before rounding
the retained factors. For the P-bit dyadic matrix, determinant bounds give
O(s*(P+log s)) bits for numerators and denominators of LU factors and
inverse entries. Fraction-free elimination or ordinary exact rational
elimination therefore costs a fixed polynomial in s and p, including
bit operations. An inefficient fixed-tape implementation by ordered scans
and sequential searches still has polynomial cost; no random access is
being assumed for this step.

Here `s<=t<=r_axis=2^Theta(p/d)` and `d=Theta(p^epsilon)` grows. Thus
the total precomputation, its storage, and later cleanup take
`poly(d,t,p)=n^o(1)=o(n)`. This is a setup cost, rather than a cost
charged once for each of the roughly `T/t` input lines. Long exact
rational records occur only in this negligible setup; the online factors
have O(p)-bit records.

## Rounding the factors and bounding the online error

Round each retained factor entry toward zero on the P-grid. Keep the
unit diagonal of L exactly. Store the P-grid reciprocal of each U pivot;
online back substitution multiplies by this reciprocal, so no online
division is required. Since a pivot lies in `[mu,2)`, its reciprocal
exceeds one half. The rounded reciprocal exceeds one quarter, and its
effective diagonal `1/rounded_reciprocal` differs from the original pivot
by less than eight eta.

The perturbations in the two triangular matrices therefore have norms
at most `p*eta` and `2p*eta`. The inverse norms after perturbation are
at most `16p` and `128p^3`, respectively, by the inverse perturbation
identity. Their product differs from A by at most `22p^3*eta`.
For each forward or backward row, multiply the dyadics and accumulate
the whole dot product exactly, then round the completed coordinate once.
Products need 2P fractional bits, and the polynomial number of summands
needs only O(log p) guard bits. The local residual bounds are `2eta`
and `8eta` in complex modulus.

These residual vectors, rather than a count of t repeated error
amplifications, give

```text
||computed_x0-A^-1 b|| < 2^25*p^9*eta, ||computed_x0||<5p.
```

Round V x0, K_inverse times that vector, each row of Z times the result,
and the final difference once per completed coordinate. The exact norms
of V, Z, and K_inverse are below 1, 4p, and 5p. Their rounded dense
rows have at most 2w entries, so their matrix perturbations have norm
at most `2p*eta`. One convenient common bound for the full rounded
Woodbury application is

```text
||computed_x-H0^-1 b|| < 2^32*p^11*eta.
```

Combining this with the analytic truncation bound gives the looser,
simple interface

```text
||computed_x-N^-1 b||
 < 2^40*p^14*2^(-256p)+16p^2*2^(-46p)
 < 2^(-p-10).
```

Both terms are bounded by exact integer inequalities; for example
`log2(p)<=p` makes their exponential margins immediate for p>100.
The factors, intermediate vectors, products and accumulators have
O(p) bits. Their polynomial magnitude bound supplies O(log p) integer
guard bits. This explains why the long line length never forces an
exponential precision loss during application.

## Ordered fixed-tape application cost

Store the two band factors in row order and the upper one in the
direction of backward substitution. A sliding buffer of the last w
coordinates supplies each dot product. A full traversal and rewind of
that buffer per row costs O(wp), already within the w scalar products.
The input, forward result and backward result occupy fixed ordered tapes;
reverse scans or a value-preserving reversal restore coordinate order.
V reads only the two boundary windows. Its small vector and the dense
K_inverse calculation cost O(w^2*p^(1+delta)). For the Z correction,
scan Z by rows and scan/rewind its length-2w input vector once per row,
costing O(swp) tape steps in addition to arithmetic.

The precomputed factor tapes are rewound for each input line, costing
O(swp); they are reused and are not additional heads per axis or row.
Their ordered format and the workspace cleanup use one fixed collection
of tapes. A constant number of scalar fields and counters specify each
loop. Each O(p)-bit scalar multiplication uses the published unconditional
fast multiplier, with fixed logarithmic factors absorbed in p^delta.
The total application cost is

```text
O(t*w*p^(1+delta)) = O(t*p^(3/2+delta)/alpha).
```

The O(w^2) small calculation is included because t eventually dominates
every polynomial in p. This cost does not invoke the multiplication bound
being proved. It uses the same unconditional short-record arithmetic as
the existing blocked evaluator.

## Replacement scalar identity and contractions

Let `j=ceil(log2(32p))`, and define

```text
S_normalized=S/2,
J_normalized=N^-1/2^j,
D_normalized=D/2^(2u),
A=S_normalized, B0=D_normalized J_normalized C.
```

The exact Fourier identity is unchanged, and now reads

```text
P_s F_s = 2^(2u+j+1) B0 P_t F_t A.
```

The norms are below 3/4, 1/8 and one for the three normalized maps.
Here `||D||<=exp(pi*u/4)<2^(2u)` for u>=4. The completed inverse is
divided by 2^j and rounded toward zero to the target p-grid. Its error
is below three grid units, and its output lies in the disk. The existing
blocked construction supplies S/2 to error below four, using its
O(p)-bit guarded factors; it requires no lower bound on u*theta for S.
Lemma 2.14 supplies D_normalized to error below four, since its scale
`2u<2p` and the positive output is bounded by one. Thus the scalar
forward and inverse interfaces retain the earlier convenient error
bound p^2, with every completed output in the disk.

Tensoring yields normalization
`gamma=d*(2u+j+1)`, error below `d*p^2`, and Gaussian arithmetic time
`O(d*T*p^(3/2+delta)/alpha)`, plus the negligible setup. Ordered
selection C and the retained permutations are unchanged. Existing
nonadjacent axis movement applies with the original exact tape bounds.

## Two other estimates must change with the dimension

The old guard exponent C1=2 would prevent crossing epsilon=1/2. Its
actual stopped one-piece depth is at most `9B^2*d^(5-4beta)` from the
pinned stopped-guard proof, where `B=s_c+64(W_c+m_c+1)^3` and `s_c<m^5`.
There are at most `(m-1)*(1+floor(log_m d))` base-m pieces. For m>=3,
`log_m d<=log d<=4d^(1/4)`, so this count is at most `5m*d^(1/4)`.
For `beta>=15/16`, the combined piece depth is at most
`45mB^2*d^(3/2)`. Preprocessing, outer phases and the final shift
contribute at most 18d. Hence the existing constant

```text
C0=128mB^2
```

supports the sharper guard exponent `C1=3/2`. The exact arithmetic
and magnitude/denominator induction are unchanged. Reserving this
guard is sublinear when `3epsilon/2<1`.

The old prime proof's convenient prerequisite `log(r)>8d` also prevents
epsilon>=1/2, but is not needed for the same prime intervals. Theorem 1
of Baker, Harman and Pintz guarantees a prime in `[y-y^(21/40),y]` for
all sufficiently large y. Set `eta_prime=1/(4d)`. Inside each required
interval `((1-2eta_prime)x,(1-eta_prime)x]`, choose d descending centers
separated by `ceil(2x^(21/40))`. Their short intervals are disjoint
and contained in the required interval once
`12d^2<x^(19/40)` and x exceeds a fixed threshold. Since
`x=2^Theta(p^(1-epsilon))`, these inequalities hold for every fixed
epsilon<1. The old deterministic trial-division scan still costs n^o(1).
The source-volume, prime distinctness, oddness and theta inequalities
are unchanged: `T/2<S<T`, `theta>1/(4d)>=1/(4p)`, and `rho<2`.

Primary reference: R. C. Baker, G. Harman and J. Pintz, *The Difference
Between Consecutive Primes, II*, Proceedings of the London Mathematical
Society 83(3), 532–562 (2001), Theorem 1;
[publisher](https://londmathsoc.onlinelibrary.wiley.com/doi/10.1112/plms/83.3.532),
[paper PDF](https://www.cs.umd.edu/~gasarch/BLOGPAPERS/BakerHarmanPintz.pdf).
This is a real replacement dependency. The old `1-2epsilon>0` check
is explicitly superseded by this proof, not silently removed.

## Exact dimension and parameter witness

Choose

```text
alpha=ceil(p^(1/6)), u=alpha^2=Theta(p^(1/3)),
epsilon=2/3-2^(-20), delta=2^(-22), C1=3/2.
```

The Gaussian normalized cost exponent is
`1/2+delta+epsilon-1/6`, so its margin is
`2/3-delta-epsilon=3*2^(-22)>0`. The normalization exponent is
`epsilon+1/3<1`, and the new guard exponent is `3epsilon/2<1`.
Every other assembly exponent is unchanged. The exact primitive savings,
packed/leaf balance root and strict c/lambda/lambda-prime choices are
those in the parameter-optimization report. The exact checker recomputes
all seven margins and all changed-interface slacks.

For `b=ceil(log2 n)`, `p=6b`, eventually
`u<=4p^(1/3)<8b^(1/3)` and `j+1<=b^(1/3)`. Therefore
`gamma<17b^(epsilon+1/3)`. The explicit Gaussian cutoff

```text
b>=2^7340032
```

gives `b^(1-epsilon-1/3)>=128>68`, and hence `gamma<=b/4`.
It also covers the logarithmic u prerequisite and the comparison of
j+1 with b^(1/3). The prime theorem and the retained finite interfaces
have additional fixed eventual cutoffs. These are asymptotic witnesses,
not practical performance estimates.

Within this reusable banded inverse model, allowing `u=Theta(p^r)` requires
`epsilon+r<1` for normalization and `epsilon<1/2+r/2` for Gaussian
cost. Together these imply `epsilon<2/3`. Balancing packed and leaf
costs as before then gives the scoped parameter supremum
`(2/3)*b_complex*x_star`, not an unrestricted algorithmic ceiling.

## Computed evidence and reproduction

The [finite inverse certificate](../runs/20261007T232103Z-downstream-banded-inverse/results/certificate.json)
passed:

- 128,140 exact rational exponent comparisons across 502 length pairs,
  including nearest-rounding ties, both directions, and periodic aliases;
- exact Schur gap/row-norm, pivot, band factor, Woodbury and residual checks;
- six rigorously enclosed full Gaussian inverses up to s=511, t=512,
  u=16 with `u*theta=16/511<1`;
- real and imaginary signed dyadic inputs, compared with an independent
  infinite-Gaussian residual enclosure and the inverse row bound;
- a signed circular-banded matrix with row gap 2^-20, and exact universal
  O(p)-precision inequalities.

The finite prototype used 56–72 work bits and 16–24 target bits. It did
not run a full P=256p implementation or simulate the tape machine.
The mathematical error proof supplies that asymptotic interface. All
acceptance thresholds and coefficient intervals use rational arithmetic;
there is no floating-point threshold check.

```sh
python3 -B research/integer-multiplication-bounds/code/downstream_banded_inverse.py \
  --upstream /path/to/pinned/integer-mult-bounds \
  --output /tmp/downstream-banded-inverse.json
python3 -B research/integer-multiplication-bounds/code/downstream_lu_assembly.py \
  --upstream /path/to/pinned/integer-mult-bounds \
  --roles 509194 494250 487650 \
  --output /tmp/downstream-lu-assembly.json
```

Source: [downstream_banded_inverse.py](../code/downstream_banded_inverse.py),
[downstream_lu_assembly.py](../code/downstream_lu_assembly.py).
These use the Python standard library and the earlier exact helpers.
Protocols record source hashes and the pinned input. One CPU worker was
used; the configured memory budget was 16 GiB. Essential compact evidence
and all commands are retained; no unpublished large derived input is needed.

Independent review additionally checked 368,480 exact exponent inequalities
and four cyclic 24-by-24 systems, including actual inverse norms 2^20,
pivots about 2^-19, and a border inverse norm 2^20. Its dense factor,
Woodbury, rounded-probe, and thirty-constraint-per-row assembly audits
passed. These are separate from this branch's finite prototype.

The next analytic opportunity is a faster application than generic banded
triangular solves, or reuse of its structure across several tensor axes.
The present model's two-thirds boundary should not be promoted to an
obstruction for such different inverse algorithms.
