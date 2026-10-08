# Paid packed affine-translation controls

Status: **EXACT FINITE CONTROLS** supporting a **CONDITIONAL RESULT** under
the stated original streaming component assumptions. No improved primitive
or multiplication exponent is asserted.

Four workers checked 790,849 residue representatives and 28,672 full-range
or forced-safe-guard addresses. Runtime was 1.384 seconds. Literal inverse,
off-guard correctness, exceptional-bank preservation, paid correction,
top-bit completion and restoration of arbitrary temporary addresses pass.

Omitting correction fails on an exact fraction `1/32` of the full rectangle
at `K=6,f=3,rho=2`, and `1/128` at `K=8,f=3,rho=0`. Exact representative
equivariance makes these full-rectangle deductions rather than estimates
from samples. Smaller K values are separate out-of-contract negative controls.

The [proof and complete cost ledger](../../reports/transfers/paid-packed-translations.md)
retain all chunk swaps, descriptor scans, exceptional record sorting and
complete payload volumes. The source is standalone standard-library Python.
The [protocol](protocol.json) pins the executable hash, generator parameters,
seeds, base revision and UTC interval. All generated compact per-case outcomes
are retained in `results/summary.json`; the identical full execution JSON is
at the ignored location recorded by the protocol.
