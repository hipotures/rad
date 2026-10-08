# Exact phase-cell assembly candidates

All 8 candidates passed the retained strict rational assembly conditions and exact primitive/root bounds. The new analytic transfer is pending independent review, so these are arithmetic candidates.

| Mode | h50 roles | Kappa | Ratio to 2^-59, rounded down |
|---|---|---|---|
| conservative | 509194 | 3955009008227/500000000000000000000000000000 | 4.559814936498 |
| conservative | 494250 | 8376746778527/1000000000000000000000000000000 | 4.828865749804 |
| conservative | 487650 | 8596128362277/1000000000000000000000000000000 | 4.955330622614 |
| conservative | 486200 | 1729095984699/200000000000000000000000000000 | 4.983779860722 |
| optimized | 509194 | 4394441138389/500000000000000000000000000000 | 5.066445689177 |
| optimized | 494250 | 1163433384887/125000000000000000000000000000 | 5.365389474455 |
| optimized | 487650 | 1193902884521/125000000000000000000000000000 | 5.505905239905 |
| optimized | 486200 | 9606057843781/1000000000000000000000000000000 | 5.537515331296 |

The cutoff refinement additionally checks the full guard constant and partial phase-cell size. The common cutoff remains asymptotic; BHP and retained-interface thresholds are also needed.

Elapsed: 0.323635 seconds. See [full derivation](../../reports/downstream-phase-cell-inverse.md) and [protocol](protocol.json).
