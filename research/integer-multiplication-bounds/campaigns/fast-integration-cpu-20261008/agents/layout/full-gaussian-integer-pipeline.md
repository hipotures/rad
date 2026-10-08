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
The four larger ordinary cases are complete, with target volumes up to
524,288 and 320--512 bit grids. The largest source `(61,59,113)` recovers all
406,687 coefficients, with error `2.494e-50`. The batch takes 4,555.94 seconds;
these are reference implementation costs. Larger direct Fourier controls use
specified frequencies, while the final coefficient oracle covers the entire
cube. The retained larger receipt explicitly separates the source hash
imported at launch from the subsequently edited filename hashed at completion.

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

## Actual complete guarded CRT and packed forward replacements

The complete arithmetic reference has now been extended in two independent
ways. These receipts are materially stronger than isolated component checks.

- Source `(17,19,23)` at target `32^3` passes both actual guarded-CRT input
  programs, with 76 recorded events per program, followed by complete Gaussian,
  synthetic-ring and integer recovery. All 7,429 coefficients match the oracle;
  maximum real error is `6.17e-96`, and total wall time is 170.46 seconds.
- Source `(17,19,31)` additionally executes the actual reverse guarded-CRT
  program on the exact rounded leaf coefficients from the numerical producer.
  Its forward template compilation uses separate positive provenance labels
  and is explicitly charged. All 10,013 coefficients match; scalar padding is
  restored, no address bits are added, and error is `5.54e-68`. Total wall time
  is 159.66 seconds. API, compiler and guard sources were frozen before launch.
- Complete joint packed-forward controls cover target volumes 4,096, 16,384,
  65,536 and 262,144. They build real signed tensor products in mixed-radix
  cells, combine interiors from two global grids, and explicitly repair all
  unselected outputs. Every selected output differs from the independently
  rounded periodic Gaussian reference by at most one integer grid unit. The
  largest case computes 169,094 outputs by packed cells and repairs 93,050.
  These finite repair fractions are reported rather than identified with the
  all-size sparse-density bound.
- The actual packed-forward stage now replaces all three forward expansions
  inside an ordinary integer multiplier at source `(127,113)`, target `128^2`.
  All 14,351 coefficients recover correctly, with maximum error `2.12e-22`
  and 91.99 seconds wall time. Every expansion uses 2,355 genuine packed
  coefficients and 14,029 explicitly charged repairs. Compression remains a
  matrix reference. A changed larger whole-pipeline case continues running.

The actual CRT API preserves complete event and repair ledgers. Converting its
axis-zero-low binary cube to source lexicographic order pays one named axis
field permutation and one padding filter. Embedding the final rounded source
coefficients before reverse CRT pays the corresponding permutation and zero
insertion. No computed modular key is treated as a free coordinate-bit route.
The first CRT API helper was extended while its input-only run was active;
its immutable raw receipt hashed the filename at completion. The derived
publication records the exact reconstructed imported source hash separately
and preserves this provenance sensitivity. The later complete inverse run
freezes every dependency before execution.

A matched precision family fixes source `(31,29,61)`, target `(32,32,64)`,
alpha 5, digit bits, input seed and direct Fourier probes. Work grids 148 and
172 lose coefficient recovery completely. Grids 196, 197 and 198 have maximum
coefficient errors 2.73449, 1.39915 and 0.69896 and recover incorrect integers.
Grid 200 has error 0.17476 and passes the quarter-unit guard; grid 224 has error
`1.04e-8`. Grid 199 reaches correct rounding but fails the stronger quarter-unit
margin; only this affected guard attempt is rerun to collect its exact compact
statistics. Thus isolated transform accuracy is insufficient without charging
final source-volume and power-of-two amplification.

The largest original 3D L128 cell attempt was stopped after 1,524.51 CPU
seconds and roughly 2.71 GiB resident memory, before an accuracy receipt.
A changed GMP attempt was also checkpointed after 2,051.10 CPU seconds.
Static source review identified a full `side^dimension` Gaussian oracle sum
per output even though the independently generated input is exactly a sum of
two separable tensors. This was an avoidable oracle workload; the live phase
was not sampled, so it is not reported as an observed stack location.

The repaired oracle uses exact distributivity and cached independently
evaluated axis coefficients. A bounded comparison to the old dense oracle
passes, with identical packed products. The same full 3D L128 GMP input,
kernel and convolution then completes in 58.23 seconds with error `7.191e-132`,
262 reserve bits and 461 work bits. The reference's rank-two shortcut does
not reduce the actual packed tensor input or multiplication. The two stopped
attempts remain execution-budget observations, not numerical negatives.
GMP runtime is not a fixed-tape complexity certificate.

The larger physical guarded-CRT family at source `(29,31,37)` completes all
actual input programs and the final inverse program in 387.32 seconds, with
coefficient error `6.113e-67`. The matched digit-precision family confirms
that six-bit digits at work grid 199 recover integers but fail the required
quarter-unit margin (`0.348862`). Eight-bit digits at grid 200 lose 156
coefficients, while grid 208 passes with error `0.0108342`. Ten-bit digits at
grid 204 lose 157 coefficients, while grid 216 passes with error `0.00067018`.
Twelve-bit digits at grid 220 pass with error `0.00067909`. These are explicit
finite thresholds, not a replacement for the all-size error calculation.

Genuine packed inverse cells have also been checked against full cyclic
physical inverse solves; see [the inverse report](packed-laurent-inverse.md).
Their normalization is bare `N^-1`, so `J'=N^-1/2` and the outer `D'` factors
must still be supplied in the complete compression interface.

## Complete genuine forward and inverse cell composition

The producer `code/check_full_pipeline_packed_both.py` now replaces both
directions inside all three complete source transforms. Forward expansions
use actual paired-grid signed tensor products. Compression selects the
original nearest target rows, applies actual regular Laurent tensor inverse
products with the centered W factors, and supplies D' and the required
power-of-two normalization. Both source-period cuts and selector phase jumps
are excluded from regular cells. The local error screen includes the full
retained chirp reserve, tensor operator norm and output D' amplification.

Source `(251,241)`, target `256^2`, alpha4 and work grid192 passes all60,491
integer coefficient comparisons and the independent carried integer product
in432.00 seconds. Maximum coefficient error is `6.891e-25`. Every one of the
three compression stages contributes108 genuinely packed inverse outputs;
the rest are explicit charged repairs. The entire periodic dense repair
reference is computed and charged, so this is a correctness prototype rather
than an implementation benchmark for the asymptotic sparse repair lemma.

Completely dyadic input/output outer-factor inverse cells also pass target
768 and1024 bits at source periods65,513--131,071. Maximum global inverse
comparison errors are `2.617e-281` and `3.756e-346`, with186.37 and753.08 seconds
wall time. Their exact four-product core and all outer applications use frozen
dyadic words; arbitrary precision is used for setup and independent reference
coefficients. These finite parameters remain distinct from an all-size cutoff.

Changed work grids and digits also pass complete genuine forward/inverse
composition. At Q188, eight-bit digits and inverse radius4 the coefficient
error is `1.802e-22`; Q184, ten-bit digits and radius4 give `4.603e-20`.
The cyclic-cut Q192/radius5 control puts a source coefficient at S-1 and
another at one, and recovers the correct wrapped coefficient at scalar zero.
Each case checks every coefficient rather than a selected final subset.

The independent driver `code/check_full_packed_both_actual_crt.py` now
composes both actual physical CRT input programs and the actual final inverse
program with all three genuine packed forward/inverse source transforms.
Ordinary and cyclic-cut source `(251,241)`, target `256^2`, alpha4 and Q192
pass all60,491 coefficient comparisons and restore scalar zero padding.
Their real coefficient errors are `6.987e-25` and `4.969e-25`; wall times are
441.62 and433.26 seconds. The driver explicitly pays source/binary axis-field
conversion, padding filters and embedding before inverse CRT. A two-prime
tree has ordinary top maps, so these two controls do not claim execution of
multi-target F_u; the earlier three-prime complete controls establish that
separate changed interface.

The long-precision three-prime actual-CRT pipeline at source `(29,31,37)`,
target `(32,32,64)`, alpha16 and Q2048 also completes, with all33,263
coefficients correct and maximum real error `5.387e-141`. Its wall time is
4,309.36 seconds. Both u theta>=1 and u^2 theta>=Q hold on every axis,
and gamma1536<Q2048. Its Gaussian passes remain explicit dense references,
so this receipt addresses the large-precision/near-identity arithmetic
interface and is distinct from the genuine localized two-axis prototype.

A reordered-prime Q200 attempt has no eligible regular inverse cells under
its declared analytic precision screen; its failure is retained as a component
eligibility negative, not a coefficient failure or a claim about all-size
prime ordering. Matched lower work grids and changed layouts continue in
serial lanes. Pending runs are not described as completed evidence.

## Changed whole packed/actual-CRT work-grid discriminator

Matched inputs at source `(251,241)`, alpha4 and eight-bit digits distinguish
whole coefficient failures from successful cell tests. At Q112, the complete
producer loses142 integer coefficients, with real error13.6107 and maximum
integer difference14. Q128 passes every coefficient and the actual inverse
CRT with error0.000203746; Q144 passes with error`3.151e-9`. Their wall times
are309.14,318.28 and352.61 seconds. The failed coefficient producer correctly
returns before final actual CRT inversion. These measurements are retained as
matched finite precision evidence, not a uniform eventual precision theorem.

A reordered-prime cyclic-cut `(241,251)` control also passes actual CRT input
and output plus genuinely packed forward/inverse cells, taking439.24 seconds.
The full current layouts and kernel screens remain charged in its receipt.
Further short-halo and adjacent-grid cases are allowed to finish their current
children while obsolete queued continuations are withheld under the user's
new structural joint-frame priority.

Those current children completed normally. Q116 loses65 integer coefficients
with maximum real error0.8507303. Q117 rounds all60,491 coefficients correctly
but has error0.4247479, so it fails the declared quarter-unit guard. This
distinction prevents incidental nearest-integer success from being promoted
to the required recovery margin. Q118 and Q119 were withheld without running.

At Q128 the shorter radius2 full packed/physical-CRT pipeline passes with
error0.000203746 in312.58 seconds. Radius1 admits no eligible regular inverse
under its analytic screen and returns before any full coefficient comparison;
it is a kernel-eligibility negative. The corresponding Q144/radius2 queued
continuation was withheld. The historical steering receipt records that only
the queue coordinators were stopped; current scientific children were allowed
to finish. The user's new joint-frame directive supersedes the remaining
obsolete queue, while the already expensive strong-gap Gaussian control
continues in its reserved legacy lane.

That final legacy control has now completed normally. Source `(29,23,37)`,
target `(32,32,64)`, alpha18, Q3072, eight-bit digits, and97 input digits
recover all24,679 cyclic-ring coefficients and the independent1,552-bit
carried product. Both input CRT programs execute30 actual F_u calls and300
rotations, with76 events and zero new address bits; the final76-event reverse
CRT restores all scalar padding. Maximum real coefficient error is
`1.736854722573e-325`; the separately checked source-transform error is
`3.544282538707e-340`. Total wall time is8,724.87 seconds.

Every axis satisfies u theta>=1 and u^2 theta>=Q, and gamma1944<Q3072.
The deliberately omitted source normalization loses193 coefficients. The
Gaussian stages remain explicitly charged dense references, so this is
whole arithmetic/physical-CRT correctness evidence, not a timing certificate
for the localized tape algorithm. `configs/full-gaussian-strong-gap-source-manifest.json`
verifies that all five executed frozen source hashes equal their durable
producer, wrapper, and inverse API/dependency files. The complete receipt
and finished stage receipts are archived under `evidence/20261008T183500Z`.
