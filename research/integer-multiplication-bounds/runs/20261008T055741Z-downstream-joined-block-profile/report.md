# Admission failure before the joined-profile control

This attempt did not launch its mathematical child. The live finite
capacity-selector cohort had not yet written its first checkpoint when
the admission wrapper tried to read it. The wrapper raised
`FileNotFoundError`, recorded the failure in the unchanged protocol, and
released its own single-worker reservation.

The exact profile source and all scientific assertions remain unchanged.
A fresh attempt will wait for the live checkpoint to exist, inspect its
status and worker counts, and admit the mathematical child only after the
shared sixteen-worker limit permits it. No result certificate or failed
mathematical conclusion is claimed for this attempt.

The [protocol](protocol.json) pins the source hash, intended command,
external log, original campaign start/deadline and authorized extension.
