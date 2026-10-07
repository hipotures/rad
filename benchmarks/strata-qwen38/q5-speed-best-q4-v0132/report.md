# Q5 actual 31,400 tokens speed test — K24 / two RTX4090

Status: COMPLETE

historical Q4 median and historical fastest run; NOT_CONTROLLED_A_B: required local Q5 runtime fallback+Q8 PLE mmap, different quant/cache capacity/adaptive cache history; no simultaneous rerun Q4

1 warmup excluded; 3 sequential measured runs. Actual prompt checked with tokenizer and API. Literal saved Q4 prompts, only model alias changed. Greedy,256 output; no prefix reuse; max context262144. No model download or weights changes. Existing patched runtime/head/build/commands recorded per raw result. Cheap telemetry1Hz; PSS only before/after request; MemAvailable floor12GiB.

| model | actual prompt | output | PP tok/s | TG tok/s | TTFT s |
|---|---:|---:|---:|---:|---:|
| Q4 historical median ×3 | 31400 | 256 | 2614.9 | 120.7 | 12.091 |
| Q4 historical fastest | 31400 | 256 | 2614.9 | 121.8 | 12.088 |
| Q5 median ×3 | 31400 | 256 | 371.7 | 79.4 | 84.576 |

| Q5 run | PP tok/s | TG tok/s | TTFT s |
|---|---:|---:|---:|
| 1 | 371.7 | 73.3 | 84.567 |
| 2 | 371.7 | 87.6 | 84.576 |
| 3 | 371.5 | 79.4 | 84.619 |

Delta against Q4 median: PP -85.8%; TG -34.2%.

Peak measured RAM(system total minus available):101.81GiB; VRAM0/1:23.31/23.50GiB.

Q5 routes unsupported Q6_K/Q8_0 layer2 wholly through CPU and reads native Q8_0 PLE with mmap. Q4 used the original runtime/default PLE I/O. This is the same workload/topology/settings comparison, with required model-specific support changes, not an isolated quant-only/runtime-only A/B. No quality conclusion.

Raw requests, complete output/streams/stats:raw/. Historical references:references/. Telemetry:telemetry/. Full config:configs/. Plan:plan.json. Summary:summary.json. Earlier smoke and failed loader tests untouched. Both servers stopped after this test.

Median Q5 prompt processing wall: 84.485s; decode wall: 3.224s; total client wall: 87.822s. Median MTP acceptance: 67.7%; median mean accepted length: 1.59.

All three measured requests had zero reuse and no memory abort. Normal logical expert file-tier counters were 0 MB for every measured request; experts use the full resident RAM arena. This does not imply zero total storage traffic: Q8_0 PLE is mmap-backed, and physical host SSD I/O behind virtiofs is not attributable from guest read_bytes.

CSV: summary.csv. Full PP/TG timing, MTP, per-second CPU/GPU/RAM and I/O data are retained in raw/ and telemetry/.
