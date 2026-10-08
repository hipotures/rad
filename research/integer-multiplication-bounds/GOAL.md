# Goal: Ten-Hour Autonomous Integer-Multiplication Research Campaign

## Active deadline: explicit user extension

On 2026-10-08 at approximately 03:10 UTC, the user explicitly extended
this same campaign to **2026-10-08 12:00 Polish time (CEST, UTC+02:00)**,
which is **2026-10-08 10:00:00 UTC**. This supersedes the original
08:25:21 UTC deadline without changing the campaign ID, start time,
running experiments, scheduling or accumulated findings. The original
start remains 2026-10-07 22:25:21 UTC. The original ten-hour brief and
deadline below are retained as history. The authorized interval is now
11 hours, 34 minutes, 39 seconds. Reserve approximately the last 45
minutes, from 09:15 UTC, for final verification and publication.

Act as an autonomous mathematical researcher and experimental programmer, not merely an implementation agent. Build and test research code, formulate your own hypotheses, investigate alternatives, search the literature, inspect proofs, and pursue stronger results. Execute the research; do not stop after producing a plan, installing tools, reproducing the baseline, or building a search framework.

## Objective

Starting point: https://github.com/CrocSwap/integer-mult-bounds

Persistent research repository: https://github.com/hipotures/rad

Use a **10-hour wall-clock campaign** to seek the strongest defensible improvement to the integer-multiplication bound and its supporting constructions:

    T(n) = O(n (log n)^(1 - kappa)).

**Larger kappa is better.** For example, 2^-56 is stronger than 2^-58, which is stronger than 2^-59. Do not reverse this comparison.

The starting repository currently advertises a conditional kappa = 2^-59 result. Verify its current state and pin the revision used before relying on that value. The objective is original progress beyond the actual starting baseline, not reproduction alone. There is no prescribed target exponent, ceiling on ambition, or requirement that improvements be powers of two. Preserve small valid improvements and pursue larger ones. Distinguish a genuinely stronger construction or estimate from merely rounding the same existing margin differently.

Do not stop after the first improvement. A discovery is a milestone within the campaign, not completion of the goal.

## 1. Establish the workspace and actual resources

First locate the canonical RaD checkout, verify its Git root and origin, and read the complete root `AGENTS.md`, applicable nested instructions, the research index, and relevant workspace/storage documentation. The recorded checkout location is `/srv/ai/research`; discover the actual location rather than assuming the current directory is correct. Preserve unrelated changes and synchronize safely according to repository policy.

Check whether this investigation already exists. Extend its existing topic if it does; otherwise create a suitably named directory under `research/`, such as `research/integer-multiplication-bounds/`. Follow `AGENTS.md` for directory roles, manifests, ignore rules, source placement, evidence publication, and recovery. Create ignore rules before downloading dependencies or producing execution payloads. Do not initialize a nested RaD repository.

Before sizing experiments, inspect and record:

- CPU model, physical/logical cores, process affinity, container or VM quotas, and current load.
- Total and available RAM, swap, memory limits, and existing memory pressure.
- Both GPUs: models, available VRAM, drivers, usable compute runtimes, and existing workloads.
- Free disk space, relevant filesystems and quotas, writable work locations, and installed tools.

The expected allocation is **16 CPU cores, 2 GPUs, and approximately 160 GB RAM**. These are planning inputs, not a substitute for discovery. Use the available allocation effectively while leaving sufficient operating headroom. Set measured concurrency and memory/disk limits; avoid uncontrolled oversubscription, swapping, or OOM failures. Do not interfere with unrelated services or processes.

You are authorized to browse the internet, download research material and source code, install local dependencies, build software, and use CPU and GPU computation as useful. Choose appropriate languages, compilers, solvers, exact-arithmetic systems, and numerical libraries autonomously. Prefer task-local environments and builds. Record versions and installation commands. Do not spend money on new services, rent compute, or expose credentials without separate authorization.

Use `gh` for GitHub content as required by `AGENTS.md`; use web research for papers, documentation, and other sources. Prefer primary sources and record URLs, revisions, dates, and relevant claims.

All authored repository artifacts, code, comments, reports, configurations, and commit messages must be in English. Progress messages to the user may be in Polish.

## 2. Run a genuine time-bounded research campaign

At the beginning of execution, record the actual UTC start time and an absolute deadline exactly ten hours later. Persist the campaign ID, start, deadline, and remaining-work state. The budget includes initialization, research, validation, reporting, and publication. Do not inherit another campaign's clock or reset this deadline after a restart, context compaction, subagent launch, or successful experiment.

Use the campaign for substantive research throughout, reserving a sensible closing portion for verification, documentation, commit, and push. Manage experiment timeouts against the remaining budget. Checkpoint long searches so promising incomplete work can be resumed later.

Do not end early because:

- the baseline reproduces or a planned experiment list is finished;
- a first improvement, including 2^-58 or 2^-56, has been found;
- one conjecture fails, a solver times out, or an initial family is exhausted.

Instead, validate and preserve the result, update your understanding, and choose the next informative direction. Closing an unproductive branch is not closing the campaign. Adapt the research agenda as evidence changes; do not sleep or repeat equivalent experiments merely to consume time.

Report significant discoveries promptly, with their verification status and artifact paths, then continue without waiting for acknowledgment. Make periodic progress updates and maintain persistent checkpoints. A user stop, a real safety/resource problem, or a hard execution-platform limit can interrupt the run; report it accurately, preserve the actual elapsed time and resume state, and never claim that ten hours ran when they did not. Do not intentionally leave untracked jobs running beyond the deadline.

## 3. Understand the baseline, then explore freely

Acquire an identifiable, pinned upstream revision in the execution workspace. Keep original inputs immutable. Inspect the current README, strongest proof note and certificate, actual code, dependency audits, research logs, and relevant failed-search results. Follow the original manuscript references as needed.

Run sufficient baseline checks to establish a trustworthy comparison and measure the real computational costs. This is a calibration step, not the deliverable. Investigate inconsistencies between documentation, code, certificates, and tests. Historical notes may describe superseded bounds; establish which assumptions and constructions each statement actually covers.

Identify how finite constructions, rank/role accounting, recurrence estimates, precision requirements, and downstream parameters determine the final kappa. Recompute useful targets from the pinned source. Do not treat earlier conversational estimates, role budgets, or proposed research directions as verified constraints.

Maintain a working hypothesis ledger: proposed mechanism, evidence, predicted benefit, assumptions being changed, cheapest discriminating test, observed outcome, and next decision. Use it to avoid rediscovering the same failed idea.

Choose the research agenda yourself. Possible directions include, but are not limited to:

- New finite circuits, block decompositions, recursive summaries, cross-group sharing, or alternative combinatorial families.
- Frame-aware circuit optimization, different label constructions, or cancellations with a valid replacement transfer argument.
- Sharper recurrence, movement, guard-width, resampling, or parameter estimates; changed primitives and compositions.
- Connections to relevant literature and solver-assisted or numerical discovery followed by exact reconstruction.

These are suggestions, not a mandatory sequence or a closed list. Neither the existing architecture nor a particular circuit size, ground-set parameter, solver, or search strategy is fixed by this goal. You may combine directions, change representations, revisit a previously excluded family when its assumptions change, or pursue an unexpected promising idea.

Optimize the **actual supported final bound**, not just gate counts, runtime of a search script, or an optimistic proxy. Use inexpensive screening and small exact examples before scaling expensive searches. Allocate more resources to promising branches and stop branches whose justified bounds or evidence make further work uninformative.

Use independent processes or subagents where available and useful, with distinct questions and recoverable outputs. Coordinate shared resources and Git publication. Avoid building a general agent platform or configuring a new local LLM stack unless it clearly serves this campaign better than doing the research directly.

GPUs are available for mathematical search, numerical optimization, batch evaluation, or other useful computation, not only model inference. Use them when the problem benefits, and validate GPU routines against trusted small cases. There is no requirement to force a CPU/exact-arithmetic problem onto GPUs or keep every device busy without scientific value.

## 4. Build tools that produce trustworthy evidence

Implement and actually run the code needed for the chosen investigations. Keep it simple and inspectable. Provide reproducible configurations, seeds, candidate identities, timeouts, resource measurements, checkpoints, and commands sufficient to repeat meaningful experiments. Separate immutable reference fixtures from generated candidate results.

Keep exploratory scores separate from exact finite witnesses and transferred mathematical claims. A promising floating-point value, fewer additions, a modular solution, or a passing small test is not by itself an improved integer-multiplication theorem.

For candidates that could improve the bound:

1. Preserve the candidate and its provenance before further modification. Test small instances and compare against an independent reference where feasible.
2. Establish exact arithmetic or rigorously bounded inequalities where required. Numerical discovery may guide the search, but acceptance must not depend on floating-point rounding near a threshold.
3. Verify the relevant scalar map, scratch restoration, forward/reverse frames, endpoint identities, nondegeneracy, rank accounting, and recurrence transfer. Derive replacement obligations when using a different construction.
4. Propagate every changed assumption through the downstream proof, including precision and computational-model requirements. Compute the strongest justified kappa with explicit strict slack.
5. Attempt to falsify the result: adversarial cases, boundary conditions, independent checker or derivation, and a separate critical review where feasible. Save failures and counterexamples.

Do not silently weaken a verifier, remove an inconvenient assertion, mix incompatible proof models, or change numerical tolerances to certify a preferred answer. A justified change of mathematical assumptions must come with a corresponding argument, tests, and explicit status.

In particular, introducing cancellations or new scalar operations does not automatically preserve a cancellation-free circuit's frame proof. Respect the distinction between the scalar computation's field and the rational frame/rank construction. Finite-field evidence needs a justified lift before it can certify a rational construction.

Keep the computational model explicit. A result on a stronger machine model is not a direct improvement of the fixed-model baseline. Do not equate a successful arithmetic certificate with a proof of all upstream algorithmic interfaces. If an upstream dependency remains assumed, retain that conditional status. If a baseline defect is found, record and investigate it rather than building a stronger claim on an invalid premise.

Do not require a complete formalization or full multiplication-machine implementation before any research can proceed. Match verification effort to each claim and state precisely what remains unproved.

## 5. Preserve the investigation continuously

Maintain a readable topic README, the goal and campaign clock, resource/environment inventory, input/dependency manifests, experiment ledger, current-best verified result, promising unverified candidates, and an evolving report. Use the existing repository conventions rather than creating unnecessary duplicate documents.

For each meaningful attempt retain its hypothesis, code/configuration revision, commands, inputs, seeds, time/resource use, result, verification status, interpretation, and reason for continuing or stopping. Preserve important negative results and reproducible counterexamples, not just successful candidates.

For modified external code, preserve an obtainable upstream base revision plus all required patches and authored files in RaD. A modified ignored checkout or a local-only dependency commit is not adequate persistence. Keep downloaded repositories, environments, caches, large logs, binaries, and other execution payloads in ignored/external storage, with recovery manifests as required by `AGENTS.md`.

Make meaningful milestone commits and push durable progress during the campaign when safe. This goal authorizes normal commit/push to the appropriate branch of `hipotures/rad`; do not impose local-only persistence. Do not publish to the upstream research project's remote or contact its authors without separate authorization.

## 6. Final validation, report, commit, and push

Before the deadline, stop launching work that cannot be usefully completed or checkpointed. Recheck the strongest retained result, exercise its reproduction path, and finish a report covering:

- The pinned starting baseline, final best supported result, improvement mechanism, and exact comparison.
- Explored directions, meaningful failures, unresolved candidates, and remaining proof obligations.
- What was computed versus derived mathematically, and the precise conditional or verification status of every headline claim.
- Actual elapsed time, CPU/GPU/RAM/disk usage, environment, and commands to reproduce or resume.
- The most promising next investigations, with concrete evidence explaining their priority.

Check upstream developments again near the end when feasible. Compare separately against the pinned starting revision and any newer available result. Do not claim novelty merely because something is absent from the starting checkout; distinguish independently rediscovered, genuinely new, and not-yet-literature-checked findings.

If no stronger bound was established, say so plainly. Preserve useful tools, tested constructions, exclusions, counterexamples, and search evidence without presenting them as a theorem-level improvement. Do not discard a partial improvement because it fails to cross a power-of-two milestone.

Follow the repository's publication procedure: review task-owned changes, complete recovery manifests, package eligible evidence, stage explicit paths only, and run the prescribed staged-content audit, currently:

    python3 tools/archive_workspace.py audit --staged-only

Resolve issues, commit the durable task artifacts, **push to the appropriate branch of `hipotures/rad`, and verify that the remote contains the final commit**. Update the research index where appropriate. Preserve unrelated work and do not rewrite shared history. If publication is genuinely blocked, keep the local commit and document the actual error, pending publication, and recovery steps; never report an unverified push as successful.

The final user-facing handoff must include the strongest result and its status, actual campaign duration, report and reproduction paths, commit SHA, branch, and verified push status.

**Begin now: inspect the environment and repository, establish the clock, and conduct the research. Keep investigating until the campaign's closing phase rather than stopping at implementation, reproduction, or the first discovery.**

## Subsequent execution steering, 2026-10-08

The user explicitly requested sixteen CPU worker processes for useful
independent exact tasks, delegated calculations, and preparation of the
next batch while computations run. This supersedes earlier twelve/fourteen
process headroom choices. The campaign deadline is unchanged; aggregate
RAM remains capped at 96 GiB and nested BLAS/OMP threads remain one per
process. Measure verified candidates and meaningful experiments per hour,
retain deterministic identities/checkpoints, and continue mathematical
exploration rather than building generic orchestration infrastructure.

## Major upstream update received during the same campaign

The user reported the new CrocSwap compact-control conditional claim
kappa=83/10^12, with bit ground50 and independent complex ground25. Fetch
and preserve its exact revision, critically examine the new wider-control
movement, recursive full-field layout, exceptional-address repair and
separate complex interface, then maximize the strongest defensible saving.
Reassess which previous results remain useful and combine valid interfaces;
continue original mathematical constructions and productive concurrent
experiments. Preserve successful and failed old work. The original deadline
2026-10-08 08:25:21 UTC remains immutable. Finding an improvement is a
milestone, never a reason to stop. Distinguish numerical screens, exact
finite certificates and complete conditional proofs. Commit and push all
durable results with verified remote publication.

## Seventh campaign checkpoint

The same active campaign now independently reviews the h51 bit witness with
502,265 roles and exact conditional saving
`31879574566994548341758160620003/10^40`. The full source, dirty controls,
finite review and exact arithmetic are linked from
[the composition report](reports/odd51-composition.md). The preceding h50
checkpoint is retained unchanged. A separately reviewed h28 controller
construction has 92,309 roles; it does not itself change the bit-limited
headline. Contiguous Bruhat-pivot batching and joint DAG/controller rewrites
are new hypotheses requiring their own complete transfers. Continue to the
user-extended 2026-10-08 10:00 UTC deadline without resetting the campaign.
