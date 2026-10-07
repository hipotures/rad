# Actual split handoff and causal router availability

COMPLETE_POSITIVE_DIAGNOSTIC

COMPLETE_NEGATIVE for the declared next-layer CPU calculation; most predictions are too late even under the optimistic one-blob test. This does not close GPU/low-rank/earlier-layer predictors.

| Profile | Next layer | Top10 precision | Nonlocal recall | True nonlocals | Predicted nonresidents | Lead median us | CPU score median us | Warm optimistic ready |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 32k | 6 | 44.0% | 37.5% | 16 | 61 | 241.4 | 320.0 | 0.0% |
| 32k | 21 | 45.2% | 66.7% | 15 | 52 | 231.5 | 335.6 | 5.5% |
| 32k | 25 | 54.2% | 44.4% | 27 | 33 | 310.6 | 363.5 | 4.4% |
| 32k | 26 | 25.4% | 10.7% | 28 | 90 | 250.2 | 328.1 | 8.7% |
| 32k | 41 | 59.6% | 81.8% | 11 | 76 | 220.7 | 377.4 | 2.2% |
| 32k | 47 | 34.0% | 40.0% | 15 | 548 | 336.3 | 329.4 | 9.8% |
| 128k | 6 | 49.2% | 56.7% | 30 | 68 | 244.2 | 366.6 | 8.0% |
| 128k | 21 | 45.9% | 22.7% | 22 | 72 | 230.4 | 361.3 | 4.3% |
| 128k | 25 | 55.7% | 44.4% | 45 | 52 | 309.0 | 359.9 | 3.2% |
| 128k | 26 | 31.7% | 6.5% | 31 | 68 | 254.1 | 367.9 | 3.7% |
| 128k | 41 | 52.7% | 58.8% | 17 | 65 | 221.5 | 363.0 | 3.7% |
| 128k | 47 | 32.3% | 22.2% | 45 | 573 | 442.4 | 365.0 | 25.1% |

Predictions use the current normalized MoE activation and the actual next BF16 gate. True next-router experts are labels only. First64windows and six chosen layer pairs are a bounded study of repository maintenance, with small rare-tail counts. No universal generalization claim.

The optimistic readiness check charges the measured single-thread CPU score/top10 cost and one weight blob at12.6GB/s with4.2uslaunch floor. It ignores multiple predicted blobs, victim selection and reader hazards; passing does not establish a feasible policy. Many predicted nonresidents are false positives, particularly layer47. Model math/routing never changed.

32k: actual GPU0 outgoing-copy median 19.456us; GPU1 incoming-copy median 20.480us. Host transition median 0.150us. GPU0 tail-sync median 89.240us; GPU1 tail-sync median 764.808us.
128k: actual GPU0 outgoing-copy median 19.456us; GPU1 incoming-copy median 19.968us. Host transition median 0.200us. GPU0 tail-sync median 82.759us; GPU1 tail-sync median 735.007us.

These are event-bracket durations on each GPU, plus separate CPU observations. The two transfer medians are not summed into a claimed measured boundary total. GPU1 tail-sync includes head/dense/resident/KV work and cannot be labeled transfer or miss cost. No direct subtraction of cross-device clocks.

Instrumentation is not a headline binary. Same diagnostic v5/v7 output IDs, branches and expert entries are recorded in summary.json; observed TG changes are not a guaranteed overhead bound. External graph events, activation copies and first-head logit copies add diagnostic work.

First-window248320-vocabulary logits are finite at both profiles. Only the same-input comparison may be interpreted as numerical parity; free-generated later heads are not teacher-forced comparisons.

v1 diagnostic load succeeded, warmup invalid because default-captured events were not observable. Preserved source/binary/logs and invalid request. Repaired with external event nodes; two-device graph reproducer and13targeted native tests pass.
Initial CPU scorer analyses were concurrent; their timing costs excluded. Serial analysis-r2 is authoritative; no new inference request was needed.

Compatible-slot placement replay; targeted GPU wait diagnostics if needed to explain the CPU/mapped tail. Optional numeric same-input head comparison strengthens frequency correctness.
