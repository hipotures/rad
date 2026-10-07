# Normalized events and field provenance

Logical event is `window * 48 + layer`. Layer IDs, expert IDs, device-local slots and generations are kept distinct. One expert's later admission cannot receive service belonging to an earlier generation. All 48 routed layers remain present. Main routed lane entries include multiplicity; distinct service count counts unique expert appearances in separate layer invocations. MTP per-expert subdivisions are not available here.

Every run summary lists original files with SHA256 and byte size. The catalog links the original campaign/result/report; the provenance panel exposes those references. Generation and demand rows use a declared column array to avoid repeated object keys. Exact layer payloads are downloadable; display rolling bins do not alter them.

| Field | Authority / derivation |
|---|---|
| run/task/arm/model/runtime | Original result row, per-request config, model manifest; missing runtime identity stays null. |
| device/layer/expert/byte_class | Pinned layer split, tape/trace expert identities, native pack's per-layer blob classes. |
| initial generation 0 / slot | Tape `initial` map or native trace `*-initial.bin`; nonresident `-1` does not create a resident. |
| admission generation / uid | Source ordinary copy record plus run/authority namespace; monotone ID is identity, not evidence of chronology. |
| trigger/target | Oracle E journal fields; native trace's named window where recorded; absent intent remains null. |
| issue/publish/eviction | Actual E `published_at` and host publication milestone; native issue withdraws victim, publication installs incoming. Native timestamps are mapped to the first observable main service boundary at or after that milestone, not an invented earlier window. |
| first/last use / use_count / distinct_use_count | Chronological service L records, exact slot/generation association. Validated against E use totals and lifecycle journal LC when available. |
| release/expiry | Recorded LC fields only. A null release for an arm without LC is unknown, not an expiry or zero duration. |
| victim / victim_layer / previous_generation | Copy record and actual live ownership at withdrawal; repeated expert admissions preserve distinct identities. |
| copy_bytes | Ordinary per-record payload; completed/unpublished/incomplete partitions stay separate. Native publication completion is the retained completion evidence. |
| copy_us | Host bracket `copy_end - copy_begin` where present; includes observation effects, not exclusive DMA time. |
| demand path | L path codes / native trace masks; lane counts preserved, slot-map consistency checked. Modeled references only identify local/nonlocal; CPU versus mapped is unknown. |
| resident interval | Publication through actual withdrawal, or observed routed end with right-censoring. Pending-drain ownership can occur after the last service. No use beyond observation is invented. |
| protection occupancy | LC release intervals sampled at observed logical state; missing LC means unavailable, not verified unprotected operation. |
| profile process fill | Frozen ranked-pair file filtered by actual device ownership and attested physical capacity; separate from decode initial state. |

Native copy records name the preceding runtime window. The timestamps and observed slot map, not the copy-array position, determine publication visibility. Oracle spare-donor withdrawal precedes event zero and is recorded explicitly. Mandatory final restoration does not create observed routed service; its charged bytes remain separate in summary reconciliation.

The frozen oracle's ordinary `victim(int l, ...)` search in `q4_oracle.hpp:105` scans experts in the incoming layer `l`. Its ordinary exchange therefore records the same victim layer; startup spare-donor selection separately scans the compatible device/class pool. Native trace version 2 names the outgoing layer explicitly and may replace across layers. These paths are parsed separately; class compatibility alone is not used to invent an outgoing layer.

## Modeled predecessor schedules

The Atlas reads retained schedule rows from the authoritative corrected IQ3_S E004 v6 and Q4 v2 reference results. It reconstructs those schedules under their declared issue/publication window convention and checks total modeled nonlocal demand against the retained result. It does not run a new policy or turn modeled join-wait proxies into measured decode latency. Timing-relaxed capacity-free replacement remains labeled idealized. Invalid older simulator versions stay in their original campaign, not in the valid comparison set.

## Disjoint completed-copy outcomes

Completed ordinary bytes partition into completed-unpublished, published-used-before-withdrawal, published-evicted-without-observed-use, and published-no-use-resident-at-observation-end. Incomplete/unknown completion is separate. First-target eviction, lateness and repeats are additional reasons, not partitions to add again. Restoration and sampled readback do not enter ordinary expert payload.

## Known limits

Exact GPU execution timestamps, pure DMA duration, warmup/prefill per-expert routing, per-event veto timestamps, causal per-expert latency and infinite future are not reconstructed. Later use outside a finite request is unobserved. Aggregated-only repetitions and conditional-admission natural runs do not gain invented residency events. Natural ON/OFF requests can diverge; exact comparisons require a common tape/trace identity. Phase 3 container-position causal attribution is not reused; the published chronology erratum remains authoritative.
