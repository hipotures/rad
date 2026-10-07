# Weighted Gaussian attempt

See the [mathematical report](../../reports/downstream-weighted-gaussian.md)
and [exact checker](../../code/downstream_gaussian.py).

Initial combined composition rejected `a_bit=306/10^11` for
`R=494250`: the exact rank-deficit check failed. The maximum certified
linear deficit/log ratio is `23/7539555375`, so the valid rounded
replacement is `305/10^11`. The next run retains the algebraic and
Gaussian claims and corrects only this overestimated finite saving.

This attempt initially completed its exhaustive rational transition
checks but aborted while constructing the combined witness; no
successful certificate was emitted for that attempt. The same exact
checks are rerun for the corrected attempt, rather than treating the
aborted run as a successful certificate.
