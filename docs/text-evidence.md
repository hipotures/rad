# Complete text evidence publication

The operator requested complete gzip copies of `.json`, `.jsonl`, `.log` and
`.txt` evidence before commit, followed by publication of all eligible ignored
text in the repository. The implemented path keeps original files unchanged,
creates reviewed copies under `evidence/`, commits them and pushes the canonical
repository. This is repository maintenance; no research measurements are rerun.

## Policy

Each complete gzip file must be **strictly smaller than 10 MiB**, or 10,485,760
bytes. The limit applies to the compressed file, not its expanded size. Never
split a source file or payload to meet the limit. Compression uses level 9,
mtime 0 and an empty gzip filename; identical stable source bytes produce
identical gzip bytes. The atomic packer refuses an existing destination,
symlinks, changed sources and incomplete publication. Original source files
remain at their original paths and are not truncated, moved or deleted.

Root ignore rules permit the four gzip formats under `evidence/`. The archive
validator reads the **indexed** bytes, checks gzip framing and CRC to EOF,
validates decompressed UTF-8, rejects NUL bytes and checks recognizable
credential patterns across chunk boundaries. Cleaning the worktree after
staging cannot hide a rejected indexed payload. Private configuration remains
excluded. These checks supplement content review; compression does not turn
private material into public material.

Complete raw request text, token-ID arrays, telemetry logs and row-level JSON
are permitted through this explicit evidence-copy path. Readable authored
source, configs, reports and compact results should remain readable. CSV is
outside this four-format change and retains its existing policy. Downloaded
source trees, environments, weights, binaries and caches remain excluded.
Historical process metadata may be preserved as evidence; an archived PID
record is never authority to stop or control a live process.

Small indispensable JSON fixtures under a research `fixtures/` directory may
remain readable, including fixed construction frame plans. They retain the
ordinary 1 MiB file limit, credential and request-payload checks, execution
directory exclusions and aggregate budget. The same large array under a
results directory remains row-level evidence and uses the complete gzip path.
This distinction does not permit downloaded datasets or execution payloads to
be relabeled as fixtures. JSON structural validation accepts exact integers
with thousands of digits without converting them to Python integers; request,
row-array and notebook-execution checks still apply.

The ordinary staged-content budget remains 20 MiB, counting whole changed
blobs. A larger import requires a durable, indexed, scoped decision. The full
2026-10-07 backfill has an explicit [one-time 512 MiB aggregate decision](text-evidence-backfill-policy.json),
while ordinary non-exempt content still has its 20 MiB budget. This decision
preserves the operator's full-import scope without dividing payloads into
commits to evade the guard. It does not change the next task's default budget.

## End-of-task commands

Run these from the repository root, replacing placeholders with reviewed paths:

```bash
python3 tools/archive_workspace.py pack-text --source <completed-text-directory> --destination <topic>/evidence/<fresh-run-id>
python3 tools/archive_workspace.py verify-text --destination <topic>/evidence/<fresh-run-id> --check-originals
gzip -dc -- <topic>/evidence/<fresh-run-id>/archive-manifest.jsonl.gz
git add -- <topic>/evidence/<fresh-run-id> <other-task-owned-paths>
git diff --cached --check
python3 tools/archive_workspace.py audit --staged-only
git commit -m "Preserve complete text evidence and task results"
git push origin <actual-branch>
```

Review the manifest's `archived` and `skipped` records before staging. Selection
is explicit rather than a silent Git hook: AGENTS.md requires this preparation
before final commit, and the validator rejects invalid staged archives.
`pack-text` recursively selects the four formats. `--paths-from <file.json>`
accepts a frozen list of relative source paths for a bounded selection; absolute
paths and parent traversal are rejected. Neither packing nor verification
stages, commits, pushes, rebuilds or benchmarks anything.

For a reviewed whole-workspace backfill, the command used here was:

```bash
python3 tools/archive_workspace.py pack-ignored-text --destination docs/evidence/ignored-text-20261007-v1
```

It scans managed repository roots, selects ignored untracked text and excludes
dependency/environment trees. It does not follow directory symlinks or silently
import external benchmark directories. The namespace already exists: repeating
the command correctly refuses to overwrite it. Choose a fresh namespace for a
new import and document any aggregate-budget decision separately.

The scoped publication audit for this import is:

```bash
python3 tools/archive_workspace.py audit --staged-only --budget-policy docs/text-evidence-backfill-policy.json
```

## Backfill and omissions

The [indexed publication audit](text-evidence-publication-audit.json) passed
for the complete import commit. The [validation receipt](text-evidence-validation.json) records exact counts,
bytes, verification scope and repairs. Each namespace has a compressed JSONL
manifest containing the source root, every selected path, original and gzip
SHA256, byte sizes, status and skip reason.

| Namespace | Archived files | Original bytes | Gzip data bytes | Manifest bytes |
|---|---:|---:|---:|---:|
| `docs/evidence/ignored-text-20261007-v1` | 19,413 | 3,510,449,673 | 320,285,448 | 1,543,326 |
| `docs/evidence/historical-process-text-20261007-v1` | 63 | 47,047 | 20,253 | 6,812 |
| Phase 2 `evidence/raw-text-v1` | 2,362 | 80,759,262 | 7,178,657 | 180,432 |
| Phase 2 `evidence/runner-logs-v1` | 26 | 897,586 | 57,969 | 2,425 |
| Phase 2 `evidence/reproduction-text-v1` | 34 | 1,320,646 | 114,710 | 4,104 |
| `docs/evidence/text-evidence-maintenance-20261007-v1` | 14 | 2,577,868 | 89,529 | 1,894 |

Total: 21,912 complete source files; 3,596,052,082 original bytes and
329,485,559 gzip bytes including manifests.

The first pass excluded 63 process records under the old transient-state rule.
A separate historical-evidence supplement retains all 63; the first manifest
is preserved rather than rewritten. One eligible original exceeds the gzip
limit: `iq3s-residency-20261004T230051Z/campaigns/q4-residency-v2-20261005T202441Z/phase-a/cost-analysis.json`,
132,050,206 original bytes. Its full compressed size was not measured: the
bounded writer detects crossing the exclusive limit and discards the temporary
output. It is not split, and the original remains local. Phase 2 raw/reproduction
archives omit 508 non-text binary files. Large tapes, binary journals, weights
and executable/environment recovery still require their original manifests
and separate storage; a Git clone is not a full execution-environment backup.

Maintenance logs and the frozen source selection are retained separately under
`docs/evidence/text-evidence-maintenance-20261007-v1`. The first oversized-copy
attempt exposed a Python gzip finalizer warning. The writer was repaired to
close cleanly before rejecting excess output; the actual oversized source was
retested successfully. Qualifying archive bytes were unaffected and all were
independently verified. An administrative invocation with a missing paths-list
failed before output creation and was corrected; it did not overwrite evidence.

## Readback and verification in a clone

Without local originals, verify retained bytes against the archive manifest:

```bash
python3 tools/archive_workspace.py verify-text --destination docs/evidence/ignored-text-20261007-v1
python3 -B -m unittest discover -s tools -p 'test_archive_workspace.py' -v
```

`--check-originals` additionally compares every retained source against the
current original and therefore requires the recorded source paths on this
host. Verification checks complete namespace membership, both SHA256 identities,
byte counts and gzip/UTF-8/credential validity. It never extracts files.

Use ordinary `gzip -dc -- <archive>` to inspect one retained file. To recover
bytes, redirect into a **fresh** output location with shell noclobber enabled;
never overwrite an existing source or run output. A standard gzip readback and
its original SHA256 were exercised during this maintenance. Archive headers
record host-local provenance; readback and clone-side verification do not
require those paths to exist.
