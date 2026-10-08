# Direct-envelope singleton successor: 420 exact candidates

The first direct-envelope successor cohort verified 420 distinct ground-50
singleton schedules. Its best compiled circuit uses 473,026 roles, improving
the independently promoted 484,264-role anchor by 11,238 roles, or 2.3206%.
Every unchanged full scalar-map, positive-frame, physical compiler, and
designated-target check passed. Subsequent independent uncached promotion
also passed in run `20261008T014255Z-review-singleton-final420`: all 63,562,800
partial coefficients, every physical/frame/controller transition, complete
small dirty bases, and stage exchanges. That audit took 101.70 seconds with
a 3,087,096-KiB peak; its certificate and report are retained by the reviewer.

The winner's position vector is `[0]*24 + [23]*24 + [0,24]`: insert the
singleton before all paired blocks for common points 0 through 23 and 48,
near the end for common points 24 through 47, and at the end for point 49.
This produces 448,127 additions and 58,800 partial outputs, an unoptimized
role count of 506,927. The controller-chain flow selects 33,901 retained
links from 40,064 candidates, giving the actual role count 473,026.
The fixed-graph flow optimum is not a global lower bound over circuits.

The candidate ID is
`171a84402dbfaba83759e04b307eaa7a0e03e945a9a58bbd10e27e0caaf47102`.
Its logical circuit digest is
`8af9284be8e3e45f761db5d7093d08205cf4af031a39f73fd4e95cb6a9902265`;
its compiled digest is
`dab8e96f621d7346acbe9811b1c6c5005fc040d6cc9dd61c8cd745b23db712ea`.
The immutable [winner file](../runs/20261008T010330Z-finite-singleton-successor/results/winner.json)
has SHA-256 `20ee3c478e30f5ab73c6105d08fe3a81ea1e1bd66095f074a38638856a630834`.

The source [finite_singleton_successor.py](../code/finite_singleton_successor.py)
reuses the frozen exact evaluator and thin dispatcher. It substitutes the
direct support-envelope constructor through a process-local binding; the
old constructor source and all verifier obligations remain unchanged.
That constructor had already passed exact equality of every Space field and
the complete unchanged ground-50 compiler/target checks. Its digest is
`b95dc6a90713db358f2fe73cdf6feb4d8621d141ed51355ee86b49a388d5b021`.
The successor source digest is
`c360762277905bfd7c376debd2f6e5ad8ec9ec4e397b799a1ff79f005c154b00`.

The protocol records all candidate definitions, seed 109, exact exclusions
of all 50 initial and 219 previous planned candidate IDs, source hashes,
timeouts, address-space limits, and reservation changes. The cohort used
at most 16 aggregate campaign workers, with one or two workers reserved
for independent controls when needed. It completed without errors in
1,025.693 seconds, or 1,474.125 verified candidates per hour. Mean per-case
phases were 12.182 seconds for envelopes, 14.398 for physical compilation,
4.992 for flow, 1.838 for the global map, 0.713 for construction/local checks,
and 0.210 for all physical target pairings. Cohort structure differs from
the predecessor, so the throughput comparison is not a same-input speedup.

The winner shows why additions alone are an inadequate score: its logical
DAG has more additions than the anchor, while many more retained controller
links make its reversible implementation smaller. Among the tested early
prefix patterns, 25 early common points gave 473,026 roles, 21 gave 473,218,
33 gave 474,658, and all 50 early gave 487,025. This motivates a finer prefix
and window search, rather than only single-position perturbations.

The [run protocol](../runs/20261008T010330Z-finite-singleton-successor/protocol.json)
contains the exact command. Set the original upstream and math environment,
use the 484,264-role winner as anchor, exclude the recorded predecessor
protocols, and provide a fresh output directory. The source retains all 420
candidate IDs and checkpoints. External results are deterministically
regenerable under
`$RAD_WORK_ROOT/derived/finite/20261008T010330Z-finite-singleton-successor/`,
with complete logs under the corresponding `logs/finite/` directory.

This report establishes independently promoted finite role savings. It does
not infer a new final integer-multiplication kappa from a role count alone;
the new compact-control analytic assembly is independently reviewed.
