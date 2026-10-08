# Independent fast-integration research: GPU track

## Activation and objective

This file is the research prompt for the directory containing it. Preparing, downloading, or reading it for setup does not start a campaign. Start only when the user explicitly launches this goal.

Conduct 120 minutes of autonomous mathematical research on stronger defensible conditional bounds of the form `T(n) = O(n (log n)^(1-kappa))`. Larger kappa is better. Integrate compatible recent discoveries and develop original ideas; reproduction and integration alone are not the objective. There is no fixed numerical target and no requirement to preserve the old RaD construction.

Record the real UTC start, start commit and deadline once in this directory. The deadline is start plus 120 minutes, including initialization, experiments, review, reporting and publication. Resuming the task does not reset it. Reserve approximately the final 15 minutes for final checks and publication while useful bounded experiments finish. Finding an improvement is a milestone, not a stopping condition: preserve it, report it briefly and keep searching until the closing phase. Do not launch work that cannot finish or checkpoint within the remaining budget.

Keep the currently configured research profile and local subagent workflow. Do not revert to earlier campaign worker limits, repeat baseline initialization, or rebuild research infrastructure. This is a new isolated campaign on the same mathematical subject; the old campaign and the separately prepared research-system project stay untouched.

## Your workspace and exclusive ownership

- Execution host: `gpu`.
- Existing repository checkout: `/srv/ai/research`.
- Your working and durable-output directory: `research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008/` relative to the repository root.
- Your exclusive research branch: `research/fast-gpu-20261008`.
- Historical RaD reference: commit `6b32837aee0561af85e4efaca21af07b9f2749d2` and its existing topic reports, sources and evidence.

Work from your campaign directory. Put every new authored file, experiment, proof, certificate, report and compact measurement under it. Treat all previous campaign files, shared indexes, root instructions and infrastructure as read-only. Copy or adapt relevant source into your own directory and record provenance instead of editing historical files. Do not initialize a nested repository or create another checkout merely for this task.

Use the dedicated branch in this host's existing checkout. If already on it, continue; otherwise create or switch to it safely from the prepared starting state. Never discard unrelated modifications or staging. Do not push research commits to main, merge the other campaign, force-push, or publish upstream pull requests. Your final results remain on your dedicated branch for later comparison.

Give local subagents distinct task-owned subdirectories within this directory. Only the coordinating agent performs Git index/branch/commit/push operations; computational subagents write their owned files and return their paths and results.

## Independence

Another independent campaign may be running on the machine named `cpu`. Do not communicate with it, connect to its host, delegate to it, read its new campaign files, inspect its branch, or consume its unpublished results. Do not configure SSH tunnels, App Server RPC, remote Codex clients, tmux, or inter-host synchronization. Public prior literature and the completed RaD history are allowed common inputs. Locally spawned subagents on this machine are required and are not prohibited by this independence rule.

## Hardware and sustained useful throughput

Available allocation: **16 CPU execution slots, approximately 160 GB RAM, and two NVIDIA RTX 4090 GPUs with approximately 24 GiB VRAM each**. The 16 CPU slots are the usable budget; do not infer an extra pool from the physical CPU model or SMT specifications.

Use all 16 available CPU slots during parallelizable compute phases. Do not impose an arbitrary 8-, 12-, or 14-worker ceiling. Take one short live snapshot of usable cores, memory headroom, free disk, GPU availability and unrelated workloads; do not run a hardware benchmark or repeat the earlier connection investigation. A real lower availability or memory bottleneck must be recorded rather than ignored.

Spawn and use local research subagents, not merely serial shell commands. Delegate substantive computational branches and targeted proof criticism. Keep useful independent experiments running asynchronously while the coordinator reads, reasons, writes new code, reviews results or commits. Do not repeatedly wait for a whole batch to finish before preparing the next experiment. Keep a small supply of distinct ready experiments, using existing execution facilities and minimal task-local scripts rather than building a scheduler framework.

Count CPU processes and native-library threads across ALL local subagents and their children. The total compute budget is 16, not 16 per agent. For process-parallel CPU-bound Python, normally use processes and one BLAS/OpenMP thread per worker. Allocate equivalent slots explicitly to solvers using multiple threads. GPU jobs still consume host CPU and memory and must be counted.

At least every three minutes, and after a major batch change, inspect aggregate CPU usage, active workers and threads, completed experiment throughput, RAM pressure, disk growth and both GPU devices. Preserve compact timestamped observations inside this campaign. When runnable valuable work exists but cores are idle, refill or repartition the work promptly. Investigate sustained underutilization instead of just reporting it. Do not use duplicate jobs, spin loops or pointless sweeps to manufacture utilization. Report serial/proof-bound periods honestly. A temporary lower concurrency is justified only by observed useful-throughput or safety constraints, not convenience.

Use either or both GPUs when a concrete numerical discovery, batched algebra or other experiment benefits. Do not force unsuitable exact combinatorial work onto CUDA. Approximate GPU output is discovery evidence, not an exact certificate; confirm accepted constructions with appropriate exact checks. Keep RAM and VRAM headroom sufficient to avoid OOM failures, and preserve unrelated processes.

## External research and a live scout

Start from these two public research sources, including active PR branches rather than only main:

- https://github.com/CrocSwap/integer-mult-bounds
- https://github.com/Swapnil-jain/integer-mult-kappa

Use the completed RaD research selectively as a third reference. Read current summaries and only the dependencies needed for an actual candidate; do not rerun unchanged full baselines or replay old large finite graphs just to begin.

Assign one local subagent a lightweight literature-scout role. At intake and approximately every ten minutes during substantive research, inspect new and updated CrocSwap PRs, both source repositories, linked forks and relevant GitHub code/repository searches. Direct GitHub API or gh reads are preferable for minute-old developments because search indexes can lag. Broaden discovery to other relevant repositories and primary literature when useful. The scout must not inspect the other RaD campaign.

For each useful finding, record URL, authors, commit/head SHA, timestamp, changed mechanism, proof status, claimed bound and overlap with existing work. Alert the coordinator only to actionable mathematical changes; avoid repeated downloads or duplicate scouting. Pin source snapshots for experiments. New public results may change priorities but must not restart running experiments or the campaign clock automatically.

Internet access and task-local dependency installation are authorized. Use isolated environments and task-owned external storage or this directory's ignored `work/` for downloads, clones, builds, solver caches and large raw output. Do not reconfigure the host, restart services or work on the separate research-system project.

## Initial scientific emphasis: constructions and geometry

Prioritize finite constructions and compatible mathematical composition. These are initial leads, not a mandatory sequence or a boundary on originality:

1. Jointly change the computation DAG, selective recomputation/cloning, frame assignments and retained-controller allocation. Score the actual compiled role/rank/recursive-width cost, not addition count alone. The historical relation `R = additions + designated outputs - retained links` is a useful starting model, not a universal constraint on new compilers.
2. Combine compatible partial-swap, translated-source-frame, two-stage/unequal-dimension and common-basis mechanisms from different sources. Check actual endpoint maps, inverse chronology, protected directions, shared banks and all charged correction calls; never combine savings by multiplying headline ratios.
3. Explore new contiguous recursive blocks, changes across invocation boundaries and central-rank-loss reductions outside already proved fixed-boundary exclusions. Optimize full child-width distributions and the exact moment, not only aggregate rank.
4. Test whether alternative producers or geometries from either external repository work better with RaD's semantic precision, routing, Gaussian inverse and bulk interfaces. Switch foundations when evidence favors them. Attempt genuinely new ideas beyond merging existing patches.

Use small exact discriminators before expensive searches. Existing negative results exclude only their documented families; revisit one only when a new mechanism changes its assumptions. New directions may cross into analytic or routing work when that is the actual bottleneck.

## Evidence and publication

Keep a live hypothesis ledger and concise status in this directory. Distinguish numerical candidates, exact finite witnesses, written general lemmas, complete conditional compositions and external review. A separate subagent or independently implemented checker is useful, but is not external human peer review or formal verification.

For a promoted result retain exact rational parameters, source/input identities, actual finite maps and physical accounting, recurrence moments, coefficient/precision bounds, tape/row-stock/setup charges, all relevant assembly inequalities, strict absorption and eventual-cutoff limitations. Target verification at changed components and their interfaces; reuse unchanged pinned evidence. Preserve informative failures and counterexamples. Report originality and credit precisely, including directly adopted mechanisms and required licenses.

Keep authored source, small fixtures, configurations, patches and compact evidence here. Large raw data, dependency clones, environments and build products stay ignored or external with recovery manifests. Maintain a readable final report and reproduction instructions. The final report must distinguish a real improvement, a reusable lemma, a scoped negative, and an incomplete promising candidate without claiming success from PASS labels alone.

Make a meaningful checkpoint commit **at least every 20 minutes when durable work has changed**, and promptly after an important accepted construction, proof repair or informative exclusion. Push each checkpoint to your dedicated branch. Do not interrupt valuable compute to serialize the whole campaign for a commit; stage stable completed artifacts or consistent snapshots only.

Commit messages must say what happened scientifically. Examples of style, to be used only when true: `gpu: certify a two-stage endpoint composition`; `gpu: reject a mixed-frame candidate after exact rank accounting`; `gpu: retain 48 graph rewrites and identify the active moment constraint`. Avoid bare messages such as `update`, `progress` or `checkpoint`. The body should identify experiment IDs, findings, verification status and unresolved gaps. Do not make empty commits or claim results not obtained.

Because this is an exclusively owned directory, stage the reviewed campaign path as a unit using `git add -- research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008/`, rather than collecting paths throughout the old project. Inspect the staged scope and sizes and use the existing `tools/archive_workspace.py audit --staged-only` publication check from the repository root without modifying the tool. Respect the existing artifact/secret limits. Keep only one local Git writer.

At the deadline, checkpoint or stop only your own remaining jobs, finish the campaign report, commit every relevant durable change and push the dedicated branch. Verify the remote contains the final SHA. If publication is genuinely blocked, preserve the local commit and exact nonsecret recovery information; do not claim a successful push. Return only a compact handoff with result, limitations, report path, branch and commit SHA. Keep long prompts, code dumps and experiment logs in files, not in the user's terminal transcript.
