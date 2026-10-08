# Inverse and precision branch

This CPU-campaign branch investigates reusable segmented Gaussian inverses and
their precision/tape interfaces. It owns only this directory. The coordinating
agent owns Git publication. Campaign start: 2026-10-08 12:40:55 UTC; deadline:
14:40:55 UTC; closing phase starts 14:25:55 UTC.

The main new general lemma is [global physical Gaussian inverse locality](reports/global-gaussian-locality.md),
including periodic aliases and principal-window errors. A second general
interface is [fixed-grid physical banded LU](reports/physical-band-lu.md) for
rare repairs. The [packed forward precision interface](reports/packed-forward-precision.md)
uses a separate cell scale and keeps the full tensor reserve `O(Q)`.

The later [guarded CRT batching lemma](reports/guarded-crt-batching.md)
uses balanced CRT recursion, joint monotone splits, repeated BIT fanout,
dirty predicate controls and exact sparse repair. It replaces independent
node rotations by a paid `O(V b^tau polylog b)` movement schedule, conditional
on the credited fixed-tape primitives and documented wide-record regime.
Independent local reviews accepted the changed bank and source interfaces;
the coordinating agent owns any resulting full multiplication bound.

The [regular Laurent split](reports/regular-laurent-interface.md) and
[uniform phase-edge obstruction](reports/phase-edge-obstruction.md) separate
the promising mechanism from the excluded naive halo inference. The earlier
[factor reuse lemma](reports/reusable-coupling.md) remains a useful independent
accounting simplification. None of these reports alone promotes a complete
multiplication exponent; the coordinator owns full integration and review.

Inputs: completed RaD phase-cell and semantic-guard reports at repository
historical commit `6b32837aee0561af85e4efaca21af07b9f2749d2`, and Swapnil Jain's
public repository at `c2c2f279d93643e5ff3fe121a0fbc68e0e6f4007` (2026-10-08).
Downloaded inputs and execution payloads live under campaign `work/inverse/`.

All authored code is independent and standard-library-only. Reproduction
commands and scope limitations are in the linked reports; completed numerical
and exact controls are in `runs/`. One CPU slot has been assigned to this
branch since its initial brief four-worker cyclic controls.
