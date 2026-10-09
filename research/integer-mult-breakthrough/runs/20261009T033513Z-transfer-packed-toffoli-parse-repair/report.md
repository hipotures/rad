# Guarded packed Toffoli parse repair

The four-worker experiment passed in 0.473784117 seconds. It exhausts 262144 native quotient representatives at K6/f2, records exact unrepaired failure fraction 1/512, and replays all 16384 complete four-field toy records including row-prefix, suffix, controls and companion. The K1 toy is outside the native guard band and explicitly has sixteen times the unguarded four-slot volume. No timing bound is inferred from Python array execution.

The earlier parse-only failure is preserved under `20261009T033427Z-transfer-packed-toffoli`. The accepted source's recovery patch reconstructs that rejected version exactly. This repair does not hide an unpaid final Toffoli: a complete extra K-axis chunk supplies guards for every selected position. The separate same-volume allocation theorem is discussed in [the guard-layout report](../../reports/transfers/guarded-slot-layout-transfer.md).

Original source/config/helper identities and run start are retained in the unchanged protocol and launch receipt. Complete results are unchanged copies of the ignored raw run with this same ID. See [the routing report](../../reports/transfers/packed-nonlinear-routing.md) for the conditional cost and limitations. No native runtime or multiplication exponent is established.
