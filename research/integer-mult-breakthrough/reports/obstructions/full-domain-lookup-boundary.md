# Full-domain lookup tables: exact component and charged access boundary

Status: **SCOPED ALL-SIZE SETUP LEMMA** and **EXACT FINITE TABLE COMPONENT**.
The measured access routine is a particular sequential scan, not an optimal
fixed-tape algorithm or a universal lower bound.

Alman's [arXiv:2211.04643v1](https://arxiv.org/pdf/2211.04643v1), Theorem3.2,
groups small finite-field transforms using complete input/output tables. Its
bit-operation bound is O(N log N/log log N), with lookup access charged in
the paper's model. A Gaussian-dyadic primitive and uniform tape access require
their own arguments. [Pinned inputs](../../configs/obstructions/wht-primary-source-pins.json)
record the primary revision, PDF hash and recovery URL.

## An explicit setup bound

Suppose a K=2^t input-symbol block has q possible values per symbol and the
algorithm materializes a separate record for every possible block input.
There are exactly q^K records. If its setup budget is O(N^delta polylog N)
for fixed delta and q>=2, even one bit per record implies

```text
K log2(q) <= delta log2(N) + O(log log N),
t <= log2 log2(N) - log2 log2(q) + O(1).
```

Thus this particular full-domain mechanism groups only O(log log N) binary
address dimensions, not (log N)^eta dimensions for a fixed positive eta.
For the integer-input length n, additionally require log N=O(log n), or
directly charge the table's materialization within O(n polylog n) global
work. The latter implies q^K<=O(n polylog n) itself. Under either premise,
if an unchanged outer architecture saves only this grouping factor, it
cannot yield a fixed positive logarithmic exponent saving. For every
kappa>0, (log n)^kappa/log log n tends to infinity. An uncharged advice table
is outside the setup premise. This conclusion does not
exclude compressed, partial-domain, low-entropy, or entirely different
lookup constructions.

The exact integer control uses q^K<=N^(1/2), rounds K down to a power of two,
and rejects the next doubled block. For q=3 and log2(N)=64,256,1024,4096,
16384,65536, its grouped dimensions are4,6,8,10,12,14. Those finite values
illustrate the proved bound; they are not an extrapolated exponent estimate.

## Exact tables and a literal sequential scan

The [independent component](../../code/obstructions/full_domain_lookup_boundary.py)
builds every table entry by butterflies and verifies it with the direct
Walsh sign formula. A three-tape abstract scan reads the serialized key
and value fields, rereads and rewinds the query, and writes a fresh output.
It charges every data read, output write and one-cell head move. Neither
the query nor the table is modified. The finite alphabet is binary symbols,
a left marker, a field delimiter and a record delimiter.

The implementation's tape controller has not been compiled into a formal
finite-control machine. Counter values are measurement metadata, and Python
execution time is not the asserted tape cost. Output assembly is charged as
sequential writes and moves. This is a useful concrete access baseline, not
a reproduction of the paper's faster lookup operation.

| Field | K | Complete records | Serialized table bytes | Checked output values |
| --- | ---: | ---: | ---: | ---: |
|F3|2|9|91|18|
|F3|4|81|1459|324|
|F3|8|6561|223075|52488|
|F5|4|625|16251|2500|

Each of four workers checks the complete domain plus fourteen sequential
lookups, including first and last keys. The largest case took0.45 seconds.
The last key forces a complete table scan. Its cost is Theta(q^K*K*log q),
so simply placing the full table on a sequential tape does not reproduce an
O(K*log q) lookup. Invalid field codes and malformed framing are rejected.
Only table hashes and deterministic reproduction are retained; the complete
table bytes are deterministically regenerable and are not described as a
committed payload.

An alternative batched sort/merge would need to pay complete keys, return
addresses and payloads. It has not been implemented here; an index relabeling
cannot replace that cost argument. Direct arithmetic on each block remains
an available baseline, and the sequential-scan failure is not a lower bound
on all lookup algorithms.

## A primary-source boundary for another tempting shortcut

The current [F3 Walsh rigidity result, arXiv:2608.06592v1](https://arxiv.org/pdf/2608.06592v1)
restricts approximations changing at most one percent of entries at its
specified logarithmic-squared target rank for sufficiently large sizes.
It is not a Gaussian-dyadic native-circuit theorem. The arithmetic H8
decomposition changes21 of64 entries and is outside that sparsity premise.
The different field and size premises must be retained; no general circuit
exclusion is derived from this recent theorem.

## Continuation

Full-domain table regrouping alone is a supporting subpower improvement.
A plausible breakthrough use would require structured small input sets or
shared signals that avoid the q^K setup count, together with paid access and
the complete Gaussian/CRT interface. Arbitrary dirty helper values make an
entropy restriction especially delicate. The next test should target an
actual constrained signal family, not a larger universal table.

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/full_domain_lookup_boundary.py --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/full_domain_lookup_boundary.py \
  --workers 4 --output /tmp/fresh-wht-lookup.json
```

The scoped setup deduction and implementation were developed with OpenAI
Codex assistance. The [independent transfer review](../transfers/full-domain-lookup-independent-review.md) accepted the setup deduction,
checked the primary paper's RAM lookup definition, and required the explicit
global-size/setup premise above. That is internal mathematical review,
not external human review or formal verification. No new kappa is asserted.
