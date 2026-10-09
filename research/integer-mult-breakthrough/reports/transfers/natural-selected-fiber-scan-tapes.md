# Natural selected-fiber scans with complete interleaved records

Status: **EXACT FINITE TAPE EVIDENCE AND AN ALL-SIZE ORDINARY-SCRATCH
COMPONENT UNDER THE STATED RECORD-WIDTH CONTRACT**. A prefix scan in the
natural selected-bit order can run in linear complete payload volume even
when selected bits are separated by arbitrary spectator bits. It needs a
complete accumulator table, a paid magnitude reserve, and ordinary blank
machine scratch. This is a total-order prefix/difference component. It
does not supply a subset-zeta transform or the high-flux zigzag order.

## Input and endpoint

Take a complete local binary address cube with n bits, in ordinary numeric
order. Let S={s_0<...<s_(f-1)} be its selected positions. All other bits
are spectators, including every K-1 unselected plane of a K-bit chunk.
An arbitrary positive stock P of old rows precedes that local cube.
Every physical address carries the same complete polynomial record with r
Gaussian coefficients, common fractional grid 2^-p and enough signed integer
bits. Neither r nor n creates another machine tape. Four-coefficient and
long-polynomial controls are separate literal implementations.

For a fixed old row and fixed spectator values, order the 2^f selected
labels a by their ordinary binary value. The forward endpoint is

    y[g,a] = sum_(b<=a) x[g,b].

The inverse endpoint is x[g,0]=y[g,0] and
x[g,a]=y[g,a]-y[g,a-1] for a>0. Every original physical record position,
coefficient position, grid and spectator bit stays in place. Address
labels may remain implicit. The consumer reads no numeric address header.
Finite tests with explicit headers additionally retain every header bit.

The procedure uses seven tapes: immutable input, immutable selected mask,
complete accumulator table, output, local binary counter, unary count of
selected-one bits, and backward countdown. The table has exactly
P*2^(n-f) complete records, a fraction 2^-f of the input record volume.
Input and output remain full-volume streams. All ordinary work tapes are
erased, and the input remains immutable. Erasing ordinary native scratch is
charged; this is not arbitrary-dirty reversible circuit scratch.

## Why natural physical order suffices

Let g(t) be the integer obtained by compressing the unselected bits of
t, preserving their bit order. At fixed g, the selected index increases
while the complete input is scanned in natural physical order. Thus the
correct accumulator for each input record is the table row g(t), with
the old-row number preceding that index. No gathering of selected fibers
or a free transpose is involved.

When t increases by one, a carry at an unselected bit changes g by +1.
A carry at s_j changes g by

    -(2^(s_j-j)-1).

There are 2^(n-s_j-1) such selected carries in one complete cube. The
total backward row displacement within P cubes is therefore

    N_minus = P sum_j 2^(n-s_j-1) (2^(s_j-j)-1)
            = P sum_j [2^(n-j-1)-2^(n-s_j-1)]
            < P*2^n = M.

The initial table row is zero and the final row is P*2^(n-f)-1. The sum
of absolute row displacements is

    P*2^(n-f)-1 + 2*N_minus < 3*M.

Every table displacement traverses a complete record of its actual width.
The table is not a constant-size scalar register. Initialization, rewinding
the input, table updates, return to each current row, final table rewind,
and table erasure add O(MR) movement. The finite programs check a conservative
table head-movement bound of 12 times their actual input symbol volume.

## Literal counters and the metadata bill

The counter is stored least-significant bit first. Its head and an aligned
immutable mask head walk through the trailing ones, flip those bits to
zero, then flip the carry bit to one and return to their marked starts.
Each selected flip moves a separate unary selected-one cursor by one cell.
The cursor is at its start marker exactly when all selected bits are zero.
This tests that condition in constant time per record.

One initial input pass emits a full zero accumulator record precisely at
selected index zero. It visits every payload bit and emits the complete
headers and polynomial-field framing required by the table. This constructs
its correct size and row order without computing a free numeric key or
initializing a table by an uncharged numeric power.

While the carry walks through lower bits, each unselected trailing-one bit
appends one literal one to the countdown. For a selected carry with a such
bits, this is the a-bit word of value 2^a-1. Repeated real binary decrements
move the table backward by one complete row each. The borrow head returns
after every decrement; underflow is detected by reaching the end marker.
The countdown is then erased. An unselected carry discards this short
countdown and moves the table forward by one row. Local cube overflow moves
forward to the next old row if one remains.

Across one complete cube, the sum of trailing-one counts is 2^n-1.
Across P cubes it is M-P. Initializing the mask/counter/unary cursor costs
O(n). Both the initial table pass and the arithmetic pass consequently pay
O(M+n) carry/mask/cursor steps, including all returns and local resets.
The countdown runs pay O(N_minus+M+n): binary borrow visits over L consecutive
decrements cost O(L+a), and their initialization lengths a were already
charged to the carry walks. This uses the same finite-counter principle as
the pinned elementary stream contract, with explicit payload-head motion.

A conservative operation count for the implemented control is at most
111M+24n+64 counter/mask/unary/countdown read, write and unit-head steps,
and hence at most 128(M+n+1). It includes both passes and scratch erasure.
The finite tests enforce the latter bound. The all-size proof uses the
carry and countdown sums; it is not extrapolation from a numeric countdown.
There is no per-record O(n) mask scan hidden outside the volume bill.
Post-execution storage comparisons and reference decoders are verification
monitors. Their Python indexing is not claimed as part of the native
consumer. The actual erase, arithmetic and head returns use only tape
reads, writes and unit moves and are included in its counters.

## Signed arithmetic and full record width

For each component, the consumer uses a finite-state bit-serial adder.
The forward scan adds the current signed component to its old table value,
writes that sum to the table and output, and checks signed overflow. The
inverse subtracts the saved previous input value, writes the current input
to the table, and outputs the difference. Each signed component word is
read and written in full. The long-record implementation repeats until the
record boundary, rather than allocating one tape or finite state per
coefficient. No component is interpreted as a Python integer in the consumer.

If each true input component has absolute value at most B, a forward
intermediate has magnitude at most 2^f B. An inverse on arbitrary inputs
bounded by B has magnitude at most 2B. The uniform forward/inverse format
can reserve f+O(1) extra integer/sign bits. No fractional-grid increment is
needed: additions and differences preserve the common Gaussian-dyadic grid.
All-one controls attain the 2^f growth. An input-only signed format raises
the explicitly retained overflow negative. Fixed-width modular wrap would
be a different endpoint, and is not substituted here.

The initial [four-field literal source](../../code/transfers/selected_fiber_scan_tapes.py)
has eight fixed real/imaginary words. The
[complete polynomial extension](../../code/transfers/selected_polynomial_scan_tapes.py)
reads any common number of Gaussian coefficient words until the marker.
The [implicit-address adapter](../../code/transfers/verify_selected_scan_native_records.py)
retains no per-record address header, matching the primary stream convention.
Fixed delimiters and their removal require a charged O(MR) framing scan.
Initializing and resetting a binary word-length counter is O(w) per w-bit
word, so framing a polynomial costs O(rw), including all its returns.
The source adapter tests the already-framed representation; it does not
claim to be a compiler for the original binary descriptor syntax.

## Compatibility with the pinned native family

The original `05-layers.tex` at openai/math revision
adc7f1241b42e322a6451854ab7e4b4c146bf78a has SHA256
20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594.
It explicitly uses r complex coefficients per record with common component
width w=Theta(p), logical record payload R=2rw, and

    d=Theta(p^epsilon), 0<epsilon<1,
    K=floor(d^c), e<=d, f<=e,
    r=2^Theta(p/d).

K is an address chunk width, not the coefficient's numerator width. Adding
the prefix magnitude reserve gives

    R_scan = 2r [w+f+O(1)],
    R_scan/R = 1+O(f/p) = 1+o(1).

Complete delimiters contribute O(r) symbols. Optional explicit A-bit address
headers add O(MA) setup, movement and removal; here A=O(dK)=O(p) and the
long record dominates that work. The implicit-address adapter avoids those
headers altogether. This compatibility is conditional on the actual
Theta(p) component width and bounded input domain. An alternative format
whose component width is only K would incur the real factor 1+f/K. For
K=d^c, f=Theta(d) and c<1, it can grow polynomially. Floating exponent fields
alone do not certify cancellation precision or the exact signed-grid word.

The pinned original `02-streams.tex` has SHA256
606c80db61cad13aa0c3b6060dc4b88dbbe7ac60cdd831aa93f28d908fd09dab.
Its complete stream, fixed tape and linear counter semantics are compatible
with this standalone procedure. Native descriptor preparation and an actual
surrounding algorithm must still provide that component width, initial
magnitude/grid domain and the complete input/output record shape.
The old unitary C network's guard proof does not automatically become a
guard theorem for a new nonunit Z/scan network. Recursive ancestor magnitude,
denominator and outer recovery obligations remain separate.

## Finite evidence and limits

The first four-worker attempt, actual start
2026-10-09T10:48:36.123965+00:00, is
`20261009T104836Z-transfer-selected-scan-first`. It passes six shapes with
1,648 complete records and 13,184 signed component values, including no
selected bits, all selected bits, non-power-of-two old-row stock and
interleaved holes. Every complete four-Gaussian-field record and literal
inverse returns exactly. Independent numerical reference checks bind all
510 selected masks at n=1 through 8 to the carry identity. Those numerical
reference checks are distinguished from the literal tape execution.

The full polynomial attempt, actual start
2026-10-09T10:54:29.652630+00:00, is
`20261009T105429Z-transfer-polynomial-selected-scan-first`. Four workers
pass r=1,3,16,64, common p=16,32,64,24, with 416 complete records and
19,392 signed component values. Complete coefficient order, arbitrary signed
Gaussian fields, immutable input, full inverse and ordinary scratch erasure
are retained. Bounded commands exercise each effective source closure.

The implicit-address attempt is
`20261009T105859Z-transfer-native-selected-scan-first`, actual start
2026-10-09T10:58:59.373241+00:00. It passes r=5,17,65,9 with no numeric
per-record address header. Its entire complete input and true inverse are
compared as finite-symbol streams. Three bounded attempts at 11:02:58 UTC
cover the fixed-four-field, variable-polynomial and implicit-address APIs.
Original source and protocol bytes remain unchanged in all six attempts.

The natural total-order prefix is not the subset incidence Z_f: for f>=2,
the column at selected label one reaches label two in a prefix and does not
in Z_f. A separate exact negative retains that distinction. High-flux
zigzag even-address ascending/odd-address descending scans require a
different complement-synchronization route in the interleaved layout.
This component does not price that route, supply a whole subset-zeta
transform, improve the inherited XOR exchange exponent, or imply kappa.

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/selected_fiber_scan_tapes.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/selected_polynomial_scan_tapes.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/verify_selected_scan_native_records.py --workers 1 --bounded
```

The report and programs were developed with AI assistance. The new component
is the amortized natural-order accumulator traversal. Counter principles and
the record/width conventions are credited to the immutable original stream
and layer contracts. No external checkout was executed or changed.
