# Independent product-gather and primitive-cap review

Reviewed 2026-10-08 around 13:35 UTC. This is source criticism of the local
layout and analytic interface, not a full tape compiler certificate or external
mathematical acceptance. The written all-size arguments and finite controls
have different roles.

## Product embedding and shifted source order

The one-pass fractional injection in
[the layout lemma](../layout/joint-fractional-gather-lemma.md) is sound: each
axis partitions its source interval into increasing consecutive cores and maps
their local indices into consecutive occupied slots of a binary target core.
The resulting strictly increasing one-dimensional injection preserves order.
Its Cartesian product preserves lexicographic order of occupied slots,
including zero-valued records. Thus a single advancing source head suffices;
neither a nonlinear-key sort nor d source payload scans is implicit.

Metadata work is paid. A deliberately conservative d independent divisions on
B-bit addresses costs O(d B^2) per output record. With d=Theta(B^epsilon),
Q=Theta(d^18), and epsilon>1/2, d B^2=o(Q). This is legitimate long-record
accounting; the assertion would fail if the source retained its old short
precision and the metadata were silently free.

The shifted-grid implementation makes one *flat* mixed-radix stream rotation.
It is equal to the desired coordinatewise translation only when no coordinate
overflows. This is exactly the stated qualification, not a global translation
identity. Source-period cut neighborhoods of the larger forward cell scale
must enter the sparse repair proof; inverse phase strips alone are too narrow.
The corresponding target rotation and the reverse source rotation are also
paid stream operations. Occupancy deletion after restoring the known bit
permutation returns the source's relative lexicographic order, then the paid
rotation returns its global order away from those excluded cuts.

Nearest-index selection is strictly increasing for t/s>1. Its Cartesian product
can be read by one advancing packet scan on outputs whose selected indices
remain in the supplied packet. A two-position rounding margin and the true
kernel radius are necessary. The checker correctly retains boundary exclusions
rather than treating a floor plateau as a valid occupied source slot.

## Router and transform contracts

The historical [arbitrary-routing review](../../../../reports/review-arbitrary-routing.md)
at RaD commit `6b32837aee0561af85e4efaca21af07b9f2749d2` supports a known
coordinate permutation on a complete binary rectangle. It explicitly supplies
short-record routing with three spectator cohorts and uses the original chunk
interchange to create paid enlarged records. The third field is at the actual
suffix. Reversing the placements restores every coordinate name. Applying
that contract to the global gather is justified only with its active masks,
bad-hole repair, current-address inverse and record-stock assumptions retained.
It is not an arbitrary computed-key sorting result.

In the new long-digit regime the short-record fallback should be restated in
terms of B and the actual minimum axis width ell, rather than reusing the old
p=Theta(B) identity: O(V ell) is within O(V B^tau) when
ell=Theta(B^(1-epsilon)) and epsilon>1-tau. Superpolynomial spectator fields
still absorb polynomial metadata because ell/log Q tends to infinity.

The deferred transform's source-supported external-field contract is reviewed
in [deferred-reservoir-review.md](deferred-reservoir-review.md). Its new second
group needs complete external row and dirty work fields, restored before every
child or scalar call, and the same stopping rule. A claim about exact Fourier
commutation does not itself establish that compiled contract or truncated
operator commutation. The report correctly uses normalized contraction errors
and common named frequency slots for both operands.

## The cap on any transferred saving

Put tau=1-a_bit and sigma=1-a_complex. With the supplied external-field layer,
lambda_prime must strictly exceed tau, sigma and the stopped leaf exponent
sigma+beta(1-sigma). Its saving q=1-lambda_prime therefore satisfies

`q < min(a_bit,(1-beta)*a_complex)`.

The full transform has cost
`O(V [ell*d^lambda_prime+B^tau+log(rQ)] polylog(Q))`, so its three savings are
epsilon*q, a_bit and epsilon. A packed Gaussian child contributes saving
`1-epsilon*(1-kappa)` under the same terminating recurrence. These facts permit
approaching the bit primitive's saving when all repair, setup and recovery rows
are actually paid. They do not permit equality at a_bit or adding independent
primitive savings.

For beta=1/20 and a_complex=717/10^7, the complex leaf saving is
6.8115e-5. It exceeds PR40's a_bit=783777693/(2*10^13)=3.918888465e-5, so the
bit primitive remains the ceiling. PR40's public composed kappa is
3.918734894e-5. The largest possible absolute gain over that number within this
transfer is 1.53571e-9, about 0.003919 percent. A result instantiated only with
PR37's weaker bit primitive must not be described as beating current PR40.

## Precision-source qualification

The current copied-complex primary proof is
[notes/copied-centers-assembly.tex](https://github.com/rohanarun/integer-mult-bounds/blob/43f59ff533598762cbc43a5e14af2bbbc76fabbd/notes/copied-centers-assembly.tex).
It includes scalar group G in E and proves a linear guard using completed-child
denominator and row-sum semantics. Reserving a looser C d^5 with Q=d^18 still
depends on that semantic argument unless a separate guard is derived.

The older notes/compact-control-guard.tex uses an equal-child recurrence
s A(e/m)+E. Its exponent 5-4 beta+zeta cannot simply be copied to the present
unequal-width children. A new universal concatenation bound is possible with
much longer polynomial digits: current complex m=784, maxchild=756 and total
child rank s=421548223824 give the exact rational check
`8*s*(756/784)^1000 < 1/1000` (approximately 0.00054158929). Under an explicitly
verified upper bound of 8s child calls per invocation, induction supplies a
degree-1000 depth bound plus outer overhead. Matching Q to a higher fixed degree
would preserve polynomial local sides and n^o(1) children. This is an optional
conservative guard route, not a proof that the old exponent5 applies unchanged.

## Remaining limits

The accepted local ordering arguments leave full sparse SOURCE multiplicity,
true Gaussian precision, recursive constants, CRT selected-bit movement and
compiled external-bank operations as separately stated obligations. Finite
PASS certificates exercise provenance and exact operators; they do not replace
those all-size premises. The new product embedding and deferred schedule are
new relative to the inspected pinned sources; worldwide novelty is unproved.
