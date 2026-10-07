# Interrupted direct h50 target-frame attempt

This direct per-basis implementation was deliberately terminated between
2026-10-07T23:24:13Z and 23:24:50Z while still constructing/checking h50 labels. It had not
written a complete h50 certificate, so no h50 count is accepted from this
attempt. The mathematical small witnesses remain in their separate runs.

The direct inclusion predicate tested each basis column against each frame
constraint. It was replaced, in a fresh run, by the exactly equivalent
simultaneous symbolic-coordinate implementation. Seeded cross-checks and
independent rational elimination verify the new predicate. The repair is
`20261007T232600Z-finite-target-fast50`; the original source and its small
results remain unchanged.
