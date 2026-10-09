# CI registry configuration role repair

The initial staged audit rejected tools/ci_checks.json as row-level result
data after the authored registry exceeded128 checks and128KiB. The complete
initial rejection and staged content review are preserved; no scientific
result was removed or converted to evade a payload rule.

The existing archive auditor now recognizes only the exact registry path
with its version1 configuration shape. Other large row arrays and malformed
registries remain rejected. The CI runner still enforces the full schema;
file/commit budgets, secret inspection, indexed-byte checks and payload roles
remain unchanged. A targeted regression includes140 valid configurations,
the same bytes at two other paths, malformed exact-path rows and an indexed
audit. Existing verification infrastructure is the only authored-source
exception outside the new research directory in this repair.

Both repository checks pass again. The17 smoke and121 scientific certificate
checks retain their already-passing reports and unchanged runtime input
hashes. Together these verify all140 current registered checks. The repair
patch applies to the published base commit and reproduces both current
infrastructure files byte-for-byte in an isolated directory outside Git
ancestry. A first nested application skipped root-relative diff paths and
was not accepted as a reproduction. A final staged audit remains required.
