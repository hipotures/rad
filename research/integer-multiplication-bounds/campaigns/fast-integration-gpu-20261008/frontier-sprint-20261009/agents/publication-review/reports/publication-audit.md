# Independent publication-script audit

Status: audited publication safeguards pass local tests at the source hashes in the final receipt. No candidate release is approved by this audit.

## Objective and source boundary

Inspect `../publication/code/build_publication.py`, `publication_runtime.py`, and
`test_publication.py` against section 8 of the sprint publication brief. The root
coordinator owns scientific acceptance, source/license inventory completeness,
current comparison, candidate freezing, research Git operations, and release.
This reviewer ran no real Git/GitHub writes and no generated publishing CLI.

The initial exact source identities and test outcome are recorded in
[initial-audit-receipt.json](../results/initial-audit-receipt.json). Full execution
logs remain in ignored `../../work/publication-review/`; compact outcomes are
retained here. Completed logs are also preserved as complete gzip text evidence in
[the audit evidence directory](../evidence/20261009T0818-publication-audit/). No real
candidate script existed at the start of this review.

## Material finding: checker changes to the Git index

Initial inspection found `prepare()` checking the staged allowlist before the
pinned lightweight checks, but checking only working-tree bytes/fingerprints and
unstaged tracked changes afterward. A successful checker can stage an unrelated
file without a tracked unstaged difference. The runtime then commits that index.

The independent `test_successful_checker_cannot_add_staged_paths` reproduces this
with an in-memory command backend: the mocked pinned checker adds `unrelated.py`
to the reported index after the original allowlist guard. Before repair the test
fails because the runtime does not stop, and the mock reaches publication. Seven
other independent adversarial tests pass. This finding was sent to the author
and root coordinator. No real publication was attempted.

The author repaired this gap with exact staged path/status, index blob and mode
checks after local checks and immediately before committing; committed-tree
allowlist/blob/mode checks before push and again before PR creation; and working
file/untracked guards. The runtime additionally validates remote content hashes
and file modes at the pushed SHA. The independent original regression now passes.
Independent tests that mutate index bytes/modes after the successful checker and
corrupt committed/remote bytes also pass: each stops at the expected guard.
A working-tree hash alone does not certify the bytes that Git will commit.

## Independently exercised guards

At `2026-10-09T08:15:13Z`, 40/40 authored tests and 14/14 independent tests pass.
The exact source hashes before and after both executions are identical and appear
in [final-audit-receipt.json](../results/final-audit-receipt.json). Both suites were
invoked from `/` using resolved script paths. The receipt also binds complete test
logs by SHA-256. The gzip evidence manifest was inspected: five whole text logs,
15,586 original bytes, 3,485 compressed bytes, no skipped files, and each gzip copy
strictly below the 10 MiB publication limit. Original execution logs are unchanged.

| Safeguard | Observed checks and result |
| --- | --- |
| Complete exact frontier | Paginated active collection includes drafts. Unknown/closed/changed head/body/title and inconsistent states stop; equality/better claims stop. Exact certificates are hashed and rational values reconciled; source-only/rounded assessments require frozen human review. PASS for tested fixtures. |
| Default branch and dependencies | Wrong branch/base, source corruption, and missing mathematical/protected fingerprints stop. Base is pinned again before fork/submission and final PR gate. PASS for tested fixtures. |
| Before-code payload integrity | Author tests exercise traversal, link, duplicate/oversized/unallowlisted member, manifest/member/compressed-hash corruption, and missing prerequisites. Packaged code runs only after all member checks. PASS. |
| Downloaded dependencies | Declared exact repository/ref/hash acquisitions are validated before any checker; independent corrupted source stops before checker invocation. PASS. |
| Fork and unique branch | Authenticated account and upstream parent are checked. API error is not treated as 404. Unique submission branch, no force, remote SHA checked; independent foreign target/push inspection passes. |
| Frozen Git bytes | Index, committed tree, remote content and modes checked. Successful checker mutations and committed/remote corruption stop at the expected guard. PASS. |
| Duplicate handling | Existing exact candidate bytes, executable modes, dependencies, change allowlist and fresh head are checked before reporting its actual URL; changed bytes/mode stop. Existing exact PR can be found even after upstream moves, without creating a new PR. PASS. |
| Command failures and URLs | Author suite covers timeouts/retry bounds, API/checker/push/PR failure and remote mismatch. Independent malformed URL outputs never produce a success receipt. PASS. |
| Arbitrary directory/local modes | Actual local shell syntax, generated `--check` and `--self-test` execute from `/`; synthetic `--dry-run` network path is blocked. No generated publishing mode runs. PASS. |

All GitHub-facing paths in these tests use the synthetic in-memory backend. The
actual subprocess tests use Bash syntax/local fixture modes and disposable Python
children only. No actual fork, push, PR creation or remote Git branch exists as a
result of this audit.

## Review limitations

These are local source and mock/fixture checks. They do not establish a
candidate's mathematical validity, completeness of the selected protected
file/dependency inventory, GitHub permissions, actual fork/PR creation behavior,
GitHub hosted CI success, or elimination of the race after the final frontier
read. Release metadata and source-only/rounded-claim assessments require the
coordinator's explicit scientific/frontier review. No candidate status is
promoted by a test passing.
