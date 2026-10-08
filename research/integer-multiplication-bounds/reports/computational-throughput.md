# Measured candidate throughput

This continues campaign 20261007T222521Z without resetting its immutable
2026-10-08 08:25:21 UTC deadline. The user observed long periods of one to
three active CPUs and explicitly requested sixteen computing processes,
delegated calculation batches, and preparation of the next useful batch
while computations run.

## Diagnosis

The resource inspection found sixteen CPUs in affinity 0-15, no CPU quota
at the session, user or user-slice cgroup ancestors, no throttling, no swap
and ample available memory. Both RTX4090 GPUs were idle during exact
circuit verification. Low earlier usage was caused by sparse dispatch and
gaps between short experiments, mathematical derivation and reporting.
OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1 are per-process thread limits;
they do not limit a process pool to one CPU. Exact Python graph/rational
work needs independent processes rather than a sixteen-thread BLAS team.

The bounded [first throughput run](../runs/20261008T004115Z-singleton-throughput/)
uses fifty distinct complete h50 position vectors. Every case executes the
unchanged global scalar map, positive-envelope inclusion, maximum-flow
controller plan, physical scalar/frame compilation and target checks.
Only immutable local DAGs already checked by their original verifier are
cached. Two small exact controls compare all cached/uncached outputs.

## Measurements

| Phase | Unique verified cases | Processes | Wall seconds | Cases/hour |
|---|---:|---:|---:|---:|
| Serial, original local construction | 2 | 1 | 97.585 | 73.78 |
| Serial, verified local cache | 2 | 1 | 84.791 | 84.91 |
| Dynamic process pool, local cache | 46 | 12 | 197.108 | 840.15 |

The parallel throughput is 11.39 times the uncached serial measurement,
or 9.89 times the cached serial measurement. The cases are distinct,
structurally matched perturbations, not identical-input repetitions. Two
serial cases per condition are a small sample; no universal speedup or
isolated cache-effect claim follows. The complete fifty-case run took
379.486 seconds. Each candidate is evaluated once, and completed workers
receive pending tasks without a batch barrier.

Across all fifty cases, mean phase costs were:

| Exact phase | Mean seconds/case |
|---|---:|
| Local construction/checks | 1.007 |
| Global scalar map | 1.709 |
| Positive envelopes | 25.315 |
| Controller flow | 5.102 |
| Compilation and physical verification | 13.852 |
| Every target | 0.202 |

The largest observed lifetime RSS was 3354268 KiB, about 3.20 GiB per
process. This is an upper bound for a case in a reused worker, not its
incremental allocation. A 6 GiB virtual-address cap applies to each worker;
the campaign RAM ceiling remains 96 GiB. Resource snapshots and complete
timing logs retain evidence of system memory, process CPU and GPU load.
Machine-wide measurements may include unrelated work.

## Scientific outcome and next action

The best first-batch vector is `[23]*48+[22,22]`, ID
`abda739268bd6b9473e6b5d05fa63c4e7ca721783ecc2e4c3c1289635f261563`,
with 485237 compiled roles and 8351 retained links. This is 123 roles fewer
than the promoted 485360 bit primitive. Its full producer finite checks
pass. The independent [arbitrary-vector audit](review-singleton-positions.md)
also passes its full uncached coefficient/frame replay, h6/h8 dirty basis
and all four shared three-stage exchanges. Exact downstream composition is
recorded separately; this run alone does not assert a new theorem exponent.

Following the later explicit sixteen-process instruction, a fresh agent
queue schedules 219 distinct useful near/far perturbations, excluding the
preceding fifty candidate IDs. Fifteen evaluations plus one reviewer meet
the sixteen-process target during promotion. No old job is restarted and
the old twelve-worker protocol retains its true historical configuration.
The next queue will use the best then available vector, with completed and
live candidate identities excluded.

The measured envelope cost justifies a fresh direct constructor for the
known E(C,V) family. It produces exactly the same canonical Space,
rational indicator basis and signed tags as generic incidence elimination.
The original inclusion, compilation and target checks remain in place.
Every frame field, rational basis and target check matches at h8/h12 and
all 454388 h50 nodes. The full h50 unchanged flow/compiler/check also matches
the independently promoted 485237-role program and its compiled hash.
On that same h50 case, old/direct envelope times are 27.654/12.183 seconds,
a 2.27-fold reduction for this phase. This sequential same-case control
does not isolate every allocator/cache effect or establish a universal
speedup. See the [completed equality run](../runs/20261008T005626Z-direct-envelope-full/).
The construction uses the exact known triangle or signed-star component
structure, including unused-coordinate tags; a reviewer-requested domain
guard excludes an unrealizable two-point core with only one outside leaf.

No GPU conversion is warranted for these symbolic sparse traversals.
The mathematical agents continue distinct construction/transfer questions
while workers compute; useful candidates/hour is the optimization metric.

## Recovery

Source: [singleton_sensitivity.py](../code/singleton_sensitivity.py).
The run protocol pins all imported source hashes and upstream commit,
candidate definitions, deadlines, commands and environment. Completed
case JSON, summary and timing/resource evidence are retained. Dynamic
neighborhood source and protocol are recorded separately; a live checkpoint
is not an immutable evidence archive or permission to control a process.


## Campaign closure and later matched limits

The user extended this same clock to10:00UTC/12:00CEST. The historical
12-worker benchmark above retains its actual configuration; later
productive sweeps use the authorized16-process scheduling policy with
shared owned reservations and no nested BLAS/OMP teams. Final early
cohort085400completed56scientific cases with42distinct compiled
witnesses and zero failures in774.701seconds:260.23cases/hour, or
195.17distinct compiled witnesses/hour. Those search families differ
from the original50-case perturbation benchmark, so these are not
a controlled universal before/after speedup comparison. Outcomes include
the independently promotedR529181graph. Peakworker lifetimeRSS was
6518696KiB; complete original case timing/memory records are archived.

Read-only telemetry was extended without restarting workers. Its final
86samples ended naturally at09:59UTC; no process was signalled. Complete
JSONL and execution evidence, protocol and closure hashes are retained
in the final telemetry inventory and archive. GPUs were not forced
into sparse exact symbolic traversal. The verified phase improvements,
scientific throughput, distinct graphs and limitations remain separate
from machine utilization.
