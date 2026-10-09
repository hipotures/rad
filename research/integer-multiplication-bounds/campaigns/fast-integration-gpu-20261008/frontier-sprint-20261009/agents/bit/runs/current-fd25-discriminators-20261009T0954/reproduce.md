# Reproduce the current-source binary discriminators

Run from the sprint directory with standard-library Python and assertions
enabled. Python 3.14.4 was exercised; an older runtime minimum is not established.
Obtain the two immutable source trees through `gh api` tarballs for
`eumemic/integer-mult-bounds@fd25adb7fbaa12ee761d02c733c54d1d2a7687ee`
and `huxint/integer-mult-bounds@29892e2fe8a90714ef61bd8cbfb1a74bec6f8fd4`.
The preceding control additionally uses eumemic commit
`91f6a059f44fb0513639d5185bde2a38973e99ca`. Verify `input-manifest.json`;
it retains the full source170 imported dependency and proof closure.

Set task-specific variables to the recovered source locations and a fresh
execution root. Generated output directories must not already exist.

```bash
TASK_BIT_SOURCE=/path/to/eumemic-fd25adb
TASK_BIT_METHOD=/path/to/huxint-29892e2
TASK_BIT_OUTPUT=/path/to/new-bit-attempt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 agents/bit/code/bit_current_control.py \
  --source "$TASK_BIT_SOURCE" --source170 "$TASK_BIT_METHOD" --output "$TASK_BIT_OUTPUT/control"

for TASK_BIT_VARIANT in endpoints transitive third-fusion; do
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 agents/bit/code/bit_current_discriminators.py \
    --source "$TASK_BIT_SOURCE" --source170 "$TASK_BIT_METHOD" --control "$TASK_BIT_OUTPUT/control" \
    --variant "$TASK_BIT_VARIANT" --output "$TASK_BIT_OUTPUT/$TASK_BIT_VARIANT" \
    --seed 20261009 --seed-limit 8000 --max-nodes 128
done

OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 agents/bit/code/audit_current_bit_plan.py \
  --source "$TASK_BIT_SOURCE" --source170 "$TASK_BIT_METHOD" --control "$TASK_BIT_OUTPUT/control" \
  --candidate "$TASK_BIT_OUTPUT/transitive" --output "$TASK_BIT_OUTPUT/transitive-prime"
```

All logical control hashes must match the frozen source exports. Control coarse
is `654940331/10^12`; endpoint, transitive and third-fusion coarse values must
be `655162151/10^12`, `655036528/10^12`, `652325428/10^12`, respectively.
Each successor is rejected by a lower interval bound. The transitive prime
receipt must cover 24,466 actual frames and add no excluded prime above `2^80`.

To replay a complete fixed fixture on the public physical word, reset operation
frames to `base_frames` before loading all saved differences. The tested audit
wrapper does this explicitly. The public physical starting plan already has
frame changes, so applying only a partial difference to that starting state
does not define the stored complete fixture.

The gzip evidence holds original complete plans and exports. Use the archive
manifest to verify compressed and decompressed hashes before restoring any
file. `python3 tools/archive_workspace.py verify-text --destination <namespace>`
from the repository root verifies each complete namespace. Preserve original
gzip bytes and decompress only into fresh task-owned execution directories.

The actual reproduction exercised full graph construction, every logical
export, copied values, all operation/frame/read obligations, every F2 column,
literal inverse, adverse controls, every charged child, rigorous fallback and
stopped-atom moments. The separate prime reconstruction also exercised every
integer frame rank and selected Gram witness. No independent full reflected
event gate or final multiplication certificate is claimed for these inferior
trials.
