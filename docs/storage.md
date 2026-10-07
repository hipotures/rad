# Storage and reproduction

The repository root is `/srv/ai/research`; the original workspace is its
`iq3s-residency-20261004T230051Z/` child. This arrangement preserves all recorded
absolute paths. GitHub contains a selective snapshot of durable work, not an
execution-environment backup.

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

The import limits individual durable artifacts to 1 MiB, with a 4 MiB limit
for source patches. Larger files are inventoried, not removed. These are this
project’s size choices, not claimed GitHub limits. Aggregate directories omit
Git internals and environment package trees; apparent byte totals can differ
from `du` because of hard links, sparse files and excluded directory metadata.

`tools/archive_workspace.py` selects by role, format and size, then stages
only those explicit paths. It generates size-specific .gitignore entries so
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
push. It records the outcome in `storage/publication-audit.json`.

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

Historical bootstrap scripts describe the original laboratory setup. Do not
rerun its Git initialization to create a nested repository inside the study;
use `/srv/ai/research` as the Git root. Runtime/source checkouts retain their
own independent Git metadata and are excluded from this shared record.

Use the campaign's natural token/work denominator and original limitations.
Forced replay identity is not proof of natural-generation quality. Repository
organization introduces no new measurement or scientific claim.
