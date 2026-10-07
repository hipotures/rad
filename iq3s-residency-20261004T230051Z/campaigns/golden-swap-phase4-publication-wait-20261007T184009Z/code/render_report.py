"""Render a reviewable report from frozen compact measurements, without inference."""
import argparse,json,statistics
from pathlib import Path
C=Path(__file__).resolve().parents[1]
def main():
 q=argparse.ArgumentParser();q.add_argument('--output',required=True,type=Path);a=q.parse_args();assert not a.output.exists()
 data=json.loads((C/'results/final/analysis.json').read_text());ident=json.loads((C/'configs/runtime-identity.json').read_text());rows=[r for r in data['rows'] if r['version']==2];traces=[r for r in rows if r['arm']=='TRACE'];parts=[]
 def emit(s):parts.append(s.strip()+'\n')
 emit('''# Golden Swap Phase 4 — publication acknowledgment attribution

Primary conclusion: **INSTRUMENTATION_OR_FIDELITY_BLOCKED**. Replay fidelity and trace identity passed. Quantitative neutrality of the instrumentation did not pass the predeclared symmetric timing gate. Structural evidence remains useful; it does not support a measured ordinary-request publication speedup.

Completed the Phase 3 correction, repaired/froze the Phase 4 protocol, implemented tracing, ran all six v2 requests, analyzed and preserved them. The earlier valid v1 pair is retained separately: eight valid measured attempts overall, no invalid completed replay requests, one substantive post-smoke instrumentation repair, one bounded kernel-cost diagnostic. No Phase 3 GPU requests were rerun. No Phase 5 was started.

## Corrected Phase 3 prior context

The original post-hoc script compared admission-array positions to infer that publication visibility preceded incoming-selection divergence. That inference was invalid: a previously proposed generation can publish after a later decision. The correction uses logical trigger, actual publication event, generation, slot and within-run timestamp/source ordering, and inspects the complete matched proposal prefix.

All 14 retained pairs have a differing publication visible at the same logical event as the first differing **recorded incoming-admission action**. No witness is strictly earlier in logical-event units. The archive block-1 old witness published at events 14/12 after the selection frontier 10 and is withdrawn; generation 3 supplies the valid same-event witness. The first recorded admission action excludes unrecorded rejected candidates and NO_SWAP decisions. Exact causal attribution to that publication or worker-readiness change remains **UNRESOLVED_WITH_RETAINED_EVIDENCE** for all pairs. The chronology lesson concerns observed precedence, not proof of a unique cause.

The Phase 3 headline **DECISION_PRESERVING_OPTIMIZATION_NO_CONFIRMED_PRACTICAL_GAIN** and its 42 timed measurements remain unchanged. Original interpretation, source and compact artifacts are preserved under the [correction record](../golden-swap-phase3-20261007T150955Z/corrections/publication-chronology-20261007/erratum.md), with explicit erratum in its report.

## Frozen experiment

The [protocol](configs/protocol.json) was repaired and validated before the fresh execution clock. Protocol SHA256 `715ab7dff70d66f58972092adb385efa8a3c183a37f7277ab3cde08e80ee2d2c`; start `2026-10-07T19:49:14.064443+00:00`, immutable deadline `2026-10-07T23:49:14.064443+00:00`. Preparation and Phase 3 correction time are excluded. Actual stopping time and elapsed duration are in [completion-audit.json](completion-audit.json).

One previously exposed development trajectory, `math-rational`, source group E026-numerical; 32K configured context, **10,943 actual input, 2,048 emitted output, 653 verifier windows, 31,344 main routed-layer invocations, 1,146,240 main lane entries, 18,480 MTP routed entries**. Final committed state occupies 12,990 positions under the engine's input-minus-one convention. Not a new holdout or multi-domain generalization study. Tape SHA256 `7aaf9c90db0394577b96a7ef8a09e75d07d590ac30623f3f75f41774dae899a5`; initial-state SHA256 `bef7b3ed1546b7e8898c6584327d16f4e394efb5f457a67973d40fcd2b8bce4d`.

Qwen3.8-Flash-Next UD-Q4_K_XL, revision `38bb39ee97821de2c9009abb7e93950eec396e66`; two RTX 4090, K24, PCIe fraction .28, pool spin 100 us, 15 workers, spec4/min-p .5, INT8 KV, requested kv-resident32768, prefill auto, suffix/reuse off. The engine reports KV resident zero in this profile; requested configuration was not retuned. Five charged spares (17,305,600 bytes), 11,541 ordinary resident slots (6,031 GPU0, 5,510 GPU1), all 48 main layers and three physical classes; full immutable 73,450 MiB host expert arena, no SSD tier. History victim rule + minimum first-use transaction control + Phase 3 incoming memo ON; oracle incoming and privileged current-window safety unchanged. Frozen logistic supplied for inherited config identity, not used for scoring. All eight runs made zero victim-future queries.

Fresh servers and identical saved 4096-input/64-output warmup; native prefill and exact initial-state attestation. Same binary per pair; only detailed trace switch changes between CONTROL and TRACE. Order: C→T, T→C, C→T. Startup, warmup and shutdown are separate; completion wall includes prefill, decode, final drain/restoration, output and tape flush. No concurrent build, download or heavy analysis during measured requests. CPU steal observations are preserved without correction.
''')
 emit(f"Final v2 source `{ident['source_sha']}`; binary SHA256 `{ident['binary_sha256']}`. Parent Phase 3 source `f3b4f19157b39ae017e2fd91814c8f5728e3b1cc`; original upstream `6f32ec070f23ced9f50e704d854d775da52591ab`. Exact build commands and both reconstructible patches are retained in [runtime identity](configs/runtime-identity.json) and [reproduce.md](reproduce.md).")
 emit('## Request results\n\nPositive time change means TRACE is slower. Decimal GB refers to ordinary expert payload, excluding restoration and sampled readback.')
 emit('| Version / block | Arm | Valid | Prefill s | Decode s | Replay tok/s | Completion wall s | Startup / warmup / cleanup s | Copy GB | CPU / mapped entries | Median steal % |\n|---|---|---|---:|---:|---:|---:|---|---:|---|---:|')
 for r in data['rows']:
  cp=r['ownership']['copies'];d=r['ownership']['demand'];emit(f"| v{r['version']} / {r['label'].split('-')[-2]} | {r['arm']} | yes | {r['prefill_s']:.3f} | {r['decode_s']:.4f} | {r['TG']:.1f} | {r['wall_s']:.4f} | {r['startup_s']:.2f} / {r['warmup_s']:.2f} / {r['cleanup_s']:.2f} | {cp['completed_bytes']/1e9:.5f} | {d['cpu']} / {d['mapped']} | {r['telemetry']['steal_pct']['median']:.2f} |")
 emit('| v2 arm | Replay tok/s min / median / max | Decode s min / median / max | Wall s min / median / max |\n|---|---|---|---|')
 for arm in ['CONTROL','TRACE']:
  rr=[r for r in rows if r['arm']==arm];qs=[]
  for key in ['TG','decode_s','wall_s']:
   vs=[r[key] for r in rr];qs.append(f'{min(vs):.4f} / {statistics.median(vs):.4f} / {max(vs):.4f}')
  emit(f"| {arm} | {' | '.join(qs)} |")
 emit('| v2 paired block | Decode change % | Completion-wall change % | Replay TG change % |\n|---|---:|---:|---:|')
 for p in data['paired_blocks']:emit(f"| {p['block']} | {p['decode_change_pct']:+.3f} | {p['wall_change_pct']:+.3f} | {p['TG_change_pct']:+.3f} |")
 emit('''Median paired decode +1.266%, wall +0.837% satisfy the median ±3% conditions. **The full gate fails:** two pairs exceed ±5%, and individual decode differences exceed ±10% in both directions. The reverse-order second block is substantially faster under TRACE; treating speedup as neutrality would be incorrect. The slow member of each first two blocks has higher median CPU steal (TRACE1 4.8%; CONTROL2 4.2%). This association is not causal proof or permission to adjust away the observations. No lucky neutral repeats were added.

The v1 first pair failed the gross gate (+18.840% decode, +12.406% wall). The bounded repair removed five extra per-layer stamp launches and recorded math boundaries inside existing kernels. V2 first pair again failed gross timing; it was paused, inspected, then the remaining frozen pairs were completed **for structural attribution only**, under the documented continuation decision. Versions are never mixed within a pair. Safety and equal fixed-schedule decision/work checks passed; realized asynchronous admission counts differ across live runs and are not claimed identical.

## Runtime chain and recorder

```mermaid
flowchart LR
  Copy[Weight copy completed] --> V[Publication validation]
  V --> M[Residency metadata submit]
  M --> E[Existing CUDA completion observation]
  E --> Ack[State 5 notify and unlock]
  Ack --> Own[Host ownership and generation commit]
  Own --> O[Remaining oracle/history plan]
  O --> N[Native plan construction]
  N --> A[Flag A publication]
  A --> WA[Consumer wait A readiness]
  WA --> R[Resident expert compute]
  R --> B[Mapped B readiness and compute]
  B --> CPU[CPU contribution readiness]
  CPU --> Join[Shared branch join]
  Shared[Shared expert stream] --> Join
  Join --> Comb[Combine]
  Comb --> H[K24 serial mapped handoff]
```

The host hook loops all five workers: a GPU0 invocation can wait for a GPU1 publication. Cross-device counts below measure this actual condition. Worker subphases nest inside host acknowledgment; the wait is a dependency constraint, not extra compute added on top of its producer. K24 uses sequential verifier stages and mapped portable pinned handoff after stage0 stream completion; there is no active remote/helper/peer-expert execution. Partial residency disables device-plan and all-resident shortcuts. Shared stream fork/join is active. STRATA_VERIFY_PROFILE and STRATA_POOL_TRACE remain **unset**, because even VERIFY_PROFILE=0 enables a scheduling-changing path.

Host producer records cover hook, publication loop, acknowledgment and ownership, remaining incoming plan, native plan and flag A. Worker records preserve event, target, generation, slot, device, class, command availability/observation, metadata submit, CUDA observation, acknowledgment state and post-notify/unlock timestamp. GPU records retain wait A/B/CPU begin/end, shared final-scale math bracket, combine math bracket and window boundaries; graph replays allocate device ordinals, avoiding captured-host-index aliasing. All writes use bounded preallocated buffers; no critical-path disk writes, polling thread or new device-wide synchronization.

V2 shared/combine endpoints are last-block **math-store completion before kernel retirement**, using a conditional block barrier/device fence and completion atomics. They are not CUDA event completion or exact shared join. Shared fork begin and independent prejoin/postjoin marks are unsupported in v2. Both arms allocate the same 14,680,064 host bytes and 7,040,104 device bytes per verifier. The legacy footer underreports device counter storage by 16 bytes; source/schema count 13 counter words correctly. These are trace storage, not extra expert slots.

Two calibration stamps per GPU per request are identical in both arms, at existing safe start/end boundaries. Each GPU maps separately to host monotonic brackets using an affine interval, with brackets approximately25–70 us. No host/GPU or cross-GPU raw timestamp subtraction is used. Two endpoints cannot independently bound interior drift; the following overlap intervals are conditional on affine mapping and are not unconditional confidence intervals. Calibration introduces an ordered readback and cudaStreamSynchronize of the calibration-only compute-stream work at each already-safe request boundary, identically in both arms; no per-invocation or device-wide synchronization was added. This is an extra boundary barrier for clock observation, so the strict no-convenience-barrier wording was not fully met. Its cost is charged to completion wall; it is not assumed cost-free or evidence of a nonperturbing baseline.
''')
 emit('## Structural acknowledgment attribution — conditional on recorded TRACE\n\n| Block | Generations | Ack total ms | Ack us median / p95 / max | Wait A ms GPU0 / GPU1 | Ack overlap ms interval | Fraction of A interval | Cross-device publications |\n|---|---:|---:|---|---|---|---|---:|')
 for r in traces:
  x=r['attribution'];us=x['publication_ack_us'];ov=x['ack_overlap_ms_interval'];f=x['ack_fraction_of_wait_A_interval'];ds=x['devices'];emit(f"| {r['label']} | {x['publication_generations']} | {x['publication_ack_ms']:.3f} | {us['median']:.3f} / {us['p95']:.3f} / {us['max']:.3f} | {ds[0]['wait_ns']['A']/1e6:.3f} / {ds[1]['wait_ns']['A']/1e6:.3f} | [{ov[0]:.3f}, {ov[1]:.3f}] | [{100*f[0]:.2f}%, {100*f[1]:.2f}%] | {x['cross_device_publications']} |")
 emit('All TRACE runs link **31,344/31,344 wait-A events (100%)** to producer event identity; all publication generations have valid worker chronology. No overflow, alias or mapped clock-order contradiction was detected. This is linkage coverage, not proof of complete critical-path coverage. Actual wait-A median is around10–23 us and p95 around134–264 us; exact per-device distributions are in analysis.json.')
 emit('| Block | Ack worker subphases ms: command→observed / setup / submit→CUDA observed / observed→state / state→notify unlock | Hook / publication loop / remaining incoming / native-plan ms | CPU wait ms GPU0 / GPU1 |\n|---|---|---|---|')
 for r in traces:
  x=r["attribution"];w=x["worker_subphases_ms_nested"];p=x["producer_phase_ms"];cpu=" / ".join(format(d["wait_ns"]["CPU"]/1e6,".3f") for d in x["devices"]);emit(f"| {r['label']} | {' / '.join(format(v,'.3f') for v in w.values())} | {' / '.join(format(v,'.3f') for v in p.values())} | {cpu} |")
 emit('''These worker measurements include scheduling/driver observation, not exclusive DMA time. Producer partition is ack plus non-ack publication-loop work, remaining incoming/history work, native/source plan, then unassigned scheduling gap. Hook includes its publication loop and incoming plan: do not add all four columns. Worker intervals likewise must not be added again to ack. Independent feature/model/selection timers are nested in planner; history is used, no learned scorer benefit is estimated here.

B/mapped waits are small (about27–31 ms combined), CPU readiness waits larger (about1.70–3.54 s combined). Shared math completion is observed before CPU wait end on all31,344 invocations in each TRACE, but exact kernel retirement and shared join delay are unavailable. CPU-end→combine-begin aggregates (~350–367 ms in v2) include joins, launch/runtime gaps and other required work and are not assigned wholly to shared masking. The serial layer split is confirmed; exact peer/handoff contribution is unassigned. These aggregates identify measured readiness constraints, not additive request costs.

The full completion graph is **PARTIAL_NOT_QUANTITATIVELY_CLOSED**. Main verifier-stage spans leave about9.64–10.68% of decode outside the retained stages, including commit/draft/host gaps. This is unassigned completion coverage, not a validated numerical graph residual. Fitting opaque gaps as fixed slack would reproduce the baseline by construction and is rejected as evidence of a correct counterfactual. Synthetic fork/join fixtures passed, while exact runtime completion-path reconstruction remains unresolved.

## Fixed interventions and uncertainty

Baseline is recorded TRACE execution unchanged. Primary fixed intervention **C_NOTIFY_TAIL** removes only

`max(0, host_ack_end - worker_notify_unlock_return - host_wait_thread_CPU_time)`.

It retains worker metadata submit/completion, acknowledgment state, notify/unlock, host CPU time, ownership validation/commit and every known dependency. This is a small plausible avoidable post-notify coordination component; it is not an executable optimization. Ideal **I_EARLIEST_SAFE** makes acknowledgment ready at actual publication-command availability after weight completion/validation, optimistically removing metadata/notification service while retaining external work/ownership constraints. It is an opportunity bound and does not authorize removing required metadata work.

For each same fixed scenario, missing competing edges and unsupported path coverage allow zero lower contribution; sum of removed node durations gives a conservative longest-path-shortening upper bound. No statistical midpoint is reported. Timing/model uncertainty does not mean varying intervention strength from baseline to ideal. Clock uncertainty constrains linkage/overlap separately; unknown interior drift prevents unconditional overlap claims. Since the perturbation gate failed, these bounds describe recorded TRACE trajectories and **cannot quantify the uninstrumented CONTROL request**.
''')
 emit('| v2 TRACE block | Primary removed ms | Primary S interval % | Primary counterfactual decode s interval | Ideal removed ms | Ideal S interval % | Ideal counterfactual decode s interval |\n|---|---:|---|---|---:|---|---|')
 for r in traces:
  x=r['attribution'];ps=x['primary_S_interval'];is_=x['idealized_S_interval'];pt=x['primary_counterfactual_decode_s_interval'];it=x['idealized_counterfactual_decode_s_interval'];emit(f"| {r['label']} | {x['primary_removed_ms']:.3f} | [{100*ps[0]:.4f}, {100*ps[1]:.4f}] | [{pt[0]:.6f}, {pt[1]:.6f}] | {x['idealized_removed_ms']:.3f} | [{100*is_[0]:.4f}, {100*is_[1]:.4f}] | [{it[0]:.6f}, {it[1]:.6f}] |")
 emit('''The narrow primary opportunity upper bound is below0.25% on all three recorded traces. The optimistic ideal bounds reach2.74–4.14%; they neither establish >3% benefit nor satisfy the protocol's <1% opportunity condition. Zero remains admissible because completion-path masking is unresolved. Publication substantially overlaps wait A but the amount reaching request completion is **not established**. Consequently none of the positive, small, or mostly-hidden classifications is justified under the failed instrumentation gate.

## Safety, resources and retained failures

Passed targeted real-copy lifecycle/readback on all five active device/class combinations, first-use/protection and same-event ownership change, expiration/NO_SWAP/cancellation/drain/restoration, and zero-copy cost veto fixtures. Passed recorder ready/delayed waits, graph replay counter/reset/overflow fixtures on both GPUs; nine relevant native tests including QSA active width, native physical classes, router, MTP and KV; six known fork/join dependency graph fixtures; deterministic detail OFF/ON math-rational candidate/work/admission/lifecycle parity; and shared/combine numerical OFF/ON fixtures on both GPUs at T1/2/4, including native N3072/FF640. Test results are actual logs, not inferred from compilation.

One bounded diagnostic timed ready-wait and native combine fixtures with recording OFF/ON. Additional cost was about0.10–0.29 us per ready wait and0.42 us per combine in that small graph, insufficient by itself to explain the multi-second pair difference. The fixture does not prove runtime neutrality, atomics/cache overhead cannot be corrected away, and no further diagnostic was run.

Early compile failures (namespace qualification, missing cstddef) and an administrative heartbeat error are retained, then repaired before timed v1 measurement. V1 and v2 gross timing failures are valid measurements, not invalid requests. No rerun was triggered merely by CPU steal or unfavorable signs.

All live ownership checks passed. Each request has issued=staged=completed=published ordinary payload, zero completed-unpublished/no-observed-use bytes and zero pending copies at end; restoration is separately17,305,600 bytes/request. Differences in counts/late publications are observed policy-dependent asynchronous trajectories, not dropped work. No natural-generation bit-equivalence is claimed: replay forces token identities; sampled CPU/GPU activation differences remain reported.

Both GPUs retained approximately23.8/24.0 GiB occupancy, SM clock around2790/2805 MHz, memory10251 MHz; per-device min/median/p95/max power/utilization/VRAM/clocks and CPU/steal/RAM are in the compact JSON and complete telemetry. Swap stayed zero. No clocks, affinity, power, worker count, pool, K, capacity or model settings were tuned.

Protocol deviations/limits: host record vectors were allocated after decode timestamp but before the first event, charging identical allocation work to both arms instead of the intended pre-timing placement; GPU buffers were allocated before timing. V2 removes independent shared/prejoin/postjoin stamps to reduce scheduling perturbation. Kernel record end precedes retirement. Two clock brackets do not measure interior drift. Full graph gaps remain unresolved. The v1 text miscounted extra per-layer launches as six; actual source count is five. Footer trace-byte undercount is16 bytes. No fourth v2 attempt, fresh-source transfer test or natural-generation quality evaluation was run; none was part of this six-request scope.

## Decision and next experiment

1. Corrected Phase 3 observed publication precedence is established relative to first recorded admission action at the same event; exact causal attribution and earlier rejected-decision chronology remain unresolved.
2. Phase 3 headline performance conclusion did not change.
3. TRACE failed the full symmetric perturbation gate despite passing the median clauses.
4. Conditional acknowledgment overlap is about29–40% of summed wait-A time across the three TRACE runs.
5. The completion-path portion is unresolved; primary-path bound0–11.1/12.6/47.9 ms, ideal0–464.5/490.8/826.5 ms.
6. Primary fixed-scenario improvement intervals: [0,0.2400%], [0,0.0738%], [0,0.0654%] on recorded traces only.
7. Ideal upper-opportunity bounds:4.1437%,2.8847%,2.7392%, with zero lower bounds; no achievable speedup claim.
8. A publication optimization is not justified yet as the highest-value next intervention: the primary opportunity is narrow and quantitative neutrality is unestablished.
9. Publication is not conclusively classified mostly hidden. CPU readiness is the strongest measured competing wait; exact masking by CPU/shared/serial handoff is unresolved.
10. Largest remaining measured readiness wait is CPU contribution readiness, not proven exclusive compute latency. Commit/draft/host gaps also lack graph closure.
11. Moving to causal incoming prediction is not justified by this attribution experiment alone; its prerequisites and separate scientific question remain open.
12. Highest-information next experiment: **same-binary adjacent CONTROL/CONTROL pairs in the same saved order/time envelope, with CPU/scheduler telemetry**, to distinguish order/environment drift from detailed tracing perturbation before interpreting publication counterfactuals quantitatively. Freeze its rules separately; do not automatically start it.

## Evidence and reproduction

[Final JSON](results/final/analysis.json), [request CSV](results/final/requests.csv), [paired blocks](results/final/paired-blocks.json), [symmetric gate](results/final/perturbation-gate.json), [clock/freeze/attempt ledger](runs/20261007T194914Z/attempt-ledger.jsonl), [schema](configs/trace-schema.json), [dependency model](dependency-model.md), [reproduction](reproduce.md), [artifact recovery](artifact-manifest.json), [completion audit](completion-audit.json).

Completed raw text uses the repository gzip workflow. Oversized combined TRACE exports remain external; each independently recorded original journal is exported as one complete typed text file, never divided into size chunks. All such exports fit the strict10 MiB gzip rule. Byte-exact journal restoration and final-result regeneration from these gzip copies were tested without inference. Original tapes and numerical activation journals remain external, with identities and an explicit off-host recovery gap. No binary payload is committed. A scoped one-time campaign evidence budget is documented in configs/evidence-budget.json; ordinary content retains the20 MiB guard.

Normal serving Q4/K24/PCIe.28/pool100us remains unchanged. These oracle-incoming traces are conditional research evidence, not deployment validation.
''')
 a.output.write_text('\n'.join(parts))
if __name__=='__main__':main()
