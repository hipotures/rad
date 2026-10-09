# Complete short-record monotone split tape trajectories

Result: **PASS** for the declared sequential split interface and counted
finite trajectories. Four workers finish 376,832 complete records in 8.736
seconds. Every payload, delimiter and invalid zero matches an independent
numeric oracle. One case uses exactly Q=B=16 bits.

Counts include all actual single-cell operational moves, reads/writes,
counter/template returns, ripple carry, complete payload copying and zero
fill, payload rewinds and workspace erase. Complete per-tape metrics and
output hashes are durable. Nonzero invalid deletion and endpoint controls
reject the omitted preconditions.

The [component report](../../reports/transfers/short-record-monotone-split.md)
states the O(T*(Q+B)) conditional scan proof, final-old baseline pin and
separate sparse-key amortization deduction. This scan has no guarded
nonlinear rotations and performs zero exception repairs. Earlier guarded
repairs must complete before invalid-zero deletion. No full short-record
CRT, Gaussian transfer or multiplication exponent is claimed.
