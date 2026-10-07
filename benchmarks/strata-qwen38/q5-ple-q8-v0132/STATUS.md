# Strata v0.1.32 — Q8_0_PLE_AND_SMOKE_PASS

## Running

```json
null
```

## Completed

- native Q8_0 PLE mmap: 170-byte rows, native decoder, larger buffers, format reporting
- real Q8_0 PLE probes/issue-collect/bulk reads vs ggml: max_abs 0
- 7/7 regression CTests
- Q5 single GPU READY + 64-token smoke with MTP
- Q5 two GPU K24 READY + 64-token smoke with MTP
- CPU-only layer 2 and GPU hits on supported layers observed

## Pending

- whole-model same-GGUF llama.cpp greedy/top-token parity
- 32K/128K needle
- long-context correctness/stability
- speed only after correctness

## Current winners

```json
{}
```

## Excluded runs

```json
[
  "initial load with default direct PLE I/O failed: Q8_0 requires mmap; preserved raw/logs"
]
```

## Next exact action

Correctness stage: prepare same-GGUF llama.cpp parity and 32K/128K needle. Current Q8_0 PLE addition and smoke validation completed; no process running.

Scope: semantic CPU fallback, smoke and correctness before any speed benchmark.
