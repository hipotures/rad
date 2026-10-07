# Exact prepared commands

The operator confirmed that unrelated GPU test processes were stopped. The MTP
loader/placement probe below was executed once. It failed before inference as
recorded in `../logs/mtp-loader-probe.log`; the formal servers were therefore
not executed under the required early-stop rule.

## Common target arguments

```bash
-m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-IQ4XS/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00003.gguf \
-c 32768 -np 1 -b 2048 -ub 2048 -t 16 -tb 16 \
-ngl all -sm layer -ts 1,1 -fa on \
--tensor-read-lazy on --cache-reuse 0 \
-ot 'per_layer_token_embd\.weight=CPU,blk\.([0-9]|2[4-9]|3[0-3])\.ffn_(up|down|gate|gate_up)_(ch|)exps=CPU'
```

## Executed controlled MTP loader/placement probe

```bash
LLAMA_ATTN_ROT_DISABLE=1 \
/srv/ai/llama.cpp-qwen4exp/build-cuda-sm89/bin/llama-server \
-m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-IQ4XS/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00003.gguf \
-c 32768 -np 1 -b 2048 -ub 2048 -t 16 -tb 16 \
-ngl all -sm layer -ts 1,1 -fa on \
--tensor-read-lazy on --cache-reuse 0 \
-ot 'per_layer_token_embd\.weight=CPU,blk\.([0-9]|2[4-9]|3[0-3])\.ffn_(up|down|gate|gate_up)_(ch|)exps=CPU' \
-md /srv/ai/models/Qwen3.8-Flash-Next-MTP-GGUF-20260830-quimmedes/mtp-Qwen3.8-Flash-Next-Q4_K_M.gguf \
-ngld all --spec-type draft-mtp --spec-draft-n-max 3 \
--spec-draft-p-min 0.75 --port 18081
```

The quimmedes artifact was selected because it has the complete 35-tensor set,
including `nextn.shared_head_norm`. The target arguments and placement expression
are byte-for-byte the same as the target-only configuration.

## Formal target-only server (not executed: MTP probe failed)

```bash
/srv/ai/llama.cpp-qwen4exp/build-cuda-sm89/bin/llama-server \
-m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-IQ4XS/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00003.gguf \
-c 32768 -np 1 -b 2048 -ub 2048 -t 16 -tb 16 \
-ngl all -sm layer -ts 1,1 -fa on \
--tensor-read-lazy on --cache-reuse 0 \
-ot 'per_layer_token_embd\.weight=CPU,blk\.([0-9]|2[4-9]|3[0-3])\.ffn_(up|down|gate|gate_up)_(ch|)exps=CPU' \
--port 18081
```

## Formal MTP server (not executed: MTP probe failed)

The formal MTP command is identical to the loader probe above. No target tensor
override is added or removed. Draft depth is capped at three; `p_min=0.75` is the
only adaptive mechanism exposed by this runtime.
