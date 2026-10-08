# Equal main axes and one distinguished wide axis

Written 2026-10-08. This is an original candidate positional interface, not yet
an accepted complete multiplication bound. It targets the `O(Vd)` top-bit/prefix
movement surviving both the historical balanced layout and Swapnil Jain's
one-chunk-per-axis layout. Gaussian `O(Vd)` work remains a separate bottleneck.

## Exact address partition without extra volume

Let the padded coefficient address length be N bits. Choose a main width ell,
let `D=floor(N/ell)>=2`, and write `N=D ell+h`, `0<=h<ell`. Use D-1 main axes
of width ell and one distinguished axis of width ell+h. Then

`(D-1)ell+(ell+h)=N`.

Each address has its ordinary unique binary expansion in those consecutive
fields. The main axes have length2^ell; the last has length2^(ell+h), between
2^ell and2^(2ell). There is no new coordinate, padding factor or small residual
axis. In particular the distinguished axis still has superpolynomial length
for `ell=Theta((log n)^(1-epsilon))`, with fixed epsilon<1.

Prime boxes may choose distinct main primes near2^ell and one prime near the
distinguished power of two, provided the changed near-one intervals are proven
to contain enough primes. Exact input digit count/capacity and all output
normalizations require a separate assembly review. This does not invoke a
prime-existence oracle or reuse another campaign's table as free advice.

## Proposed transform schedule and complete alignment

The main axes form one complete equal-width chunk family. Their input physical
axis-major order is already the one-group transform order, so no low-bit or
extra-top-slot extraction is needed. Set `r=2^(ell+h)` and place the distinguished
axis at the physical polynomial suffix. This uses the existing coefficient twist
and `iota` identification, not a new standalone last-axis FFT. Every transformed
main axis has length `t=2^ell`, dividing2r, so its synthetic root `y^(2r/t)` exists.

The synthetic transform convolves the D-1 main axes over `C[y]/(y^r+1)`.
Twisting scalar suffix coefficient k by `exp(pi*i*k/r)` turns its cyclic
convolution into the negacyclic ring product; untwisting recovers the full scalar
tensor convolution. The normalization remains `1/T` because the transform volume
is `M=T/r` and each ring product divides by r. A coordinate permutation at the
outer routing interface must retain the same frequency field names for both
operands and for the pointwise product; the opposite transform restores the
original named coordinate order. This is a required paid machine interface.

If native simultaneous main layers support supplied `K=ell`, their butterfly
cost is `O(V ell D^lambda_prime polylog(log n))`. The distinguished ring products
cost `O(V log(rp))`, with exponent margin epsilon. The twist costs
`O(V p^delta)` and has constant dimension count. Both are below a target near
the bit primitive saving when epsilon is close to1. The previous O(Vd) prefix
charge is absent in this positional plan.

## Conditions still open

The complete proof must check: main-axis layer reservations with supplied width
ell; leading row prefix and spectator records; twist/negacyclic polynomial
degree requirements; exact Fourier conventions and main-axis transform errors;
prime capacities; CRT routing and both operands' product alignment. The original
restriction `t_i in {r/2,r}` must be generalized to powers of two dividing r
whose widths are between `log2(r)/2` and `log2(r)`. Every setup argument requiring
a superpolynomial lower bound on axis lengths still has minimum2^ell>=sqrt(r).
An independent finite polynomial Fourier operator check is planned.

Even if this candidate passes, the current separable Gaussian passes still cost
O(Vd) and retain `1-epsilon-delta`. Thus eliminating the top-bit charge alone
does not improve the public PR37 kappa ceiling `a/(1+a)`.

## Attribution

Swapnil Jain's public one-chunk layout, commit
`c2c2f279d93643e5ff3fe121a0fbc68e0e6f4007`, supplies the compatible equal-width
layer idea. The historical RaD balanced-transform review supplies the positional
and Fourier interface. The single wide residual axis is a derived campaign
candidate rather than an adopted public finite witness. Independent discovery
and worldwide novelty are not established.
