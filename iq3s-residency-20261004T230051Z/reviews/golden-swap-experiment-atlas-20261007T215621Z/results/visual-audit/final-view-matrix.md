# Existing views after repair and visual review

This matrix follows the pre-change audit, not an assumption that every desired view was absent.

| Desired view | Existing implementation | Visually usable | Bug fix | Redesign or addition | Missing |
|---|---|---|---|---|---|
| Admissions/evictions through time | Existing churn series | Yes | Different color/dash | Combined aligned panel reused series | No |
| Copy volume through time | Existing published/cumulative series | Yes | Explicit sums/means/MB | Same panel | No |
| CPU/mapped/local through time | Existing service series | Yes | Separate scale for nonlocal work | Added to primary churn | No |
| Startup-set survival | Existing initial-generation series | Yes | None | Principal chart retained | No |
| Startup-set turnover | Existing identity/replacement series | Yes | Distinguish gen0 service from service after reload | Added initial-identity local-service curve | No |
| Expert demand heatmap | Existing expert × time | Yes | None | Retained; curated high-churn layer | No |
| Expert lifetime drill-down | Existing intervals/service | Yes | Explicit expert selection | Separate generation rows and target markers | No |
| CURRENT vs FULL_ORACLE | Existing matched comparison | Yes | Blank B auto-match | Aligned state/churn with linked time | No |
| Physical VRAM slot ownership | Retained slot field, no plot | Yes | Device/class validation | New exact owner timeline | No |
| Residency state heatmap | Gantt only | Yes with zoom | None | New primary resident-fraction heatmap | No |
| Repeated reloads | Existing repeats/generation data | Yes | Explicit drill-down | Curated native expert and generation rows | No |
| Lease/TTL evidence | Existing scatter/distributions | Yes | Threshold table now updates | Curated scatter; no new TTL policy | No |

Aggregate-only records have no invented chronology. Their page-specific empty states now work, and each offers a detailed alternative. Unfiltered overview and long unfocused predictor tables retain explicit POOR judgments; curated focus views are GOOD.
