# CPU fast-integration campaign

Status: prepared; research has not started.

[GOAL.md](GOAL.md) is the execution prompt. This directory is the exclusive working and durable-output location for the CPU track.

- Host: `cpu`; checkout `/home/user/DEV/rad`.
- Budget: 12 CPU slots, approximately 62 GiB RAM; no GPU.
- Duration: 120 minutes from explicit goal launch, not file creation.
- Research branch: `research/fast-cpu-20261008`.
- Initial emphasis: Gaussian inversion, precision, transform layouts, tape movement and compatible integrations.

Use local subagents and sustained useful parallel computation. Check resource use at least every three minutes. Commit and push descriptive scientific checkpoints at least every twenty minutes when durable work changes.

No communication with the independent GPU campaign. Historical results and shared infrastructure are read-only. All new durable artifacts belong here; large execution payloads belong in ignored or external task-owned storage.
