# Qwen3.8-Flash-Next GPU-resident MTP investigation

**Result: NO-GO in the required current runtime.**

The exact runtime at commit `250b61446efc91e3a179c8677956f2667c8fbda0`
cannot load an architecture-correct Qwen3.8-Flash-Next MTP sidecar. The controlled
32K probe, with the fixed target placement and `-ngld all`, failed before
inference because the Qwen4Exp handler asked the sidecar for the target tensor
`blk.0.hc_attn_norm.weight`. The true MTP block is stored as block 48 plus
`nextn.*` tensors. This activates the required early-stop rule, so no formal A/B,
acceptance benchmark, or speculative throughput claim is valid.

## Scope and reproducibility

- Target: `/srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-IQ4XS/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00003.gguf`
- Runtime: `/srv/ai/llama.cpp-qwen4exp/build-cuda-sm89/bin/llama-server`
- Binary SHA-256: `4de7b5535feb468f79f3fa83f9d0f7eef22e11be3a73cce9027ffe1ad8fe5242`
- Source commit: `250b61446efc91e3a179c8677956f2667c8fbda0`
- Formal context: 32768
- Target override: `per_layer_token_embd\.weight=CPU,blk\.([0-9]|2[4-9]|3[0-3])\.ffn_(up|down|gate|gate_up)_(ch|)exps=CPU`
- Tested sidecar: quimmedes Q4_K_M, revision
  `fb84e51f3777024a5d0cef40c95e9c4df6b7a4b4`, SHA-256
  `4563303ab6e7d40f409750fd48af76bf33dd76b0773951cbf484109107de8140`
- Test flags: `--spec-type draft-mtp --spec-draft-n-max 3 --spec-draft-p-min 0.75 -ngld all`

The exact command is in `commands/README.md`; the complete output is in
`logs/mtp-loader-probe.log`. The target placement was not tuned or changed.

## Direct answers

### 1. What exactly is the MTP drafter?

It is one separately trained Lightning MTP decoder block. It consumes the
target's 10240-wide four-stream hyperconnection state and the current token
embedding, combines them through `nextn.eh_proj`, runs one sparse-attention/QSA
plus MoE block, and produces draft logits and a successor hyperconnection state.

### 2. Small module or another target-like model?

It is a small module relative to the 48-block target, not a second full target.
It is not a cheap linear head: its single block includes sparse attention and a
512-routed-expert MoE plus a shared expert. Whether it is cheap enough depends on
GPU placement and avoiding host state staging.

### 3. What tensors does it contain?

The complete quimmedes artifact has 35 tensors:

- `token_embd.weight`, `output.weight`, output HC norm/down/up;
- block 48 attention Q/K/V/output and Q/K norms;
- block 48 QSA indexer Q/K projections and norms;
- router, 512 routed expert gate/up/down tensors, and shared-expert gate/up/down;
- attention and FFN HC norm/down/up/inject tensors;
- `nextn.eh_proj`, `nextn.enorm`, `nextn.hnorm`, and
  `nextn.shared_head_norm`.

Exact names, shapes, offsets, and types are preserved in
`metadata/quimmedes-mtp-gguf.json`. Types are mixed Q4_K, Q5_0, Q6_K, Q8_0,
BF16, and F32.

### 4. How large is it?

- quimmedes Q4_K_M: 2,786,245,792 bytes (2.595 GiB), 35 tensors;
- dzannotti Q4_K_M: 2,622,313,344 bytes (2.442 GiB), 34 tensors;
- native BF16 sidecar: approximately 7.77 GB from repository metadata.

The public Jundot artifact is an integrated approximately 100 GB oMLX target,
not a current-llama.cpp standalone sidecar; it was inspected remotely rather
than downloaded.

### 5. Can the complete draft path remain GPU-resident here?

**Not in the current runtime.** The loader fails before draft tensors are
placed. Even after adding the missing Qwen4Exp graph, the current generic MTP
orchestrator keeps `pending_h`, `verify_h`, and `chain_h` in host
`std::vector<float>` storage and copies state rows through CPU memory. Thus
`-ngld all` could make the weights GPU-resident, but would not make the complete
draft path GPU-resident.

### 6. Does drafting invoke CPU-resident target experts?

No draft was executable. Source-level answer for the intended path: each draft
step calls `llama_decode(ctx_dft)`, so it would execute the sidecar's own MoE,
not the target's CPU-offloaded expert blocks. The target CPU experts still run
during batched verification. This is a fact about the generic orchestrator, not
an observed Qwen4Exp runtime measurement.

### 7. Does drafting invoke PLE?

No in the architecture-correct public implementation: the MTP configuration has
an empty PLE layer list. Target PLE runs during target verification, not inside
the standalone MTP block. Again, the current llama.cpp never reached drafting.

### 8. Does drafting add PCIe traffic per draft token?

The current generic llama.cpp implementation would. A 10240-element FP32 state
row is 40,960 bytes. `llama_get_embeddings_nextn[_ith]()` exposes/copies that
row to host vectors, after which `memcpy` places it in a host draft batch for the
next decode. On a GPU graph this entails device-to-host extraction,
synchronization, and host-to-device batch upload for each chained draft step.
This is distinct from rerunning the target CPU MoE: it is host staging of the
MTP state itself.

### 9. How much extra VRAM does MTP require?

Not measurable in this runtime: tensor construction failed before placement.
The 2.595 GiB file size is not reported as VRAM usage because quantized tensor
padding, split placement, graph buffers, caches, and temporary allocations differ
from disk size. After exit both GPUs were at 1 MiB used / 24082 MiB free.

### 10-12. Acceptance and accepted length

Temperature-0 acceptance: **N/A — blocked before inference**.

Reasoning-workload acceptance: **N/A — blocked before inference**.

Mean accepted length: **N/A — blocked before inference**.

Reporting these as zero would be misleading: no draft attempt occurred.

### 13-15. Throughput and speedup

Target-only TG, effective MTP TG, and real speedup are all **N/A**. The protocol
requires a formal same-target A/B only after establishing a credible MTP path.
The loader failure established the opposite, so the early-stop rule prevented a
meaningless target-only run and hours of structurally irrelevant tuning.

### 16. Is output correct?

Not testable: the MTP server exited before listening and produced no tokens.
There was no crash during inference, but loader rejection is not correctness.

### 17. Why can the public implementation report high acceptance?

The public oMLX implementation has the model-specific graph that is missing
here: it exports the target pre-head hyperconnection state, chains the trained
MTP block's state without rerunning the target, verifies candidates in one target
call, and restores/trims recurrent and attention caches on rejection. It also
uses a moving-average controller that selects depth by estimated acceptance and
cost. Current llama.cpp's `p_min` is a confidence threshold, not the same adaptive
controller. It is a reasonable inference—not proof—that near-100% acceptance in
the public result also depends on the jointly trained native head, greedy or
predictable prompts, and workload selection.

### 18. What source/runtime limitation remains?

There are two layers of work:

1. **Immediate functional blocker.** Enable Qwen4Exp MTP conversion and teach
   the loader to map block 48 / `nextn.*` as a one-block draft model rather than
   requiring target blocks 0-47. Add a Qwen4Exp MTP graph that consumes a token
   plus the 10240-wide target state, exports the next MTP state, and preserves
   the model's recurrent/QSA/HC semantics across verify, rejection, and rollback.
   The local dzannotti patch illustrates this but does not apply cleanly to the
   audited commit and was not silently installed.
2. **GPU-residency blocker.** Replace host `pending_h` / `verify_h` / `chain_h`
   staging in `common/speculative.cpp` with backend tensors and device-to-device
   handoff, or fuse/chains drafts in a GPU graph. Sampling/control should remain
   backend-side where possible. Only then can startup placement logs and
   telemetry prove that no per-draft PCIe round trip remains.

The immediate failure is the incorrect target-style tensor load. Once that is
fixed, the exact operation pulling the draft path onto the host is the
`llama_get_embeddings_nextn[_ith]()` to `std::vector<float>` extraction followed
by `memcpy` into `batch.embd` before `llama_decode(ctx_dft)`.

## Required result table

| Workload | MTP | TG tok/s | Speedup | Draft acceptance | Mean accepted length | VRAM 0/1 | CPU | Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---|
| deterministic | off | N/A | 1.00x reference only | - | - | N/A | N/A | baseline not run after early stop |
| deterministic | on | N/A | N/A | N/A | N/A | no allocation | N/A | blocked before inference |
| reasoning | off | N/A | 1.00x reference only | - | - | N/A | N/A | baseline not run after early stop |
| reasoning | on | N/A | N/A | N/A | N/A | no allocation | N/A | blocked before inference |

## Core decision

**NO for the audited runtime.** Qwen3.8-Flash-Next MTP is architecturally capable
of avoiding the target's CPU PLE and selected CPU experts during draft steps,
but this binary cannot construct the drafter at all. Its generic MTP state path
also performs host staging per draft token, so it does not meet the requested
strict GPU-residency criterion even after the model handler is repaired.

There is therefore no valid deployment command to recommend. The executed
command is retained only as a reproducible failing probe. A new benchmark should
begin only after the loader/graph and device-resident state handoff changes above
land; it should then repeat this exact 32K target placement before considering
64K.

## Evidence and cleanup

- `source-audit.md`: detailed source and public-runtime execution audit;
- `mtp-artifacts.json`: candidate revisions, hashes, sizes, and compatibility;
- `metadata/`: complete target and sidecar GGUF metadata;
- `logs/mtp-loader-probe.log`: full runtime failure;
- `placement/mtp-loader-placement.txt`: requested and observed placement result;
- `experiments.jsonl`: machine-readable audit/probe/cleanup events;
- `telemetry/final-gpu.csv` and `telemetry/final-cpu.txt`: final release checks;
- `responses/README.md`: explicit record that no endpoint/response existed.

No test server remains. `pgrep -a llama-server` returned nothing, both GPUs show
0% utilization and 1 MiB used, and no unrelated process was killed by this
investigation.

## Public references inspected

- Qwen model documentation: <https://huggingface.co/Qwen/Qwen3.8-Flash-Next>
- Jundot working oMLX artifact: <https://huggingface.co/Jundot/Qwen3.8-Flash-Next-oQ4e-mtp>
- oMLX runtime: <https://github.com/jundot/omlx>
- dzannotti GGUF sidecar: <https://huggingface.co/dzannotti/Qwen3.8-Flash-Next-MTP-GGUF>
- quimmedes GGUF sidecar: <https://huggingface.co/quimmedes/Qwen3.8-Flash-Next-MTP-GGUF>
