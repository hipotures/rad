# Physically common target kernels

The safely indefinite target-kernel family extends beyond nodes whose
designated common point is unique. If all actual descendant target triples
share any coordinate, their span is positive under9I-J. Its orthogonal
complement is nondegenerate and has one negative direction for h>9.
This allows some shared pair-star nodes to be widened safely.

For example, designated targets {c,a,b} and {d,a,b} have designated common
points c,d but actual shared coordinates a,b. The common-point positivity
argument applies at a or b. This is a mathematical extension, not evidence
that the larger family necessarily improves a physical circuit.

## Exact construction

Compute the intersection J(n) of every descendant physical target by
reverse DAG propagation. For child->parent, J(child) is contained in
J(parent). If J(n) is nonempty, select its first coordinate and reconstruct
the exact target span from local outputs and canonical target-span bases
propagated from parents. Re-encoding each parent basis at the child's
shared coordinate preserves the exact rational span. The builder asserts
that the canonical basis intersection equals J(n), the original source
envelope is contained in the kernel, both optional frame families nest on
all original edges, and every input remains its original triple line.

This avoids full C(h, 3)-bit descendant-support sets in the scalable
constructor. The independent small checker does use original physical
descendant triples, reconstructs their rational spans, and compares all
frame Grams and sampled/edge inclusion decisions with dense elimination.

## Small discriminating result

At the default paired ground 12 graph, 3054 nodes have a physically common
target span, versus2988 in the designated-common family. The additional66
nodes all have two designated and two physical common points. However,
they create no new controller candidates: the union remains552 candidates,
348 relevant frame variables, 96 nesting constraints and 282 selected links.
The optimized R remains3858, with 276 chosen wide nodes. HiGHS reported a
closed optimum and the recovered integer constraints passed.

The independent exact audit checked 4378 distinct frame Gram matrices,
3054 original descendant-target spans and 16564 rational inclusion
decisions, seed109. Both complete 4310-coordinate dirty side-invocation
maps passed. Total elapsed time was28.493 seconds.

The first attempt additionally requested complete ground 12 three-stage
exchange. It exceeded its180-second process-group limit after construction
and the independent phase; the original source, log, protocol and timeout
remain unchanged. Its repair retained the same source and omitted that
expensive whole-motif scalar calibration. The repair is complete for its
stated Gram/map/frame/dirty scope. No three-stage result is claimed from
the timed-out attempt.

## Interpretation and next test

These 66 particular alternatives are irrelevant to the fixed schedule's
controller optimization. That is a finite negative for this graph and
schedule, not a general exclusion of the mathematical family. Asymmetric
singleton orders may create shared nodes with one physical common point
and two designated common points, whose larger kernels can admit new
retained links. The next cheapest test uses an early singleton in only one
common-point group, compares the old and new candidate sets, then runs a
full ground only if the count changes.

The authored source is
[finite_physical_target_kernels.py](../code/finite_physical_target_kernels.py).
The completed result is
[the ground12 audit](../runs/20261008T010729Z-finite-physical-kernels-audit/results/certificate.json).
The scoped timeout is
[the original protocol](../runs/20261008T005914Z-finite-physical-kernels-small/protocol.json).
Both runs preserve exact commands, source/input identities, UTC times,
bounded resource policy, logs and recovery instructions.

Representative reproduction with BLAS/OMP threads1 and a fresh output:

```bash
python -B code/finite_physical_target_kernels.py --reference "$REFERENCE" \
  --h 12 --time-limit 60 --independent --dirty --output "$FRESH_RESULT"
```

No exponent improvement is attributed to this broadened family. A changed
full graph would still require physical coefficients/frames/targets,
nondegenerate rank transfer, stage joins and separate analytic composition.
