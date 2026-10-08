# Independent proof review: clones with unused capacities

The sufficient clone construction is valid: one additional cancellation-free
sum can add two controller links and remove one physical side role while
preserving the scalar map, rational envelope family and complete dirty-scratch
interface. The recorded h51 batch has 1,431 such clones and algebraically
supports R=500703. Its complete changed-DAG/physical promotion is a separate
root-owned check; the audit reported here does not duplicate that replay.

This is a new graph, not merely a different flow score for an old graph.
Maximum-flow optimality of the recovered plan is unnecessary. The proof
uses the existing retained-controller compiler and the previously accepted
rational envelope and whole-invocation transfers.

## Sufficient edit and preservation of every old link

Let P add formal values A and B. Assume that P's outgoing value has at
least two controller chains of uses, and neither incoming use at P has a
selected outgoing controller link. Let Q be an earlier gate with unused
controller capacity, containing a use of the same formal B, whose frame
is contained in P's frame. Insert an explicit duplicate P' of P, with the
same two formal children, and move exactly one *whole* output chain of P
to P'. Add a link from the A use at P to the fresh A use at P', and from
the B use at Q to the fresh B use at P'.

Both newly used gate capacities were free, and both new recipients are
fresh. The A value is retained at P; B remains a terminating input and
can supply P's result pivot. At P' both incoming uses terminate, so P'
also has a result pivot. Q retains at most one input. Each addition thus
continues to have the terminating pivot required by the reversible compiler.
The clone's outgoing result links are distinct from its incoming controller
uses; they do not silently consume a second incoming controller capacity.

Old links inside the moved output chain now have P' as their formal source
at both ends. Links in the other chains still have P at both ends. No
chain is split by the move. Moving only its first use would leave an old
link with unequal formal source IDs; the independent negative control
rejects this. At least one original P chain remains and at least one P'
chain exists, so both additions stay active. Explicit duplicate node IDs
must not be re-interned merely because their scalar supports agree.

For a batch, the sufficient conflict rule makes all capacity sets {P,Q}
pairwise disjoint and forbids a selected clone parent from being an original
formal input of another selected clone parent. This ensures that each
new A/B link still refers to the same mapped formal child on both ends.
All moved chains are complete, so any other rewiring preserves old source
equalities. The recovered selected plan itself should still be audited;
the sufficient conflict rule is not a substitute for checking its actual
links and per-gate capacities.

## Chronology and frames

The execution order is the canonical `(frame dimension, explicit node ID)`
order. P' has P's frame and is inserted immediately after P's ID.
The original rank order of mapped nodes is preserved. Q was earlier in
the original use order; its frame is contained in P's, so the new link
still precedes P'. This argument permits Q's raw original ID to be larger
than P's when Q has a smaller frame dimension; raw node-ID order alone
is not the actual controller schedule.

Every original node retains its old envelope E(C,V), and each clone has
its parent's envelope. A rewired child has exactly the old formal scalar
value, core and support. Thus all union/intersection recurrences and
canonical envelope fields remain valid. A child's frame is contained in
its parent's, and equality of dimensions is resolved by the preserved
topological ID order. The P->P' retained use has an equal frame and zero
residual; the Q->P' retained use has a nested frame. Zero frame changes
are allowed. The source-copy injection still starts from the original
triple line.

The positive restricted rational envelope form remains

`sum_(outside core) x_j^2+(|core|-1)z^2`.

Its nondegeneracy, inclusion proof and target orthogonality do not depend
on how many identical sums are present. Every designated output retains
the same envelope and target intersection condition. Reversing the mixer
uses orthogonal complements: `U subset V` becomes
`V^perp subset U^perp`, with the same nondegenerate difference. Consequently
the unchanged forward and reverse physical-frame checks are the right
checks for this changed program.

The bit address table is a new finite collection of edges and may require
the usual new fixed odd-prime/factor-table selection. This is an eventual
fixed setup constant, not a variable per-call basis adapter. When the global
axis construction is composed, conjugate this entire new collection once.
The separate complex arithmetic circuit and its numerical constants are
not changed by cloning this bit mixer.

## Complete invocation and rank accounting

The compiled mixer L is a reversible linear map on all its physical slots.
Its zero-scratch source coefficients determine JLV, but its internal scratch
slots may be arbitrary during the complete invocation. The accepted
transparent schedule uses the difference

`J*L(a+Vx)-J*L(a)=J*L*Vx`.

It runs the same L and its exact inverse around both target passes, and
undoes V at the end. Therefore arbitrary dirty scratch contributions cancel
and the original scratch values return exactly. The cloned DAG changes L,
but preserves its source-to-target scalar map and reversible structure, so
this identity remains valid for the new L. Equality of scalar supports is
not an assumption of zero intermediate scratch.

The full data/center identity shear and odd matching use the same external
input/output partial maps. First/third bank sharing and their complementary
endpoint labels still apply with the new role count R. The side histories
are monotone in the same envelopes and reverse complements. Their dimension
changes telescope; new intermediate nodes do not create extra nonmonotone
decreases. The data negative-source correction remains one rank per X
source in stage1. Thus the original closed rank formula is retained:

```text
N=v^3, m=h^3
W=2N+2v^2(R+h)
L=3v^2h^2
D=N-2L
s=W*m-D.
```

This statement concerns the complete changed physical program, not the
unproved interpretation of a favorable local addition count. The root's
independent full reconstruction checks the actual histories, designated
targets, compiler hash and representative dirty invocations.

For c binary additions, q partial outputs and ell selected links, the
compiler allocates `R=c+q-ell`. Each clone adds one logical addition,
two fresh incoming uses and two selected links; q is unchanged. Its role
change is exactly +1-2=-1. One new link would merely pay for the new
addition and save no role; that negative control is retained.

## New exact operation guard

In one forward L, every addition costs one scalar update. The total
number of output-copy updates is R-v: the number of chain starts minus
the number of active logical nodes equals
`(2c+q-ell)-(v+c)=R-v`. Thus L uses exactly `c+R-v` scalar updates.
There are four L/inverse passes, two J passes with 3v outputs each,
two V passes with v inputs each, and the unchanged central gathers and
scatters with 12v updates in total. One invocation therefore has

`G_invocation=4(c+R-v)+20v`.

For the three tensor stages, `G=3v^2*G_invocation`. This is recomputed for
the changed DAG. An old gate-count shortcut is not inherited merely because
the frames are equal.

The recorded h51 values are

```text
v=20825, c=474540, q=62475, ell=36312, R=500703
G_invocation=4234172
G=5508835077952500
W=452397413413750
s=60010967023368169375
D=2263379181875.
```

The exact conservative elementary-operation guard
`E=64(W+m+1)^3` exceeds `2GW^2+4s+4W+4` by

`3670794861655268745434778017984148373367443208`.

This is fixed finite-operation accounting for the new bit program. The
separate selected h28 complex circuit supplies its own unchanged numerical
semantic guard; this bit G must not be substituted into that complex
computation without a distinct construction.

## Independent recorded audit and scope

[review_clone_proof.py](../code/review_clone_proof.py) imports no cloner,
optimizer or producer accounting function. It checks all 1,431 explicit
jobs for 2,862 disjoint P/Q capacities, selected-parent/formal-child
conflicts and fresh input-position descriptions. It checks all 36,312
recorded integer links for unique first uses, unique recipients and
chronology, verifies descriptor and node counts, and recomputes the
role identity, every category/histogram rank sum, literal G and guard
slack. Partial-chain, double-retained-input and one-link/no-saving negative
controls discriminate the necessary structural premises.

The fresh [run](../runs/20261008T0517Z-review-clone-proof/protocol.json)
was terminal PASS in 0.25 seconds, Python 3.14.7, one CPU worker,
30,860 KiB RSS and no swap. Its owned reservation was released in finally.
Its inputs are the immutable clone certificate, selected-link export and
canonical-order metadata; their source/input digests and fresh command
are pinned in the protocol. Execute that command with a fresh output path.

This thin audit does not reconstruct actual formal sources, frame
inclusions or per-gate capacities from a giant DAG, and does not execute
a dirty basis. Those are the separate root-owned changed-witness checks;
no accepted baseline replay is required. The sufficient all-size argument
above is positive. A specific promotion and composed exponent must link
the completed independent changed-DAG certificate before becoming a headline.
Parent publication owns commit, push and remote verification. The original
campaign start, historical deadline and active user extension are retained.
