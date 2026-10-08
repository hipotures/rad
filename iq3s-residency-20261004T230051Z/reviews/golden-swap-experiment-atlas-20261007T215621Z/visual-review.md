# Visual audit and usable evidence views

This is the revised Atlas objective, executed after the original publication. No new experimental phase, inference request, predictor training, TTL implementation or serving-runtime change was introduced. Start with the [curated gallery](http://192.168.100.207:8765/gallery): twelve complete screenshots link directly to the corresponding interactive views. The [curated manifest](results/curated-views.json) records canonical IDs, filters, ranges and selection reasons.

## What was actually broken

The original application was inspected through its live HTTP server **before changing application code**. All ten pages were navigated, allowed to finish loading, captured in full and inspected directly. The old browser receipt remains historical mechanical validation; it is not used as evidence of visual usefulness.

For the aggregate-only `q4-multigpu--32k-layer-split-1` run, Residency, Churn, Startup, Expert and Current/future produced the **same text SHA256**, no graphs and one generic message. The early aggregate return occurred before the individual page renderers. Changing the selected tab therefore made no visible page-specific difference. The [reproducer](results/visual-audit/before-navigation/diagnosis.json) retains the five screenshots. The repair provides a distinct heading, states exactly which chronological evidence is unavailable, and offers an actual detailed trajectory. It does not invent missing events.

On the default detailed Phase 2 archive history run, all ten original pages had distinct content and no JavaScript exception. A blank Run B made the future-comparison page empty; the original matching button worked and rendered nine charts. The repaired page selects a same-campaign, same-logical-work counterpart when B is absent. Retained scroll position could hide a new heading, so navigation now scrolls to the top. Rapid navigation was tested; no independent cache or asynchronous race defect was established.

Final control inspection also reproduced a stale reset display: `Reset all zoom` cleared the URL/application range but left From/To at 12/36. Reset now rebuilds the view, controls and identity together. Its targeted BEFORE receipt is retained, and the final acceptance explicitly checks full-range controls and URL after reset.

## What was poor and what already worked

Startup survival/turnover, Demand, physical Size classes, expert service detail and lease distributions were already useful. They were reused. The residency Gantt was a dense wall of 512 lanes; it is now secondary to a state heatmap. Admissions and evictions had indistinguishable presentation, and service paths were scattered across pages. They now share a four-axis churn panel, with local and nonlocal work on separate axes. The predictor page buried its explanation below a long collection of plots and tables; its primary panel now connects AUC, unused bytes and paired throughput, with explicit different denominators.

The unfiltered 335-row experiment table remains wide and is classified **POOR** as a first inspection surface. The unfocused predictor page remains long and also receives **POOR** for overall navigation density, despite a useful primary panel. These are disclosed limitations, not blanket PASS claims. All twelve curated, focused views were directly inspected and classified GOOD. Use the gallery rather than attempting to infer the most important evidence from the full catalog.

The [before matrix](results/visual-audit/existing-view-matrix.md), [after matrix](results/visual-audit/final-view-matrix.md), [full audit index](results/visual-audit/visual-audit.json) and per-page BEFORE/AFTER receipts retain judgments, titles, axes, legends, errors and capture paths.

## New and repaired views

Physical slots are device-local cache destinations, not expert IDs or the proposed victim's old slot. Ownership is reconstructed from all compatible layers. A spare publication puts the incoming expert in the former spare; the withdrawn victim slot becomes the next spare. The view supports GPU/class, changed-only, layer/expert scope, most-changed-slot count, zoom and exact generation/owner-transition hover. Blank time is unowned in the retained resident map; an issued copy is not yet residency. [Physical slot semantics](provenance/physical-slots.md) links the active source and bounds. Four representative policies across all 48 layers have no overlapping slot-owner intervals and preserve each slot's byte class.

The layer state heatmap encodes the fraction of a displayed logical-time bin spent resident. Local, CPU, mapped, admission and withdrawal overlays remain distinct. Binning is display aggregation; generation boundaries and service rows remain exact in the published assets. Zoom requests finer bins, and selecting an expert opens the separate-generation lifecycle plot. Logical event order is not a sub-event wall-clock measurement.

Startup's principal chart now separates original generation survival, initial identity resident after reload, initial identity demanded, local service before initial eviction, local service including reload, and cumulative replacement. On archive CURRENT, 8,542 initial generations serve locally before eviction, while 9,970 initial identities eventually serve locally including reload. These are different questions and must not share a label.

CURRENT/future displays synchronized state panels and aligned churn/service axes. Absolute and A−B residency views are available on exact logical work. The original oracle variants retain their different semantics; full oracle is feasible, not an optimal upper bound.

## What the selected screenshots establish

The selection uses retained counts and identities, not favorable timing. Archive CURRENT block 1 spans 769 verifier windows and publishes 10,822 admissions / 34.1275648 GB. It executes 70,827 CPU/mapped lane entries. Contemporary full oracle publishes 19,872 admissions / 63.044608 GB and leaves 1,685 CPU/mapped entries. More traffic can be useful: oracle's behavior is not simply fewer swaps. Native churn continues through the whole request. The chosen comparison range, windows 262–358, maximizes CURRENT's recorded nonlocal count among 96-window intervals; it was not selected by speedup.

The startup set is partially useful early and substantially replaced later. The original report's ranked-file-prefix interpretation remains valid. The first 64 archive windows contain 1,044 of 10,822 native admissions, while 90.95% of initial generations survive that interval; this does not prove a universal startup correction burst. Startup still refers to the post-warmup/prefill decode snapshot unless explicitly labeled process-fill reference.

For archive L0/E122, Phase 1 learned control has 41 published generations and 40 readmissions. The selected event range 12,500–12,750 exposes 21 rapid unused generations followed by a used generation. One retained generation publishes at 12,520, targets 12,576 and is withdrawn at 12,522 without service. Phase 2 frozen logistic plus first-use control publishes at 12,535, serves at 12,576, releases protection at 12,577 and remains until 17,521. Its whole-tape expert has only two admissions. Source E/LC/replacement records verify these identities and slots. This is a lifecycle illustration on the same tape/checkpoint; different campaign implementations and guards prevent treating it as a new paired timing ablation.

The native L3/E135 example has six resident generations, five readmissions and 17 nonlocal lane entries; one interval is unused and others have repeated service. Lifetime/reuse scatter spans transient unused intervals and long repeated-use residents. End residents remain censored and initial age is unknown. Exploratory short/long/pinned labels are not policy ground truth or an implemented TTL.

The AUC panel preserves native-distribution ranking evidence. It does not make admission lifetime, copy cost, competing admission opportunity or exposed latency part of AUC. Phase 2's retained diagnosis links 99.998328% of Phase 1 learned no-use bytes to withdrawal before the intended target. First-use control changes that mechanism for both history and logistic. Common oracle incoming and protection are privileges, and the chart does not attribute their benefit to learning. No historical performance conclusion is silently rewritten.

## URL state and discovery

Every principal view is addressable as `/?view=...&run=<canonical-id>`. Supported parameters include `view`, `run`, `compare`, `gpu`, `layer`, `class`, `expert`, `experts`, `from`, `to`, `time`, `smooth`, `metric`, `comparison`, `focus` and `snapshot`. Additional parameters control counts, slot scope/count/changed-only and lease thresholds. Controls and Plotly zoom update the URL; a fresh empty-cache context reproduces the same plotted numerical state. Exact examples are in the curated manifest and [URL reference](provenance/url-state.md).

Read-only metadata: `/api/views`, `/api/runs`, `/api/runs?task=code-archive`, `/api/matches?run=<id>`, `/api/interesting?run=<id>`. Unknown identity is null, not an equality of missing hashes. Unknown routes/IDs return 404; no generic filesystem API or mutating API was added. Matches establish logical work, not timing comparability.

## Validation, publication and recovery

The final fresh-browser test opens all twelve deep links in independent contexts, checks title/run/filter/range/Plotly identity, nontrivial chart pixels, distinct charts, numerical URL round-trip and exceptions. It additionally reproduces aggregate navigation, actual zoom URL update, pan/hover, rapid navigation and light theme. Direct screenshot inspection is a separate required step. Edge tests cover GPU1/class, subset A−B, percent time/service shares and lease settings. The browser uses software rendering; no GPU inference runs.

The durable package contains 86 complete PNGs: all ten original and eleven final full-page captures, focused important charts, the navigation reproducer, twelve curated screenshots and final edge/gallery captures. Duplicate viewport/intermediate screenshots remain complete locally with hashes. Oversized full-resolution predictor/gallery PNGs are not forced into Git; complete lower-DPR browser captures are published. Whole chart specs and the screenshot inventory use the normal complete-file gzip workflow. No source file is split to evade a cap. Exact raw captures may be local-only; current views are recapturable from Git's static data/source, and the historical BEFORE source is pinned to `3a6f011fa00dd9b0082475fe51b8b4b8d34712ca`.

The original missing evidence remains missing: profile training provenance, warmup/prefill expert demand, exact sub-event wall times, per-event guard vetoes, exclusive CPU/DMA latency and fresh causal scorer disagreements. The strongest research follow-up remains a bounded offline opportunity-cost study of selective post-use retention. The Atlas supplies inspection evidence and implements no new policy.
