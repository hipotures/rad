# Arbitrary-width tail crossings and a conservative batch count

The tail stream schedule passes complete finite controls. It removes an
e=m b divisibility restriction from an existing equal-width main-block
interchange. This result alone does not prove a better recursive bit
primitive: actual Bruhat pivot grouping and endpoint counts remain separate
obligations.

Write e=m b+t, b=floor(e/m), 0<=t<m. For e>=m, b>=1. The fields initially
appear as

`[P][H_main][H_tail][B][D_main][D_tail][Q]`.

P includes parked row headers and any outer prefix; B is an arbitrary
complete spectator range and Q an arbitrary suffix. Move the t-bit H tail
right across B and D_main by a stable sequential split/interleave scan.
Then apply the existing complete interchange to H_main and D_main, swap
the now-adjacent constant-width tails, and move the D tail left across B
and H_main. The final fields are

`[P][D_main][D_tail][B][H_main][H_tail][Q]`.

Every record of P, B and Q keeps its value, and the two whole e-bit fields
are interchanged. The complete stream volume is preserved. The tail width
is bounded by the fixed machine constant m; splitting into 2^t streams
therefore uses a fixed finite number of tapes and O(2^t V)=O(V) work. It
can alternatively be decomposed into t stable one-bit crossings with
fixed temporary tapes. The test implements the direct sequential
multi-stream form. Main-block interchange is explicitly an existing
interface, not free random access; the test's ideal main permutation is a
reference for that interface only.

The same argument preserves arbitrary complete records, including arbitrary
dirty data on auxiliary roles. The finite control uses binary H/D fields;
the written sequential crossing works for any fixed field alphabet q,
using q^t streams. When attached to the original rational matrix-shear
interface, it preserves that interface's original fixed odd prime q. This
is separate from the prospective native-binary payload construction and
does not convert one address alphabet to another. Small e<m instances
belong to a fixed base case.

A contiguous run of r<m diagonal pivots exchanges r adjacent b-bit chunks
by one child of width rb. Its strict shrink satisfies rb<e and
rb<=floor(re/m). No noncontiguous pivots are gathered by this argument.
Componentwise ordered-affine operations must reset carry at each original
b-bit component; their compatibility with the original Bruhat factors is
part of the separate full transfer.

## Exact stream evidence

The [source](../code/downstream_arbitrary_width_tail.py), executed SHA256
`d54789bf923d6506a790fd95bdc3eb0c1221801a5a00ea1b0d8a98d8625ffb6b`,
checks 1,684,112 complete records in 23 shapes, with m=2..7, e up to 8,
mixed spectator/prefix/suffix radices, zero and nonzero tails, and 72 child
shrink inequalities. Both directions match a direct complete interchange.
Omitting the last crossing gives 1,486,976 record disagreements, preserved
as a negative control. The worker used 233,040 KiB peak RSS and 5.284 s.

The completed run is
[20261008T043058Z-downstream-diagonal-tail-subset](../runs/20261008T043058Z-downstream-diagonal-tail-subset/protocol.json).
Its [tail certificate](../runs/20261008T043058Z-downstream-diagonal-tail-subset/results/tail-certificate.json)
has SHA256
`5f36f0dda062efa36eb57c1e01e420c7a1fb1a8f3e597f579840bc4e4e66c8e9`.
All records are independent labels, so the equality establishes the same
permutation for arbitrary record payloads; it is not merely a numeric
constant-input comparison.

## Conservative prospective characteristic

The companion [count source](../code/downstream_diagonal_batch_subset.py)
leaves every old scalar pivot individual except the final middle auxiliary
endpoints with residual I tensor I tensor (I-P_t). For a triple with minimum
a, its rank-one complement profile has diagonal runs a and h-a-2 and one
offdiagonal pivot. There are C(h-a-1,2) triples with this minimum. Assuming
the independently investigated physical endpoint/profile identities, this
gives the exact batch histogram in the
[subset certificate](../runs/20261008T043058Z-downstream-diagonal-tail-subset/results/subset-certificate.json).

For accepted h51 R502265, 28,330,705,423,416,375,000 old singleton pivots
are replaced. The whole rank sum remains
s=60,190,685,022,033,566,875; the candidate call count is
33,526,491,682,347,566,875, with largest changed width 49. Exact rational
logarithm enclosures and the second-order Taylor bound support

`a=736911727178901/(2*10^23)`.

Indeed, with L_r and U_r lower/upper bounds on log(r),

`D - a*(W*m*U_m - sum(n_r*r*L_r))
   - (a*a/2)*sum(n_r*r*U_r*U_r) > 0`

implies W m^(1-a)>sum(n_r r^(1-a)), using exp(-x)>=1-x and
exp(-x)<=1-x+x²/2 for x>=0. This is a strict characteristic check,
not a promoted exponent. It still needs the actual endpoint multiplicity,
diagonal grouping, recursive row-reservation/setup, base case and full
fixed-tape transfer proofs.

The sources/results are stable. Reproduction uses the two commands in the
protocol with fresh output paths. The original campaign start remains
2026-10-07 22:25:21 UTC, original deadline 2026-10-08 08:25:21 UTC, and
authorized extended deadline 2026-10-08 10:00:00 UTC.
