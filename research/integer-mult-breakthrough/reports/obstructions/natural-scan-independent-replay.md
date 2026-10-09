# Independent complete-record replay of the natural selected scan

Status: **EXACT FINITE REPLAY AND INTERNAL ANALYTICAL REVIEW**. The unchanged
seven-tape polynomial consumer passes a separately written complete endpoint
reference on new masks, record lengths, guard stocks and signed grids. This
is an independently checked ordinary-scratch component. Its surrounding
native transform, arbitrary-dirty circuit implementation and multiplier
exponent remain open.

## Reference and execution

The coordinator's [replay source](../../code/obstructions/selected_scan_independent_replay.py)
imports only the immutable polynomial consumer and its elementary encoding.
It imports neither the author's reference, probe nor native-record verifier.
For every original address x, the expected output explicitly sums all y in
the same old row with the same spectator bits and selected submask no greater
than x's selected submask. This reference does not maintain the consumer's
table or use its carry paths. A separate parser checks every signed component
and the entire headerless output framing.

The actual consumer runs forward and backward. The backward output must
equal every original byte. Both runs must retain seven tapes, erase all
ordinary scratch, respect the complete accumulator movement bound 12V and
respect the metadata bound 128(M+n+1). V is the actual full input symbol
volume and M is the full physical record count. These are finite measured
controls; the following analysis supplies the scaling argument.

| Address bits | Selected positions | Old rows | Gaussian coefficients per record | Fractional bits | Signed width | Complete records | Signed values |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 0, 2, 4 | 3 | 7 | 8 | 14 | 96 | 1,344 |
| 7 | 2, 5 | 5 | 33 | 12 | 17 | 640 | 42,240 |
| 4 | 0, 1, 2, 3 | 1 | 4 | 4 | 11 | 16 | 128 |
| 6 | none | 2 | 11 | 9 | 12 | 128 | 2,816 |

All **880 records and 46,528 signed component values** pass. The full run
`20261009T111029Z-selected-scan-independent-replay` used four workers and
completed at 2026-10-09T11:10:32.240078+00:00. Its process wall time was
2.859 seconds; this is diagnostic, not a multiplication speed comparison.
The exact seeds and source hashes are retained with the run.

All-one first components attain the prefix magnitude growth. For three or
more selected bits, omitting the magnitude reserve causes a real signed
overflow and is rejected. A single global prefix that ignores spectators or
old-row boundaries disagrees in every applicable shape. The all-selected,
one-old-row shape intentionally has no such boundary discriminator. The
empty selected mask tests the identity endpoint, including multiple old rows.

## Analytical review of the actual consumer

Let s_j be the j-th selected bit, G=2^(n-f), and M=P*2^n. In natural input
order, every fixed spectator fiber encounters selected labels in increasing
order. A carry at an unselected bit moves its compressed spectator index
forward by one. A carry at s_j moves it backward by 2^(s_j-j)-1. Summing
these actual carries gives

    N_minus = P sum_j [2^(n-j-1)-2^(n-s_j-1)] < M,
    total table row travel = PG-1 + 2N_minus < 3M.

The full table contains PG records. Row motion traverses every coefficient
word; initialization, update, rewind and erasure therefore cost O(MR) for
the actual record width R. A physical carry at the end of each local cube
moves to the next old-row table block. Arbitrary guard values are retained.

The source implements the mask and binary-counter walk with unit tape
steps. Its unary selected-one cursor identifies selected index zero during
table initialization. Its countdown is a real binary word with charged
borrow, return, underflow and erasure operations. The sum of trailing-one
visits is M-P. Binary decrement visits amortize to the actual backward table
distance plus the already charged countdown initialization. Thus metadata
work is O(M+n); no per-record scan of all n bits is hidden in an address
lookup. Python integer fields and complete storage comparisons in the
verifier are monitors, not native instructions.

The polynomial consumer stops at the record delimiter, using a fixed tape
count for all coefficient lengths. Its inverse saves the previous input
component, not the previous reconstructed output. The full endpoint and
ordinary-scratch erasure agree with those source operations.

## Precision and remaining interfaces

For input magnitude B, a selected prefix reaches at most 2^f B. Reserving
f+O(1) integer/sign bits preserves its common fractional grid. Under the
pinned original native family w=Theta(p), f<=d=Theta(p^epsilon), epsilon<1,
the record inflation is 1+O(f/p)=1+o(1). K is an address chunk width and is
not substituted for w. A different w=K contract pays its actual 1+f/K
inflation. Full polynomial records, all guard coordinates and every
coefficient remain necessary.

The independently reviewed supplier is already-framed and uses ordinary
blank machine scratch. Framing from the original descriptor still needs
its charged linear implementation. An altered scan network still needs
global ancestor magnitude, denominator, normalization and recovery bounds.
The original unitary circuit's guard theorem does not prove them for this
nonunit scan. High-flux ordering and the subset-zeta transform are separate
operators. No all-size native zeta supplier or larger kappa follows from
this replay.

## Recovery and reproduction

The immutable consumer pins are
`selected_polynomial_scan_tapes.py` at
`0dcd1ada09c55f74b5001d14d4ffcf89a8ef0589363535f37758cd071fb385c6`
and `selected_fiber_scan_tapes.py` at
`5565695705b0525861a136dd0ef74e6e0b28802916f080cdc3df015b2ee62e7a`.
The complete runtime closure and seeds are in the
[replay configuration](../../configs/obstructions/selected-scan-independent-replay.json).
The author's [component report](../transfers/natural-selected-fiber-scan-tapes.md)
retains the original stream/layer source attribution.

From the repository root:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/selected_scan_independent_replay.py --workers 4 --output NEW_OUTPUT_DIRECTORY
python3 -B research/integer-mult-breakthrough/code/obstructions/selected_scan_independent_replay.py --workers 1 --bounded
```

The complete 1,470,225-byte original certificate contains all input and
expected endpoint fields. It is retained whole through the gzip publication
path. The separate readable summary omits only those two arrays per case,
records their original certificate hash and size, and preserves all literal
operation counters. No original is split, trimmed or overwritten. This is
internal agent review and finite replay, not external human peer review or
formal verification.
