# Inverse and precision branch

This CPU-campaign branch investigates reusable segmented Gaussian inverses and
their precision/tape interfaces. It owns only this directory. The coordinating
agent owns Git publication. Campaign start: 2026-10-08 12:40:55 UTC; deadline:
14:40:55 UTC; closing phase starts 14:25:55 UTC.

The user extended the campaign indefinitely at approximately 14:23 UTC.
The initial deadline and closing phase above are historical; research now
continues until the user stops it. This branch has three compute slots under
the coordinating agent's extended allocation.

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

The [extended compiled validation](reports/compiled-crt-validation.md)
executes the ACTUAL masked `F_u` rotations and their
computed-inverse-key radix repairs inside full CRT trees, including reverse
padding and existing-coordinate banks. Four/five-prime completed controls are
retained under `runs/20261008T1440Z-compiled-crt-*`; a genuine two-node batch
with 14,608 wrong outer records repaired also passes the full forward and
reverse pipeline in `runs/20261008T1448Z-compiled-crt-bankleaf-five-bank`.
Six-prime and two-bit guard variants have explicit running protocols and
pinned code snapshots.
The [coefficient-payload API](code/compiled_crt_payload_api.py) lets the
arithmetic integration branch execute these physical maps on ring residues.
The [native complete-cube controls](reports/native-crt-controls.md) independently
validate two-bit inner/outer dirty digits and a complete six-prime tree,
including actual computed-key repairs and explicit omission counterexamples.
A three-bit outer guard also passes the complete 24-bit cube, restoring
801,496 wrong outer records before zero-padding scans and recovering every
tag in the reverse program.
The [four-target reflection controls](reports/four-target-reflection-controls.md)
also pass mixed binary/odd moduli with a shared fixed source. Deliberately
borrowing that endpoint control as a dirty guard makes addresses0 and1
collide, giving an explicit exclusion required by the legal bank interface.
The [nested bank recycling note](reports/nested-bank-recycling.md) states when
completed inner shears may borrow high outer-U bits. A complete two-target
three-bit inner control passes; its planned missing-inner negative also
passes both actual oracles, an anomaly retained unchanged. Full unique tags
confirm that its outer composition absorbs raw-inner errors on all addresses;
the standalone raw fanout still differs from ideal XOR on 49,152 addresses.
The four-target three-bit-inner bank restoration and two-target fixed-source
controls are complete, preserving both positive and negative outcomes.
The [Hadamard routing budget](reports/hadamard-routing-budget.md) proves the
long-record arithmetic identity and excludes its literal per-residual
complex-only basis substitution by a source-reviewed rank-mass count.
It leaves a globally shared or changed compiler unresolved.
The [dyadic interval Gaussian certificates](reports/dyadic-interval-gaussian.md)
give five exact residual/all-alias positive enclosures, three matched failed
target certificates and a frozen-word replay, independent of floating LU
accuracy. These bounded certificates do not change the conditional exponent.
The [cyclic free-axis interface](reports/cyclic-free-axis-repair.md) supplies
global principal-window band LU on every complete free axis of inverse repair
packets, including regular face packets.
The [cyclic reference API](reports/cyclic-reference-api.md) supplies a separate
bordered numerical solve for discriminating packed regular inverse cores;
eight independently executed layout callers pass their higher-precision
residual plus all-alias tail estimates through source period262139.
Seven are explicitly outside u*theta>=1; the final large-mismatch case lies
inside it. Genuine packed Laurent inverse integration is still being tested.

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

Exact Python address controls use only the standard library. Numerical Gaussian
references additionally use the campaign's pinned mpmath dependency; the
independent native controls use C++17 and g++. Reproduction
commands and scope limitations are in the linked reports; completed numerical
and exact controls are in `runs/`. Resource allocation changed from an initial
four-worker cyclic phase to one proof-focused slot, then to three slots after
the campaign extension. Current execution must follow the coordinator's live
allocation rather than these historical counts.
