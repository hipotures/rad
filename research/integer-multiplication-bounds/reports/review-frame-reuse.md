# Independent review of increasing-frame controller reuse

This report reviews the campaign's `frame_reuse.py` compiler against the
actual paired transfer at pinned revision
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`. Campaign interval:
2026-10-07 22:25:21 UTC to 2026-10-08 08:25:21 UTC.

## Transfer argument

The proposed reuse is valid under its explicit constraints. A retained
controller keeps the same logical circuit value across uses. It is not
overwritten by its previous gate. An addition has at least one incoming
role whose last use is that gate; that role supplies the result pivot.
The other role may remain available, and extra outgoing copies use fresh
roles. The scalar gate is an invertible sequence of additions and copies.
No two simultaneous inputs coincide.

For a logical wire `z`, let its consecutive retained uses be gates
`g1,...,gk`. The controller role has the sequence of rational frames
`U_z, U_g1,...,U_gk`. Reuse is permitted only if each successive gate
span contains the preceding one. Child spans already lie in their parent
gate span, so the terminating pivot role also has an increasing frame.
At a gate, assigning its single common frame to every incident role is
valid. All frames still have a common point and are nondegenerate by the
paired norm identity. A controller need not follow a directed dataflow
path; increasing frames, rather than the old path description, are the
property that the revised proof must state.

Reverse the physical role sequence and use orthogonal-complement frames.
If `U_gi subset U_g(i+1)`, then
`U_g(i+1)^perp subset U_gi^perp`. The original output line is contained
in the starting complement, and the final complement at an original input
is its physical source complement. This verifies the reverse middle
computation without assuming that descendant target spans are positive.
Newly activated roles enter from the broad base frame and retired roles
grow to the broad final frame, as in the original invocation.

The arbitrary-dirty-scratch schedule works for every invertible mixer `L`
realizing `J L V`: early and late injections contribute
`J L z + J L(z+Vx)=J L Vx` in characteristic two. Its inverse mixers
and final copy restore `z`. Consequently controller reuse introduces no
new scalar restoration condition. It changes the finite mixer and role
count, whose common-frame and endpoint proof must be supplied explicitly.

There are `2c+q` uses before identification. The original `c` pivot
identifications and the selected controller links each remove one physical
role. Thus `R=c+q-links`. Outputs remain distinct. With monotone side
frames, central returns remain the only decreases; the original rank
telescoping and source correction apply after substituting this actual
physical role count. The stage-sharing bijection and joining frames are
independent of the internal role path and retain the same role index.

More explicitly, user occurrences form disjoint forward chains. Each selected
link removes one chain start. Input nodes allocate one role per remaining
start; addition nodes allocate one fewer because the consumed pivot supplies
the first outgoing role. Hence the total is
`(2c+q-links)-c`. The unit capacity per addition permits at most one
retained incoming role, leaving a terminating pivot. Increasing user order
prevents a cycle or a missing first chain start.

A controller chain that terminates at a designated output is checked against
that logical output's own span `U_z`, rather than merely its last use gate.
The wire span lies in every use-gate span; the final inclusion in `U_z`
therefore forces equality of these spans. Thus an enlarged controller frame
cannot silently reach an output whose valid frame is smaller. Distinct output
users have distinct physical roles, and a completed output role is not used
as a controller later in the schedule. Ordinary fresh output copies receive
the node's own common frame. The source-span neighbor condition then gives
the same inclusion in the physical target complement as the baseline.

These statements justify this compiler ansatz. They are not a lower bound
or a claim that its maximum-flow solution optimizes all reversible circuits.
The upstream general transfer remains conditional as before.

## Independent exact checks

For triples with common point `i`, delete coordinate `i`. Their rational
indicator vectors become signless edge vectors `e_a+e_b`. A connected
bipartite component has the single signed-sum constraint; a connected odd
component spans every active coordinate. Reattach the common coordinate
as half the sum of the other coordinates. This argument is over `Q`:
an odd triangle has determinant two, and its conclusion cannot be inferred
from characteristic-two elimination.

The authored checker `review_frame_reuse.py` validates the compiler's
signless-graph representation with independent `Fraction` elimination.
It checks all nonempty source subsets at `h=5` and fixed-seed samples at
`h=6`, including span inclusions between different common points:

| Check | Count |
|---|---:|
| Source/canonical span equivalence | 3,315 |
| Exact rational containment comparisons at h=5 | 27,225 |
| Exact rational containment comparisons at h=6 | 10,000 |

Every canonical frame also passes an exact rational Gram-rank test.

For the rank-order global `h=6` candidate, the compiler has 150 physical
roles and 12 retained-controller links. The independent checker expands
the complete elementary side invocation on all 190 scalar basis vectors,
including every arbitrary dirty role. The logical neighbor shear is exact,
scratch is restored, and the transposed reverse schedule implements the
opposite neighbor shear. It independently verifies 708 physical frame
transitions by rational elimination, rather than using the compiler's
symbolic inclusion function.

The all-size transfer argument above is separate from these finite tests.
Larger finite graph counts and endpoint/rank certificates are owned by the
parent campaign; this report does not substitute the small check for them.

The same independent full-basis check also passes at `h=8` and `h=10`:

| h | Roles | Scalar basis vectors | Physical frame checks |
|---:|---:|---:|---:|
| 6 | 150 | 190 | 708 |
| 8 | 768 | 880 | 4,032 |
| 10 | 1,870 | 2,110 | 10,420 |

Both shear directions restore all scratch in every case.

## Reproduction

From the topic's `code` directory, in the campaign's pinned math environment:

```bash
PYTHONDONTWRITEBYTECODE=1 python review_frame_reuse.py --reference "$REF" --h 6 --output "$OUT"
PYTHONDONTWRITEBYTECODE=1 python review_frame_reuse.py --reference "$REF" --h 8 --skip-census --output "$OUT"
PYTHONDONTWRITEBYTECODE=1 python review_frame_reuse.py --reference "$REF" --h 10 --skip-census --output "$OUT"
```

The construction imports `frame_reuse.py`, `finite_block_search.py`, and
the pinned reference constructor. Independent scalar and rational checks
use the authored review code. Compact evidence and source hashes are in
`runs/20261007T225800Z-review-frame-reuse/`.
