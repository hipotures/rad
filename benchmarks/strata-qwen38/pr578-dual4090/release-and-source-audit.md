# Frozen source audit

Fetched GitHub PR body, commits, diff, review comments and issue comments via `gh api` on 2026-10-03. PR578 open, mergeable/clean, head b28121ff6ef117bec2558b3ece7e188dd33a2b7e. Main/base 99f3dbd0b21d1401b3769e0c0d963913607f380b; latest release v0.1.38. Local merge has no conflicts. Main frozen for whole campaign.

`RemoteExpertOpt::owns()` excludes helper residents from primary adaptive candidates. `RemoteExpertOpt::adapt()` excludes current primary, pending primary admissions and all helper residents from candidates; same-layer cold helper victims are replaced by CPU misses with usage>=2 and gain>=1.5. This is per-layer capacity preservation, not repartitioning.

Helper GPU reduction sums weighted expert rows into one H-dimensional partial vector per token. `reduce()` transfers n_tok*H*sizeof(float), instead of owned_rows*H*sizeof(float). Transport remains pinned host memory; primary combines the partial sum. No P2P/NVLink requirement. It changes FP summation order.

CPU activation quantization is skipped if optimized helper mode is active and all token's routed kinds are nonnegative. No quantization-skip counter exists. We do not add a hot-path counter.

Helper auto sizing uses actual per-layer aligned expert bytes and free VRAM with512MiB reserve. Explicit budgets continue to work. Up to3 helpers supported structurally; only dual CUDA measured by author. CUDA implementation not validated on HIP.

--remote-expert-opt requires --serve. Helpers require expert-profile, primary cache and expert pool. --peer-device excludes layer split and helper caches. Layer split with helpers needs additional GPUs not occupied by stages; with2 GPUs it cannot combine layer split and helper.

Single-helper `stripe` and `layer` both bypass multi_remote placement branch and use identical ranked list. Therefore duplicate placement sweep is omitted as semantically identical. Multi-helper placement cannot be tested on2 GPUs.

--suffix-draft0 genuinely disables suffix lookup. Main suite OFF; secondary production suite ON with default3. MTP spec4/min-p0.5, same local MTP directory and INT8 KV with resident32768 are preserved. Pool-workers explicitly15 (old effective15+host) for all variants. --pcie-frac auto remains LS-A/default; LS-B explicit0.28 is a separate one-variable test.

Published benchmark values are in PR body only. PR adds no author's request corpus or benchmark script (diff11files, implementation/docs only); no reproduction of author workload claimed. IQ3_S is our workload.

`--dump-logits` exists, but writes in non-serve per-token loop; remote-expert-opt rejects non-serve and native-pack fast path does not reach that dump. Therefore no easy comparable optimized-helper teacher-forced KL/top1 dump. Correctness records actual protocol-generated token IDs, first autoregressive divergence and positional agreement; it does not label positional agreement teacher-forced top1.

Local instrumentation is boundary-only and default-off: startup and completed-request cache set snapshots. It is identical on both branches in separate commits. No dispatch/cache policy change, no new per-token quantization counter. Existing logs already provide helper computed entries, returned MiB, host wait/staging, CPU entries/misses, primary hits, PCIe expert count and verifier timing. Set differences give net resident changes; they cannot recover all transient adaptation swaps.

Fairness capacity detail: primary auto initially grants6567uniform maximum-blob budgets, converted to8586variable-sized actual slots. Passing8586as --expert-cache would enlarge the byte budget. Numeric controlled variants therefore use --expert-cache6567 and --expert-cache-device111796, producing exactly8586/11796actual initial slots. This preserves capacity rather than matching misleading CLI numerals. Both have20382initial residents and zero overlap; initial exact IDs are captured beforewarmup.

All headline speed runs have STRATA_BENCH_CACHE_SNAPSHOT unset. Boundary snapshots are diagnostic only; an OFF/ON diagnostic repetition will estimate overhead. No speed attribution relies on enabling instrumentation.

Transfer interpretation: upstream's "full rows" baseline is all10routed rows per token, not the original helper's already-packed actual owned rows. Use actual original returnedMiB, optimized returnedMiB and actual helpercomputedentries. Weighted reduction can reduce bytes per sameowned-entry group while total request returnedbytes rises as complementary caches leave more hot work on helper. Never claim wholePCIe decrease from a lower fractionof full-rowbaseline alone.

Boundary snapshots report committed hostresidency (pendingprimary admissions excluded); temporary primary_resident count below slotcapacity is not VRAM capacity shrinking. Helperresidency remains full. Netset differences are not totaladaptive swaps.

HIP precision: newremote_expert_opt.cu isaddedinsharedGPUengineCMakeblock, notbehindanexplicitCUDA-only CLIvalidation. HIP compatibility isnotverified here; docs stateonlyCUDAdual-cardvalidated. Do notclaimstrictHIPrejection withoutaHIPbuild.
