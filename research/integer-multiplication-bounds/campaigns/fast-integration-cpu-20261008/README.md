# CPU fast-integration campaign

Status: active since 2026-10-08 12:40:55 UTC; deadline 14:40:55 UTC.

[GOAL.md](GOAL.md) is the execution prompt. This directory is the exclusive working and durable-output location for the CPU track.

- Host: `cpu`; checkout `/home/user/DEV/rad`.
- Budget: 12 CPU slots, approximately 62 GiB RAM; no GPU.
- Duration: 120 minutes from explicit goal launch, not file creation.
- Research branch: `research/fast-cpu-20261008`.
- Initial emphasis: Gaussian inversion, precision, transform layouts, tape movement and compatible integrations.

Use local subagents and sustained useful parallel computation. Check resource use at least every three minutes. Commit and push descriptive scientific checkpoints at least every twenty minutes when durable work changes.

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
