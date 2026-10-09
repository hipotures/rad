# Direct singleton aggregation cannot use the raw geodesic bill

Status: **SCOPED ALL-SIZE SOURCE-FORMATION OBSTRUCTION WITH EXACT CONTROLS**.
For weight-five paired source cubes, a single pure carried helper per source
cannot directly form every singleton aggregate along the declared monotone
root paths without at least 24 extra ranks per 32-source cube. Three core
passes therefore require at least 2.25v extra rank, exceeding the retained
master's entire deficit of at most 2v. This excludes a specific way to obtain
the attractive raw cap role count. It does not exclude source-helper mixing,
response cuts and new births, cancellation-created aggregates, copied readers,
non-Clifford frame operators, general cross-column entanglement or changed
endpoints. No native supplier or multiplier exponent is asserted.

## The precise formation model

A paired weight-k cube has n=2^k source labels. Each label selects one axis
from each of k disjoint coordinate pairs; k is odd. Each original source is
in its line frame. There is one carried dirty helper per source; its original
source coefficient remains that source alone, with no helper-row mixing.
Every singleton-pattern aggregate is formed by direct unit additions from
these helpers. Aggregate roots follow monotone canonical L_E frame paths
from zero into their literal bucket subspaces, then can continue toward the
cap/full endpoint. Those root paths never lose previously acquired E
directions. All scalar additions use the identical actual common operator,
including its monomial gauges. Arbitrary dirty seeds are retained.

Helper paths may be nonmonotone. The rank price is the retained Clifford
frame metric, including every actual child transition. For a general helper
Lagrangian L, let E(L)=L intersect the fixed full diagonal Lagrangian D.
The common bucket endpoints are canonical L_E. A helper is called released
if, after its source injection along the line-to-full continuation, some
point has E(L) not containing its original source label.
This definition permits its source to be gathered at zero for a paid price;
it does not silently impose the root-support premise on released sources.

## Bucket geometry and release-aware bound

The whole paired cube spans a (k+1)-dimensional binary space Q. For each
coordinate pair and each selector value, its singleton bucket is a distinct
rank-k hyperplane of Q with 2^(k-1) source labels. All those labels have odd
coordinate parity. A proper rank-(k-1) subspace of a bucket contains at most
2^(k-2) odd labels: a nonzero linear parity functional splits that subspace
into two equal fibers. Hence any 2^(k-2)+1 labels span the full bucket.

For k=5 there are ten buckets, each with sixteen labels, and any nine labels
span its rank-five endpoint. Suppose l of the 32 source helpers are released.
If a bucket contains r released sources, at least max(8-r,0) unreleased
writes must meet its full bucket frame. Before and at those meetings, all
previous unreleased labels remain in the monotone root E. Each released
source belongs to five buckets. The number F of compulsory full-bucket
meetings consequently satisfies

    F >= sum_b max(8-r_b,0) >= 80-5l.

Two distinct bucket Lagrangians have distance two. An unreleased helper
visiting r distinct compulsory bucket frames pays at least
h-1+2(r-1): its initial line belongs to every such bucket, the first
entrance costs four, and the last bucket to full costs h-5. Summing across
at most 32-l unreleased helpers gives at least

    2 max(F-(32-l),0) >= 2 max(48-4l,0)

extra ranks beyond their line/full endpoint baselines.

A released helper pays at least two extra ranks independently. The general
frame inequality

    d(A,B) >= dim E(A)+dim E(B)-2 dim(E(A) intersect E(B))

follows because E(A)+E(B)+(A intersect B) is isotropic; its dimension is
at most h, and its extra intersection is exactly E(A) intersect E(B).
Applying it to the initial source line, a frame losing that line, and full
gives h+1 instead of the h-1 endpoint distance. This is a frame-metric
argument, not a numerical amplitude or tape-time claim.

The complete extra rank is therefore bounded below by

    2l+2 max(48-4l,0) >= 24,   0<=l<=32.

The elementary minimum is at l=12. It is a necessary lower bound, not an
attained chronology. In general odd weight k, the same calculation gives
at least (k-2)n/(k-1) extra ranks, before integral rounding. Every odd
k>=5 therefore requires at least 3n/4 per core in this formation class.
Summing across source cubes and three cores gives at least 2.25v. The
synchronized-center master deficit is at most 2v and smaller after its
paid copies. Even its first moment cannot contract if this source-formation
cost is added. No parameter sweep is needed for this exclusion.

## Why the stronger no-release claim is separately scoped

With l=0, the count gives at least96 extra ranks per cube. If helpers are
processed in one global source order, its first eight source passes cannot
have compulsory ninth-label meetings, improving this to112. These two
statements are no-release subcases. They must not be applied to arbitrary
helper paths. An explicit all-release word gives only64 extra ranks and
rejects that promotion.

The all-release control first subtracts every old helper seed from its
aggregate roots at identity. Each helper then moves zero to its source
line, receives the source there, moves back to identity, and contributes
to its roots. Roots now contain their original dirty seeds plus the desired
source sums. Finally sources and helpers go to full and each source is
un-injected from its helper. Every helper restores its arbitrary old value
under the full physical endpoint operator. A helper has paid path
zero->line->zero->full, rank h+2 rather than h. There are no clean helper
assumptions. Scalar gates at every stage share the actual frame.

The finite source constructs this complete scalar word and its chronological
inverse, checks every independent source/helper/root column, and audits all
common actual anchors. It does not expand literal Gaussian address matrices
or compile native wrapper words. The operator argument uses the declared
actual frames and exact common-operator telescoping; those limits are explicit
in each receipt. The early old-response omission changes the complete matrix
and is rejected.

## Evidence and reproduction

[The standalone probe](../../code/synthesis/singleton_fanout_release_probe.py)
uses only the Python standard library, source SHA256
fec8292dd3fad1c1e008b543bfefc448d51648068ebdb32ea123959a27ff5746.
The original four-worker run started at
2026-10-09T11:52:36.177436+00:00 and completed in 0.817141031 seconds.
It checks exact cube/bucket geometry at k=3,5,7; all 11,440 nine-label
subsets of a representative k5 bucket, with explicit coordinate symmetry
for the other buckets; all 40,320 k3 global source orders; and natural,
Gray and seeded shuffled k5 orders with zero, twelve and all 32 releases.
The k3 no-release forced schedule extra ranks range from 12 to 16.

The complete all-release scalar matrices/inverses retain 22 and 74 roles,
5,960 total matrix entries, 64 and 384 common-frame scalar gates, respectively.
The k5 control pays 64 extra ranks and therefore rejects the invalid
universal 96 claim. Bounded regeneration retains all geometry, dirty matrices,
release negatives and a declared subset/order prefix. Original complete
certificates and logs remain unchanged in ignored work/synthesis. Readable
run summaries omit only generated event words and the full per-count lower
arrays, with paths and hashes pointing to the complete originals. The source
regenerates all of them. Complete text archival is required at publication.

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/singleton_fanout_release_probe.py --workers 4 --bounded
python3 -B research/integer-mult-breakthrough/code/synthesis/singleton_fanout_release_probe.py --workers 4
```

Optional --output requires a fresh file. No downloaded dependency or random
solver is needed; the shuffled-order seed is 202610091146. The bound received
an independent analytical review from the coordinator before publication.
The written proof is not a proof-assistant formal artifact. This work was
developed with AI assistance. A viable raw-stock construction must change
its carried rows or aggregate chronology, rather than assume direct singleton
fanout is geodesic.
