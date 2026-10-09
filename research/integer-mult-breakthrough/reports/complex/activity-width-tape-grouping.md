# Paid grouping of complete activity fibers

Status: **EXACT FINITE TAPE CONTROLS** and an **ALL-SIZE LINEAR-PASS
CONSTRUCTION** for the grouping stage. This starts from the already
permuted [complete-chunk prefix layout](prefix-activity-complete-chunk-shape.md).
The initial prefix permutation remains unpriced. There is no faster zeta
supplier or exponent claim.

## Construction and cost

Let M complete records already occur in prefix order. Each contains its
width w in an ell-bit header, where ell = ceil(log2(f+1)), its original
address tag, and the complete payload. A delimiter ends every record.
Let Q include this whole record and its delimiter. Additional tags and
headers are paid metadata: their generation and representation cost
O(M A^3), with A at least the original address length. They add no address
axis. No coefficient field supplies clean scratch.

The [consumer](../../code/complex/activity_width_grouping_tapes.py) uses
seven one-dimensional tapes and ten symbols. Each tape operation is a
read or write at the current head or a unit head move. A fixed binary
encoding of this alphabet changes costs by a constant. The tapes hold
the current stream, two buckets, the next stream, a partition journal,
a unary threshold, and a header template. Their number is independent
of f, K and record length. Temporary copies occupy ordinary computation
tapes; their creation, erasure and returns are charged.

For each width bit, from least to most significant, scan the entire
header using a template marker, return to the record's first cell, and
copy its whole payload and delimiter to bucket zero or bucket one.
Save one partition bit per record. Concatenate bucket zero then bucket
one. Save the zero-bucket population as one unary token per record,
and delimit this journal stage. Clear and rewind the old stream and
buckets. A least-significant-bit stable radix sort groups widths in
increasing order and preserves the previous order among equal widths.

The journal contains at most `(2M+2) ell` symbols. To undo one stage,
recover its unary zero population and original partition pattern by
scanning backward. Split the current stream after the indicated number
of complete records. Merge those buckets according to the saved pattern.
Erase all completed stage metadata and rewind every reused tape. This
inverse depends on the saved record order, not on the original coefficient
values. It therefore restores the order of newly changed arbitrary
payloads. It retains the keys and original address tags that an actual
child must preserve.

Every stage makes a constant number of full copying, erasure and return
passes, plus O(ell) header work per record and O(M) journal work. The full
forward and inverse construction consequently costs

    O(ell M(Q+ell+2)) = O(V log(f+1) + M A^3),

where V includes complete payloads and A also covers their length and
address metadata. Header/template setup is included. The source counts
all literal tape reads, writes and unit moves, and enforces the loose
bound `160 ell [M(Q+ell+2)+1]`. This bound is a conservative pass ledger;
the measured constants do not optimize it. Extra scalar child work is
explicitly outside this routing time.

This grouping cost can fit a retained local allowance V(EK)^tau for
fixed tau > 0 and f <= E, together with its paid metadata term. That
comparison only prices grouping. A generic radix sort by all EK bits of
the initial prefix destination costs O(VEK) and does not provide the
required sublinear power. The fixed-h paid Boolean wrappers also do not
automatically route an f-dependent prefix permutation.

## Complete disjoint fibers

Every concatenated prefix codeword p has length `(hf-w)K` and exactly the
full free tail `{0,1}^{wK}`. Prefix-freeness makes these cylinders disjoint
and their union the complete hfK-bit cube. Every unselected K-1-bit guard
coordinate and every Gaussian field belongs to the same partition.

Stable width sorting keeps each individual cylinder intact because its
records were contiguous in prefix order and have equal w. Within a
width class, the original prefix order and complete tail order survive.
Relabeling the prefix list as a dense group number is metadata work;
the actual data movement has already been paid. Thus a bulk child at
one width can operate on a complete ordered group-prefix by tail cube,
provided its declared full Gaussian block, spectators and guard
endpoints actually satisfy the child contract.

The sorted class boundaries also respect full tail alignment. Each
width population is

    binomial(f,w) 2^(f[h(K-1)+1]) (2^(h-1)-1)^(f-w).

Since `h(K-1)+1 >= K`, every class population is a multiple of 2^(fK).
Every preceding-class offset is therefore a multiple of 2^(wK).
Grouping retains complete tail cubes even in the original full-cube
address numbering, without an extra incomplete boundary block.

For one elementary row gate the resulting full endpoint is a direct
sum of its complete fiber operators, including identity on w=0 fibers.
Its operator norm is the maximum of the fiber norms, rather than their
product over f+1 width classes. Stable grouping is a permutation and
does not change this fact. This does not establish the precision
recurrence of an entire supplier: all parking regions, helpers, scalar
prefixes and completed child endpoints must satisfy the same invariant.
The transfer track's geometric precision argument is conditional on
these obligations and was not tested by this tape checker.

For the pinned elementary coefficient c=(1-i)/2, c^-1=1+i, a complete
fiber is `diag(c^wt) Z_w diag(c^-wt)`. The exact endpoint and its inverse
have component-L1 row norm at most 2^w and denominator increment at most
w. The displayed entrance and middle prefixes have the safe norm bound
4^w. Since c^2=-i/2, its powers and inverse powers are dyadic shifts with
a fourth-root unit, plus one constant Gaussian addition when needed.
Their metadata and complete-field passes must still be paid by any
native implementation. A general row word needs admissible actual
coefficient gauges; nonunit coefficients cannot inherit this dyadic
inverse interface silently.

An eventual contracting child moment also requires a routing overhead
exponent tau no larger than the chosen recursion exponent. Ordinary
twelve-gate Z3 has a neutral first moment; a hypothetical eleven-gate
word is only an optimistic capacity hypothesis. Neither such a word
nor the required improved routing supplier follows from this grouping.

## Exact finite evidence

The [full run](../../runs/20261009T071532Z-complex-activity-width-tapes/report.md)
uses four workers for h=3, f=1/2, K=1/2, and component widths 8/16/32/64.
It checks all 4232 records and all 16928 arbitrary Gaussian fields.
The checker changes both ends of every one of 33856 real/imaginary
component bitstrings after grouping; the journal inverse restores their
correct original record positions. All prefix cylinders stay contiguous
and all scratch tapes and metadata are erased. Corrupted partition
metadata and cropped payload framing reject.

The full word counts 231113414 literal tape operations and takes
17.544948 seconds in the Python simulator. Measured routing operations
per whole symbol per radix stage lie between 53.10 and 53.94. These are
simulator measurements, not native host performance predictions.
The largest case has 4096 records of 527 symbols and a 14596-symbol
saved journal. No original or updated coefficient payload is omitted
from the checks; generated row data deterministically regenerate.

The [bounded run](../../runs/20261009T071834Z-complex-prefix-grouping-ci/report.md)
also replays the prefix operator separately. Its commands are portable:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/prefix_activity_shape.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/activity_width_grouping_tapes.py --workers 1 --bounded
```

There was no failed tape-word attempt. Source and dependency bytes remain
unchanged across both runs. The only dependency is the pinned owned
prefix source and Python's standard library. This is AI-assisted
internal research, not formal verification or external peer review.

## Next discriminator

Bind an actual control-preserving switch-network route to the full K
chunk geometry, every quarter guard and complete exceptional-record
repair. A correct address-array permutation or cheap Benes-mask
computation alone does not pay that route. Once available, compose its
forward and reverse with this complete grouping word and the actual
Gaussian child block, rather than treating them as separate oracles.
