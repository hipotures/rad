# Independent audit of exact 1% publication policy

Status: local source and mock tests pass at the hashes in the fresh receipt. This
is a publication-policy and safety audit, not acceptance of a scientific candidate.
No real publication script exists in this review and no publication is authorized.

## Policy and inspected implementation

The user now requires an accepted final candidate satisfying
`candidate >= (101/100) * max(active comparable claims including drafts, retained main)`.
Reviewed conservative upper bounds for rounded claims are included in the maximum.
The immutable release field is exactly `minimum_relative_improvement: "1/100"`.
Missing, weaker, or noncanonical representations are rejected; no fallback to
mere strict improvement remains in the active source version.

The builder checks each comparable exact claim or reviewed bound and retained
main with exact `Fraction` arithmetic. Both runtime frontier checks calculate
`minimum_required_kappa` dynamically from the current observed maximum. Equality
at the 1% boundary passes. Changed/unrecognized current claims close the gate
pending renewed assessment, rather than silently changing the frozen inventory.
The actual CLI rejects malformed policy before authentication or any command.

## Verification and source identity

[Fresh receipt](../results/policy-audit-20261009.json) records unchanged hashes
before/after all three suites, with log hashes and scope flags. The three audited
publication sources are:

| Source | SHA-256 |
| --- | --- |
| `build_publication.py` | `695c17525668eb7b4546196eae38ec8c52591bd8be6d445864ef8e6432b0a159` |
| `publication_runtime.py` | `bf8601a55b4f9e71cf9b03d7d633d0e98b5cca62a8331fc970a0715ffd7720e6` |
| `test_publication.py` | `5434f5d5c2873db2919a6c5f91dacec2e5ec5444e904b2552c34146c116fcd82` |

44 authored tests, 14 unchanged independent safety regressions, and seven new
[independent policy tests](../code/test_publication_policy.py) all pass. Every
suite was launched from `/` using resolved script paths. The policy suite uses
multiple subcases:

- Below/equal/above boundary with an exact `1/10^30` difference, for active exact
  claims, reviewed conservative bounds for rounded claims, and retained main.
- All three layers: builder, initial production execution guard, and isolated
  final `submit()` frontier guard. The final unit tests deliberately enter the
  mock `submit()` layer after mock preparation so its independent guard is
  exercised even for candidates the earlier production guard would reject.
  This is a Python fixture construction, not a CLI bypass.
- Absent, weakened, and noncanonical policy rejection at builder and runtime
  layers. No command runs when the actual `execute()` entry has an invalid field.
- A changed current top head/body or new unknown claim after mock pushing blocks
  PR creation. Frozen comparison metadata is left unchanged in those cases.
- Global Git destination rewrite blocks the mock push. Network Git disables hooks
  per command; the submission remote's resolved push URL must equal the canonical
  authenticated-fork URL.
- Dynamic fixture arithmetic: if a comparable exact maximum were
  `6105562/10^10`, its threshold would be `616661762/10^12`. This is arithmetic
  only; this reviewer did not independently observe or validate a live PR #169.

The original safety regressions still cover checker-induced index path/blob/mode
changes, committed and remote corruption, safe exact duplicate handling, corrupt
pinned downloads, fork/API failures, malformed PR URLs, and unique no-force
submission behavior. The prior audit and receipts remain unchanged historical
source snapshots and do not apply automatically to this new source version.

## Evidence, reproduction and limitations

Three full text logs are preserved in
[the fresh evidence directory](../evidence/policy-audit-20261009/) with a gzip
manifest: 8,890 original bytes and 1,915 compressed bytes, no skipped inputs and
no splitting. Manifest entries and decompressed hashes were reviewed; every gzip
copy is strictly below 10 MiB. Original execution logs remain unchanged in ignored
`../../work/publication-review/policy-20261009/`.

From any directory, with paths resolved to the checkout:

```bash
PUBLICATION_REVIEW_WORK=<sprint>/work/publication-review/policy-20261009 \
python3 <sprint>/agents/publication-review/code/test_independent_publication.py
PUBLICATION_REVIEW_WORK=<sprint>/work/publication-review/policy-20261009 \
python3 <sprint>/agents/publication-review/code/test_publication_policy.py
PUBLICATION_TEST_WORK=<sprint>/work/publication-review/policy-20261009 \
python3 <sprint>/agents/publication/code/test_publication.py
```

All Git/GitHub-facing operations use the in-memory synthetic backend. No real Git
write, GitHub request/write, fork, push, PR creation, or generated publishing CLI
ran. Tests do not establish candidate science, completeness of frozen comparison
assessments, GitHub write permissions, hosted CI, or absence of a race after the
last frontier read. Source-only exact claims and rounded envelopes continue to
require coordinator review. The coordinator owns final scientific acceptance,
live comparison, freezing, and the RaD commit/push.
