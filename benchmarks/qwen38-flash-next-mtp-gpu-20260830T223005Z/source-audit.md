# Qwen3.8-Flash-Next MTP source audit

## Audited runtime

- Repository: `/srv/ai/llama.cpp-qwen4exp`
- Origin: `https://github.com/unslothai/llama.cpp`
- Exact commit: `250b61446efc91e3a179c8677956f2667c8fbda0`
- Commit date: 2026-08-27
- Primary binary: `/srv/ai/llama.cpp-qwen4exp/build-cuda-sm89/bin/llama-server`
- Worktree was clean at audit time.

## What the Qwen3.8-Flash-Next MTP module is

The native/public implementation is an embedded one-layer **Lightning MTP**
module. It is not another 48-layer target model, but it is substantially more
than an output projection. Its input is the target's 4-stream hyperconnection
state (4 x 2560 = 10240 floats) plus the embedding of the next token. It contains:

- embedding and hidden normalization plus `nextn.eh_proj`;
- one Qwen sparse-attention block with Q/K/V/output projections;
- a QSA indexer;
- one routed MoE with 512 experts plus a shared expert;
- attention and FFN hyperconnection mixers;
- output/hyperconnection projection and tied or copied token embedding/output.

The local Q4 candidates are 2.62 and 2.79 GB. The native BF16 sidecar is about
7.77 GB. The public oMLX implementation explicitly sets one MTP layer and an
empty PLE layer list. Therefore the MTP head has its own one-block GPU work and
does not need to execute the target's PLE or its 48 target blocks while drafting.

## Public oMLX/Jundot execution path

```text
target verified hyperconnection state (10240-wide, GPU)
  -> normalize target state + next-token embedding
  -> nextn.eh_proj
  -> one MTP sparse-attention + 512-expert MoE block (PLE disabled)
  -> draft token + next MTP hyperconnection state
  -> repeat MTP block up to maximum depth 3
  -> one batched target verification of [main token, drafts]
  -> accept/reject; trim/replay target recurrent and KV state
```

Facts from the public implementation:

- MTP is embedded as `Qwen4ExpMTPModule`, with one decoder layer.
- The target exposes residual/hyperconnection state before its final mixer.
- Draft steps chain the MTP output state; they do not rerun all target blocks.
- Verification evaluates the main token and draft candidates in one target call.
- Greedy verification accepts matching argmax tokens. Stochastic verification
  uses the standard probability-ratio acceptance and residual distribution on
  rejection, preserving the target distribution.
- The adaptive controller estimates conditional acceptance per depth and elapsed
  costs with moving averages, then selects the best depth up to the configured max.
- MLX arrays and caches remain on the Metal device; host involvement is limited
  to control/sampling synchronization.

Inference, not independently established fact: the reported near-100% acceptance
is plausibly due to a jointly trained native MTP module, favorable/greedy prompts,
and workload choice. High acceptance alone does not prove a speedup.

## Current llama.cpp generic `draft-mtp` path

`common/speculative.cpp` contains generic MTP orchestration. For one MTP layer it
does the following:

```text
target decode/verify (target PLE and selected CPU MoE execute here)
  -> copy target nextn hidden row to host `verify_h` / `pending_h`
  -> inject token + hidden row into draft context
  -> decode one MTP block
  -> copy draft nextn hidden row to host
  -> inject token + hidden row for next draft step
  -> repeat up to depth 3
  -> target verifies candidates in a batch
```

Important consequences:

- Draft generation itself calls `llama_decode(ctx_dft)`, not the target context.
  Therefore a correct Qwen4Exp MTP graph would not invoke target routed experts
  or target PLE for each draft token.
- The MTP block has its own 512-expert MoE. With `-ngld all` its weights can in
  principle reside on GPU.
- The generic implementation stores `pending_h`, `verify_h`, and `chain_h` in
  host `std::vector<float>` objects. `llama_get_embeddings_nextn[_ith]()` is read
  into those buffers and `memcpy` injects the row into the next draft batch.
- Qwen4Exp sets `n_embd_out = hc_mult * n_embd = 4 * 2560 = 10240`, so one FP32
  state row is 40,960 bytes. Chained depth-3 drafting therefore introduces at
  least one device-to-host state extraction and one host-to-device injection per
  draft step, plus synchronization. It is not a strictly GPU-resident draft path.
- The built-in adaptive behavior is only a probability threshold (`p_min`), not
  the oMLX time/acceptance EMA depth controller.

## Blocking Qwen4Exp runtime limitation

The current Qwen4Exp conversion class explicitly declares
`supports_mtp_export = False` and `no_mtp = True`. The current
`src/models/qwen4exp.cpp` loads and builds only the 48-layer target graph; it has
no Qwen4Exp `nextn` tensor loader or MTP graph. Thus the generic
`--spec-type draft-mtp` orchestration exists, but this exact model handler cannot
construct the model-specific sidecar execution graph.

The local dzannotti patch demonstrates the missing implementation: it adds the
`nextn` tensor mappings, one extra full Qwen4Exp block, target hidden-state export,
and the MTP graph consuming a 10240-wide target state. The patch does not apply
cleanly to commit `250b614...` (`conversion/qwen4exp.py` and
`src/models/qwen4exp.cpp` both conflict), so it is not part of the required current
runtime and was not silently applied.

The controlled startup test established the limitation in the actual loader.
After the operator released both GPUs, the exact fixed target configuration and
the complete quimmedes sidecar were started with `--spec-type draft-mtp`,
`--spec-draft-n-max 3`, and `-ngld all`. The target initialized, then the real
draft-model load failed at 31.284 seconds:

```text
common_speculative_init_result: loading draft model '...mtp-Qwen3.8-Flash-Next-Q4_K_M.gguf'
llama_model_load: error loading model: check_tensor_dims: tensor 'blk.0.hc_attn_norm.weight' not found
common_speculative_init_result: failed to load draft model
srv load_model: failed to load draft model
```

The earlier memory-fitting preflight produced the identical error. This is not
an out-of-memory condition and not a placement-override failure: the current
handler is constructing the ordinary Qwen4Exp target tensor schema, beginning
at block 0, instead of the sidecar-specific `nextn` schema. The server exited
before listening and before any inference. Both GPUs returned to 1 MiB used.

This satisfies the mandatory early-stop condition: the current llama.cpp cannot
execute this model-specific MTP correctly. Consequently no performance or
acceptance claims are made.

## Source evidence locations

- `conversion/qwen4exp.py:30-31`: MTP conversion disabled.
- `src/models/qwen4exp.cpp:23-27`: 4-stream hyperconnection and 10240 output state.
- `common/speculative.cpp:1284-1700`: generic MTP orchestration.
- `common/speculative.cpp:1307-1318`: host-resident hidden-state vectors.
- `common/speculative.cpp:1486-1550`: target hidden-state extraction/copy.
- `common/speculative.cpp:1607-1685`: per-draft decode and hidden-state copy/reinjection.
- `/tmp/omlx-mtp-audit/omlx/patches/mlx_vlm_qwen4_exp_compat/vendor/mlx_vlm/models/qwen4_exp/language.py`: public one-layer module.
- `source-snapshots/mtp-symbols.txt` and `source-snapshots/omlx-symbols.txt`: line-index snapshots.
- `logs/mtp-loader-probe.log`: complete controlled loader failure.
