# Routing-aware depth/row transfer controls

Result: **PASS** for the declared time/row recurrence, with a **REJECTED
ILLUSTRATIVE GUARD FIELD** subsequently repaired in a fresh attempt.
Four workers finish 80 exact stopped recurrences in 2.507 seconds, through
width `2^128` plus remainder cases. Every result retains its exact rational
cost, full row stock, fixed routing chunk and all early/final leaves.

Two complete profiles demonstrate stronger sufficient powers under the same
overhead ledger: 5/8 versus 3/4, and 13/16 versus `(5+sqrt(3))/8`.
Missing rows, incomplete role boundaries, circular width-only recursion,
unit self-mass and omitted routing chunks are rejected.

The second profile has total serial child width 19e/2. The initial receipt
mistakenly used the first profile's conservative q=8 in its illustrative
guard. That numeric field is invalid for the second profile, although the
time/row comparisons and their rational proof are unaffected. The
[fresh repair attempt](../20261008T231946Z-transfer-routing-budget-guard-repair/report.md)
derives q from each profile, giving eight and ten, and adds a targeted
undercharge negative. Neither run supplies an actual Gaussian phase circuit.

The initial source SHA is preserved in the protocol. The
[correction patch](conditional-guard-correction.patch) records the exact
source change and can be reversed against corrected source SHA
`55a391b221f21aea1b1f0053dc150ed00e3cce929eb86ecd02e6d1bf3be91c8a`
to regenerate the initial source. Original raw and compact results remain
unchanged; the raw status string alone does not override this scoped review.

The [analytical report](../../reports/transfers/routing-aware-depth-transfer.md)
proves the weighted internal/frontier/budget bounds and states the complete
native endpoint, fixed-tape routing, dirty field, precision and row allocation
hypotheses. The source-only reproduction and complete deterministic protocol
are retained. No actual Gaussian native profile or larger kappa is claimed.
