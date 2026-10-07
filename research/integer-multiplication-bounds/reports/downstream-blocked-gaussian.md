# Local chirp convolutions for Gaussian resampling

Campaign `20261007T222521Z`, start 2026-10-07 22:25:21 UTC, immutable
deadline 2026-10-08 08:25:21 UTC. This is a second downstream extension of
the pinned CrocSwap/integer-mult-bounds revision
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.

The construction below improves evaluation of the same analytic Gaussian
operators. It uses the known unconditional fast integer-multiplication bound
on polynomial-size local inputs, rather than the multiplication bound being
proved. It preserves the finite-alphabet machine with a fixed number of
one-dimensional tapes. Its intended scalar interface is explicitly restricted
to `1<t/s<2` and source lengths that exceed every fixed polynomial in `p`.
The actual prime-source setup satisfies both restrictions. No claim is made
for arbitrary ratios in the old scalar lemma.

## Result and verification status

Combining local Gaussian convolution with the
[weighted Neumann power bound](downstream-weighted-gaussian.md) gives a
Gaussian line-map cost `O(t*p^(3/2+delta))`. The normalized tensor cost is
`p^(1/2+delta+epsilon)`, replacing the starting
`p^(3/4+delta+5*epsilon/4)`. The dimension exponent can approach `1/2`
under the retained guard, prime, and scaling constraints.

For the unchanged upstream paired graph, the strict witness
`epsilon=499/1000`, `delta=1/10000`, `beta=999/1000`,
`a_bit=296/10^11`, and `a_complex=1/10^11` supports
`kappa=5/2^60`. This is exactly `5/2` times the advertised starting
`2^-59`, and is stronger than `2^-58`. Its actual minimum margin is
`682447869/156250000000000000000000000`. This claim remains conditional
on the written replacement Gaussian proof and the retained upstream
finite-network, frame, rank, and multiplication interfaces.

The exact prototype is
[downstream_blocked_gaussian.py](../code/downstream_blocked_gaussian.py).
It verifies factor identities, local exponent bounds, signed Kronecker
convolution against direct multiplication, exact dyadic Gaussian-surrogate
blocks, and true Gaussian blocks with rational pi/exponential enclosures.
Its Python integer multiplication is an exact finite testing backend;
the complexity proof invokes a published unconditional multitape algorithm.
It is not a complete multiplication-machine implementation.

## Exact local factorization

For positive rational `A,B,c`, integer local coordinates `h,v`, and rational
offset `gamma`, put `mu=A*B`. There is an exact identity

```text
c*(gamma+A*h-B*v)^2
 = c*((A^2-mu)*h^2+2*gamma*A*h+gamma^2)
 + c*((B^2-mu)*v^2-2*gamma*B*v)
 + c*mu*(h-v)^2.
```

Thus `exp(-pi*c*(gamma+A*h-B*v)^2)` is an input diagonal, an output
diagonal, and a Toeplitz Gaussian kernel. The kernel is at most one.
The diagonal factors may exceed one; they are not incorrectly treated
as contractions. Their local exponents and the required extra precision
are bounded below. All intermediate arithmetic is exact on rounded dyadics
until a stated final output rounding.

For the forward map `S'`, take `A=1`, `B=s/t`, and `c=1/alpha^2`.
At output block origin `k0`, choose `j0=floor((s/t)*k0)` and
`gamma=j0-(s/t)*k0`, so `-1<gamma<=0`. For the map `T`, take
`A=t/s`, `B=1`, and `c=alpha^2`, with
`j0=floor(k0/(t/s))` and `gamma=(t/s)*j0-k0`, so
`-2<gamma<=0` under the stated ratio restriction.

The `D` diagonal used in `N=C*T*D` is folded into the `T` input factor.
It subtracts `alpha^2*beta_j^2` from that factor's rational exponent.
This avoids adding a third normalization factor. The final `E=N-I` call
selects the ordered coordinates of `C`, subtracts the exact input, and then
rounds the completed result to the original disk grid.

## Blocks and Gaussian tails

Assume `p>100` and `2<=alpha<sqrt(p)`.
For `S'`, use output blocks of
`L=alpha*ceil(sqrt(p))`. Include all integer input indices from
`floor((s/t)*k0)-L-1` through
`ceil((s/t)*(k0+L-1))+L+1`. Every omitted index is at distance at least
`L>=alpha*sqrt(p)` from every output center. The Gaussian tail, including
periodic aliases and the factor `1/(2alpha)`, is bounded by a constant
times `exp(-pi*p)`, hence by `2^(-p-10)` for `p>100`.
For example successive omitted Gaussian terms have ratio below
`exp(-6)` because `L/alpha^2>=1`; summing the geometric majorant proves
the stated constant bound.

For `T*D`, use output blocks
`L=ceil(sqrt(p)/alpha)` and radius `R=L+2`. Include integer inputs from
`floor((k0-R)/(t/s))-1` through
`ceil((k0+L-1+R)/(t/s))+1`.
Omitted distances from the center are at least `L`, while
`D_j<=exp(pi*alpha^2/4)`. Their total contribution is below

```text
4*exp(-pi*(alpha^2*L^2-alpha^2/4))
 < 4*exp(-9p/4) < 2^(-p-10),
```

using `alpha^2*L^2>=p`, `alpha^2<p`, and `pi>3`.
The input lattice spacing `t/s>1` only decreases this Gaussian majorant.
Source values and `D_j` are extended periodically; the bounds include
every omitted periodic alias, not only indices within one period.

The final short output block may be evaluated at full length and its
extra outputs discarded. Periodicity makes the same formulas valid,
and `t` is much larger than `L` in the assembly regime.

## Explicit local exponent and precision bounds

Let `u=alpha^2`. Each of the input, output, and kernel rational exponents
before multiplication by `pi` has absolute value at most `512p`.
This deliberately loose common bound includes the `D` diagonal.

For `S'`, `L<=2alpha*sqrt(p)`, `|h|<=3L`, `|v|<L`, and `|gamma|<=1`.
Thus its input exponent has absolute value at most
`(9L^2+6L+1)/u`, its output exponent at most `(L^2+2L)/u`, and its
kernel exponent at most `16L^2/u`. These are below `512p`.

For `T*D`, `L>=2`, `L<=2sqrt(p)/alpha`, `|h|<=4L`, `|v|<L`,
`|gamma|<2`, and `1<t/s<2`. Its input exponent, including `D`, has
absolute value at most
`u*(32L^2+32L+4+1/4)<512p`. The output exponent is bounded by
`u*(L^2+4L)`, and the kernel by `2u*(5L)^2`, also below `512p`.
Both input spans contain at most `16p` terms.

Normalize only the input and output diagonal factors by `2^-sigma`,
where `sigma=4096p`. Keep the Toeplitz kernel unscaled because it is
already at most one. Since `pi<4` and `exp(1)<4`, every diagonal
factor is below `2^(4096p)`, and its normalized value is in the unit
interval. Their product is restored by a final shift of **`2sigma`**,
not `3sigma`.

Choose work precision `P=32768p`. The retained real exponential routines
handle each normalized coefficient at precision `P`:

- A negative exponent uses the real negative-exponential routine.
- A positive exponent uses the positive-exponential routine with
  scale `sigma<=2P` and the just-proved bound on its value.
- Zero exponents and rational normalization by `1/(2alpha)` are handled
  exactly or with a directed dyadic rounding at precision `P`.

The rational exponents have `O(p)`-bit numerators and denominators.
Computing each coefficient therefore costs `O(p^(1+delta))` using the
same scalar arithmetic model as the starting proof. Rounded factors have
absolute error less than a fixed constant times `2^-P`.

Products of those dyadics, the signed polynomial convolution, and the
final output multiplication are retained exactly. At most `16p` terms
contribute to a coefficient. Expanding the product errors and allowing
the rational normalization gives a conservative absolute error bound

```text
128*p^2 * 2^(2sigma-P) < 2^(-p-10),  p>100.
```

The generous precision margin is intentional; no floating-point threshold
or numerical cancellation hypothesis is used. Partial convolution sums
have `O(log p)` extra integer bits. Exact dyadic products have at most
a fixed multiple of `P` fractional bits and `O(p)` total width, even
before cancellation or the final shift.

The Gaussian tail and this arithmetic error together are much smaller
than one original-grid unit. Final componentwise rounding gives scaled
complex error below four. The exact `S'` norm is below `3/4`, so its
rounded output remains in the disk. At selected `T*D` outputs, subtracting
the exact input gives `E` with norm below `0.42`; its completed rounded
output remains in the disk and has scaled error below `p/3` for `p>100`.
Large intermediate full-`T*D` values are stored at the guarded work width;
they are never fed into an interface requiring disk-valued records.

## Polynomial convolution and fixed tapes

A block has `O(L)` rounded coefficients, each of `O(p)` bits. Signed
coefficients are split into positive and negative parts; real and imaginary
parts are handled separately. A fixed number of nonnegative polynomial
products suffices. In Kronecker packing choose a digit width equal to the
sum of the two coefficient widths plus `ceil(log2(O(L)))+O(1)`. Each
convolution coefficient is strictly below one packed digit, so no carry
crosses a coefficient boundary. This adds only `O(log L)` bits and yields
one integer product on `O(Lp)` bits per signed component.

Use a known unconditional fixed-tape integer multiplier, for example
the Harvey–van der Hoeven 2021 `O(N log N)` theorem. Since `L=O(p)`,
`log(Lp)=O(log p)`, and every fixed power of `log p` is bounded by
`p^delta` for any fixed positive `delta`. A block therefore costs
`O(L*p^(1+delta))`, including all coefficient generation and scans.
This use is confined to polynomial-size local inputs and does not invoke
the stronger bound claimed by this campaign.

Blocks are processed in increasing output order. Their source centers
are monotone; consecutive windows advance by `O(L)` records and overlap
by `O(L)`. A fixed number of work tapes buffers a window, retains the
overlap, appends its new records, writes the local packed operands, and
then clears the multiplier's local workspace. Each block copies or visits
only `O(L)` records, so total movement costs `O(tp)`.
An initial sequential pass may copy the short periodic prefix and suffix
to separate tapes; the first and last windows use these buffers. This
handles wraparound without one full-period traversal per block.

Each descriptor and coordinate counter has `O(p)` bits. A block performs
`O(L)` scalar work, so its `O(p)` descriptor generation is absorbed.
The original scalar exponential and the unconditional multiplier have
fixed tape counts; nesting a fixed collection of these routines retains
a fixed total tape count. There is no growing-radix instruction,
random-access primitive, or uncharged global permutation.

There are `O(t/L)` blocks because the assembly lengths are
superpolynomial in `p`, whereas `L=O(p)`. Both `S'` and one application
of `E` consequently cost `O(t*p^(1+delta))`. The extraction `C`, exact
subtraction, record-format conversions, and `D'` map fit the same bound.

## Neumann iterations and the final assembly

Use `alpha=ceil((32b)^(1/4))`, `p=6b`, and `d=floor(b^epsilon)` with
`epsilon<1/2`. Keep the prime setup `theta>1/(4d)`.
Then `u>=sqrt(32b)` and `d<=sqrt(b)`, hence `u*theta>sqrt(2)>1`.
The weighted cutoff remains
`k=ceil(1/theta)+ceil(p/u)<=u=alpha^2<p`:
the same increasing quadratic has

```text
u^2-4du-6b >= 26b-4sqrt(32)*b^(epsilon+1/2)
             > 26b-24b >= 2b > 0.
```

This generalizes the earlier `epsilon<=1/4` sufficient condition in the
first weighted report. Thus the Neumann numerical constants, exact
accumulation, disk margins, and unweighted remainder stay intact.
There are `O(sqrt(p))` calls to the new fast `E` procedure, yielding
`O(t*p^(3/2+delta))` per Gaussian line. Tensorization over the same
physical axis schedule gives `O(d*T*p^(3/2+delta))`.

The width and scale satisfy `gamma<46d*sqrt(b)`. For the chosen
`epsilon=499/1000`, the old `b>=2^40` cutoff is no longer sufficient.
Replace it by `b>=2^8000`: then
`184^1000<2^8000` proves `gamma<=b/4`. This is one explicit Gaussian
cutoff; the retained eventual setup and guard cutoffs still apply.
The original source-scale and final-rounding analysis uses `gamma<=b/4`
and is otherwise unchanged.

The assembly prime intervals give `s_i>(1-1/(2d))*t_i>=3t_i/4` for
`d>=2`, so `1<t_i/s_i<4/3<2`. The line lengths remain
`2^Theta(p^(1-epsilon))`, satisfying the restricted blocked interface.
Prime-interval growth `1-2epsilon>0`, stopped guard `2epsilon<1`,
prefix layout, packed recursion, complex leaf cost, and nonadjacent
address movement all retain strict slack. Only the Gaussian cost row
changes to margin `g5=1/2-delta-epsilon`.

Set `c=beta*a_bit`, `lambda=1-(1+beta)*a_bit^2/2`, and
`lambda_prime=1-beta*a_bit^2`, as before. The minimum of the seven
assembly margins is `epsilon*beta*a_bit^2`, strictly above `5/2^60`
for the unchanged finite graph. A composed circuit with fewer side roles
must also supply its separate scalar-restoration, frame, and rank proof.

## Evidence and reproduction

The first prototype checked 9,040 exact factor identities across 640
boundary blocks, three exact dyadic surrogate convolutions, and two true
Gaussian blocks with rational interval error bounds. Independent critical
review additionally tested signed complex inputs, coordinate wraps, and
packed-digit carry bounds at `p=128`.

From a RaD checkout, with Python 3.11 or newer:

```sh
python3 -B research/integer-multiplication-bounds/code/downstream_blocked_gaussian.py \
  --output /tmp/downstream-blocked-gaussian-certificate.json
```

The complete assembly certificate is under
`runs/20261007T225200Z-downstream-blocked-gaussian-assembly/results/`.
The scripts use standard-library integer and rational arithmetic.
The finite tests supplement the all-size written proof and do not replace
the retained transcendental identity or multiplication interfaces.

Primary sources are Harvey and van der Hoeven, *Integer multiplication in
time O(n log n)*, Annals of Mathematics 193(2), 563–617 (2021),
DOI `10.4007/annals.2021.193.2.4`,
[author manuscript](https://www.texmacs.org/joris/nlogn/nlogn.pdf), Sections
2 and 4; and the pinned upstream manuscript's `07-resampling.tex` and
`08-assembly.tex`. The local factorization and blocking argument were
derived in this campaign. Exhaustive literature novelty is not claimed.

Next: audit the independent constraints behind the `epsilon<1/2`
boundary, including prime intervals, coefficient guard, Gaussian scaling,
and possible alternatives to the retained inverse interface.
