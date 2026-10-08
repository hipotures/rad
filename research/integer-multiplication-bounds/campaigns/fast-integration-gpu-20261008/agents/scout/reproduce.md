# Scout acquisition, verification and continuation

The [input manifest](input-manifest.json) records obtainable public commits,
source/archive hashes, license identities, selected file lists and recovery.
External source archives contain downloaded third-party code; they are not
tracked campaign artifacts. Restoring one needs only GitHub CLI, tar and
the manifest's repository/commit. No dependency remote is written.

For example, restore the PR40 source used in the bounded verification:

```sh
set -e
TASK_WORK_ROOT=/srv/ai/work/rad/integer-multiplication-bounds/fast-integration-gpu-20261008
TASK_SOURCE="$TASK_WORK_ROOT/repos/scout/croc-pr40-e3bf3ab0cb1e"
test ! -e "$TASK_SOURCE"
test ! -e "$TASK_SOURCE.tar.gz"
mkdir -p "$TASK_SOURCE"
gh api repos/rohanarun/integer-mult-bounds/tarball/e3bf3ab0cb1ec48588e279b31a97e7a49c72f99e > "$TASK_SOURCE.tar.gz"
tar -xzf "$TASK_SOURCE.tar.gz" --strip-components=1 -C "$TASK_SOURCE"
```

Use fresh task-owned locations if these paths already contain a validated
snapshot. Validate each consumed file against `consumed_source_hashes` in
the manifest before making sources read-only. The Colkitt review input uses
selected contents files rather than a full archive: `gh api` at each listed
`contents/<path>?ref=<commit>` returns base64-encoded content, with exact
file hashes in the manifest.

The representative verification exercised in this campaign is:

```sh
PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 python3 "$TASK_SOURCE/research/copied-both-reversed/geometry.py"
```

It passed in0.565 seconds with exit0 and unchanged source hashes. The
[receipt](bounded-pr40-verification.json) preserves the exact environment,
command, UTC times, output and external log hashes. The default checks saved
complete data-family evidence, inherited finite restriction/rank-cut
controls, all4071 individual source lines, all48 complements and all10 exact
rational bad-prime pairs. Its printed multi-million-pair totals refer to
the pinned upstream complete run, not a fresh run by the scout.

The source's `--full` additionally compiles and replays all4073300 pairs;
it was deliberately not used here. A full replay requires a writable COPY
in owned derived storage because it builds into the source tree. It should
not be launched in the immutable snapshot or during an allocation with zero
CPU-bound slots. That optional complete path is the source author's retained
reproduction, not an exercised new campaign check.

The lightweight acquisition script can collect a current read-only poll:

```sh
python3 research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008/agents/scout/scout_poll.py --work-root "$TASK_WORK_ROOT" --search 'integer multiplication kappa'
```

The campaign initially used `scout_watch.py` at a600-second cadence with the
fixed UTC cutoff from protocol.json. The user's14:24 indefinite extension
revoked that closing deadline, as recorded in
[extension-protocol.json](extension-protocol.json). Continued monitoring uses
the same interval with `--until` omitted:

```sh
python3 research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008/agents/scout/scout_watch.py --work-root "$TASK_WORK_ROOT" --interval 600
```

Stop the task-owned watcher only at explicit campaign closing. API metadata polls are
historical observations; repeating an API request later does not recreate
the same minute's repository state. The pinned source commits are the
reproducible scientific inputs. Mutable RaD branches/PRs and uncertain
current derivatives are explicitly excluded. Early unfiltered external API
acquisitions are unconsumed provenance, not part of published mathematical
evidence; use the scoped compact polls and bounded-verifier logs.

Discovery now selects only PR/head metadata inside `gh`, omitting PR bodies
and commit patches before delivery to the collector. Held current producer
derivatives are filtered as recorded in
[independence-exclusions.json](independence-exclusions.json).
[metadata-selector-validation.json](metadata-selector-validation.json)
records four bounded live API checks of those selections; it is an API
integrity check, not a mathematical baseline replay.

[input-integrity-review.json](input-integrity-review.json) checks 79 consumed
source files, 7 archives and one versioned PDF across 10 inputs, plus scout Python syntax and
retained JSON framing. [The intake](intake.md) gives source credit and
chronology; the individual interface reviews state their exact scope.
