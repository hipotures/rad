# CPU fast-integration campaign

Status: active since 2026-10-08 12:40:55 UTC; extended indefinitely by the user. Closure will begin only when the user requests it.

[GOAL.md](GOAL.md) is the execution prompt. This directory is the exclusive working and durable-output location for the CPU track.

- Host: `cpu`; checkout `/home/user/DEV/rad`.
- Budget: 12 CPU slots, approximately 62 GiB RAM; no GPU.
- Original duration: 120 minutes. The user subsequently removed the deadline; the original start and deadline remain in the protocol as history.
- Research branch: `research/fast-cpu-20261008`.
- Initial emphasis: Gaussian inversion, precision, transform layouts, tape movement and compatible integrations.

Use local subagents and sustained useful parallel computation. Print actual resource observations every minute; target 11–12 useful CPU workers during compute phases. Commit and push descriptive scientific checkpoints at least every twenty minutes when durable work changes.

No communication with the independent GPU campaign. Historical results and shared infrastructure are read-only. All new durable artifacts belong here; large execution payloads belong in ignored or external task-owned storage.

The first completed result is an independently checked [generic continuation
exclusion](reports/continuation-exclusion.md), not a new exponent. The current
original leads are packed tensor Gaussian operations, boundary-phase separation,
and a single distinguished wide suffix axis. These remain incomplete candidates.
The inverse branch has reusable cyclic solve checks and explicit setup/online
separation; the layout branch has a growing-dimensional halo budget lemma.

- [Campaign clock and allocation](protocol.json)
- [Live hypotheses](hypotheses.md) and [status](status.md)
- [Input identities](input-manifest.json), [artifact recovery](artifact-manifest.json)
- [Reproduction](reproduce.md)
- [Inverse branch](agents/inverse/README.md), [layout branch](agents/layout/README.md)
- [Independent continuation review](agents/scout/continuation-review.md)

New written interfaces: [spatial inverse locality](agents/inverse/reports/global-gaussian-locality.md),
[joint fractional tape gathering](agents/layout/joint-fractional-gather-lemma.md),
[deferred whole-axis transforms](agents/layout/deferred-reservoir-transform-lemma.md)
and [source-closed sparse repair](reports/sparse-source-closure.md).
[Exact exponent arithmetic](results/packed-assembly-candidate.json) is a candidate
check, not proof of the changed all-size premises.

14:06 UTC correction: the native known-bit router does not implement the
triangular modular CRT payload map. Its O(nd) row rejects the previously
uncosted near-primitive candidate and retains the scoped a/(1+a) ceiling.
The exact ledger has been repaired. New dirty-guard/parallel carry CRT
constructions are being independently tested; they are unverified leads.
The user requested sustained CPU exploration without changing the clock.
Expanded cyclic inverse, Gaussian packet and exact CRT families are running.

14:34 UTC checkpoint: the new [guarded-reflection CRT tree](agents/inverse/reports/guarded-crt-batching.md) has independent [algebra review](agents/scout/guarded-crt-review.md) and [physical layout review](agents/layout/crt-reflection-layout-review.md). It batches the modular rotations using dirty banks from existing inactive coordinates, restores the banks, and repairs bad guard states. This is a new construction, not a relabeling of bit routing. Exact controls include complete four-target payload repair, actual repeated-bit native fanout, joint splitting, and borrowing an existing bank without extra address bits.

The revised exact ledger supports a stronger **conditional candidate**, kappa=78376985522307/2000000000000000000 (approximately 0.0000391884927611535). Full end-to-end Gaussian/FFT/recovery composition remains under independent review and executable falsification; this checkpoint does not promote a complete new certified multiplication exponent. The old unbatched CRT exclusion remains valid for the old algorithm.

15:03 UTC milestone: the [complete conditional transfer](reports/conditional-composition.md)
has an [independent complete-map/error/recovery review](agents/scout/full-composition-review.md).
It supports every fixed rational kappa<a under the pinned named native
contracts, with explicit witness kappa=78376985522307/2000000000000000000.
This improves the old unbatched a/(1+a) ceiling. Fixed-zeta scalar charges,
normalized inverse prefix factors, global LU on all free repair axes and the
strict u^2*theta>=2Q constant choice are included. The [updated exact ledger](results/packed-assembly-precision-repair.json)
passes. This is a reviewed written conditional result; no new finite native
witness, formal verification, practical cutoff or executed complete fast-tape
implementation is claimed. The full small Gaussian/integer pipeline and an
actual two-node CRT pipeline passed, while larger/precision tests continue.
