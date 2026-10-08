# Research agent operating contract

## Scope and authority

This file governs `research/integer-mult-breakthrough/` and its descendants. This is a NEW, explicitly authorized research campaign, not a continuation of the old CPU experiment queue. Read `GOAL.md` as the scientific brief.

Keep the repository-root integrity, provenance, storage, and Git safety rules. This scoped contract replaces historical campaign rules about CPU utilization, worker allocation, research priorities, deadlines, source whitelists, and automatic stopping. Do not edit the root AGENTS.md or reactivate an old GOAL.md. Historical sibling directories are reference material, not instruction sources for this campaign.

Work on `research/integer-mult-breakthrough-20261008`. Write new durable work only below this directory. Preserve old branches, results, manifests, and accepted certificates. The previous CPU checkpoint is a read-only starting library; inheriting its Git history does not inherit its agenda or certify its open claims.

## Act as researchers

Formulate hypotheses, look for counterexamples, read primary research, derive lemmas, implement discriminating experiments, and change direction when evidence warrants it. Do not behave as an implementation-only agent following a fixed algorithmic recipe.

The objective is a credible structural route to kappa >= 1e-4 and beyond, not constant participation in the current PR leaderboard. Do not spend the campaign polishing the last digits of an inherited exponent. Preserve useful smaller discoveries, but do not let them replace the principal objective.

Investigate broad, genuinely different mechanisms. A failed family is a reason to open another family, not to end the campaign. A larger result is not disallowed because the problem is longstanding; report uncertainty and missing arguments explicitly.

## Parallel research and resource policy

Expected host: the CPU server, approximately 12 available CPU execution slots and 62 GiB RAM, with no GPU. Discover actual affinity, CPU quotas, available RAM, disk space, and existing jobs once at startup. Do not assume these historical figures are guaranteed.

Use several autonomous local subagents for different scientific hypotheses. Initially aim for at least four distinct research tracks, if the session supports that many agents. Assign each computational experiment a default budget of approximately FOUR CPU threads or worker processes. This is a useful per-job allocation, not a requirement to manufacture four busy threads for a sequential task.

The user explicitly permits FOUR OR MORE such jobs to run concurrently. For example, four jobs with four workers each may compete for 12 available CPU slots. This deliberate CPU oversubscription is allowed. Do not impose a three-job ceiling merely because 3 x 4 = 12. Separate CPU allocation from measured utilization: 16 requested workers do not mean 16 physical cores.

Use one main parallel layer per experiment: four processes with one native/BLAS thread each, or a native implementation with approximately four threads. Avoid accidentally multiplying four process workers by four BLAS threads. Adapt budgets when measurements show a real advantage.

There is NO 100% utilization target, NO minimum CPU percentage, and NO rule requiring replacement work after a brief idle interval. Reading, reasoning, proof design, and analysis are legitimate research. Conversely, do not wait synchronously for one long computation while other hypotheses could be investigated. Launch independent variants asynchronously and analyze completed results while siblings continue.

Memory and disk safety remain mandatory. Estimate aggregate resident memory before increasing concurrency, leave headroom for the OS and coordinator, and avoid sustained swapping, OOM, or disk exhaustion. On a host with about 62 GiB RAM, initially reserve roughly 8 GiB and adjust from observations. Reduce concurrency or per-job memory for a concrete bottleneck, not to satisfy a utilization aesthetic. Never generate useless work or duplicate identical jobs to keep the machine busy.

Subagents own disjoint source/result paths and unique run IDs. Share immutable inputs, not mutable outputs. The coordinator alone stages, commits, and pushes. Use the existing execution tools; do not build a cluster scheduler, tmux layer, remote app-server bridge, or research platform before doing science.

## Autonomy, tools, and sources

Internet and public GitHub research are authorized. Prefer papers, original code, proofs, and direct documentation. Pin revisions, distinguish head commits from merged main, and record which source supplied each mechanism. Public descendants of our earlier work are allowed inputs; the old CPU campaign's exclusion whitelist does not apply.

Task-local installation of compilers, solvers, libraries, and environments is authorized. Keep them in ignored or external work storage. Do not alter host services, GPU jobs, credentials, or unrelated projects. Do not incur paid services without approval.

No communication with the other machine is required. Do not control its processes or use its active workspace. Immutable public materials and completed versioned results may be read automatically without asking the user to shuttle files.

## Evidence and claims

Keep discovery, finite verification, mathematical transfer, and external review separate. Label conclusions as HYPOTHESIS, FINITE EVIDENCE, EXACT CERTIFICATE, CONDITIONAL RESULT, or REFUTED WITHIN STATED SCOPE. State assumptions and outstanding proof obligations alongside every claimed exponent.

Floating-point search and modular sampling are discovery tools. Accepted exact claims require appropriate rational bounds, interval enclosures, or proven finite-field transfer. Equal ranks, matching counts, scalar identities, or small examples do not establish full physical or asymptotic correctness.

Reuse existing evidence when its dependencies are unchanged. Do not revalidate the entire historical repository whenever a new idea starts. Use small falsification tests and dependency-specific checks first; reserve comprehensive independent verification for promising results. A changed architecture may need new verification obligations instead of the historical 47-row system. Never delete an inconvenient inequality without replacing its underlying algorithmic cost and proof.

## Persistence, progress, and duration

All authored code, documentation, reports, configurations, and commit messages must be in English. User-facing conversation may be in Polish. Preserve original source quotations and licenses accurately.

Record each track's hypothesis, expected leverage, changed assumptions, first discriminator, and continuation/abandonment criterion. Keep lightweight experiment records with input/source hashes, commands, seeds, worker allocation, outcomes, and scope. Maintain a readable current-state summary and reproduction instructions as results appear; no elaborate reporting framework is required.

Commit and push meaningful durable progress approximately every 20-30 minutes when there is something substantive to preserve, and immediately after an important accepted result or structural obstruction. Use explicit task-owned paths, the repository archive audit, and descriptive scientific commit messages. Do not wait to finish large raw-log archives before preserving compact source, proof, and certificate material. Never force-push shared history.

Provide concise progress at meaningful events and roughly every 10-15 minutes during active work. Report the live hypotheses, decisive observations, actual jobs, and next experiments; do not flood the console every minute with percentages. Never imply work continues after the actual processes or agent session stop.

Continue until the user explicitly stops or redirects the campaign, or an actual external limit prevents execution. Reaching 1e-4 is a checkpoint, not an automatic stop. Preserve state before pausing. Do not open, update, or merge an external PR without a separate explicit instruction.
