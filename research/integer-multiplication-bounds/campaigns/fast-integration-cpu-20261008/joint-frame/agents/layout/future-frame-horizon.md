# Reclaim carriers by future frame accessibility

The first future-horizon experiment gives 30,667 roles on the 23-axis public
dual-suffix graph: 123 fewer than PR58 and 21 fewer than high-rank priority.
The exact word passes the producer's full scalar, dirty-basis, and frame
checks. Its physical word SHA256 is
`f833497c99613b1f98091bc54cedc31d3d48fbe42bd3c9c76389bdc6f35c978e`.
Actual fixed-I+J profiles and recurrence assembly remain separate obligations.

The new rule uses the finite graph beyond the current region. For each
current frame F, compute the set of all regions G that contain F, in the
compiler's fixed topological order. A retired component's last compatible
region is the largest index in this set. Before clearing a dependency,
insert components in increasing order of this last index, then decreasing
current rank, then slot index. The hypothesis is that carriers with fewer
future opportunities should supply the clearing basis first, preserving
carriers with a longer horizon. This is a selection rule, not a claim of
global optimality.

The controlled second rule orders components by the number of compatible
regions at or after the current region, with the same rank and slot ties.
This distinguishes a late last opportunity from many remaining opportunities.
The 23-axis and 25-axis attempts have separate fresh execution directories,
protocols, immutable generated sources, and output word hashes. A small
explicit serial queue replenishes each CPU lane with one distinct continuation;
it neither controls an unrelated process nor launches more than one heavy
child per lane.

## Exact finite setup

For the inherited mask frames `(C,U)`, containment is

    C_G subset C_F, and U_F subset U_G.

Index region positions by core mask and by each coordinate present in the
cover mask. Intersect the cover bitsets for all coordinates in U_F, and
intersect the result with the union of core bitsets for nonempty subsets
of C_F. The resulting bitset is exactly the set used by the inherited
containment rule. The highest set bit gives the last compatible region;
shifting by the current position and counting set bits gives the remaining
count. The table is computed from the fixed finite input graph, not supplied
as growing advice. It affects the offline finite compiler and does not grant
an online computed-address permutation.

Every chosen clearing still uses the original compatibility guard, exact
binary dependence, literal clearing XORs, recorded frame raises, and complete
arbitrary dirty wrapper. No existing source, requested output, or scalar
graph node is dropped. The graph, original envelope family, and underlying
compiler are credited to pinned public PR55/57/58; the future accessibility
selection and inverted-bitset compiler experiment are new to this branch.

## Independent local geometric discriminator

The standard-library checker `code/check_borrowing_guards.py` constructs the
actual rational space E(C,U) directly from

    support(x) subset U, x_i=t for i in C, sum(x)=3t.

It checks all 26,525 ordered frame pairs at dimensions four and five. Every
mask-containment accepted by the compiler implies inclusion of the actual
rational spaces. Some additional exact inclusions occur for a two-point core
with a three-point cover: that one-dimensional space is the same positive
triple line for every choice of the two-point core. Those special frames are
absent from the completed 23-axis word, so this simple canonicalization cannot
improve that word's legal accessibility set.

The checker also gives an explicit terminal-guard counterexample. The current
frame `(C={0,1},U={0,1,2,3})` lies in the proposed borrowing frame
`(C={0},U={0,1,2,3})`, but the latter cannot return by a monotone raise to the
original terminal frame. Vector `(1,0,0,2)` belongs to the borrowing frame
and violates that terminal frame. A separate four-role exact XOR test shows
that omitting the first dirty scatter contaminates the target, while omitting
the final injection leaves scratch unrestored even when the target is correct.

These local checks do not substitute for native address execution. The
all-size transfer must exhibit common frame assignments for the entire dirty
wrapper and preserve the paid center, data, endpoint, and cleanup profiles.
The campaign's inverse agent is independently constructing that schedule.

## Reproduction

Use `code/future_horizon_variant.py` with the same fresh public execution-copy
procedure as [reproduce.md](reproduce.md), and `--h 23 --policy last-compatible`.
Use `--policy remaining-compatible` for the changed continuation. The driver
verifies the pinned base compiler hash and writes the exact generated source,
word, and compact receipt. `configs/future-horizon-h23-20261008T182100Z.json`
and its 25-axis counterpart record the first pair; the separate future-count
protocols record the continuation.
