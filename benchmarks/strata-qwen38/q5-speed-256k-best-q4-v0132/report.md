# Q5 actual 259,500 tokens speed test — K24 / two RTX4090

Status: COMPLETE

historical Q4 median and historical fastest run; NOT_CONTROLLED_A_B: required local Q5 runtime fallback+Q8 PLE mmap, different quant/cache capacity/adaptive cache history; no simultaneous rerun Q4

1 warmup excluded; 3 sequential measured runs. Actual prompt checked with tokenizer and API. Literal saved Q4 prompts, only model alias changed. Greedy,256 output; no prefix reuse; max context262144. No model download or weights changes. Existing patched runtime/head/build/commands recorded per raw result. Cheap telemetry1Hz; PSS only before/after request; MemAvailable floor12GiB.

| model | actual prompt | output | PP tok/s | TG tok/s | TTFT s |
|---|---:|---:|---:|---:|---:|
| Q4 historical median ×3 | 259500 | 256 | 5665.0 | 94.6 | 46.324 |
| Q4 historical fastest | 259500 | 256 | 5667.0 | 101.3 | 46.294 |
| Q5 median ×3 | 259500 | 256 | 394.4 | 67.3 | 658.608 |

| Q5 run | PP tok/s | TG tok/s | TTFT s |
|---|---:|---:|---:|
| 1 | 380.3 | 65.2 | 683.019 |
| 2 | 394.4 | 67.3 | 658.608 |
| 3 | 412.1 | 73.8 | 630.472 |

Delta against Q4 median: PP -93.0%; TG -28.9%.

Peak measured RAM(system total minus available):104.23GiB; VRAM0/1:23.31/23.50GiB.

Q5 routes unsupported Q6_K/Q8_0 layer2 wholly through CPU and reads native Q8_0 PLE with mmap. Q4 used the original runtime/default PLE I/O. This is the same workload/topology/settings comparison, with required model-specific support changes, not an isolated quant-only/runtime-only A/B. No quality conclusion.

Raw requests, complete output/streams/stats:raw/. Historical references:references/. Telemetry:telemetry/. Full config:configs/. Plan:plan.json. Summary:summary.json. Earlier smoke and failed loader tests untouched. Both servers stopped after this test.

Configured prefill chunk:32768; actual chunk:16384 for both historical Q4 and Q5.

Q5 median prompt processing wall:657.996s; decode wall:3.802s; MTP acceptance:70.18%; mean accepted length:1.667.

Peak process RSS:140.203GiB includes file-backed mappings; peak system RAM usage is reported separately.

Comparison classification:NOT_CONTROLLED_A_B (historical Q4, Q5 support patches and native PLE mmap). Routed-expert file counters:0 MB for all measured requests; no claim about all host physical storage I/O.
