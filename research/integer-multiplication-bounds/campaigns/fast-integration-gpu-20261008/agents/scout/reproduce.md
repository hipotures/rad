Campaign closed at the user's request. Final accepted conditional κ=5.143624568e-5; see the [final handoff](../../reports/final-campaign-handoff.md). The checkpoint narrative below is historical.

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


## GPU environment and exact DATA recovery

The exercised environment was Python3.14.7, NumPy2.5.3 and
`cupy-cuda13x==14.2.0`, with CUDA runtime13020 and driver13040 on both
local NVIDIA devices. The existing environment was read only; a fresh
environment can install the same packages with a compatible CUDA13 driver.
The runtime kernel is compiled by CuPy into each fresh owned cache.
All CPU math-library thread variables were one. Keep the entire campaign
source tree: the scout imports the coordinator's versioned
`code/gpu_changed_basis_repair.py` and its scientific dependencies.
The individual protocols bind every consumed source and CUDA hash.

The following commands regenerate the three certified DATA families in a
fresh external root. They do not repeat a fixed-basis scientific baseline.
Run from the repository root, substitute an available Python/CuPy environment,
and never overwrite an earlier completed output.

```sh
SCOUT=research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008/agents/scout
GPU_PYTHON=/srv/ai/work/rad/integer-multiplication-bounds/20261007T222521Z/envs/gpu/bin/python
REPLAY_ROOT=/srv/ai/work/rad/integer-multiplication-bounds/fast-integration-gpu-replay
mkdir -p "$REPLAY_ROOT/derived/scout" "$REPLAY_ROOT/builds/scout"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export CUPY_CACHE_DIR="$REPLAY_ROOT/builds/scout/cupy"
CANDIDATE="$SCOUT/gpu-parameter-results/completed-20261008T1553/gpu-basis-20261008T1507-device0/candidate-001.json"
BASELINE=research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008/agents/geometry/results/both-negative-data-histogram.json

# Hybrid lower ranks: all actual source pairs in two small proven fields.
"$GPU_PYTHON" "$SCOUT/code/gpu_basis_parameter_full_family_followup.py" --device 0 --seed 2026100927 --batch 8192 --candidate "$CANDIDATE" --baseline-histogram "$BASELINE" --output "$REPLAY_ROOT/derived/scout/gpu-basis-full-family-followup-20261008T1619-device0"

# Hybrid upper ranks: complementary source partitions across all24 CRT fields.
# These two commands may run simultaneously, one per device.
for DEVICE in 0 1; do
  "$GPU_PYTHON" "$SCOUT/code/gpu_basis_family_crt_wide.py" --device "$DEVICE" --seed "$((2026100937 + DEVICE))" --batch 8192 --initial-run "$REPLAY_ROOT/derived/scout/gpu-basis-full-family-followup-20261008T1619-device0" --output "$REPLAY_ROOT/derived/scout/gpu-basis-full-crt-wide-20261008T1629-device$DEVICE"
done

# Distinct both-half and five-thirds DATA families, whole family per device.
for DEVICE in 0 1; do
  "$GPU_PYTHON" "$SCOUT/code/gpu_basis_parameter_other_families.py" --device "$DEVICE" --seed "$((2026100947 + DEVICE))" --batch 8192 --candidate "$CANDIDATE" --baseline-histogram "$BASELINE" --output "$REPLAY_ROOT/derived/scout/gpu-basis-other-families-20261008T1634-device$DEVICE"
  "$GPU_PYTHON" "$SCOUT/code/gpu_basis_family_crt_other.py" --device "$DEVICE" --seed "$((2026100957 + DEVICE))" --batch 8192 --initial-run "$REPLAY_ROOT/derived/scout/gpu-basis-other-families-20261008T1634-device$DEVICE" --output "$REPLAY_ROOT/derived/scout/gpu-basis-other-crt-20261008T1638-device$DEVICE"
done

# Independent input/hash/prime/coverage binding; no GPU upper-rank replay.
"$GPU_PYTHON" "$SCOUT/code/audit_complete_data_certificates.py" --work-root "$REPLAY_ROOT" --output "$REPLAY_ROOT/complete-data-input-audit.json"
```

Expected outcomes are complete uniform nine-singleton/width21/width17/width481
histograms, zero upper-rank violations, a proven-prime product strictly
larger than the complete integer-minor bound, and PASS input audits.
The original executions and independent byte audits were exercised for all
three families. This ordered recovery description has been reviewed against
source CLI contracts; it has not been replayed in a second fresh root.
The audit uses the original scientific run names above. Fresh regenerated
UTC times, paths and raw `.npy` container headers need not reproduce a
historical receipt hash; scientific coverage, source hashes, modular pivots
and deterministic input-table hashes must reproduce their checks.
Binary pivots are regenerable, not present in Git. Complete unsplit text
archives preserve original logs and progress records, with external-array
hashes and byte sizes in the summaries.

## Authorized PR54 compatibility and finite discovery

The user explicitly authorized exact PR54/53/51 implementation intake.
The [compatibility proof](pr54-data-basis-compatibility.md) and
[receipt](gpu-parameter-results/pr54-IJ-conjugate-data-compatibility-20261008T1714.json)
bind PR54 head84eb0b067741dc2690da837743fda06d133da865, its source archive,
its actual inherited physical order and the bounded retained data verifier.
Restore that commit using `gh api repos/chafreaky/integer-mult-bounds/tarball/84eb0b067741dc2690da837743fda06d133da865`
into an owned immutable directory named
`pr54-84eb0b067741dc2690da837743fda06d133da865`; check the repository owner
against the input manifest before acquisition. Its parent
`snapshot-manifest.json` is the coordinator's pinned three-source manifest,
whose exact copy is [retained here](gpu-parameter-results/pr54-authorized-snapshot-manifest.json).
Its hash is recorded in the compatibility receipt. Copy it beside the restored
directory as `snapshot-manifest.json`; the audit expects that manifest there and verifies all consumed hashes:

```sh
"$GPU_PYTHON" "$SCOUT/code/audit_pr54_data_compatibility.py" --pr54-snapshot "$PR54_SNAPSHOT" --output "$REPLAY_ROOT/pr54-compatibility.json"
```

This is a bounded reuse check, including ten exact rational unlucky-field
controls. It never regenerates the unchanged multi-million-pair baseline.
The source-weight identity proves compatibility for both independent
conjugate choices on each axis; transposed local projector flags still need
separate profiling.

Joint finite-field discovery uses `gpu_basis_joint_field_loci.py` with
`--device 0/1 --seed <recorded-seed> --batch <recorded-batch>
--pr54-snapshot "$PR54_SNAPSHOT" --output <fresh-directory>`.
Each device covers one disjoint half of the1,073,086,564 admissible source
weight-class pairs over F65521. Two actual source fixtures are tested.
`gpu_basis_joint_boundary_loci.py` adds `--permutation <pinned-JSON>` and
checks the forced physical boundary coordinates; altered orders cannot
reuse PR54's DATA proof. `gpu_basis_joint_generic_source_loci.py` changes
the actual source fixtures rather than repeating earlier matrices.
Field-locus catalogues and exact rational reconstructed samples remain
DISCOVERY ONLY. Full source-family discrimination uses
`gpu_basis_configured_full_family.py --beta23 <fraction> --beta25 <fraction>
--candidate <actual-order-JSON> --baseline-histogram "$BASELINE"
--whole-family` with the same device/seed/batch/output options. Complete
field disagreement arrays and bounded rational controls are retained;
matching two fields alone never proves rational zero minors.

The versioned `configs/` files contain exact fresh command vectors,
source hashes, mathematical questions, seeds and fixture identities.
Queues start a successor only after an owned complete predecessor receipt
passes coverage checks. Historical PID records do not authorize controlling
a live process. The30-second `live-status.json` is a current observation;
completed compact summaries and manifests are the durable scientific record.

## New structural DATA and executed-word interface checks

The four new exact families in
[the incidence proof](changed-basis-incidence-data-proof.md) were each run
over every source pair in two fields. Their rational zero cuts are proved
by fixed incidence ranks. The complete retained field arrays supply the
nonzero lower witnesses; no new many-prime replay is needed.

For a fresh recovery of half23/negative25, use the previously defined
environment and a fresh output directory:

```sh
"$GPU_PYTHON" "$SCOUT/code/gpu_basis_configured_full_family.py" --device 0 --seed 2026101177 --batch 8192 --candidate "$SCOUT/gpu-parameter-results/joint-new-rational-basis-candidate.json" --baseline-histogram "$BASELINE" --beta23 1/51 --beta25=-1/3 --whole-family --output "$REPLAY_ROOT/half23-negative25"
"$GPU_PYTHON" "$SCOUT/code/audit_basis_full_family_incidence.py" --run "$REPLAY_ROOT/half23-negative25" --mixed-cut-receipt "$SCOUT/gpu-parameter-results/mixed-fixed23-negative25-data-input-audit-20261008T1800.json" --output "$REPLAY_ROOT/half23-negative25-rational-certificate.json"
```

The other changed families use `(beta23,beta25)=(1/51,-1),(5/3,-1)` and
`(5/3,-1/3)` with fresh seeds and outputs. The exact original protocols and
array identities are in their certificates. All four original executions,
complete-array audits, independent Q incidence cuts and targeted rational
controls were exercised. A second fresh external recovery was not run.
Expected result: `PASS COMPLETE RATIONAL UNIFORM DATA FAMILY`, no uncovered
whole-field witnesses, and one-front histogram `{1:9N,17:N,21:N,481:N}`.

The pinned PR62/57/61 snapshots are recoverable by GitHub CLI using the
fork repositories and exact commits in
[the authorized manifest](gpu-parameter-results/interval-joint-authorized-snapshot-manifest.json).
The copied manifest must sit at `SNAPSHOTS_ROOT/snapshot-manifest.json`
beside the three `pr<number>-<commit>` directories. With their hashes
validated, run these bounded audits:

```sh
python3 "$SCOUT/code/audit_interval_joint_compatibility.py" --snapshots-root "$SNAPSHOTS_ROOT" --output "$REPLAY_ROOT/interval-joint-interface.json"
python3 "$SCOUT/code/audit_joint_scalar_stock.py" --snapshot "$PR62_SNAPSHOT" --output "$REPLAY_ROOT/joint-scalar-stock.json"
```

The source/center audit `audit_source_center_basis_interfaces.py` takes
`--source-interface-receipt` and `--data-certificates` with the listed
retained receipts. Its original exercised receipt covers I+J/negative25
and all four new changed families. The coherent-flag auditor
`audit_coherent_flag_interfaces.py` takes `--snapshot`, `--graph-receipts`,
`--data-certificates` and `--output`. It needs the graph team's recovered
literal flagged word and transition bytes; regenerate them using that
team's source and configuration before invoking it on another host.
The [flag proof](coherent-coordinate-flag-transfer.md) records why a
complete DATA replay is unnecessary and why the explicit source-index
bijection is essential.

The finite tree queue config lists six new actual endpoint orders and
disjoint device class partitions. It is a recovery protocol, not a mandate
to repeat already completed finite-field questions. Source and output
locations in that historical launch config must be remapped to a fresh
owned workspace before replay. Historical PID records are never used to
control live processes. Complete per-order text is archived after each
finite run, and binary arrays remain external as described in
[the artifact manifest](artifact-manifest.json).

## Algebraically selected beta23=1/15 and changed budget words

The exact same-core rank-two cancellation selects `beta23=1/15` and its
conjugate `-1/12`. Both preserve all source and center coordinate gates.
The new complete DATA families `(1/15,1/21)` and `(1/15,-1)` were executed
and independently audited. Their certificates are
[negative25](gpu-parameter-results/one15-negative25-uniform-data-certificate-20261008T1919.json)
and [fixed25](gpu-parameter-results/one15-fixed25-uniform-data-certificate-20261008T1920.json).
Each proves the same uniform one-front histogram, using all47 exact
coefficient-free incidence upper cuts and disjoint unlucky whole-field
sets. To recover the first, use the full-family and incidence-audit commands
above with `--beta23 1/15 --beta25 1/21`, seed2026101915 and fresh output
names. The second uses `--beta25=-1`, seed2026101916. The NumPy-dependent
audit must use the declared GPU Python environment; system Python on this
host lacks NumPy. A failed system-interpreter launch performed no matrix
work and wrote no certificate.

For the changed budget256+Q word interface, first regenerate the actual
literal words and complete graph source-only receipts using the graph
team's source, pinned public inputs and selected-parent fixtures. Then run:

```sh
python3 "$SCOUT/code/audit_changed_joint_word_interfaces.py" --phase-snapshot "$PR62_SNAPSHOT" --graph-receipts "$GRAPH/results/joint-budget-Q-source-only-23.json" "$GRAPH/results/joint-budget-Q-source-only-25.json" --geometry-fixtures "$GEOMETRY/results/selected-budget-Q-joint-word-axis-23.json" "$GEOMETRY/results/selected-budget-Q-joint-word-axis-25.json" --data-certificate "$SCOUT/gpu-parameter-results/half23-negative25-uniform-data-certificate-20261008T1835.json" --beta23 1/51 --beta25 1/21 --output "$REPLAY_ROOT/changed-word-interface.json"
```

This complete finite interface audit was exercised on both new words. It
expects exactly one initial `a=-1` frame sentinel per scratch role, then
checks every subsequent event against the actual current frame. It binds
the new literal source/ordinary-output/center maps, source Q bijections,
transition/profile bytes, paid XOR counts and recomputed rank/row stock.
General conditional lifting and complete characteristic assembly remain
separate gates. A new basis profile collection must be written to a fresh
fixture rather than changing the already-bound profile fixture bytes.

Two current complete-text publications preserve distinct completed scopes:
[structural searches](gpu-parameter-results/completed-structural-20261008T1902/manifest.json)
and [new DATA families plus eight finite tree catalogues](gpu-parameter-results/completed-new-family-tree-20261008T1924/manifest.json).
Every namespace passed `verify-text --check-originals`; originals remain
unchanged. Together their gzip bytes exceed the20MiB per-commit default, so
publish them as separate scoped commits. Historical queue process IDs are
observational metadata, never authority to control a future live process.
