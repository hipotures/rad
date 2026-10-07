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

The first verified milestone is an aligned-pairing circuit with 494,250 side
roles, compared with 509,194 in the pinned baseline. Under the retained upstream
assumptions it supports the strict saving
`738998782479/400000000000000000000000000000`, approximately
`1.0650 * 2^-59`. This changes the circuit, not merely the rounding of the
starting margin. The complete upstream theorem remains assumed.

- [Full goal](GOAL.md)
- [Campaign clock, protocol and resume state](runs/20261007T222521Z-campaign/protocol.json)
- [Working hypothesis ledger](reports/hypotheses.md)
- [Evolving report](reports/campaign-20261007T222521Z.md)
- [Aligned-pairing result and proof](reports/finite-aligned-pairing.md)
- [Reproduction and recovery](reproduce.md)

Durable authored code, compact evidence and reports live here. Downloaded
repositories, environments, inputs and execution output live in the campaign's
external work root, identified in [artifact-manifest.json](artifact-manifest.json).
The research starts from upstream commit
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`; its advertised conditional
`kappa = 2^-59` is consistent with the checked proof/certificate interfaces.
Originality against the wider literature is not established by these checks.
