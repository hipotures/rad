# Compatible-slot source audit

Frozen source `6f32ec070f23ced9f50e704d854d775da52591ab`. This is a feasibility audit, not an implemented runtime claim.

`ExpertCache::open_sized` (`src/core/expert_cache.cpp`, around482) allocates immutable offsets for the physical size of each initial slot, aligned to256bytes. `include/strata/core/expert_cache.hpp` explicitly describes the existing same-layer policy. Any new incoming expert must fit the actual slot extent; merely checking total bytes is unsafe.

Serve decode builds the routing plan from `host_res`, `cache_base` and `cache_slot_off` (`src/core/expert_source.cpp`, around2035). Its native kernel format is selected by the actual routed layer. A correctly populated compatible slot can in principle hold a different layer's format; its bytes and kernel must describe the incoming expert. Slot offsets remain fixed.

The server's `apply_pending` (`src/program/generate.cpp`, around5468) waits on each owner's existing event, then publishes the incoming `(layer,expert)->slot` and uploads the residency table to each device. The previous reader windows have completed before adapt copies issue. An extension must keep those safety boundaries, reject duplicate slot assignments and withdraw the correct outgoing layer immediately.

The current `Swap` lacks an outgoing-layer field. Its copy/refill/prefetch addresses assume a same-layer victim. A cross-layer candidate needs explicit outgoing identity. `resident_stage_swaps` assumes a same-layer RAM-complement exchange; the experiment must reject resident-CPU/complement mode and retain the full immutable RAM arena, so no expert needs a reverse copy to RAM.

The prompt loan marks entries from dynamic `host_res` inside the owner's layer range and saves `(residency-index,slot)` (`generate.cpp`, around6825). Refill reads the blob and its format/byte count from that saved incoming expert (`generate.cpp`, around6744); it does not require the initial expert at that slot. Prefill compute likewise uses the dynamic table (`src/prefill/prefill.cpp`, around2299/2809/2846). This supports cross-layer identity inside one owner in principle, but a live candidate must exercise warmup, multiple requests and loan restoration, including rejected MTP rows.

`ExpertCache`'s own initial residency metadata is stale even under the existing serve adaptation; the serve graph/prefill explicitly uses `host_res`. Elastic resize and learned-profile persistence have additional assumptions. The bounded candidate must reject elastic/batch/helper/peer/complement combinations rather than advertise them as tested. MTP uses separate draft weights; actual router-selected experts still execute without substitution.

Cross-GPU placement is not covered by this policy. K25 remains fixed and a victim is eligible only inside the same owner's physical cache. No P2P or freely shared48GiB pool is assumed. The incoming immutable weight blob comes from existing host RAM; asynchronous copy is published only after completion.
