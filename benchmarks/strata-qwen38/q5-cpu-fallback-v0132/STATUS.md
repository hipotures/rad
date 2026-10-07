# Strata v0.1.32 — STOP_NEXT_BLOCKER

## Running

```json
null
```

## Completed

- semantic CPU/GPU per-layer policy, no hardcoded layer index
- GPU cache/profile/adaptive/PCIe/helper exclusion
- verify graph grouped-expert bypass with normal plan/combine protocol
- native CPU prefill with MAXT=8 bounded batches
- separate build-cpu-only CUDA build
- 6/6 regression CTests PASS
- single-GPU load attempted: experts accepted, next PLE blocker reported

## Pending

- native Q8_0 PLE support feasibility/implementation
- single GPU READY and 64-token generation
- two GPU K24 READY and 64-token generation with MTP
- full prefill/verify/graph/reuse integration correctness
- same GGUF llama.cpp greedy/top-token parity
- 32K and 128K needle
- speed only after correctness

## Current winners

```json
{}
```

## Excluded runs

```json
[]
```

## Next exact action

Study native Q8_0 per_layer_token_embd.weight handling in PleTable (src/kernels/ngram.cpp:208). Current requested routed-expert fallback is implemented and unit-tested; do not bypass PLE, change weights, or claim Q5 working.

Scope: semantic CPU fallback, smoke and correctness before any speed benchmark.
