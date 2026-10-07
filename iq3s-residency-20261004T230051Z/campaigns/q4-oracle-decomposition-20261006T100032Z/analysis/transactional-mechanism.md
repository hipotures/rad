# Comparable transactional accounting

| Profile | Arm | Victim-absent entries | Victim reloads | Victims reloaded >=2 times | Actual target-admission hit entries | Admissions reused in >=2 invocations | End-censored admissions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 128k | F256 | 85,759 | 89,901 | 16,702 | 118,240 | 73,647 | 10,700 |
| 128k | FF | 19,736 | 52,635 | 13,583 | 73,004 | 48,773 | 9,201 |
| 128k | current | 185,345 | 24,222 | 6,725 | n/a | n/a | n/a |
| 256k | F256 | 83,093 | 88,454 | 15,950 | 115,474 | 70,435 | 10,448 |
| 256k | FF | 17,639 | 53,520 | 13,455 | 73,870 | 48,001 | 8,920 |
| 256k | current | 168,745 | 23,217 | 6,592 | n/a | n/a | n/a |
| 32k | 6464 | 87,241 | 87,381 | 15,743 | 112,621 | 67,933 | 10,504 |
| 32k | 64F | 15,886 | 51,711 | 13,349 | 70,678 | 46,117 | 9,251 |
| 32k | F64 | 86,179 | 87,823 | 15,784 | 113,420 | 68,272 | 10,519 |
| 32k | FF | 11,736 | 53,850 | 13,729 | 73,273 | 47,616 | 9,306 |
| 32k | current | 151,049 | 20,547 | 5,594 | n/a | n/a | n/a |

All medians are derived from the preserved per-attempt journals. Victim-absent demand is an observation, not exclusive causal latency. Readmission resets absence; initial spare donors are separate.
