# Qwen3.8-Flash-Next Phase 3 — dual-24GB UD-IQ4_XS

Run root: `/srv/ai/benchmarks/qwen38-flash-next-phase3-iq4xs-20260830-080504`

Status: **COMPLETE**

## A. Executive result

**PERFORMANCE WIN / QUALITY LOSS**

UD-IQ4_XS with CPU-mapped PLE and dual-band routed-expert offload is deployable at all three required contexts on this 2×RTX 4090 machine. It completed genuine prompts of 31,803, 64,403, and 122,910 tokens and generated 512 tokens in every formal run.

It does **not** replace the Phase-2 Q6_K_XL/cafe recommendation:

- At 32K, IQ4_XS is useful: PP is 20.77% faster and TG is 22.72% faster than Q6/cafe, while host RSS is about 61.35 GiB lower.
- At 64K, IQ4_XS is 15.79% slower in PP and 3.33% slower in TG.
- At 122,910 tokens, IQ4_XS is 54.87% slower in PP and 23.42% slower in TG than the nearly identical 122,897-token Q6 result.
- UD-IQ4_XS is materially less faithful numerically than Q6_K_XL. The small deterministic gate found no retrieval collapse, but it is not evidence of fidelity parity.

Decision: retain **Q6_K_XL/cafe as the general and long-context deployment**. Use IQ4_XS only as an optional memory-saving 32K profile when its approximately 23% TG gain is worth the quantization loss. For 64K and 128K, IQ4_XS offers neither a fidelity nor a speed advantage over the established Q6 setup.

The AWQ-W4A16 checkpoint is a quantitative **NO-GO** for a supported, performant TP=2 deployment on two 24 GB GPUs in its current runtime ecosystem. It was not downloaded.

## Scope and provenance

Measured in Phase 3:

- Primary representation: `unsloth/Qwen3.8-Flash-Next-GGUF`, `UD-IQ4_XS`.
- Formal lanes only: 32K, 64K, and 128K.
- MTP off; no new source evidence specific to this model invalidated the prior negative result.
- Text inference only; no mmproj.
- One restricted F16-versus-Q8 KV feasibility check at 128K.
- AWQ metadata and source audit only.

Reused, not remeasured:

- Phase-2 Q6_K_XL/cafe baselines.
- Phase-1 and Phase-2 correctness history.

## Machine audit — measured in Phase 3

- GPUs: 2 × NVIDIA RTX 4090, 24,564 MiB each.
- Driver: 595.84; reported CUDA runtime 13.2.
- CUDA toolkit: 13.3 (`nvcc` 13.3.73).
- GPU interconnect: PHB, no NVLink; maximum Gen4 x16 per GPU. The idle audit showed Gen1 x8, which is normal power-state behavior and not a measured loaded-link result.
- CPU: AMD Ryzen 9 7950X3D; VM exposes 16 single-threaded logical CPUs.
- NUMA: one exposed node.
- RAM: 156 GiB total, about 153 GiB available at audit; no swap.
- `/srv/ai`: 1.9 TiB total, 1.1 TiB free at audit.
- `/srv/ai` filesystem: `virtiofs`; the physical backing device is hidden from the VM.
- GPU users before runs: none; 1 MiB allocated per GPU.

## Source and correctness audit

The benchmark runtime is:

`/srv/ai/benchmarks/qwen38-flash-next-phase3-iq4xs-20260830-080504/builds/current-corrected-e1f3c2d1/bin/llama-server`

Exact commit: `e1f3c2d1ff745c1f24d5954e64f55583818949bd`.

It is upstream `bebc9350ecc42a31ad119da1513998386671cf5b` plus the retained correctness series:

- `b21faef26`: sparse-attention block selection.
- `7bca92cfe`: independent PLE embedding widths.
- `e47a771e3`: metadata validation.
- `88be2426b`: update indexer cache after sequence copies.
- `9fbc7cebb`: recurrent rollback.
- `bd6d5d9f1`: disable unsupported tensor split.
- `e25186a75`: GDN Q/K normalization.
- `e1f3c2d1f`: avoid the CUDA RMSNorm grid limit.

The exact community b10674 source, commit `866322481`, was built and used only for the EXP-006 startup diagnostic. It accepted the original `ub=2048` graph, but it was not used for formal results because the retained correctness patches are the stronger correctness basis.

Source revisions audited:

- `ruashots/flashnext-2x3090`: `57ced68c0366c42828b467710140a8116bd29cda`.
- current upstream llama.cpp snapshot: `bebc9350ecc42a31ad119da1513998386671cf5b`.
- AWQ metadata repository: `0939125b929543a783ce700c90e36dd1a575c00c`.
- `wtdcode/vllm-backport`: `13acfebd73e062b3c9004f1adee6fd568de2968f`.

The corrected runtime cannot use the community recipe's `ub=2048` within 24 GB: its corrected graph allocation is much larger. Formal runs therefore used `ub=64` at 32K/64K and `ub=32` at 128K. This is a runtime/correctness tradeoff, not an unexplained change to the reference recipe.

## Model identity

Repository revision: `c8b5954a88c2775c546b92593eda40ea041d3176`.

First shard:

`/srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-IQ4XS/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00003.gguf`

Aggregate size: 93,682,584,224 bytes = 93.68 GB decimal = 87.25 GiB.

SHA-256:

- shard 1: `5ce89370720f8bf90890f439361282104c1aa1482d4013bb9a50923e758e71a4`
- shard 2: `577a38a2392b40ca2193cea502e1d92f60b8cd370675d308e0ec21885d9daaa7`
- shard 3: `d4634e6d84f0ebb0940be15c90d3790bf6464e3dea3a1cddc567dc0e83ad8833`

## Placement verification

Repeated `-ot` behavior was not assumed. A single combined expression was used, and verbose startup logs prove that both components applied:

1. `per_layer_token_embd.weight` was CPU-mapped/lazy-read; its logged size was about 27,465 MiB.
2. Routed expert tensors in both non-contiguous bands were assigned to host memory.

At 32K, the selected bands were layers 0–11 and 25–34. The logged model buffers were 43,718.14 + 12,520.21 MiB CPU-mapped, 16,865.25 MiB CUDA0, and 17,969.38 MiB CUDA1. F16 KV was 384 MiB per GPU plus a 144 MiB indexer per GPU. Compute buffers were 2,946.69 MiB on CUDA0 and 2,223.00 MiB on CUDA1.

At 128K, the bands were widened by one layer at each inner edge to 0–12 and 25–35. Logged model buffers were 44,924.92 + 13,748.87 MiB CPU-mapped, 15,727.75 MiB CUDA0, and 16,831.88 MiB CUDA1. F16 KV was 1,536 MiB per GPU plus a 576 MiB indexer per GPU. Compute buffers were 5,028.34 MiB on CUDA0 and 4,348.00 MiB on CUDA1.

The log phrase `offloaded 49/49 layers` describes layer offload, not the final placement of every overridden tensor. The CPU-mapped buffer totals and individual override entries are the direct proof that PLE and the specified expert tensors remained on host.

## Benchmark method

- Each formal server was configured for its declared lane and received a unique nonce, preventing prefix-cache reuse.
- Each formal measurement followed two 512-token warm-up generations, matching the community method and warming CPU expert/PLE pages.
- Each measured request generated 512 tokens with EOS suppression so TG timing was stable.
- `cache_n=0` was recorded for formal requests.
- Formal PP/TG values are therefore **warm steady-state** results.
- Cold behavior was retained separately: server readiness was 28.046 s at 32K, 29.048 s at 64K, and 28.045 s at 128K. No separate cold full-prompt throughput run was performed, so none is invented here.
- The TTFT column uses the server's prompt-evaluation duration as a reproducible proxy. Client-side first-byte timing was not separately captured.
- GPU telemetry averages cover the whole server lifecycle—load, both warm-ups, and the formal request—not only token kernels.
- PCIe byte counters were unavailable. Disk telemetry is guest-visible `virtiofs` activity, not a direct physical-device measurement.

## B. Final profile table

| Context | Actual prompt tokens | Placement | KV | PP tok/s | TG tok/s | TTFT | VRAM 0/1 | RSS | Result |
|---|---:|---|---|---:|---:|---:|---:|---:|---|
| 32K | 31,803 | PLE CPU; experts 0–11, 25–34 CPU | F16 | 77.48 | 16.78 | 410.47 s proxy | 20,942 / 21,300 MiB | 46.01 GiB | PASS; 512 tokens |
| 64K | 64,403 | PLE CPU; experts 0–11, 25–34 CPU | F16 | 54.29 | 12.08 | 1,186.34 s proxy | 23,558 / 24,038 MiB | 46.01 GiB | PASS; 512 tokens |
| 128K | 122,910 | PLE CPU; experts 0–12, 25–35 CPU | F16 | 29.05 | 7.87 | 4,231.38 s proxy | 23,462 / 23,864 MiB | 44.90 GiB | PASS; 512 tokens |

Total response wall times were 441.07 s, 1,228.81 s, and 4,296.59 s respectively. Mean GPU utilization for GPU0/GPU1 was 55.86%/17.30% at 32K, 52.74%/21.49% at 64K, and 50.96%/22.36% at 128K; both GPUs reached a sampled peak of 100% in every lane. Mean power for GPU0/GPU1 was 116.74/102.20 W, 122.17/112.16 W, and 121.67/113.62 W; sampled peak power was 138.50/127.46 W, 154.87/148.46 W, and 149.20/146.41 W respectively. The asymmetry is consistent with layer split and host-offloaded MoE work. Peak observed major faults were 90,087, 86,076, and 88,370; these lifecycle-wide values reinforce why the formal rates must be described as post-warm-up.

## C. Comparison with Phase-2 Q6/cafe

Phase-2 Q6 was not rerun. Exact persisted values were used.

| Lane | IQ4 / Q6 prompt tokens | IQ4 PP vs Q6 | IQ4 TG vs Q6 | Host RSS difference | Interpretation |
|---|---:|---:|---:|---:|---|
| 32K | 31,803 / 32,785 | 77.48 / 64.15 = **1.208×** | 16.78 / 13.67 = **1.227×** | about **−61.35 GiB** | IQ4 performance win; prompt occupancy is ~3.0% lower |
| 64K | 64,403 / 65,553 | 54.29 / 64.47 = **0.842×** | 12.08 / 12.50 = **0.967×** | about **−61.35 GiB** | Near TG parity but IQ4 loses; occupancy is ~1.8% lower |
| Long | 122,910 / 122,897 | 29.05 / 64.37 = **0.451×** | 7.87 / 10.27 = **0.766×** | about **−62.47 GiB** | Strictly comparable occupancy; Q6 clearly wins |

Phase-2 Q6 model size was 169,165,382,688 bytes (157.55 GiB), so IQ4_XS saves about 70.30 GiB on disk. Q6 host HWM was about 107.36–107.37 GiB versus 44.90–46.01 GiB here. This is not a same-placement GPU-memory comparison: host-heavy cafe Q6 used approximately 6,042/6,364 MiB peak GPU memory, while the IQ4 placement intentionally filled 20.9–24.0 GiB per GPU. Phase 3 also generated 512 measured tokens versus 128 in the persisted Q6 tests, improving TG stability but making the harnesses not perfectly identical.

The representation caveat dominates deployment selection: Q6_K_XL has higher numerical fidelity than UD-IQ4_XS. A 32K speed gain is a selectable tradeoff, not proof that IQ4 is the better model.

## Correctness and quality gate

- Sparse-attention correctness is based on the retained sparse-attention patch, the absence of fallback/error reports, and successful genuine occupancy at all three lanes. No dedicated kernel counter was available, so this does not prove kernel-level parity independently.
- Deterministic retrieval succeeded near the beginning, middle, and end of every formal context:
  - 32K: `CITRUS-32K-17`, `COBALT-32K-29`, `JASPER-32K-43`.
  - 64K: `CITRUS-64K-17`, `COBALT-64K-29`, `JASPER-64K-43`.
  - 128K: `CITRUS-128K-17`, `COBALT-128K-29`, `JASPER-128K-43`.
- No server OOM, truncation, recurrent-state crash, or cross-request contamination occurred in the passing formal runs.
- Forced 512-token generation with EOS disabled caused the model to repeat the requested JSON after it had answered. At 128K the first object also contained a minor extra quote/bracket before subsequent clean repetitions. The retrieval values remained correct. This fails strict single-object formatting under an artificial non-termination condition, but it is not sufficient evidence of long-context corruption.
- The gate is deliberately small. It rejects an obvious collapse; it cannot establish quality equality with Q6. Fidelity ranking remains Q6_K_XL > UD-IQ4_XS.

## KV result

F16 KV is the only recommended KV configuration. Q8_0 KV did free memory, but both allowed 128K attempts (`ub=64` and `ub=32`) terminated with a scheduler/assertion failure and exit code -6 before a valid formal request. F16 with `ub=32` and the refined dual bands completed 122,910 tokens. Therefore Q8 KV has no demonstrated deployment advantage in this corrected runtime.

## Diagnostic failures retained

- EXP-001 through EXP-003: older retained runtime, reference placement, structural graph OOM at progressively smaller ubatches.
- EXP-004: older runtime startup-only pass at `ub=32`.
- EXP-005: current corrected runtime with reference `ub=2048`, structural OOM. The generic harness labeled the load failure `REJECTED-INCORRECT`; manual log classification is `REJECTED-OOM`.
- EXP-006: exact community b10674 startup-only diagnostic passed at `ub=2048`; not a formal/correctness winner.
- EXP-007: corrected runtime, widened bands, startup-only pass at `ub=64`.
- EXP-010: 128K F16, `ub=64`, bands 0–11/25–34, OOM.
- EXP-011 and EXP-012: 128K Q8 KV, scheduler/assertion exit -6 at `ub=64` and `ub=32`.
- EXP-013: 128K F16, `ub=32`, bands 0–11/25–34, OOM.
- EXP-014: refined bands 0–12/25–35 passed and became the 128K result.

Manual corrections to generic harness classifications are persisted in `results/diagnostic-reclassification.json`; no failed attempt was removed.

## D. Exact IQ4_XS deployment commands

These are the measured optional IQ4 profiles. `LLAMA_ATTN_ROT_DISABLE=1` is part of the retained corrected-runtime configuration.

### 32K

```bash
LLAMA_ATTN_ROT_DISABLE=1 \
/srv/ai/benchmarks/qwen38-flash-next-phase3-iq4xs-20260830-080504/builds/current-corrected-e1f3c2d1/bin/llama-server \
  -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-IQ4XS/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00003.gguf \
  -c 32768 -np 1 -dev CUDA0,CUDA1 -sm layer -ngl 99 -fit off \
  -fa on -ctk f16 -ctv f16 -b 2048 -ub 64 -lzm on \
  -ot '(^per_layer_token_embd\.weight$|blk\.([0-9]|1[01]|2[5-9]|3[0-4])\.ffn_(up|down|gate|gate_up)_(ch|)exps)=CPU' \
  -lv 4 --metrics --host 127.0.0.1 --port 18080
```

### 64K

```bash
LLAMA_ATTN_ROT_DISABLE=1 \
/srv/ai/benchmarks/qwen38-flash-next-phase3-iq4xs-20260830-080504/builds/current-corrected-e1f3c2d1/bin/llama-server \
  -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-IQ4XS/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00003.gguf \
  -c 65536 -np 1 -dev CUDA0,CUDA1 -sm layer -ngl 99 -fit off \
  -fa on -ctk f16 -ctv f16 -b 2048 -ub 64 -lzm on \
  -ot '(^per_layer_token_embd\.weight$|blk\.([0-9]|1[01]|2[5-9]|3[0-4])\.ffn_(up|down|gate|gate_up)_(ch|)exps)=CPU' \
  -lv 4 --metrics --host 127.0.0.1 --port 18080
```

### 128K

```bash
LLAMA_ATTN_ROT_DISABLE=1 \
/srv/ai/benchmarks/qwen38-flash-next-phase3-iq4xs-20260830-080504/builds/current-corrected-e1f3c2d1/bin/llama-server \
  -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-IQ4XS/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00003.gguf \
  -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer -ngl 99 -fit off \
  -fa on -ctk f16 -ctv f16 -b 2048 -ub 32 -lzm on \
  -ot '(^per_layer_token_embd\.weight$|blk\.([0-9]|1[0-2]|2[5-9]|3[0-5])\.ffn_(up|down|gate|gate_up)_(ch|)exps)=CPU' \
  -lv 4 --metrics --host 127.0.0.1 --port 18080
```

These are exact reproducible IQ4 commands, not the overall primary recommendation. The Phase-2 Q6/cafe deployment remains preferred at 64K/128K and for fidelity-first use.

## E. AWQ-W4A16 feasibility verdict

**Not feasible as a supported, performant deployment on exactly two 24 GB GPUs; downloading is not justified.**

Metadata-only parsing found:

- Index total including the separate MTP artifact: 180,725,866,024 bytes.
- Five main weight shards: 175,480,345,080 payload bytes = 163.43 GiB.
- PLE: 128 tensors, 102,400,491,520 bytes = 95.37 GiB.
- Routed experts: 62,286,594,048 bytes = 58.01 GiB.
- Total non-PLE main weights: 73,079,853,560 bytes = 68.06 GiB.

Even granting the model-specific `VLLM_PLE_CPU_OFFLOAD=1`, TP=2 has a hard lower bound of **34.03 GiB of non-PLE weights per rank**. Each GPU physically provides 24,564 MiB = 23.99 GiB, a deficit of **10.04 GiB per rank before KV cache, CUDA graphs, activations, and safety margin**. Thus 32K already fails the straightforward placement bound; 64K and 128K only worsen it.

The model card's documented path uses `--tp 4 --enable-expert-parallel` on 4×A100 80GB. AWQ INT4 symmetric group-size 128 is applied to routed experts, while PLE, attention, recurrent/linear-attention, hyperconnection, vision, and shared-expert components are excluded and remain BF16. The audited fork exposes generic UVA CPU offload, but no model/source evidence establishes a performant, supported mechanism for offloading the additional >10.04 GiB per rank plus runtime headroom on a two-rank 24GB setup. “Can be addressed through UVA” is not equivalent to a viable dual-4090 execution path.

Conclusion: current AWQ-W4A16 is effectively a >=4-GPU checkpoint in its documented runtime ecosystem. Full shards were not downloaded. The calculation is persisted in `results/awq-feasibility.json`.

## F. Evidence index

- Machine audit: `results/machine-audit.md`.
- Append-only experiment records: `results/experiments.jsonl`.
- Derived lifecycle telemetry summary: `results/telemetry-summary.json`; raw samples remain under `logs/`.
- AWQ calculation: `results/awq-feasibility.json`.
- Manual failure classification: `results/diagnostic-reclassification.json`.
- Exact server output: `logs/EXP-008-server-stdout.log`, `logs/EXP-009-server-stdout.log`, `logs/EXP-014-server-stdout.log` and matching stderr files.
- Responses and retrieval evidence: `logs/EXP-008-responses.json`, `logs/EXP-009-responses.json`, `logs/EXP-014-responses.json`.
- GPU telemetry: `logs/EXP-008-gpu-telemetry.jsonl`, `logs/EXP-009-gpu-telemetry.jsonl`, `logs/EXP-014-gpu-telemetry.jsonl`.
- All failed EXP-001–EXP-013 logs remain in `logs/`; none were overwritten or deleted.
- Prior baseline: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/REPORT.md`.

## Final answer

UD-IQ4_XS plus CPU PLE and dual-band MoE placement is technically successful on 2×24 GB at 32K, 64K, and genuine near-limit 128K. Its only compelling deployment point is 32K, where it gives about 22.7% more decode throughput and saves about 61 GiB host RSS relative to Q6/cafe. It does not justify its fidelity reduction at 64K or 128K: by ~123K it is 23.4% slower in TG and 54.9% slower in PP than higher-fidelity Q6.

Therefore: deploy Q6_K_XL/cafe for the general fidelity-first service; offer the measured IQ4_XS 32K command as an explicit performance/memory option. Do not download AWQ-W4A16 for this two-GPU machine.
