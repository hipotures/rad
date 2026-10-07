# UD-Q4_K_XL — single RTX 4090 sanity

Load/smoke: **OK**. CUDA0 only; GPU1 stayed at1 MiB. No CUDA/host OOM. Existing verified pack and MTP; no downloads, engine changes or experts.bin.

Config: context65536, KV int8, MTP spec4/min-p0.5, vision off, projection off. Strata0.1.31, HEAD `9259cad4cfa3543cd3b8decab5962672b968c649`. Available RAM before start: 158.12 GiB; resident budget80 GiB.

RAM holds19338 experts (56.45 GiB, page-locked); GPU cache5238 experts (15.28 GiB). Together all24576 experts are covered. The whole ~71.7 GiB set is **not duplicated in RAM**: upstream copies only the GPU-cache complement, even with80 GiB budget.

## Speed64K: 3 runs, zero prompt reuse, temperature0, 256 generated tokens

| run | actual prompt tokens | PP t/s | PP s | TTFT s | TG t/s | decode s | peak RAM used GiB | peak VRAM GiB | decode expert file MB |
|---|---|---|---|---|---|---|---|---|---|

| 1 | 63300 | 1416.70 | 44.68 | 44.82 | 36.60 | 6.99 | 65.28 | 23.48 | 0.0 |

| 2 | 63300 | 1539.80 | 41.11 | 41.26 | 44.20 | 5.79 | 65.29 | 23.48 | 0.0 |

| 3 | 63299 | 1539.30 | 41.12 | 41.27 | 43.40 | 5.90 | 65.32 | 23.48 | 0.0 |


Medians: PP 1539.3 t/s, TG 43.4 t/s, TTFT 41.27 s, PP time 41.12 s, decode time 5.90 s.

## Residency and I/O

All three speed runs: decode `file_blobs=0`, `file_mb=0.0`; misses are served from resident RAM. Cumulative file bytes in smoke.log also include startup/prefill/cache refills and must not be interpreted as decode traffic. Prefill/refill does read native GGUF files for GPU-cached experts without a RAM duplicate. `/srv/ai` is virtiofs, so logical file reads do not prove physical host SSD I/O.

Peak across startup/smoke/speed/quality, sampled around1 s: RAM used (total−available) 65.33 GiB; sum process RSS 133.26 GiB (includes mapped/file-backed pages); GPU0 VRAM 23.48 GiB. Minimum MemAvailable 95.80 GiB. GPU utilization/power and system/process CPU are in telemetry-64k-1/2/3.csv.

## Quality

Exact saved final IQ3_S requests used, including system prompts, temperature, reasoning_effort and caps: A1536, B/C8192. Only model name changed. All replies ended before caps. No ranking or LLM judge.

- [A-coding-debug](/srv/ai/benchmarks/strata-qwen38/results/quality/UD-Q4_K_XL/A-coding-debug.txt)

- [B-mathematical-reasoning](/srv/ai/benchmarks/strata-qwen38/results/quality/UD-Q4_K_XL/B-mathematical-reasoning.txt)

- [C-repository-architecture](/srv/ai/benchmarks/strata-qwen38/results/quality/UD-Q4_K_XL/C-repository-architecture.txt)


One concrete limitation: resident-budget does not produce a full routed-expert RAM duplicate, so prefill/refill still reads GGUF files. Decode expert file reads were zero.

Server stopped after test. No commit or push.
