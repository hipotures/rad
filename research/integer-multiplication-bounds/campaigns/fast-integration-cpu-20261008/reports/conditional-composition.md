# Full cost ledger for the packed tensor candidate

Status as of13:55 UTC: reusable local analytic and movement lemmas, with a
rejected stronger-exponent assembly. No new complete multiplication exponent
is promoted. The triangular CRT map retains an O(nd) payload row. Treating its
known bit-order reversal as the entire CRT was incorrect; the independently
reviewed correction is included in the executable exact ledger.

## Conditional inputs and credit

The public native bit/complex constructions are conditional inputs, not this
campaign's finite witnesses. The eligible pinned PR40 scientific head is
`43f59ff533598762cbc43a5e14af2bbbc76fabbd`, with bit saving
`a=783777693/20000000000000` and complex saving `b_complex=717/10000000`.
Its readiness head is a separate public review record; readiness is not
acceptance or proof of every physical hypothesis. The earlier PR36 producer
is used only by the continuation exclusion. Historical RaD routing, semantic
guard and phase interfaces remain explicit credited inputs.

The campaign-derived mechanisms are spatial inverse decay with phase-square
cancellation, one-pass fractional source-core embedding, a global shifted grid
with explicit carry-cut exclusions, tensor convolution by a small recursive
integer multiplication, whole-axis deferred FFT reservoirs, the ell-first wide
suffix chooser, and source-closed sparse repair. General tools used inside
these arguments are established. No worldwide priority claim is made.

## Acyclic shapes and long digits

Let B0=ceil(log2 n). Choose fixed rational epsilon in(1/2,1). Compute an input
digit width `B=ceil(C_D B0^(18epsilon))` and working precision `Q=C_Q B`, with
fixed positive rational constants large enough for the local error budgets.
Choose a binary coefficient volume `T in[4n/B,8n/B)` and N=log2 T. Compute
`ell=floor(B0^(1-epsilon))` FIRST, then `d=floor(N/ell)` and `h=N-d ell`.
There are d-1 main axes of length2^ell and one contiguous polynomial suffix
`r=2^(ell+h)`. Exactly0<=h<ell; total scalar volume is T and log r<2ell.

Thus TQ=Theta(n), d=Theta(B0^epsilon), Q=Theta(d^18),
ell=Theta(B0^(1-epsilon)), and every physical axis exceeds every fixed power
of Q eventually. Computing d first would instead allow h<d and a suffix of
widthTheta(d), restoring the very pointwise-product bottleneck being removed.

Choose distinct odd prime lengths s_i below t_i with
`theta_i=t_i/s_i-1 in[c_theta*d^-16,2c_theta*d^-16]`.
The short-interval prime premise supplies enough candidates eventually;
trial division of all candidates is a permissible n^o(1) setup. S/T tends
to1, since sum_i theta_i=O(d^-15). Original digit products have degree less
than T/2<S, so cyclic source convolution causes no coefficient wrap.

Choose alpha as the ceiling of sqrt(B/(64d)) and u=alpha^2. Eventually
`B/(64d)<=u<=B/(16d)`, hence the total resampling scale
`gamma=2du<=B/8`. With C_D sufficiently large relative to c_theta,C_Q,
`u^2 theta_i>=Q`, u theta_i grows, and all inherited Gaussian contraction
conditions hold. These are eventual constant choices, not numerical machine
thresholds or practical running-time promises.

## Gaussian packets and precision

Use delta=d^-4. A regular inverse row needs radius
`R_I=C_I Q/(u delta)=Theta(d^5)`. Use a binary cell side
lambda_I=Theta(d^3 R_I)=Theta(d^8). Enlarge phase exceptions by
O(theta lambda_I) so that a retained cell stays entirely inside one affine
phase; this increment is o(delta). The spatial locality lemma bounds the
regular tail by `16exp(-6u delta R_I)+32exp(-3u delta^2/(4theta))`.

In the regular phase the exact inverse is a contracted input chirp, a Laurent
convolution and an output chirp. The TOTAL d-axis chirp reserve satisfies
`Gamma_I=O(d u theta lambda_I^2)=O(Q)`; choose c_theta small relative to the
fixed radius constant to keep its constant under control. A sufficiently
large R_I then covers both the requested Q-bit accuracy and this reserve.
Each Laurent perturbation is exponentially small in u delta, so the tensor
norm product is bounded; merely replacing each norm by2 would need an
additional d-bit reserve. Finite principal kernels approximate the Laurent
coefficients with a separately paid boundary residual.

The forward S' map has radius `R_F=Theta(sqrt(uQ))=Theta(d^(35/2))` and
uses its OWN cell side `lambda_F=Theta(d^3 R_F)=Theta(d^(41/2))`.
Its exact diagonal/Toeplitz split has chirp coefficient theta/u, so
`Gamma_F=O(d theta lambda_F^2/u)=O(Q*d^-9)`.
Its actual source origin is floor(k0/rho), with y=rho*j0-k0 retained. Setting
y=0 is incorrect. Target/source core padding and two rounding positions must
be included in the excluded faces. Numerical controls retain those negatives.

For either packet choose internal precision
`P>=Q+Gamma+O(d log(lambda+R)+log d)`, hence P=O(Q).
Round EACH contracting prefix product; keeping all d exact denominators would
silently require dP bits. A fixed-tape prefix stack emits O(lambda^d) factor
products, because its partial volumes form a geometric series. Polynomial
axis catalogues may be scanned completely per cell: their logarithmic size
is O(B0^(1-epsilon)), whereas log(cell volume)=Theta(B0^epsilon log B0).
For epsilon>1/2 their traffic and setup are absorbed by the cell payload.

After one paid gather all cell fine coordinates are contiguous. Ordinary
signed Kronecker products use radixlambda+2R, giving volume inflation
`(1+2R/lambda)^d=O(1)`. Alternatively the independently tested unpadded
interior variant admits address carries only at outputs already excluded by
the face masks. There are a fixed number of real/imaginary signed products;
their exact coefficient-field carry reserve is included in P.

## Repair and native transform charges

Two half-cell grids leave regular bad output densityO(d^-4). Source packets
are expanded and their SUM counts every duplicated copy. Phase slabs expanded
by `R_exception=Theta(sqrt(Q/(u theta)))=Theta(d^(17/2))` have total density
O(d delta)=O(d^-3), since their phase-pocket width isTheta(d^12).
Original-period strips must use the larger forward scale. Their density is
superpolynomially small. Regular packets use R_I rather than R_exception.

The root's source-closure lemma uses buffers E_k expanded only in unprocessed
axes. Ordinary fixed-tape sorts and d stages costO(n B0/d^2). Conventional
polynomial-window convolution costs only polylog(B0) per payload bit.
Phase repair uses direct near-identity band LU with half-bandwidth
`w^2=O(Q/u)=O(d)`; setup is charged on EVERY needed patch. This costs
O(n/d) times scalar polylog factors (or a sufficiently small fixed Q^zeta).
The inverse branch proves row-gap preservation and fixed-grid backward error,
including remote Gaussian aliases as a separate perturbation.

The native completed layer is restated for independent B0,d,Q; its old
d=Theta(p^epsilon),r=exp(Theta(p/d)) promise is not invoked unchanged.
Actual conditions are semantic guardDelta<<Q, address descriptorsO(B0)<<Q,
K=ell>>log Q, polynomial suffixr>>Q^C, product row stock and complete restored
dirty fields. The two full FFT groups defer donor axes rather than executing
their kernels at every level. Their normalized charge is
`ell*d^(1-q)` for q strictly below the native bit saving and stopped complex
leaf saving. Two paid bank routes costB0^tau. Ring products costlog(rQ).

Both operands use identical named-frequency schedules; the opposite transform
uses reverse group/routing order. Exact tensor operators commute. Truncations
do not: normalized contractions bound the two groups' additive error. Native
row padding is removed after each completed invocation and does not compound.

Source-transform chirps formerly computed d Q-bit factors per coefficient.
They can instead sum their O(B0)-bit phase numerators using O(d B0^2) metadata
work, then compute ONE Q-bit exponential. Long Q pays this metadata, but
cannot pay repeated payload movements. Exact-recovery scales have logarithm
O(B+N+gamma); Q is a sufficiently large fixed multiple of B to dominate
2B+2N+3gamma plus polynomial error factors. Finite checks of local maps are
not an executed full all-size integer multiplier or explicit full cutoff.

## The genuine surviving CRT obstruction

For original scalar coefficient index k=sum_j a_j P_j,
`P_i=product_(j<i) s_j`, the cyclic algebra map has coordinates

`b_i=a_i+mu_i sum_(j<i) a_j P_j mod s_i`, `mu_i=P_i^-1 mod s_i`.

The inherited implementation performs d controlled interval rotations of
payloads. The known binary-coordinate permutation pays their AXIS ORDER,
not these nonlinear modular rotations. Metadata dominated by Q cannot
remove the O(nd) physical movements. Primary finite-tape CRT literature
examined by the scout likewise charges transpositions/rotations and does
not supply the needed sub-d joint map.

Consequently every justified assembly here must retain the normalized rows

| Operation | Power of B0, ignoring polylog(B0) |
|---|---|
| Triangular CRT and inverse | epsilon |
| Deferred main Fourier groups |1-epsilon*q |
| Paid named-coordinate routing |1-a |
| Polynomial suffix products |1-epsilon |
| Packed recursive children |epsilon*(1-kappa) |
| Sparse repair sorting |1-2epsilon |
| Direct phase band LU |-epsilon |
| Scalar construction and scans |0 |

Strict absorption requires `kappa<min(1-epsilon,epsilon*q,a)`, q<a.
For fixed q the first two rows balance at epsilon=1/(1+q). Their supremum
is q/(1+q), so the scoped limit is a/(1+a), not a. The initially predicted
near-a parameters fail the corrected exact CRT slack. The corrected balanced
ledger has strictly positive arithmetic gaps and provides no improved bound.

## Terminating self-reduction, not an assumed improved oracle

Each packed integer child has length at most
`S_child=C Q lambda_F^d=exp(O(B0^epsilon log B0))=n^o(1)`.
The sum of all child bit lengths is at most C' n; all signed products, holes,
two grids and coefficient reserves only change fixed constants. Eventually
S_child<n/2. Use the SAME algorithm recursively, with a conventional finite
base case. No improved multiplication oracle is assumed.

If the nonrecursive saving is g>kappa, a strong-induction bound has normalized
right side at most

`(A/C_ind)*B0^(kappa-g)*polylog(B0)
 + C''*B0^[-(1-epsilon)(1-kappa)]*(log B0)^(1-kappa)`.

Both terms tend to zero for epsilon<1,kappa<1. Choose an eventual threshold
where their sum is below1/2 and increase C_ind to cover the finite base.
This absorbs the recursive leading constants. The CRT row controls g and
prevents the stronger claimed exponent; recurrence absorption does not fix it.

## What remains and what is retained

The accepted evidence supports local general lemmas and scoped negatives.
All-size compiled premises, constructive eventual prime thresholds and final
error constants remain distinguishable from finite numerical/exact controls.
A useful stronger result needs a genuinely paid joint CRT layout or a different
cyclic-convolution representation. Fixed bit permutations, free computed-key
sorting, sparse halos on arbitrary large CRT shifts, or ignoring carry terms
do not provide that interface. This is the next research target.
