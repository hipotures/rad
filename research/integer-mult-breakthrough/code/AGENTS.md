# Verification contract for research code

Keep the parent research goal, parallelism policy and scientific independence.
CI does not impose a CPU utilization target or launch additional research jobs.

For new reusable verifiers or accepted finite certificates, register bounded
checks in the repository's `tools/ci_checks.json`, following
`docs/continuous-integration.md`. Editing that shared registry for this purpose
is allowed; preserve entries belonging to other research tracks.

Record every effective input and dependency. Supply negative controls and fail
with a nonzero exit status on invalid evidence. Do not rewrite input certificates
during verification. Keep discovery workloads out of automatic CI. Use the
manual `full` group for costly regeneration and register `formal` only for
actual proof packages with a reproducible pinned toolchain.

Every check must state its scientific scope. A green workflow is not proof of
a new exponent, an all-size transfer, or a claim absent from the registry.
Document unregistered or unavailable checks rather than inventing PASS results.
