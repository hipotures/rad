# Physical lineage verifier prototype

This bounded prototype validates a full coefficient-disjoint logical DAG,
then proves each physical copy recursively from its exact operand identities.
It leaves the existing source/target frame assertions and canonical digest
unchanged. Complete h8/h12 controls pass and a deliberately missing physical
operand is rejected. The saved output and original command are in
[runs/20261008T011408Z-physical-lineage-small](../runs/20261008T011408Z-physical-lineage-small/).

The new small verifier took0.002655 and0.016571 seconds versus0.002350
and0.013894 seconds for the old coefficient-set phase. It is about18% slower
on the larger control, so no throughput improvement is claimed and it was
not adopted by current queues. There is no full h50 calibration for this
prototype. The induction presumes the unchanged verified DAG and complete
source/output key coverage; a future implementation should explicitly assert
that coverage before adoption. This is retained negative/partial evidence,
not an alternative independent promotion standard.

The authored source is [physical_lineage_check.py](../code/physical_lineage_check.py),
SHA2564f5a4c6f798ad3dbcfd6c4d3cfcd4d772ae936f6f772b28fc6c679df3f678225.
No accepted verifier or candidate was changed.
