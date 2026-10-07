# Initial schedule environment failure

The first small schedule comparison selected the system Python 3.14 without
the campaign math environment. It stopped before compiling any candidate:
`frame_reuse.optimize_chains` raised `ModuleNotFoundError: No module named
'numpy'`. No candidate from this failed invocation is accepted.

The repaired invocation uses the existing campaign environment
`envs/math/bin/python` (Python 3.14.7, NumPy 2.5.3, SciPy 1.18.1). It was
recorded in a fresh run,
`20261007T230730Z-finite-schedule-small`, and passed the complete scalar maps,
both frame directions, and both dirty-scratch orientations for 30 cases.

The run-directory timestamp of the initial attempt was a prospective label;
the repaired run's machine timestamps are recorded in its result JSON and
are authoritative for chronology.
