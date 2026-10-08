# Review of the exact both-negative data classification

Reviewed 2026-10-08 14:40 UTC. This is an independent source, arithmetic and
proof review of the geometry worker's completed classification. The scout
did not repeat the multi-million-pair computation. The basis formulas and
unchanged transfer conditions are derived separately in
[new-basis-algebra-review.md](new-basis-algebra-review.md).

The former uniform `9*[1]+[21,17]` profile does not hold for every pair at
`L_h=I-4J/[3(h+3)]`. The complete first pass retained all 192596 exceptions,
including a genuine rational zero. A uniform width19 replacement also failed.
The accepted repair computes each exceptional ordered profile exactly; it
does not discard failed pairs, assume the old17-block, or infer a rational
zero from one modular failure.

## Reviewed evidence and input binding

The [complete histogram](../geometry/results/both-negative-data-histogram.json)
records 3880704 regular pairs and 192596 exceptions, totaling 4073300 actual
lexical triple pairs. The exceptions have 169 distinct width-run profiles.
The first 21 block remains common, while the residual17-block can split.
One data front has rank mass `528*4073300=2150702400`, including the unchanged
width 481 middle. Both front histograms are retained explicitly.

The [input audit](../geometry/results/both-negative-data-input-audit.json),
completed 14:32:15 UTC, binds every unique exception index to the lexical
Cartesian product of 1771 triples at 23 and 2300 triples at 25. It checks the
binary fixture against the complete failure list, counts regular plus
exception coverage, validates part hashes and receipts, and independently
reaggregates every width frequency and rank mass. I also inspected the four
receipts: their part ids are exactly 0, 1, 2, 3, each has parts=4 and 48149 cases.
The native modulo partition therefore covers every fixture position once.

Reviewed identities:

| Artifact | SHA256 |
| --- | --- |
| [Native exact rank source](../geometry/code/negative_exception_rank_union.cpp) | `dd984ddba70b0d13adbec30750a483c139374688f2850b019fd602a35785b9b9` |
| [Input audit source](../geometry/code/audit_negative_data.py) | `f9d881c5ce3860065c0614c038dc2612be83ac95a8a0d8cf3a801f47bf2c4d80` |
| Complete histogram | `12e6a17f9282827881c9aebe46dbf0bfd4737173a774b1581509374d12e08186` |
| Input audit receipt | `cd21e9a1b85cd5ff144c83ffe2909846140dd1a41e0fffa87989dcb8dd995c77` |
| Complete first-pass classification, external derived JSON | `d5af857ca7b5ebeadbecca4271696db71be663b1cb8b330a8fcffcdb9de4126b` |
| Exact exception fixture, external derived binary | `cf4e194ad69cfa7b02dee171eea16347ff04533e3e2fa6aff79d3ee60abb5f03` |

External paths and acquisition/regeneration remain geometry's manifest and
reproduction responsibility. The scout read the compact evidence and audit
source; the byte-for-byte full input check was executed by geometry.

## Exact rank argument

After nonzero diagonal scaling, the 47-square ordered boundary has entries

```
M[i,j] = -1 + [R_i=C_j]*x[R_i] + [i mod25=(528+j) mod25]*y[i mod25],
x = 13/11 inside the first triple, -13 outside,
y = 7/6 inside the second triple, -14 outside.
```

Thus 66M is integral with the source's conservative absolute entry bound 1848.
For every minor of order e<=47, Hadamard gives
`|det| <= e^(e/2)*1848^e <= 47^24*1848^47`. The last integer has 644 bits.
The source constructs 21 distinct 31-bit primes by exact trial division, with
a 651-bit product strictly greater than that bound; all four receipts retain
the exact integers and primes. Scaling by 66 changes no rational rank, and
none of these primes divides 66.

For each first-row/last-column corner, let r be its maximum modular rank over
the 21 primes. Every (r+1)-minor vanishes modulo every prime, so the product
divides its integer determinant. The bound forces that determinant to be
zero over the integers. At least one r-minor is nonzero modulo a witness
prime, hence nonzero over Q. Therefore r is the exact rational corner rank.

Rightmost row elimination preserves all first-row/last-column corner ranks:
earlier pivot rows have zeros to the right of their pivot, and later rows
are modified only using earlier rows. The prefix-count table from each
modular pivot set consequently supplies the required corner ranks. The
source takes their componentwise maximum and then takes mixed second
differences to recover the rational rook pivots. It never unions modular
pivot positions. Every difference is asserted 0 or 1; full rank 47 and the
total run length 47 are checked for each exception. Consecutive diagonal
pivots supply the exact contiguous runs used by the histogram.

All modular values remain in[0,p-1], with p<=2147483647. Multiplication is
strictly below2^62 and fits signed int64; subtraction is greater than-p and
less than p, and conditional addition restores the range. Integer matrix
formation and the exact primality loop likewise fit their types. Arbitrary
precision integers hold the Hadamard bound and prime product.

## Scope of acceptance

The regular first pass uses a complete fresh replay at a fallback prime,
so successful prescribed prefix minors are nonzero over Q. Their ordered
zero identities still require the inherited all-weight rank-cut proof;
modular zero observations alone do not prove those identities. Exceptional
profiles instead receive the full exact corner-rank argument above.

The reviewed complete input binding and classification close the new
data-profile gate for this specific basis, source family and ordering.
Any changed basis, source restriction, permutation or boundary ordering
requires fresh certification. Internal producer changes can retain these
static data inputs only when those actual objects remain identical; actual
local residuals and copied-center profiles must still be rebuilt for the
changed producer and matching.

The physical front assembly, complete paid-copy and endpoint timeline,
scalar envelope, local CRT profiles, address-prime conditions and inherited
analytic/tape hypotheses remain coordinator proof gates. Neither the
classification nor this review alone certifies an improved integer
multiplication theorem.
