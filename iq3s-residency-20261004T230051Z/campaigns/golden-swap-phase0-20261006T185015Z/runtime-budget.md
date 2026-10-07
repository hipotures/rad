# Runtime budget

All new costs are **instrumented natural recording** costs, not clean-baseline speed measurements. One sample per task supplies no robust p95 or confidence interval. Source-group diversity and performance repetitions are different quantities.

`arm_cost = startup + warmup + tokenization/prefill + decode + trace/commit/drain + shutdown`

`campaign_cost = shared_setup + sum(each scheduled arm) + analysis_and_cleanup_reserve`

One-time preparation: 14.14 min; actual summed model operations: 25.17 min; retained new trace/log bytes: 3.406 GiB. Data preparation scan: 27.06 s across 12 tasks. Policy replay/evaluation execution was not timed; its cost remains unknown, separate from this scan.

| Future schedule | Tasks | Arms/task | Observed-component projection min | Empirical component range min | With setup + 10min reserve | Phase-cap operating ceiling min |
|---|---:|---:|---:|---:|---:|---:|
| Quick development screening | 4 | 1 | 8.27 | 6.79–11.39 | 30.94–35.53 min | 30.33 |
| Full measured core / one policy | 12 | 1 | 25.17 | 20.49–34.29 | 44.63–58.44 min | 91.00 |
| Full core baseline + finalist / three pairs | 12 | 6 | 151.01 | 122.93–205.76 | 147.07–229.90 min | 546.00 |
| Full core four policies / three repetitions | 12 | 12 | 302.01 | 245.87–411.52 | 270.01–435.66 min | 1092.00 |
| Baseline + one finalist / three pairs | 4 | 6 | 49.62 | 40.77–68.31 | 64.91–92.45 min | 182.00 |
| Baseline + two finalists + oracle / three repetitions | 4 | 12 | 99.24 | 81.54–136.62 | 105.68–160.76 min | 364.00 |
| Reduced four-policy task set | 2 | 12 | 56.55 | 41.71–69.46 | 65.85–93.60 min | 182.00 |


The empirical envelope varies observed startup/warmup/shutdown components within each context and retains each task's observed request cost,plus5s per arm at the upper end. It is an estimate from this hardware/run,not a probabilistic guarantee. Phase caps provide a separate planning ceiling; preflight/validation allowance is additional. CPU/VM scheduling,OS cache,actual EOS and future policy work can change costs.

Screening task IDs: code-heg, math-rational, text-http, mixed-build. The predeclared roles choose them without inspecting routing or oracle benefit.

Four-policy reduced IDs: code-heg, math-rational. If the larger empirical envelope exceeds120min,this reduction is explicit; it does not delete the remaining corpus.

Three contemporary baseline arms per task can serve all comparisons within the same four-arm repetition block, with identical tape/work prefix,engine/config/protocol and matched initial state. Correlation must be retained. Do not duplicate baselines per candidate or reuse stale historical controls,other engines,models or trajectories. Fourpolicies x3repetitions=12arms/task; baseline+onefinalist=6arms/task.

All new timings use recording hooks; original clean0.1.39 baseline is verified but not newly timed here. Prior short development recording was2.3986s decode/7.1197s request versus original2.1953s/6.1720s. Do not extrapolate that overhead as a universal correction.

Later A/B arms must replay the same validated completed logical tape prefix,including rejected speculative work,or use frozen output/work budgets. Giving each policy60s and comparing raw routed counts would compare different work. Natural output-limit slices do not imply task completion.

Short prompts remain short; a128K context limit does not imply128K input occupancy. No costs from unmeasured tasks are averaged into measured totals. Historical extended tapes have their original protocols and do not substitute for new clean timing.
