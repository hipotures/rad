# Selected-layer GPU wait diagnosis

Status: COMPLETE_POSITIVE_DIAGNOSTIC. No algorithm change.

The48external CUDA timing events bracket four phases at layers2,24,40 after the existing graph replay/synchronization. Bothprofiles pass full accounting, exact output/router/MTP trajectory comparison, and one-position numeric head parity (KL0/maxdifference0). Event fixture,13targeted native tests and realIQexpert parity pass.

| Profile | Layer | Phase | Median us | P95 us | CPU-positive median/P95 us | Mapped-positive median us (N) |
|---|---:|---|---:|---:|---:|---:|
| 32k | 2 | GPU plan waitA plus mapped plan copy | 9.2 | 31.7 | 9.2/17.8 | 9.2 (33) |
| 32k | 2 | resident grouped native expert compute | 78.8 | 91.1 | 80.9/90.1 | 74.8 (33) |
| 32k | 2 | waitB plus staging/fetch and mapped native grouped compute | 9.2 | 9.2 | 9.2/164.9 | 165.9 (33) |
| 32k | 2 | CPU-completion waitM kernel only | 5.1 | 22.5 | 5.1/65.9 | 6.1 (33) |
| 32k | 24 | GPU plan waitA plus mapped plan copy | 8.2 | 19.5 | 8.2/14.3 | 8.2 (25) |
| 32k | 24 | resident grouped native expert compute | 71.7 | 89.1 | 75.8/89.1 | 73.7 (25) |
| 32k | 24 | waitB plus staging/fetch and mapped native grouped compute | 9.2 | 9.2 | 9.2/163.3 | 163.8 (25) |
| 32k | 24 | CPU-completion waitM kernel only | 4.1 | 25.6 | 4.1/65.7 | 4.1 (25) |
| 32k | 40 | GPU plan waitA plus mapped plan copy | 9.2 | 16.4 | 9.2/16.2 | 8.7 (6) |
| 32k | 40 | resident grouped native expert compute | 73.7 | 98.3 | 79.9/98.2 | 87.0 (6) |
| 32k | 40 | waitB plus staging/fetch and mapped native grouped compute | 9.2 | 10.2 | 9.2/10.2 | 192.5 (6) |
| 32k | 40 | CPU-completion waitM kernel only | 4.1 | 28.7 | 4.1/69.5 | 4.1 (6) |
| 128k | 2 | GPU plan waitA plus mapped plan copy | 9.2 | 18.6 | 9.2/25.9 | 9.2 (40) |
| 128k | 2 | resident grouped native expert compute | 72.7 | 89.1 | 74.8/88.1 | 72.7 (40) |
| 128k | 2 | waitB plus staging/fetch and mapped native grouped compute | 9.2 | 10.2 | 9.2/163.8 | 166.4 (40) |
| 128k | 2 | CPU-completion waitM kernel only | 5.1 | 62.5 | 6.1/124.2 | 6.1 (40) |
| 128k | 24 | GPU plan waitA plus mapped plan copy | 8.2 | 32.6 | 8.2/17.4 | 8.2 (35) |
| 128k | 24 | resident grouped native expert compute | 65.5 | 84.6 | 68.6/86.0 | 73.7 (35) |
| 128k | 24 | waitB plus staging/fetch and mapped native grouped compute | 9.2 | 10.2 | 9.2/165.5 | 169.0 (35) |
| 128k | 24 | CPU-completion waitM kernel only | 4.1 | 52.8 | 4.1/112.2 | 5.1 (35) |
| 128k | 40 | GPU plan waitA plus mapped plan copy | 9.2 | 16.4 | 9.2/17.4 | 9.2 (16) |
| 128k | 40 | resident grouped native expert compute | 66.6 | 93.2 | 74.8/94.2 | 75.8 (16) |
| 128k | 40 | waitB plus staging/fetch and mapped native grouped compute | 9.2 | 10.2 | 9.2/11.0 | 195.1 (16) |
| 128k | 40 | CPU-completion waitM kernel only | 4.1 | 68.2 | 4.1/149.5 | 5.1 (16) |

All4096output IDs, allMTPwindowT/acceptances and allrouter entries exactly match previousv7 diagnostics, first-head logits bit-identical at bothprofiles. Direct GPU spans distinguish mostly overlappedCPUwork from occasional exposedCPUwait and expensive mapped execution. This is not a policy or global TG gain.

Same-trajectory diagnosticTG differs +21.5%32k/-9.45%128k across separate builds/time. Cannot certify<=1% overhead or claim a causal node speedup from onepair. All diagnosticTG excluded from headline ranking.

The CPU-completion span brackets only the GPU wait kernel before returned rows are copied; it includes event/doorbell floors. Most CPU-positive groups have only a few microseconds exposed after local expert compute, but the tail can be much larger. Mapped-positive groups are measurably more expensive than the empty mapped launch. These phases are not the time for allCPUexpert arithmetic, and not the total critical path. Do not multiply the selected-layer results by48.

The32k/128k CPU record buffers written are714816/834624bytes; reserve capacity is120000records(5.76MB). There are no explicit newGPUbuffers; internal CUDAevent memory is unknown. Original expert slot/class capacities match. All histories, rows, clocks and tests are retained.

Reproducer: variants/diagnostic-v8/diagnose-profiles.sh with a fresh --attempt name. This tested launcher is diagnostic only and remains separate from clean headline binaries.

