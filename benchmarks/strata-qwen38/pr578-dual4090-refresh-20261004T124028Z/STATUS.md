# Strata PR578 — COMPLETE_WITH_DOCUMENTED_NEGATIVES

## Running

```json
null
```

## Completed

- Current GitHub snapshot
- Two fresh same-main checkouts
- Upstream integration verified; no second merge
- Local IQ3_S unchanged size/mtime verified
- Literal replay payloads copied
- Hardware campaign: 434 raw records /425 valid sustained repetitions; independent final audit PASS 2026-10-04T16:06:39Z
- original upstream pilot
- boundary-only diagnostics build
- fresh helper auto sizing
- 10 paired correctness prompts
- Both identical CUDA sm89 builds; explicit native expert support
- Native72-test suites reviewed, Python268 OK7skip; environmental limitations preserved
- Two code budget extensions completed, binary-search tests passed
- Instrumented timing failed<=1% gate: headline policy switches to unmodified upstream binaries, diagnostics kept separate
- primary 32K sweep
- cache progression diagnostics
- secondary lookup ON
- fresh-server confirmations or documented >5% gap
- steady decode
- final context matrix
- clean32K replacement
- Current-API tokenizer correction verified; literal payload text retained
- Fresh clean32K helper cell replaces background-analysis-excluded cell
- Final context matrix:24 valid controlled requests, actual31400/63402/127002/259507
- Independent final audit PASS with documented negative/availability limits
- Final report, summary CSV/JSON and code snapshots saved

## Pending


## Current winners

```json
{
  "best_layer_split": {
    "config": "LS-B",
    "actual_prompt": 31400,
    "valid_runs": 3,
    "three_run_headline_complete": true,
    "statistic_basis": "median_of_3_valid_runs",
    "raw_paths": [
      "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/LS-B-32K-run1.json",
      "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/LS-B-32K-run2.json",
      "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/LS-B-32K-run3.json"
    ],
    "pp_tps": 4727.1,
    "pp_tps_min": 2173.4,
    "pp_tps_max": 4729.8,
    "tg_tps": 156.2,
    "tg_tps_min": 152.6,
    "tg_tps_max": 156.7,
    "ttft_s": 6.720342212996911,
    "acceptance_pct": 76.6355140186916,
    "mean_accepted_length": 1.7157894736842105,
    "verify_windows": 95,
    "committed_tokens_per_window": 2.69,
    "mean_verify_window_latency_ms": 17.29,
    "suffix_accepted": 0,
    "helper_entries": null,
    "helper_hit_pct_of_all_routed": null,
    "cpu_fallback_pct_of_all_routed": null,
    "offloaded_routed_entries": 22,
    "total_routed_entries": 146880,
    "helper_returned_bytes": null,
    "helper_returned_bytes_per_generated_token": null,
    "helper_returned_bytes_per_layer_launch": null,
    "helper_wait_ms": null,
    "primary_hits_per_layer_window": 32.82,
    "pcie_experts_per_layer_window": 0.0,
    "cpu_fallback_entries_estimate": 1117.4399999999998,
    "cpu_fallback_entries": 1135,
    "primary_hits_exact": 145032,
    "primary_pcie_experts_exact": null,
    "cpu_missed_experts_exact": null,
    "cpu_activation_quant_ms": null,
    "cache_overlap": null,
    "decode_cpu_system_pct": 68.1,
    "decode_cpu_system_pct_peak": 99.2,
    "decode_cpu_process_pct": 1084.25,
    "decode_cpu_process_pct_peak": 1577.6,
    "gpu0_decode_util_pct": 40.0,
    "gpu1_decode_util_pct": 54.0,
    "gpu0_decode_util_pct_peak": 49.0,
    "gpu1_decode_util_pct_peak": 54.0,
    "gpu0_decode_power_w": 145.315,
    "gpu1_decode_power_w": 191.94,
    "gpu0_decode_power_w_peak": 185.51,
    "gpu1_decode_power_w_peak": 208.89,
    "gpu0_decode_pcie_rx_MBps": 2840.0,
    "gpu0_decode_pcie_tx_MBps": 91.0,
    "gpu1_decode_pcie_rx_MBps": 50.666666666666664,
    "gpu1_decode_pcie_tx_MBps": 31.0,
    "peak_rss_gib": 54.59064865112305,
    "peak_ram_used_gib": 58.89884567260742,
    "peak_vram0_gib": 23.275390625,
    "peak_vram1_gib": 23.392578125,
    "draft_tokens": 214,
    "accepted_tokens": 163,
    "reported_expert_hit_rate": 0.993,
    "reported_primary_cache_hits": 145032,
    "reported_primary_cache_lookups": 146798,
    "reported_primary_cache_nonhits": 1135,
    "logical_expert_file_blobs": null,
    "logical_expert_file_MB": null,
    "initial_primary_slot_capacity": 10112,
    "initial_helper_slot_capacity": 0,
    "selected_layer_split_K": 25
  },
  "best_optimized_helper": {
    "config": "H-OPT-FIXED",
    "actual_prompt": 31400,
    "valid_runs": 3,
    "three_run_headline_complete": true,
    "statistic_basis": "median_of_3_valid_runs",
    "raw_paths": [
      "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-FIXED-32K-run1.json",
      "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-FIXED-32K-run2.json",
      "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-FIXED-32K-run3.json"
    ],
    "pp_tps": 2420.2,
    "pp_tps_min": 2017.5,
    "pp_tps_max": 2422.1,
    "tg_tps": 103.8,
    "tg_tps_min": 95.8,
    "tg_tps_max": 104.0,
    "ttft_s": 13.051360248005949,
    "acceptance_pct": 79.08163265306122,
    "mean_accepted_length": 1.7052631578947368,
    "verify_windows": 95,
    "committed_tokens_per_window": 2.69,
    "mean_verify_window_latency_ms": 26.82,
    "suffix_accepted": 0,
    "helper_entries": 18555,
    "helper_hit_pct_of_all_routed": 12.757838283828383,
    "cpu_fallback_pct_of_all_routed": 0.3874491869918699,
    "offloaded_routed_entries": 23574,
    "total_routed_entries": 145440,
    "helper_returned_bytes": 144703488.0,
    "helper_returned_bytes_per_generated_token": 565248.0,
    "helper_returned_bytes_per_layer_launch": 34659.518083832336,
    "helper_wait_ms": 119.0,
    "primary_hits_per_layer_window": 27.4,
    "pcie_experts_per_layer_window": 1.23,
    "cpu_fallback_entries_estimate": 592.8,
    "cpu_fallback_entries": 610,
    "primary_hits_exact": 121147,
    "primary_pcie_experts_exact": null,
    "cpu_missed_experts_exact": null,
    "cpu_activation_quant_ms": null,
    "cache_overlap": null,
    "decode_cpu_system_pct": 76.55000000000001,
    "decode_cpu_system_pct_peak": 87.7,
    "decode_cpu_process_pct": 1213.55,
    "decode_cpu_process_pct_peak": 1394.6,
    "gpu0_decode_util_pct": 99.5,
    "gpu1_decode_util_pct": 6.0,
    "gpu0_decode_util_pct_peak": 100.0,
    "gpu1_decode_util_pct_peak": 7.0,
    "gpu0_decode_power_w": 217.67000000000002,
    "gpu1_decode_power_w": 78.745,
    "gpu0_decode_power_w_peak": 245.4,
    "gpu1_decode_power_w_peak": 80.56,
    "gpu0_decode_pcie_rx_MBps": 3677.0,
    "gpu0_decode_pcie_tx_MBps": 603.0,
    "gpu1_decode_pcie_rx_MBps": 88.0,
    "gpu1_decode_pcie_tx_MBps": 81.0,
    "peak_rss_gib": 53.74453353881836,
    "peak_ram_used_gib": 58.020355224609375,
    "peak_vram0_gib": 23.310546875,
    "peak_vram1_gib": 23.34375,
    "draft_tokens": 211,
    "accepted_tokens": 162,
    "reported_expert_hit_rate": 0.995,
    "reported_primary_cache_hits": 121147,
    "reported_primary_cache_lookups": 121866,
    "reported_primary_cache_nonhits": 610,
    "logical_expert_file_blobs": null,
    "logical_expert_file_MB": null,
    "initial_primary_slot_capacity": 8586,
    "initial_helper_slot_capacity": 11796,
    "selected_layer_split_K": null
  },
  "top2": [
    {
      "config": "LS-B",
      "actual_prompt": 31400,
      "valid_runs": 3,
      "three_run_headline_complete": true,
      "statistic_basis": "median_of_3_valid_runs",
      "raw_paths": [
        "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/LS-B-32K-run1.json",
        "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/LS-B-32K-run2.json",
        "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/LS-B-32K-run3.json"
      ],
      "pp_tps": 4727.1,
      "pp_tps_min": 2173.4,
      "pp_tps_max": 4729.8,
      "tg_tps": 156.2,
      "tg_tps_min": 152.6,
      "tg_tps_max": 156.7,
      "ttft_s": 6.720342212996911,
      "acceptance_pct": 76.6355140186916,
      "mean_accepted_length": 1.7157894736842105,
      "verify_windows": 95,
      "committed_tokens_per_window": 2.69,
      "mean_verify_window_latency_ms": 17.29,
      "suffix_accepted": 0,
      "helper_entries": null,
      "helper_hit_pct_of_all_routed": null,
      "cpu_fallback_pct_of_all_routed": null,
      "offloaded_routed_entries": 22,
      "total_routed_entries": 146880,
      "helper_returned_bytes": null,
      "helper_returned_bytes_per_generated_token": null,
      "helper_returned_bytes_per_layer_launch": null,
      "helper_wait_ms": null,
      "primary_hits_per_layer_window": 32.82,
      "pcie_experts_per_layer_window": 0.0,
      "cpu_fallback_entries_estimate": 1117.4399999999998,
      "cpu_fallback_entries": 1135,
      "primary_hits_exact": 145032,
      "primary_pcie_experts_exact": null,
      "cpu_missed_experts_exact": null,
      "cpu_activation_quant_ms": null,
      "cache_overlap": null,
      "decode_cpu_system_pct": 68.1,
      "decode_cpu_system_pct_peak": 99.2,
      "decode_cpu_process_pct": 1084.25,
      "decode_cpu_process_pct_peak": 1577.6,
      "gpu0_decode_util_pct": 40.0,
      "gpu1_decode_util_pct": 54.0,
      "gpu0_decode_util_pct_peak": 49.0,
      "gpu1_decode_util_pct_peak": 54.0,
      "gpu0_decode_power_w": 145.315,
      "gpu1_decode_power_w": 191.94,
      "gpu0_decode_power_w_peak": 185.51,
      "gpu1_decode_power_w_peak": 208.89,
      "gpu0_decode_pcie_rx_MBps": 2840.0,
      "gpu0_decode_pcie_tx_MBps": 91.0,
      "gpu1_decode_pcie_rx_MBps": 50.666666666666664,
      "gpu1_decode_pcie_tx_MBps": 31.0,
      "peak_rss_gib": 54.59064865112305,
      "peak_ram_used_gib": 58.89884567260742,
      "peak_vram0_gib": 23.275390625,
      "peak_vram1_gib": 23.392578125,
      "draft_tokens": 214,
      "accepted_tokens": 163,
      "reported_expert_hit_rate": 0.993,
      "reported_primary_cache_hits": 145032,
      "reported_primary_cache_lookups": 146798,
      "reported_primary_cache_nonhits": 1135,
      "logical_expert_file_blobs": null,
      "logical_expert_file_MB": null,
      "initial_primary_slot_capacity": 10112,
      "initial_helper_slot_capacity": 0,
      "selected_layer_split_K": 25
    },
    {
      "config": "H-OPT-FIXED",
      "actual_prompt": 31400,
      "valid_runs": 3,
      "three_run_headline_complete": true,
      "statistic_basis": "median_of_3_valid_runs",
      "raw_paths": [
        "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-FIXED-32K-run1.json",
        "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-FIXED-32K-run2.json",
        "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-FIXED-32K-run3.json"
      ],
      "pp_tps": 2420.2,
      "pp_tps_min": 2017.5,
      "pp_tps_max": 2422.1,
      "tg_tps": 103.8,
      "tg_tps_min": 95.8,
      "tg_tps_max": 104.0,
      "ttft_s": 13.051360248005949,
      "acceptance_pct": 79.08163265306122,
      "mean_accepted_length": 1.7052631578947368,
      "verify_windows": 95,
      "committed_tokens_per_window": 2.69,
      "mean_verify_window_latency_ms": 26.82,
      "suffix_accepted": 0,
      "helper_entries": 18555,
      "helper_hit_pct_of_all_routed": 12.757838283828383,
      "cpu_fallback_pct_of_all_routed": 0.3874491869918699,
      "offloaded_routed_entries": 23574,
      "total_routed_entries": 145440,
      "helper_returned_bytes": 144703488.0,
      "helper_returned_bytes_per_generated_token": 565248.0,
      "helper_returned_bytes_per_layer_launch": 34659.518083832336,
      "helper_wait_ms": 119.0,
      "primary_hits_per_layer_window": 27.4,
      "pcie_experts_per_layer_window": 1.23,
      "cpu_fallback_entries_estimate": 592.8,
      "cpu_fallback_entries": 610,
      "primary_hits_exact": 121147,
      "primary_pcie_experts_exact": null,
      "cpu_missed_experts_exact": null,
      "cpu_activation_quant_ms": null,
      "cache_overlap": null,
      "decode_cpu_system_pct": 76.55000000000001,
      "decode_cpu_system_pct_peak": 87.7,
      "decode_cpu_process_pct": 1213.55,
      "decode_cpu_process_pct_peak": 1394.6,
      "gpu0_decode_util_pct": 99.5,
      "gpu1_decode_util_pct": 6.0,
      "gpu0_decode_util_pct_peak": 100.0,
      "gpu1_decode_util_pct_peak": 7.0,
      "gpu0_decode_power_w": 217.67000000000002,
      "gpu1_decode_power_w": 78.745,
      "gpu0_decode_power_w_peak": 245.4,
      "gpu1_decode_power_w_peak": 80.56,
      "gpu0_decode_pcie_rx_MBps": 3677.0,
      "gpu0_decode_pcie_tx_MBps": 603.0,
      "gpu1_decode_pcie_rx_MBps": 88.0,
      "gpu1_decode_pcie_tx_MBps": 81.0,
      "peak_rss_gib": 53.74453353881836,
      "peak_ram_used_gib": 58.020355224609375,
      "peak_vram0_gib": 23.310546875,
      "peak_vram1_gib": 23.34375,
      "draft_tokens": 211,
      "accepted_tokens": 162,
      "reported_expert_hit_rate": 0.995,
      "reported_primary_cache_hits": 121147,
      "reported_primary_cache_lookups": 121866,
      "reported_primary_cache_nonhits": 610,
      "logical_expert_file_blobs": null,
      "logical_expert_file_MB": null,
      "initial_primary_slot_capacity": 8586,
      "initial_helper_slot_capacity": 11796,
      "selected_layer_split_K": null
    }
  ],
  "top2_within5pct": false
}
```

## Excluded runs

```json
[
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/LS-A-32K-run2.json",
    "reason": "INVALID_REQUEST",
    "generated_tokens": 52
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-FIXED-DIAG-32K-run1.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-FIXED-DIAG-32K-run2.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-FIXED-DIAG-32K-run3.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/UPSTREAM-PR-AUTO-PILOT-32K-run1.json",
    "reason": "PILOT_UNCONFIRMED",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-OVERHEAD-DIAG-ON-FRESH3-32K-run1.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-OVERHEAD-DIAG-ON-FRESH3-32K-run2.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-OVERHEAD-DIAG-ON-FRESH3-32K-run3.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/PR-LS-32K-run2.json",
    "reason": "INVALID_REQUEST",
    "generated_tokens": 52
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-STARTUP-DIAG-ON-32K-run1.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-STARTUP-DIAG-ON-32K-run2.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-STARTUP-DIAG-ON-32K-run3.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-OVERHEAD-DIAG-OFF-FRESH2-32K-run1.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-OVERHEAD-DIAG-OFF-FRESH2-32K-run2.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-OVERHEAD-DIAG-OFF-FRESH2-32K-run3.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-OVERHEAD-DIAG-OFF-FRESH3-32K-run1.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-OVERHEAD-DIAG-OFF-FRESH3-32K-run2.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-OVERHEAD-DIAG-OFF-FRESH3-32K-run3.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-STARTUP-DIAG-OFF-32K-run1.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-STARTUP-DIAG-OFF-32K-run2.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-STARTUP-DIAG-OFF-32K-run3.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OLD-DIAG-32K-run1.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OLD-DIAG-32K-run2.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OLD-DIAG-32K-run3.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-FIXED-FINAL-TOKFIX-32K-run1.json",
    "reason": "EXCLUDED_BACKGROUND_ANALYSIS_OR_SUPERSEDED_CELL",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-FIXED-FINAL-TOKFIX-32K-run2.json",
    "reason": "EXCLUDED_BACKGROUND_ANALYSIS_OR_SUPERSEDED_CELL",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-FIXED-FINAL-TOKFIX-32K-run3.json",
    "reason": "EXCLUDED_BACKGROUND_ANALYSIS_OR_SUPERSEDED_CELL",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-OVERHEAD-DIAG-ON-FRESH2-32K-run1.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-OVERHEAD-DIAG-ON-FRESH2-32K-run2.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/H-OPT-OVERHEAD-DIAG-ON-FRESH2-32K-run3.json",
    "reason": "DIAGNOSTIC_INSTRUMENTATION",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/LS-B-FINAL-32K-run1.json",
    "reason": "SUPERSEDED_PARTIAL_MATRIX",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/LS-B-FINAL-32K-run2.json",
    "reason": "SUPERSEDED_PARTIAL_MATRIX",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/LS-B-FINAL-32K-run3.json",
    "reason": "SUPERSEDED_PARTIAL_MATRIX",
    "generated_tokens": 256
  },
  {
    "raw": "/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw/LS-B-FINAL-64K-run1.json",
    "reason": "INVALID_REQUEST",
    "generated_tokens": 256
  },
  {
    "raw": "raw/H-OLD-LOOKUP-ON-32K-warmup.json",
    "reason": "INVALID_NATURAL_EOS_WARMUP51_OF64; entire secondary stage retried with equal32 warmup"
  }
]
```

## Next exact action

None. Completed controlled campaign; retain layer split for measured workloads. Review report.md and audit-refresh.json before any new experiment.

Full authorized scope: PLAN.md. Both builds use frozen upstream main and local PR snapshot.
