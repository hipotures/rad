# Strata v0.1.32 release audit — source and compiled help verified

Exact tag `v0.1.32`, commit `c499bd102e7a4135c0de389dcfe38c399759ccc8`. Previous checkout remains at `9259cad4cfa3543cd3b8decab5962672b968c649`. Release fetched with `gh api repos/Niko1221/Strata/releases/tags/v0.1.32`, preserved in evidence/release.json. Documentation and CMake snapshots are in evidence/. No release claims below are measurements on our4090 pair.

| Change | Frozen source evidence | Effect on campaign |
|---|---|---|
| Concurrent split prompt refill | src/program/generate.cpp:5055–5083, refill issue/wait operations; release notes describe refill across all cards concurrently | Controlled default A/B at8/16/32/64/128/256K; includes wall time/refill overhead |
| Smaller prompt staging ring for split | generate.cpp:2270–2276 and:3835–3844; split ring96blob logic | Read actual resource allocation from each startup; do not assume v0.1.31 slot counts |
| Unsloth prompt I/O concurrency | docs/UNSLOTH_Q4.md: larger stager thread/ring defaults for native file-backed Q4 | Most relevant when experts do not fit RAM; full-arena results may differ from release's64GB SSD-bound PC |
| Q4_K/Q5_K/Q5_1 prompt MMQ | **CMake `STRATA_MMQ_KQUANTS`**, defaultOFF, CMakeLists.txt:38–41 and:858–889 | Separate build-default and build-q4-fast. FlagON adds q4_k,q5_k,q5_1 template instances and upstream numerical test. It can consume extra VRAM; fastest choice requires resident64K A/B, not speculation |
| Larger auto prompt chunks | generate.cpp:330–331,:1125–1126,:3734,:3873; `--prefill auto:32768` | Defaultauto ceiling8192; opt-in ceilings16384/32768. Actual allocation may shrink; log actual chunk and loans. No promise32768 fits |
| Stage-owned prompt buffers | generate.cpp:1350–1385, `STRATA_SPLIT_OWN=1` | **NON_BIT_IDENTICAL_OPT_IN**. Default unset/0 borrows; explicit1 uses own buffers. `auto` applies reserve/VRAM rule. Test separately; do not mix with defaults |
| No prompt borrow | parser generate.cpp:1129, reserve accounting:2270 | `--no-prefill-borrow` supported on split; reserves permanent buffers, changing available expert cache. Evaluate separately at64/128K |
| Rotated INT8 KV | generate.cpp:1462–1468, `STRATA_KV_ROT=1` with `--kv int8` | Separate candidate from ordinaryINT8; opt-in may change output. Existing KV choices fp16/int8/k8v4/q4_0 still checked; k8v4+kv-resident remains rejected |
| Coupled draft sampling | generate.cpp:265,:561–562,:1102–1103 | `--coupled-draft` / `--no-coupled-draft`, env STRATA_SPEC_COUPLED. Audit policy source before use; do not silently change sampled long/agentic semantics |
| Other options | help source lists pool-affinity; release notes mentionBF16 projections,RoPE precision,embedding,FP8PLE | These are opt-ins and possible parity changes; not enabled implicitly. No experimental-speed-projection |
| Resident multi-GPU restriction | generate.cpp:1319–1335 | Guard still rejects resident-cpu-experts with layer split/remote caches. Full RAM ArenaExpertSource uses neither resident flag nor mmap and remains the supported target |

Setup explicitly supports `--family unsloth --model UD-Q4_K_XL` and `--gguf-dir`. setup.py:2508–2522 bypasses model download with localshards;:2604 uses iq_pack.py with --compat-bf16. Setup itself chooses oneGPU for Unsloth; direct runtime layer-split is a distinct tested path. Existing local GGUFstat identity matches prior verification; no download is authorized. Setup/MTP discovery and potential writes must be inspected before invocation so oldpack/MTP remain intact.

Packer diff versus0.1.31 changes experts.bin reuse validation only (six native blobs checked); native_experts.txt/tokenizer/dense compatibility packing path has not changed in that diff. Native existingpack can be reused read-only. If officialsetup needs its own pack path, use an independentv0132 destination; never overwrite0.1.31 pack or createexperts.bin for Q4.

Compiled --help from both variants is preserved in evidence/help-default.txt and help-q4-fast.txt. Both binaries contain exact engineversion0.1.32. Q4-fast **failed** upstream prefill_mmq_kquant_test: Q4_K gate/up-1 unwritten or non-finite output; first four synthetic formats passed, later test failed. No engine patch, no Q4-fast model request and no claim of actual-model corruption. Default build selected under the correctness/abort gate; requested speed A/B cannot be validly performed on the rejected candidate. Raw evidence: raw/q4-fast-kernel-test.json and raw/builds-terminal.json.

Independent nativepack prepared with iq_pack.py --compat-bf16, no experts.bin. ExistingMTP copied and verified. Officialsetup --gguf-dir completed with an isolatedXDG_CONFIG_HOME after its globaldata migration was detected and reversed; originalQ4inode/size/mtime identities reverified. Evidence: raw/setup-relocation-recovery.json and raw/local-setup-terminal.json.

Coupled draft defaults OFF unless STRATA_SPEC_COUPLED is set; include/strata/core/coupled_draft.hpp:52–59. No coupled flag is silently enabled. No benchmark speed/parity conclusion is inferred from release notes.
