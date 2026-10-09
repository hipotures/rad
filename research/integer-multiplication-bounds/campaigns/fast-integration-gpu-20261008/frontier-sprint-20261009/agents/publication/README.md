# Publication generator and synthetic safeguards

Status: tested preparation only. No scientific publication package has been frozen, no real candidate script has been generated, and no GitHub mutation has been executed. The coordinator owns scientific acceptance, final frontier review, release freezing and Git publication of this research record.

The [sprint brief](../../sprint-prompt.md), section 8, requires a portable script that the user runs after independent conditional acceptance and a current-frontier comparison. The user's later requirement supersedes the brief's strict-only numerical gate: publication now requires **at least 1% relative improvement**, using exact rational arithmetic. This directory implements the script's generator and safeguards while those scientific gates are pending.

- [Generator](code/build_publication.py): creates one immutable Bash script with an embedded compressed, allowlisted payload and pinned release metadata.
- [Runtime](code/publication_runtime.py): performs read-only preparation or the user's safeguarded fork/push/PR path.
- [Synthetic tests](code/test_publication.py): exercise shell/bootstrap checks and an entirely mocked Git/GitHub publication path.
- [Provisional export helper](code/prepare_candidate_export.py): assembles only the first candidate's declared sources in a coordinator-created upstream clone; it performs no network access or Git mutation.
- [Preparation report](reports/publication-preparation-20261009.md): records the source-bound 44 authored and 21 independent passing tests, exact policy, historical export and remaining release inputs.
- [Artifact manifest](artifact-manifest.json): inventories the source hashes, complete archived evidence and recovery of the disposable export.

## Scope and safety decisions

The CLI has no mock bypass. Generated synthetic fixtures refuse network and publication paths. Tests inject an in-memory command backend into the Python driver; its GitHub URLs, fork, commit, push and PR creation are fabricated test values and are not published objects. Actual subprocess tests execute only generated `--check`/`--self-test` modes, Bash syntax checks, a synthetic blocked `--dry-run`, and disposable local Python children.

The bootstrap creates a fresh private temporary workspace, checks prerequisites, hashes the complete compressed payload, rejects unsafe/linked/duplicate/oversized archive members, checks the exact member allowlist and all member hashes, and manually writes files before running any packaged code. It retains workspace and logs on success or failure. It never modifies an existing user checkout. Publication requires Bash, Git, Python 3.8 or newer and an already authenticated `gh`; no installation, token request or authentication change is performed.

Default execution of a real frozen script performs publication. `--check` validates local integrity, `--self-test` additionally exercises local path/exact-arithmetic controls, and `--dry-run` uses read-only GitHub APIs plus a fresh local clone and staged package. The coordinator must never execute the default mode. GitHub mutations are limited to creating the authenticated user's own upstream fork when necessary, pushing a new immutable submission branch, and creating a ready-for-review PR after every gate passes. No edit, force push, merge, approval or draft reservation exists in the driver.

Every current open PR, including drafts, must match an explicitly reviewed frozen head/body/title inventory. Exact leading claims are checked against hashed certificates at their actual heads. A manually inspected source-only assertion is hashed but never executed. Lower rounded claims may use an explicitly reviewed conservative upper bound pinned to unchanged body/title/head; this is a claim envelope, not independent certification of the construction. New, closed, changed or unresolved claims require reassessment. Main must match the exact reviewed base, and its retained certificates must match pinned hashes and exact rational values. The immutable release field is `minimum_relative_improvement: "1/100"`; missing, noncanonical or weaker policies stop generation and execution. With `F` the maximum active comparable claim/bound and retained reviewed result, both runtime gates require `candidate >= (101/100)*F`. The exact 1% boundary is accepted; a lower score, equality to the frontier, or a better eligible claim stops publication. The final body states the observation timestamp and exact required score, and does not claim permanent record status or completed hosted CI.

Inherited dependency files may optionally be obtained through declared `gh` content requests using exact public repository, commit, path, byte count when available and SHA-256 pins. Each download is checked before any candidate checker runs. Larger GitHub source responses use the documented raw-content representation through `gh`. This keeps the artifact a single fully self-describing script without embedding an entire predecessor source tree or requiring another host's files. A final handoff must disclose which inherited files are downloaded rather than embedded. Whether this interpretation meets the frozen candidate's publication scope remains the coordinator's explicit release decision.

Read commands have a 45-second timeout and at most three attempts; writes have a 60-second timeout and one attempt. A partial clone is not retried into its existing destination. Network Git commands use the existing `gh` credential helper only for that command, and no token is printed. Git hooks are disabled per network/commit command and signing is disabled for the fresh local submission commit. The expanded push destination must equal the authenticated user's canonical fork URL, so a global Git rewrite cannot redirect a submission. Staged paths, bytes and modes are checked after all local checkers and immediately before commit; committed paths/bytes/modes and working/untracked state are checked before push and PR creation. Remote SHA, bytes and file modes are verified. An exact existing candidate returns its actual URL after checking files/modes, unchanged dependencies, allowlist and current head, including when upstream has subsequently advanced.

## Reproduction

From the research repository root:

```bash
SPRINT_DIR=research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008/frontier-sprint-20261009
mkdir -p "$SPRINT_DIR/work/publication"
PUBLICATION_TEST_WORK="$SPRINT_DIR/work/publication" python3 "$SPRINT_DIR/agents/publication/code/test_publication.py"
```

The tests use only synthetic inputs. Their bootstrap temporary files live under the supplied test directory and are removed with their fixtures; no real publication mode is launched. The tests do not establish scientific correctness, GitHub write permissions, eventual hosted CI success, or freedom from a race after the last API check.

The final release owner can call the builder only after explicitly freezing the scientific result:

```bash
python3 "$SPRINT_DIR/agents/publication/code/build_publication.py" \
  --spec <frozen-release-spec.json> \
  --payload-root <allowlisted-public-files> \
  --output <publication-directory>/publish_<candidate-id>.sh
```

This command does not access GitHub. It refuses an existing output and refuses an unfrozen/incomplete/non-improving release. These placeholders are not a delivered record script or authorization to publish.

## Frozen-release input contract

| Field | Required meaning |
| --- | --- |
| `candidate_id`, `candidate_digest` | Immutable scientific identity and SHA-256; a stronger result needs a new identity. |
| `status`, `freeze_approved`, `gates` | Explicit coordinator freeze at `ACCEPTED_CONDITIONAL` or `PUBLICATION_READY`; completed exact finite, conditional exponent, independent reproduction, negative-control, inherited-check, frontier-review and source/license gates. |
| `upstream`, `default_branch`, `base_sha` | `CrocSwap/integer-mult-bounds`, verified `main`, exact inspected upstream commit. |
| `exact_kappa` | Final accepted nonnegative exact integer/rational string, never a native component or proxy. |
| `minimum_relative_improvement` | Immutable canonical string `"1/100"`; candidate must be at least 101/100 of the complete current comparable maximum. No strict-only fallback. |
| `changes` | Each add/replacement's portable path, exact final SHA-256, mode 644/755 and prior base hash or null for an addition. No deletion. Optional `acquire` holds an immutable public source pin. |
| `source_fingerprints` | Hashes of unchanged mathematical dependencies. Every intentionally replaced source separately carries its exact prior base hash. |
| `protected_base_paths` | All inherited tests/licenses that must remain byte-for-byte unchanged; they cannot appear in the change allowlist. |
| `local_checks` | Optional lightweight, bounded Python argv using declared hashed files; no inline or shell command. Full discovery/certification is already complete. |
| `frontier_rules` | Complete frozen open-PR inventory plus retained main. Scout's flat retained-certificate fields are normalized by the builder. Source-only exact claims need explicit `manual_exact_assessment: true`. Unresolved/new assumption flags block generation and execution. |
| `title`, `commit_message`, `public_text` | English title/message and complete construction, pinned predecessor, verification coverage, reproduction, all conditional assumptions/exclusions, attribution, source/license inventory and AI-assistance text. |

The generator automatically states exact rational/decimal saving and improvement, inserts the publication-time observation, and makes no pre-emptive hosted-CI claim. The release owner must still review mathematical scope, source provenance, all reused contributions and licenses, privacy, and the exact allowlisted upstream diff.
