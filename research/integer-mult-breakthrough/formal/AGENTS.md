# Formal proof package rules

This directory contains Lean proofs, not the running research agenda. Do not
stop or retask other agents when maintaining it. The parent research goal and
its resource policy remain unchanged.

Keep all authored files in English. Pin the toolchain and all dependencies.
Every new theorem must be listed in coverage.json with an accurate scope.
Do not add proof placeholders, new axioms, unsafe proof code, native decision
shortcuts or checks which only read stored success flags.

Run verify.py --self-test and the complete verify.py before claiming formal
acceptance; a successful Python run alone does not compile a Lean proof.
Record actual formal coverage separately from finite numerical evidence and
all-size transfer obligations. Passing this package does not certify kappa.

Keep .lake, downloaded packages, compiled objects and raw logs out of Git.
For commits containing this package's .lean or lean-toolchain files use:

    python3 tools/lean_archive_audit.py audit --staged-only

This is a narrow source-format exception; all existing size, secret, UTF-8,
symlink, indexed-content and unrelated-change rules still apply. Do not change
the root publication policy or the active coordinator's registry incidentally.
Only the coordinator publishes shared-branch changes. Never force-push.
