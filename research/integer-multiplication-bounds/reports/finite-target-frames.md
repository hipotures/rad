# Positive frames defined by descendant targets

This experiment enlarges support frames using physical output constraints.
The finite graph and retained-controller algorithm are unchanged. The aim is
to see whether cancellation among coordinates can permit more controller
reuse while keeping every frame nondegenerate, all transitions nested, and
the physical source/target endpoints correct.

## Maximal descendant-target family

For a node, let C be the intersection of its formal source triples. Each
descendant partial output is indexed by a common point c and a physical
target triple T. Since the original map is cancellation free, c belongs to C
and T meets the union of this node's sources exactly at c. In particular,
T meets C once.

Let E(C,[h]) consist of vectors x whose coordinates on C are all z and whose
total coordinate sum is 3z. Define

`U(C,D) = E(C,[h]) ∩ ⋂_{T∈D} T^⊥`,

where orthogonality is for H=I-J/9 and D is the set of descendant physical
targets. For a target meeting C at c, its equation becomes `x_a+x_b=0` for
the other two target points a,b. These excluded-pair equations are represented
by an undirected graph on the coordinates outside C. An odd component forces
all its coordinates to zero; each bipartite component allows one alternating
signed parameter. Isolated vertices allow independent parameters.

The family is positive, because on E(C,[h])

`xᵀHx = ∑_{i∉C} x_i² + (|C|-1)z²`.

For |C|=1, vanishing outside coordinates also forces z=0 by the total-sum
relation. For |C|≥2, the displayed form is plainly positive on every nonzero
vector. The family contains the original source span. It nests along every
original DAG edge: the core shrinks toward a parent gate, while the set of
descendant targets shrinks. Thus both defining systems relax.

At an input triple S, all excluded pairs outside S occur among its descendant
targets. They form the complete graph on h-3≥3 vertices, whose odd cycles
force all outside coordinates to zero. Its frame therefore collapses to the
original triple line. This is checked explicitly for every source, including
the large experiment, rather than used as an unchecked endpoint assumption.

## A selected interpolation

Enlarging a gate's frame can help a later controller use, but also imposes a
larger obligation on subsequent uses. To avoid adding every available
direction, a second family starts from the positive support envelope E(C,V)
and considers a fixed matching of point pairs.

For a selected pair {a,b}, add the difference direction `e_a-e_b` only when
a,b lie outside C and every descendant target contains both or neither.
This direction has zero total sum, zero core coordinates and zero H pairing
with every descendant target. It belongs to the positive E(C,[h]). Its
availability persists toward parent gates, so the enlarged frames remain
nested. The sum of the original support envelope and all available matching
directions is therefore a positive admissible frame family.

At an input S, a selected pair meeting S is rejected by the core condition.
If both a,b lie outside S, choose any point d outside S∪{a,b}; one exists for
h≥6. A target {s,a,d}, with s∈S, descends from this input and contains a but
not b, so that difference is unavailable. The source frame again remains
exactly its triple line. All source lines and all physical output pairings
are checked in the implementation.

Because the selected pairs are disjoint, the resulting coordinates have a
simple exact description. A pair with one point already in V adds the other
point as a free coordinate; a pair with both points outside V adds one signed
two-coordinate component. This fits the same rational constraint checker.

## Small measured results

| h | Precompile R | Exact source span R | Support envelope R | Maximal target frame R | Selected aligned/shifted R |
|---:|---:|---:|---:|---:|---:|
| 6 | 162 | not compared here | not compared here | 150 | not screened |
| 8 | 792 | 768 | 696 | 792 | 696 |
| 12 | 4140 | 3936 | 3864 | 4104 | 3864 |
| 50 | 494250 | 487650 | 486200 | 493950 | 486200 (shifted) |

The maximal family passes the mathematical checks but loses reuse at h=8 and
h=12 and h=50. The matching interpolation preserves the support-envelope counts for
both aligned and shifted matchings at the small sizes and for shifted matching
at h=50. Neither is an established
improvement over the support-envelope compiler.

The maximal-family independent checks include 122/632/3340 positive exact
Gram matrices at h=6/8/12, source containment at every active node, and
1278/2799/10939 independently eliminated rational inclusion pairs. Every
small maximal candidate and the selected aligned/control candidates passed
dirty scratch in both orientations on every basis input. Selected aligned
h=8 has a further independent check of 608 positive Grams, 680 source spans,
and 2755 rational inclusion pairs.

Witnesses are [h6 maximal](../runs/20261007T231650Z-finite-target-frames-small/results/certificate.json),
[h8/h12 maximal](../runs/20261007T231730Z-finite-target-frames-dirty/results/certificate.json),
[support control](../runs/20261007T232130Z-finite-selected-frames-control/results/certificate.json),
[selected aligned](../runs/20261007T232145Z-finite-selected-frames-aligned/results/certificate.json),
and [selected rational check](../runs/20261007T232330Z-finite-selected-frames-rational/results/certificate.json).

## Exact implementation and scalable checks

[finite_target_frames.py](../code/finite_target_frames.py) encodes each basis
column by a core coefficient and signed coordinate masks. Its inclusion
predicate tests all defining equations of the candidate containing frame.
[finite_selected_target_frames.py](../code/finite_selected_target_frames.py)
implements the matching interpolation.

The first h=50 attempts spent minutes in per-column inclusion checks and
were deliberately interrupted before a complete certificate was produced.
Their small results remain retained. The scalable implementation
[finite_fast_target_frames.py](../code/finite_fast_target_frames.py) compares
the symbolic coefficient vector of each coordinate simultaneously, reducing
the work per inclusion from a product of frame dimensions to a scan of the
containing frame's components. Its signed-graph implementation stops early
only after every incident vertex has been proved to lie in an odd component;
remaining edges can no longer change the solution space.

The fast and direct implementations agree on 480 seeded signed graphs across
h=6,8,12,50 and 10000 seeded frame-inclusion pairs at h=8. The
[replayable equivalence check](../runs/20261007T232500Z-finite-target-fast-replay/results/certificate.json)
records seed 109 and both source hashes. Fast selected h=8 also independently
passes the dense rational and dirty-scratch checks in
[this fresh run](../runs/20261007T232530Z-finite-target-fast-rational/results/certificate.json).

The compiler and scalar verifier are imported without editing their files.
A process-local predicate binding substitutes the new exact rational frame
inclusion relation; all original scalar/frame checks still execute. Results
record every imported source hash, Python/NumPy/SciPy versions, reference
commit, matching seed, topological schedule digest and compiled scalar digest.
No three-stage multiplication transfer is claimed by these finite witnesses.

The h=50 maximal-family run finished in 117.6300 seconds for rank and random
seed 109; both selected 300 links. The independent support-envelope control
finished in 66.7304 seconds and selected 8050 of 13700 candidate links. The
shifted matching adds 2375 frame dimensions in total but leaves those counts
unchanged, finishing in 67.1401 seconds. All 19600 input lines, every original
edge, all compiled scalar coefficients, both compiled frame directions, and
2763600/2764800/2822400 output basis pairings were checked. Witnesses are
[maximal h50](../runs/20261007T232600Z-finite-target-fast50/results/certificate.json),
[control h50](../runs/20261007T232615Z-finite-target-fast50-control/results/certificate.json),
and [shifted h50](../runs/20261007T232630Z-finite-target-fast50-shifted/results/certificate.json).

## Complete-support certificate and dominance within the core family

A final intermediate family keeps E(C,V*) with V* equal to all points minus
all descendant excluded-pair endpoints. This discards alternating target
directions and adds only unused positive coordinates. Since descendant target
sets shrink toward parents, V* grows, so it is nested and positive. The
[implementation](../code/finite_completed_support_frames.py) checks V⊂V*,
source lines, physical target pairings and the complete compiled frames.

At h=8, h=12 and h=50, V*=V at **every active node**: no coordinate is added.
The complete h=50 check therefore reproduces 486200 roles. The
[small independent dirty checks](../runs/20261007T233050Z-finite-support-completion-small/results/certificate.json)
and [full h50 witness](../runs/20261007T233100Z-finite-support-completion50/results/certificate.json)
preserve this exact completeness property, not merely an unchanged role count.

This property proves a stronger, fixed-graph negative result. Suppose each
proposed frame U_n contains its original source span, lies in E(C_n,[h]),
and is orthogonal to every descendant physical target. If a retained link
requires U_a⊂U_b, every original nonnegative triple indicator from a belongs
to U_b. Its total coordinate sum is 3, so the E(C_b,[h]) equations force
every coordinate of C_b to equal 1; hence C_b⊂C_a. For each descendant
excluded pair at b, its two coordinates must sum to zero. Since the triple
indicator is nonnegative, both coordinates must be zero. Thus its support
lies in V*_b=V_b, giving V_a⊂V_b. These two conditions imply
E(C_a,V_a)⊂E(C_b,V_b).

Consequently, at any fixed legal schedule, the support-envelope family admits
every controller link admitted by this entire larger core-constrained family.
Its maximum-flow optimum cannot be improved by choosing other frames inside
that family. This does not establish an optimum over arbitrary schedules,
graphs, or nondegenerate frames without the core total-sum restriction.

## Reproduction

Use the pinned topic math environment and one BLAS/OMP thread per process.
The reference is `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`. Each invocation
below needs a fresh output path.

```bash
python code/finite_target_frames.py --reference "$REF" --h 6 8 12 \
  --modes rank_id,rank_random --seeds 109 --independent --dirty \
  --output "$FRESH_RUN/results/certificate.json"
python code/finite_fast_target_frames.py equivalence --reference "$REF" \
  --seed 109 --samples 10000 --output "$FRESH_RUN/results/certificate.json"
python code/finite_fast_target_frames.py maximal --reference "$REF" --h 50 \
  --modes rank_id,rank_random --seeds 109 \
  --output "$FRESH_RUN/results/certificate.json"
python code/finite_fast_target_frames.py selected --reference "$REF" --h 50 \
  --pair-mode none --output "$FRESH_RUN/results/certificate.json"
python code/finite_fast_target_frames.py selected --reference "$REF" --h 50 \
  --pair-mode shifted --output "$FRESH_RUN/results/certificate.json"
python code/finite_completed_support_frames.py --reference "$REF" --h 8 12 \
  --pair-mode none --independent --dirty \
  --output "$FRESH_RUN/results/certificate.json"
python code/finite_completed_support_frames.py --reference "$REF" --h 50 \
  --pair-mode none --output "$FRESH_RUN/results/certificate.json"
```
