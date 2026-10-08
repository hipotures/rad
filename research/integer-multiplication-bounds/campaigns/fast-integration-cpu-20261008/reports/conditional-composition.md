# Full cost ledger for the packed tensor candidate

Status as of 14:39 UTC: the old unbatched CRT assembly remains rejected.
A new guarded-reflection CRT tree has independent algebra and physical layout
reviews and supports an improved exact conditional composition. The complete
Gaussian/FFT/recovery cost and error closure has a separate independent
[written review](../agents/scout/full-composition-review.md). This is a promoted
written conditional result under the named native hypotheses, rather than a
new formally certified finite native witness. The numerical
controls are finite evidence, not a replacement for the all-size contracts.

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
suffix chooser, source-closed sparse repair, and restored dirty-guard modular CRT batching. General tools used inside
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
The primary Baker--Harman--Pintz theorem supplies a prime in
[x-x^(21/40),x] eventually. The required interval has width at least
c_theta*d^-16*t/4; it contains d disjoint prime windows once
c_theta*t^(19/40)/d^17 grows. Its base-two logarithm is at least
(19/40)*ell-17*log2(d)+O(1), which tends to infinity. This gives d distinct
odd primes, including when capacities coincide. Trial division of all
candidates costs at most poly(d,log t)*t^(3/2)=n^o(1).
See the [primary-source review](../agents/scout/prime-interval-review.md).
The theorem is effective in principle; no numerical full-machine cutoff is
supplied here. S/T tends
to1, since sum_i theta_i=O(d^-15). Original digit products have degree less
than T/2<S, so cyclic source convolution causes no coefficient wrap.

Choose alpha as the ceiling of sqrt(B/(64d)) and u=alpha^2. Eventually
`B/(64d)<=u<=B/(16d)`, hence the total resampling scale
`gamma=2du<=B/8`. With C_D sufficiently large relative to c_theta,C_Q,
`u^2 theta_i>=2Q`, u theta_i grows, and all inherited Gaussian contraction
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
An inverse Laurent coefficient can exceed1. Normalize each one-axis inverse
vector by the rational L=1+1/d^2, after choosing the eventual phase margin
so its perturbation norm is at most1/(4d^2). Every normalized coefficient
has modulus at most1; restore L^d<2 in one scalar factor. This avoids an
unsupported assumption that inverse coefficients themselves contract.
Round EACH normalized contracting prefix product; keeping all d exact denominators would
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
including remote Gaussian aliases as a separate perturbation. Every inverse repair packet can have free complete axes, including regular
bad-grid pair packets. A regular Laurent-only pass on a complete free axis
would include phase exceptions and is invalid. Retain the cyclic topology
of each free axis: cover each such
axis by overlapping principal windows using R_exception, compute a window,
and return only its core before proceeding to the next axis. The transient
window replication is a fixed constant at one stage and does not compound
to 2^d. A single ordinary band LU that omits a cyclic corner is insufficient.
Regular constrained faces still use regular-radius principal windows and
regular-phase core locality; their source volume stays unchanged. The global
free-axis band-LU charge is O(n/d^2) for regular repair packets and O(n/d)
for phase repair packets, before the scalar arithmetic reserve below.

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

The source inverse is not the bare N^-1 Gaussian solve. In the pinned
source convention A=S'=S/2, J'=N_matrix^-1/2 and
D'=2^(-(2u-2))*diag(exp(pi*u*beta_j^2)); B_source=D'J'C.
Retain the factor1/2 per axis and the opposite transform signs explicitly.
Their product gives the inherited resampling normalization2^(-2du), with
gamma=2du. These diagonal/scalar factors are folded into the already paid
joint packet passes, not implemented by another d full-payload scan.

Source-transform chirps formerly computed d Q-bit factors per coefficient.
They can instead sum their O(B0)-bit phase numerators using O(d B0^2) metadata
work, then compute ONE Q-bit exponential. The cited elementary-function primitive
costs O(Q^(1+zeta)) for every fixed0<zeta<1/8; it is not silently a polylog-only
primitive. Choose zeta=1/1000. The one phase per coefficient costs
O(n*Q^zeta), with B0 exponent18*epsilon*zeta. Band-LU exponents are
-epsilon+18epsilon*zeta for phase packets and
-2epsilon+18epsilon*zeta for regular packets. Each is explicitly below
the target1-kappa; fixed zeta is not treated as o(1). Long Q pays this metadata, but
cannot pay repeated payload movements. Exact-recovery scales have logarithm
O(B+N+gamma); Q is a sufficiently large fixed multiple of B to dominate
2B+3N+gamma plus polynomial error factors. For normalized input digits,
the inherited final error bound is
`448*N*2^(2B+gamma+3N-Q)`.
For example Q>=6B, gamma<=B/8 and N<=B make this less than1/2 eventually.
The bound transfers only after the changed complete maps satisfy their
uniform rounded error contracts, including all sparse and phase outputs.
The independent recovery review checks this obligation separately. Finite checks of local maps are
not an executed full all-size integer multiplier or explicit full cutoff.

## Old obstruction and the new paid CRT replacement

For original scalar coefficient index k=sum_j a_j P_j,
`P_i=product_(j<i) s_j`, the cyclic algebra map has coordinates

`b_i=a_i+mu_i sum_(j<i) a_j P_j mod s_i`, `mu_i=P_i^-1 mod s_i`.

The inherited triangular implementation pays d controlled interval rotations.
Known binary-coordinate routing pays their axis order, not the modular
rotations. Keeping that algorithm imposes the normalized epsilon CRT row,
and the scoped a/(1+a) ceiling remains valid. The rejected exact ledger
retains this negative result without reinterpreting it as a general lower bound.

The new [guarded CRT lemma](../agents/inverse/reports/guarded-crt-batching.md)
uses a balanced tree. Split k=A+S_L*B, rotate
B by S_L^-1*A modulo S_R, and recurse independently in both children.
All nodes at one depth have disjoint fixed controls and targets. Joint
monotone occupied-slot scans maintain the same exact binary volume T.
After bounded ordinary top levels, two width-balanced active classes borrow
actual inactive coordinates as dirty banks; there are no new address bits.
Conditional complements use the extended repeated-source native bit shear.
Three guarded interval reflections implement the required modular rotations.
Their outer repair uses the actual reversed program and stable binary radix
sorting, and finishes before any zero padding is deleted or a new split starts.
Every inner native shear repair is paid and completed too.

Use the conservative inactive bank bound N/8 and router spacing256G_router.
Nine router fields occupy less than N/16, outer dirty U/T less than N/64,
and an untouched suffix ell less than N/64, eventually. These disjoint
fields fit the real bank with positive margin. Guard failure density is
O(B0^-5). Arithmetic descriptors, offset evaluations and inverse keys have
an explicit conservative degree-four metadata bound with polylog factors;
Q=Theta(B0^(18epsilon)) absorbs it. The enlarged untouched suffix pays the
ordinary prefix computations. This yields
`O(TQ*B0^(1-a)*polylog B0)` for the complete forward and opposite CRT maps,
including O(log d) levels, all paid routes, repair and joint scans.
See the independent [algebra review](../agents/scout/guarded-crt-review.md)
and [layout review](../agents/layout/crt-reflection-layout-review.md).

The replacement gives this conditional ledger:

| Operation | Power of B0, ignoring polylog(B0) |
|---|---|
| Guarded tree CRT and inverse |1-a |
| Deferred main Fourier groups |1-epsilon*q |
| Paid named-coordinate routing |1-a |
| Polynomial suffix products |1-epsilon |
| Packed recursive children |epsilon*(1-kappa) |
| Sparse repair sorting |1-2epsilon |
| Direct phase band LU |-epsilon+18epsilon*zeta |
| Regular free-axis band LU |-2epsilon+18epsilon*zeta |
| One source elementary phase per coefficient |18epsilon*zeta |
| Scalar construction and scans |0 |

The nonrecursive absorption condition is now
`kappa<min(a,epsilon*q,epsilon)`, with q strictly below both native bit
saving and stopped complex leaf saving. The remaining rows are strictly
below1-kappa for the explicit parameters below. The child row is absorbed
by strong induction rather than by assuming an improved oracle.

Take epsilon=999999/1000000, beta=1/20, zeta=1/1000,
q=783776909222307/20000000000000000000 and
kappa=78376985522307/2000000000000000000.
The exact ledger records all strict rational gaps; the smallest native gap
is783777693/40000000000000000000. The candidate kappa is approximately
0.0000391884927611535, above the old a/(1+a) scoped supremum by approximately
1.143820e-9. These arithmetic statements are exact; they alone do not
validate the complete numerical/physical composition.

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
This absorbs the recursive leading constants. The new guarded CRT row permits g>kappa for the displayed parameters.
With the old triangular implementation its epsilon row restores the old
ceiling; recurrence absorption never removes a genuine payload charge.

## Verification boundary and continuing experiments

The written conditional candidate uses named native finite moment/compiler,
semantic guard, product row stock and routing inputs. It does not claim a
new independently audited finite native witness. The newly derived local
lemmas and guarded CRT replacement have independent agent reviews, finite
exact controls and retained falsification evidence. Full native fixed-tape
implementation and formal verification have not been executed.

Current discriminators execute the entire nested native/guarded CRT program
on complete small boxes; larger period-mismatch cyclic inverse families;
full source normalization; and a small complete Gaussian/FFT/convolution/
compression/opposite/recovery pipeline. The recovery reviewer is checking
uniform complete-map precision contracts. The written all-size composition is now independently reviewed and promoted
relative to its named native contracts. A new finite native witness, formal
proof and executed complete fast-tape multiplier are not claimed. Numerical
full-pipeline tests execute some Gaussian stages by explicitly charged dense
reference passes; they validate arithmetic and signs, not the asymptotic cost. The user extended the campaign indefinitely; this report
will be updated as evidence arrives, with scientific checkpoints pushed.

## Promoted conditional transfer and explicit limits

Assume the pinned native bit and complex finite moment/compiler contracts,
their semantic guard with coefficient1, fixed-tape chunk interchanges and
complete restored bit routing. With bit saving a and a stopped complex saving
strictly above a, the new construction yields
`T(n)=O(n*(log n)^(1-kappa))` for every fixed rational0<kappa<a.
Choose q strictly between kappa and a, then epsilon strictly between
max(1/2,kappa/q) and1, and a sufficiently small fixed scalar exponent zeta.
All native lambda gaps are strict; all changed Gaussian, layout, CRT and
recursion rows above are paid. This is a conditional implication, not an
assertion that this campaign independently certified the native inputs.
The displayed rational kappa is an explicit witness exceeding the old
unbatched a/(1+a) ceiling and the pinned eligible public integer claim.

The choice of constants must retain the STRICT inherited Gaussian condition
`theta>Q/u^2`; choose C_D large enough that `u^2*theta>=2Q`.
This is available at the existing degree equality18=16+2 and changes no
power. Numerical grid tests are not substitutes for this constant choice.
The full effective machine cutoff is unspecified and may be enormous.
No practical speedup or worldwide-best theorem claim is made.

## Changed-DAG input refinement, 15:58 UTC

The same transfer now has a newly executed exact finite h23 input paired with the pinned h25 producer. Its independently checked full fixed-basis/controller saving is a_new=397034999791/10000000000000000, and the resulting reviewed conditional witness is kappa=39703102944100209/1000000000000000000000. The unchanged complex producer and C1 constants satisfy the same native bridge; replacing the bit input therefore extends the stated conditional range to every fixed rational0<kappa<a_new. See [construction, exact evidence and independent review](changed-fixed-composition.md). This retains the named full tape/compiler premises.

The second changed axis has now also passed independent support/link/controller and native bridge checks. The [joint refinement](changed-fixed-composition.md) extends the conditional range to a_joint=80475950257/2000000000000000 and supports kappa_joint=8047514549749743/200000000000000000000. All named premises of the transfer remain explicit.
