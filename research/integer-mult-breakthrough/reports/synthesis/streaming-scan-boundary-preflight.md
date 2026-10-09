# Streaming scan boundaries: full operator and literal precision preflight

Status: **EXACT FINITE OPERATOR AND REGISTER CONTROLS**, with a separate
**CONDITIONAL CONTIGUOUS-RECORD SCAN COST**. No fast canonical repair or new
multiplication exponent is supplied.

## Changed mechanism and exact model

A prefix scan `y_a=sum_(b<=a) x_b` mixes an entire address range in one
record pass. Its inverse is the saved-original difference
`x_a=y_a-y_(a-1)`. Both are nonunit. This is a genuine escape from the
bounded-coordinate-fan-in models in the
[earlier boundary result](address-dependent-boundary-obstructions.md):
exponential row support does not by itself require many tape passes.

The first test retains the common missing-line quotient
`P0=diag(I,I,C_f,C_f,C_f,C_f)`, with full target
`Q=diag(C_f,...,C_f)` on six arbitrary input banks. It does not identify
the distinct labels 1 and 7 of the actual h4 joint component. A useful
positive here would still require that original component's physical audit.

Two fixed preprocessors combine scans and differences, repeated bank
matchings, nonlinear amplitudes and cyclic address routes. Layout one also
uses explicit per-bank address reversal. Repeating the first matching
creates multiple paths in a source bank block, lifting the
[unique-path restriction](nonunit-address-amplitude-preflight.md).
For each B, the unique required postoperator is `R=Q*B^-1*P0^-1`.

Every coefficient of `R*P0*B=Q` is compared exactly over Gaussian dyadics.
This includes all six physical inputs and the two dirty carrier banks.
The derived dense R is not a supplied native word.

## Finite outcome

| Columns | Layout | Complete target coefficients | Input prefix grid | Input prefix component L1 | Inverse prefix component L1 | Post lower-cut rank lower bound |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 0 | 576 | 1 bit | 689/2 | 372 | 10 |
| 2 | 1 | 576 | 1 bit | 769/2 | 349 | 12 |
| 4 | 0 | 9,216 | 1 bit | 4085/2 | 2103 | 34 |
| 4 | 1 | 9,216 | 1 bit | 1459 | 1404 | 35 |

Four workers passed all four cases, at most 1.820 seconds per case. The
post's maximum row/column support is 16 at f2 and 64 at f4, but coordinate
support is not an exclusion of a streaming implementation. At f4/layout0,
eight rows have support 62, two have 63 and 86 have 64; the small cancellations
are retained rather than rounded away. No compact post factorization was
found or asserted.

The cut certificates reduce exact Gaussian-dyadic entries modulo three into
`F3[i]/(i^2+1)`. This is a field: -1 is not a square in F3. A nonzero minor
there proves a nonzero characteristic-zero minor, so the displayed ranks
are exact lower bounds, not claims that the modular rank is always the
full rational rank. On the same address-midpoint cut, the target rank is
exactly `3*2^f` and the provided core rank exactly `2*2^f`, independently
from their tensor block structure.

These ranks concern the declared address ordering. Large-stride buffers,
global permutations, reversal gauges and another layout can evade a
limited-state scan model. The rank result is not a universal streaming
lower bound. The finite tests retain the reversal layout explicitly.

## Complete records and scan buffers

The record simulator checks three Gaussian fields, hence six real/imaginary
components, in every record. It compares the field word with its full
matrix and restores all fields under the true inverse. A separate scan
uses the current original record and a saved previous record:

```text
prefix:     output = original+previous_sum; previous_sum = output,
difference: output = original-previous_original; previous_original = original.
```

Two complete record buffers suffice for this standalone contiguous pass.
The simulator accounts for every record read/written and clears the
temporary buffer. These are ordinary native-machine temporary registers,
not free additional recursive Gaussian row streams. This finite simulation
is not a bit-level Turing-machine program or a native integration theorem.

For a common fixed format, the finite codec stores three bank bits, f
address bits, an eight-bit grid descriptor and all six signed components.
Input-word records use a common three-bit fractional grid. The declared
magnitude allowance is 42 bits at f2 and 44 at f4 in both layouts.
The corresponding full records have 289 and 303 bits. No field, tag,
grid component or spectator is deleted. Cyclic routes have fixed offsets
of magnitude at most six, and reversal is an explicit permutation.

The standalone scan's conditional traffic bound is O(V) for a contiguous
complete-record stream of volume V and a fixed number of fields. Each
record performs a bounded number of full-field reads, additions, buffer
copies and writes. A prefix adds at most f magnitude bits over `2^f`
records; the inverse difference adds at most one. Temporary numerator/carry
space must be paid as well. Each buffer holds a complete guarded record.

This does not certify the full preprocessing word in the original layout.
Bank interleaving, counter/control compilation, cyclic/reversal routing,
all f cross-column bits of the amplitude rule, field allocation and return
must be implemented on the actual fixed tapes. The scan uses blank ordinary
machine workspace and permits erasure there; the six logical input banks
remain arbitrary throughout. It does not claim a reversible dirty-register
identity for that low-level workspace.

## Literal common-grid and dense repair audit

The separate [integer audit](../../code/synthesis/audit_streaming_scan_precision.py)
keeps one physical dyadic grid through the complete finite pipeline. It
executes all scalar shears, scans, amplitudes and C numerators on integers,
observes every signed numerator prefix, and rejects an inexact division.
It then realizes R by explicitly multiplying and summing its nonzero
coefficients. This is a deliberately dense negative cost control.

| Columns | Layout | Fixed grid bits | Peak signed register width | Post coefficient grid | Dense post nonzero coefficients | Integer coefficient products |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 0 | 8 | 25 | 3 | 384 | 4,608 |
| 2 | 1 | 8 | 24 | 3 | 384 | 4,608 |
| 4 | 0 | 12 | 32 | 5 | 6,126 | 73,512 |
| 4 | 1 | 12 | 32 | 5 | 6,144 | 73,728 |

All three Gaussian fields in every physical record return the exact full
target. The fixed grid is retained; the endpoint's zero trailing bits are
not a free normalization. Coefficient products and numerator temporaries
are counted before their exact divisions. Undercharging the global grid
to the incoming two-bit field format is rejected by a physical division.

Four workers passed the repaired audit in at most 0.806 seconds per case.
Its 156,456 integer coefficient products and 1,440 final real/imaginary
component comparisons are finite receipts, not an all-size time proof.
The naive dense repair's work must be paid from its actual coefficients,
including their generation, multiplication and record movement. Its dense
matrix identity supplies no sublinear native supplier.

The initial audit passed the same arithmetic but its `asymptotic_scope`
annotation incorrectly described the maximum support as every row's
support. The [fresh interpretation repair](../../runs/20261009T040121Z-synthesis-streaming-scan-precision-repair/)
changes that annotation only. The original source/evidence is unchanged,
and the [recovery patch](../../code/synthesis/patches/streaming-density-scope-repair.patch)
reconstructs its exact source. No all-f density extrapolation is made.

## Reproduction and remaining leverage

The [operator producer](../../code/synthesis/streaming_scan_boundary_preflight.py)
uses the read-only
[amplitude arithmetic](../../code/synthesis/nonunit_address_amplitude_preflight.py).
The [operator run](../../runs/20261009T035303Z-synthesis-streaming-scan-preflight/)
and [initial integer run](../../runs/20261009T040006Z-synthesis-streaming-scan-precision-attempt/)
pin actual starts, immutable raw hashes, effective source closures and the
namespace differences. The repair run separately pins its final source.
All code is standard-library Python.

From the breakthrough worktree root, use fresh outputs:

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/streaming_scan_boundary_preflight.py \
  --workers 2 --output research/integer-mult-breakthrough/work/ci/<fresh>-scan/results
python3 -B research/integer-mult-breakthrough/code/synthesis/audit_streaming_scan_precision.py \
  --workers 2 --output research/integer-mult-breakthrough/work/ci/<fresh>-scan-grid/results
```

The source APIs are `probe((f,layout))`, `word(f,layout)` and
`apply_word(matrix,events,f,left=True,inverse=False,monitor=False)`.
The literal audit exposes `pipeline(original,events,required,f,grid)`.
Each default main covers f2/f4 and both layouts; the operator closure is
two source files and the literal audit closure three.

The next useful search should characterize cheap streaming intertwiner
spaces or find an executable post factorization. A matrix that is correct
but dense is an exact control, not the desired mechanism. Prefix scans,
reductions, broadcasts and large structured temporary states must be tested
with their own complete volume, layout and guard bills; they remain outside
the earlier bounded-fan-in exclusions.
