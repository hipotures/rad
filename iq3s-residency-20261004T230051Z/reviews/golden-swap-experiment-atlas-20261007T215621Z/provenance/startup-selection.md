# Exactly how startup residency was selected

There are two initial states. **Process fill** happens before saved warmup and native prefill. **Decode initial state** is the recorded tape/trace snapshot after those operations, before the measured request's routed work. The Atlas retains both. The tape snapshot, not a hypothetical fresh profile fill, initializes every reconstructed timeline.

The pinned Q4 profile is `/srv/ai/strata/data/expert-profile.bin`, 196,632 bytes, SHA256 `8f59b4aa8873209dff11c11e37bcda9529a1335b724a1afeea37bf6388975baf`. Its 24,576 ranked `(layer, expert)` pairs are exported losslessly as text. This profile identity agrees with the original Q4 characterization and Phase 0's model identity. The historical routing dataset that originally produced this file is not attested. Calling it a learned Q4 ranking would exceed the evidence.

The inspected Phase 4 derivative is `95fba2541a57fe6be8290faa639f493c7b8e895f`; its upstream serving base is Strata 0.1.39, `6f32ec070f23ced9f50e704d854d775da52591ab`, from <https://github.com/Niko1221/Strata>. [startup-code.json](startup-code.json) preserves exact source excerpts, line numbers, file hashes, and base/derivative equality checks. The campaign patches and reconstruction instructions preserve the experimental additions separately.

1. `src/core/expert_cache.cpp:23–78` reads the STRP header and ranked pair sequence. It preserves file order; it does not recompute heat or sort these pairs.
2. `src/program/generate.cpp:2647–2692` loads that sequence. Its peer-hot redistribution branch requires the peer/helper device configuration. The studied K24 layer split does not activate this branch. Per-layer cache partitioning and profile-save ranking are also inactive in the relevant Q4 launch arguments. Defaults at lines 373–409 explicitly set `expert_cache_per_layer=false`, `peer_device=-1` and an empty profile-save path; lines 1905–1920 reject peer mode with layer split. The Atlas records the exact per-request inactive options rather than inferring this from an unused branch.
3. `generate.cpp:2850–2874` filters pairs by layer ownership while preserving their relative order: GPU0 owns layers 0–23; GPU1 owns 24–47. A high-ranked expert on GPU1 cannot occupy a GPU0 slot.
4. `generate.cpp:3200–3322` derives the ordinary free-memory capacity after weights, session/KV, heads and reserves. With a native pack and profile, it walks the device's ranked prefix, charging the actual layer blob size aligned to 256 bytes. It **stops** when the next blob exceeds the byte cap. It does not skip the expert to find a smaller first-fit candidate. The cap is the minimum of the uniform grant and actual free room after reserve.
5. `generate.cpp:3455–3554` loads those experts from immutable RAM, assigning successive device-local slots. GPU1 applies its own stage-room bound and file-order prefix. There is no random tie break at fill: the file already supplies a total order.

For the common 32K Q4 profile, the attested ordinary physical capacity is:

| Device | Layer ownership | 3,072,000 B | 3,584,000 B | 3,993,600 B | Total slots |
|---|---|---:|---:|---:|---:|
| GPU0 | 0–23 | 5,502 | 233 | 296 | 6,031 |
| GPU1 | 24–47 | 4,855 | 655 | 0 | 5,510 |

The 128K and 256K repository trajectories have smaller attested capacities. The Atlas reads each initial slot map instead of imposing the 32K count. It checks profile-prefix size-class counts against that run's physical classes before labeling process fill reconstructed. It does not claim to have observed prefill routing merely because a process-fill reference can be rebuilt. The old IQ3_S/K25 predecessor retains an exact decode snapshot, but no matching immutable startup profile revision is attested here; its process fill remains unknown.

The five Golden Swap spares do not add capacity or change ordinary startup loading. `include/strata/research/q4_oracle.hpp` withdraws one already resident donor in each active device/class at the measured request boundary: three on GPU0, two on GPU1. Their total payload is 17,305,600 bytes. Donor selection depends on the arm's declared victim rule and common privileged protection. CURRENT keeps ordinary full capacity. The Atlas records these withdrawals separately from ordinary promotions and restores no fictitious post-request service. Mandatory restoration is charged in the original request accounting, outside the observed routed timeline.

## Where the file's order might have come from

`tools/make_profile.py:66–90` keeps an existing base order by default and appends trace-ranked missing pairs. If the base already contains all pairs, new trace counts do not reorder it. Explicit `--reorder` or `--no-base` ranks trace frequency descending, ties by `(layer, expert)`, then fills missing pairs in expert-major/layer-minor order. These are possible creation paths, not evidence that one particular command produced the frozen shared file.

`rank_learned_profile` in `src/core/expert_cache.cpp:81–109` is a **save/output** path: resident first, heat descending, prior rank, flattened identity. It is not the startup load path. The studied launch configurations do not enable profile saving. Historical measured heat affects native adaptation after fill; it does not silently replace the ranked startup sequence.

## The visual quality comparison

Startup charts distinguish demanded identities from actual local service before the initial generation was withdrawn. They retain never-observed demand, eviction before use, subsequent reload, uninterrupted generation survival, initial-identity return, and set Jaccard separately.

The selected-layer full-tape frequency reference has exactly the same layer slot count and blob class, ranks total observed lane demand descending, and breaks ties by expert ID. It is a retrospective static reference, not a feasible full-oracle schedule or a measured speedup. A profile resident that is never requested on this finite tape is an observed poor match to this request, not proof it is globally useless.
