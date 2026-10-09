# Independent field-cyclic algebra, packing and transfer review

Status: **EXACT FINITE ALGEBRA REVIEW** and **CONDITIONAL COST DEDUCTIONS**.
The finite-field reduction supplies a genuine new fixed-kernel interface.
The current evidence does not supply a native algorithm for that interface,
an improving recursive multiplier, or a positive multiplication exponent.

## Independently accepted algebra

The producer is
[finite_field_cyclic_reduction.py](../../code/synthesis/finite_field_cyclic_reduction.py),
effective SHA-256
`7044ff3bfedeaf76ccf56c00885a90ebc0df80af94cfa46175b1d8dc45c3d17e`.
Its [report](../synthesis/finite-field-cyclic-core.md) distinguishes its
nonrecursive Python integer products from a proved native multiplication cost.
The [immutable review fixture](../../fixtures/transfers/field-cyclic-producer-contract.json)
retains the exact field, kernel and permutation contracts from the producer's
certificate, whose hash and original location are recorded there. Timing and
basis hashes omitted from this small fixture remain in that certificate.

My [independent source](../../code/transfers/field_cyclic_cost_review.py)
imports no producer code. It constructs polynomial products followed by
binary polynomial long division, computes trace by separate exponentiation,
inverts the trace Gram map by exhaustive finite images, evaluates Walsh entries
from ordinary binary dot products, and encodes signed monomials separately.
The Gaussian tensor entries are reconstructed as
`alpha^d*(-i)^popcount(row xor column)` with `alpha=(1+i)/2`.

Put `D=2^d`, `M=D-1`, and `k_j=(-1)^Tr(g^j)` for a supplied primitive element.
Input order is `g^(-j)` and output order is `G*g^i`, where G is the trace Gram
matrix. The independently reordered full Walsh matrix is

```text
W = [[1, ones^T], [ones, K]],   K[i,j]=k[i-j]  (indices modulo M).
```

The exact identities `K*ones=-ones` and `K^T*K=D*I-J` give
`K^-1=(K^T-J)/D`. Consequently the inverse cyclic kernel is
`(k[-j]-1)/D`, not an independently guessed sign or missing-zero transform.
The supplied finite field is enough for this all-size algebra; these four
primitive polynomials do not constitute a uniform field-generation theorem.

The two zero-coordinate shears matter. With B subtracting the zero input
from every nonzero input and A subtracting the sum of transformed nonzero
values from the zero output,

```text
W = A * diag(D,K) * B.
```

I checked every entry including the zero row and column. The Gaussian chirps
and global normalization then give the exact C tensor, with its explicit
inverse. The complete word applies C to the source, adds it into the sink,
undoes C on the source, and applies C to arbitrary dirty scratch. The scratch
endpoint is C times its original arbitrary value; it is not a zero bank.

Four workers checked d=3,4,5,6, all 360 independent three-bank basis columns
with Gaussian value `1+i`, and additional mixed arbitrary dyadic fields in
28.651 seconds. This basis suffices because the program's Gaussian-linear
operations and the exact signed-packing lemma establish complex linearity;
it is not an assertion that one sampled Gaussian value spans two real
directions without that premise. All forward, inverse, source-restoration,
sink and dirty endpoints matched the independent tensor formula. Each complete
word uses three cyclic convolutions and six actual real integer products.

The [complete compact attempt](../../runs/20261008T235517Z-transfer-field-cyclic-review/report.md)
retains all counts, hashes and scopes. Matched controls detect omitted zero
scaling, omitted border sums, incorrect inverse kernels and insufficient
balanced radix. A zero numeric operand still reserves all M physical
coefficient positions. Its short Python integer representation does not
permit skipping the complete native payload.

## Signed packing and long coefficients

For signed integer coefficients bounded by A and kernel numerators bounded
by H, an ordinary convolution coefficient has absolute value at most M*A*H.
Choosing `2^s>2*M*A*H` makes every coefficient lie strictly within the centered
base-`2^s` digit interval. Repeated centered residues therefore recover the
complete ordinary product, including negative coefficients; folding degree
j+M into j gives the cyclic result. Clearing a Gaussian-dyadic denominator
and dividing by it, and by D for the inverse, remain explicit operations.
The review compares every extracted ordinary digit against independently
summed coefficients, rather than relying only on a zero leftover high digit.

For a whole Q-bit coefficient, a reserved packed operand has approximately
`M*(Q+d+O(1))` bits. Its logarithmic size is `d+log Q+O(1)` when Q dominates d.
It holds the whole current fiber. In an ambient array with many fibers it may
be smaller than the global input, so this observation is not a universal
same-size recursion impossibility. It does not itself decrease selected width
or furnish a well-founded native coupled recurrence.

Slicing coefficients into b-bit signed chunks changes that scale. Each chunk
needs spacing `s=b+d+O(1)`, and each coefficient needs `O(Q/b+1)` chunks.
The complete real-product input volume is thus

```text
O(M*(Q/b+1)*(b+d)),
```

including the reserved high positions and every slice. Taking b at least d
and polynomial in d makes it O(M*Q) when Q is at least b, while the logarithm
of each product operand is Theta(d). This is the useful possible transfer
interface, rather than a free whole-record recursive call.

Exact signed slice reconstruction passed for Q=17,65,129, b=4 or 8, at each
tested field size. For example d=6,Q=129,b=8 uses 18 signed chunks, 15-bit
spacing and 945 reserved operand bits per chunk, with total input-volume
inflation `90/43`. The intentionally conservative extra signed chunk is
charged. These are finite arithmetic controls, not native transpose timing.

Both transpose directions and reconstruction must be paid. The input is
coefficient-major, whereas each product needs one entire field vector of a
fixed chunk index. Python list slicing is an algebraic oracle in this review.
The output must return to coefficient-major order before streaming signed
carries. Once that order is supplied, a digit at a time can combine the current
slice coefficient and previous carry, emitting b bits and retaining O(d) carry
bits; that proposed linear reconstruction still needs its literal tape
interface. Repeatedly rescanning every Q-bit record for every slice would cost
Omega(M*Q*(Q/b)) and does not establish the desired bound. A general multi-pass
transpose also needs its actual number of full-payload passes charged.

## Precise condition for mathematical leverage

Here is a scoped transfer test. Assume a complete selected-width primitive on
full volume V, including the dirty word, costs

```text
O(V*d^gamma*polylog(d)).
```

This must pay all six fixed-kernel products, both field-address permutations,
every coefficient transpose, signed packing/extraction/folding, chirps, zero
borders, all guards, record setup and every companion/control field. Suppose
the outer architecture makes O(p/d) such rounds for `p=Theta(log n)` and chooses
`d=p^epsilon`, with `0<epsilon<1`. Its resulting exponent contribution is

```text
T(n) = O(n*p^(1-epsilon*(1-gamma))*polylog(p)).
kappa_new < epsilon*(1-gamma)  after positive slack and other contracts.
```

If the only implementation of the fixed-kernel products is an assumed general
multiplier with saving kappa_call, then `gamma=1-kappa_call` even after granting
linear-time routing and transposes. The unchanged outer construction returns
only `epsilon*kappa_call`, strictly less than kappa_call. This is the scoped
circularity obstruction. Six products are a constant factor, not an omitted
exponent, but assigning the desired improved multiplier to those products
cannot bootstrap that same improvement by this unchanged architecture.

An independently proved fixed-kernel algorithm with saving eta could pass
this test if `epsilon*eta` exceeds the target and every other paid charge is
smaller. For the 1e-4 target, required eta is greater than 4e-4 at epsilon=1/4,
2e-4 at epsilon=1/2, or 4e-4/3 at epsilon=3/4. These are necessary values for
this conditional contribution, not accepted final exponents or permitted
outer parameter choices. An exponent at most gamma for the kernel is
insufficient if its actual router costs O(V*d): that full-volume term alone
sets the primitive bound back to gamma=1. The same issue applies to expensive
transpose passes, convolution normalization or temporary precision.

This test does not rule out a genuinely cheaper fixed kernel, an outer
construction with a different number of rounds, a different analytic coupling,
or a complete payload-decreasing same-width recurrence. Those alternatives
need their own time/row/depth, exact endpoint and precision contracts. The
[routing-aware stopping lemma](routing-aware-depth-transfer.md) demonstrates
how to state such contracts without declaring the current products smaller
by fiat; no frozen child ledger is transplanted here.

## A structural limit on a tempting kernel shortcut

The short binary LFSR description of k does not imply a short Gaussian-linear
cyclic filter. Since K is invertible, its M cyclic shift vectors are linearly
independent over the rationals and Gaussian rationals. If
`sum_j c_j*shift^j(k)=0`, every coefficient c_j is zero modulo the M-position
representation. In particular no nonzero cyclic annihilator using fewer than
M shifts exists. This is an immediate all-size consequence of the accepted
core inverse, not a complexity lower bound on convolution algorithms.

The binary primitive-polynomial recurrence becomes a product of signs under
`(-1)^trace`, rather than an ordinary linear recurrence of those signs. It
can generate kernel data cheaply, but a claimed small-tap linear convolution
algorithm must supply an additional mechanism. FFT, nonlinear layouts and
special fixed-kernel algorithms are not excluded by the shift-span statement.

## Physical boundaries and next work

Polynomial-to-multiplicative field ordering remains a nonlinear address map.
The parent is independently examining its prefix-affine obstruction; that
separate result concerns the old linear address-relabeling interface, not all
paid native routing. No free logarithm lookup or scattered table gather is
imported here. Finite field enumeration and trace Gram setup must also be
uniformly generated and amortized with their actual space and time costs.

Moving Gaussian normalization early reduces the producer's zero-source peak,
but is not an arbitrary-payload fixed-grid guard. Native integer product
buffers, all signed slice accumulators, inverse denominators and every dirty
field must enter the prefix bound. The independently reviewed
[endpoint-aware guard](endpoint-aware-guards.md) is conditional on those
literal local-prefix and complete returned-endpoint interfaces; it does not
certify them from this finite replay.

A discriminating next direction is an independent algorithm for the specific
m-sequence fixed kernel, or a paid address layout retained across a changed
outer architecture. At the current stage, the algebra is accepted as a
component, while native cost and asymptotic leverage remain hypotheses.

## Reproduction and run integrity

The bounded check depends only on the retained review source and its fixture:

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/field_cyclic_cost_review.py \
  --workers 1 --small
```

The full four-worker command and seeds are retained in the attempt protocol.
Use a fresh output path. The initial raw full-run namespace was manually chosen
152.444568 seconds later than the actual recorded start. It is preserved
unchanged, with an explicit integrity note. The durable attempt ID is derived
from `created_utc=2026-10-08T23:55:17.555432+00:00`; the namespace is not timing
evidence. The preliminary small raw namespace was also manually chosen later
than its recorded start and is not used as scientific timing evidence. Future
attempt names should be generated from the actual clock.

This review was developed by an independent OpenAI Codex research agent. It is
not external peer review or formal verification.
