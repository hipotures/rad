# Admission-only timeout, preserved unchanged

This attempt ended with exit1 and `AssertionError: Admission timeout`
at wrapper line57 after its180-second admission allowance. The scientific
Python child never launched. The original protocol's `status` remains
`Admission pending` because that wrapper only wrote terminal status after
a child; its actual `finished_utc` and locked reservation release show the
attempt ended. This annotation corrects interpretation without replacing
the original bytes.

The current085400 finite cohort still had sixteen pending process-local
chunks and no completion. Its jobs were not interrupted. This review's
own one-worker reservation was released in `finally`,1 to0. A fresh
[attempt](../20261008T0859Z-review-two-disjoint-centers-admission-repair/protocol.json)
extended the admission allowance and launched only after the current
checkpoint reported fourteen pending chunks and two reserved slots.
That scientific run passed and released only its own slot.

The traceback was returned by the execution tool; no scientific
`execution.log` was created because the wrapper had not opened a child
stream. The exact wrapper source/hash, inputs, Python version and source
identity are recorded in this attempt's protocol. The external wrapper is
`tmp/review/20261008T0857Z-two-center-review-repair-wrapper.py` under the
campaign work root. Its reproduction configuration is also recoverable
from the protocol; this is a resource-admission failure, not a failed
matrix or native-interface check.
