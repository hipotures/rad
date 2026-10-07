# Qwen3.8-Flash-Next — Phase 2 live report

- Run root: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320`
- Started: `2026-08-29T21:13:20Z`
- Status: **COMPLETE**
- Scope: high-fidelity Q8/Q6, mandatory `-c 131072 -np 1`; no BF16 or low-qubit sweep.

## REUSED FROM PHASE 1

Source: `/srv/ai/benchmarks/qwen38-flash-next-20260829-105917/REPORT.md`

| Configuration | Target | Runtime | Placement | KV | MTP | 8K pp/tg | 32K pp/tg | 64K pp/tg | ~123K pp/tg | VRAM 0/1 | Host RSS | Status |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| Phase-1 Q8 baseline | Q8_0 | llama.cpp `d0e6d1a` | fit/layer | F16 | off | 42.42 / 10.63 | 40.97 / 8.76 | 32.83 / 6.94 | 23.53 / 5.03 | 23146 / 23072 MiB | 127.17 GiB | REUSED FROM PHASE 1 |

BF16 was rejected in Phase 1 because ~329.7 GiB of weights exceed the practical combined memory budget before KV/runtime buffers. Q4 remains only a reused speed reference.

## MEASURED IN PHASE 2

### Q8 automatic-fit placement diagnostic

`llama-fit-params` from the corrected current-upstream build was run with the Phase-1 Q8 deployment arguments and mandatory `-c 131072 -np 1`. This was a placement/memory diagnostic, not a throughput result (`DIAGNOSTIC-ONLY`). Full log: `logs/q8-current-fit-params.log`.

- Q8 GGUF: 175.29 GiB, 176.94B parameters, 8.51 bpw; architecture has 48 blocks, 512 routed experts and 10 active experts.
- F16 cache allocation reported 3072 MiB ordinary KV, 1152 MiB indexer KV and 112.57 MiB recurrent state.
- Automatic fit selected `-ngl 45 -ts 30,15` plus CPU overrides for routed-expert tensors in blocks 4–33 and 35–48.
- Consequently the first four repeating blocks remain fully on CPU, routed experts in 43 additional blocks are explicitly kept on CPU, and only one block's routed-expert weights remain GPU-resident. The rest of the latency-sensitive non-expert tensors are largely GPU-offloaded.
- Estimated fitted allocation was 22535 MiB on CUDA0 and 22549 MiB on CUDA1, leaving roughly 1.1 GiB per GPU.

This directly justifies the Phase-2 manual-placement experiment: preserve dense/GDN/attention/router tensors on GPU, host-offload routed experts explicitly, and use freed KV/cache capacity to retain more expert weights where useful.

## Research and source revisions

### Current source audit — 2026-08-29 (MEASURED/VERIFIED IN PHASE 2)

| Source | Current revision checked | Finding |
|---|---|---|
| `ggml-org/llama.cpp` | `c841aeeb8bb2fe417038dadfa9b007cf1a9ef950` | Current upstream HEAD; Phase-2 builds must preserve the Phase-1 Qwen4Exp correctness fixes that are not yet equivalent upstream. |
| `unslothai/llama.cpp` | `062406552f1ae026722e6dee27334a4bbb51f3c9` | Current fork HEAD checked. |
| `quimmedes/cafe-llama.cpp` | `f4dac26e6ef38e279fa0c4f81b9a54643d71cf3f` | Current HEAD; exposes pinned-host MoE (`-hmoe`/`-nhmoe`), CPU MoE, n-gram/PLE and lazy tensor-read controls. |
| `ikawrakow/ik_llama.cpp` | `15dddc60b3fc937a9e2a210359ecce392ccdf446` | Current HEAD is the Qwen3.8-Flash-Next CUDA TG optimization commit (`Qwen3.8-Flash-Next: faster TG on CUDA`). |
| `unsloth/Qwen3.8-Flash-Next-GGUF` | `c8b5954a88c2775c546b92593eda40ea041d3176` | Still the current verified model revision; Q6_K_XL is present as six shards. |

Relevant current upstream work was inspected rather than inferred from PR numbers:

- PR `#27861`, expert LRU cache: still open/draft at head `bccbacdb8945680f1cfc7e6bffd1e59014705750`; exposes `--moe-expert-cache` and insertion throttling. It is promising but must be rebased/combined with correctness fixes before a valid A/B.
- PR `#27978`, CUDA fast `mm_ids_helper` path for 10 active experts: open and mergeable at head `af8ae552a8914a4c84f6931c9eb8debcbf207615`; expected to affect prefill, not decode.
- PR `#27836`, native Qwen4Exp MTP: open/draft at head `1d8de7c1b0c7d2febf8f983174d8e6a711e2b1af`; current discussion reports the corrected combiner materially improving acceptance, but detached-sidecar loading and correctness integration must be verified locally.
- PR `#27956`, combined MTP/correctness branch: closed unmerged at `994905...`; rejected as the Phase-2 base.
- PR `#27941`, follow-up Qwen4Exp correctness: open/draft at `132832dc3a18674f2ffec37097efd4e78d3fb12e`; includes sequence-copy indexer, recurrent/KV state, M-RoPE, metadata, and very-long-context CUDA fixes.

Two additional source-level decisions were resolved before spending benchmark time:

- **Tensor split remains unsupported for this model.** Current issue `#27964` reproduces a CUDA abort (`SPLIT_AXIS_UNKNOWN`) for Qwen3.8-Flash-Next tensor splitting even after Phase 1. There is no credible newly merged fix, while the known-correct Phase-1 patch stack explicitly disables the unsafe path. Phase 2 therefore retains layer split and does not repeat the already-failing tensor-parallel experiment.
- **PLE can now be treated independently through lazy reads.** Current upstream exposes `--tensor-read-lazy on|auto|off`; `auto` reads eligible tensors larger than 4 GiB (notably the huge `per_layer_token_embd` table) on demand from the mmap rather than keeping all rows resident. The Q8 placement log confirms the PLE tensor is eligible. A controlled `auto` versus `off` test is justified after the primary placement screen; SSD-backed PLE is not assumed beneficial because host RAM is ample.

The known-correct Phase-1 runtime is not plain upstream. Its `d0e6d1a` branch contains eight local fixes after upstream base `cc83d7b`: sparse-attention block selection, independent PLE embedding widths, metadata validation, indexer state after sequence copies, recurrent rollback, tensor-split disablement, GDN QK normalization, and the CUDA RMSNorm grid-limit fix. New builds will be compared against these fixes explicitly; a newer date alone is not accepted as correctness evidence.

The current upstream source was rebased by applying those same eight Phase-1 patches cleanly on top of `c841aeeb`; the resulting Phase-2 corrected commit is `eb4a485cd5346f9a5666700acc4bb01bdbbf34f1`. Its CUDA SM89 Release build completed successfully at `builds/upstream-corrected` with CUDA, Flash Attention all-quants, CUDA graphs, and peer max batch 128 enabled. This is the first Phase-2 runtime candidate, not yet a measured winner.

Two focused experimental builds also completed successfully with the same CUDA SM89 Release options:

- CUDA 10-active-expert fast path (`#27978`) cherry-picked on the corrected base: commit `72f9a97`, binary `builds/pr27978/bin/llama-server`. This branch is reserved for controlled prefill A/B tests.
- GPU expert LRU cache (`#27861`) cherry-picked on the corrected base: commit `7c4ba38fe93aceeca2383d0667102fe338d54f51`, binary `builds/lru/bin/llama-server`. This branch exposes the cache controls while retaining the eight correctness patches.

### Manual-placement memory design (DIAGNOSTIC-ONLY)

Current `llama-fit-params` was used to evaluate explicit placements before starting expensive servers:

- With all non-expert layers requested on GPU and all routed experts on CPU (`-ngl all -cmoe -ts 1,1`), estimated Q8 allocation is `21792 / 21459 MiB` with F16 KV, or `20803 / 20472 MiB` with Q8_0 KV. This keeps the dense/GDN/attention/router core on GPU and leaves substantially more safety margin than automatic fit.
- A full Q8 routed-expert block is about `2550 MiB` (three ~850 MiB expert tensors), so the first-N `-ncmoe` control cannot balance the final two expert blocks: both land on CUDA1 and exceed 24 GiB.
- Explicitly keeping one routed-expert block on each GPU with Q8 KV is estimated at `23268 / 23108 MiB` using `-ts 23,25`. This is potentially faster but leaves only about 0.4–0.6 GiB of nominal margin, so it will be attempted only after the safer all-experts-host placement proves stable.

These are allocation estimates, not throughput measurements and not deployment verdicts.

### Storage audit and Q6 acquisition

- Before download: `/srv/ai` had about `1.3 TiB` available (`1.9 TiB` total, `527 GiB` used).
- Q6_K_XL remote payload: `169,165,382,688` bytes (`157.55 GiB`) in six shards.
- Destination: `/srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q6/UD-Q6_K_XL/`.
- Download completed: all six shards are present and total `169,165,382,688` bytes (`157.55 GiB`). The first transfer retained all completed data but stopped on the remaining 54.4 GB shard because the system Hugging Face client lacked Xet support. `hf_xet 1.6.0` was installed under this Phase-2 run root (not under `/home` or `/tmp`) and the download was resumed from the retained partial data. No existing model was overwritten.
- Full SHA-256 verification completed successfully; the model is admitted to the benchmark matrix:
  - shard 1: `8bdc6bad55b6699f46f60708829932ff4018d7ac9bd309c388534fa31753bdb7`
  - shard 2: `494ca4ed3dbf97bc28da88af3890b8877b9032f909812d00c0526a9ca5e91d2e`
  - shard 3: `34efd79a80a1ce540a517a5d56171924b66ce1c38b04c904f17ad6d8ef17cf20`
  - shard 4: `0ea4b599880a5a52fcd9c188ba1443f646c69c96571904ddbd6a79246a01a997`
  - shard 5: `9948e81ae8368144b135a7403d8c0f2cf9a6c2f9f692313865855b2832e696c9`
  - shard 6: `e4ae255234f42b18012f6d6eec5bf615b57479b7e0a0233c47436a321ffeec3f`

### Phase-2 builds prepared

- Corrected current upstream: `c841aeeb8bb2fe417038dadfa9b007cf1a9ef950` plus the eight Phase-1 correctness patches, resulting commit `eb4a485cd5346f9a5666700acc4bb01bdbbf34f1`; binary under `builds/upstream-corrected/`.
- CUDA 10-active-expert candidate: PR #27978 head applied to the corrected base, resulting commit `72f9a97`; binary under `builds/pr27978/`.
- GPU expert LRU candidate: PR #27861 head applied to the corrected base, resulting commit `7c4ba38fe93aceeca2383d0667102fe338d54f51`; binary under `builds/lru/`.
- Native MTP candidate: PR #27836 native Qwen4Exp MTP commits applied to the corrected current base, resulting commit `9bf4c03e37e3b835f336bdd23fc7562efbb9dcb8`; binary under `builds/mtp/`. PR #27941 was not force-merged because it is based on an older QSA graph and conflicts broadly with newer upstream and the retained Phase-1 correctness fixes.
- Cafe runtime: current `quimmedes/cafe-llama.cpp` commit `f4dac26e6ef38e279fa0c4f81b9a54643d71cf3f`; binary under `builds/cafe/`.
- ik_llama runtime: current commit `15dddc60b3fc937a9e2a210359ecce392ccdf446` (the current `Qwen3.8-Flash-Next: faster TG on CUDA` head); CUDA SM89 Release build completed successfully under `builds/ik/`.
- All CUDA builds target SM89 in Release mode. Cafe configuration confirms NCCL is not installed; because current Flash-Next tensor split remains unsupported, no NCCL installation is justified.

### Harness

The Phase-1 server and microbenchmark harnesses and identical prompt sets were copied into this run root and retargeted to the Phase-2 JSONL/log/report paths. Phase-1 scripts and results remain untouched.

## Experiment log

Phase 2 executed 15 persisted experiments. All deployment-class throughput runs used `-c 131072 -np 1`; only actual prompt occupancy varied according to the required funnel. EXP-001–002 established the same-runtime Q8/Q6 control, EXP-003–009 tested placement, KV, expert cache, the 10-expert CUDA path and cafe, EXP-010–013 tested ik_llama and MTP, and EXP-014–015 validated the winning Q6 configuration at 32K, 64K and 122,897 actual prompt tokens. Raw commands, response timings, hashes, telemetry and errors are retained below and in `results/experiments.jsonl`.

Manual verdict corrections take precedence over the harness's initial automatic label: EXP-006 is `REJECTED-SLOW`, EXP-009 is `REJECTED-SLOW`, EXP-011 is `REJECTED-OOM`, EXP-013 is `REJECTED-SLOW`, and EXP-015 is `WINNER`. No Phase-1 number is represented as newly measured.

## Final leaderboard

| Configuration | Target | Runtime | Placement | KV | MTP | 8K tg | 32K tg | 64K tg | ~120K tg | ~120K pp | VRAM 0/1 | Host RAM | Verdict |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Phase-1 Q8 baseline | Q8_0 | corrected llama.cpp `d0e6d1a` | fit/layer | F16 | off | 10.63 | 8.76 | 6.94 | 5.03 | 23.53 | 23146 / 23072 MiB | 127.17 GiB | REUSED BASELINE |
| Phase-2 Q8 control | Q8_0 | corrected llama.cpp `eb4a485` | fit/layer | F16 | off | 10.91 | 8.89 | n/a | n/a | n/a | 23142 / 23068 MiB | 126.31 GiB | CONTROL ONLY |
| Q6 automatic fit | Q6_K_XL | corrected llama.cpp `eb4a485` | fit/layer | F16 | off | 12.24 | 9.63 | n/a | n/a | n/a | 22988 / 22870 MiB | 108.57 GiB | PROMISING |
| Q6 manual MoE | Q6_K_XL | corrected llama.cpp `eb4a485` | `-ncmoe 47 -ts 27,21` | Q8_0 | off | 15.12 | n/a | n/a | n/a | n/a | 21848 / 22744 MiB | 107.14 GiB | PROMISING |
| Q6 expert LRU-16 | Q6_K_XL | llama.cpp `7c4ba38` | all routed experts host | Q8_0 | off | 9.75 | n/a | n/a | n/a | n/a | 23204 / 22690 MiB | 108.02 GiB | REJECTED-SLOW |
| Q6 10-expert CUDA path | Q6_K_XL | llama.cpp `72f9a97` | `-ncmoe 47 -ts 27,21` | Q8_0 | off | 14.84 | 12.16 | n/a | n/a | n/a | 21848 / 22744 MiB | 106.60 GiB | NEUTRAL |
| Q6 cafe winner | Q6_K_XL | cafe `f4dac26` | `-ncmoe 47 -ts 27,21`; no-pipeline fallback | Q8_0 | off | 16.90 | 13.67 | 12.50 | **10.27** | **64.37** | 6042 / 6364 MiB | 107.37 GiB | **WINNER** |
| Q6 cafe pinned-host | Q6_K_XL | cafe `f4dac26` | `-nhmoe 47 -ts 27,21` | Q8_0 | off | 15.61 | n/a | n/a | n/a | n/a | 6042 / 6364 MiB | 107.37 GiB | REJECTED-SLOW |
| Q6 cafe MTP n=2 | Q6_K_XL + Q4_K_M draft | cafe `f4dac26` | all routed experts host | Q8_0 | on | 11.99 | n/a | n/a | n/a | n/a | 5598 / 7562 MiB | 108.61 GiB | REJECTED-SLOW |

Rates are tokens/s. VRAM is the peak `nvidia-smi memory.used` observed during each run; host RAM is peak process RSS. The cafe rows' low VRAM is real: its initial pipeline graph reservation failed and it automatically retried without pipeline parallelism. EXP-015 processed 122,897 prompt tokens without truncation or server error and generated 128 tokens before natural termination; therefore its decode sample is valid but shorter than the requested 512-token target.

## Required recommendations and answers

### 1. HIGHEST-FIDELITY PRACTICAL

Q8_0 remains the highest-fidelity practical representation actually validated on this machine. Use Unsloth revision `c8b5954a88c2775c546b92593eda40ea041d3176`, first shard:

`/srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q8/Q8_0/Qwen3.8-Flash-Next-Q8_0-00001-of-00006.gguf`

The fully long-context-validated conservative command remains the Phase-1 corrected build:

```bash
LLAMA_ATTN_ROT_DISABLE=1 \
/srv/ai/benchmarks/qwen38-flash-next-20260829-105917/builds/current-corrected-d0e6d1a/bin/llama-server \
  -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q8/Q8_0/Qwen3.8-Flash-Next-Q8_0-00001-of-00006.gguf \
  -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer \
  -fit on -fitt 1024,1024 -fitc 131072 \
  -fa on -ctk f16 -ctv f16 -b 512 -ub 128 -t 16 -tb 16 \
  --metrics --host 127.0.0.1 --port 18080
```

Verified at 122,897 tokens: `23.53 pp tok/s`, `5.03 tg tok/s`, about `23.1/23.1 GiB` VRAM and `127.17 GiB` peak RSS.

### 2. BEST HIGH-FIDELITY PERFORMANCE

The primary deployment recommendation is Q6_K_XL on cafe `f4dac26`. Q6 is a modest numerical-fidelity reduction from Q8, but preserves the campaign's high-fidelity objective while more than doubling genuine 123K decode throughput. Exact command:

```bash
LLAMA_ATTN_ROT_DISABLE=1 \
/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/builds/cafe/bin/llama-server \
  -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q6/UD-Q6_K_XL/Qwen3.8-Flash-Next-UD-Q6_K_XL-00001-of-00006.gguf \
  -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer \
  -ngl all -ncmoe 47 -ts 27,21 \
  -fa on -ctk q8_0 -ctv q8_0 -b 512 -ub 128 -t 16 -tb 16 \
  --metrics --host 127.0.0.1 --port 18080
```

Model revision: `c8b5954a88c2775c546b92593eda40ea041d3176`; size `169,165,382,688` bytes (`157.55 GiB`). At 122,897 tokens it reached `64.37 pp tok/s` and `10.27 tg tok/s`, peak `6042/6364 MiB` VRAM and `107.37 GiB` RSS. Keep `LLAMA_ATTN_ROT_DISABLE=1`; it is part of the retained correctness configuration.

### 3. BEST Q8 CONFIGURATION

The best fully validated Q8 configuration is still the Phase-1 command above. Phase 2 intentionally limited the new Q8 control to 8K/32K before the Q6 decision, as instructed. Current corrected upstream gave `10.91/8.89 tg tok/s` at 8K/32K, but it was not promoted to a 64K/123K Q8 winner.

### 4. BEST Q6 CONFIGURATION

Use the cafe Q6 command in recommendation 2. Its measured path was `16.90`, `13.67`, `12.50`, and `10.27 tg tok/s` at 8K, 32K, 64K, and 122,897 tokens respectively; corresponding measured prefill was `60.76`, `64.15`, `64.47`, and `64.37 pp tok/s`.

### 5. BEST MTP CONFIGURATION

**MTP still not deployment-ready.** The only current compatible setup that loaded was cafe with the quimmedes Q4_K_M sidecar at revision `fb84e51`, `--spec-draft-n-max 2`. It achieved 110 accepted of 182 drafted tokens (`60.44%`) and `11.99` effective tg tok/s, versus `16.90` without MTP at 8K. It was stable in this screen but `29.1%` slower, so n=3/n=5 and deep-context MTP were correctly terminated early.

### 6. BEST 120K CONFIGURATION

The cafe Q6 command in recommendation 2 is the sole Phase-2 winner validated near full occupancy: 122,897 prompt tokens, `64.37 pp tok/s`, `10.27 tg tok/s`, no truncation, no server error, peak RSS `107.37 GiB`. Relative to the Phase-1 Q8 final it delivered `2.04x` decode (`+104.2%`) and `2.74x` prefill (`+173.6%`).

### Explicit answers to the 22 final questions

1. **Does Q6_K_XL justify its fidelity reduction?** Yes as the best high-fidelity performance point: on the same corrected runtime it was already `12.2%` faster at 8K and `8.4%` faster at 32K decode than Q8 automatic fit; the optimized final more than doubled Phase-1 Q8 deep-context decode. Q8 remains numerically higher fidelity.
2. **Is Q8 still preferred?** Only when maximum numerical fidelity is the overriding choice. For practical high-fidelity deployment, Q6 is preferred because of the measured throughput and lower RAM use.
3. **How much faster was Q8 made at ~123K?** Not measured in Phase 2; by instruction, the Q8 control stopped after 8K/32K. The validated Q8 ~123K figure remains `5.03 tg tok/s` from Phase 1.
4. **How much faster can Q6 be made?** The Phase-2 winner reaches `10.27 tg tok/s` at 122,897 tokens. At 8K, tuning raised Q6 from `12.24` automatic-fit to `16.90 tg tok/s` (`+38.1%`).
5. **Is automatic fit inferior?** For Q6 decode, yes: manual `-ncmoe 47` plus Q8 KV improved the corrected-upstream 8K result from `12.24` to `15.12 tg tok/s` (`+23.5%`).
6. **Best MoE placement?** `-ngl all -ncmoe 47 -ts 27,21`: the first 47 routed-expert blocks on host, the final one GPU-resident, with non-expert components requested on GPU.
7. **Does Q8 KV help placement?** Yes. At identical all-host-expert placement it improved decode from `14.14` to `14.69 tg tok/s` (`+3.9%`) and freed roughly 1 GiB/GPU; reinvesting capacity into the final expert block raised it to `15.12`.
8. **Does the GPU expert LRU help?** No. LRU-16 delivered `9.75 tg tok/s`, `35.5%` below the best manual upstream placement.
9. **Best cache size?** None. Only the evidence-backed 16-slot setting was tested; it regressed enough to trigger early termination, so no cache setting is recommended.
10. **Does latest proper MTP work correctly?** The cafe-specific current sidecar loaded and completed repeated inference without the Phase-1 termination failure, but it was slower. The separate native branch rejected the stale sidecar due to missing required tensors.
11. **MTP acceptance?** `110/182 = 60.44%` at n=2.
12. **Best `--spec-draft-n-max`?** n=2 is the only valid measured value, but is not recommended because it is slower than MTP-off.
13. **MTP at 64K/~120K?** Not measured; the 8K regression triggered the required early termination. It cannot be claimed beneficial there.
14. **Does cafe outperform corrected llama.cpp?** Yes at identical Q6 placement at 8K: `+15.7%` prefill and `+11.8%` decode. It also remained stable through 122,897 tokens.
15. **Does pinned-host MoE beat ordinary CPU MoE?** No. Prefill tied, while pinned-host decode was `7.6%` slower (`15.61` versus `16.90`).
16. **Does ik_llama improve CUDA decode?** Not demonstrable. The corrected attempt grew to about `151.4 GiB` RSS and was killed by OOM before readiness; classify it `REJECTED-OOM / NOT COMPARABLE`.
17. **Does selective PLE placement/quantization help?** Not measured. No credible public hybrid was found, and local conversion would have exceeded the focused campaign budget. PLE remained enabled in all winners.
18. **Is PLE a measured bottleneck?** Not isolated. Telemetry shows host traffic and sequential layer-split behavior, but does not separate PLE lookup cost from MoE expert traffic; no unsupported attribution is made.
19. **Does the 10-active-expert CUDA optimization improve long prefill?** No measurable benefit in the controlled tests: 8K prefill was identical and 32K was effectively unchanged. It was not advanced to 64K.
20. **Is tensor split correct/faster now?** No validated fix was present; current issue evidence still shows `SPLIT_AXIS_UNKNOWN`. Layer split remains the only correct tested mode.
21. **Is NCCL relevant?** No for the winner. NCCL was unavailable and tensor split remained unsupported; layer split does not provide a credible NCCL optimization path here.
22. **Exact model and command now?** For the recommended speed/fidelity deployment, use the Q6 model and cafe command in recommendation 2. If absolute fidelity outranks speed, use Q8 and the Phase-1 command in recommendation 1.

### EXP-001 — q8-current-auto-fit-f16kv-8k32k

- Hypothesis: Current upstream plus retained correctness patches may improve Q8 versus Phase 1 without changing representation
- Reason: Establish Phase-2 same-model runtime baseline before placement and feature A/B tests
- Result: PROMISING; ready 65.08196363600291; decode rates [10.908961984994722, 8.888894785336507]; hashes ['a84f511a8bd297b9d02c810cc7039d06cd8c6d09d44d03fb88ba6c0fc2a708bc', '497743d16c855e20daed97ea502e6004ddbc3d5c75f3965661d901a58f5752c2']; error None.
- Command: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/builds/upstream-corrected/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q8/Q8_0/Qwen3.8-Flash-Next-Q8_0-00001-of-00006.gguf -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer -fit on -fitt 1024,1024 -fitc 131072 -fa on -ctk f16 -ctv f16 -b 512 -ub 128 -t 16 -tb 16 --metrics --host 127.0.0.1 --port 18080`
- Raw logs: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-001-server-stdout.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-001-server-stderr.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-001-responses.json`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-001-gpu-telemetry.jsonl`

Control results on corrected current upstream: at 8,209 tokens, `36.38 pp tok/s` and `10.91 tg tok/s`; at 32,785 tokens, `40.53 pp tok/s` and `8.89 tg tok/s`. The model stopped naturally after 89 and 68 generated tokens respectively, so these are valid but shorter decode samples than the intended 256-token screen. The next Q6 run uses `ignore_eos` to obtain the full decode sample; no further Q8 tuning or longer Q8 run is performed before the Q6 comparison.

A 20-second live profile during the 32K prefill measured about `125.9 GiB` RSS, approximately one CPU core, no disk I/O or major faults, CUDA0 commonly at `90–96%` SM utilization while CUDA1 was mostly idle between layer-split bursts, and frequent CUDA0 PCIe receive traffic around `12–13 GB/s`. The full profile note is in `results/q8-32k-live-profile.md`. This is evidence of sequential layer-split execution plus substantial host expert traffic, not a final bottleneck attribution.

### EXP-002 — q6-current-auto-fit-f16kv-8k32k

- Hypothesis: Q6_K_XL materially improves throughput versus Q8 on identical corrected current runtime and automatic placement
- Reason: Direct same-runtime model decision before any further Q8 tuning
- Result: PROMISING; ready 67.07832336999854; decode rates [12.235298317444958, 9.633654862253527]; hashes ['5a5a2491cad8f142ec623fdbc7d78f93e96b42bf84bd342c015acd08356bd4f4', '49349ae1d1a289d567500a40f788481e5ace5940b778f2c08b931791c8b8d1ce']; error None.
- Command: `builds/upstream-corrected/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q6/UD-Q6_K_XL/Qwen3.8-Flash-Next-UD-Q6_K_XL-00001-of-00006.gguf -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer -fit on -fitt 1024,1024 -fitc 131072 -fa on -ctk f16 -ctv f16 -b 512 -ub 128 -t 16 -tb 16 --metrics --host 127.0.0.1 --port 18080`
- Raw logs: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-002-server-stdout.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-002-server-stderr.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-002-responses.json`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-002-gpu-telemetry.jsonl`

### EXP-003 — q6-manual-cmoe-f16kv-8k

- Hypothesis: Keeping all dense, attention, router, shared-expert and PLE tensors on GPU while placing all routed experts on CPU improves Q6 decode versus automatic fit.
- Reason: Direct manual-MoE placement test after same-runtime Q6 control.
- Result: PROMISING; ready 44.052791667003476; decode rates [14.139295347423278]; hashes ['6cdc107f570c36372020f8027ecc6f3192260e16cb43ef7e9621bfb3cb706fb8']; error None.
- Command: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/builds/upstream-corrected/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q6/UD-Q6_K_XL/Qwen3.8-Flash-Next-UD-Q6_K_XL-00001-of-00006.gguf -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer -ngl all -cmoe -ts 1,1 -fa on -ctk f16 -ctv f16 -b 512 -ub 128 -t 16 -tb 16 --metrics --host 127.0.0.1 --port 18080`
- Raw logs: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-003-server-stdout.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-003-server-stderr.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-003-responses.json`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-003-gpu-telemetry.jsonl`

### EXP-004 — q6-manual-cmoe-q8kv-8k

- Hypothesis: Q8_0 KV at identical manual MoE placement preserves speed while freeing about 1 GiB per GPU for a better placement or expert cache.
- Reason: Required same-placement F16 KV versus Q8 KV A/B before re-optimizing placement.
- Result: PROMISING; ready 53.06609110899808; decode rates [14.692167121730133]; hashes ['5a5a2491cad8f142ec623fdbc7d78f93e96b42bf84bd342c015acd08356bd4f4']; error None.
- Command: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/builds/upstream-corrected/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q6/UD-Q6_K_XL/Qwen3.8-Flash-Next-UD-Q6_K_XL-00001-of-00006.gguf -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer -ngl all -cmoe -ts 1,1 -fa on -ctk q8_0 -ctv q8_0 -b 512 -ub 128 -t 16 -tb 16 --metrics --host 127.0.0.1 --port 18080`
- Raw logs: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-004-server-stdout.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-004-server-stderr.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-004-responses.json`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-004-gpu-telemetry.jsonl`

### EXP-005 — q6-manual-ncmoe47-q8kv-8k

- Hypothesis: Q8 KV frees enough VRAM to keep the final routed-expert block on GPU and improve Q6 decode.
- Result: `PROMISING`; at 8,209 prompt tokens, `52.51 pp tok/s` and `15.12 tg tok/s` for the full 256-token decode.
- Placement: all non-MoE layers on GPU, the first 47 routed-expert layers on host, final routed-expert layer on GPU, layer split `27,21`, Q8_0 K/V.
- Relative result: decode is `+2.9%` versus EXP-004 (all routed experts on host, Q8 KV), `+6.9%` versus EXP-003 (manual host experts, F16 KV), and `+23.5%` versus EXP-002 (automatic-fit Q6). Prefill is effectively unchanged versus the other Q6 manual-placement tests.
- Peak measured allocation: CUDA0 `21848 MiB`, CUDA1 `22744 MiB`; process RSS `109.7 GiB` (`112,348,724 KiB`). The configuration initialized successfully with `-c 131072 -np 1` and retained usable VRAM margin.
- Raw logs: `logs/EXP-005-server-stdout.log`, `logs/EXP-005-server-stderr.log`, `logs/EXP-005-responses.json`, `logs/EXP-005-gpu-telemetry.jsonl`.

### EXP-006 — q6-lru16-cmoe-q8kv-8k

- Hypothesis: a 16-slot-per-layer GPU expert LRU cache would reduce host expert traffic.
- Result: `REJECTED-SLOW`; at 8,209 prompt tokens, `52.33 pp tok/s` and `9.75 tg tok/s` for 256 generated tokens.
- The prefill rate was effectively unchanged, while decode was `35.5%` slower than EXP-005 and `33.6%` slower than the equivalent all-host-expert Q8-KV placement without the cache (EXP-004). Peak process RSS also rose to `110.6 GiB`.
- The implementation performs exact cache-side and host-side MoE paths plus throttled uploads; on this machine its overhead dominates at LRU-16. Per the early-termination rule, no cache-size sweep is justified unless later profiling provides contrary evidence.
- Raw logs: `logs/EXP-006-server-stdout.log`, `logs/EXP-006-server-stderr.log`, `logs/EXP-006-responses.json`, `logs/EXP-006-gpu-telemetry.jsonl`.

### EXP-005 — q6-manual-ncmoe47-q8kv-8k

- Hypothesis: Q8 KV frees enough VRAM to keep the final routed-expert block on GPU and improve Q6 decode.
- Reason: Single targeted placement refinement after Q8-KV A/B.
- Result: PROMISING; ready 46.06065903999843; decode rates [15.115937461987862]; hashes ['5a5a2491cad8f142ec623fdbc7d78f93e96b42bf84bd342c015acd08356bd4f4']; error None.
- Command: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/builds/upstream-corrected/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q6/UD-Q6_K_XL/Qwen3.8-Flash-Next-UD-Q6_K_XL-00001-of-00006.gguf -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer -ngl all -ncmoe 47 -ts 27,21 -fa on -ctk q8_0 -ctv q8_0 -b 512 -ub 128 -t 16 -tb 16 --metrics --host 127.0.0.1 --port 18080`
- Raw logs: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-005-server-stdout.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-005-server-stderr.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-005-responses.json`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-005-gpu-telemetry.jsonl`

### EXP-006 — q6-lru16-cmoe-q8kv-8k

- Hypothesis: A 16-slot per-layer GPU LRU cache reduces host expert traffic enough to improve Q6 decode within safe VRAM.
- Reason: High-priority expert-cache test using the manual all-host-expert layout and measured Q8-KV headroom.
- Result: REJECTED-SLOW; ready 53.06416358599745; decode rates [9.749838267388741]; hashes ['53e92fb0dd749ed3a66225b1692325a7d05dee88a20f3e6e6780612453844f9b']; error None.
- Command: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/builds/lru/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q6/UD-Q6_K_XL/Qwen3.8-Flash-Next-UD-Q6_K_XL-00001-of-00006.gguf -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer -ngl all -cmoe -ts 1,1 -fa on -ctk q8_0 -ctv q8_0 -b 512 -ub 128 -t 16 -tb 16 --moe-expert-cache 16 --moe-expert-cache-inserts 2 --metrics --host 127.0.0.1 --port 18080`
- Raw logs: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-006-server-stdout.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-006-server-stderr.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-006-responses.json`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-006-gpu-telemetry.jsonl`

### EXP-007 — q6-pr27978-ncmoe47-q8kv-8k32k

- Hypothesis: The current 10-active-expert CUDA mm_ids fast path materially improves Q6 prefill without regressing decode.
- Reason: Controlled current-runtime A/B of the dedicated Flash-Next MoE prefill optimization on the best placement.
- Result: PROMISING; ready 53.06964377699842; decode rates [14.84370797920903, 12.156419618546867]; hashes ['5a5a2491cad8f142ec623fdbc7d78f93e96b42bf84bd342c015acd08356bd4f4', '49349ae1d1a289d567500a40f788481e5ace5940b778f2c08b931791c8b8d1ce']; error None.
- Command: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/builds/pr27978/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q6/UD-Q6_K_XL/Qwen3.8-Flash-Next-UD-Q6_K_XL-00001-of-00006.gguf -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer -ngl all -ncmoe 47 -ts 27,21 -fa on -ctk q8_0 -ctv q8_0 -b 512 -ub 128 -t 16 -tb 16 --metrics --host 127.0.0.1 --port 18080`
- Raw logs: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-007-server-stdout.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-007-server-stderr.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-007-responses.json`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-007-gpu-telemetry.jsonl`

Interpretation: `NEUTRAL` for the PR-specific hypothesis. At 8,209 tokens the prefill result (`52.5087 tok/s`) is numerically identical to corrected-upstream EXP-005 (`52.5086 tok/s`), while decode is `1.8%` lower (`14.84` versus `15.12 tok/s`). At 32,785 tokens it measured `43.03 pp tok/s` and `12.16 tg tok/s`. The 32K prefill is also effectively unchanged from the automatic-placement corrected-upstream Q6 control (`43.21 tok/s`); the decode improvement there is attributable to the already-proven manual placement. The dedicated 10-expert patch does not justify further testing in this campaign.

### EXP-008 — q6-cafe-ncmoe47-q8kv-8k

- Hypothesis: Current cafe-llama.cpp improves Q6 throughput at identical manual MoE placement.
- Reason: Clean current corrected llama.cpp versus cafe-llama.cpp A/B before testing cafe pinned-host MoE.
- Result: PROMISING; ready 53.06695036599922; decode rates [16.898597151360406]; hashes ['c860f1e4beb842896c736471d014a29cd379c08b98e8f8d15bb9c742b841a321']; error None.
- Command: `builds/cafe/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q6/UD-Q6_K_XL/Qwen3.8-Flash-Next-UD-Q6_K_XL-00001-of-00006.gguf -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer -ngl all -ncmoe 47 -ts 27,21 -fa on -ctk q8_0 -ctv q8_0 -b 512 -ub 128 -t 16 -tb 16 --metrics --host 127.0.0.1 --port 18080`
- Raw logs: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-008-server-stdout.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-008-server-stderr.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-008-responses.json`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-008-gpu-telemetry.jsonl`

### EXP-009 — q6-cafe-nhmoe47-q8kv-8k

- Hypothesis: Cafe pinned-host MoE improves over ordinary CPU MoE through pinned asynchronous transfer.
- Reason: Direct cafe CPU-MoE versus pinned-host-MoE comparison at identical Q6 placement.
- Result: REJECTED-SLOW; ready 55.06873804100178; decode rates [15.610296478096734]; hashes ['906df722e631df86c47b02379aec93b52fc00f42ca7bc72256eb39ee5d39b00e']; error None.
- Command: `builds/cafe/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q6/UD-Q6_K_XL/Qwen3.8-Flash-Next-UD-Q6_K_XL-00001-of-00006.gguf -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer -ngl all -nhmoe 47 -ts 27,21 -fa on -ctk q8_0 -ctv q8_0 -b 512 -ub 128 -t 16 -tb 16 --metrics --host 127.0.0.1 --port 18080`
- Raw logs: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-009-server-stdout.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-009-server-stderr.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-009-responses.json`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-009-gpu-telemetry.jsonl`

Interpretation: `REJECTED-SLOW` relative to cafe ordinary CPU-MoE EXP-008. At 8,209 prompt tokens, pinned-host MoE produced `60.79 pp tok/s` and `15.61 tg tok/s`; ordinary CPU-MoE produced `60.76 pp tok/s` and `16.90 tg tok/s`. Prefill is a numerical tie, while pinned-host decode is `7.6%` slower. No pinned-host parameter sweep is justified.

EXP-008 interpretation: `PROMISING`. At the identical Q6 `-ncmoe 47`, Q8-KV placement, cafe produced `60.76 pp tok/s` and `16.90 tg tok/s`, improving corrected-upstream EXP-005 by `15.7%` in prefill and `11.8%` in decode. Cafe first attempted an invalid `408774.60 MiB` pipeline graph allocation, then automatically retried without pipeline parallelism and completed stably; this fallback is recorded because it may contribute to the observed runtime difference.

### EXP-010 — q6-ik-ncmoe47-q8kv-8k

- Hypothesis: Current ik_llama Qwen3.8-Flash-Next CUDA TG optimization improves Q6 throughput at comparable placement.
- Reason: Single controlled current ik_llama versus corrected upstream and cafe A/B.
- Result: REJECTED-INCORRECT; ready None; decode rates []; hashes []; error RuntimeError('server exited during load with code 1').
- Command: `builds/ik/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q6/UD-Q6_K_XL/Qwen3.8-Flash-Next-UD-Q6_K_XL-00001-of-00006.gguf -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer -ngl all -ncmoe 47 -ts 27,21 -fa on -ctk q8_0 -ctv q8_0 -b 512 -ub 128 -t 16 -tb 16 --metrics --host 127.0.0.1 --port 18080`
- Raw logs: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-010-server-stdout.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-010-server-stderr.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-010-responses.json`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-010-gpu-telemetry.jsonl`

### EXP-011 — q6-ik-ncmoe47-q8kv-8k-retry

- Hypothesis: Current ik_llama Qwen3.8-Flash-Next CUDA TG optimization improves Q6 throughput at comparable placement.
- Reason: One corrected retry: ik_llama requires numeric -ngl; EXP-010 used upstream-specific value all and failed in CLI parsing before model load.
- Result: REJECTED-OOM; ready None; decode rates []; hashes []; error RuntimeError('server exited during load with code -9'). Peak RSS reached about 151.4 GiB before SIGKILL.
- Command: `builds/ik/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q6/UD-Q6_K_XL/Qwen3.8-Flash-Next-UD-Q6_K_XL-00001-of-00006.gguf -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer -ngl 999 -ncmoe 47 -ts 27,21 -fa on -ctk q8_0 -ctv q8_0 -b 512 -ub 128 -t 16 -tb 16 --metrics --host 127.0.0.1 --port 18080`
- Raw logs: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-011-server-stdout.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-011-server-stderr.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-011-responses.json`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-011-gpu-telemetry.jsonl`

### EXP-012 — q6-mtp-n2-cmoe-q8kv-8k

- Hypothesis: Correct current Qwen4Exp native MTP with two draft tokens increases effective Q6 decode while preserving deterministic target output.
- Reason: Low-cost first MTP test after independent target-placement and cache tests; all target routed experts stay on host to reserve VRAM for the 2.5 GiB sidecar.
- Result: REJECTED-INCORRECT; ready None; decode rates []; hashes []; error RuntimeError('server exited during load with code 1').
- Command: `builds/mtp/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q6/UD-Q6_K_XL/Qwen3.8-Flash-Next-UD-Q6_K_XL-00001-of-00006.gguf -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer -ngl all -cmoe -ts 1,1 -fa on -ctk q8_0 -ctv q8_0 -b 512 -ub 128 -t 16 -tb 16 --spec-type draft-mtp -md /srv/ai/models/Qwen3.8-Flash-Next-MTP-GGUF-20260829-dzannotti/Qwen3.8-Flash-Next-MTP-Q4_K_M.gguf -devd CUDA0,CUDA1 -ngld all --spec-draft-n-max 2 -ctkd q8_0 -ctvd q8_0 --metrics --host 127.0.0.1 --port 18080`
- Raw logs: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-012-server-stdout.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-012-server-stderr.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-012-responses.json`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-012-gpu-telemetry.jsonl`

### EXP-013 — q6-cafe-current-mtp-n2-cmoe-q8kv-8k

- Hypothesis: Current cafe-native Qwen3.8-Flash-Next MTP sidecar increases effective Q6 decode and loads with corrected hyperconnection tensors.
- Reason: One targeted compatibility/performance retest using the newly released cafe-specific sidecar revision fb84e51 after the stale sidecar failed tensor validation.
- Result: REJECTED-SLOW; ready 56.0638974800022; decode rates [11.988275748395147]; hashes ['5e80a99cedb5cfba7204443ee508124bdc5c826363f40c592c3c4dd297db68f3']; error None. Acceptance was 110/182 (60.44%), but effective decode was 29.1% slower than MTP-off.
- Command: `builds/cafe/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q6/UD-Q6_K_XL/Qwen3.8-Flash-Next-UD-Q6_K_XL-00001-of-00006.gguf -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer -ngl all -cmoe -ts 1,1 -fa on -ctk q8_0 -ctv q8_0 -b 512 -ub 128 -t 16 -tb 16 --spec-type draft-mtp -md /srv/ai/models/Qwen3.8-Flash-Next-MTP-GGUF-20260830-quimmedes/mtp-Qwen3.8-Flash-Next-Q4_K_M.gguf -devd CUDA0,CUDA1 -ngld all --spec-draft-n-max 2 -ctkd q8_0 -ctvd q8_0 --metrics --host 127.0.0.1 --port 18080`
- Raw logs: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-013-server-stdout.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-013-server-stderr.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-013-responses.json`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-013-gpu-telemetry.jsonl`

### EXP-014 — q6-cafe-ncmoe47-q8kv-32k64k

- Hypothesis: Cafe winner retains its 8K advantage at 32K and 64K occupancy.
- Reason: Semifinal validation of the strongest Q6 configuration before any long-context final.
- Result: PROMISING; ready 52.06208915800016; decode rates [13.671246354782838, 12.49999876968516]; hashes ['82ded9aca13528b025079ee75b191434a234d748def7e43844185d98049667dd', '0824f0c1b2bc65108b91da96532a9ab9929ffb54fd6b0404805014bcda1d997e']; error None.
- Command: `builds/cafe/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q6/UD-Q6_K_XL/Qwen3.8-Flash-Next-UD-Q6_K_XL-00001-of-00006.gguf -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer -ngl all -ncmoe 47 -ts 27,21 -fa on -ctk q8_0 -ctv q8_0 -b 512 -ub 128 -t 16 -tb 16 --metrics --host 127.0.0.1 --port 18080`
- Raw logs: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-014-server-stdout.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-014-server-stderr.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-014-responses.json`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-014-gpu-telemetry.jsonl`

### EXP-015 — q6-cafe-ncmoe47-q8kv-123k-final

- Hypothesis: The Q6 cafe winner remains stable and materially faster than Phase-1 Q8 at genuine ~123K occupancy.
- Reason: Single cold-server final validation of the strongest Phase-2 configuration.
- Result: WINNER; ready 54.068657897001685; decode rates [10.272134731583863]; hashes ['0d2d2168c6cb604a51c8264febe3a677f80c7d9df6f3fcd8b88c1c6e1a5be957']; error None.
- Command: `builds/cafe/bin/llama-server -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q6/UD-Q6_K_XL/Qwen3.8-Flash-Next-UD-Q6_K_XL-00001-of-00006.gguf -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer -ngl all -ncmoe 47 -ts 27,21 -fa on -ctk q8_0 -ctv q8_0 -b 512 -ub 128 -t 16 -tb 16 --metrics --host 127.0.0.1 --port 18080`
- Raw logs: `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-015-server-stdout.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-015-server-stderr.log`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-015-responses.json`, `/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320/logs/EXP-015-gpu-telemetry.jsonl`
