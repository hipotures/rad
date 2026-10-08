# Exact physical residual-rank distribution

The promoted ground-50 cutoff-two circuit has an exact categorized physical
edge-rank histogram, including its source corrections, complementary middle
stage, center returns, shared-bank join and all boundary edges. Its rank sum
is **47,303,059,632,864,000,000**, exactly the existing `W*m-D`.

The [certificate](../runs/20261008T031020Z-finite-residual-ranks/results/certificate.json)
records `m=125000`, `W=378424491200000`, `D=1767136000000`, side width
472,885 and 7,049,306,035,520,000 physical edges for the stated gate grouping.
It reconstructs the unchanged map, positive envelopes, compiler and physical
target checks. Its compiled hash matches the independently promoted witness
`0119f56ac55b12ee03d204857a470f95243591a2f86dae2ec9325bc03f96a44a`.

The grouping is explicit: each compiled logical-node mixer is one invertible
common-frame gate; source copies and output injections are grouped by data
triple; a central gather or scatter is one common-frame gate on a bank and
its h centers. Identity input mixers are retained. Splitting a grouped gate
at the same frame inserts only zero-rank edges and leaves the positive-rank
histogram unchanged. Additional identity padding is zero. Both zero-rank
and full-rank-m keys are retained, with full-rank count zero.

Local forward side events use source-line dimension1, all recorded middle
frames, target complement dimension `h-1`, and cleanup dimension h. The
inverse middle uses the original frames' complements, in reverse order.
Every actual middle path is checked as increasing. The four full mixer
passes, two copies and two injections determine the exact zero-edge counts.
Independent small chronological event replay executes each pass separately
at grounds6,8,12 and matches the whole histogram, including zero incidences.

Each stage has `v^2` invocations. The first/third shared role begins at0,
joins dimension-h frame E to dimension-`m-h` frame H with rank `m-2h`, and
ends with a zero edge. Each middle-bank role enters with rank `h^2-h` and
leaves with rank `m-h^2`. A center adds three rank-h changes per stage,
including one decreasing return. The N initial physical X sources use
negative projectors: their first edge has rank1 even though its positive
label dimension change is zero. Data sinks contribute zero. These formulas
regress exactly to `W*m-N+6*v^2*h^2`; each category retains its multiplicity.

The current proved recurrence charges one width-`e/m` child per unit of edge
rank. A proposed one-child implementation on `r*e/m` bits would instead
lead to the prospective score `sum count(r)*(r/m)^tau / W`. Its derivative
at tau1 is about0.055975371. The corresponding first-order saving is
`6.673962231485795e-7`, versus `3.1831570838553596e-9` for the current
uniform-shrink estimate. These are floating discriminators for a hypothetical
interface, not certified exponents. Arbitrary Bruhat pivot gathering and the
fixed-tape recurrence remain proof obligations; the exact histogram itself
does not resolve them.

The full run took48.11seconds on one reserved worker and peaked at
3,358,264KiB. Source [finite_residual_rank_histogram.py](../code/finite_residual_rank_histogram.py),
SHA256 `422eb0f5c18fcb55a5fd11ee28211e36c1ecd4e9ea5ddf954fe82a2250fb40a5`,
and [protocol](../runs/20261008T031020Z-finite-residual-ranks/protocol.json)
record the exact command and dependency hashes. Reproduce in the pinned
math environment against immutable upstream bcd4ebde, using a fresh output
path. This extends the ongoing campaign; its original start and previous
deadline are retained, and future work follows the user-extended10:00UTC
deadline.
