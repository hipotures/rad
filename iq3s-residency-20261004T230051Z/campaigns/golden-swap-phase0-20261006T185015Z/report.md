# Golden Swap Phase 0: audited corpus and runtime calibration

**PHASE0_READY**: 12 tasks defined, 12 newly calibrated and structurally replay-ready, across 4 families. Phase 0 only: no predictor training, replacement algorithm, Golden Swap implementation, live oracle matrix, forced routing or dropped expert contributions.

Start **2026-10-06T18:49:49.997758+00:00**, hard deadline **2026-10-06T19:49:49.997758+00:00**, monotonic start **460510.865267**. Request-launch cutoff **2026-10-06T19:39:49.997758+00:00**. Render time **2026-10-06T19:42:41.365779+00:00**, elapsed **52.86 min**. The earlier timing-only directory governs; the deadline was not reset. Final lifecycle elapsed time is in progress.json and completion-audit.json.

## What the existing benchmark actually contained

The historical audit opened 124 payload files and actual builders, rather than treating reports as payloads. Exact messages, source boundaries, text/ID hashes, nonce locations and source snapshots are in workload-inventory.json; prompt-catalog.md shows actual instructions and source excerpts. The original Strata repository-maintenance requests are source snapshots wrapped as a "coding agent", with a 40-section maintenance/diff task. They are not interactive agent executions. E026 contains HEG storage repository source, CPython/NumPy numerical libraries, and HTTP RFCs; its variants and context excerpts are shared lineages. Earlier short dev/cal/hold prompts were 59–72-token instructions, not 32K inputs. The archive request is a 26000-character CPython zipfile excerpt. Conditional-admission math problems and incident packets are locally authored; the fictional packets are labelled, not real logs.

The old corpus builder can cycle files, but no repeated source headings were found in the inspected saved payloads. Repeated long lines and boilerplate are recorded individually; standard legal headers, source templates and similar mathematical topics do not make nonce variants independent. Lab builders truncate to complete-line prefixes; individual files may still be incomplete. E026 uses natural source concatenations without padding. The later issue #921 Q4 instruction requests 18000 words and 60 cases: artificial output elongation, retained historically and excluded here. The 4096/64 warmup is a deliberately truncated CMake stress excerpt, used solely for infrastructure. None of this retroactively invalidates previous spin timing.

## Sources, roles and natural task design

The core has three task/source groups per family and one source-group role each: development, calibration, reserved evaluation. The queue alternates code, math, text, structured in each role block. Related excerpts/nonce versions stay on the same side. Distinct CPython module tasks share a collection, which limits broad independence; they do not share excerpt text. Existing exposed tasks are explicitly flagged rather than called pristine holdouts. Reserved evaluation is excluded from fitting by default; this phase only calibrates infrastructure and does not choose features/policies from its routing.

Public discovery inspected two collections: official RFC Editor and the official Chinook repository via gh. Three small RFC documents and one SQLite source script/license were downloaded. TLS explanation/Polish translation, WebSocket explanation, Structured Fields grammar extraction and Chinook DDL extraction fill concrete source/subtask gaps. Local HEG/CPython snapshots and authored applied problems are reused. Actual paths, URLs, revisions, permissions and adaptations are recorded; unknown historical revisions remain unknown. The real build-log task uses an actual preserved CUDA build log. No reference answers/gold patches/hidden tests were supplied.

All twelve tasks are single offline requests with **tool_execution=false**. No autonomous agent framework was installed. New instructions request ordinary substantive work, with no deliberate filler, source cycling to reach a token target or book-length demand. The short authored math tasks retain the problem once as source material and add a separate ordinary solving instruction. A complete-paragraph prefix replaces the new archive prompt's incomplete historical trailing comment; its original source remains untouched. WebSocket uses a coherent paragraph prefix to fit. Source data and generated outputs are retained verbatim. Credential/private-key pattern scans and direct source inspection precede model use; no private prompts/logs were uploaded.

Eight 32K and four 128K configured limits are assigned once per task. Actual input spans 165–81722 tokens; max context is not occupancy. Short mathematical problems remain short. Role/context assignments are mixed rather than assigning all holdouts 128K. Each new task uses a 2048 output cap, natural EOS or a 60s soft decode boundary, and 240s request wall cap. An output-limit slice is meaningful routing work, not proof that the whole task or JSON artifact was finished.

## Verified baseline and recording contract

Original control: **Strata 0.1.39**, source **6f32ec070f23ced9f50e704d854d775da52591ab**, binary `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/control/strata`, SHA256 **eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d**. Q4 revision **38bb39ee97821de2c9009abb7e93950eec396e66**. No migration to the issue #921 0.1.40 engine.

The validated capture derivative has source **117bc89b3bacbf263379c336557e6c8aa07aff5e**, binary SHA256 **30a31432b5aff51bcd4340900c13cad0c8487a832bfdb22d05f9157b88d5bdb3**. All new measurements are **instrumented natural recording**, not clean baseline timing. Existing short development fidelity/overhead evidence is preserved in provenance/baseline.json; it matches original generated IDs/MTP, but does not provide a universal overhead correction. The first two configs inherited stale descriptive OFF/base-HEAD fields; actual executable/source/record environment were correctly checked and every episode is explicitly labelled instrumented. Later configs correct only those descriptive fields; original logs remain.

Q4 K24, PCIe 0.28, pool 100 us / 15 workers, MTP 4/min-p 0.5, INT8 KV, kv-resident 32768 where applicable, prefill auto, suffix/reuse off, greedy, serial. One fresh server and the exact saved 4096-input/64-output warmup per task. Model identity reuses the prior full model SHA256 audit plus unchanged size/mtime/inode for every file; no heavyweight rehash during timing. No model/source changes, rebuild, host/VM/clock/power/affinity changes or normal launcher edits. Hardware is one dual RTX 4090 / 7950X3D, 16-vCPU KVM guest, no swap; environment-summary.json and per-episode native metadata/telemetry preserve detail.

Tape mode is record; oracle mode is off. Source checks prove no future index is built in record mode and no oracle spares/actions are enabled. Native generation, cache adaptation and expert computation remain active. Schema2 retains full main/MTP routed IDs/coefficients, rejected speculative lanes, batched verify shapes, positions, QSA selections, initial residency/heat and meaningful initial-state hashes. Native layer observations provide main local/CPU/mapped paths, and swap hooks provide actual issued payload bytes/victims/publication timestamps. Main decode has 48 layers; repeated MTP draft-step slots represent the same physical MTP layer, not three new model layers. Prefill is naturally recomputed from exact IDs; its complete routing is not separately taped.

## Calibration table

| Task | Family/subtask | Source group/split | Context limit / actual input | Output / stop reason | Startup + warmup s | Prefill s | Decode s | Total operating s | Local / CPU / mapped % | Trace status | Core / screening / deferred |
|---|---|---|---|---|---:|---:|---:|---:|---|---|---|
| code-heg | code/agent/repository review | heg-storage/development | 131072 / 22883 | 2048 / OUTPUT_CAP | 133.70 | 13.67 | 20.94 | 175.69 | 90.37 / 8.27 / 1.36 | FULL_REPLAY_TAPE / PASS | core / screening |
| math-rational | math/research/exact arithmetic | E026-numerical/development | 32768 / 10943 | 2048 / OUTPUT_CAP | 71.70 | 12.41 | 17.96 | 107.08 | 91.77 / 7.19 / 1.05 | FULL_REPLAY_TAPE / PASS | core / screening |
| text-http | text/translation/document summarization | E026-HTTP-standards/development | 32768 / 20938 | 2048 / OUTPUT_CAP | 66.49 | 16.82 | 20.28 | 110.28 | 93.23 / 6.04 / 0.74 | FULL_REPLAY_TAPE / PASS | core / screening |
| mixed-build | structured/mixed/real build log analysis | strata-release-build-log/development | 32768 / 10934 | 2048 / OUTPUT_CAP | 69.74 | 8.21 | 17.87 | 103.17 | 92.25 / 6.80 / 0.96 | FULL_REPLAY_TAPE / PASS | core / screening |
| code-queue | code/agent/implementation reasoning | cpython-asyncio-queues/calibration | 32768 / 2498 | 2048 / OUTPUT_CAP | 82.10 | 5.26 | 18.57 | 112.24 | 92.86 / 6.34 / 0.80 | FULL_REPLAY_TAPE / PASS | core / — |
| math-sensor | math/research/numerical parameter fitting | authored-sensor-problem/calibration | 131072 / 179 | 2048 / OUTPUT_CAP | 94.56 | 1.26 | 18.98 | 122.30 | 93.32 / 5.96 / 0.73 | FULL_REPLAY_TAPE / PASS | core / — |
| text-tls | text/translation/English to Polish technical translation | rfc8446-TLS/calibration | 131072 / 81722 | 2048 / OUTPUT_CAP | 108.32 | 44.30 | 24.53 | 185.94 | 94.55 / 5.00 / 0.45 | FULL_REPLAY_TAPE / PASS | core / — |
| mixed-fields | structured/mixed/grammar and schema extraction | rfc8941-structured-fields/calibration | 131072 / 16346 | 2048 / OUTPUT_CAP | 70.57 | 13.52 | 16.76 | 106.15 | 93.31 / 5.98 / 0.71 | FULL_REPLAY_TAPE / PASS | core / — |
| code-archive | code/agent/safe archive import | cpython-zipfile/reserved_evaluation | 32768 / 6983 | 2048 / OUTPUT_CAP | 62.71 | 9.26 | 20.05 | 98.10 | 94.17 / 5.24 / 0.59 | FULL_REPLAY_TAPE / PASS | core / — |
| math-inventory | math/research/stochastic inventory | authored-warehouse-problem/reserved_evaluation | 32768 / 165 | 2048 / OUTPUT_CAP | 98.86 | 1.12 | 18.73 | 124.23 | 93.70 / 5.65 / 0.65 | FULL_REPLAY_TAPE / PASS | core / — |
| text-websocket | text/translation/technical explanation | rfc6455-WebSocket/reserved_evaluation | 32768 / 30383 | 1773 / NATURAL_EOS | 64.81 | 20.31 | 18.51 | 111.26 | 93.66 / 5.72 / 0.62 | FULL_REPLAY_TAPE / PASS | core / — |
| mixed-chinook | structured/mixed/real SQL schema extraction | chinook-SQLite-DDL/reserved_evaluation | 32768 / 1899 | 2048 / OUTPUT_CAP | 123.66 | 4.27 | 18.58 | 153.63 | 89.25 / 9.10 / 1.65 | FULL_REPLAY_TAPE / PASS | core / — |

Shares use one normal **main token-expert-entry denominator**, local+CPU+mapped. MTP entries are recorded separately; unique experts, admissions, jobs and token-expert entries are different units. Native copy bytes come from actual expert-layout hook sizes, not aggregate PCIe utilization. Unknown dynamic usage/heat, queue/protection fields and MTP dispatch subdivisions remain null. PP, TG, TTFT and full operating component details are in trace-summary.csv and runtime-budget.json. Telemetry has CPU/steal, RSS/RAM and both GPU utilization/VRAM/power/clocks; no swap is present.

## Trace diversity and victim-return suitability

| Task | Complete windows | Main / MTP entries | Unique main (layer, expert) | Native issues / publications | Native payload GiB | Median inter-use gap / distinct reuse distance |
|---|---:|---:|---:|---:|---:|
| code-heg | 681 | 1,135,200 / 18,490 | 21,714 | 12,836 / 12,836 | 37.52 | 3.0 / 39.0 |
| math-rational | 653 | 1,146,240 / 18,480 | 20,431 | 11,502 / 11,502 | 33.71 | 2.0 / 28.0 |
| text-http | 712 | 1,194,720 / 19,520 | 19,535 | 11,274 / 11,274 | 33.05 | 3.0 / 34.0 |
| mixed-build | 592 | 1,061,760 / 16,930 | 21,007 | 9,992 / 9,992 | 29.16 | 3.0 / 40.0 |
| code-queue | 682 | 1,153,920 / 18,740 | 20,457 | 11,555 / 11,555 | 33.83 | 3.0 / 33.0 |
| math-sensor | 668 | 1,159,680 / 18,750 | 19,567 | 10,652 / 10,652 | 31.21 | 2.0 / 28.0 |
| text-tls | 965 | 1,315,680 / 23,100 | 19,386 | 10,733 / 10,733 | 31.33 | 2.0 / 22.0 |
| mixed-fields | 646 | 1,134,720 / 18,270 | 19,612 | 10,221 / 10,221 | 29.90 | 2.0 / 33.0 |
| code-archive | 769 | 1,214,400 / 20,210 | 19,687 | 10,822 / 10,822 | 31.78 | 2.0 / 28.0 |
| math-inventory | 766 | 1,238,400 / 20,470 | 19,150 | 11,536 / 11,536 | 33.88 | 2.0 / 24.0 |
| text-websocket | 636 | 1,053,600 / 17,230 | 19,598 | 10,381 / 10,381 | 30.38 | 3.0 / 32.0 |
| mixed-chinook | 548 | 1,028,160 / 16,150 | 20,796 | 11,421 / 11,421 | 33.20 | 3.0 / 54.0 |

Across measured task pairs, layer-aware main-demand cosine spans 0.1101–0.8177; JS divergence spans 0.1134–0.5727 bits. Exact pair/family rows and definitions are in analysis/trace-diversity.json. These describe routing overlap, not semantic independence or which category benefits from a future policy.

## Family-level descriptive coverage

Three tasks per family remain a small source-group sample. Context, source length and subtask differ; these rows describe demand and are not policy comparisons.

| Family | Groups / prior exposed | Complete windows | Main entries | Local / CPU / mapped % (entry-weighted) | Operating min |
|---|---:|---:|---:|---|---:|
| code/agent | 3 / 3 | 2132 | 3,503,520 | 92.50 / 6.59 / 0.91 | 6.43 |
| math/research | 3 / 3 | 2087 | 3,544,320 | 92.95 / 6.25 / 0.80 | 5.89 |
| structured/mixed | 3 / 0 | 1786 | 3,224,640 | 91.67 / 7.24 / 1.09 | 6.05 |
| text/translation | 3 / 1 | 2313 | 3,564,000 | 93.84 / 5.56 / 0.60 | 6.79 |

Decode mean CPU steal by task ranges 0.93–13.08%. This VM scheduling interference limits clean cost predictions; one trace per task cannot separate source effects from temporal system drift. Burstiness, inter-use distributions and all66task-pair routing comparisons are saved in analysis/trace-diversity.json.

Actual native evictions yield **97,123 observed victim returns** and **35,802 right-censored events** within finite tapes. This is sufficient to **begin a small, scoped victim-return study** using source-level splits and censored labels. It is not enough to establish universal generalization or exact counterfactual eviction regret. Dynamic heat/protection metadata is unavailable; prefix-derived last-use/count features and initial heat can be causal. Future next-use values are stored only in analysis/victim-return-labels.json under labels/evaluation.

Inter-use gaps are window differences between uses of one(layer, expert). Distinct-expert reuse distance counts unique experts in intervening same-layer windows, excluding endpoint batches. Simultaneous lanes are never given an invented serial order. Burstiness B=(sd(gaps)-mean(gaps))/(sd+mean) is computed only with at least two observed gaps. Native eviction occurs after the indexed main window's routed work; return search starts after it. Physical issue/publication nanoseconds remain measured cost, not logical decision order. Observation bounds and right censoring are saved; unrelated requests are never concatenated.

Output snippets and repeated-long-line counts are retained in the descriptive JSON and output-review.md. Output caps can truncate code/prose/JSON. Short completions and degeneration would remain labelled rather than trigger retries. No task was selected or removed because of its routing or oracle speedup.

## Repair, replay readiness and scope

Episode 6 exposed a legacy validator error on 179-token input: it inspected all 2051 QSA capacity cells, including unused zero tail. Native source explicitly sets min(n_kv,2051) active width. The corrected validator checks active width per lane with strict bounds, ascending order and uniqueness, preserving the complete tape. Original failure and original validator are archived. No model task was repeated or excluded. Episode 11 naturally stopped at EOS inside its final accepted verifier window. The native engine commits that whole prefix but emits only through EOS. A second bounded validator correction uses the header emission count, checks that discarded outputs belong solely to the last complete window, and verifies the actual final token is the configured EOS. Original failure/validator/tape are preserved; no rerun. Current validation covers FNV/SHA256, exact input/output IDs, MTP/window dependencies, coefficients and normal main routing conservation. These are structurally usable tapes with a validated capture substrate; no new per-task live replay or policy fidelity matrix was run.

Safe client cancellation is available, but the legacy tape intentionally rejects cancelled capture and may not flush a reusable tape. A future planned-time slice or hard-kill must be INVALID_TRACE unless a complete logical tape can be validated. This limitation is documented, not hidden by classifying a partial file as full replay. The recorded completed output-cap work can be replayed exactly for later A/B; sixty seconds per policy would compare different amounts of work.

Existing compatible historical tapes, including 256K extended material, are hash-verified immutable snapshots in provenance/compatible-existing-tapes.json. Their original wrappers/output budgets and prior exposure remain distinct from the natural core; they are not new 256K recordings.

## Runtime and future experiment pricing



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


The empirical envelope varies observed startup/warmup/shutdown components within each context and retains each task's observed request cost, plus5s per arm at the upper end. It is an estimate from this hardware/run, not a probabilistic guarantee. Phase caps provide a separate planning ceiling; preflight/validation allowance is additional. CPU/VM scheduling, OS cache, actual EOS and future policy work can change costs.

Screening task IDs: code-heg, math-rational, text-http, mixed-build. The predeclared roles choose them without inspecting routing or oracle benefit.

Four-policy reduced IDs: code-heg, math-rational. If the larger empirical envelope exceeds120min, this reduction is explicit; it does not delete the remaining corpus.

Three contemporary baseline arms per task can serve all comparisons within the same four-arm repetition block, with identical tape/work prefix, engine/config/protocol and matched initial state. Correlation must be retained. Do not duplicate baselines per candidate or reuse stale historical controls, other engines, models or trajectories. Fourpolicies x3repetitions=12arms/task; baseline+onefinalist=6arms/task.

All new timings use recording hooks; original clean0.1.39 baseline is verified but not newly timed here. Prior short development recording was2.3986s decode/7.1197s request versus original2.1953s/6.1720s. Do not extrapolate that overhead as a universal correction.

Later A/B arms must replay the same validated completed logical tape prefix, including rejected speculative work, or use frozen output/work budgets. Giving each policy60s and comparing raw routed counts would compare different work. Natural output-limit slices do not imply task completion.

Short prompts remain short; a128K context limit does not imply128K input occupancy. No costs from unmeasured tasks are averaged into measured totals. Historical extended tapes have their original protocols and do not substitute for new clean timing.


## Handoff and limitations

Required artifacts are in this campaign: GOAL.md, DECISIONS.md, STATUS.md, progress.json/progress.jsonl, attempt-ledger.jsonl, workload audit/inventory/prompt catalog, public sources, benchmark manifest, trace-summary.csv, runtime budget JSON/Markdown, raw tapes/logs, validation/schema evidence, report and reproduce.md. Reusable scripts inspect prompts, check identities, record one task or frozen screening/core queues, validate traces, regenerate analysis and print progress. Later recordings use new reproduction directories and their own explicitly authorized deadline, without overwriting this campaign.

The useful result is an audited, source-grounded routing corpus with measured operational cost. It cannot identify a Golden Swap winner, a Python-specific speedup, a universal cache policy or universal predictor diversity. One physical VM, fixed task groups, shared source collections, prior exposed items, finite 16.8–24.5s output slices and instrumented timing limit generality. Development screening was fixed by provenance/family/length/runtime before inspecting routing. No source class was discarded as unhelpful.

Deferred items: none of the defined core tasks. Unmeasured costs: clean-baseline timings, longer natural completions, new per-task live replay and future policy execution; these remain separate unknowns. No training or further campaign follows automatically.

Exact commands:

```bash
python3 scripts/inspect_prompt.py code-archive --full
python3 scripts/progress.py
/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python scripts/run.py check
/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python scripts/validate_traces.py raw/code-archive
```

Owned processes are stopped and cleanup is checked in completion-audit.json. Final hashes are in artifact-manifest.json. No push, PR, paid services, normal serving change or prompt upload.

PHASE0_READY
