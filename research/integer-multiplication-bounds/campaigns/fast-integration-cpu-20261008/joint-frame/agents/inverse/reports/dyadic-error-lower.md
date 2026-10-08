# Exact upper and lower certificates for cyclic Gaussian solves

This extends the earlier [integer interval checker](../../../../agents/inverse/reports/dyadic-interval-gaussian.md)
with an error lower bound and an untrusted sparse bordered Decimal proposal.
The proposal retains cyclic corners through a Schur border and banded
interior solve. Certification trusts only the frozen integer words, directed
coefficient intervals, and the proved tail over **every** omitted lifted
Gaussian image. No Decimal accuracy assertion enters a certificate.

Let retained row residual intervals be `[lo_i,hi_i]`. Their maximum absolute
lower bound is `r0=max_i max(0,lo_i,-hi_i)` with the sign-compatible endpoint
chosen when the interval avoids zero. With all-image tail upper bound `t`
and frozen solution norm `x0`, the true full residual has lower bound
`r=max(0,r0-t*x0)`. The row-gap certificate also supplies
`||N||_infinity<=1+off+t=2-gap`. If `N*x*=b`, then

```
||x-x*||_infinity >= r/(2-gap).
```

The existing upper bound is `(r_upper+t*x0)/gap` for positive `gap`.
All powers of two and rational comparisons are evaluated with integers.
Strict lower and upper certificates cannot contradict each other. A positive
lower bound is allowed for an accurate finite-word proposal: its residual
need not be exactly zero.

The new control changes the proposal bandwidth while evaluating the full
matrix with the original wider retained band and full tail. Thus a narrow
proposal is tested for an actual error, rather than being judged by its own
loose truncation bound. The other malformed proposals omit cyclic corners
or reduce the frozen solution word precision. All cases use the same seed
`202610081752`; the proposal is independent of the subsequent verifier.

| Source/target, alpha | Target bits | Change | Strict certified conclusion |
|---|---:|---|---|
| 127/128, 2 | 128 | complete bordered solve | error < 2^-190 |
| 127/128, 2 | 128 | omit cyclic corners in proposal | error > 2^-21 |
| 127/128, 2 | 128 | freeze at 112 fractional bits | error > 2^-113 |
| 127/128, 2 | 128 | proposal half-bandwidth 1 | error > 2^-39 |
| 4093/4096, 2 | 256 | complete bordered solve | error < 2^-313 |
| 4093/4096, 64 | 512 | complete bordered solve | error < 2^-575 |

The complete 127, omitted-corner 127 and narrow-proposal 127 receipts were
replayed from frozen words without running Decimal. Every conclusion was
unchanged. The two large cases took 2.75 and 2.06 seconds respectively on
one CPU lane, with standard-library-only code. These are bounded certificate
costs, not fast-tape runtime measurements.

The alpha-2 cases do not satisfy the all-size lemma's `u*theta>=1`.
They certify their individual cyclic matrices using the measured positive
row gap. The alpha-64 case has `u*theta=12288/4093>1` and
`theta=3/4093<1/4`; it is a distinct admissible control. No domain satisfaction
is transferred between cases.

All six predeclared outcomes matched. These negatives prove that the actual
frozen vector misses the requested target, a stronger conclusion than the
earlier checker merely failing to certify it. They remain finite statements;
they do not prove a general omission theorem or the complete multiplication
reduction. Source hashes, full RHS words, proposed words, all-alias bounds
and exact residual/error ratios are retained under
`runs/20261008T1753Z-interval-lower-*`. The source and queue controller are
frozen separately in every run. [Reproduction commands](../reproduce.md)
exercise both proposal-and-certificate and pure integer replay.
