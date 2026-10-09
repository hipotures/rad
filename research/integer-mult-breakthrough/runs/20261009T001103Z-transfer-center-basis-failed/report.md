# Scalar temporary guard assertion failure

Status: **FAILED BEFORE CASE REPLAY**. The independently derived inverse
classes passed, but a prefix assertion used endpoint-only constants after
the observer began including scalar multiplication temporaries. The true
base forward/inverse row-L1 constants are 260/384, and border constants 8/7.
The old constants 232/347 and 4/7 were insufficient for these temporaries.

The [protocol](protocol.json) and [failure receipt](results/failure.json)
preserve the old source hash. The correction patch reconstructs that source
from the repaired version. The failed attempt is not relabeled as a pass;
the complete replay uses a fresh attempt.
