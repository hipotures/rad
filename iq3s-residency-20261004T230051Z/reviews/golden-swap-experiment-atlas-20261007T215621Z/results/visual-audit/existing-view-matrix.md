# Existing view matrix, before application changes

The original ten pages were navigated through HTTP and their screenshots inspected. No page is classified from Plotly object existence alone. The audit uses the default detailed Phase 2 archive history run; the aggregate-only failure and matched CURRENT/FULL_ORACLE case are retained separately.

| Desired view | Existing implementation | Visually usable | Needs bug fix | Needs redesign | Missing |
|---|---|---|---|---|---|
| Admissions/evictions over time | Churn, six stacked charts | Partly | Identical series colors | Compact combined panel | No |
| Copy volume over time | Rolling and cumulative published bytes | Yes | Unit/normalization clarity | Reuse in combined panel | No |
| CPU/mapped/local over time | Demand and comparison service chart | Partly | Nonlocal work dwarfed by local | Separate service axes in churn | No |
| Startup-set survival | Startup principal percentage curves | Yes | No | Promote existing chart | No |
| Startup-set turnover | Generation survival, identity presence and replacement | Yes | No | Shorter legends | No |
| Expert demand heatmap | Demand, expert × binned time | Yes | No | No | No |
| Expert lifetime drill-down | Expert intervals, physical service, table | Yes | Implicit expert changes global state | Better evidence-based default | No |
| CURRENT vs FULL_ORACLE | Nine charts after matching button | Yes after choosing B | Default empty comparison | Aligned state/churn panel | No |
| Physical VRAM slot ownership | Generation field exists; no chart | No | No | New view | Yes |
| Residency state heatmap | Only dense expert Gantt | No | No | Replace primary dense display | Yes |
| Repeated reloads | Churn repeat series + expert generations | Partly | Expert selection default | Curated concrete lifecycle | No |
| Lease/TTL evidence | Lifetime scatter and seven distributions | Yes | Threshold table stale | Focus primary scatter | No |

## Confirmed navigation defect

For `q4-multigpu--32k-layer-split-1`, Residency, Churn, Startup, Expert and Current/future all produce the exact same content text SHA256 and no graphs. The generic aggregate-evidence early return precedes every page-specific renderer. Tab selection changes, content does not. This is an application empty-state bug, not evidence that the underlying journals are absent from all experiments.

For the default detailed trajectory, all ten page content hashes differ and there are no browser exceptions. The original matching button selects the correct archive CURRENT/FULL_ORACLE pair and renders nine charts. No asynchronous race or cache failure has been established. Scroll position is retained on navigation and can obscure newly rendered page headings; reset it explicitly.
