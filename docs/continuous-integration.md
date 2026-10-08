# Continuous verification for RaD

The workflow `.github/workflows/verify.yml` runs on pushes and pull requests.
It uses isolated GitHub-hosted Ubuntu workers, never the CPU or GPU research
servers. The initial matrix covers Python 3.11, 3.13 and 3.14. Dependencies
for the initial checks are standard-library Python and Git.

## What is verified today

`tools/ci_checks.json` is the explicit registry. It initially contains:

- The existing publication/archive-policy tests in `tools/test_archive_workspace.py`.
- CI runner failure, timeout, path, manifest and provenance controls.
- Small exact-arithmetic and negative tests for the frozen assembly ceiling.
- Replay of the frozen-inequality arithmetic fixture in the breakthrough project.

The last two checks establish consequences of **assumed inequalities**, not
an integer-multiplication algorithm, its finite network, or an all-size theorem.
The historical research archive is not recursively executed or retroactively
certified. New experimental files are not automatically mathematical checks.
No Lean package or full research reproduction is registered at installation.
Empty groups are excluded from the Actions matrix; explicitly running an empty
group locally is an error, not a successful verification.

## Run the same checks locally

From the repository root:

```sh
python3 tools/run_ci.py --group repository --all
python3 tools/run_ci.py --group smoke --all
python3 tools/run_ci.py --group certificates --all
```

Outputs use fresh temporary directories by default. Set `--output` to a NEW
ignored/external directory to retain them. The runner refuses to overwrite
existing evidence. Each report identifies the actual commit, interpreter,
command, input SHA-256 values, return code, duration and scientific scope.
A failed or timed-out check returns a nonzero status. Logs and JSON/Markdown
reports are uploaded by Actions even on failure and retained for 14 days;
important research evidence must also be committed under the research policy.

Automatic runs compare changed paths when the comparison commit is available.
An unchanged check is recorded as `skipped-unaffected`, never as a mathematical
PASS. Missing comparison history falls back to running the registered checks.
Registry or runner changes select every automatic check. Documentation-only
changes do not require repeated expensive mathematical computations.

## Register a mathematical verifier

Add an explicit object to `tools/ci_checks.json`:

```json
{
  "id": "new-network-certificate",
  "group": "certificates",
  "command": ["{python}", "research/TOPIC/code/verify.py"],
  "inputs": ["research/TOPIC/code/verify.py", "research/TOPIC/fixtures/witness.json"],
  "paths": ["research/TOPIC/code/**", "research/TOPIC/fixtures/**"],
  "timeout_seconds": 600,
  "scope": "Exact finite network and recurrence only; analytic transfer remains assumed"
}
```

Replace the example paths with actual committed files. Include **all** effective
code, fixtures, imported local modules and dependency locks in `inputs`, and
all paths that can affect them in `paths`. Optional `sha256` pins map a subset
of input paths to immutable 64-character digests; mismatches fail before running.
Review pin changes together with the underlying scientific change.

Commands are argv arrays, run without an implicit shell. Use `{python}` for
the selected matrix interpreter. Every verifier must fail on corruption, preserve
source fixtures, write generated results to fresh ignored/external storage, and
state which claims it checks. Add targeted negative controls. A verifier reading
its own saved PASS flag is not independent reproduction.

Use `smoke` for cheap discriminators, `certificates` for bounded exact replay,
`full` for expensive regeneration, and `formal` for real proof packages. Full
and formal groups are opt-in through manual `mode=full`; they never run merely
because an agent pushes an experiment. Register their actual commands only
after providing pinned toolchains/dependencies and testing their setup on a
clean runner. No GPU or local dataset may be assumed to exist.

## Manual full reproduction and rollout

The `workflow_dispatch` input supports `mode=full`, selecting all registered
groups. The GitHub UI normally exposes manual dispatch only after this workflow
also exists on the default branch. Until then pushes test this research-branch
installation, and the same full commands can be run locally. Promote a **narrow
CI-only change** to main after review; do not merge the entire research branch
just to install CI. Other existing branches need the workflow commit as well.

Full formalization is not implied by a workflow named `formal`: document the
actual theorem coverage, axioms, dependencies and any unproved interfaces.

## Security and repository policy

Actions have only `contents: read`. Third-party actions are pinned to full
commit SHAs, checkout does not persist credentials, and no research-server
runner or `pull_request_target` executes contributor code. No deployment,
secret provisioning, paid service, automatic merge or branch-rule change is
part of this installation. Update action pins deliberately after review.

For a commit containing workflow files, use the narrow infrastructure audit:

```sh
python3 tools/ci_archive_audit.py audit --staged-only
```

This delegates to the existing archive auditor and additionally recognizes
only direct `.github/workflows/*.yml` and `*.yaml` files. Existing content,
size, secret and indexed-file rules remain. Ordinary research commits can
continue using `tools/archive_workspace.py`. The workflow file is created as
a tracked file; inherited ignore rules do not hide later edits to tracked files.
Do not use broad force-staging. This exception does not admit other `.github`
payloads, dependencies, credentials or local artifacts.

A future ruleset may require stable CI checks, but no branch protection has
been enabled automatically. Green checks cover only the registered evidence,
not every assertion in a report or external mathematical peer review.
