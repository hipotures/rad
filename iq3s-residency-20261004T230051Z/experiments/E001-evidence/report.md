# E001 evidence and source audit

The four required reports and actual configs, summaries, tokenization/provenance evidence and hardware cost models were inspected and copied with hashes. Hardware study located at `/srv/ai/benchmarks/qwen-hardware-characterization/run-20261004T104353Z/`, titled `VM hardware and MoE residency data-movement study`. Its cost-model/scheduler-envelope and source manifests point to retained raw/code evidence. This campaign reuses those measurements rather than rerunning them.

Fresh checkout/control is frozen to6f32ec070f23ced9f50e704d854d775da52591ab. The former checkout's e15f4f0 diagnostic commit is not used. New control binary eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d is rebuilt and measured; preserved original871bb3b8... remains untouched. Current GitHub main inspected through gh still equals6f32ec0; no moving-base substitution.

Runtime admission requires input+max_new+8 <= configured context in both serve/server.py and src/program/generate.cpp. Frozen workload family uses complete-line truncation, output4096 and256 preparation headroom at total limits32768/131072. No hidden context extension or output shortening.

## Counters and implementation

- `cache_hits`: routed(token,expert) entries with local resident slot. `cache_refused`: CPU fallback entries. `offload_entries`: mapped PCIe or peer/remote entries; neither hits nor refused. Reported hit denominator is hits+admitted+refused, so it excludes offload work. All-demand denominator includes offload entries. Counts are not distinct miss identities.
- `multi_misses`: distinct expert CPU jobs per layer/group; `multi_entries`: CPU routed entries. `pcie_experts`: distinct experts assigned to mapped/DMA GPU path. Distinguish entries/jobs/bytes.
- CPU and GPU compute selected experts from the actual router. Native arena is preloaded RAM; mmap-source file counters do not independently measure arena SSD reads. Unknown logical file reads stay unavailable.
- Existing policy adds all computed verification-branch routing into usage, including rejected drafts; every4rounds it compares same-layer most-used missing experts against cold residents, gain threshold1.5, minimum incoming usage2, at most96swaps, then usage decays0.7. Immutable weights are copied on adaptation streams, outgoing residency withdrawn, incoming published after existing events complete. `apply_pending(true)` waits before the next window. This can expose readiness latency despite asynchronous issue.
- Cache slots have variable byte sizes fixed at startup. Contiguous layer ownership staysK25. Per-layer-only swaps can create budget imbalance; cross-layer exchanges require compatible slot sizes and same GPU ownership. Two memories are not one freely accessible48GiB pool.
- GPU-reach waits include actual graph dependencies before router/doorbell delivery; they are not per-miss costs. Existing wait/pool clocks overlap GPU work and must not be summed as disjoint total costs.
- RouterLookahead already computes next-layer gates on current CPU-visible activations but only warms file pages; full-RAM arena makes page warming alone a weak hypothesis. Its legitimate signal timing and numeric cost are still to be evaluated, rather than using future router outputs as causal predictors.

## Primary-source review

Open-Jev pinnedbd4118882f733574a3250a4b65fe4d884130c08b, MIT, source fetched withgh without executing vendor code. README/model/training/calibration source inspected. Reused conceptual pattern: score explicit candidates with a scalar head, without autoregressive answer generation; separate calibration and task-isolated evaluation. Our branch will be a small numeric expert-demand scorer, not its released LM backbone and not a claim about proprietary Jev internals or published task scores. [Source](https://github.com/Zefan-Cai/Open-Jev/tree/bd4118882f733574a3250a4b65fe4d884130c08b).

Fate v1 uses current intermediate states with next-layer gate weights to predict upcoming demand early; transfer readiness and differing per-layer needs matter. Only prediction/cache scheduling ideas are in scope; its quantization changes are excluded. [Paper](https://arxiv.org/html/2502.12224v1).

SpecMD v1 Least-Stale distinguishes previous-cycle stale entries from current/prefetched entries, prioritizes stale victims, and uses layer-position FIFO within queues. Its cross-layer/global-cache motivation differs from Strata's fixed same-layer slots. Replay will label adaptations explicitly and preserve the router; dropping/substitution/precision changes are excluded. [Paper](https://arxiv.org/html/2602.03921v1).

All candidate branches remain in candidate-ledger.json. Evidence is not yet sufficient to select a runtime improvement or declare a capacity/coordination ceiling.
