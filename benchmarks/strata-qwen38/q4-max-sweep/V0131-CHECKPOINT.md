# Strata v0.1.31 checkpoint

Status: CANDIDATE_COMPLETE_PROCESS_STOPPED_AT_BOUNDARY. No new v0.1.31 phase authorized. All results preserved; this is not a completed campaign.

## A. Version
{
  "HEAD": "9259cad4cfa3543cd3b8decab5962672b968c649",
  "tracked_git_status": "",
  "version": "0.1.31",
  "version_evidence": "/srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/T2-auto-startup.json",
  "engine_sha256": "94e6f39e637b06d312c5b5880be2ad7a093c0914aa77375649ab3dd95551ee26",
  "build_info": {
    "CMakeCache": "/srv/ai/strata/build/CMakeCache.txt",
    "type": "Release",
    "CUDA_arch": "89",
    "CUDA_compiler": "/usr/local/cuda/bin/nvcc"
  },
  "environment_evidence": "/srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/environment.json",
  "CUDA": "nvcc: NVIDIA (R) Cuda compiler driver\nCopyright (c) 2005-2026 NVIDIA Corporation\nBuilt on Tue_Sep_01_08:45:21_PDT_2026\nCuda compilation tools, release 13.4, V13.4.92\nBuild cuda_13.4.r13.4/compiler.38855100_0",
  "driver": "615.71.09\n615.71.09"
}

## B. Actually performed
| Phase | Status | Measured / all requests | Best observed TG / PP | Raw evidence |
|---|---|---:|---|---|
| single GPU resident | COMPLETE | 1 / 2 | T0-control n=1 out=256: 43.70 / 1534.70 | /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/T0-control-run1.json |
| single GPU full arena | COMPLETE | 3 / 5 | T1-arena n=3 out=256: 66.10 / 1557.70 | /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/T1-arena-run1.json |
| 2 GPU auto split | COMPLETE | 3 / 5 | T2-auto n=3 out=256: 104.30 / 3179.50 | /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/T2-auto-run1.json |
| manual K screening | COMPLETE | 9 / 18 | T3-K32 n=1 out=256: 96.40 / 2160.90 | /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/T3-K32-run1.json |
| TOP3 K confirmations | COMPLETE | 9 / 15 | T3-K22-confirm n=3 out=256: 112.50 / 2928.30 | /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/T3-K22-confirm-run1.json |
| helper stripe/layer and capacity | COMPLETE | 26 / 49 | T4-layer-5806-confirm n=3 out=256: 67.80 / 1556.70 | /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/T4-layer-5806-confirm-run1.json |
| static/adaptive | COMPLETE | 6 / 10 | adapt-adaptive n=3 out=256: 111.40 / 2928.00 | /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/adapt-adaptive-run1.json |
| worker screening | COMPLETE | 6 / 12 | tune-workers-8 n=1 out=256: 101.30 / 2233.50 | /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/tune-workers-8-run1.json |
| PCIe fraction screening | COMPLETE | 2 / 4 | tune-pcie-0.2 n=1 out=256: 98.60 / 2233.80 | /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/tune-pcie-0.2-run1.json |
| min-p screening | COMPLETE | 3 / 6 | tune-minp-0.3 n=1 out=256: 99.30 / 2142.20 | /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/tune-minp-0.3-run1.json |
| local confirmation | COMPLETE | 3 / 5 | tune-best-confirm n=3 out=256: 104.10 / 2921.00 | /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/tune-best-confirm-run1.json |
| MTP and matched control | COMPLETE | 20 / 36 | MTP-spec3-confirm n=3 out=1024: 111.50 / 2917.10 | /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/MTP-spec3-confirm-run1.json |
| KV matrix | COMPLETE | 16 / 28 | KV-int8-stream n=2 out=256: 99.05 / 2839.00 | /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/KV-int8-stream-127000-run1.json |
| prefill chunk | COMPLETE | 13 / 26 | prefill-auto-confirm n=3 out=256: 100.80 / 3014.60 | /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/prefill-auto-confirm-127000-run1.json |
| final matrices | COMPLETE | 24 / 34 | FINAL-A n=3 out=256: 103.90 / 2424.00 | /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/FINAL-A-31400-run1.json |
| long decode | COMPLETE | 4 / 5 | LONG-FINAL-A n=2 out=4096: 93.05 / 2780.20 | /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/LONG-FINAL-A-64K-4096-greedy.json |
| agentic | PARTIAL | 11 / 11 | AGENT-63400 n=1 out=1024: 97.70 / 404.60 | /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/AGENT-63400-turn4.json |
| compaction | NOT_EXECUTED | 0 / 0 | — | Missing |
| quality | NOT_EXECUTED | 0 / 0 | — | Missing |
| needle | NOT_EXECUTED | 0 / 0 | — | Missing |

Calibrator COMPLETE: /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/calibration.json settings {'--pcie-frac': '0.00', '--spec-min-p': '0.70', '--pool-workers': '10'}

All per-candidate counts, medians, actual context/output and raw request paths are in V0131-CHECKPOINT.json. Best TG across distinct tasks is not a controlled A/B. T5 is the same supported ArenaExpertSource as T1/T2, not an additional duplicated run.

## C. Excluded preserved results
- **EXCLUDED_TELEMETRY_PSS**: /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/pss-1s-excluded; 14 request results. Preserved. 1Hz PSS scans of ~73GiB arena took ~0.65s, perturbing timing.
- **EXCLUDED_INCOMPLETE_OUTPUT**: /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/mtp-original-task-excluded; 14 request results. See archived reason/logs; not a completed candidate.
- **EXCLUDED_INCOMPLETE_AGENTIC_SESSION**: /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/agentic-short-eos-excluded; 6 request results. See archived reason/logs; not a completed candidate.
- **EXCLUDED_INCOMPLETE_AGENTIC_SESSION**: /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/agentic-distinct-files-short-eos-excluded; 5 request results. See archived reason/logs; not a completed candidate.
- **EXCLUDED_EXTERNAL_DRIVER_INTERRUPTION**: /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/interrupted-driver-20261001; 2 request results. See archived reason/logs; not a completed candidate.

## D. Verified winners
- T3-K22-confirm: actual [63399, 63399, 63399], output 256, n=3; PP 2928.30, TG 112.50, TTFT 21.785s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/T3-K22-confirm-run1.json
- T3-K26-confirm: actual [63400, 63400, 63400], output 256, n=3; PP 3135.90, TG 106.30, TTFT 20.357s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/T3-K26-confirm-run1.json
- T3-K32-confirm: actual [63399, 63399, 63400], output 256, n=3; PP 2470.10, TG 80.70, TTFT 25.932s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/T3-K32-confirm-run1.json
- T4-layer-5806-confirm: actual [63400, 63400, 63400], output 256, n=3; PP 1556.70, TG 67.80, TTFT 40.882s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/T4-layer-5806-confirm-run1.json
- T4-stripe-5225-confirm: actual [63400, 63400, 63400], output 256, n=3; PP 1557.80, TG 66.80, TTFT 40.864s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/T4-stripe-5225-confirm-run1.json
- T4-stripe-3693-confirm: actual [63400, 63400, 63400], output 256, n=3; PP 1556.90, TG 66.20, TTFT 40.878s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/T4-stripe-3693-confirm-run1.json
- adapt-adaptive: actual [63400, 63399, 63400], output 256, n=3; PP 2928.00, TG 111.40, TTFT 21.790s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/adapt-adaptive-run1.json
- adapt-static: actual [63400, 63400, 63400], output 256, n=3; PP 2925.80, TG 86.00, TTFT 21.806s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/adapt-static-run1.json
- MTP-spec3-confirm: actual [63400, 63400, 63400], output 1024, n=3; PP 2917.10, TG 111.50, TTFT 21.872s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/MTP-spec3-confirm-run1.json
- MTP-spec5: actual [63400, 63400], output 1024, n=2; PP 2929.50, TG 107.60, TTFT 21.780s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/MTP-spec5-run1.json
- MTP-spec5-confirm: actual [63400, 63400, 63400], output 1024, n=3; PP 2928.00, TG 107.10, TTFT 21.796s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/MTP-spec5-confirm-run1.json
- MTP-spec3: actual [63400, 63400], output 1024, n=2; PP 2913.75, TG 105.20, TTFT 21.897s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/MTP-spec3-run1.json
- MTP-spec2: actual [63400, 63400], output 1024, n=2; PP 2905.45, TG 102.75, TTFT 21.969s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/MTP-spec2-run1.json
- MTP-best-local-minp-confirm: actual [63400, 63400, 63400], output 1024, n=3; PP 2916.00, TG 102.70, TTFT 21.890s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/MTP-best-local-minp-confirm-run1.json
- MTP-spec4: actual [63400, 63400], output 1024, n=2; PP 2906.10, TG 99.65, TTFT 21.989s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/MTP-spec4-run1.json
- MTP-default-baseline-confirm: actual [63400, 63400, 63400], output 1024, n=3; PP 2909.80, TG 91.00, TTFT 21.939s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/MTP-default-baseline-confirm-run1.json
- KV-int8-stream: actual [127000, 127000], output 256, n=2; PP 2839.00, TG 99.05, TTFT 44.993s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/KV-int8-stream-127000-run1.json
- KV-k8v4: actual [127000, 127000], output 256, n=2; PP 3004.35, TG 97.45, TTFT 42.540s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/KV-k8v4-127000-run1.json
- KV-k8v4: actual [259500, 259500], output 256, n=2; PP 3179.80, TG 96.50, TTFT 82.115s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/KV-k8v4-259500-run1.json
- KV-int8-stream: actual [259500, 259500], output 256, n=2; PP 2883.35, TG 92.90, TTFT 90.505s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/KV-int8-stream-259500-run1.json
- KV-q4_0: actual [127000, 127000], output 256, n=2; PP 3025.30, TG 92.85, TTFT 42.289s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/KV-q4_0-127000-run1.json
- KV-int8-full: actual [259500, 259500], output 256, n=2; PP 3162.25, TG 89.00, TTFT 82.581s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/KV-int8-full-259500-run1.json
- KV-int8-full: actual [127000, 127000], output 256, n=2; PP 2955.70, TG 88.30, TTFT 43.502s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/KV-int8-full-127000-run1.json
- KV-q4_0: actual [259500, 259500], output 256, n=2; PP 3118.55, TG 87.20, TTFT 84.064s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/KV-q4_0-259500-run1.json
- FINAL-A: actual [31400, 31400, 31400], output 256, n=3; PP 2424.00, TG 103.90, TTFT 13.035s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/FINAL-A-31400-run1.json
- FINAL-A: actual [63400, 63400, 63399], output 256, n=3; PP 2793.20, TG 98.70, TTFT 22.837s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/FINAL-A-63400-run1.json
- FINAL-A: actual [259500, 259500, 259500], output 256, n=3; PP 3196.60, TG 92.10, TTFT 82.369s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/FINAL-A-259500-run1.json
- FINAL-A: actual [127000, 127000, 127000], output 256, n=3; PP 2956.70, TG 86.90, TTFT 43.210s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/FINAL-A-127000-run1.json
- FINAL-B: actual [63400, 63399, 63400], output 256, n=3; PP 1447.60, TG 63.20, TTFT 43.961s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/FINAL-B-63400-run1.json
- FINAL-B: actual [31400, 31400, 31400], output 256, n=3; PP 1418.40, TG 61.30, TTFT 22.244s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/FINAL-B-31400-run1.json
- FINAL-B: actual [127000, 127000, 127000], output 256, n=3; PP 1440.50, TG 60.20, TTFT 88.446s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/FINAL-B-127000-run1.json
- FINAL-B: actual [259500, 259500, 259500], output 256, n=3; PP 1428.10, TG 52.30, TTFT 182.332s. /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/raw/FINAL-B-259500-run1.json

## E. Remaining plan
Worker/PCIe/min-p, MTP, KV, prefill, final matrices and four long requests are already executed. They are not pending. The original completion audit has stale narrative entries; standalone raw evidence above takes precedence. Completed phases should be re-evaluated on v0.1.32 because runtime/kernel changes can change the optimum. No new v0.1.31 stages will start.

### Agentic multi-turn
11 uninterrupted turns from actual~64K and~128K, prefix reuse; initial1024 then256–1024 actual output, additions500–2000
Candidates: ['FINAL-A AGENT-63400 COMPLETE, do not rerun v0.1.31', 'FINAL-A AGENT-127000 not begun']; repeats: one full session per starting context; dependencies: current candidate terminal/boundary; no engine patch; repeat on v0.1.32: True.

### Compaction
Summarize actual saved coding-agent history at127000/250000 input to<=4096 output
Candidates: ['127000', '250000']; repeats: one per context; dependencies: completed saved agentic histories plus actual long requests/answers; repeat on v0.1.32: True.

### Quality parity
Exact three saved IQ3 requests; full outputs, no judge
Candidates: ['FINAL-A INT8 streaming', 'FINAL-A k8v4', 'IQ3 existing copies']; repeats: three exact prompts per Q4 config; dependencies: saved requests and selected configs; repeat on v0.1.32: True.

### Needle
Existing upstream harness with tokenizer-sized prompt
Candidates: ['31400', '127000', '259500']; repeats: depth10/50/90 each, seed7,9requests; dependencies: selected final config; repeat on v0.1.32: True.

### Prefill phase diagnostic
Use upstream STRATA_PREFILL_TIMING, excluded from speed ranking
Candidates: ['8K smoke64output', '127K256output']; repeats: one each; dependencies: all timed stages done/no engine; currently NOT_EXECUTED; repeat on v0.1.32: True.

### Final summaries/plots/report and audit
Regenerate full artifacts,15required plots+acceptance/resources,20answers and ready configs; inspect against raw evidence
Candidates: ['summarize.py', 'plots.py', 'render_report.py', 'audit.py']; repeats: one final generation and requirement audit; dependencies: remaining measurements; old artifacts preliminary; repeat on v0.1.32: True.

## Evidence and limitations
- Physical host SSD traffic invisible behind virtiofs; logical expert file counters are not physical SSD proof.
- Warm filesystem only; no safe physical cold-cache claim.
- MTP OFF unsupported by current native serve guard.
- Separate per-GPU routed hit/time-resolved cache/adaptive maps unavailable.
- Existing summary/report/plots are preliminary and campaign incomplete.

Original objective, audit, and every campaign Python script are preserved in checkpoint-plan/. SHA256 inventory is in JSON. Existing models, checkout and packs remain untouched.

## Final safe boundary and stop

AGENT-63400 COMPLETE:11 requests,23 history messages; all actual outputs813–1024. AGENT-127000 did not start. Engine exited via normal Session cleanup before the boundary watcher stopped the harness. Parent driver and stopped harness then terminated outside any request. Both GPUs verified free:1MiB each,0%utilization; no compute applications. Evidence: raw/v0131-safe-boundary.json and raw/v0131-process-stop.json.
