# E002: fresh controls at production context capacities

Question: what is CURRENT performance and actual expert memory at total-context limits 32768 and 131072?

Frozen source 6f32ec070f23ced9f50e704d854d775da52591ab; separately rebuilt clean binary. Toolchain/dependencies and commands are retained in git/. Historical 262144-capacity measurements are not fresh controls.

Order: 32k, then 128k. One fresh server per profile; identical saved 4096-input/64-output warmup, then exactly three measured attempts using frozen run1/run2/run3 payloads. Cache history persists within a cell. No concurrency, training/builds/heavy analysis/hashing during headline requests. Greedy, MTP4/min-p0.5, INT8 KV, kv-resident32768, workers15, K25, PCIe0.28, prefillauto, suffix0, prompt-cache0. Every measured output requests4096 tokens. Preserve early EOS and failures; do not silently retry unchanged points.

Inputs retain the saved repository maintenance task and deterministic complete-line source prefixes. Actual IDs/counts are in workloads/manifest.json. Admission requires input+output+8 <= configured context; a larger 256-token preparation allowance remains. Check API count, zero reuse, output4096 and no tool calls. Record startup capacities/bytes and per-GPU peak allocation; do not assume smaller maximum context frees VRAM.

Completion: both bounded three-attempt cells, saved logs/raw/system telemetry, resource/counter table, validity classification and baseline report. Native environmental failures are separately documented; no unexamined correctness failure is waived.
