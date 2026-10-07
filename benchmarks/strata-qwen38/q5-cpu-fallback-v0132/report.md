# Q5 semantic CPU-only expert fallback — checkpoint

**Status: STOP_NEXT_BLOCKER: PLE_Q8_0_NATIVE_TABLE_UNSUPPORTED.** Patch built and regression tests passed. Single-GPU Q5 load accepted the expert formats, then failed before READY on the Q8_0 PLE table. Q5 is not yet operational; no model generation, speed measurements, llama.cpp output comparison or needles were performed.

## Provenance and preservation

Separate checkout `/srv/ai/strata-v0.1.32-q5`, exact base v0.1.32 / HEAD `c499bd102e7a4135c0de389dcfe38c399759ccc8`. Separate `build-cpu-only/strata` default CUDA Release build, architecture 89, Q4 MMQ optimization option OFF. Prior `build-default`, prior loader results and clean `/srv/ai/strata-v0.1.32` preserved. No commits/push, no new CUDA arithmetic kernels, no model/pack edits, no experts.bin.

Full patch (including prior metadata-only loader fix and both new untracked source files): `cpu-only-fallback.patch`, SHA256 `eaf9c752f4737553984c589e3f2374ed7e8fef5792ff693e8cd24370893b5e75`. Binary SHA256 `bb4f920d5bed1aaa56cb1d917f259633395e8dd316fe3d56c354e45756510802`. Full command/config and model revision are in `raw/Q5-CPU-1GPU-load-result.json` and `environment.json`. Six GGUF files retained original size/mtime/inode; this is a stat preservation check, not a new full-file hash pass. Existing verified hashes remain in prior environment/model manifests. Clean checkout tracked files unchanged. Both GPUs released after failure.

## Runtime change

CPU format/geometry support is validated by `expert_layout_load` / `native_fmt`. Startup computes GPU capabilities with `native_expert_supported` and marks unsupported GPU formats CPU-only; no test on a particular layer number is used. Actual Q5 has one such layer (2: Q6_K/Q8_0), and 47 GPU-supported Q5_K/Q8_0 layers.

The mask filters ranked profiles, blocks cache lookup/admission and adaptive candidates, prevents PCIe expert groups and helper GPU placement/dispatch, and skips unsupported grouped CUDA expert nodes in verify while retaining host plan publication, completion and combine. CPU-only prefill downloads FP32 mixed activations, computes native routed experts through bounded CPU batches (MAXT=8), scatters expert-sorted outputs into the existing GPU combine layout and applies router weights only in combine. CPU-only experts are omitted from the streamed GPU expert ring. Shared experts and dense/attention operations retain their GPU paths.

Native packs still use upstream multi-token verify even for a one-token window; the upstream canonical single-token adapter explicitly refuses native packs and has not been expanded. The fallback follows that native verify path.

## Validation completed

CTest command:

```sh
ctest --test-dir build-cpu-only --output-on-failure -R '^(cpu_only_expert_test|gguf_reader_test|gguf_split_test|expert_layout_test|native_expert_parity_refuses_q6_K|native_expert_parity_q5_K_q8_0)$'
```

6/6 PASS (`logs/strata-q5-cpu-ctest3.log`). Detailed new-test output: `logs/cpu-only-test-detail.log`.

- Q6_K/Q8_0 CPU supported; direct GPU Q6 expert pair still rejected.
- Q5_K/Q8_0 direct GPU parity test remains passing.
- Capability-derived mixed policy; CPU-only layer cannot obtain GPU cache slots, other layers retain slots.
- Helper GPU rejects an exclusively CPU-only ranking; profile filter preserves supported-layer order.
- 19-token CPU prefill batch with reordered source indices and a MAXT tail matches serial native CPU reference bitwise; invalid token indices rejected.
- Multi-token decode with deliberately stale positive residency and maximum PCIe fraction still dispatches every CPU-only entry to CPU. Zero GPU/PCIe counts, publication and fetch completion preserved. Output matches serial CPU reference without weights being applied in the expert computation.
- Supported layer still produces GPU-hit plans.
- GGUF reader/split and existing layout tests pass.

These are synthetic/unit/component tests. They do not establish whole-model graph/MTP correctness, greedy parity, quality or throughput. Full integration tests remain blocked by loading PLE.

## Single-GPU load outcome and exact next blocker

Intended smoke: CUDA0 only, full routed RAM arena, max_context 262144, INT8 KV, spec 4/min-p 0.5, default prefill, existing MTP; 2048-token prompt / 64-token output after READY. The model failed before the arena/prompt request stage, so neither prompt nor generation was sent. Two-GPU K24 smoke was not started.

```text
strata generate: layer 2 routed experts Q6_K/Q8_0: CPU_ONLY_FORMAT_FALLBACK (GPU cache/PCIe/helper disabled)
strata generate: PCIe probe: 13.4 GB/s host->device -> pcie_frac 0.28 (default 0.55)
strata generate: native pack: /srv/ai/models/strata/packs/ud-q5_k_xl-v0132 experts (largest blob 4.43 MB), token embedding Q8_0 in mapped host memory (644 MiB)
strata generate: 1416 MiB of weights loaded from /srv/ai/models/strata/packs/ud-q5_k_xl-v0132 (303 canonical tensors skipped: served natively)
strata generate: 301 native projection matrices, 2975.00 MiB of weights
strata generate: per_layer_token_embd.weight is Q8_0, not IQ4_NL, Q5_0 or FP8 (I8)
```

Blocker is `strata::kernels::PleTable::open` in `src/kernels/ngram.cpp:208`, reached from `src/program/generate.cpp:2038`. Supported table formats there are IQ4_NL, Q5_0 and tagged FP8/I8; Q8_0 is explicitly refused. This is a different tensor from the already-supported Q8_0 PLE key projection.

Actual tensor (read from GGUF header): `per_layer_token_embd.weight`, Q8_0 / ggml type 8, shape `[160, 320001536]`, `54400261120` bytes (~54.4 GB), shard `/srv/ai/models/Qwen3.8-Flash-Next-GGUF-38bb39ee-unsloth-Q5/UD-Q5_K_XL/Qwen3.8-Flash-Next-UD-Q5_K_XL-00003-of-00006.gguf`, absolute payload offset `192`. Details: `raw/next-blocker-tensors.json`.

## Pending and next action

Next blocker to study is native Q8_0 PLE table access/dequantization, keeping original GGUF unchanged. No attempt was made to disable PLE, substitute Q4's table, requantize it or add a second unrelated patch. After PLE support is validated, resume one- and two-GPU smoke, full prefill/graph/MTP correctness, same-GGUF llama.cpp parity and 32K/128K needles. Only then speed.

No quality or tok/s inference is drawn from the quantization bitrate or from synthetic CPU parity. All pending work is also in STATUS.md/STATUS.json.
