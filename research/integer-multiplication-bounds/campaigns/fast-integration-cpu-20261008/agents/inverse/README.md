# Inverse and precision branch

This CPU-campaign branch investigates reusable segmented Gaussian inverses and
their precision/tape interfaces. It owns only this directory. The coordinating
agent owns Git publication. Campaign start: 2026-10-08 12:40:55 UTC; deadline:
14:40:55 UTC; closing phase starts 14:25:55 UTC.

Current candidate: build cyclic boundary factors once per tensor axis and charge
their online application separately. A block boundary of width `w` has factor
setup `O(w^3)` and per-right-hand-side application `O(w^2)`. Reuse can replace
the segmented inverse's per-output `w^3(1/lambda+theta)` by the online charge
`w^2(1/lambda+theta)`, provided catalogue movement and setup are paid.

This is an accounting/interface candidate, not an accepted multiplication
exponent. Exact controls and a written bounded-precision lemma are in progress.

Inputs: completed RaD phase-cell and semantic-guard reports at repository
historical commit `6b32837aee0561af85e4efaca21af07b9f2749d2`, and Swapnil Jain's
public repository at `c2c2f279d93643e5ff3fe121a0fbc68e0e6f4007` (2026-10-08).
Downloaded inputs and execution payloads live under campaign `work/inverse/`.
