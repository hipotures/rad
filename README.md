# RaD

RaD preserves research code, evidence and conclusions. This repository is the
durable record; large execution payloads remain in the local working storage.
The connected repository is [hipotures/rad](https://github.com/hipotures/rad).

The [benchmark archive](benchmarks/README.md) preserves earlier Qwen phases,
Strata comparisons, hardware characterization, scripts, configurations,
patches and compact results from `/srv/ai/benchmarks`. These investigations and
the residency laboratory belong to the same RaD project. Find serving scripts
and their configurations in the [starter index](launchers/README.md), including
direct links to every preserved `start-128k.sh`.

The familiar report shortcuts are now portable links:
[Qwen first phase](QWEN38_FLASH_NEXT_LATEST_REPORT.md),
[phase 2](QWEN38_FLASH_NEXT_PHASE2_LATEST_REPORT.md) and
[phase 3](QWEN38_FLASH_NEXT_PHASE3_LATEST_REPORT.md).
See the [workspace map](docs/workspaces.md) for Git and local execution paths.

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

For a fresh task, read [AGENTS.md](AGENTS.md) before creating files. Durable
material goes in `research/<topic>/`: authored `code/`, small `fixtures/`,
`configs/`, isolated run results, reports and recovery manifests. Large inputs,
downloaded repositories, environments and compiled output belong in a task-owned
directory under `/srv/ai/work/rad/`. Create/check `.gitignore` before execution.

At completion, stage the actual task-owned paths explicitly, inspect the diff
and run the publication check:

```bash
cd /srv/ai/research
git status --short --branch
git add -- <actual-task-owned-paths>
git diff --cached --stat
git diff --cached --check
python3 tools/archive_workspace.py audit --staged-only
git commit -m "Record the task outcome and reproduction material"
git push origin <actual-branch>
```

Replace placeholders with reviewed paths and the appropriate upstream branch.
Verify the remote contains the commit. The default limits are 1 MiB per file,
4 MiB per patch and 20 MiB of staged content per commit.

`tools/archive_workspace.py plan` and `stage` are bulk-import tools for the
managed workspace, rather than the completion workflow for an individual task.
Review their plan in `storage/retention-plan.json` before explicitly using them.
The helper never commits, pushes, deletes, rebuilds or runs a benchmark.
Do not use `git add -f .` to bypass the storage policy.

Read [AGENTS.md](AGENTS.md) for the execution protocol. Continue this
investigation in its existing directory. New, unrelated research topics use
`research/<short-kebab-case-name>/` as specified there.

The [migration record](docs/migration.md) identifies the preserved legacy Git
history. The original remote instructions remain in that history; AGENTS.md
now defines the fresh-task workflow. LICENSE was retained. Existing
source material and dependencies keep their own licensing; see
[third-party provenance](docs/third-party.md).
