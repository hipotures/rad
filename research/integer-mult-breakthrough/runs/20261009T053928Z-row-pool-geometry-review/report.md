# Independent geometry review of the initial pool

The initial row-capacity recurrence and exact numerical run remain valid,
but per-role modulo splitting can destroy the independent fresh guard cube
required by the native packed wrapper. This review therefore narrows the
native claim and proposes an aligned old-row split. It is an analytical
scope failure, not a failed arithmetic experiment.

The [initial report](initial-report.md) retains the exact pre-review bytes;
the [receipt](results/receipt.json) pins their hash. The original producer
and run files are unchanged. The separately authored
[aligned report](../../reports/obstructions/aligned-guard-row-lifecycle.md)
states the corrected allocation and conditional rehydration requirements.

The immutable initial report was originally located at
`reports/obstructions/retired-guard-row-lifecycle.md`. Resolve its relative
links against that original directory; moving this exact historical copy
does not rewrite its content or turn its pre-review claims into current claims.
