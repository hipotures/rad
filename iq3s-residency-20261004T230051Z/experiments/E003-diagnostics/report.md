# E003 demand, readiness and critical-path diagnostics

Status: COMPLETE_POSITIVE for full trace accounting; causal performance attribution
remains limited. Both fixed-profile4096-output traces and all six independent
1024-output task traces pass route, branch, slot publication and API/footer checks.
Exact frozen C++ selector replay matches every promotion and final float32 heat
value on the two repository traces. These gates precede policy projections.

Actual expert-cache storage:

| Total capacity | GPU0 slots / bytes | GPU1 slots / bytes |
|---|---:|---:|
|32768|10240 /19824128000|8477 /18323200000|
|131072|10183 /19712998400|8437 /18220492800|

These are per-device physical allocations and variable byte classes. Same-layer
replacement never borrows a differently sized slot or changes K25 ownership.
Storage freed by smaller context limits is modest, consistent with streamed KV.

32k trace:2117280 routed entries,2080504local,35552CPU,1224mapped;5226promotions,
10697139200promotion bytes. 128k trace:2351040entries,2305764local,43557CPU,
1719mapped;7069promotions,14373222400bytes. Reported hit denominator excludes
mapped work. Exact route and issue/publication replay has zero mismatches.

Observed blocking `apply_pending` brackets total121.6ms and166.0ms, versus
approximately25.5s and30.9s window wall time. This includes publication/upload
overhead and cannot be called pure DMA stall. Issue-to-observed-publication medians
are2.90/2.97ms; these include delayed observation, not GPU copy-event duration.
All expert promotion time is not exposed request latency.

At32k window-aligned diagnostic interval TG rises125.5→150.9→174.4→168.3tok/s;
MTP acceptance78.7→89.3→95.3→90.9%, local all-demand hit97.47→97.85→98.10→98.66%.
At128k TG94.6→138.4→137.4→143.2 while acceptance is roughly75–78%. The first
interval includes lazy window captures and startup effects. These are single
instrumented trajectories, not headline medians or causal adaptation effects.

Lagged nonlocal demand versus next-layer GPU-reach waits has weak negative
aggregate correlation(-0.058/-0.033); same-layer nonlocal demand versus host work
has positive correlation(0.272/0.240). Layer, T and resident compute confound these
statistics. The wait clocks overlap GPU work and are not an additive miss-cost
budget. Individual expensive misses and publication waits are retained in each
profile's diagnosis.json, including repeated expert IDs and per-layer brackets.

The six predictor tasks are genuinely different code/math/prose/structured tasks,
not repository nonce copies. Their cache history continues serially, but labels
will be split by whole episode. Training/calibration/holdout are declared in E005.

## Repairs and limitations

Separate v1–v4 failed instrumentation attempts remain. v5 built and passed the
buffer lifecycle test and real IQ3_S parity on layers0/1/2/12. Native62pass/4known
environmental failures; two optional tests were not registered without a local
checkout venv. See repair-history.md, build/tests and per-attempt records.

128k startup failed before any request because the external port probe rejected
TIME_WAIT; v5-portfix changes only harness reuse/selection and preserves the empty
failed attempt. Reader initially assumed zero-based rounds; runtime round numbers
include prefill, so an explicit number→index map repairs it without trace changes.

Diagnostic overhead is NOT proven zero. Headline speed uses the clean control and
future separate uninstrumented candidates. Diagnostic stream flushing happens
after engine timing but inside client wall time. One trace/control pair has equal
routing accounting but does not by itself identify instrumentation overhead.

Next: finite byte/slot/queue replay, learned scoring on isolated episodes, then a
trace-justified minimal runtime candidate. No capacity or coordination ceiling is
declared from these observations alone.
