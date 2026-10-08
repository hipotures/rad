# Native symmetry failure and exact complex continuation

The original complex multi-provider attempt completed 32 exact witnesses but
then stalled in native HiGHS symmetry preprocessing. A fresh two-second native
profile of each affected live worker found at least 90% of its sampled cycles
inside `HighsSymmetryDetection`. The requested six-second MILP time limit did
not bound this preprocessing. All 13 affected workers, including the earlier
h40 ground worker, were ended individually only after checking current PID,
birth tick, parent/source command and a fresh native profile. No productive
coefficient or phase verification was ended. Original completed witnesses,
inputs, protocols, checkpoints and failure logs remain unchanged.

The original ground cohort `063400` is scientifically PARTIAL: 15 of 16
witnesses completed. The original multi-option cohort `065400` has a FAILED
wrapper and 32 complete scientific witnesses. Its coordinator additionally
hit a `JSONDecodeError` while reading the predecessor's concurrently updated
checkpoint. It emitted no summary. A separate postmortem source and new
terminal summary record this state; its original stale checkpoint remains
intact. The terminal record corrects the successor's phantom predecessor
allocation without restarting any useful worker.

The fresh selector sets native `mip_detect_symmetry=False`. The installed
HiGHS interface accepted this option and read it back as false. Thirty-six
small controls proved literal offered-job identity between the old and new
opportunity enumeration. Early termination of chain-table enumeration only
omits tables that cannot enter the bounded offered list. Exact integer
capacity/formal-child feasibility, the greedy fallback, and all changed
scalar, physical, Gram, phase, target and guard checks remain in force. The
complete h8 Gaussian dirty basis and shared exchange also passed.

The fresh `072400` continuation excluded all 32 completed configurations and
verified all 136 distinct remaining configurations with zero errors. It took
709.761 seconds, or 689.81 verified cases/hour, including the initial stale
allocation interval. After correcting that record at 07:30:20 UTC, 119
witnesses completed over 398.652 seconds, an observed 1,074.62/hour. The latter
measurement uses case-file completion timestamps and the recorded capacity
transition; it is not a matched-input algorithm speedup. Per-case complete
witness time averaged 44.282 seconds, with median 40.456 seconds. Peak worker
RSS was 1,871,432 KiB; the wrapper recorded no swaps.

The strongest nonalternating h28 continuation has R=87,503, candidate
`390a8e09073b3bbbf59b9307eb143e3865b9541676d3538a6b048ef24022eeab`.
This remains a producer witness. The independently promoted h28 delayed
boundary is R=88,377; no new final multiplication bound follows merely from
the continuation's smaller role count.

Source and evidence are in `code/finite_complex_clone_nosym.py`,
`code/finite_complex_nosym_control.py`, `code/finite_stop_native_symmetry.py`,
`code/finite_complex_options_repair.py` and
`code/finite_complex_postmortem_summary.py`. Exact commands, hashes and
outcomes are retained in the corresponding `071700`, `071800`, `072400` and
`073000` topic runs. Full external cases/logs live under the campaign workroot's
`derived/finite/<run>` and `logs/finite/<run>`. Readable profile reports and
live-identity records are UTF-8 evidence. The two small binary perf captures
remain external observations; their commands are retained, but a new live
profile cannot reproduce the same sampled bytes. Archived PID records do not
authorize control of future processes.
