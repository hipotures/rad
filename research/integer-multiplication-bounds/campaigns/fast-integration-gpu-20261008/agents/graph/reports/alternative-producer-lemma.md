# Alternative producers on inherited positive frames

This extends the whole-chain duplicate construction in
[positive-clone-lemma.md](positive-clone-lemma.md). It changes the producer's
source partition as well as its retained controllers. The finite heuristic is
`code/alternative_producer_clones.py`; it does not solve a global minimum
support-cover problem.

Let an existing gate x have at least two result-carrier chains. Choose one
complete chain whose first consumer f has positive frame F. Let earlier
nodes y,z have disjoint integer source-coefficient supports whose union is
the support of x. Require a gate g1 consuming y and a distinct gate g2
consuming z, both with unused retained-input capacities, occurring before f
and having frames contained in F. Create x'=y+z immediately before f,
give it the literal frame F, move the entire chosen chain from x to x', and
retain the appropriate operand from g1 and g2 to the new gate.

The search explicitly excludes the original two-operand partition of x.
Consequently a selected edit tests a new factorization through existing
intermediate forms. Exact disjoint coefficient supports imply equality of
x and x' under source injection over the integers; no equality on arbitrary
initial dirty scratch is assumed. All old gates retain their scalar form
and actual frame. Each new operand's span lies inside its provider frame
and therefore inside F. All later frames of the moved chain contain F.

Batch capacities are disjoint. Selected parents retain at least one old
result-chain start, and a conservative selected-parent/formal-component
exclusion prevents a batch from moving the new producers' operand chains.
Every old selected retention is preserved after the explicit relabeling.
The constructed witness adds one gate and two valid retention links per
new producer, reducing role count by at least one per edit. A fresh native
matcher may improve this witness; every additional retention and its real
rank transition is checked separately by the independent physical compiler.

Producer coefficient partitions are exact over the integers. The packed
dirty-memory checker implements the scalar mixer and target scatter over
F2 and verifies JLV=I over F2; it does not assert an integer scatter identity.
For this invertible mixer L, the transparent word restores arbitrary
scratch and implements the source shear; the transpose of every elementary
operation in reverse chronology supplies the opposite invocation. The
finite checker separately reconstructs all gate, copy, cleanup and terminal
roles, source/target coefficients, rational nondegenerate frames and both
chronological frame directions.

The h10 control genuinely adds five alternative-partition gates after six
whole-chain duplicates. It lowers R1809 to R1804 and passes the complete
dirty basis in both directions. Selected h23 and h25 candidates add 377 and
596 alternative producers, reaching positive-frame R36015 and R47429. Both
independent compiled audits pass. Fresh source-only recovery of all h10,
h23 and h25 selections has also passed with identical DAG, frame and
selected-link digests.

Retained centers have one designated terminal use and are never eligible
parents. All h centers remain paid rank-(h-1) copies. Source triples, target
scatter and the paid endpoint corrections remain the original maps. A
fresh ORIGINAL E(C,M) matching is required before these edited scalar DAGs
can be used with fixed I+J matrix profiles; their positive-frame role counts
must not be substituted into that interface.

Public copied-center, prefix/suffix and paired-circuit mechanisms are
credited to their pinned upstream sources. The new edit is this alternative
factorization combined with inherited actual positive frames and two
arbitrary unused controller capacities. No worldwide priority claim is
made. General basis, finite alphabet, setup, analytic/tape and strict
absorption conditions are still the campaign's conditional transfer
interfaces, not consequences of the finite witness alone.
