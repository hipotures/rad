# Fixed-tape tensor catalogue generation by growing prefix buffers

## Statement

Let axis j supply an explicitly generated catalogue of radix `r_j>=2`, with
one fixed-width P-bit real or complex coefficient per entry. Let
`V_j=product_{i<=j} r_i` and `V_0=1`. A complete rounded tensor catalogue can
be emitted with `O(P V_d)` actual tape movement and `O(V_d)` bounded-precision
coefficient multiplications, using a fixed number of tapes. It does not
require one tape head per axis or d complete passes over the final catalogue.

The campaign has `P>>d log(max r_j)`, so a complete bounded metadata update
fits within the charged record width. For a use outside that regime, metadata
must be charged separately or implemented with delimited streams and
amortized counters; this statement does not grant free large address words.

The multiplication arithmetic is charged separately as `O(V_d M(CP))` for a
fixed constant C accommodating complex products. It can use the strictly
smaller conditional multiplier in the campaign's recurrence. Ordinary
schoolbook arithmetic is not silently counted as linear time.

## Physical construction

Keep an old prefix buffer, a new prefix buffer, and the current short axis
catalogue on separate tapes. Fixed scratch tapes implement a P-bit product
and its rounding; their number does not depend on d. A sequential metadata
counter records the current prefix and catalogue entry.

At level j:

1. Read one P-bit record from the old buffer and copy it to a fixed scratch
   word. The old-buffer head remains there while its children are emitted.
2. Scan all `r_j` entries of the current axis catalogue. For each entry,
   multiply it by the saved prefix, round the product back to P bits, and
   append one new-buffer record. Copying the saved word to the product's
   input and performing the product's local tape operations are charged.
3. Rewind exactly the current `r_j P`-bit catalogue region and continue with
   the next old prefix. No growing tensor payload is carried in that rewind.
4. After all old prefixes, exchange the old/new buffer roles, rewind their
   actual used regions, and advance to the next axis catalogue.

The output is lexicographic order with coordinate j appended after the old
prefix. Every old prefix is used with every entry of the current catalogue.
The short catalogue is physically scanned and rewound for every old record;
its repetition is part of the charge, not a RAM broadcast assumption.

At level j, old-buffer reads cost `O(P V_{j-1})`, catalogue scans/rewinds cost
`O(P V_j)`, output writes and buffer rewinds cost `O(P V_j)`, and there are
exactly `V_j` products. Holding one P-bit prefix on a scratch tape is a paid
fixed-width record, not a growing-memory advice table.

Because every radix is at least two,

`sum_{j=1}^d V_j <= V_d sum_{k=0}^{d-1} 2^-k < 2 V_d`.

One-time access to all short axis catalogues costs `P sum_j r_j`, also at
most `O(P V_d)`. Thus the d levels have geometrically growing buffers; the
aggregate movement and number of products are bounded by a constant times
the final coefficient volume. The same argument applies to unequal radices.

## Precision and applicability

For normalized contracting coefficients, round each factor and each prefix
to P bits. If factor and product rounding errors are at most eta, a prefix
of depth j has absolute error `O(j eta)`. Choose P to absorb `log d`, the
required coefficient accuracy and the explicit chirp reserve. Retaining all
exact denominators would instead create an uncharged `dP`-bit record.

Bare Laurent inverse factors may have norm slightly above one. Normalize by
the campaign's paid common bound, or explicitly charge the product of
coordinate operator norms and its amplification. The real/imaginary record
width remains a constant multiple of P. Expanding outer factors use the
separately paid reserve; this lemma does not itself bound that reserve.

This is a constructive source-level tape lemma for setup coefficients. It
does not permit d passes over the main multiplication input, remove CRT
movement, or establish a kernel tail. It sharpens the physical presentation
of the campaign's existing rounded-prefix tensor generation interface.

## Exact finite movement discriminator

`code/check_tensor_catalogue_tapes.py` executes old/new buffer reads, writes,
catalogue scans and rewinds as explicit word-head movements. It compares the
complete generated tensor against independently repeated prefix rounding and
exact rational inputs. Native product internals are separate, with four exact
integer child products charged per complex prefix; this is not a binary tape
instruction simulator.

The four completed cases have1,001,6,561,65,536 and262,144 final records,
through dimension18 and256 fractional bits. Their prefix-volume ratios are
1.15584,1.49977,1.99997 and1.99999. Measured outer movement per final record bit
is7.5934,11.0020,16.00024 and16.00008. Every independent exact comparison stays
within `4*d*2^-P`. Configuration, source identity and results are retained at
`configs/tensor-catalogue-tape-controls.json` and
`results/tensor-catalogue-tape-controls.json`.
