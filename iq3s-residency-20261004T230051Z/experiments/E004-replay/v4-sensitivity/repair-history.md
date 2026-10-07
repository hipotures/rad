# Completion-clock repair

The first slower-bandwidth sensitivity exposed a floating-point endpoint error: reconstructing `base + delay` after adding the wait could round one ULP below the last completion timestamp. This left a finished entry unpublished, occasionally added a false single nonlocal entry, and caused the future-nextuse policy's next issue to reject a nonempty queue.

No inference runtime or model changed. The old replay source is retained as `replay-before-queue-repair.py`; completed partial results and the failed command remain preserved. These v4-sensitivity records are INVALID_NUMERICAL_QUEUE for precise accounting. Earlier peak-rate v1–v3 current selection and observed counts remain directly validated, but full models should use the corrected publication implementation for replication.

The repair publishes through the exact completion endpoint after the blocking wait and asserts the queue is drained. `scripts/test_replay_publication.py` reproduces a cancellation case. Corrected E004 sensitivities use v5-sensitivity, and E007 causal models use a separate v2 attempt rather than overwriting v1. All source, policy and fixed-input assumptions remain unchanged.
