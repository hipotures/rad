# Nonunit address amplitudes and exact pre/post preflight

Status: **CONDITIONAL PAULI SUPPORT LEMMA**, **EXACT FINITE OPERATOR TESTS**,
and **UNRESOLVED NATIVE BOUNDARY HYPOTHESIS**. No new canonical supplier,
native postprocessor or multiplication exponent is established.

## Structural hypothesis and leverage

The [joint mutable-source core](joint-mutable-birth-algebraic-cleanup.md)
has a favorable child profile before its canonical source boundary. Its
normalized moment is `(1/12)*4^b+(5/6)*2^b`; it has substantial slack near
the campaign target `b=1e-4`. The two separately paid line corrections remove
that slack. A complete boundary with polylogarithmic work per current volume,
rather than a recursive line call or a linear number of full scans, would
be a structural change. Such a boundary is not supplied here.

The [preceding discriminator](address-dependent-boundary-obstructions.md)
excludes post-only shallow repairs and one pointwise bank mixer on each
boundary. It deliberately leaves deeper, address-dependent nonunit words
open. The present tests add those coefficients and interleaved routing on
the input side, derive the unique required output operator, and assess its
support before attempting a deeper search.

## A two-sided uncertainty bound that permits nonunit coefficients

For n address bits, use the normalized orthogonal Pauli operator basis
`W(p,q)=X_p*Z_q`. The coefficients may be arbitrary complex numbers; the
operator being expanded need not be unitary. Let F be the full C tensor,
and let A be the tensor of f independent line kernels C_U. The translation
directions are independent because they occupy separate columns.

Conjugation by F permutes the Pauli basis, with fourth-root unit factors.
For one bit, `X->X` and `Z->-i*XZ`, so its exact coefficient action is
`(p,q)->(p xor q,q)` with multiplier `(-i)^wt(q)`.
The right multiplication by A expands each Pauli into exactly `2^f`
distinct Paulis with coefficient magnitude `2^(-f/2)`. It is a unitary
linear map on normalized Hilbert-Schmidt coefficients: right multiplication
by the unitary A preserves that norm. Consequently the coefficient map

```text
X -> Y = F*X*A*F^-1
```

is unitary and has maximum entry magnitude `2^(-f/2)`. If X is nonzero,
Cauchy-Schwarz gives

```text
||y||_infinity <= 2^(-f/2)*sqrt(s_X)*||x||_2,
||y||_2 <= sqrt(s_Y)*||y||_infinity,
s_X*s_Y >= 2^f.
```

Here s denotes the number of nonzero Pauli coefficients. No condition-number
assumption is used, and cancellation or nonunit coefficients do not alter
the inequality.

For the decoded physical core P0 and full target Q, a complete boundary
would satisfy `B_out*P0*B_in=Q`. Its source-column block equation is
`F*X=Y*(F*A^-1)`, where X is a block of `B_in^-1` and Y the corresponding
block of B_out. Thus Y has exactly the coefficient map above. Invertibility
ensures that each source column has a nonzero such block. A boundary whose
inverse-input and output blocks have Pauli support at most S_in and S_out
must obey `S_in*S_out>=2^f`.

If every factor has at most s Pauli terms per bank block, multiplication
can grow a block support by at most W*s per factor. This yields a linear
depth requirement for that bounded-Pauli model. Actual inverse factors
must be included; a sparse forward matrix does not guarantee a sparse
inverse. General affine address permutations, quadratic phase gauges and
arbitrary address-dependent coefficients are outside the model unless
their complete Pauli support is charged. This is an operator-basis support
statement, distinct from physical coordinate support or fixed-tape time.

## A compact amplitude escapes the small-Pauli model

For even f, define a cross-column quadratic Boolean function

```text
q(a) = sum_j a_(2j)*a_(2j+1) mod2,
g(a) = 5/4+(3/4)*(-1)^q(a).
```

The invertible diagonal gate G_q has values 2 and 1/2, inverse values 1/2
and 2, and exact singular condition number four. Its inverse rule is
`5/4-(3/4)*(-1)^q(a)`. A single pair has normalized Walsh coefficients
`(1/2)*(-1)^(z0*z1)`; multiplying the independent pair sums gives
`2^(-f/2)*(-1)^q(z)`. Therefore

```text
g_hat(z) = (5/4)*[z=0]+(3/4)*2^(-f/2)*(-1)^q(z).
```

All `2^f` coefficients are nonzero, as are those of the inverse. The
diagonal amplitude is Gaussian dyadic with a compact address rule but
exponential Pauli support. This refutes any attempt to equate one native
address rule with constant Pauli support. It does not evade the earlier
post-only physical coordinate support bound.

The cross terms here involve distinct selected columns. They cannot be
silently treated as a fixed single-column scalar or a tensor of independent
one-column controls. All f bits and f/2 products are explicit in the tests.
An actual tape compiler must charge their metadata, the complete counter
and control state, every conditional field scale and its common grid.

## Exact pre/post operator models and outcome

To keep the first f=2/4 test small, use the six-bank active quotient model

```text
P0 = diag(I,I,C_f,C_f,C_f,C_f),       Q = diag(C_f,...,C_f).
```

This treats the two source banks as missing the same active line tensor.
It is a separate preflight model. It does not identify the distinct source
labels 1 and 7 in the actual h4 joint component. A positive factorization
here would require a new distinct-label physical audit.

Each of two named input words has two nonunit scalar bank-mixing layers,
two address-amplitude layers and an intermediate bank-dependent affine
address route. All scalar shears are expanded into signed unit additions.
Each S block has a Frobenius norm bound giving condition at most 15; each
amplitude layer has condition four. The whole input word has condition at
most `15^2*4^2=3600`, uniformly in f. This is a bound for these specific
prewords, not for a discovered complete boundary family.

For each preword B, derive the unique required postoperator
`R=Q*B^-1*P0^-1`. R has the same singular condition number as B because
the factors Q and P0 are unitary. Exact Gaussian-dyadic matrices compare
every coefficient of `R*P0*B=Q`, including all six arbitrary input banks.
The derived dense R is not presented as a native word.

| Columns f | Layout | Exact target coefficients | Pre prefix grid | Pre prefix component L1 | Inverse prefix component L1 | Required post row/column support |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 0 | 576 | 2 bits | 61 | 52 | 16 |
| 2 | 1 | 576 | 2 bits | 99/2 | 72 | 16 |
| 4 | 0 | 9,216 | 2 bits | 64 | 64 | 64 |
| 4 | 1 | 9,216 | 2 bits | 99/2 | 80 | 64 |

The inverse prewords also need at most two grid bits. Every required post
support graph is one connected component on all 24 or 96 coordinates.
It therefore cannot be one six-wide mixing layer even with arbitrary
input/output coordinate routing. The maximum row and column supports also
force at least two post layers at f2 and three at f4, since `6^T` bounds
support after T such layers. These are necessary conditions for the named
prewords; the experiments neither find nor exclude deeper post words.

Four workers finished all cases in at most 1.339 seconds per case. They
compared 19,584 complete target coefficients and separately bound each
preword's exact forward/inverse fields. Omitting the nonlinear amplitude
gates fails the complete operator. Each case also checks the exact bent
spectrum, inverse amplitude and Pauli uncertainty against literal matrix
operations; tensor equality witnesses have support pairs `(2^r,2^(f-r))`.
Six seeded nonunit Gaussian-dyadic coefficient samples per f give additional
cancellation controls. These samples support the implementation, not an
exhaustive circuit search or an all-size proof by experiment.

## Time, metadata and precision obligations

The finite preword coefficients have exact common-grid and component-L1
prefix bounds above. These do not bound an unspecified implementation of R.
Any eventual native post word must supply its own complete prefixes,
temporary registers, field copies and arbitrary dirty restoration.

Each preword declares 18 signed unit bank additions, 12 amplitude bank
operations and six address routes. A scale by two or one-half has a real
one-bit magnitude or grid cost; the inverse and both real/imaginary fields
remain paid. Per-record metadata must retain all selected bits needed by
q and the explicit affine routing columns. No coefficient is raised to
the number of payload fields, and no grid normalization is free.

If an actual boundary used O(log f) complete materialized passes, its
`O(V*log(f))` scans would fit the retained positive-power local overhead
for fixed native constants. This is only a sensitivity observation.
Computing q, enumerating records, restoring routing controls, maintaining
full long chunks and performing every copy could add other costs. The
[routing-aware transfer](../transfers/routing-aware-depth-transfer.md)
and [endpoint-aware guard](../transfers/endpoint-aware-guards.md) must be
bound to that complete program before using a complex moment. The current
input words plus an unspecified dense R do not meet that interface.

## Persistence, reproduction and next discriminator

The standalone [producer](../../code/synthesis/nonunit_address_amplitude_preflight.py)
is standard-library Python and imports no other track's source. The
[completed run](../../runs/20261009T033016Z-synthesis-nonunit-amplitude-preflight/)
retains the full compact protocol/certificate and matrix hashes. The
original ignored output is
`work/synthesis/20261009T032958Z-nonunit-amplitude-preflight/results`.
Its namespace was selected from the clock immediately before launch;
the actual protocol start is `2026-10-09T03:30:16.001171+00:00`, 18 seconds
later. The durable run uses the actual start time. No original is replaced.
The only source SHA-256 is
`b1ddb07507be5b093ae88bc16364c3284f8db14366f57fa9916e96b17ed5a50a`.

From the breakthrough worktree root, choose a fresh output:

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/nonunit_address_amplitude_preflight.py \
  --workers 2 \
  --output research/integer-mult-breakthrough/work/ci/<fresh-id>-amplitude-preflight/results
```

The next useful search should optimize true pre/post words jointly and
retain their complete Gaussian operators. Merely making a Pauli expansion
large or deriving an algebraically correct dense postmatrix is insufficient.
A promising candidate must factor R into actual native layers, pay their
cross-column metadata and field scans, and then survive the original
distinct-label h4 component's whole-operator audit.

## All-size obstruction for the retained unique-path topology

There is a stronger explanation for these particular negatives. Their
preword is `B=M2*D2*P*M1*D1`, with two constant bank matchings M1/M2,
invertible diagonal address amplitudes D1/D2, and per-bank routed monomials
P. Thus

```text
(B^-1)_ij = sum_k D1_i^-1*(M1^-1)_ik*P_k^-1*D2_k^-1*(M2^-1)_kj.
```

The two matchings share no pair. For every i,j there is at most one
intermediate k with both scalar factors nonzero. Each nonzero block is
therefore a single weighted address monomial, with no internal interference.
For a source bank j, `P0_j=I`, so the required post block is
`R_ij=C_f*(B^-1)_ij`. Every C_f coefficient is nonzero, and multiplication
by an invertible weighted monomial only permutes/rescales its columns.
Hence each such R block is completely dense.

Every output bank reaches at least one source bank; two of the six output
bank rows reach both source banks. The required post has maximum coordinate
support at least `2*2^f`, for arbitrary even f, arbitrary nonzero address
amplitudes and arbitrary bijective per-bank routes under this topology.
An implementation by six-wide coordinate mixing layers therefore requires
`T>=log_6(2*2^f)`. This is an all-size conditional topology result, rather
than an extrapolation of the measured support 16/64.

The independent standard-library
[path verifier](../../code/synthesis/single_route_prepost_obstruction.py)
reads the completed certificate as immutable data, reconstructs both
inverse bank matrices from the signed unit shears, and verifies all 32
bounded source-block paths. Repeating the same matching creates multiple
routes per bank block and is rejected as outside the premise. That negative
control is a failed proof premise, not a demonstrated faster circuit.
Its [completed run](../../runs/20261009T033817Z-synthesis-single-route-obstruction/)
pins the input bytes and source closure separately from the producer.

This result suggests a concrete change: multiple paths must meet inside
the same source bank block if the input boundary is to cancel the dense
response. Streaming scans or reductions have many such paths and are also
outside the bounded-coordinate-layer model. They require their own complete
layout, buffers, numeric guards and exact pre/post operator audit.
