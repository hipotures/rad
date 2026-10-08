# Golden Swap Experiment Atlas

**Start with the [curated evidence gallery](http://192.168.100.207:8765/gallery).** Twelve selected views explain startup turnover, physical slot ownership, current/full-oracle behavior and the Phase 1/2 lifecycle mechanism. Each card opens the exact interactive deep link. See the [visual review and repairs](visual-review.md), [BEFORE/AFTER audit](results/visual-audit/visual-audit.json), [curated URLs](results/curated-views.json) and [URL/discovery API](provenance/url-state.md). The revised review uses direct screenshot inspection, not just the original mechanical browser receipt.

An interactive research instrument for inspecting completed expert-residency experiments. It is a retrospective review, not another experimental phase. It runs from retained evidence and starts no inference service.

**On the research host:** open <http://192.168.100.207:8765/>. The task-owned server binds to `0.0.0.0:8765`; its current identity is in ignored `server-status.json`. [results/server-launch.json](results/server-launch.json) is the historical launch receipt, not authority to signal a reused PID.

The catalog indexes **12 experiments / 335 run records**. **102 identity-selected trajectories** have full detail, covering **3,615,449 startup/admission generations** and **156,180,000 main routed lane entries**. Repetitions without selected detail remain indexed with their original results. Detail selection used the first retained task/policy identity, all Phase 0 recordings and all Phase 4 attempts, never a favorable timing.

Read [report.md](report.md) for findings, [startup-selection.md](provenance/startup-selection.md) for the exact fill algorithm, and [event-schema.md](provenance/event-schema.md) for field meaning and uncertainty. [source-catalog.json](results/source-catalog.json) records inclusion/exclusion and original hashes.

## Open a portable clone

From this review directory:

```bash
python3 code/serve.py --host 0.0.0.0 --port 8765
```

The server prints listening and discovered IPv4 URLs. Choose another unprivileged port if occupied. It needs only Python's standard library, the checked-in static site and gzip evidence. No Node build, GPU, original tape, model, or external CDN is needed to inspect the dashboard. Plotly 2.35.2 is a complete local pinned distribution served from its gzip archive with JavaScript MIME. Its MIT license and hashes are retained. The custom server sets gzip Content-Encoding; an unconfigured generic server that serves `.gz` as opaque bytes is insufficient.

## Explore the evidence

| Page | What to inspect |
|---|---|
| Experiments | Filter campaign/task/policy/profile/source group; click a row to select A. A filled dot means a selected complete trajectory. |
| Residency | Primary layer residency-state heatmap, local/CPU/mapped overlays and A−B. Exact expert intervals and the global layer map remain drill-downs. |
| Physical slots | Actual device-local destination ownership over time; GPU/class, changed-only, most-changed count and layer/expert scope. Exact owner transitions in hover. |
| Swaps & churn | Published admissions, withdrawals, bytes, repeat admissions, late publication, cumulative traffic and observed protection. Rolling smoothing can show counts or per-window averages. |
| Startup | Process profile fill versus attested decode snapshot; early demand, service before eviction, uninterrupted survival, return of initial identities, Jaccard and sortable poor placements. |
| Expert lifecycle | Every generation of one `(layer, expert)`, required local/CPU/mapped demand, readmissions and reuse gaps. |
| Current ↔ future | Linked matched-tape overlays, A−B, identity overlap and comparison with the same-source future reference. Exact logical work does not make timings from different binaries/blocks a paired performance experiment. |
| Demand | Expert × time heatmap, active set, adjacent-bin overlap and path evolution. Bins are display aggregation; exact row data remain available. |
| Size classes | Physical capacities by GPU/class, traffic by class and selected-layer lifetimes. GPU1 has no Q4 3,993,600-byte pool under K24. |
| AUC → outcomes | Retained ROC/AUC/Brier/calibration, sampled ranking, unit-labeled decision funnel, guard activity, OFF/ON lifecycle ablation, direct history/logistic timing, unused-copy outcome and opportunity exposure. |
| Lease evidence | Lifetime/use scatter, initial-generation toggle, first-use delay, idle/reuse/eviction-return distributions and host-bracket copy cost. Threshold labels are exploratory; no TTL policy or cluster ground truth is produced. |

Choose A and B globally; use **Choose matching current / oracle** for a same-source counterpart. The future page preserves distinct full-oracle and modeled-reference semantics. Linked time zoom/hover, mouse pan, reset, legend toggles, light/dark theme and PNG/SVG export are available. Logical units are verifier windows, routed-layer invocations, or percent of observed request. Global series use GPU/class filters across all matching layers; layer/expert selectors govern detailed panels. Set similarity panels explicitly cover the whole model.

Default startup means the **post-warmup/prefill decode boundary**. Process startup is a separate source-reconstructed reference. Never-used initial experts, actual local service and finite-end censoring are separate. Hover and the provenance panel identify generation, slot, target, byte class and source hashes.

## Included lineage

| Record | Reason |
|---|---|
| Original IQ3_S E004 corrected v6 | Earliest recorded-demand / modeled future-nextuse replay; IQ3_S/K25 and assumed transfers, not live Q4 throughput. |
| Q4 multi-GPU and pool-spin | Ordinary K24 capacity, baseline/runtime characterization and repeatability context; aggregate records. |
| Q4 residency v2 | Native demand/slot traces, history/early admission and distinct future-feasible, timing-relaxed capacity-free, narrow/wide future-utility schedules. |
| Conditional admission | Rejection/copy funnel and retained natural ON/OFF results; exact trajectories are not invented. |
| Q4 live oracle v3 | Same full native logical work, real copies, preserved capacity and five charged spares. |
| Oracle decomposition | Incoming/victim information limits; incoming/victim window horizons differ from the E64 routed-invocation frontier. |
| Golden Swap 0–4 | Corpus capture, frozen risk model, transaction control and history comparator, planner memoization, corrected chronology and failed instrumentation-neutrality gate. |

These are separate experiments. Simulator fixed-compute/join-wait proxies are not measured TG. Natural ON/OFF work may differ. Ordinary/current capacity is retained; the spares are withdrawn from existing residents. Full oracle is a feasible scheduler, not an optimal upper bound. CPU/GPU arithmetic and replay equality do not establish natural-generation quality.

## Regenerate and validate

Serving needs no dependencies. Derivation needs Python 3.10+ and NumPy 2.3.3; browser validation used Playwright 1.55.0 and system Chromium 154 with GPU rendering disabled. Use a task-owned external environment. Exact commands, input relocation, namespace refusal and the exercised bounded reproducer are in [reproduce.md](reproduce.md).

The pipeline is `catalog.py` → `build_atlas.py` → `predictor.py` / `finish_data.py` → `compact_assets.py` → repository `pack-text`. Demand is shared by exact content hash across arms; generation intervals plus exact service exceptions reconstruct **every** original normalized row. All 4,896 layer payloads round-trip exactly. Gzip files are complete copies; no original was overwritten or split to meet a size cap.

Original validation receipts: [data](results/data-validation.json), [lossless encoding](results/compact-validation.json), [predictor](results/predictor-validation.json), [mechanical browser](results/browser-validation.json), [bounded regeneration](results/reproduction-validation.json). Revised visual validation: [final deep links, reset and pixel-identical reconstruction](results/visual-audit/reproduction-publish/acceptance.json), [direct image review](results/visual-audit/release-acceptance-v2/acceptance.json), [slot/service/raw lifecycle checks](results/visual-audit/data-validation.json) and [URL edge checks](results/visual-audit/edge-checks-v3/validation.json). Screenshots document tested HTTP views; the interactive site is the deliverable.

## Missing evidence and recovery

Warmup/prefill per-expert demand and the original dataset used to create the shared startup profile are not attested. IQ3_S process fill cannot be reconstructed from a matching pinned profile. GPU0/1 timestamps, exclusive DMA/CPU savings, per-event guard-veto time series and MTP expert-path subdivisions are unavailable. A native 256K trace retains 96 copies without observed publication; their completion remains unknown. Finite-end residents are censored, not proven waste. Native/history live AUC and identical-state live scorer disagreements are not retrospectively fabricated.

The static Atlas and selected normalized records are recoverable from Git. Rebuilding them from original binary evidence requires the existing tapes/journals; some are local-only, irreplaceable captures without an identified off-host backup. [artifact-manifest.json](artifact-manifest.json) states this gap. Do not claim that a clone contains those binaries or that regeneration guarantees identical natural output.

The generated evidence import has a reviewed **256 MiB scoped aggregate budget** in [configs/evidence-budget.json](configs/evidence-budget.json); ordinary content limits, complete-file gzip ceiling, UTF-8/CRC and credential checks remain active. No new GPU benchmark, model fit, TTL implementation or normal serving change was made.
