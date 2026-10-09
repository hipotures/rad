# Independent review of complete activity batching and its moment

Status: **INDEPENDENT MATHEMATICAL AND SOURCE REVIEW**. This accepts the
stated grouping construction and conditional volume discriminator. It
does not independently repeat either producer experiment, compile the
initial activity route, supply a shorter zeta word, or establish an
integer multiplication exponent.

The reviewed tape source is
[`activity_width_grouping_tapes.py`](../../code/complex/activity_width_grouping_tapes.py),
SHA256 `b2110ccbf6f5b366c56e930dc5384e08afdcd2c9e6f8bfbb2c3d8090ea5b8256`.
Its only owned dependency is
[`prefix_activity_shape.py`](../../code/complex/prefix_activity_shape.py),
SHA256 `b55dd778362a34b53b452ba73bd87cced70b680721a2547ac3f7e5689383c20d`.
The independently authored moment source is
[`activity_gate_moment.py`](../../code/obstructions/activity_gate_moment.py),
SHA256 `9cddd0288de0363033d772248566abca91d21edf56e9dcd655f9ec353b8bd3f3`.
The review receipt pins the reports, configuration and observed producer
evidence separately.

## Finite alphabet and head motion

The consumer has seven tapes and ten symbols. Its routing decisions use
only a symbol under the current head, a current-cell write, or a unit
head move. `Tape.read`, `write`, and `move` charge those operations.
Numeric buffer indices and lengths implement the simulator or its
legality checks; they do not choose a routing destination. The consumer
uses a fixed number of tape pointers and finite control states. The
increasing `stages` counter records a measurement rather than selecting
an uncharged jump. A fixed binary encoding of the alphabet multiplies
cost and storage by a constant.

At one radix stage, `read_key_and_return` scans the complete width header
against the marked template, then reverses all those input-head moves.
`copy_record` copies every subsequent symbol through its delimiter.
Concatenation, clearing and rewinding also walk the entire affected
streams. `clear` stops at the first blank; the maintained invariant is a
contiguous nonblank stream without internal blank gaps. The partition
journal append head advances by one cell. There is no random-access
population lookup in the consumer.

The fixture does use ordinary Python address decoding, sorting and buffer
indexing to construct inputs, check outputs, and simulate an outside
child. Those operations are separate from the claimed routing word.
In particular, this source starts in prefix order and its inverse ends
in prefix order. Neither direction executes the original prefix codec.
Producing the width labels and address tags is also a separate metadata
procedure. The reported polynomial metadata allowance must be supplied
by that procedure rather than inferred from fixture indexing.

## Journal inverse after payload changes

For one stage the saved metadata are the original sequence of M partition
bits, a separator, one unary token per zero-bucket record, and an end
marker. The inverse scans backward to recover the token count and pattern
boundary. It splits the current stream after that number of **whole
records**, and merges the resulting buckets according to the pattern.
All journal crossings, complete record copies, count erasure, bucket
erasure, stream returns and stage erasure are charged head operations.

The invariant is that stage metadata identify positions, independently
of coefficient values. Inductively, reversing each stable partition
restores the record permutation even after all payload components have
changed. No original coefficient snapshot is read. The reverse preserves
previous journal stages and erases only the completed stage. The header
template is erased after the forward sort; buckets and threshold are
erased as they are reused; the last inverse leaves no routing metadata.
The surviving current stream is the newly changed payload in its original
prefix order.

The fixture changes both ends of all eight real/imaginary component words
per record while preserving key, tag and framing. The observed producer
full result reports 4232 records, 16928 Gaussian fields and 231113414
literal routing steps; the bounded result reports its smaller cases.
These are producer measurements inspected in this review, not new
independent measurements. The corruption and cropped-framing controls
are appropriately scoped.

The tested records have equal lengths. The delimiter-based proof also
works for initially unequal lengths: replace M Q by the total complete
record length L. Each record must still contain its entire fixed-length
header; delimiter symbols must not occur inside encoded payloads; keys,
tags, record population and each record's framing must survive the child.
The current fixture's replacement interface rejects any length change.
No tested variable-length or child-resizing claim follows from it.

## Complete volume and auxiliary tapes

Let ell=ceil(log2(f+1)) and L be the total length of all complete records,
including their headers, tags and delimiters. A stage uses O(L+M ell+M)
read/write/move operations. Full forward and reverse therefore cost
O(ell [L+M ell+M]). Input loading and template initialization are measured
separately in the source and have the same or smaller asymptotic order.
The asserted numerical constant 160 bounds the measured forward plus
reverse ledger, rather than supplying a native performance estimate.

A conservative space reservation is four L-symbol complete-record tape
extents, a journal of at most (2M+2)ell symbols, a threshold of at most M
symbols, a header of ell+1 symbols and the fixed origin markers. Actual
simultaneously occupied payload volume can be smaller, but previously
visited tape extents remain covered by this reservation. The additional
tapes are ordinary initially blank machine workspace; the result is not
a reversible circuit with arbitrary dirty auxiliary banks.

If a payload has R bits and its address/tag metadata require A bits, then
Q=R+O(A+ell+1). Relative to the original payload volume V=M R, the explicit
bill is O(ell V+M ell[A+ell+1]) and constant additional complete-payload
buffers, plus the journal. For A at least ell and a supplied O(M A^3)
metadata procedure, this yields the report's O(V log(f+1)+M A^3) bound.
It does not erase copied buffers or tags from the accounting. The child
must accept this complete record format or pay the conversion to its
own format. Logical record-index alignment alone does not provide that
native interface.

Stable filtering by width preserves every complete contiguous prefix
cylinder and its internal tail order. The displayed class population is
a multiple of 2^(fK), so class boundaries also align to each 2^(wK) tail
in record numbers. Guards and all Gaussian fields remain present. A
complete gate is consequently a direct sum over disjoint cylinders, and
its operator norm is the maximum of the complete fiber norms. This does
not cover a helper shared across overlapping cylinders or an unreturned
external companion. Such an interface needs its own norm, volume and
restoration proof.

## Exact activity moment and its assumptions

Write D=2^h. An active prefix has A0=2^((h-1)(K-1)) choices and a free
K-bit tail. An inactive prefix has I0=(D-2)2^(h(K-1)) choices. Thus the
whole-record volume fraction at width w is exactly

    binom(f,w) A0^w I0^(f-w) 2^(wK) / 2^(hfK)
      = binom(f,w) (2/D)^w (1-2/D)^(f-w).

This includes every inactive letter, unselected guard bit, zero-width
fiber and rare all-active class. It is a binomial law for **complete
equal-format payload volume**, not for scalar record counts after an
unpaid change in precision or representation.

For the assumed g-gate recurrence Phi_f(p)=g E[(W/(hf))^p], its first
moment is 2g/(hD). Every positive child ratio lies in (0,1/h]. Hence
x^p>x for 0<p<1, and the ordinary Yates count g=hD/2 has Phi_f(p)>1.
Successful activity routing cannot manufacture the absent gate saving.
For a genuinely shorter word, Jensen instead gives
Phi_f(p)<=g [2/(hD)]^p. The hypothetical h=3, g=11, p=97/100 comparison
is exactly equivalent to 11^100<12^97. The source's positive-integer
comparison certifies this sufficient bound without numerical root
evaluation. Its twelve-gate control fails the same bound. The rational
mass, mean and variance checks and integer square-root enclosures are
consistent with the formulas; they do not supply the missing word.

Extra helpers, copies, padding, changed precision and larger child
formats must multiply the appropriate weights or receive separate paid
charges. Local fixed coefficients need actual invertible dyadic gauges.
Remainder axes, initialization, routing, cleanup, stopping and integer
recovery remain in a complete replacement ledger. In the previously
reviewed stopping theorem the actual overhead exponent must satisfy
tau<=p; a supplier near tau=1 cannot silently support p=.97. Fixed
branching norm lemmas also cannot be transferred to f+1 sequential
children unless their full-state block-disjointness, or another explicit
sibling bound, is established.

I accept both reports under these stated interfaces. The useful next
step is a complete shorter scalar word with paid complete-cylinder
dispatch and endpoint restoration. Neither this review nor a green
bounded check establishes such a supplier or a larger kappa.
