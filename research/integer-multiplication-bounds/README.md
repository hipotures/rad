# Integer multiplication bounds

This investigation seeks stronger defensible conditional bounds of the form
`T(n) = O(n (log n)^(1 - kappa))`, starting from
[CrocSwap/integer-mult-bounds](https://github.com/CrocSwap/integer-mult-bounds).
Larger `kappa` is stronger. Finite witnesses, mathematical transfer arguments,
and upstream algorithmic assumptions must be distinguished.

## Current campaign

The ten-hour campaign `20261007T222521Z` began at
2026-10-07 22:25:21 UTC and has an immutable deadline of
2026-10-08 08:25:21 UTC. Substantive research is active. The pinned baseline
passes all 85 tests and regenerates its certificates and patches unchanged.

The current strongest verified composition supports the strict conditional
saving `6412736146231/10^30`, more than `3.696690703179 * 2^-59`.
It combines positive support envelopes and retained controllers, unequal
52/48/52 bit tensor factors, and a reused banded Gaussian inverse with
reviewed precision, guard and prime-interval proofs. Exact parameter
tuning follows those substantive changes. The complete upstream
theorem remains assumed, and the enormous eventual cutoff is an asymptotic
limitation. Research continues through the immutable deadline.

- [Full goal](GOAL.md)
- [Campaign clock, protocol and resume state](runs/20261007T222521Z-campaign/protocol.json)
- [Working hypothesis ledger](reports/hypotheses.md)
- [Evolving report](reports/campaign-20261007T222521Z.md)
- [Aligned-pairing result and proof](reports/finite-aligned-pairing.md)
- [Controller compiler and independent review](reports/frame-reuse.md)
- [Weighted Gaussian estimate](reports/downstream-weighted-gaussian.md)
- [Blocked convolution and review](reports/downstream-blocked-gaussian.md)
- [Blocked Gaussian parameters and scoped ceiling](reports/downstream-parameter-optimum.md)
- [Current composed result and unequal-factor proof](reports/asymmetric-motifs.md)
- [Reusable Gaussian inverse and independent review](reports/downstream-reusable-banded-inverse.md)
- [Rational support-envelope review](reports/review-rational-envelopes.md)
- [Scoped negative frame searches](reports/finite-target-frames.md)
- [Calibrated pair-feature discovery](reports/pair-feature-discovery.md)
- [Reproduction and recovery](reproduce.md)

Durable authored code, compact evidence and reports live here. Downloaded
repositories, environments, inputs and execution output live in the campaign's
external work root, identified in [artifact-manifest.json](artifact-manifest.json).
The research starts from upstream commit
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`; its advertised conditional
`kappa = 2^-59` is consistent with the checked proof/certificate interfaces.
Originality against the wider literature is not established by these checks.
