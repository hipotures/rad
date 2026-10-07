# Strata PR578 — COMPLETE

## Running

```json
null
```

## Completed

- GitHub snapshot
- fresh checkouts
- clean local merge
- existing model and replay inventory
- 10 paired correctness cases
- primary32K sweep
- identical sm89 builds
- CTest suites:56pass/2skip/4environment failures each
- Python serve tests OK197cases each
- paired10prompt correctness
- 32K primary six-config sweep
- fair64
- diagnostics
- secondary
- fresh
- steady
- matrix
- originalPR finalcontextmatrix
- originalPR independentaudit and preservedcheckpoint
- localhelperprioritybuild andCTest sameenvironment failures
- localhelperpriority10prompt correctness
- local helper-priority 32K: 3 valid measured runs
- local helper-priority steady2048: 3 valid runs, median135.4 TG
- local helper-priority final matrix: all 12 measured runs valid
- matched-capacity lookup ON: 3 valid measured runs
- original helper steady2048: 3 valid measured runs, median76.0 TG
- final Polish report, CSV/JSON
- independent audit: 105 raw requests, no issues
- all campaign engines/drivers stopped; GPUs0/1 free

## Pending


## Current winners

```json
{
  "recommendation": "KEEP_LAYER_SPLIT",
  "layer_split": "LS-A auto K25; final TG135.1/126.9/119.2/114.3 at31400/63400/127000/259500",
  "original_PR_optimized_helper": "final TG95.4/84.1/82.4/76.2; steady75.3",
  "local_helper_priority_fix": "separate commit ec511d128247ccf25a1ec94168481bd053d35dfd; final TG117.5/100.8/125.1/117.7; steady135.4",
  "steady_original_helper": "76.0",
  "steady_layer_split": "158.8"
}
```

## Excluded runs

```json
[
  {
    "path": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090/raw/H-OPT-DIAG-32K-run2.json",
    "generated": 63,
    "finish": [
      "tool_calls"
    ],
    "tools": 5,
    "exclusion": "INVALID_EOS_OR_REQUEST"
  },
  {
    "path": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090/raw/H-OPT-FAIR64-32K-run2.json",
    "generated": 63,
    "finish": [
      "tool_calls"
    ],
    "tools": 5,
    "exclusion": "INVALID_EOS_OR_REQUEST"
  },
  {
    "path": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090/raw/H-OPT-FAIR64-RETRY1-32K-run2.json",
    "generated": 63,
    "finish": [
      "tool_calls"
    ],
    "tools": 5,
    "exclusion": "INVALID_EOS_OR_REQUEST"
  },
  {
    "group": "H-OPT-LOOKUP-ON",
    "reason": "INITIAL_CACHE_CAPACITY_MISMATCH; secondary numeric rerun preserved separately"
  },
  {
    "group": "H-OLD-DIAG/H-OPT-DIAG",
    "reason": "DIAGNOSTIC_INSTRUMENTATION: not headline speed"
  }
]
```

## Next exact action

None. Campaign completed; report.md and raw data preserved; both GPUs free.

Full authorized scope: PLAN.md. Both builds use frozen upstream main and local PR snapshot.
