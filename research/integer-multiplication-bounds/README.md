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
saving `12053467103858103170301/(125*10^37)`, more than `5.558680571643687 * 2^-59`.
It combines the 50/50/50 nonuniform singleton bit circuit with 485,237 side roles,
positive support envelopes and retained controllers, a reused phase-cell
Toeplitz/Schur Gaussian inverse, and a shared binary complex D/E circuit
with 629,617 side roles. The changed order of the two primitive exponents
requires the independently reviewed decaying recurrence estimate.
Independent full finite replay and analytic/arithmetic reviews pass.
The complete upstream theorem remains assumed, and the enormous eventual
cutoff is an asymptotic limitation. Research continues through the
immutable deadline.

- [Full goal](GOAL.md)
- [Campaign clock, protocol and resume state](runs/20261007T222521Z-campaign/protocol.json)
- [Working hypothesis ledger](reports/hypotheses.md)
- [Evolving report](reports/campaign-20261007T222521Z.md)
- [Aligned-pairing result and proof](reports/finite-aligned-pairing.md)
- [Controller compiler and independent review](reports/frame-reuse.md)
- [Weighted Gaussian estimate](reports/downstream-weighted-gaussian.md)
- [Blocked convolution and review](reports/downstream-blocked-gaussian.md)
- [Blocked Gaussian parameters and scoped ceiling](reports/downstream-parameter-optimum.md)
- [Current promoted composition and limits](reports/downstream-promoted-complex-composition.md)
- [Shared complex construction and transfer](reports/downstream-complex-side-circuit.md)
- [Independent complete complex transfer review](reports/review-complex-transfer.md)
- [Previous phase and packed composition](reports/phase-singleton-composition.md)
- [Measured candidate throughput and resource use](reports/computational-throughput.md)
- [Unequal-factor proof and earlier milestone](reports/asymmetric-motifs.md)
- [Reusable Gaussian inverse and independent review](reports/downstream-reusable-banded-inverse.md)
- [Phase-cell inverse and full review](reports/downstream-phase-cell-inverse.md)
- [Exact packed recurrence and review](reports/downstream-packed-unrolling.md)
- [Singleton circuit and independent full witness](reports/finite-singleton-gaps.md)
- [Rational support-envelope review](reports/review-rational-envelopes.md)
- [Scoped negative frame searches](reports/finite-target-frames.md)
- [Calibrated pair-feature discovery](reports/pair-feature-discovery.md)
- [Vertex-feature uniqueness and scoped XOR obstruction](reports/vertex-feature-uniqueness.md)
- [Reproduction and recovery](reproduce.md)

Durable authored code, compact evidence and reports live here. Downloaded
repositories, environments, inputs and execution output live in the campaign's
external work root, identified in [artifact-manifest.json](artifact-manifest.json).
The research starts from upstream commit
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`; its advertised conditional
`kappa = 2^-59` is consistent with the checked proof/certificate interfaces.
Originality against the wider literature is not established by these checks.
