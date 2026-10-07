# Frozen v0.1.39 / PR578 integration audit

Main: `6f32ec070f23ced9f50e704d854d775da52591ab`. PR head: `b28121ff6ef117bec2558b3ece7e188dd33a2b7e`.
GitHub closed PR without a merge marker; upstream contains it at `4d20d25925374a9a3da7bb0e37e2aa4868d7e7bd`.
The four helper implementation/header files match original PR at integration exactly.
Preserve upstream #646 verifier/doorbell changes. No second merge or conflict resolution.
CONTROL and PR578 checkouts use identical source HEAD. Compare `--remote-expert-opt` absent/present;
this is a controlled same-base algorithm A/B, not a historical v0.1.38 vs v0.1.39 claim.

Complementary caches, helper same-layer adaptation, weighted GPU reduction, lazy CPU activation
quantization and helper `auto` sizing are present. Helper uses pinned host transport, no P2P required.
It requires serve mode, profile/cache/CPU pool and visible CUDA helper tiers enabled in order.
`--peer-device` is incompatible with helper caches and layer split. On our two cards, helper and split
are alternative topologies. Up to three helpers are coded; only dual CUDA is in this campaign.
With one helper stripe/layer select the same resident list; do not claim a placement optimization.
Suffix lookup CLI is `--suffix-draft 0`. MTP4/min-p0.5, INT8/kv-resident32768, workers15,
max-context262144 are frozen from saved valid IQ3_S configuration. Literal old payloads retained.
Every measured 256-output replay requires actual31400/reuse0/generated256; early stops remain invalid.

Fresh helper capacity discovery is mandatory. Never reuse old physical auto capacities as if they
were current v0.1.39 sizing. Determine numeric CLI budget separately from physical primary slots.
Original/optimized comparison must verify same primary/helper physical capacity, initial count,
and initial sets/overlap before equal64-output warmup. Boundary diagnostics absent in current main:
if needed, add default-off request-boundary instrumentation in a separate local commit only after
preserving clean upstream binary/results. Request-end cache enumeration is OFF for headline timing. The startup-only instrumentation study failed the <=1% gate (observed3.43% difference across three fresh servers/arm), so all headline measurements use the preserved unmodified upstream binaries without debug. Initial capacities are logged directly; initial count/overlap derives from the deterministic constructor and is independently observed in separate diagnostic runs. Full request-end snapshots remain diagnostic-only.

The previous full report is preserved at ../pr578-dual4090/report.md. Its headline numbers are
HISTORICAL / NOT_CONTROLLED_A_B with this refreshed release. Measurements are now in progress; see STATUS.json for completed phases. Existing cumulative CPU fallback/cache/activation-quantization counters are optionally printed after the native decode clock stops; this adds no hot-loop counter. The diagnostic overhead A/B also checks this request-footer output. Exact quantization-skip and all adaptation-swap totals remain unavailable.

Backend/combination precision: `CMakeLists.txt:248` uses the shared GPU engine
under CUDA OR HIP; remote_experts.cpp and remote_expert_opt.cu are in that engine
at lines417-418. This campaign validates NVIDIA/CUDA only; HIP correctness and
performance are NOT validated here. Layer split can coexist with helpers only
if another visible GPU runs no split stage (`generate.cpp:1696`); with two GPUs
both occupied by split, no helper remains. `--peer-device` explicitly rejects
split or remote caches (`generate.cpp:1911`). `--remote-expert-opt` requires
serve (`generate.cpp:1905`). Helper slots must be contiguous device1..3 and
nonnegative; a nonempty primary cache/profile and CPU pool are required.

Transport statistics precision: the returned byte fields are derived from the
normal footer rounded to0.1MiB, not a byte-exact hardware traffic counter. The
"with full rows" number includes ALL routed entries for the layer window,
including entries not computed on the helper. It must not be interpreted as
actual original-helper traffic for the same helper routing.
