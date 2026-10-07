# One RaD record, several historical execution roots

`/srv/ai/benchmarks` and the timestamped residency laboratory are two historical
parts of the same project. Their durable files are now preserved in
`hipotures/rad`, whose checkout root on this host is `/srv/ai/research`.

| Original working location | Tracked repository location | Role |
|---|---|---|
| `/srv/ai/benchmarks/<study>/` | `benchmarks/<study>/` | Earlier Qwen phases, Strata experiments, hardware characterization, reports, authored scripts/kernels, configurations, patches and compact results. |
| `/srv/ai/research/iq3s-residency-20261004T230051Z/` | `iq3s-residency-20261004T230051Z/` | Residency laboratory and subsequent campaigns; existing frozen files remain in place. |
| `/srv/ai/launchers/<family>/` | `launchers/<family>/` | User-owned serving starters, their exact configuration and provenance; installation/verification records. |
| `/srv/ai/*LATEST_REPORT.md` symlinks | Same named Markdown files at the repository root | Portable links to the preserved report, with the original alias/target recorded. |
| New investigations | `research/<topic>/` | New durable work, using the directory/storage contract in AGENTS.md. |
| New large/disposable work | `/srv/ai/work/rad/<topic>/<run-id>/` | Inputs, derived data, checkouts, build output, environments, raw logs and temporary files, outside Git. |

The benchmark/launcher import copies actual files, rather than only creating an
index or symlinks. The [source manifest](external-workspaces.json) records 1:1
copies with SHA256, sizes and executable bits. Reports and scientific source
are preserved verbatim. Compact header exports identify their source/hash and
what was omitted; they are not replacement input data or the original schema.

Large inputs, weights, generated test corpora, request/token dumps, raw captures,
build output, downloaded checkouts and environments remain local. Full exclusion
details are in the ignored `storage/external-workspace-exclusions.jsonl`; public
group counts and the largest excluded files are in the source manifest. Pruned
environment/checkouts are represented as directories, not counted as inventoried
individual package files. No claim that Git backs up every local byte is made.

Original working paths and symbolic report aliases are preserved on the host.
Copied starters still refer to their original runtime/configuration paths. A
clone provides their definitions, but requires the identified runtimes, weights
and environments to execute them. None of the import commands starts a server,
changes the serving configuration or rebuilds an engine. Historical reports'
absolute paths and links to omitted raw evidence still describe local storage;
the shared indexes and root report shortcuts provide portable navigation.

To review or verify this import:

```bash
python3 tools/import_external_workspaces.py plan
python3 tools/import_external_workspaces.py verify
```

`copy` explicitly imports eligible originals into the checkout and refuses to
overwrite a different existing destination. Review differences before refreshing
a saved file; preserve unrelated edits. Continue existing work in its existing
logical topic, and retain any new durable changes in Git before commit/push.
The mirror is a recorded snapshot, not an automatic background synchronization.

Recovery still depends on retained acquisition/build commands, pinned sources
and patches. An excluded irreplaceable input needs an external backup; its path
and hash alone cannot restore it. The import does not certify that every old
runtime can be regenerated without its local dependencies. Existing measurement
limits and failed experiments remain authoritative.
