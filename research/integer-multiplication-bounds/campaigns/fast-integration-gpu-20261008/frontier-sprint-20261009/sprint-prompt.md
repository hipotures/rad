# Integer multiplication: rapid construction and verified-publication sprint

## Mission and authorization

Read the supplied frontier-review PDF, check what has changed publicly, and run short parallel batches that **build and test actual candidate constructions**. Prioritize a rigorously checked final exponent saving `kappa` strictly greater than the current comparable public frontier.

If such a result is obtained, prepare a **self-contained publication script that the user can run to create the upstream pull request**. Do not execute its publishing mode yourself. Do not open, comment on, modify, merge, or close an upstream PR on the user's behalf.

Research checkpoint commits and pushes to the current authorized `hipotures/rad` research branch remain permitted. Publishing to `CrocSwap/integer-mult-bounds`, or creating a public-submission branch in another repository, is reserved for the user's execution of the delivered script.

Do not stop after a plan. Start real delegation and experiments, report measured results, and preserve useful evidence. Do not claim an improved exponent from a proxy score, a component saving, or a supplied PASS flag.

## 1. Remain in the existing Codex workspace

Confirm the current working directory, Git root, branch, origin, working-tree status, and available resources. The research repository is `hipotures/rad`; the upstream submission target is `CrocSwap/integer-mult-bounds`. They are different repositories with different purposes.

**Keep the existing Codex-attached checkout and its current research branch.** Do not create an external worktree, relocate the session, switch branches underneath running agents, reset, force-push, or overwrite uncommitted work. Do not assume a fixed absolute path such as `/home/user/DEV/rad` or `/root/...`.

Read the applicable repository and local `AGENTS.md` files. Create one task-owned sprint directory inside the active campaign, for example `frontier-sprint-20261009/`. Reuse an existing sprint only after inspecting its ownership and state. Give each subagent and experiment a distinct subdirectory. Only the coordinator manages Git.

Keep downloaded source snapshots immutable and inside task-owned ignored storage within this checkout. Do not change another active campaign or require direct communication with the CPU/GPU host running it. Existing useful jobs may continue; do not kill them merely to start this sprint.

## 2. Read the actual report, not a remembered summary

Required file:

`Integer_Multiplication_Frontier_Review_2026-10-09.pdf`

Expected SHA-256:

`8287760a0e737119167e5a17b50df20fc60283badd19bacd20994098ed7cdc77`

Optional accompanying arithmetic package:

`Integer_Multiplication_Arithmetic_Supplement_2026-10-09.zip`

Expected SHA-256:

`818b13781338e3ac3f9a3de2b3641c3bc433b5d635163113c014afa57b55baf4`

Locate these among the files explicitly supplied to this session or within the current checkout. Do not search the user's entire home directory or filesystem. If the PDF is unavailable, ask for that file or its local path; do not pretend it was read. A differing hash requires identifying the actual version before treating it as the reviewed snapshot.

Read the entire 14-page report, including evidence boundaries, source pins, compatibility warnings and the publication criteria. Extract its text with an available PDF reader and inspect tables or equations visually when extraction is ambiguous. Keep the source document unchanged.

The PDF is a historical snapshot at **2026-10-09 01:01 UTC**, not a live leaderboard. Its highest reported value was PR #120 at `1.0911630664e-4`. That number is **not** the permanent target.

The optional supplement independently checks supplied histogram arithmetic. Inspect it before execution. Passing it does not independently regenerate the underlying network or prove its transfer assumptions.

## 3. Maintain an exact, current public comparison

Read the live upstream PR collection:

`https://github.com/CrocSwap/integer-mult-bounds/pulls`

Use available Git/GitHub tools. Enumerate all pages of open PRs, including drafts; inspect updated older PRs as well as new PR numbers. Read the current default branch and its retained reviewed result. For likely leaders, inspect the actual body, source head and exact certificate rather than sorting titles alone.

Record a compact `public-frontier.json` containing observation time in UTC, PR number, author, current head SHA, state/draft/merged status, exact rational kappa, certificate source, construction family, conditional assumptions, and the evidence actually observed. Distinguish author-reported local verification, hosted checks, scoped Lean coverage and maintainer review.

Track separately:

- The highest active comparable public claim, **including drafts**.
- The strongest comparable result with completed reported reproduction.
- The retained maintainer-reviewed result.

For the user's publication condition, compare against the **maximum active comparable public claim and retained reviewed result**, not merely main or the easiest verified baseline. Exclude withdrawn claims only with explicit evidence; preserve their history. Do not silently ignore an inconvenient stronger claim because its review is pending.

Use integers and exact rational arithmetic. Do not compare rounded floats, `a_bit`, `b_complex`, percentages, or values under incompatible models as though they were final kappa. Reconcile titles with current certificates. If only a rounded public value is available, establish a conservative comparison bound or mark the comparison unresolved. A construction using stronger assumptions needs an explicit comparability assessment; do not label it a like-for-like record automatically.

Refresh at startup, after meaningful batches or approximately every 10–15 minutes, before freezing a publication package, and immediately before handing it over. One coordinator/scout handles these reads so other agents keep working. If GitHub cannot be queried reliably, research may continue but the current-record publication gate remains closed.

## 4. Delegate early and run short construction batches

As soon as the workspace and first relevant report sections are understood, launch **at least four actual native subagents concurrently**, when the session supports them. Do not wait for every dependency to download or every historical test to finish. If delegation is unavailable, state that explicitly rather than presenting sequential work as a multi-agent run.

Suggested first lanes:

| Lane | Initial task | Required output |
|---|---|---|
| Baseline and reviewer | Pin the current relevant leader; establish its focused reproducible baseline and inspect proof boundaries. | Exact baseline profile, source pins, pass/fail scope and independent review plan. |
| Alternate complements | E1: change the actual nondegenerate complement or pivot choices, not just dimension. | Distinct legal candidate frames and freshly evaluated complete profiles. |
| Moment-aware placement | E1/E2: price downstream target-chain costs; try bounded joint selection or local exchanges. | Explicit selected schedules and comparison with the unchanged baseline. |
| Signed synthesis | E3: test signed reclamation or a small producer change on the current complex construction. | Exact signed identities, legal lifetimes and a complete paid-program discriminator. |

The coordinator handles source integration, comparisons and publication preparation; it should not redo every subagent's job. Review a candidate through an agent or checker distinct from its discoverer. Additional agents may inspect new public mechanisms or pursue one E4/E5 structural alternative when useful.

A normal computational job may use about **four CPU workers**. Four or more jobs may overlap even on a 12-core host. Bound actual aggregate RAM, disk growth and nested numerical-library thread pools; oversubscription is allowed, uncontrolled memory exhaustion is not. There is no CPU-utilization quota. Use GPUs only when the current host has them and an existing or inexpensive batched implementation provides a measured benefit.

Start with one unchanged control and at least three discriminating variants. Aim for first bounded screening batches of roughly 10–20 minutes after the minimum baseline is available; adjust to measured costs. This is a search budget, not permission to truncate decisive verification or a guaranteed completion time.

Reuse immutable inputs and established evaluators. Do not spend the first hour building an orchestration framework, traversing the whole archive, or repeatedly running broad historical suites. While one candidate is being certified, other lanes can continue searching.

## 5. Apply the report's compatibility boundaries

The PDF's E1–E3 are the immediate sprint priorities. E4–E6 provide alternatives and verification targets, not a requirement to implement six large projects before producing anything.

At the report's snapshot, **#120 already combined #117's smaller complex DAG with #114's saturated placement**. Reproducing that combination is a control, not a discovery. Check whether the latest public head has already added any proposed further variant.

Initially freeze the scalar DAG, binary supplier, stopping policy and assembly while changing one placement mechanism. Evaluate alternate complements, downstream-cost priorities and small jointly optimized conflict components separately before combining winners. Recheck target containment and nesting after every complement extraction; never count radical dimensions as a nondegenerate frame.

Under one-child-per-projector accounting, a rank-preserving coordinate permutation alone need not change the characteristic. Only pursue it when it changes legal selections, residual ranks or multiplicities, paid implementation, or the actual transfer. Do not port an obsolete coordinate-only objective into a different compiler.

For signed reclamation, use exact signed arithmetic and actual inverse/sign-negate/bank-swap semantics. Binary XOR cancellation alone does not establish a complex phase identity. Preserve all centers, copies, endpoints, frame raises, arbitrary dirty state and expanded readout costs.

Score the **complete paid child distribution** with its own normalization. Smaller W, fewer roles, more deferred dimensions or a lower local surrogate is not sufficient. Do not add independently reported improvements together. When changing the DAG, reconstruct its supported map and geometry rather than splicing incompatible profiles.

Keep the report's scoped headroom analysis in mind: its fixed binary supplier leaves a ceiling near `1.24e-4` under the retained relation. This is historical and conditional, not universal. A target near `2e-4` requires changed components or transfer; do not attempt to obtain it by parameter polishing of the frozen pair.

## 6. Use staged evidence gates

**Screening:** record variant, seed, runtime, resources, local validity and a common-trial complete moment. Label approximate calculations as discovery-only. Cache only immutable, fully identified inputs.

**Exact finite construction:** rebuild scalar outputs, legal carrier uses, actual frames, target chains and literal program; verify arbitrary-dirty restoration and signed/reflected execution in both orientations. Reconstruct every charged transition and the complete histogram. Use exact rank/subspace arithmetic and justified modular certificates, not unexplained prime agreement.

**Conditional exponent:** independently enclose full binary and complex moments, derive the final kappa, and check all applicable assembly inequalities and margins. For the retained framework this includes its 47 constraints and seven margins. Account for expanded scalar work, precision, row reserves, adapters, ordinary leaves, copies, routing and recovery. Explicitly identify inherited and newly required general hypotheses. Do not require a new unconditional theorem merely to publish a correctly scoped conditional result.

**Independent reproduction:** run the focused checker from a clean exported candidate with pinned dependencies and no undeclared absolute paths. Recompute rather than read saved verdicts. Include negative controls for unpaid cancelling operations, omitted cleanup, bad signs/complements, illegal indices, assertion-disabled execution, source corruption and misleading mass-preserving histogram mutations where relevant. Reuse the existing CI and relevant Lean checks without claiming that unrelated formal modules prove the new result.

Run expensive repository-wide verification once for a frozen publication candidate when required by the target's contribution policy, not after every failed trial. Reuse prior checks only with explicit unchanged-source evidence and a stated scope. A timeout or incomplete review is unresolved, not PASS. Speed comes from staging and reuse, never by dropping an obligation or disabling a failing check.

Maintain at least these statuses: `DISCOVERY`, `EXACT_FINITE`, `ACCEPTED_CONDITIONAL`, and `PUBLICATION_READY`. Only the last two contain a final accepted kappa; `PUBLICATION_READY` additionally requires a resolved current-frontier comparison and a tested standalone publication package.

## 7. Freeze a winner immediately, without stopping the search

When a candidate passes conditional acceptance and strictly exceeds the refreshed comparable public frontier:

1. Commit and push its compact scientific checkpoint to the current authorized research branch; verify remote containment.
2. Freeze the exact proof, source/licensing inventory, candidate data, independent receipts, reproducible commands and comparison timestamp.
3. Prepare a minimal upstream change against an exact inspected upstream base. Keep internal campaign paths, host names, usernames, private logs, unrelated research archives and credentials out of public material. Credit every directly reused contribution by contributor, mechanism, PR and source revision, with inherited licenses and AI-assistance disclosures preserved.
4. Prepare the script below and test it locally without performing GitHub writes.
5. Deliver the script and exact invocation promptly. Do not wait for a later experimental batch or package every historical log first.

There is no arbitrary minimum percentage gain: any rigorously demonstrated strict improvement can satisfy the numerical condition. Describe a parameter-only increment as such; do not market it as a new network. If no qualifying result exists, preserve the results but do not manufacture a record script.

## 8. Required deliverable: a self-contained publication script

Create `publish_<candidate-id>.sh` in the sprint's publication directory. It must be runnable by the user from an arbitrary local directory, not only inside the research machine's checkout.

Prefer a single script with an embedded compressed allowlisted payload, exact metadata and SHA-256 checks. Do not require a separately installed research package, an unmentioned artifact directory, or files left on another host. Reasonable explicit prerequisites are Bash, Git, Python 3 and an already authenticated GitHub CLI. Check them at startup; never silently install system packages, request pasted tokens, or change the user's authentication.

**Default execution by the user performs publication after successful safeguards.** Also provide non-publishing `--check`/`--dry-run` and local self-tests. The coordinator must never execute publishing mode. Exercise the GitHub-facing control flow with mocks or recorded fixtures, not a real trial PR.

The publishing path must:

- Validate embedded payload hashes and safe extraction paths before executing packaged code. Use a fresh disposable workspace; do not modify the user's existing checkout. Print timestamped progress from the first operation, give network commands bounded timeouts/retries, and retain the workspace/logs after failure. Avoid downloading the full historical research repository.
- Use the authenticated user's own upstream fork, creating it only when the user runs the script and when necessary. Target **`CrocSwap/integer-mult-bounds`** and its verified default branch. Never push directly to upstream main.
- Detect an existing PR for the exact frozen candidate and print its URL instead of duplicating it. Do not edit a different PR or replace an earlier delivered candidate silently.
- Refresh the public frontier using current, paginated GitHub data and exact certificate-aware comparison. If a newer eligible public claim is equal or better, the comparison is ambiguous, or network/API access fails, stop clearly **without opening the PR**. Save the staged package for inspection; do not weaken the guard automatically.
- Check the current upstream base against the verified base and relevant source fingerprints. Do not silently rebase a certificate onto changed mathematical dependencies. If compatibility is not already established, stop and report that revalidation is required.
- Apply only the allowlisted publication changes. No unrelated files, secret material, forced history replacement or deletion of inherited tests is permitted. Use a unique submission branch and verify its remote commit after pushing.
- Use a prepared English title and body. State exact rational and decimal kappa; the construction change; the pinned predecessor and numerical improvement; actual verification coverage; reproduction commands; all conditional assumptions and exclusions; full attribution; and the observation time of the frontier comparison. Avoid internal campaign/machine terminology in the public title. Do not claim hosted CI has passed before it actually runs.
- Recheck the frontier immediately before creating the PR. A race with another contributor after that final check cannot be eliminated; state the comparison timestamp rather than promising permanent record status.
- Create the PR only after every guard passes and print its actual returned URL and submission commit. Do not merge it, auto-approve checks, mark incomplete work ready, or treat a failed command as success.

Default to a ready-for-review PR only when the stated publication/reproduction gates are complete. Do not open an unfinished draft just to reserve a place. Keep expensive mathematical discovery and full certification out of the user's publication-time path; those should already have produced a frozen, verified package.

Before handoff, test shell syntax, safe extraction, payload hashes, missing dependencies, wrong upstream base, API failures, stale/equal/better public scores, duplicate handling and command-failure propagation. Mocked tests are not an actual published PR; label them correctly.

## 9. Reporting and continuation

All authored code, reports, manifests, commit messages and public materials must be in English. User-facing status messages may be in Polish.

After each meaningful batch, give one compact status: live comparison time/value, strongest accepted final kappa, best pending candidate and exact blocker, variants actually tested, useful throughput, and checkpoint/evidence location. Distinguish native `a`/`b` from final `kappa`. Do not flood the console with raw archives, grep output or large JSON dumps.

For a publication-ready result, deliver the precise script path or accessible attachment and one command to execute it, the frozen commit, exact comparison and verification scope. Do not say a PR exists until the user has executed the script and GitHub has returned one.

Continue useful short batches after delivering a package unless the user stops the campaign. Keep delivered packages immutable; a stronger candidate receives a new identity and script. Do not redirect or stop the independent other-host campaign.

**Begin now: read the supplied PDF, confirm the existing workspace, refresh the public frontier, launch independent lanes early, and build the first bounded candidate batch.**
