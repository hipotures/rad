# RaD

RaD preserves research code, evidence and conclusions. This repository is the
durable record; large execution payloads remain in the local working storage.
The connected repository is [hipotures/rad](https://github.com/hipotures/rad).

The existing expert-residency investigation stays in
[iq3s-residency-20261004T230051Z](iq3s-residency-20261004T230051Z/).
Its original absolute path remains
`/srv/ai/research/iq3s-residency-20261004T230051Z`, so measured launchers, frozen
manifests and existing reproduction commands retain their original addressing.
The repository root on this host is `/srv/ai/research`.

Start with the [research index](docs/research-index.md). The latest completed
study is [Golden Swap Phase 1](iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/report.md):
36/36 valid reserved replay requests, with the primary conclusion
`MECHANISM_IMPROVED_NO_CONFIRMED_LATENCY_GAIN`. It learned return-risk signal
and reduced nonlocal demand, but did not establish a consistent latency gain.
Normal serving was left unchanged. This repository organization does not change
those measurements or enable an experimental scheduler.

Reports, scripts, patches, contracts, compact JSON/CSV results, small numeric
model exports and research plots belong in Git. Build trees, model weights,
source clones, virtual environments, large datasets, tapes, telemetry and large
row-level result dumps stay local. Git ignores them; it does not delete them.
See [storage and reproduction](docs/storage.md) and the
[local artifact catalog](docs/local-artifacts.json).

To inspect and prepare a durable snapshot:

```bash
cd /srv/ai/research
git status --short --branch
python3 tools/archive_workspace.py plan
python3 tools/archive_workspace.py stage
python3 tools/archive_workspace.py audit
git diff --cached --stat
```

The selector never commits, pushes, deletes, rebuilds or runs a benchmark.
Review its plan in `storage/retention-plan.json`, then commit and push the
reviewed snapshot. Do not use `git add -f .` to bypass the storage policy.

Read [AGENTS.md](AGENTS.md) for the execution protocol. Continue this
investigation in its existing directory. New, unrelated research topics use
`research/<short-kebab-case-name>/` as specified there.

The [migration record](docs/migration.md) identifies the preserved legacy Git
history. The original remote AGENTS.md and LICENSE were retained. Existing
source material and dependencies keep their own licensing; see
[third-party provenance](docs/third-party.md).
