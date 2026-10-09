# Full basis-slice and form-incidence controls

Status: **PASS EXACT FINITE CONTROLS**. Four workers at packet axes 1, 2,
4 and 6 check all 532624 input/output Gram entries, exact symmetry of the
two input families and every support of the named 3^s product word. Each
raw slice has Gram D I. All three direct form sides have D^2 incidences,
with exactly D terms per coordinate. A one-entry corruption is rejected.
The run takes 0.172946 source seconds; this measures the finite checker,
not a payload algorithm.

The [cross-run proof](../../reports/complex/product-slice-wire-boundary.md)
explains the all-rank incidence lemma and its scope. The finite run does
not enumerate arbitrary decompositions or prove a general time lower bound.
Shared/layered circuits and record products remain outside. No kappa is
asserted.

Reproduce with Python standard library:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/product_slice_wire_floor.py --workers 4
```

The immutable full certificate is retained without row omissions. Full
matrices are generated, not serialized. Original source/log snapshots are
under the task-owned ignored work namespace; portable source recovers the
matrices. Source identity, exact command, start time and environment are
pinned in results.
