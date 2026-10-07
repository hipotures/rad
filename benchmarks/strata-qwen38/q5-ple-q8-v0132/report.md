# Native Q8_0 PLE support for Q5 — PASS

Q8_0 support was added to the separate Q5 checkout. Q5 now reaches READY and generates 64 tokens with normal MTP on both one RTX4090 and two RTX4090 (layer split K24). This is smoke validation only; whole-model parity, long-context correctness, needles and speed benchmarks remain pending.

## Why adding just the name was insufficient

`src/kernels/ngram.cpp` has the allowed-format branch in `PleTable::open`. Without decoder and stride changes, admitting Q8_0 would retain an IQ4_NL reader and a 90-byte stride. Native Q8_0 has five 34-byte blocks per 160-element row: 170 bytes.

Changes: Q8_0 flag/detection; native `strata::dequantize_q8_0` per block; 170-byte row stride for size checks and row offsets; maximum scratch row buffer increased to 170; format/reset handling. Existing IQ4_NL/Q5_0/FP8 branches retained. Q8_0 support uses `--ple-io mmap`; direct Q8_0 remains explicitly rejected. No new CUDA kernel or changed model weights.

Actual table is `per_layer_token_embd.weight`, Q8_0, shape [160, 320001536], 54,400,261,120 bytes, offset 192 in shard 3. GGUF files and the existing pack were not modified.

## Validation

`ple_q8_parity` compares selected actual rows (first, last and dispersed rows), issue/collect, and prefill bulk gather against ggml's Q8_0 reference `to_float`. Maximum absolute difference 0. It also checks format, bytes_read and explicit direct-mode rejection. This samples the table, rather than comparing all 320 million rows.

Regression suite: 7/7 PASS, including CPU-only experts, GGUF reader/split/layout, GPU Q5_K/Q8_0 parity, intentional GPU Q6 rejection, and PLE reader selftest. Logs: `logs/ple-q8-real-parity.log`, `logs/regressions.log`.

## Sequential model smoke

| topology | actual prompt | output | drafted | accepted | smoke PP t/s | smoke TG t/s | min MemAvailable GiB |
|---|---:|---:|---:|---:|---:|---:|---:|
| Q5-PLE-Q8-1GPU-MMAP | 2048 | 64 | 61 | 33 | 125.8 | 28.9 | 61.87 |
| Q5-PLE-Q8-2GPU-K24-MMAP | 2048 | 64 | 58 | 36 | 139.2 | 46.5 | 60.15 |

These are one short 2048-token prompt / 64-token greedy output per topology, not controlled speed benchmark medians or 64K results. Full text, request, stats and telemetry are under `raw/` and `telemetry/`.

Logs confirm layer 2 routed CPU entries >0 and zero GPU expert entries in prefill/decode, GPU expert cache hits on the supported layers, repeated CUDA verify graph captures and active MTP. Single-GPU telemetry shows GPU1 at only its idle 1 MiB; the two-GPU run has caches and activity on both GPUs. No CUDA/host OOM or 12 GiB memory-floor abort.

The initial load with the server's default direct PLE I/O failed before READY. It was preserved as `raw/load-with-default-ple-io-failure.json`, `logs/Q5-CPU-1GPU-engine.log` and `logs/driver-default-ple-io.log`. Setting the supported `--ple-io mmap` resolved that configuration issue without another engine patch.

## Reproduction and pending work

Base HEAD/tag: v0.1.32 / c499bd102e7a4135c0de389dcfe38c399759ccc8. Separate build: `/srv/ai/strata-v0.1.32-q5/build-ple-q8/strata`, CUDA Release arch89, MMQ_KQUANTS OFF. Earlier builds/results retained. Full combined diff: `q5-loader-cpu-ple.patch`; provenance, patch SHA256, engine SHA256, original model stats and full configs/commands in `environment.json`, `raw/` and `configs/`.

Clean `/srv/ai/strata-v0.1.32` tracked files unchanged; six GGUF size/mtime/inode checks unchanged. No commit or push. Both servers have stopped and GPUs are free. Original verified SHA256 manifests retained; models were not downloaded or hashed in full again.

Pending: same-GGUF whole-model llama.cpp parity, 32K/128K needles and long-context correctness before speed measurements. Short readable outputs and component parity do not establish model quality. STATUS.md/STATUS.json preserve the next action.
