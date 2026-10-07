# Storage and reproduction

The repository root is `/srv/ai/research`; the original workspace is its
`iq3s-residency-20261004T230051Z/` child. This arrangement preserves all recorded
absolute paths. GitHub contains a selective snapshot of durable work, not an
execution-environment backup.

The same repository also versions durable files from the original
`/srv/ai/benchmarks` and `/srv/ai/launchers` roots under `benchmarks/` and
`launchers/`. The [workspace map](workspaces.md) describes their relationship.
Originals stay at their execution paths; tracked copies preserve reports,
authored source, exact configurations, source patches and compact evidence.
The [external-workspace manifest](external-workspaces.json) identifies every
verbatim copy by bytes/hash and records omissions and portable report aliases.
Use `python3 tools/import_external_workspaces.py verify` on this host to compare
the retained files with both their recorded hashes and their originals.

| Material | Location/policy |
|---|---|
| Reports, goals, decisions, audits and source-group splits | Tracked verbatim. |
| Research scripts, source patches, fixture source and build/config identities | Tracked. Runtime/source clones and compiled fixtures remain local. |
| Compact JSON/CSV results and small text/JSON predictor exports | Tracked. Binary pickles and numeric row arrays remain local. |
| Saved run contracts and fidelity/validation records | Selected explicitly, including bounded records inside ignored raw directories. |
| Research plots | Bounded SVG/PNG exports tracked. |
| Model weights, datasets, tapes, raw traces, telemetry, build output and environments | Local working storage; original provenance/hash manifests identify them. |
| Large text result dumps | Local, even when their extension is JSON/CSV. Reports and the storage catalog retain their context/location. |
| Scalar/header evidence from large JSON results | Exported into docs/compact-results/ with original file path, bytes and SHA256; omitted arrays are explicit. |
| Credentials and process/PID state | Excluded. |

Publication limits individual durable artifacts to 1 MiB, with a 4 MiB limit
for source patches and a 20 MiB budget for added/modified staged file content
per commit. The budget counts the complete changed blobs, not just diff lines;
unchanged imported files are not charged to a new commit. Larger execution
payloads stay local. Essential larger durable changes require a documented
policy decision; never split a payload to evade the limits. These are this
project's size choices, not claimed GitHub limits. Aggregate directories omit
Git internals and environment package trees; apparent byte totals can differ
from `du` because of hard links, sparse files and excluded directory metadata.

For fresh tasks, follow [AGENTS.md](../AGENTS.md): inputs are immutable,
transformations write separate derived files, and each attempt has its own run
ID, input identities and configuration. Author source under `code/`, keep small
indispensable inputs in `fixtures/` and preserve compact outputs under the run's
`results/`. Global `src/` and `source/` exclusions protect downloaded legacy
trees; check that essential new code is not silently ignored. Extend both the
ignore rules and validator for an essential new format. Tracked notebooks must
have execution counts and cell outputs cleared.

Use `/srv/ai/work/rad/<topic>/<run-id>/` for large inputs, derived data, downloaded
repositories, environments, binaries, raw logs and temporary files. On other
machines choose a writable equivalent. Use separate directories per task/run;
do not overwrite inputs with results or reuse another task's writable build.
Create/check the topic's `.gitignore` before execution. An ignored topic `work/`
is an alternative when external storage is unavailable.

Stage only the reviewed task-owned paths with Git, then run:

```bash
git diff --cached --stat
git diff --cached --check
python3 tools/archive_workspace.py audit --staged-only
```

This audit checks changed indexed bytes and does not require unrelated unstaged
edits to be committed or reverted. Commit the durable task outcome and recovery
material, push the appropriate branch and verify the remote commit. Authentication
or network failures must be reported with the local SHA and remaining work.

For an explicit bulk import, `tools/archive_workspace.py` selects by role,
format and size, then stages those paths across the managed workspace. It
generates size-specific .gitignore entries so
a later broad add does not silently import oversized result files. Existing
campaign .gitignore files are preserved, and bounded raw contracts are staged
explicitly through their exclusions. `storage/` is ignored local bookkeeping.

```bash
python3 tools/archive_workspace.py plan
python3 tools/archive_workspace.py stage
python3 tools/archive_workspace.py audit
```

The audit checks indexed bytes against the worktree, artifact policy, nested
repositories/symlinks and recognizable credential formats. It prints file
names and finding categories, never matched credential values. It is not a
comprehensive secret-detection guarantee; review new content before a public
push. Oversized indexed blobs are rejected from their metadata without loading
their contents. The total staged-content budget prevents a large collection of
individually small files passing the size check. It records the outcome in
`storage/publication-audit.json`. The whole-index form above also checks existing
tracked material; ordinary task completion uses `audit --staged-only`.

Validate the guardrails independently of the research workloads with:

```bash
python3 -B -m unittest discover -s tools -p 'test_archive_workspace.py' -v
```

The public [local-artifacts.json](local-artifacts.json) gives directory
aggregates, the largest working files and authoritative manifest locations.
The complete local exclusion inventory is
`/srv/ai/research/storage/local-inventory.jsonl`. Known original hashes remain
in their original manifests; this inventory does not invent hashes for files
which lack one or rehash tens of gigabytes of payload unnecessarily.

Token-ID arrays and request-message payloads are local data rather than compact
results. Large row-level JSON results have bounded scalar/header exports in
`docs/compact-results/`; the original files remain unchanged. These exports
explicitly mark omitted arrays/strings and are not drop-in inputs for the
research scripts. Workload catalogs and manifests retain provenance and
reproduction addressing.

A fresh clone contains the code and compact evidence. To reproduce measured
GPU runs, provision the exact weights, tape/initial-state sidecars, source and
build dependencies listed in the relevant campaign, then follow its frozen
reproduction commands. Existing binaries must match recorded hashes; ordinary
launchers never auto-update or rebuild them. A path/hash manifest cannot recover
a lost tape: keep a separate storage backup of irreplaceable raw evidence.

For each new topic, preserve the brief, source and external-source patches,
pinned dependencies, configurations/seeds, compact evidence and ordered
reproduction commands. `input-manifest.json` identifies acquisition and input
roles; `artifact-manifest.json` identifies required external bytes, sizes/hashes
and download/regeneration or persistent backup locations. A local-only source
commit or an unbacked local raw-data path is a recovery gap, not a reproducible
backup. Exercise a representative reproduction command and record its limits.

Historical bootstrap scripts describe the original laboratory setup. Do not
rerun its Git initialization to create a nested repository inside the study;
use `/srv/ai/research` as the Git root. Runtime/source checkouts retain their
own independent Git metadata and are excluded from this shared record.

Use the campaign's natural token/work denominator and original limitations.
Forced replay identity is not proof of natural-generation quality. Repository
organization introduces no new measurement or scientific claim.
