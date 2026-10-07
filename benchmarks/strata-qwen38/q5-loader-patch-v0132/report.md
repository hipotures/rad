# Q5 metadata-only loader patch and smoke

Status: FAIL_NEXT_BLOCKER

Separate checkout /srv/ai/strata-v0.1.32-q5, exact basev0.1.32 c499bd102e7a4135c0de389dcfe38c399759ccc8 plus recordedlocaldiff. Clean checkout unchanged. No model/pack edits. No commit/push.

Regression: gguf_reader_test / gguf_split_test PASS; newly added metadata-only test FAIL with clean header and PASS with patch; tensor-bearing truncation and truncated metadata remain rejected. RealQ5 split headers6shards/1224tensors PASS. Separate defaultCUDA build sm89; Q4-fast OFF.

Runtime:2RTX4090,K24,INT8KV,max262144,prefillauto,spec4,minp0.5,same existingMTP,fullRAMarena91.6GiB, noresidentbudget. Memoryguard12GiB. Smoke8Kprompt64output only; no warmup or benchmark.

RuntimeError('Engine exited 1')

```text
strata generate: layer split across 2 GPUs: CUDA0, then CUDA1 (split 24)
strata generate: layer 2's experts are Q6_K/Q8_0 (ggml types 14/8), which this engine has no GPU kernels for
```

Stopped at next blocker; no additional patch or fallback applied.

Patch:metadata-only-gguf.patch. Source/build/test/config/modelprovenance:environment.json; normal logs:logs/; canonical raw smoke:raw/. BothGPUreleased after run.

## Exact next blocker

Layer2 gate/up: `blk.2.ffn_gate_exps.weight`, `blk.2.ffn_up_exps.weight` = **Q6_K (type14)**; down: `blk.2.ffn_down_exps.weight` = **Q8_0 (type8)**. All in shard4. Native GPU format guard at src/program/generate.cpp:1678 calls native_expert_supported in src/kernels/cuda/iq_kernels.cu:1417; its is_iq/gu_qk supported-type tables omit Q6_K. Guard exits1 before arena/GPU cache allocation. No further modification made; zero generation and benchmark requests.
