# Packed tensor cells and sparse tape repair

This is an original analytic/movement candidate, not a promoted multiplication
bound. At13:47 UTC, independent source review found a blocking surviving
O(nd) triangular CRT movement row. The prediction of approaching the native
bit saving a is withdrawn. The currently paid composition retains the
a/(1+a) ceiling. It combines spatial inverse locality, mixed-radix tensor packing,
two shifted cell grids and sparse classical repair. The deferred-reservoir FFT
and distinguished suffix-axis interface are separate required components.

## Exact local convolution and safe padding

Let a cell have side lambda and a separable finite kernel have radius R in
each of D axes. Encode coordinates in mixed radix `B=lambda+2R`. The input has
degree at most lambda-1 per coordinate and the shifted kernel degree2R, so
every product coordinate is at most B-1. The univariate Kronecker product has
degree below B^D without coordinate carries. The padded volume is exactly
`lambda^D*(1+2R/lambda)^D`. It stays within a constant multiple of the cell
volume when `D*R/lambda=O(1)`. Rounding every axis up to2lambda is unnecessary
and would introduce2^D volume.

Signed coefficients can be split into positive and negative parts and use
four ordinary integer products. Each coefficient field includes the exact
sum-of-absolute-products carry bound. The authored finite checker compares
all resulting coefficients against an independently ordered sequence of
one-axis convolutions. Its Python multiplication backend is only a finite
identity checker, not evidence about asymptotic multitape complexity.

Once all low coordinate fields of the cell are contiguous, emitting the
mixed-radix holes is a sequential operation. A coordinate counter and validity
flags use `O(D log B)` bits. With coefficient precision Q dominating that
metadata, their work is absorbed by the Q-bit output records. No next-power
padding, random lookup or free repeated axis exposure is assumed.

## Two grids and rare output repair

For a power-of-two lambda and `4R<=lambda`, use a cell grid and its translate by
lambda/2 on every axis. One grid fails only on the R-wide faces of its cells.
The exact residue-space count failing both grids is

`lambda^D - 2*(lambda-2R)^D + (lambda-4R)^D`.

The face sets in one coordinate are disjoint. Thus any double failure needs
two different axes, and a union bound gives density at most
`4*D*(D-1)*(R/lambda)^2`. Source packets require expansion by their actual
stencil radius; counting only target outputs is insufficient. The layout
branch is checking the expanded source volume and period-cut pockets.

With `R/lambda=O(D^-3)`, this regular double-failure set has densityO(D^-4).
An exceptional phase band of width `delta=D^-4` in each coordinate has total
densityO(D^-3), provided its enlarged inverse halo is smaller than the band.
If the required SOURCE packet volume is `rho*n` with `rho=O(D^-3)`, up to D
ordinary fixed-tape sorts and repair passes cost `O(rho*n*D*b)` for
`b=ceil(log2 n)`. At `D=Theta(b^epsilon)`, epsilon>1/2, this is O(n). Here n
already includes the Q-bit coefficient payload; Q must not be charged twice.
Selection and packet duplication must read the original payload once, with
all metadata and every emitted copy charged.

## Inverse scales and the separate forward problem

The inverse branch proposes `delta=D^-4`, `theta=Theta(D^-16)`, `Q=Theta(D^18)`,
`u=Theta(Q/D)`, inverse core lambda_I=Theta(D^8) and regular radiusR_I=Theta(D^5).
Then `u*theta=Theta(D)` gives constant contraction, the complete tensor chirp
reserve `D*u*theta*lambda_I^2=O(Q)`, and a global phase-edge inverse halo has
radiusO(D^(17/2)). The exceptional phase pocket has width
`delta/theta=Theta(D^12)`, larger than that halo. The new spatially weighted
inverse and resolvent argument, rather than a forward-band assumption,
must supply every precision statement.

The forward S' resampling map has a much larger physical window
`R_F=Theta(sqrt(uQ))=Theta(D^(35/2))`. It cannot share the inverse cell scale.
Its exact Gaussian diagonal/Toeplitz factorization has chirp coefficient
theta/u, so a separate forward core `lambda_F=Theta(D^3*R_F)` gives a tensor
reserve `O(theta*D^7*Q)=o(Q)`. Fractional source cores and their actual gathering
remain the central open movement obligation. A simple lifted array
`f(c(j))` is not a valid Toeplitz input across repeated nearest-center indices.

## Conditional recurrence and current gaps

For either polynomial cell side, a packed child has bit length
`S=O(Q*lambda^D)=exp(O(b^epsilon log b))=n^o(1)`. A terminating induction using
`M(S)<=C*S*(log S)^(1-kappa)` would charge normalized packed arithmetic
`b^(epsilon*(1-kappa)+o(1))`. For epsilon<1 this lies below the target exponent
1-kappa. This is a proposed recursive call in the same algorithm, rather than
an available improved multiplication oracle. All child sizes, repetitions,+rounding errors and leading constants must be included in its recurrence.

Current unclosed interfaces: joint fractional forward acquisition; full source
packet volume and ordering for repair; coefficient-generation and catalogue
traffic; recursive calls and constants; all forward/inverse resampling,
CRT, alignment, guard and exact-recovery costs. A better isolated inverse
or PASS label does not establish a better multiplication exponent.
