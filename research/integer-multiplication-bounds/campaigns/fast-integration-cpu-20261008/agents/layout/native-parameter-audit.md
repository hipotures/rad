# Native compact layer with independent address and coefficient precision

Audited 2026-10-08 against CrocSwap PR37 head
`cb86e50e9a07685068874d8e4174b2e6c209b95c`, pinned `upstream/build/sections/05-layers.tex`,
`06-transforms.tex`, `08-assembly.tex` and `notes/compact-control-layout.tex`.
This audit rederives the changed parameter interface; it does not invoke the
old theorem's displayed promise unchanged. Primitive moment/graph proofs,
semantic completed-child guard and the short-record coordinate router remain
explicit conditional inputs.

## An acyclic exact parameter chooser

Let `b=ceil(log2(n))` and choose fixed rational `1/2<epsilon<1`.
Set digit width `b_digit=ceil(b^(18epsilon))` and precision `Q=6b_digit`.
Choose the binary coefficient volume T in `[4n/b_digit,8n/b_digit)` and write
`N=log2(T)`. Compute the MAIN width first:

`ell=floor(b^(1-epsilon))`, `d=floor(N/ell)`, `h=N-d ell`.

Then `0<=h<ell`, d=Theta(b^epsilon), Q=Theta(d^18), and
`log2(r)=ell+h<2ell` for the polynomial suffix r. All quantities are obtained
in this order by fixed rational power comparisons, integer divisions and shifts.
There is no fixed-point definition of d via a precision depending on d.

Choosing d first and setting ell=floor(N/d) would give only h<d. For epsilon>1/2
that can make log r=Theta(d) and recreate the O(Vd) pointwise-product charge.
The exact chooser order is part of the scientific construction, not cosmetic.

## Old promises and the actual uses in their proofs

The old simultaneous-layer promise `d=Theta(p^epsilon_old)` and
`r=2^Theta(p/d)` appears at05-layers lines21--22 and849--850. Its proof uses
these bounds at934--962 solely for the following operational consequences:

- Guarded component width remains O(p): Delta=ceil(C0 d^C1)<=p.
- `A_*=ceil(log2(2M_child R_guard))<=C_Ap` for every current child.
- `K/log(p)->infinity`, so exceptional packed-address terms vanish.
- r grows faster than every fixed polynomial in p, absorbing address arithmetic
  and metadata inside the polynomial record's actual rp-bit scan.

The transform proof uses the same bounds at06-transforms lines297 and384 for
header/layout and twiddle arithmetic domination. Its inequalities `d log2(r)=O(p)`
and log2(M)=O(p) bound descriptor lengths, rather than tying physical address
length to coefficient precision from below. No inspected proof step requires
the numerical lower bound `r>=2^(a_r Q/d)` once those consequences are rederived.

The current compact note replaces the OLD packed `K^tau` overhead. Its recurrence
uses a global stop `e<d^beta`, G=O(log p), and actual selected width e. Therefore
its internal exponent is `chi=tau+(1-beta)max(sigma-tau,0)` and its leaf exponent
is `sigma+beta(1-sigma)`; neither exponent gains a factor18 from long coefficients.
Only the logarithmic G changes to log Q.

## Direct checks with Q much larger than the address length

For the new chooser, set p=Q in native coefficient words. The accepted semantic
completed-child guard has `Delta<=C0d`, with fixed finite C0 and C1=1.
Then Delta/Q=O(d^-17)->0. This audit retains that precise premise; it does not
substitute a crude depth estimate for the primitive's guard proof.

The guarded polynomial record has `R_guard=Theta(rQ)` bits. Actual address length
is N=Theta(b), so even allowing row padding and headers,

`A_*=O(N+log(r)+log(Q))=O(b)=o(Q)`.

The old loose `A_*=O(Q)` statement remains true. Compact descriptor/key arithmetic
is polynomial in these supplied values; the old ordinary terms
`A_*^3/R_guard` and `d 2^-K A_* (1+A_*/R_guard)` tend to zero, because

`K=ell=Theta(b^(1-epsilon))`, `log(Q)=Theta(log b)`,
`log(r) in [ell,2ell)`, and `r/Q^C ->infinity` for each fixed C.

Uniform constants exist for every sufficiently large input in this fixed rational
epsilon family. Native supplied K may be a constant-factor band around
`d^c`, `c=(1-epsilon)/epsilon`, rather than exactly floor(d^c). The physical proof
uses lower superlogarithmic growth and an O(Q) address/descriptor upper bound;
the current compact overhead uses G rather than K^tau. Both are uniform in
that band. In the equal-main-axis transform there is exactly ONE chunk per
axis, with K equal to its actual width. The former `K<=log2(r)-1` or
ell/K->infinity promises belong to the old unequal-width/chunk regrouping
construction and must be restated, not silently retained.

Every main transform length t=2^ell divides2r and is at least sqrt(r).
Root character cancellation, bit-reversal significance and signed monomial
coefficient permutations therefore still hold; the independent generalized
Fourier and full ring convolution checker covers h=0 as well as h>1.

## External dirty fields and row stock

The row and work requirements are unchanged:

`G=4ceil(log2(Q))+6`, `H=dG`,
`qF=ceil(2H/K)`, `qB=ceil(H/K)`,
`q0=ceil(log2(W))ceil(log_m(2d))`.

Their donor-axis count is `q0+qF+qB=O(log d+dG/K)=o(d)`, since K/log Q tends
to infinity. The initial donor axes are deferred as whole transforms.
The second group borrows the same fields from completed main axes. This is
the [external-field/deferred-reservoir construction](deferred-reservoir-transform-lemma.md),
not the old per-round reservation-kernel schedule. Hence the old assembly's
reservation condition `1-c<lambda_prime` is not a cost condition of the new
schedule. Deleting that inequality without providing the external fields and
paid routing would be invalid.

The complete row range `2^(q0K)` dominates every fixed power of Q, because
log2(Q)=Theta(log d) while K tends to infinity. In particular a fixed supplied
joint bit/complex row-stock estimate Q^2000 fits eventually. Its rows are still
constructed, padded and restored on tapes, with at most a factor2 current-volume
increase per completed layer. This is an eventual stock inequality, not an
explicit numerical full-machine cutoff or a materialized growing advice table.
Actual native finite basis/table construction remains a separately charged
fixed setup assumption.

## Remaining full algorithm charges

Exact target volume satisfies TQ=Theta(n). Input digit capacity remains
`coefficient<2^(3 b_digit)` once q<=2^b_digit, which holds eventually.
Address N=Theta(b), instead of Q, controls the synthetic layer count and the
coordinate-router exponent. The native bit routing cost is
`O(n b^tau polylog b)`; two deferred groups cost
`O(n ell d^lambda_prime polylog b)`.

Ring products retain log(rQ)=Theta(ell+logQ), so their saving is epsilon in b.
Twiddles are ordinary signed rotations of an rp-bit polynomial record and
their setup is absorbed by r's superpolynomial growth. Prime searches and
axis setup are polynomial in the actual axis lengths and Q; their logarithmic
time is O(b^(1-epsilon)+log b)=o(b), so they remain n^o(1).

The Gaussian normalization, long-digit rounding threshold, regular/exceptional
packed kernels, sparse source-packet volumes, shrinking repair buffers and
inductive self-reduction are new assembly obligations. They are not certified
by the native layer audit or a finite PASS label. The coordinator retains them
as separate proof dependencies.
