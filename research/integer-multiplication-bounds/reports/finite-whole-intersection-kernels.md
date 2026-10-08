# Whole intersection-one circuit with nondegenerate target kernels

A new cancellation-free circuit computes each whole intersection-one sum
`B_S = sum_{|T intersect S|=1} x_T` as one output. It supports an exact nested
frame family even when source spans are singular. At ground 50 it compiles
to **509,147 physical roles**, exceeding the reviewed partial-output recipe's
472,885 roles. This is a finite construction and a negative count comparator;
it is not a stronger multiplication bound.

The constructor recursively contracts global paired blocks. For each selected
vertex subset it computes the necessary degree/query deletion sum outside
the touched blocks, allowing full selected pairs as well as partial pairs.
Equal disjoint source supports are interned globally. The whole output
enumerates selected subsets meeting its target exactly once. Its exact
support partition is checked at every addition and every output.

The first frame hypothesis failed. A core-zero sum need not be supported on
fewer than nine coordinates: at ground 50 there are 27,600 such nodes with
no shared physical target point, and their source unions range from 48 to 50
coordinates. Ground-12 exact elimination also finds 125 singular actual
source spans. These failures are retained in the premise and actual-span
runs. Every examined core-zero descendant-target span nevertheless has rank
one or two and is positive definite, suggesting the successful replacement.

Use the rational form `H=9I-J` on an even ground `h>=6`. Its ambient form is
nondegenerate for the examined grounds. A node with nonempty source core uses
its exact common-point indicator span, which is positive: writing its common
coordinate as z gives `sum x_i=3z` and squared norm `9*sum_{i!=common} x_i^2`.
A node with empty source core uses `K = span(T)^perp`, where T is its complete
physical descendant-target family. This constructor checks that T contains
one or two triples at every such node.

For two distinct triple indicators with intersection r in `{0,1,2}`, their
Gram is `9*[[2,r-1],[r-1,2]]`; its determinant is positive. Thus every target
span is positive and every kernel is nondegenerate. When `h>9` each kernel
has one negative direction. In particular, disjoint target pairs are valid;
no shared target point is needed.

The frame inclusion rules are exact. Positive-to-positive inclusion uses the
original rational span test. A positive source span is contained in a kernel
exactly when every basis triple meets every target in one point. Kernel-to-
kernel inclusion reverses the target-span containment. The span of two
distinct constant-weight zero-one triple indicators contains no third such
indicator: coefficients must sum to one, and a differing coordinate forces
one coefficient to be zero or one. Target containment therefore reduces to
set containment. A kernel cannot lie in a positive common-point frame for
`h>9` by inertia; the small even grounds are independently checked. The
reverse false branch is not asserted for arbitrary odd grounds.

Original frame edges are nested because source cores can only shrink and
descendant families grow when traversing toward a child. Empty source core
propagates toward parents, so no original kernel-to-positive edge occurs.
At each input the frame is its exact triple line; each whole output has frame
exactly `t_S^perp`. Complements give nested reverse frames. The original
optimizer and compiler run without edits, under a process-local binding to
this exact inclusion predicate. A separate physical checker verifies both
input coefficients, every disjoint addition, fresh copy destinations and
every whole output.

| Ground | Additions | Whole outputs | Roles before reuse | Retained links | Physical roles |
|---|---:|---:|---:|---:|---:|
| 6 | 118 | 20 | 138 | 11 | 127 |
| 8 | 710 | 56 | 766 | 38 | 728 |
| 12 | 3,953 | 220 | 4,173 | 268 | 3,905 |
| 20 | 25,019 | 1,140 | 26,159 | 1,059 | 25,100 |
| 50 | 496,954 | 19,600 | 516,554 | 7,407 | 509,147 |

The small witness checks 3,537 independent restricted rational Grams and
10,471 exact inclusion decisions, including original edges, selected links
and seeded independent frame pairs. Complete forward/inverse dirty bases
cover 173, 848 and 4,357 coordinates at grounds 6, 8 and 12. Two complete
ground-6 shared three-stage exchanges also pass. The large witness checks
all 63,562,800 nonzero whole-output coefficients and every physical/frame
transition at ground 50 in 45.05 seconds. Its 159,700 kernel nodes comprise
113,400 one-target and 46,300 two-target nodes, including 27,600 disjoint
two-target cases. There are also 356,854 positive nodes.

These results verify the finite mixer and its nondegenerate flags. Extending
the written motif rank and stage-sharing argument to this changed output
interface still requires a separate acknowledgement. The standard transfer
uses nondegeneracy and nested projectors, rather than positivity itself;
the finite construction preserves exact source-copy lines, output target
orthogonality and arbitrary scratch restoration. No new final kappa is
claimed, and the count is already worse than the accepted circuit.

Reproduce with the pinned math environment and immutable upstream using the
exact commands in each run protocol and fresh output paths. Sources are
[whole-map constructor](../code/finite_intersection_blocks.py),
[failed premise screen](../code/finite_intersection_frame_screen.py),
[actual-span control](../code/finite_intersection_span_control.py), and
[target-kernel witness](../code/finite_intersection_target_frames.py).
The [small](../runs/20261008T023552Z-finite-intersection-kernels-small/) and
[full](../runs/20261008T024228Z-finite-intersection-kernels-full/) certificates
are compact. The complete actual-span row certificate remains externally
recorded by its protocol and compact summary; its intact gzip publication
and recovery pointer must be supplied by the campaign coordinator before
claiming those full rows are preserved in Git.
