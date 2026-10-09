# Reproduce the bounded local association trials

Recover and hash-check the fd25 and source170 trees as described in the
[control reproduction](../current-fd25-discriminators-20261009T0954/reproduce.md).
Standard-library Python 3.14.4 and assertions were exercised. Use the unchanged
control from that reproduction, then three fresh output directories:

```bash
for TASK_BIT_VARIANT in without01-mode0 without01-mode1 with02-mode0; do
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 agents/bit/code/bit_current_local_associations.py \
    --source "$TASK_BIT_SOURCE" --source170 "$TASK_BIT_METHOD" \
    --control "$TASK_BIT_OUTPUT/control" --variant "$TASK_BIT_VARIANT" \
    --output "$TASK_BIT_OUTPUT/local-$TASK_BIT_VARIANT" --seed 20261009
done
```

The wrapper verifies all five unchanged source/control export hashes before
changing the exact supported diagonal map in memory. No immutable source file
is edited. Each new graph, carrier matching, rational frame table, gauges,
copies, source chronology and physical alias fixture is exported and checked.
Expected native coarse values are `650896166/10^12` for both removals and
`645735134/10^12` for the additional diagonal. Every successor must fail the
full fallback moment lower bound; every actual F2 source/dirty input and
inverse restoration must pass.

The fresh frame plans are complete differences from each trial's native
baseline and contain its five export hashes. Their complete original bytes are
preserved in the evidence gzip namespace; filenames and SHA/size pairs are
listed in its archive manifest. Verify the entire namespace with
`python3 tools/archive_workspace.py verify-text --destination <namespace>`
before decompressing into a fresh execution directory.

The separate transitive prime receipt in this archive is reproduced by
`audit_current_bit_plan.py` using the preceding control and transitive plan;
see the control reproduction. It is not an audit of these local variants.

This exact recovery path exercises the entire fresh graph, literal F2 and
paid native moment pipeline. No local trial's all-frame prime certificate,
independent full reflected physical execution, final complex supplier or final
multiplication kappa is claimed.
