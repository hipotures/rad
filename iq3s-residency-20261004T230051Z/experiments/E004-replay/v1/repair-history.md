# Replay repairs

Five policies completed on each profile: static/current/recency/frequency and
Least-Stale-inspired fixed-layer adaptation. Current reproduces observed nonlocal
entries and promotion bytes exactly. The Markov branch then failed on the first
transition update: NumPy advanced indexing produced `(dst,1)` instead of `(1,dst)`.

Repair: explicit `vector[:,None] * vector[None,:]`. This changes no completed
policy result. Repaired Markov and both future references run in v2 output
directories only; v1 records remain. No redundant deterministic replays of the
five completed policies are requested.
