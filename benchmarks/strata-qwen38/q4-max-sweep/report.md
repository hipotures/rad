# Q4 max sweep — campaign in progress

Frozen Strata HEAD: `9259cad4cfa3543cd3b8decab5962672b968c649`, runtime version0.1.31. No downloads, quant changes, experts.bin, engine edits or git commits. Exact pinned four-shard model and existing BF16-compatible pack. Environment, original configurations, help/docs and source references archived alongside this report.

## Verified so far

Native Q4 starts on both RTX4090s using ordinary full host arena and automatic layer split, WITHOUT resident-cpu-experts or resident-budget-gib. Runtime loads71.73GiB, `cudaHostRegister PORTABLE ok`. AutoK24, layers0–23 on GPU0 and24–47 on GPU1. Runtime cache5955slots/17.39GiB on GPU0 and5420slots/15.81GiB on GPU1; predicted routed coverage~97.8%. Actual auto prefill chunk8192, temporarily borrows cache slots on BOTH cards (older docs describe a different buffer policy).

8K/64-token smoke: coherent source explanation, MTP active, no OOM. Three measured64K runs: actual63400, output256, no prompt reuse. PP3179.5/3179.6/3179.5t/s; TG100.7/104.3/117.5t/s. MedianPP3179.5, TG104.3. Decode expert file fetches0 for all three. RAM arena reads are NOT counted in the FileExpertSource's RAM-complement counter, so ram_blobs0 does not imply lack of a host arena.

These are preliminary results, not a selected best configuration. Adaptive cache evolves over requests; chronological repetitions are saved. The manual split and initial helper sweeps are complete. Refined helper capacity, calibration/MTP/KV/prefill/final context/long decode/agentic/compaction/quality experiments remain incomplete.

## Measurement limits

Expert-file request counters refer to decode; startup, prefill/refill and PLE are separate. /srv/ai is virtiofs; logical file counters and guest I/O do not directly prove host SSD traffic. GPU per-stage hit counts and PLE-specific byte counts will be null where upstream exposes no counter; combined decode hit rates and per-layer CPU/PCIe expert work are preserved. RSS includes file mappings; physical RAM use is total minus MemAvailable, with PSS additionally sampled from phase2 onward. Phase1 uses the original1-second sampler (RSS, CPU, RAM, both GPU power/utilization/VRAM, API metrics including aggregate PCIe).

## Telemetry correction during manual split screening

An observed `memory_full_info()` PSS read took0.655s for73.12GiB. Scanning it every second disturbed the workload. Initial affected T3 screens are preserved under `raw/pss-1s-excluded/` with their original raw/config/log/telemetry files and are EXCLUDED from summary and selection. No engine change was made. All affected manual screens were repeated. Current PSS snapshots are captured between requests, outside client and engine PP/TG/TTFT timers; cached snapshot values have timestamps. RSS, physical RAM, CPU, GPU power/utilization/clocks/VRAM and normal API counters continue at~1Hz.

The repeated K16 screen reached88.6TGt/s (old excluded46.5). TOP3 confirmations have now completed: K22 medianTG112.5/PP2928.3; K26 TG106.3/PP3135.9; K32 TG80.7/PP2470.1 (three measured runs each). Best initial helper confirmations: layer5806slots TG67.8/PP1556.7; stripe5225slots TG66.8/PP1557.8. Exact native blob sizing refines the conservative5806slot bound to7387slots with2GiB reserved onGPU1; this additional sweep is still running. These results select further tuning, not a finished best configuration. Primary artifact `summary.json` remains IN_PROGRESS. Preliminary plots with missing phases are not completion evidence.

## IQ3 baseline reuse verification

`raw/IQ3_S-reuse-verification.json` verifies the original12 measured requests (3 per actual31400/63400/127000/259500),256 generated tokens,no cache reuse,matching frozenHEAD0.1.31 and matching published medians. The original model/engine/KV/MTP/split configuration is retained in `configs/IQ3_S-best-runtime.json`; `configs/run-IQ3_S-best.sh` starts an isolated server on18084. Only port/log path changed; it has not been launched during this Q4 campaign.

## Topology and calibration checkpoint

K22 static/adaptive comparison completed: medianTG86.0 versus111.4t/s, PP2925.8 versus2928.0t/s (3runs each actual~63400/output256/reuse0). Default-adaptive selected. Upstream calibrator completed in411s: defaults15workers/PCIe.28/min-p.5; selected10workers/PCIe0/min-p.7. Its short-prompt confirmation medians are94.7 vs104.4t/s, not64K campaign rates. Local64K validation, MTP, KV, prefill, finalist matrices and extended/quality workloads remain incomplete.

## MTP methodology correction

The original long-task prompt allowed an exploration/tool-use preamble. MTPspec3 measured output stopped naturally after91tokens (requested1024), metrics.finish=stop, no engine crash/OOM. All original MTP arms, including successful arms, are archived and EXCLUDED in `raw/mtp-original-task-excluded/`. The complete MTP gate is repeated with one uniform offline/no-tools40-section task. Warmups and measured outputs must actually reach1024. Full SSE chunks/tool-call events are saved outside request clocks. Existing quality messages/system/sampling/caps remain unchanged.

Local256-token winner8workers/PCIe.2/min-p.3 confirmed104.1TGt/s, below default-adaptive111.4. A same1024-token default control (warmup+3) will therefore gate selection before KV, rather than automatically retain slower tuned settings.
