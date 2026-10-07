# AGENTS.md

## Purpose

This repository is the persistent execution workspace for the RaD project.

The canonical remote is `hipotures/rad` on GitHub. On this host the checkout root is `/srv/ai/research`; the old timestamped study is a child directory. If launched elsewhere, locate this checkout or use a clone of the canonical repository and verify its origin before creating task files. Do not treat an arbitrary current directory as the research repository.

Historical `/srv/ai/benchmarks` and the timestamped residency laboratory are parts of the same research record. Durable benchmark files are versioned under `benchmarks/`; user-owned serving starters/configurations are under `launchers/`. Read `docs/workspaces.md` and the shared index before deciding that only the current directory belongs to the project. External execution locations remain stable; the recorded mappings distinguish the Git snapshot from the live workspace.

Agents working here are research executors. They are given a concrete goal and are expected to investigate, test, analyze, implement, measure, document, and preserve results. Do not stop at planning when the requested work can be carried out.

The surrounding ChatGPT project is used for discussion, synthesis, interpretation, and deciding the next research direction. This repository is where those directions are executed and made durable.

## Language

Communication with the user may be in Polish or another language, but all repository artifacts created or modified by agents must be written in English unless the current goal explicitly requires a different language.

This applies to documentation, README files, reports, research notes, source code, comments, identifiers where practical, scripts, configuration descriptions, data schemas and field names, reproduction instructions, and commit messages.

Quoted source material, external data, logs, and tool output may remain in their original language when preserving them verbatim is useful. Any agent-written explanation or annotation around them must be in English.

## Goal Execution

Treat the user's current goal as the primary objective.

Before acting:

1. Understand the requested outcome, constraints, and success criteria.
2. Inspect the current repository state and relevant existing research.
3. Determine whether the goal continues an existing investigation or starts a new research topic.
4. Choose the smallest set of actions or experiments that can produce decisive evidence.

Do not ask unnecessary questions. Resolve ordinary implementation and research choices autonomously. Ask only when a missing decision would materially change the objective, create significant irreversible risk, or require information that cannot reasonably be inferred.

Do not merely propose experiments when they can be run. Do not merely describe code changes when they can be implemented and verified.

## Repository Synchronization

At the start of substantive work:

- find the repository root with `git rev-parse --show-toplevel`; do not initialize a nested RaD repository
- inspect Git status and current branch
- synchronize with the remote repository when it is safe to do so
- inspect relevant README files, reports, code, data, and history
- preserve unrelated user or agent changes

Never discard, overwrite, reset, or rewrite unrelated work to obtain a clean tree.

Do not force-push or rewrite shared history unless explicitly instructed.

Use `gh` as the primary interface for GitHub repositories, issues, pull requests, commits and releases. Read issue bodies with `gh api repos/<owner>/<repo>/issues/<number>`; fetch comments separately when needed. Do not use a browser or web search for content which `gh` can retrieve. Ordinary Git fetch/commit/push operations remain appropriate for synchronization.

## Research Initialization

Classify the task before creating new structure.

If it continues or extends existing research, work in the existing research directory and preserve its accumulated context. Do not create a parallel directory for substantially the same investigation.

If it is a genuinely new research problem, create:

`research/<short-kebab-case-name>/`

and add a concise `README.md` describing:

- topic and scope
- primary objective or question
- important initial assumptions or constraints
- current status

A new experiment, benchmark, or variation does not by itself require a new research directory.

Keep the research README useful as an index and current-state summary. Link to detailed reports, experiments, data, and conclusions rather than turning it into an unbounded log.

For a new task with no prior history, use this startup sequence:

1. Record the brief, objective, constraints and completion criteria in the topic's `GOAL.md` (or relevant existing documentation for maintenance). Preserve the supplied prompt where useful, omitting credentials and confidential values from tracked files.
2. Create the topic README and record assumptions, uncertainties and the intended work. A repository maintenance task belongs in existing `tools/` or `docs/`; it does not need a fictitious research topic.
3. Choose separate locations for immutable input data, durable source/results and disposable execution files before downloading or generating anything.
4. Create the topic `.gitignore` and check the shared ignore rules before cloning dependencies, installing an environment, compiling or collecting data.
5. Record input provenance and the planned run configuration, including seeds and metrics when relevant.
6. Implement/run the smallest useful validation, then carry out the authorized work. Preserve failures and meaningful partial evidence.
7. Produce a report and executable reproduction instructions, review persistence, commit the durable changes and push them.

Do not carry an old campaign's inputs, split, clock, deadline, model settings, output directory or conclusions into an unrelated task. The timestamped IQ3_S/Q4 directory is historical research, not a template of mandatory settings for every goal.

## New-Task Directory and Storage Contract

Use the following roles for new topics. Create only the subdirectories needed for the task; keep their meaning consistent.

```text
research/<topic>/
  README.md                  # Index, status and conclusions
  GOAL.md                    # Brief, scope and completion criteria
  .gitignore                 # Topic-specific execution/payload exclusions
  input-manifest.json        # Input identities and acquisition/generation
  artifact-manifest.json     # External artifact locations and recovery
  reproduce.md               # Commands, prerequisites and expected checks
  code/                      # Authored source, scripts and dependency patches
  configs/                   # Portable configuration, locks and seeds
  fixtures/                  # Small inputs/reference cases needed for tests
  runs/<UTC>-<name>/
    protocol.json            # Exact version/settings/input IDs for this attempt
    results/                 # Compact results and essential measurements
    report.md                # Outcome, failure or partial result
  reports/                   # Cross-run analysis and exportable figures
```

Authored source goes in `code/`. Global `src/` and `source/` exclusions protect legacy source clones; do not put new authored code there and silently lose it. Check whether every essential new file is ignored with `git check-ignore -v <path>`, and correct a narrowly scoped rule when needed. New languages/formats must be permitted by both `.gitignore` and the archive validator before publication.

Large/disposable work belongs outside the Git checkout by default. On this host use a task-owned root such as `/srv/ai/work/rad/<topic>/<run-id>/`; elsewhere choose and record a writable equivalent. An optional `RAD_WORK_ROOT` configuration must not embed a machine-specific absolute path in otherwise portable code. Keep separate subdirectories such as:

```text
inputs/     # Original large inputs; read-only after acquisition/validation
derived/    # Preprocessed/regenerable data
repos/      # Downloaded third-party source checkouts
builds/     # Compiled binaries and build-system output
envs/       # Virtual environments and dependency caches
raw/        # Large captures and measurements
logs/       # Full execution logs
tmp/        # Disposable temporary work
```

If local work must live inside the topic, use an ignored `work/` directory. Do not compile into `code/`, copy a downloaded repository into the durable tree, create nested Git links, or stage a symlink to a large external directory. Record external paths in manifests instead. Do not reuse another task's writable build/output directory.

The topic `.gitignore` must exist before execution and cover any task-specific outputs. A minimal starting point is:

```gitignore
/work/
/downloads/
/repos/
/build/
/builds/
/envs/
/raw/
/logs/
/tmp/
/.venv/
/.cache/
__pycache__/
*.pyc
*.pid
.env*
```

Check that generated files really are ignored. `.gitignore` does not remove files which are already tracked and cannot enforce a byte budget by itself. Never delete irreplaceable raw evidence as a way to clean Git status.

## Input and Run Integrity

Assign stable IDs to inputs and separate acquisition, transformation and evaluation. The input manifest records the original source/URL or generator, revision, local or relative location, byte size and available hash, plus acquisition parameters, seeds and usage/split where relevant. Mark unavailable provenance explicitly.

Keep originals immutable. Transformations write separate derived files and record their source input IDs and commands. Do not overwrite inputs with results, reuse a successful output filename for a failed retry, mix train/evaluation roles, or silently replace an existing run. Each attempt/repair gets its own run ID and records source/config/input identities. Treat scientific correctness requirements in the current goal as authoritative.

Raw data, logs and compact results have different roles. Save all important results, including negatives; publish the compact evidence needed to assess them. A reduced/aggregated export must link to its original and state what was omitted. Never describe omitted raw data as present in the Git clone.

## Research Method

Prefer:

observation -> question -> hypothesis -> experiment/investigation -> evidence -> conclusion -> next step

Distinguish clearly between:

- established facts
- measured results
- conclusions derived from evidence
- hypotheses
- speculation
- unknowns

Never promote an assumption or hypothesis to a fact.

When several explanations are plausible, rank them and prefer experiments or evidence that discriminate between them.

For external research, prefer primary sources, source code, official documentation, papers, specifications, and direct developer/researcher statements. For fast-changing subjects, verify the current state and record relevant dates, versions, revisions, or commits.

When documentation and implementation disagree, investigate the implementation.

## Experiments and Measurements

For experiments:

- define the question and baseline
- change as few variables as practical
- control unrelated conditions
- record exact configuration and methodology
- define measurements before interpreting results
- preserve important raw measurements
- explain what observed outcomes imply

Prefer small discriminating experiments before large sweeps.

Investigate anomalies instead of discarding them. Preserve useful negative results and failed approaches when they constrain future work.

Do not compare measurements as equivalent when conditions differ. Normalize where useful and calculate derived metrics such as ratios, percentages, speedups, efficiency, or cost/performance.

## Development and Debugging

Prefer simple, robust, maintainable solutions.

Avoid unnecessary frameworks, abstractions, dependencies, and architecture.

Before replacing a working approach, establish that the replacement provides a meaningful advantage for the actual objective.

When debugging, collect evidence that separates plausible causes. Prefer targeted instrumentation and source inspection over large undirected log collection.

Verify important changes with tests, reproductions, benchmarks, or direct inspection as appropriate.

## Artifacts and Persistence

Important results must not exist only in terminal output, chat history, temporary directories, or an agent's local workspace.

User-owned launchers and their exact configurations are durable source, even when they currently live outside the checkout. Preserve them and their provenance; a compiled executable or model is a separate local artifact. Check historical benchmark/launcher roots when importing related work. Do not move live files or rewrite launcher paths just to make them tracked. Preserve useful report shortcuts as portable relative Markdown links instead of absolute filesystem symlinks.

Store durable, reasonably small artifacts in the relevant research directory, including as appropriate:

- reports and conclusions
- experiment and benchmark results
- important raw measurements
- research notes and source findings
- reproduction instructions
- configurations and manifests
- scripts and source code
- compact JSON, CSV, or text data

Preserve enough methodology, parameters, versions, commands, measurements, limitations, and provenance for another agent to continue or verify the work.

For important external or large artifacts that should not be committed, record where they came from, their version or hash when useful, and how to obtain or reproduce them.

Do not commit model weights, large datasets, large binaries, caches, virtual environments, build artifacts, downloaded source trees or large temporary outputs. A JSON/CSV extension does not make a multi-gigabyte dump suitable for Git. Do not split a payload across small files or commits to evade the storage policy.

Default publication limits are 1 MiB per durable file, 4 MiB per source patch and 20 MiB of staged file content per commit. These are project guardrails, not GitHub service limits. Existing imported history is retained. Essential larger durable changes need an explicit, documented policy decision; large execution payloads still belong in local/external storage.

Never commit secrets, credentials, API keys, tokens, private keys, or private configuration.

## Reproducibility and Recovery Minimum

Before finishing, ensure Git preserves the material whose loss would prevent another agent from understanding or regenerating the work:

- brief/scope, methodology, input definitions/provenance and the exact run configuration
- authored source, scripts, small indispensable fixtures and all modifications to external source
- pinned dependency/source versions, build commands, configuration, seeds and environment requirements
- compact outcomes/measurements, validation results, limitations, failures and conclusions
- ordered commands to obtain inputs, build/run and regenerate the retained results
- manifests for required large artifacts, with locations, sizes, available hashes and acquisition/regeneration instructions

For an external checkout, retain its upstream URL and an obtainable base commit plus patches/new files required to reconstruct changes. A local-only commit SHA or the presence of a modified ignored checkout is not a sufficient source backup. Do not push changes to a dependency's remote without authorization.

For each essential large artifact, say whether it is downloadable, deterministically regenerable, or irreplaceable. A local path/hash cannot recover lost bytes. Irreplaceable data needs an identified persistent storage/backup location; if one is unavailable, preserve what is feasible and explicitly report the recovery gap. Do not claim full reproducibility until the required material and commands are actually available.

Test the relevant reproduction path or a bounded representative case, and state exactly what was exercised. Avoid relying solely on shell history, an installed environment, machine-local binaries or this conversation. Remove notebook execution payloads from tracked notebooks and preserve significant outputs as separate compact results.

## Reports

A research conclusion should state, when applicable:

- question or objective
- methodology
- evidence and measurements
- result
- interpretation
- confidence and limitations
- unresolved questions
- recommended next step

Use precise language. Separate what was measured from what is inferred.

For external sources, preserve enough citation information to identify the source later, preferably including URL, title, date/version, and commit or revision where relevant.

## Git Discipline

**Commit and push are mandatory for every task with durable changes.** Before reporting completion, commit the task-owned artifacts, push them to the appropriate branch of `hipotures/rad`, and verify that the remote contains the commit. A local-only commit is unfinished work; do not stop after committing or leave publication for a separate goal.

Use Git as the shared research record.

During long investigations, make meaningful milestone commits when they preserve substantial progress or important evidence.

Before completing a goal:

1. Review changes against the task's starting state; preserve unrelated user/agent edits and pre-existing staged files.
2. Complete relevant checks and the recovery minimum above. Leave execution payloads in ignored/external storage.
3. Update the topic README/report, manifests and repository index when relevant.
4. Stage only explicit task-owned paths, then inspect the staged diff, file sizes and total content. Do not use `git add -A`, `git add .` or `git add -f .` as a substitute for scope review.
5. Run `python3 tools/archive_workspace.py audit --staged-only` and resolve findings. It inspects the staged bytes, enforces size/role limits and checks recognizable credential formats; it does not replace content/recovery review.
6. Commit the relevant changes with a descriptive English message.
7. Push to this repository's appropriate upstream branch and verify that the remote contains the commit.

Unrelated pre-existing staged changes must not become part of the task commit. Preserve their contents and staging state while isolating the task's commit, for example in a separate worktree. A clean status is not a reason to discard another task's work.

Typical commands, after selecting the actual task paths and branch:

```bash
git add -- research/<topic>/ <other-task-owned-paths>
git diff --cached --stat
git diff --cached --check
python3 tools/archive_workspace.py audit --staged-only
git commit -m "Record <concrete outcome> and reproduction material"
git push origin <branch>
```

`tools/archive_workspace.py stage` stages all eligible material across the managed workspace. It is an explicit bulk-import tool, not the default completion command for an individual task. Its legacy catalogs are not a substitute for a new topic's own manifests. Do not use it to capture unrelated edits.

If the remote branch advanced, integrate changes safely. Never solve a push conflict by discarding unrelated remote work.

Every task with durable changes must finish with a commit and push, including maintenance, fixes, negative results and useful partial work. Do not leave the last meaningful work only in a local commit or ask the operator to launch a separate goal just to publish it. This standing instruction authorizes routine commit/push to this repository unless the current user explicitly requests otherwise.

If authentication, network access, permissions or another actual blocker prevents pushing, make the local commit where feasible, retain the error/recovery instructions without credentials, and report the local SHA, pending work and reason. Never claim a successful push without checking it. A read-only/no-change task requires no empty commit, but pre-existing task commits must not be left unpublished.

## Completion Standard

Continue working until one of these is true:

- the goal is achieved and verified
- the available evidence supports a clear conclusion
- a well-defined external blocker prevents further progress
- further work has sharply diminishing information value relative to the stated objective

Do not claim success when verification failed or evidence is inconclusive.

At completion, provide a concise handoff containing:

- what was done
- main findings
- confidence and important limitations
- paths to relevant repository artifacts
- commit identifier(s)
- recommended next step, if any

The final handoff should make it easy for the ChatGPT discussion layer or another agent to evaluate the result and define the next goal.
