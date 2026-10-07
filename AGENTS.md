# AGENTS.md

## Purpose

This repository is the persistent execution workspace for the RaD project.

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

- inspect Git status and current branch
- synchronize with the remote repository when it is safe to do so
- inspect relevant README files, reports, code, data, and history
- preserve unrelated user or agent changes

Never discard, overwrite, reset, or rewrite unrelated work to obtain a clean tree.

Do not force-push or rewrite shared history unless explicitly instructed.

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

Do not commit model weights, large datasets, large binaries, caches, virtual environments, build artifacts, or large temporary outputs unless specifically justified.

Never commit secrets, credentials, API keys, tokens, private keys, or private configuration.

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

Use Git as the shared research record.

During long investigations, make meaningful milestone commits when they preserve substantial progress or important evidence.

Before completing a goal:

1. review repository changes
2. remove accidental temporary artifacts
3. update the relevant research README if status or conclusions changed
4. ensure important results and reproduction material are preserved
5. commit the relevant changes with a descriptive message
6. push the commits to the remote repository

If the remote branch advanced, integrate changes safely. Never solve a push conflict by discarding unrelated remote work.

A substantive research task is not complete until its important results are committed and pushed, unless pushing is impossible. If blocked, document the reason and report it explicitly.

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
