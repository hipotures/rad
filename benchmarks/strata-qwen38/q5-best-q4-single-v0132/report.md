# Q5 single test — upstream load failure

Attempted exact engine configuration of the historical fastest Q4 run: v0.1.32 default build, bothRTX4090, K24, INT8KV, prefillauto, max262144, spec4/minp0.5; same commonMTP. Planned literal saved prompt31400+256 output, temperature0.

Status: Q5_LOAD_FAILED_UPSTREAM_GGUF_READER. Zero smoke/warmup/measured requests. PP/TG/TTFT unavailable, not zero.

Error: `GGUF: data section starts past EOF`. First Q5 GGUF shard has zero tensors and only metadata; size10946618bytes, correct pinned LFS SHA256. Loader default32-byte alignment produces data_start10946624,6bytes beyond EOF; include/strata/artifact/gguf_reader.hpp:458 rejects it even though no tensor data exists.

Q5 pack completed successfully with tools/iq_pack.py --compat-bf16 and noexperts.bin; routed experts91.61377GiB. No engine patch, no GGUF padding or weight edits, no alternate candidate. Both GPUs released.

Evidence: logs/Q5-BEST-Q4-engine.log, raw/load-failure-audit.json, summary.json, plan.json. Prepared exact payload saved for future supported runtime. Earlier external preflight config-file error retained separately in raw/preflight-driver-attempt1.json; it also made zero requests.
