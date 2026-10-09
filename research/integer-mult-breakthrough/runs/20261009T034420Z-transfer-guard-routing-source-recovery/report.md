# Exact source-recovery control

The original receipt verifies all three rejected/prior source hashes by real `git apply` operations in an isolated ignored tree. The fixed-grid patch recovers the accepted variable-grid checker; applying its control patch then recovers the failed negative-control version. The Toffoli parse patch separately recovers the rejected parse-only source. None of the original run outputs was changed or regenerated under a newer source identity.

This receipt's actual UTC follows its recorded creation time. The reconstruction tree is disposable; the retained current sources plus these patches recover every effective prior source. The unchanged receipt is preserved in results, with source/patch identities in the protocol. See the [guard-layout report](../../reports/transfers/guarded-slot-layout-transfer.md) and [nonlinear routing report](../../reports/transfers/packed-nonlinear-routing.md).
