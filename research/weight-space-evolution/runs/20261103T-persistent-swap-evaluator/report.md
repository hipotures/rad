# Persistent weight-swap evaluator — transition integrity and cost (Workstream B)

Run ID `20261103T-persistent-swap-evaluator`; configuration in [protocol.json](protocol.json); compact results in
[results/swap_tests.json](results/swap_tests.json) (round 1) and [results/swap_tests_r2.json](results/swap_tests_r2.json)
(round 2). The full-cycle throughput of the evaluator inside the benchmark loop is reported separately in
[../20261103T-phaseD-v2-e2e/report.md](../20261103T-phaseD-v2-e2e/report.md).

## Question

Can a long-lived vLLM engine (one per GPU) move between Gold and arbitrary candidate patches and back without a
restart, with every visited state producing **the same token ids as a freshly started engine on the same weights**?
What does each transition method cost?

## Implementation

- `code/wse/vllm_ext.py` — a vLLM worker extension (`worker_extension_cls`) with four RPCs: parameter inventory,
  sha256 fingerprints of selected runtime parameters, worker memory, and `wse_apply` (sparse write of BF16 values at
  flat indices; it checks every touched tensor's hash before the write and after it, and rolls back on mismatch).
- `code/wse/swap_engine.py` — `PersistentEngine` with three modes:
  - **direct**: the transition spec is the sparse difference between the current and target state (union of
    tensors touched by either patch), so Gold→A, A→B and A→Gold are all single sparse writes. Only tensors whose
    runtime storage is byte-identical to the checkpoint can be patched this way (164 of 248 runtime parameters,
    including all `down_proj`, `o_proj`, `out_proj` and the embedding; measured by comparing the runtime fingerprint
    with the checkpoint). Patches touching a fused (`qkv_proj`, `gate_up_proj`, `in_proj_qkvz`, `in_proj_ba`) or
    load-time transformed tensor (`linear_attn.norm.weight`) automatically fall back to **reload**.
  - **reload**: the candidate is exported once to `work/derived/candidates/<patch id>/` and loaded with
    `collective_rpc("reload_weights", weights_path=…)`.
  - **restart**: a new engine per state (the reference).
  After every transition the prefix cache is reset and the touched patchable tensors are verified against the
  expected target hashes; tensors that cannot be fingerprinted against the checkpoint are counted as
  `unverifiable_runtime_tensors`. Transitions are refused while requests are in flight. A full-runtime Gold
  fingerprint audit (all 248 parameters, ~1.1–1.3 s) runs periodically and at the end of every worker.
- Population (`configs/phaseD_v2/editor_population.json`): p50c, p25c, p10c (upstream), 4 random directions with
  p50c's per-tensor norms, 3 random sparse patches, 1 random patch touching `gate_proj` (forces reload), and a
  chained child of p50c (lineage test).

## Tests

`code/scripts/run_swap_tests.sh`, both GPUs concurrently: GPU0 runs the direct sequence and then random extended
cycles; GPU1 runs the restart sequence (the fresh-engine reference for every state) and then the reload sequence.
Sequence: `gold,p50c,gold,p25c,p50c,gold,p10c,rand-dir-0,rand-fused,chain-p50c,gold`. For every visit, three cases
run on 144 Phase D v1 prompts: greedy (64 tokens), sampled (T 0.7, top-p 0.8, n 4, seed 0, 256 tokens) and
constrained (sampled with structured outputs). Identity means the token-id hashes of all requests match a fresh
engine visit of the same state.

## Results

### Round 1 (prefix cache reset only at transitions) — negative result kept

| mode | greedy identical | sampled identical | constrained identical |
|---|---|---|---|
| direct | 11/11 | 6/11 | 5/11 |
| reload | 11/11 | 5/11 | 4/11 |
| restart (fresh vs fresh) | 6/6 | 4/6 | 4/6 |

Fresh engines did not agree with each other either (sampled mean agreement 0.62). So the mismatch came from the
engine, not from the swap. `code/wse/determinism_probe.py` (raw `det_default.json`, `det_profile3.json`) isolated
the cause. The same sampled batch repeated on one engine gives the same hash whenever the prefix cache is reset
first (steps 0, 1, 2, 7). The hash changes when the batch runs on a warm cache (steps 4, 6), and that holds for
greedy decoding too (step 5 ≠ step 3). It holds under both vLLM defaults and profile3. Cache hits change prefill
chunking and batch composition, so BF16 reductions run in a different order. `VLLM_BATCH_INVARIANT=1` is not an
option: vLLM 0.33 rejects it for the GDN attention used by Qwen3.5 ("batch_invariant mode is not supported for
GDN_ATTN"). The evaluator therefore resets the prefix cache before **every** `generate()` call. That is now the
default in `PersistentEngine.generate` and is part of the frozen benchmark protocol.

The round 1 extended run (74 random transitions, greedy only) had 62/62 revisits identical and 20/20 Gold audits
passing. Allocated memory stayed constant at 17 117 MiB.

### Round 2 (prefix cache reset before every generate) — primary result

| mode | greedy | sampled | constrained | Gold audits | memory (allocated) |
|---|---|---|---|---|---|
| direct (8 direct + 2 reload fallbacks) | 11/11 | 11/11 | 11/11 | 3/3 | 17 239 MiB constant |
| reload | 11/11 | 11/11 | 11/11 | 3/3 | constant |
| restart (fresh vs fresh) | 6/6 | 6/6 | 6/6 | 3/3 | constant |
| extended direct, 32 random transitions, all cases | 20/20 revisits | 20/20 | 20/20 | 5/5 | constant |

Every visited state was bit-identical to the fresh-engine reference on all three cases. Revisiting a state after
arbitrary intermediate states (e.g. Gold→p50c→Gold→p25c→p50c, chain-p50c after rand-fused) reproduced its outputs
exactly. Patches really change behaviour: greedy agreement with Gold is p50c 0.03, p25c 0.16, p10c 0.05,
rand-dir-0 0.72, rand-fused 0.66, chain-p50c 0.03.

### Transition cost (round 2, per transition)

| mode | median total | range | dominant phase |
|---|---|---|---|
| direct, small patches (p50c, p25c, Gold restore; 0.13–0.39 M entries) | 0.04–0.16 s | | patch preparation ~0.02–0.06 s, apply ~0.02 s, verify ~0.01 s |
| direct, dense patches (p10c, rand-dir-0; ~73 M entries in 30–31 tensors) | 1.3–3.1 s | | preparation (diff computation on the host) 0.6–2.4 s; apply 0.5 s |
| reload (exported candidate) | 0.21–0.25 s | up to 2.0 s | `reload_weights` ~0.2 s; verification of 30 dense tensors 0.09 s; the first visit also exports (~2.7 s) |
| restart | 19.2 s | 16–23 s | engine construction, CUDA graph capture and compilation |

Direct patching and reload are both **≈ 80–500× cheaper than restart**. Direct is the fastest for the sparse patches
expected from editors. For dense patches reload is as fast or faster once the candidate is exported, so both stay
available. Round 1 numbers agree (direct 0.06 s median, reload 0.21 s, restart 27 s with a busier host).

## Interpretation and limitations

- **Established:** with the prefix cache reset before each batch, a persistent engine in direct or reload mode
  produces exactly the token ids a fresh engine produces for the same state, over long random transition sequences,
  with constant memory and passing full Gold audits. Restart is therefore unnecessary for correctness.
- **Limitation:** byte-level verification covers the 164 checkpoint-identical runtime tensors. Fused/transformed
  tensors are reloaded by vLLM's own loader and verified only through output identity (rand-fused and chain-p50c
  visits were identical to their fresh references); their storage hashes are not compared with an independent
  reference.
- **Limitation:** identity is guaranteed only for the same engine configuration, batch and prompts. Different engine
  profiles give different (equally valid) outputs: default and profile3 hashes differ. Primary comparisons must keep
  the profile fixed. Batch invariance across different batch compositions is not available for this architecture
  in vLLM 0.33.
- Tested on one model (Qwen3.5-0.8B), BF16, single-GPU engines; tensor parallel engines were not tested.

## Reproduction

```bash
cd research/weight-space-evolution
CAMPAIGN=20261103T-persistent-swap-evaluator P=r2_ EXT=32 EXTSEED=1 EXTFULL=--ext-full code/scripts/run_swap_tests.sh
(cd code && ../work/envs/wse/bin/python -m wse.swap_analyze --raw ../work/raw/20261103T-persistent-swap-evaluator --prefix r2_ \
   --out ../runs/20261103T-persistent-swap-evaluator/results/swap_tests_r2.json)
code/scripts/run_determinism_probe.sh
```

Raw per-visit records: `evidence/20261103T-persistent-swap-evaluator/` (gzip copies of `work/raw/<campaign>/`).
