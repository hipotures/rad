# Followup: independent promotion of delayed-frame clones

The delayed first-consumer-frame h51 witness with 16,454 clones and
R485680 now has both the frozen
[all-size frame, capacity, invocation and guard proof](review-descendant-clone-frames.md)
and the root-owned full independent changed-DAG audit. This fresh
followup records acceptance without changing the earlier proof bytes.

The full audit is
[run20261008T060418Z-review-descendant-clone-repair](../runs/20261008T060418Z-review-descendant-clone-repair/protocol.json)
and its [certificate](../runs/20261008T060418Z-review-descendant-clone-repair/results/certificate.json).
Its candidate identity is
`5ca948ed6bd951f011d325627ca1730e4268aa63695cabcdbb59840b36dbb513`,
and the compiled hash is
`eb34b7ccee4439e5758643b25cc81260442a8723e5987b3d7f97b0b74ef1422f`.

The reviewer reconstructs the changed DAG and consumes the actual
saved 66,358-link plan and 16,454 placement/frame-owner triples. It
imports no clone producer and replays no accepted baseline physical
program. It verifies all 70,471,800 nonzero partial-output coefficients,
every physical gate/output, all 510,388 logical frames and 2,929,612
physical frame transitions. Every actual enlarged frame contains its
source span, equals its declared first-consumer frame, and satisfies
forward/reverse-complement nesting and all designated target
orthogonality. Formal-core equality is explicitly not assumed at
clones. Saved order/descriptor identities and separate gate capacities
are checked.

New h12 controls check all 4,126 complete source, target, central and
dirty auxiliary basis vectors in each orientation. The separate side
invocation checks 4,114 basis vectors; the difference consists of the
12 central registers. Dense rational controls cover 3,317 distinct
small envelopes. Both complete maps restore arbitrary dirty scratch.

The audited counts are `c=489563`, `q=62475`, `links=66358`, and
`R=c+q-links=485680`. The full transfer counts are
`W=439367045355000`, `s=58282475670006923125`,
`N=9031399015625`, `L=3384009916875`, `D=2263379181875` and `m=132651`.
The literal scalar guard uses `G=5508835077952500`, and the positive
slack in the conservative E bound is
`3301393637375458038560503238883475024110043208`.

The wrapper took 100.3196s, with 3627864KiB peak RSS and zero swaps;
the root-owned reservation was released. This promotes a feasible
explicit construction under the retained conditional transfer. It
does not claim selector optimality or a final multiplication kappa;
a fresh exact parameter composition must consume the promoted counts.
