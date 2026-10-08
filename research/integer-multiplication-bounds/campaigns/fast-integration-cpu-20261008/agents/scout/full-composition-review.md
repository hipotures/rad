# Independent complete-map and recovery review

Review begun 2026-10-08 14:41 UTC and recorded at 14:54 UTC. Targets are the
coordinator's [full ledger](../../reports/conditional-composition.md),
[exact parameter code](../../code/packed_assembly.py), inverse and layout
reports, and pinned eligible PR40 science commit
`43f59ff533598762cbc43a5e14af2bbbc76fabbd`. The ledger snapshot inspected
has SHA256 `9cad61e314783dc7a49d3f450ae6c6fead6b8d61552a003d252b5d271ebce0f5`;
parameter-code SHA256 is
`f7e8a4e5e31029b16399f4d360dbf9d5355604836aa94e5a79f3fc3fa3fefb61`.
Later repairs must be identified separately from this inspected snapshot.

The written argument supports the conditional candidate after the three
clarifications below: inverse-kernel prefix normalization, free complete axes
in regular repair packets, and a fixed scalar-evaluation exponent. No further
cost or normalization obstruction was found in this review. This conclusion
is relative to the named native compiler, moment, semantic-guard and machine
contracts. It does not certify those inherited inputs, execute an all-size
multiplier, replace numerical controls by proof, or provide a numerical full
machine cutoff.

## Complete source maps have fixed normalizations

Use `B` for the integer radix-digit width, `Q` for fractional precision,
`N=log2(T)` for physical address bits, and `u=alpha^2`. The source identities
in pinned `upstream/build/sections/07-resampling.tex` define

`A=S'=S/2`, `J'=N_matrix^-1/2`,
`D'=2^(-(2u-2))*diag(exp(pi*u*beta_j^2))`, `B_source=D'J'C`.

Here `C` is exact ordered nearest-coordinate selection. The scalar factors
multiply to `2^(-2u)` per axis and `2^(-gamma)` over all axes, with
`gamma=2du`. Bare correction inversion is not the complete source inverse.
The new solver must retain `1/2` in `J'` and the diagonal normalization in
`D'`. Their tensor factors can be formed in the existing packet setup and
multiplied during its existing writes. They require no additional per-axis
payload pass. Opposite transform signs and both identical source permutations
must likewise remain those of the pinned identity.

The inherited exact maps `A`, `B_source`, Fourier operations and normalized
convolutions are contractions. For the multiplication inputs it suffices to
compute approximations on a fixed strict disk margin; the digit inputs have
norm below `1/4`. An internal bare inverse or chirp may use larger guarded
numerators, but its complete normalized output must satisfy the same margin.
The exact signed widths grow by only `O(Q)` in the present parameter family.

## Uniform Gaussian precision can be budgeted

Put `eta_Q=2^-Q`. A sufficient conservative completed tensor-map target is

`||A_tilde-A||<d Q^2 eta_Q`,
`||B_source_tilde-B_source||<d Q^2 eta_Q`

on the actual strict-margin inputs. The following construction can give the
much stronger `O(eta_Q)` bound; the loose target makes transfer of the original
recovery constants transparent.

Each retained regular or forward output has one selected packet owner.
Rounding and approximation errors are pointwise, so the number of cells and
duplicate source copies does not multiply the error at one output. Cell
ownership must be applied after all needed sources have been retained.

The tensor packet has `M` records, total output chirp reserve `Gamma=O(Q)`,
and at most `d` factors per generated coefficient. Work precision

`P>=Q+Gamma+ceil(log2(M))+ceil(log2(d))+C`

for a sufficiently large fixed `C` pays the rounded setup products, coefficient
rounding, exact signed convolution accumulation and final rescaling. The
finite integer slot width includes `2P+ceil(log2 M)+O(1)` bits. Because
`log M=O(d log d)=o(Q)`, this is still `O(Q)` precision. Storing all exact
factor denominators would instead give `dP` and is not allowed.

One small correction is needed on the inverse side. A Laurent inverse's
diagonal coefficient can exceed one, even for a tridiagonal matrix arbitrarily
close to identity. Literal contracting-factor rounding therefore needs a
normalization. Its weighted perturbation norm `rho_i` is exponentially small
in `u*delta`. Eventually `rho_i<=1/(4d^2)`, so every coefficient has magnitude
at most `1/(1-rho_i)<=1+1/d^2=:L`. Divide each one-axis inverse vector by this
rational `L` before generating contracting prefix products and restore `L^d`
once. Since `L^d<2`, this adds one guard bit, not `d` guards. Exact setup needs
only `O(d log d)=o(Q)` denominator bits. Equivalently, bounded prefix and future
products give a rounding bound `2d*2^-P` directly.

The physical principal-window estimates are uniform in phases and inputs.
Increase the radius constants, and include `O(log d)` in the requested local
accuracy, so every one-axis window error is at most `eta_Q/(128d)`. The
exceptional bound `32 exp(-3u theta R^2)` and the regular bound
`16 exp(-6u delta R)+32 exp(-3u delta^2/(4theta))` permit this choice.
Their range conditions hold eventually: `R_exception=Theta(d^(17/2))`
is below `1/(2theta)=Theta(d^16)`, and `R_I=Theta(d^5)` is below
`delta/(2theta)=Theta(d^12)`. Finite kernel setup uses the same accuracy
with its chirp reserve included. Boundary cells may use `delta/2` after
enlargement; this changes fixed constants only.

The band solver adds a fixed-grid error bounded by
`2^12*(w+1)^2*2^-P`, with `w^2=O(d)`, plus the explicitly bounded matrix
truncation and remote-alias perturbations. Increasing `P` by `O(log d)`
allocates each of these an `eta_Q/(128d)` share. No cyclic corner is silently
removed: free complete axes use overlapping unfolded principal windows,
retaining only each window's core. Overlap is a constant at ONE axis stage;
returned cores are joined before proceeding to another axis.

The tensor norms remain bounded: the bare corrections satisfy a near-identity
bound with exponentially small one-axis perturbations, and their product is
eventually below two. Alternatively, folding the inherited `J'=N^-1/2`
normalization into each stage makes the relevant axis contracts contractions.
Errors from the `d` stages therefore sum within the stated budget.

## Regular repair packets also have complete free axes

A bad-grid pair packet constrains two face coordinates and leaves other
coordinates complete. If a rectangular source-closed implementation evaluates
every row on a free axis, that axis includes phase-exception rows and cyclic
wraps. A regular Laurent-only kernel cannot be used there without a further
argument.

A simple valid implementation uses the global overlapping-principal band
solver on every free axis of ALL inverse repair packets. The regular pair
packet volume is `O(d^-4 V)`; `d` axis stages and `w^2=O(d)` give arithmetic
cost `O(V/d^2)` up to scalar factors. Phase packets still give `O(V/d)`.
Constrained regular faces retain `R_I` principal windows and the sharper
regular bound, so their emitted source copies remain sparse. Expanding those
narrow faces by `R_exception` would be invalid. Another valid implementation
uses minimal source-closed buffers and trims processed coordinates to their
final regular predicate. One of these policies must be explicit.

The root's sum of packet SOURCE volumes, rather than only target density,
pays every copy. Source-closed buffers retain halos in all unprocessed axes.
Paid ordinary sorting across `d` stages has `O(V b/d^2)` traffic. The inverse
error budget includes ALL repaired outputs, including complete free-axis
periods; it is not conditional on avoiding the rare masks.

## Native transforms and scalar arithmetic

The semantic native guard remains `O(d)`, independently of input precision.
It is negligible compared with `Q=Theta(d^18)` but must still be allocated.
Two complete deferred transform groups perform at most `2ell` final rounded
layers. Their combined additive error is below `2sqrt(2)ell*eta_Q`, which
is at most `N*eta_Q` eventually. Paid coordinate routes and exact restored
banks add no numerical error. Normalized synthetic convolution and its
scale `M=T/r` retain the original bounded-error and strict-disk argument.

The phase routine cited in pinned upstream07 is Harvey–van der Hoeven's
Lemma 2.12, with cost `O(Q^(1+zeta))` for every FIXED positive
`zeta<1/8`. Unless a separate quasi-linear elementary-function implementation
is supplied, one phase per coefficient has normalized exponent
`18epsilon*zeta`, not literally zero. Taking `zeta=1/100` gives
`18epsilon*zeta<0.18<1-kappa`. Under the same conservative scalar convention,
the phase band-LU row is `-epsilon+18epsilon*zeta`, and the regular inverse
repair row is `-2epsilon+18epsilon*zeta`; both are negative. Conventional
integer convolution on polynomial windows has only polylogarithmic factors.
These explicit scalar rows do not change the candidate's limiting Fourier
and routing constraints.

## Independent exact margin argument

Let `a=783777693/(2*10^13)` and `h=10^-6`. The proposed parameters are
`epsilon=1-h`, `q=a(1-h)`, `kappa=a(1-10h)`, `beta=1/20`.
The native complex stopped-leaf saving exceeds `a`, so the largest internal
exponent is `tau=1-a`. Choosing `lambda=(tau+1-q)/2` gives both native
strict gaps `a*h/2`. Routing and guarded CRT have slack `10*a*h`.
The completed Fourier slack is

`epsilon*q-kappa=a*(8h+h^2)>0`.

The recursive packed-child slack is `h*(1-kappa)>0`. Suffix products,
sparse sorts, both band-solver rows and the explicit scalar-phase row are
also strictly absorbed. The new candidate exceeds the old scoped supremum
because

`kappa-a/(1+a)=a/(1+a)*(a-10h*(1+a))>0`.

This derivation is separate from the coordinator's positive rational PASS.
The strong-induction recurrence is legitimate: total child bits are `O(n)`
and every child has logarithmic length `O(b^epsilon log b)`. Its leading
recursive ratio tends to zero for fixed `epsilon<1`; it is not an assumed
improved multiplication oracle.

## Exact recovery

The uniform Gaussian targets above and complete native transform target give
the original source error envelope

`E_s=9*2^gamma*T*N*eta_Q`,

because `2d Q^2<TN` eventually. Strict input disk margins persist through
the three source transforms, phase products and normalized convolution.
The two source inputs have norm below `1/4`; their computed transforms stay
below `0.26`; their pointwise product stays below `1/2`.

After the first exact numerator multiplication by `S`, the error coefficient
is below `28*2^gamma*T^2*N`. The second scale multiplies by
`2^(2B+4)*S`. With `S<=T`, the final absolute error is therefore below

`448*N*2^(2B+gamma+3N-Q)`.

There are THREE powers of `T` in this bound. For `Q>=6B`,
`gamma<=B/8`, and `N<=B`, it is at most
`448B*2^(-7B/8)<1/2` eventually. Nearest integer rounding consequently
recovers the true real coefficients. Exact signed numerator scaling fits
width `Q+2B+2N+gamma+O(1)=O(Q)` and is paid; no clipping replaces that scaling.
Input product degree is below `T/2<S`, so cyclic convolution has no
nonzero coefficient wrap. Ordinary carry propagation then reconstructs the
integer product.

All these are eventual statements in a fixed parameter family. The finite
base algorithm covers the remaining lengths. The effective prime-gap input
provides eventual constructive prime supply but no published numerical
threshold for the complete machine. Full-map executables are valuable checks
of the changed implementation; their PASS labels alone cannot establish any
of these uniform contracts.

## Adoption receipt after the initial review

The coordinator adopted complete free-axis band-LU for ALL inverse repair
packets, rational inverse-kernel normalization `L=1+1/d^2` with `L^d<2`
restored once, and explicit fixed scalar exponent `zeta=1/1000`. The inverse
branch also wrote the contracting-prefix interface with coefficient error
`(2d+1)2^-P` and scalar setup denominators of only `O(d log d)` bits.
These repair the three clarifications identified above without changing the
limiting rows. The coordinator's current chooser now enforces
`u^2 theta_i>=2Q`, which safely satisfies the pinned source's STRICT
`theta_i>Q/u^2`. The written complete-map and recovery closure is supported
relative to its named native hypotheses; no additional obstruction was
identified by this scout review. The inherited machine/compiler premises and
the absence of a numerical full-machine cutoff remain material limitations.
