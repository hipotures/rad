# Duplicate gates on actual enlarged positive frames

The new construction applies the retained RaD delayed-clone idea to the
backward-positive address frames of icekylinx PR36 and the new reflected
producer DAGs. The positive frames are larger than their original scalar
envelopes; they are inherited literally, rather than recomputed or silently
replaced by original E(C,M). The exact finite search is in
`code/positive_clone_search.py`.

Let x=a+b be a gate with at least two result-carrier chains. Let one complete
chain start at consumer f, whose actual nondegenerate frame F contains the
frame of x. Assume a second gate g before f consumes b, both x and g have
unused retained-input capacities, and the frame of g lies in F. Duplicate
x immediately before f, assign its gate frame F, move the whole selected
result chain to the duplicate, retain a from x to the duplicate and retain
b from g to the duplicate. Either operand can take the x-provider role.

All scalar values induced by source injection are unchanged: the new gate
adds the same two operands and every moved consumer receives the same sum.
Its inputs' source spans lie in F. The original and provider retained
physical frames grow into F; every later use in the moved chain contains F
because it was an actual increasing controller chain. Frames for all old
gates remain unchanged. Nondegeneracy follows because F is an existing
positive frame. Reversing physical chronology and taking orthogonal
complements gives the other invocation orientation.

Every selected batch uses two distinct unused gate capacities per clone;
batches additionally forbid parent/child conflicts between selected
duplicate gates. Each old parent retains another result-chain start. This
supplies a feasible explicit compiled plan with one new gate and two new
links per duplicate, hence one fewer physical role. The new native
compiler may find further valid links, but those are separately charged and
checked by the independent physical compiler.

The arbitrary-dirty contract does not presume that the old and duplicated
gate values agree on an arbitrary initial scratch vector. For the resulting
invertible mixer L it requires the separately checked source relation
JLV=I. The transparent chronological word cancels JLq against JL(q+Vx),
restores q, and applies the source shear. Transposing every elementary
operation and reversing the whole word gives the opposite bank shear.
Complete small dirty controls, including a genuine nonempty cloned batch,
are required separately from this induction argument.

Designated retained totals are excluded from duplication because each has
one distinct terminal use and no later producer incidence. Thus all h
retained centers keep rank h-1, terminal scalar reads and paid copy/cleanup
costs. Source triples, designated target maps, the paid rank-one two-stage
endpoint correction and the source geometry are unchanged. New additions,
role volume, child ranks, row reserves and literal scalar precision guards
must nevertheless be charged in the composed recurrence.

The initial accepted finite candidates have h23 R36,363 (322 duplicates)
and h25 R48,104 (275 then 100 duplicates), improving the reflected parents
by exactly those duplicate counts. Their exact independent scalar,
rational-frame, reverse-complement and positive rank timelines are retained
in `results/cloned-independent-check.json`. The generic mixed-width moment
is evaluated by the coordinator separately. The eventual common basis,
finite alphabet, setup, analytic/tape and strict absorption conditions
remain conditional interfaces; this lemma is not an unconditional integer
multiplication theorem or formal verification.
