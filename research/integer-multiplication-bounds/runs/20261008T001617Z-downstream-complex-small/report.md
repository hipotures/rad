# Completed finite complex side prototype

PASS completed finite scalar/frame prototype; full tensor transfer pending independent review.

The complete circuit generator and exact formal-support checks are retained. Binary-frame checks use explicit norm-one witnesses; complete tensor/phase transfer is separately reviewed. h=6 is excluded because its direct disjoint-triple residual is alternating.

* h=8: 786 additions, 898 roles, 1572 directed frame edges; 3 dirty probes and 0 exact local basis probes pass.
* h=10: 2160 additions, 2400 roles, 4320 directed frame edges; 3 dirty probes and 0 exact local basis probes pass.
* h=12: 4533 additions, 4973 roles, 9066 directed frame edges; 3 dirty probes and 0 exact local basis probes pass.

The compact result is [certificate.json](results/certificate.json). The cross-run proof is [the complex circuit report](../../reports/downstream-complex-side-circuit.md). Reproduction command, exact source/dependency hashes, immutable input and any external timing log are in [protocol.json](protocol.json).

Follow-up: [independent complex transfer review](../../reports/review-complex-transfer.md) is complete and positive; the original provisional execution status remains recorded in its immutable result.
