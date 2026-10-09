# Reproduce the final bounded continuation

Recover the immutable fd25 and source170 trees using `gh api` at the exact
commits in `input-manifest.json`. Regenerate the unchanged public control and
the earlier endpoint/transitive attempts through the
[preceding reproduction](../current-fd25-discriminators-20261009T0954/reproduce.md).
Their executed policy source fingerprints must match; no old operation IDs
are loaded into a changed source graph. Standard-library Python 3.14.4 and
assertions were exercised. An older runtime minimum is not established.

From the sprint directory, using those recovered source and execution paths:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 agents/bit/code/bit_current_final_continuation.py \
  --source "$TASK_BIT_SOURCE" --source170 "$TASK_BIT_METHOD" \
  --control "$TASK_BIT_OUTPUT/control" --endpoint "$TASK_BIT_OUTPUT/endpoints" \
  --prior-transitive "$TASK_BIT_OUTPUT/transitive" \
  --output "$TASK_BIT_OUTPUT/final-continuation" --seed 20261009 --max-nodes 128
```

The program recovers the old raise selection, reconstructs the four accepted
raises, checks their paid deltas and recovers the old lower selection. It then
resets and fully replays the 4,212-frame endpoint fixture, writes the complete
41,288-operation inventory and both old selections, and checks the disjoint
old/new seed partitions. Exactly two new 33,288-seed orders are retained.

Expected final native coarse is `655174925/10^12`; its next grid point must
fail. The final fixture changes 192 operations relative to the endpoint and
contains 4,356 operation differences relative to named node frames. Full F2,
mutations, mass, actual read/alias geometry and all 24,284 exact Gram/kernel
prime witnesses must pass. The historical sufficient target
`656266512/10^12` must fail.

To reproduce the later paid target rejection on this exact old-source profile:

```bash
python3 - "$TASK_BIT_SOURCE" "$TASK_BIT_METHOD" "$TASK_BIT_OUTPUT/final-continuation" <<'PY'
import json, sys
from fractions import Fraction
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, 'agents/bit/code')
from bit_current_control import modules
_, _, _, params = modules(Path(sys.argv[1]), Path(sys.argv[2]))
result = json.loads((Path(sys.argv[3]) / 'result.json').read_text())
bounds = params.interval_moment(params.counts(result['profile']), Fraction(663301643, 10**12), bit=True)
assert bounds[0] > 1
print(tuple(map(str, bounds)))
PY
```

The complete original generated files are retained in
`evidence/completed-final-continuation-20261009T1024-fix1`, including the
7,521,765-byte inventory and complete 43,832,234-byte prime witness. They are
whole-file gzip archives, with exact compressed and decompressed hashes and
sizes in the namespace manifest. Verify with
`python3 tools/archive_workspace.py verify-text --destination <namespace>`
before restoring any original file into a fresh task-owned execution directory.
No source text or evidence was split to meet a publication limit.

For the new comparison certificate, obtain eumemic commit
`4a3c769e5c5430e7114c4d3e099ff34664677f17`, verify the exact certificate pin in
`latest-qualification.json`, and read its top-level `kappa`. Its large integer
counts can be parsed with `json.loads(text, parse_int=str)`; no conversion of
those counts is needed for this score comparison. This comparison does not
reinterpret the older candidate's graph or inventories.

All listed construction, fixture/F2, moment and prime checks were actually
exercised. No broad independent reflected physical-event gate or final
multiplication certificate is claimed for this nonqualifying continuation.
