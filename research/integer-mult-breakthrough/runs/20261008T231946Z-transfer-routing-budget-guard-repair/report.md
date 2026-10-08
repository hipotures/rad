# Routing-aware transfer: corrected serial-width illustration

Result: **PASS** for 80 exact declared time/row recurrences and all controls.
Four workers finish in 2.570 seconds. Widths extend through `2^128` and
separate remainder cases. The full routing chunk, complete row stock,
nonselected remainder operations and every early/final leaf are retained.

The source now derives the illustrative guard's serial coefficient from
the complete profile: 15/2 and 19/2, rounded up to eight and ten. The added
negative rejects the previous uniform eight for the second profile. The
numeric guard remains an illustration conditional on actual endpoint and
local-prefix contracts, not an implemented Gaussian circuit.

The time powers are unchanged: 5/8 and 13/16 improve the compared coarse
sufficient powers 3/4 and `(5+sqrt(3))/8` under the same overhead ledger.
The [analytical report](../../reports/transfers/routing-aware-depth-transfer.md)
gives the proof, complete interface assumptions, limitations and reproduction.
The initial receipt and exact source correction are preserved in their own
run. No larger b or kappa is asserted.
