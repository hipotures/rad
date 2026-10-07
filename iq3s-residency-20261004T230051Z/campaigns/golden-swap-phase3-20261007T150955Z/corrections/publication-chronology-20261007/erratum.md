# Phase 3 chronology erratum

## Correction: publication chronology (2026-10-07)

The original post-hoc live-trajectory script compared admission-array positions
as though they proved publication-before-selection chronology. That inference
was invalid. An earlier-created admission may publish after a later proposal.
The original report, conclusion, script and diagnostic are retained under
`corrections/publication-chronology-20261007/original/` and in Git history.

The corrected diagnostic examines every matching proposal generation before
the first action divergence, actual `published_at` logical events, within-run
host publication/issue times, source publication-before-selection ordering,
and service slots/generations. It does not compare absolute clocks across runs.
On Archive block 1, the original generation-0 witness publishes at events14/12,
after the first action divergence at event10; it does not establish precedence.
A different generation3 publishes at event10 in BASE and12 in OPT. BASE's
publication timestamp535817545215441 precedes its new issue535817545242651;
the released slot4962 is the destination of that new copy, on device1/class0.
This is a real same-hook state/worker-release witness, not a vector-index argument.

All14 pairs have a corrected same-logical-event, source-ordered publication
witness before their first observed differing admission action; none has a
strictly earlier logical-event witness in the matched prefix. Relevant service
records are separately linked through actual publication timestamps and slots.
**Exact causal attribution remains unresolved in14/14 pairs:** candidate scans,
complete worker-state snapshots and copy/event EWMA were not retained. This
withdraws the original automatic vector-order justification and its causal
implication. It does not establish that asynchronous readiness is irrelevant,
nor does it prove that every later divergence has the same cause.

The headline **DECISION_PRESERVING_OPTIMIZATION_NO_CONFIRMED_PRACTICAL_GAIN**,
all42 valid measurements, work/copy safety, deterministic policy parity and
paired performance results remain unchanged. Four targeted chronology regression
cases passed; the timing file identities were verified unchanged. No Phase3 GPU
request was rerun. See `corrections/publication-chronology-20261007/summary.json`
and the regenerated `results/live-trajectory-diagnostics.json`.

