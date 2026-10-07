# Qwen3.8-Flash-Next standalone runtime optimization campaign

Run directory: `/srv/ai/benchmarks/qwen38-flash-next-runtime-opt-20260830T155104Z`

Campaign date: 2026-08-30 UTC. This is a new, self-contained experiment using only measurements and source inspection performed for this run. The model was the three-shard Unsloth `UD-IQ4_XS` GGUF; no alternate checkpoint, vision projector, or quantization sweep was used.

## 1. Executive result

The best configuration is one request at a time, CUDA graphs enabled, lazy tensor reads enabled, Flash Attention enabled, and a context-specific ubatch. Two-request continuous serving was a throughput loss at every formal context. The current server did not reuse any evaluated prefix tokens for this hybrid recurrent/sparse-attention model, despite recognizing a common prefix.

| Context | Latency-oriented recommendation | Throughput-oriented recommendation | Near-limit measured result |
|---:|---|---|---|
| 32K | 1 slot, `-c 32768 -b 2048 -ub 2048`, p20 placement | Same; queue requests sequentially | 30,976 prompt + 512 output: PP 635.28 tok/s, TG 27.54 tok/s, TTFT 48.77 s |
| 64K | 1 slot, `-c 65536 -b 2048 -ub 1024`, p20 placement | Same; queue requests sequentially | 63,744 prompt + 512 output: PP 440.81 tok/s, TG 23.47 tok/s, TTFT 144.62 s |
| 128K | 1 slot, `-c 131072 -b 2048 -ub 1024`, p24 placement | Same; queue requests sequentially | 129,280 prompt + 512 output: PP 366.55 tok/s, TG 17.64 tok/s, TTFT 352.72 s |

`p20` places PLE and routed experts in layers 0–9 and 24–33 on CPU. `p24` places PLE and routed experts in layers 0–11 and 24–35 on CPU. The latter costs about 3.6% decode throughput relative to the p20 warm baseline, but leaves 2.48 GiB more headroom on the tighter GPU at 128K.

## 2. Machine and runtime audit

### Machine

- GPUs: 2 × NVIDIA GeForce RTX 4090, 24,564 MiB nominal each; 24,082 MiB reported free before the campaign; no GPU processes.
- Driver: 595.84. CUDA compatibility/runtime reported by `nvidia-smi`: 13.2. Installed toolkit: CUDA 13.3, `nvcc` 13.3.73; `libcudart13` installed.
- CPU: AMD Ryzen 9 7950X3D, 16 guest-visible CPUs, one thread per exposed core. ISA includes AVX2, AVX-512F/DQ/BW/VL, AVX-512 BF16/VNNI/VBMI/VBMI2.
- NUMA: one guest-visible node, CPUs 0–15. Both GPUs have affinity 0–15.
- RAM: 156 GiB; about 153 GiB initially available. Swap: 0.
- PCIe: GPUs are PHB-separated with no NVLink; both links are capable of and became Gen4 ×8 under load.
- Model storage: `/srv/ai` on `virtiofs` (source `ai`), 1.8 TiB total, 1.1 TiB initially free. The guest cannot observe the host backing-NVMe device directly.

The complete command outputs are in `raw/audit.txt` and machine-readable fields are in `raw/audit.json`.

### Source and binary

- Source: `/srv/ai/llama.cpp-qwen4exp`
- Exact commit: `250b61446efc91e3a179c8677956f2667c8fbda0`
- Binary: `/srv/ai/llama.cpp-qwen4exp/build-cuda-sm89/bin/llama-server`
- Reported server version/build: `0.3.0-dev`, build 10707.
- Build: Release, GNU 15.2, CUDA enabled for architecture 89, CUDA graphs compiled in, OpenMP/native CPU enabled, BLAS disabled.
- Current source explicitly implements `QWEN4EXP` and includes Qwen3.8-Flash-Next conversion support. The model loaded as architecture `qwen4exp`: 48 blocks, 512 experts with 10 selected, hybrid SSM/full attention, 262,144-token metadata context.
- The actual binary help was inspected for context, batch/ubatch, Flash Attention, KV types, tensor override, layer split, slots, continuous batching, prompt cache, `--cache-reuse`, metrics, and `--tensor-read-lazy` semantics. No flags were assumed from an older build.
- CUDA graphs are compiled and enabled by default. Current source exposes the controlled fallback through `GGML_CUDA_DISABLE_GRAPHS=1`; there is no equivalent server CLI flag in this build.

No new build was required and no source tree was modified.

### Model and verified placement

The GGUF is 87.24 GiB of tensor data. PLE (`per_layer_token_embd.weight`) is 26.82 GiB. Routed-expert tensors total 55.43 GiB; all other tensors total only about 4.98 GiB. Startup logs, not merely commands, verified that the single combined override applied to PLE and every intended expert tensor. PLE remained CPU/mmap resident in all formal runs.

An initial contiguous expert placement (layers 0–15) failed because layer split assigned about 29.0 GiB to GPU1. This failure is preserved in `records/sanity-placement-32-failure.json` and its server log. Balanced bands were therefore used.

## 3. Method

The reusable `harness.py` starts a fresh server, waits for readiness, sends exact token arrays to avoid tokenizer ambiguity, streams responses for client-observed TTFT, samples process/GPU state every 0.5 s, and terminates the server. Formal prompts leave output headroom and request 512 output tokens. Every ordinary baseline prompt begins with a unique nonce. Prefix tests deliberately share only the large stable portion; concurrency prompts are independent.

Raw prompts, streamed responses, server logs, telemetry, configuration, and one structured record per request are retained under `prompts/`, `responses/`, `logs/`, `telemetry/`, `configs/`, and `records/`. The representative 64K profile additionally retains raw `pidstat`, `nvidia-smi dmon`, `vmstat`, `iostat`, and NUMA/proc snapshots under `raw/`.

### Single-stream baseline table

Cold and warm results are intentionally not averaged. These comparable baselines use `-b 2048 -ub 512`, p20 placement, one slot, lazy reads on, and CUDA graphs on.

| Context | State | Prompt tokens | PP tok/s | TG tok/s | TTFT | VRAM 0/1 MiB | RSS GiB | batch | ubatch |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 32K | COLD | 31,488 | 283.20 | 26.76 | 111.19 s | 20,926 / 20,556 | 24.03 | 2048 | 512 |
| 32K | WARM | 31,488 | 301.31 | 26.70 | 105.72 s | 20,926 / 20,556 | 25.68 | 2048 | 512 |
| 64K | COLD | 64,256 | 281.12 | 21.21 | 228.59 s | 21,458 / 21,332 | 25.70 | 2048 | 512 |
| 64K | WARM | 64,256 | 292.45 | 23.20 | 221.72 s | 21,458 / 21,332 | 28.19 | 2048 | 512 |
| 128K | COLD | 129,792 | 267.26 | 18.40 | 485.67 s | 22,518 / 22,880 | 25.02 | 2048 | 512 |
| 128K | WARM | 129,792 | 272.97 | 18.30 | 478.40 s | 22,518 / 22,880 | 29.72 | 2048 | 512 |

Cold major faults were 11,755, 28,114, and 16,878 respectively. Warm major faults fell to 313, 270, and 302. Guest-visible process storage reads were zero during every measured request.

## 4. Prefix/KV reuse

Requests A and B used exactly the same large prefix and different suffixes. C changed one token at approximately 50% depth and also used a distinct suffix. `speedup` below is A TTFT divided by the request TTFT; values above 1 do **not** represent cache reuse because the measured reused count was zero.

| Context | Request | Shared prefix | Reused tokens | Newly processed | TTFT | Wall time | TTFT speedup vs A |
|---:|---|---:|---:|---:|---:|---:|---:|
| 32K | A | 29,000 | 0 | 31,488 | 110.21 s | 132.38 s | 1.000× |
| 32K | B | 29,000 | 0 | 31,488 | 102.50 s | 123.65 s | 1.075× |
| 32K | C, midpoint mutation | 29,000 | 0 | 31,488 | 103.67 s | 124.32 s | 1.063× |
| 64K | A | 60,000 | 0 | 64,256 | 228.96 s | 253.12 s | 1.000× |
| 64K | B | 60,000 | 0 | 64,256 | 218.47 s | 241.20 s | 1.048× |
| 64K | C, midpoint mutation | 60,000 | 0 | 64,256 | 220.91 s | 244.23 s | 1.036× |
| 128K | A | 120,000 | 0 | 129,792 | 484.89 s | 513.57 s | 1.000× |
| 128K | B | 120,000 | 0 | 129,792 | 473.43 s | 503.45 s | 1.024× |
| 128K | C, midpoint mutation | 120,000 | 0 | 129,792 | 477.10 s | 506.14 s | 1.016× |

The server log recognized the common prefix but reported no usable cache checkpoint before the suffix and forced the full prompt to be re-evaluated. In current server source, rollback requires matching stored cache data; this architecture/path did not retain a usable checkpoint. `--cache-reuse` controls a minimum reusable KV-shift chunk after the common prefix; it does not repair the absent rollback state.

All nine outputs completed, and A/B/C response hashes were distinct. There was no suffix leakage or invalid-state reuse. Thus prefix caching was correct in the conservative sense—no invalid reuse—but provided **zero prompt-work or TTFT benefit** for this Qwen4Exp hybrid recurrent/sparse-attention path. The small B/C improvements are ordinary warm-state variation.

## 5. Concurrency / continuous serving

For concurrency 2, total server context was doubled and divided into two full-size slots: 65,536 for two 32K sessions, 131,072 for two 64K sessions, and 262,144 for two 128K sessions. No lane was accidentally divided into undersized slots. Aggregate output tok/s is total generated tokens divided by the interval from first output token to last completion. The per-user field shows both clients because fairness was poor.

| Context | Concurrency | Per-user TG tok/s | Aggregate TG tok/s | TTFT p50 | Total completion | VRAM 0/1 MiB |
|---:|---:|---|---:|---:|---:|---:|
| 32K | 1 | 26.70 | 26.70 | 105.72 s | 124.86 s | 20,926 / 20,556 |
| 32K | 2 | 4.29 / 17.38 | 8.55 | 165.40 s | 240.03 s | 21,498 / 21,118 |
| 64K | 1 | 23.20 | 23.20 | 221.72 s | 243.75 s | 21,458 / 21,332 |
| 64K | 2 | 2.10 / 14.80 | 4.19 | 345.14 s | 484.55 s | 22,574 / 22,440 |
| 128K | 1, p24/ub1024 | 17.64 | 17.64 | 352.72 s | 381.70 s | 20,396 / 21,598 |
| 128K | 2, p24/ub512 | 0.88 / 10.31 | 1.75 | 834.65 s | 1,152.29 s | 22,416 / 22,706 |

Concurrency 2 reduced aggregate output throughput by 68.0%, 81.9%, and 90.1% at 32K, 64K, and 128K respectively. It also increased TTFT and produced severe inter-client asymmetry. Concurrency 4 was not attempted because concurrency 2 was already decisive and the experiment budget explicitly called for stopping this branch.

## 6. Batch, ubatch, compute buffers, and placement

The adaptive search tested a smaller value and then a larger value only while the trend remained useful. Server startup alone was not accepted: every retained setting completed a genuine near-limit prompt.

| Context | Placement | ubatch | Prompt/output | PP tok/s | TG tok/s | TTFT | Peak VRAM 0/1 MiB | Judgment |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 32K | p20 | 512 | 31,488 / 512 warm | 301.31 | 26.70 | 105.72 s | 20,926 / 20,556 | smaller comparator |
| 32K | p20 | 1024 | 30,976 / 512 | 448.04 | 27.26 | 69.15 s | 21,072 / 20,938 | safe, faster PP |
| 32K | p20 | 2048 | 30,976 / 512 | 635.28 | 27.54 | 48.77 s | 21,370 / 21,712 | largest batch ceiling; final |
| 64K | p20 | 512 | 64,256 / 512 warm | 292.45 | 23.20 | 221.72 s | 21,458 / 21,332 | smaller comparator |
| 64K | p20 | 1024 | 63,744 / 512 | 440.81 | 23.47 | 144.62 s | 21,610 / 21,964 | safe; final |
| 128K | p20 | 512 | 129,792 / 512 warm | 272.97 | 18.30 | 478.40 s | 22,518 / 22,880 | smaller comparator |
| 128K | p20 | 1024 | 129,664 / 128 | 411.77 | 18.54 | 314.92 s | 23,154 / 24,002 | completes, but only 82 MiB nominal margin on GPU1; reject |
| 128K | p24 | 1024 | 129,280 / 512 | 366.55 | 17.64 | 352.72 s | 20,396 / 21,598 | safe final |

Relative to the warm ubatch-512 baselines, PP improved by 110.8% at 32K with ubatch 2048 and by 50.7% at 64K with ubatch 1024. The 128K p24/ubatch-1024 final improves PP 34.3% despite its more conservative placement. Decode changes were small because ubatch primarily affects prompt work.

The largest safe/useful ubatches are 2048 at 32K and 1024 at 64K and 128K. Larger 64K/128K values were not tried after buffer growth and remaining margin made the direction operationally unsafe. The dynamic limiter is compute/graph workspace, not static model loading alone. For example, 32K ubatch 2048 allocated approximately 2,234/1,488 MiB CUDA compute buffers plus 941 MiB host compute buffer. At 128K p24/ubatch 1024 the initial compute buffers were about 1,949/2,088 MiB plus 1,830 MiB host, and CUDA0 later grew to about 1,975 MiB. KV scales independently with context.

### Memory/placement table

Buffer values are from startup logs; runtime peaks are from 0.5 s GPU sampling. CPU model buffers are the two mapped shard groups printed by the loader.

| Profile | PLE placement | CPU expert bands | CPU model buffers MiB | GPU0 model MiB | GPU1 model MiB | KV per GPU MiB | Compute CUDA0/1 + host MiB | Runtime peak VRAM 0/1 MiB |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 32K final p20 | CPU/mmap, verified | 0–9, 24–33 | 41,268.78 + 12,520.21 | 18,002.75 | 19,106.88 | 384 + 144 = 528 | 2,234 / 1,488 + 941 | 21,370 / 21,712 |
| 64K final p20 | CPU/mmap, verified | 0–9, 24–33 | 41,268.78 + 12,520.21 | 18,002.75 | 19,106.88 | 768 + 288 = 1,056 | up to 1,975 / 1,240 + 925 | 21,610 / 21,964 |
| 128K rejected p20 | CPU/mmap, verified | 0–9, 24–33 | 41,268.78 + 12,520.21 | 18,002.75 | 19,106.88 | 1,536 + 576 = 2,112 | 2,461 / 2,216 + 1,830 | 23,154 / 24,002 |
| 128K final p24 | CPU/mmap, verified | 0–11, 24–35 | 43,718.14 + 14,969.57 | 15,727.75 | 16,831.88 | 1,536 + 576 = 2,112 | up to 1,975 / 2,088 + 1,830 | 20,396 / 21,598 |

The p24 refinement moved four additional expert layers to CPU. It reduced static GPU buffers by about 2,275 MiB on each GPU, retained more than 2.4 GiB practical runtime headroom on the tighter GPU, and made 128K ubatch 1024 stable. It did not improve TG: safety and PP capacity, not decode speed, are the reasons to use it.

## 7. Lazy reads and CUDA graph A/B

### `--tensor-read-lazy`

At 32K p20/ubatch-512, lazy off took 52.06 s to start and reached 53.93–55.26 GiB RSS. Its cold request had 62 major faults, PP 303.70 tok/s, TG 27.52 tok/s, and TTFT 102.01 s; its warm request had zero major faults, PP 305.22, TG 26.55, and TTFT 102.64 s. Lazy on started in approximately 29 s, used 24.03–25.68 GiB RSS, and had 11,755 cold/313 warm major faults. Lazy off saved about 9.2 s on the cold request but had no material warm throughput advantage, while costing roughly 29.6 GiB RSS and about 23 s extra startup. Final profiles retain lazy reads and require a warm-up request operationally.

Guest-visible process read bytes remained zero during timed requests in both modes; faults serviced through mmap/page cache are not necessarily counted as process `read_bytes`.

### CUDA graphs

The matched 64K p20/ubatch-1024 comparison produced:

| Graphs | PP tok/s | TG tok/s | Peak VRAM 0/1 MiB |
|---|---:|---:|---:|
| enabled | 440.81 | 23.47 | 21,610 / 21,964 |
| disabled (`GGML_CUDA_DISABLE_GRAPHS=1`) | 439.45 | 21.31 | 21,584 / 21,948 |

Graphs improved TG by 10.2%, changed PP by only 0.3%, and cost just 26/16 MiB measured peak VRAM. They should remain enabled. Current source can execute unsupported MoE/PLE operations through eager/fallback paths; the measured result shows graph capture still benefits the supported decode portion enough to justify its small memory cost.

## 8. Bottleneck diagnosis

### MEASURED

- GPUs were not compute-saturated. Across formal near-limit runs GPU0 averaged roughly 56–78% utilization while GPU1 averaged roughly 10–21%; power was typically about 124–133 W on GPU0 and 99–108 W on GPU1, far below RTX 4090 board limits. Short 100% bursts occurred, but not sustained saturation.
- One CPU thread was consistently near saturation: maximum per-thread utilization was about 94–100%. Total process CPU was only about 142–256% of the 16 exposed CPUs, so the machine did not exhaust aggregate CPU capacity.
- GPU0 was systematically busier than GPU1 even when GPU1 held the slightly larger model buffer. This is a useful-compute imbalance, not merely a capacity imbalance.
- The representative 64K profile retained raw `nvidia-smi dmon` samples. Steady decode showed continuing PCIe receive/transmit activity on both GPUs, often tens to hundreds of MiB/s, correlated with modest SM utilization.
- Major faults were large on cold lazy runs and fell to a few hundred after warm-up. With lazy reads disabled, the warm run had zero major faults.
- `/proc` process storage read deltas were zero during every timed request, including steady decode. Guest `iostat` did not show model-file reads, but the actual host backing device is hidden behind virtiofs.
- The graph A/B establishes that GPU launch/capture overhead matters: decode was 10.2% faster with graphs, for negligible extra VRAM.
- Both the p20 and p24 placements left GPU1 much less utilized than GPU0. Moving four more expert layers to CPU improved memory safety but did not correct compute utilization balance.

### INFERRED, with limits

- The runtime is **mixed serialized CPU-MoE/host-transfer/synchronization bound during decode**, not GPU-compute bound. Evidence is the saturated CPU thread, low GPU power, highly uneven GPU utilization, and per-token PCIe traffic.
- CPU-resident routed experts are the dominant host-side decode burden. Twenty or twenty-four layers perform token-dependent routed-expert work on CPU and exchange activations with GPUs. PLE performs lookup-like access to a very large table, so it contributes host memory/page-cache pressure, especially cold, but its steady per-token work is plausibly smaller than routed expert matmuls and transfers. PLE and expert traffic were not independently instrumented, so their exact shares are not measured.
- Whole-system RAM bandwidth saturation is **not demonstrated**. No privileged memory-controller counters were available (`perf_event_paranoid=4`), and only one core was saturated while most CPU capacity was idle. A serialized expert/control path and synchronization are better supported than global DRAM saturation, though host memory bandwidth is part of the mixed path.
- Persistent backing-storage access is not a steady-state decode bottleneck after warm-up. This conclusion is strong for guest-visible I/O and page-fault behavior but cannot exclude host-side virtiofs/page-cache activity invisible to the guest.
- GPU1 underutilization is systematic, but simply moving more work to it is constrained by static expert size and layer-split behavior. The failed contiguous placement demonstrates that automatic layer assignment can overflow one GPU despite aggregate capacity.

Answers to the requested profiling questions: (1) GPUs compute-saturated: no. (2) waiting on host: materially, yes. (3) one GPU substantially more loaded: yes, GPU0. (4) one CPU thread saturated: yes. (5) RAM bandwidth limiting: plausible contributor, not proven dominant. (6) persistent major faults after warm-up: nearly gone. (7) steady model storage reads: none guest-visible. (8) per-token PCIe traffic: yes. (9) PLE material versus experts: PLE is material to residency/cold faults, but routed experts are inferred to dominate steady decode traffic/work.

## 9. Speculative decoding and vLLM feasibility

### MTP

No MTP run was performed. Current source contains generic draft-MTP machinery, but the selected Qwen4Exp model implementation and this GGUF expose no Qwen3.8-Flash-Next next-token prediction head/tensors or credible architecture-specific MTP execution path. Running an arbitrary generic draft setting would not be a correctness-valid experiment. Therefore no positive net MTP result exists for this representation/runtime; MTP remains off in every deployment command.

### vLLM

The [public vLLM recipe](https://recipes.vllm.ai/Qwen/Qwen3.8-Flash-Next) was inspected only for architectural ideas: prefix caching, continuous batching, batched-token scheduling, CUDA graphs, MTP, and PLE CPU offload. Its hardware/model assumptions are not transferable: the recipe targets a large native checkpoint and much larger multi-GPU memory. Current vLLM cannot meaningfully reproduce this campaign's three-shard GGUF plus llama.cpp tensor-regex placement on two 24 GiB GPUs. A compatible native checkpoint would require a very large new download and a different placement path, so no vLLM runtime or checkpoint was installed.

## 10. Exact deployment commands

Latency and throughput commands are identical for each lane because concurrency 2 reduced both aggregate throughput and latency. These commands use port 18080 as tested; change only the port if operationally necessary.

### 32K latency

```bash
/srv/ai/llama.cpp-qwen4exp/build-cuda-sm89/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-IQ4XS/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00003.gguf --host 127.0.0.1 --port 18080 -c 32768 -np 1 -b 2048 -ub 2048 -t 16 -tb 16 -ngl all -sm layer -ts 1,1 -ot 'per_layer_token_embd\.weight=CPU,blk\.([0-9]|2[4-9]|3[0-3])\.ffn_(up|down|gate|gate_up)_(ch|)exps=CPU' --tensor-read-lazy on -fa on --cache-reuse 0 --metrics --slots --perf --no-warmup --log-verbosity 4
```

### 32K throughput

```bash
/srv/ai/llama.cpp-qwen4exp/build-cuda-sm89/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-IQ4XS/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00003.gguf --host 127.0.0.1 --port 18080 -c 32768 -np 1 -b 2048 -ub 2048 -t 16 -tb 16 -ngl all -sm layer -ts 1,1 -ot 'per_layer_token_embd\.weight=CPU,blk\.([0-9]|2[4-9]|3[0-3])\.ffn_(up|down|gate|gate_up)_(ch|)exps=CPU' --tensor-read-lazy on -fa on --cache-reuse 0 --metrics --slots --perf --no-warmup --log-verbosity 4
```

### 64K latency

```bash
/srv/ai/llama.cpp-qwen4exp/build-cuda-sm89/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-IQ4XS/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00003.gguf --host 127.0.0.1 --port 18080 -c 65536 -np 1 -b 2048 -ub 1024 -t 16 -tb 16 -ngl all -sm layer -ts 1,1 -ot 'per_layer_token_embd\.weight=CPU,blk\.([0-9]|2[4-9]|3[0-3])\.ffn_(up|down|gate|gate_up)_(ch|)exps=CPU' --tensor-read-lazy on -fa on --cache-reuse 0 --metrics --slots --perf --no-warmup --log-verbosity 4
```

### 64K throughput

```bash
/srv/ai/llama.cpp-qwen4exp/build-cuda-sm89/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-IQ4XS/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00003.gguf --host 127.0.0.1 --port 18080 -c 65536 -np 1 -b 2048 -ub 1024 -t 16 -tb 16 -ngl all -sm layer -ts 1,1 -ot 'per_layer_token_embd\.weight=CPU,blk\.([0-9]|2[4-9]|3[0-3])\.ffn_(up|down|gate|gate_up)_(ch|)exps=CPU' --tensor-read-lazy on -fa on --cache-reuse 0 --metrics --slots --perf --no-warmup --log-verbosity 4
```

### 128K latency

```bash
/srv/ai/llama.cpp-qwen4exp/build-cuda-sm89/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-IQ4XS/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00003.gguf --host 127.0.0.1 --port 18080 -c 131072 -np 1 -b 2048 -ub 1024 -t 16 -tb 16 -ngl all -sm layer -ts 1,1 -ot 'per_layer_token_embd\.weight=CPU,blk\.([0-9]|1[01]|2[4-9]|3[0-5])\.ffn_(up|down|gate|gate_up)_(ch|)exps=CPU' --tensor-read-lazy on -fa on --cache-reuse 0 --metrics --slots --perf --no-warmup --log-verbosity 4
```

### 128K throughput

```bash
/srv/ai/llama.cpp-qwen4exp/build-cuda-sm89/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-IQ4XS/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00003.gguf --host 127.0.0.1 --port 18080 -c 131072 -np 1 -b 2048 -ub 1024 -t 16 -tb 16 -ngl all -sm layer -ts 1,1 -ot 'per_layer_token_embd\.weight=CPU,blk\.([0-9]|1[01]|2[4-9]|3[0-5])\.ffn_(up|down|gate|gate_up)_(ch|)exps=CPU' --tensor-read-lazy on -fa on --cache-reuse 0 --metrics --slots --perf --no-warmup --log-verbosity 4
```

## 11. Operational guidance

- **Persistent server for related prompts:** keep a server alive to retain mapped pages and avoid cold faults, not for prefix-evaluation reuse. This runtime/model combination saved zero evaluated tokens for 29K, 60K, and 120K stable prefixes.
- **Prefix-reuse savings:** 0 tokens and 0 measured prompt work at all three contexts. Apparent warm TTFT improvements were only 7.5%, 4.8%, and 2.4% and occurred despite full reprocessing.
- **Application concurrency:** use one in-flight generation per server. Queue independent requests sequentially. Two requests did not improve aggregate throughput at any lane, including 128K.
- **Slot sizing:** allocate exactly 32,768, 65,536, or 131,072 total context to a one-slot server. If future code changes make two-slot tests worthwhile, allocate 2× the per-session context; do not divide one lane's context between users.
- **Latency/throughput crossover:** concurrency already loses decisively at two requests, so there is no useful crossover on this runtime/hardware.
- **Warm-up:** important with lazy tensor reads. Issue an operational near-representative warm-up before accepting latency-sensitive traffic; tiny startup probes do not fault in the expert/PLE working set.
- **Resource classification:** mixed serialized CPU-resident MoE, host-GPU transfer, and synchronization bound during decode; prompt processing benefits strongly from GPU workspace/ubatch. It is not primarily GPU-compute bound, and global RAM-bandwidth saturation was not proven.
- **128K safety:** do not use p20/ubatch 1024 operationally even though it completed once; its tighter GPU had only about 82 MiB nominal free. Use p24.

## 12. Direct answers to the scientific questions

1. Reused 32K/64K/128K prefixes reduced evaluated work by **0 tokens** and provided no attributable TTFT reduction.
2. Cache behavior was correctness-safe: it refused invalid/incomplete reuse and outputs remained distinct, but it was not performance-useful for the hybrid architecture.
3. Two-request concurrency was not faster than sequential execution in aggregate.
4. Aggregate TG at c1/c2 was 26.70/8.55 (32K), 23.20/4.19 (64K), and 17.64/1.75 tok/s (128K).
5. Concurrency was least useful at 128K; it lost about 90.1% aggregate throughput and greatly worsened fairness/TTFT.
6. Largest safe/useful ubatch: 2048 at 32K, 1024 at 64K, 1024 with p24 at 128K.
7. Larger ubatch materially improved PP: approximately +110.8%, +50.7%, and +34.3% for the final profiles versus warm ubatch-512 baselines.
8. Dynamic VRAM was primarily CUDA compute/graph workspace; context-dependent KV was the other large dynamic allocation.
9. Yes. GPU1 was systematically underutilized relative to GPU0.
10. CPU-resident routed experts are the best-supported dominant decode bottleneck, combined with transfers and synchronization.
11. PLE is meaningful for residency and cold page faults, but was not separably measured and is inferred smaller than routed-expert work in steady decode.
12. No guest-visible model storage reads continued in steady decode.
13. Major faults were nearly gone after warm-up (hundreds versus tens of thousands cold); lazy-off warm measured zero.
14. Yes. CUDA graphs improved TG 10.2% for only 26/16 MiB extra measured peak VRAM.
15. No placement improved both PP and TG. p24 made 128K safe and allowed higher-PP ubatch, at a small TG cost.
16. No valid MTP result exists: current Qwen4Exp GGUF/source lacks a credible compatible MTP head/path, so it was correctly not run.
17. For many related requests: one persistent, warmed server, one in-flight request, sequential queueing, context-specific final profile; do not expect prefix reuse.
18. For one interactive request: the same one-slot final profile, CUDA graphs on, maximum safe ubatch, and a warmed page cache.

## 13. Reproduction and artifact integrity

Run `python3 harness.py --help` from this directory for harness options. Each config JSON contains the exact argument vector and placement expression used. Scientific failures are retained rather than erased. Raw responses and server logs are not reconstructed from summaries.

At report completion, the final cleanup check found no `llama-server`, harness, `pidstat`, `nvidia-smi dmon`, `vmstat`, or `iostat` benchmark process. Both GPUs reported no compute process and returned to zero MiB process allocation.
