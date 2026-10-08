# Full bounded Gaussian, CRT and integer recovery pipeline

## Question and scope

Can the complete proposed arithmetic interface compose with the correct
normalizations and cyclic signs, before replacing its dense Gaussian reference
passes by the conditional fast localized producers? Separate successful cell,
FFT or CRT controls do not answer this question.

The executable `code/check_full_gaussian_integer_pipeline.py` now performs the
entire bounded composition. All online numbers are signed integer pairs on a
single dyadic grid. Matrix and phase setup uses pinned mpmath 1.3.0 at a precision
strictly above the work grid. Actual pointwise polynomial multiplication uses
four signed Kronecker integer products, centered exact coefficient extraction,
and reduction modulo `y^r+1`. No floating-point FFT or direct integer product is
substituted for this producer. Direct integer multiplication is an independent
final oracle.

This is a finite arithmetic discriminator. Its Gaussian matrix passes are
explicitly charged dense references, and its finite CRT array arrangement is
a reference execution of the exact map. It does not prove the fast fixed-tape
layout theorem or the eventual row-bank stock conditions. The movement ledger
records actual reference coefficient products, payload reads and writes,
synthetic butterflies, twists and child integer-product sizes. These costs
must not be attributed to the fast algorithm.

## Producer and independent checks

1. Generate two nonnegative radix digit arrays from a pinned seed. Scale digits
   by `2^(-B-2)`, so their magnitudes are below one quarter.
2. Apply the balanced CRT tree exactly and verify every address against the
   independent prefix-product formula `b_i=P_i^(-1) k mod s_i`, where
   `P_i=product_{j<i}s_j`. Verify the inverse tree on the complete source cube.
   This normalization differs from the conventional full-cofactor CRT basis.
3. Construct periodic Gaussian `A=S/2` and `B0=D N^(-1) C/2^(2u-1)` matrices,
   with `u=alpha^2`. Selectors use the true nearest integer to `t*j/s`.
   Period-image counts grow with the declared setup precision.
4. Expand each source axis, apply the exact target frequency permutation via
   the chirp identity, and compress each axis. Scale once by `2^gamma`, where
   `gamma=2 sum_i alpha_i^2`. A separate direct source DFT evaluates every
   frequency in the initial small cases; larger cases explicitly list the
   selected independent probe frequencies.
5. Implement the chirp's normalized tensor cyclic convolution in the
   distinguished suffix ring. Both forward operand transforms are normalized,
   the pointwise ring product divides by `r`, and the normalized opposite
   transforms are followed by the main-volume scale. Coefficient twists are
   `exp(pi*i*k/r)` and their conjugates.
6. Multiply the two source Fourier outputs pointwise and use the opposite
   complete Gaussian transform. Multiply the result by
   `S^2 * 2^(2B+4)`, undo CRT, and round the recovered integer coefficients.
   Compare every coefficient with an independently computed ordinary or cyclic
   convolution. Carrying the ordinary coefficients reproduces the independent
   Python integer product exactly.

The prefix CRT tree uses only an additive group isomorphism. Its output basis
is not changed after the tree. An initial independent oracle mistakenly used
full-cofactor normalization; the checker rejected this immediately. The
retained negative records the difference `(1,3)` versus `(3,3)` for input one
at source shape `(7,5)`. The correction changes the oracle, with no additional
unpaid modular scaling in the proposed physical program.

## Completed evidence at 14:48 UTC

Four ordinary products at source shapes `(7,5)`, `(7,13)`, `(7,5,13)` and
`(13,11,29)` have target volumes 64, 128, 1024 and 8192. Every source coefficient
is recovered correctly. Maximum absolute real coefficient errors are
`2.55e-66`, `1.91e-59`, `6.95e-72` and `2.58e-57` at 256 or 320 fractional bits.
The four-case batch takes 14.66 seconds on two single-thread workers on this
host. These are bounded setup and reference-producer measurements, not
asymptotic multiplication benchmarks.

Four changed cyclic-cut cases put one input coefficient at scalar `S-1` and
the other at one. Their actual complete pipelines recover the coefficient at
zero, with errors below `2.22e-58`. Their recovered radix values equal the
integer products modulo `radix^S-1` and differ from the ordinary integer
products, as required. A separate actual synthetic convolution repeats the
suffix wrap with the twist removed: the wrapped coefficient is negative.
The correct twisted producer returns its positive cyclic coefficient. Omitting
one of the two required source-volume factors also changes recovered
coefficients in every case.

The two initial four-case receipts check 4,728 source coefficients each and
9,456 CRT input addresses each. Their complete inputs, grid precisions, source
hashes, setup radii, residuals and measured movement ledgers are retained.
Larger full-pipeline cases are running with target volumes up to 524,288 and
384--512 bit grids. Larger direct Fourier controls use specified frequencies,
while their final integer coefficient oracle still covers the complete cube.

## Separate source-transform setup sensitivity

The preliminary one-dimensional composition also passes changed source/target
families up to `251/256`, with complete target matrices and independent source
DFT probes. A first attempt used only period images -1, 0 and 1. At source 7,
target 8 and alpha 2 this left error `6.75e-23`, above its requested `1e-60`
target. This is retained as a setup-tail negative. The repaired producer uses
an image radius derived from alpha, source period and setup digits. Treating
the omitted images as negligible without a precision-dependent charge is
invalid. Further unequal-ratio cases include `251/1024` and `509/512`.

## Confidence and remaining work

The completed receipts give strong bounded evidence for the composite
normalization, CRT convention, cyclic boundary signs and coefficient recovery.
They do not certify the analytic kernel tails, exceptional packet selection,
dirty-control fast CRT execution, native bit-router contracts, terminating
recursive multiplier, or the all-size cutoff. The next implementation step
is to replace each charged dense Gaussian stage by the actual joint source
embedding, packed local kernels and sparse repairs, while keeping this
independent coefficient oracle and the same explicit movement ledger.
