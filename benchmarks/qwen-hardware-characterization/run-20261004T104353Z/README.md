# VM hardware and immutable-expert movement characterization

This is an isolated synthetic hardware study. It does not alter Strata, model weights, existing deployments, GPU configuration, or mounts. All documentation and data are English.

Run or resume:

```bash
/srv/ai/benchmarks/qwen-hardware-characterization/run_campaign.sh
/srv/ai/benchmarks/qwen-hardware-characterization/run_campaign.sh --resume /srv/ai/benchmarks/qwen-hardware-characterization/run-20261004T103125Z
# Narrow rerun: completed successful repetitions are preserved, not repeated.
/srv/ai/benchmarks/qwen-hardware-characterization/run_campaign.sh --resume RUN_DIRECTORY --only SCENARIO_ID
```

To deliberately obtain fresh independent measurements, start a new timestamped campaign. Never edit an old code/config hash to bypass resume checks after formal execution.

Environment: BENCH_ROOT, BENCH_DATA_DIR, MAX_CAMPAIGN_SECONDS (21600), FORMAL_SECONDS (60), WARMUP_SECONDS (15), FORMAL_REPEATS (3), MAX_STORAGE_WRITE_GIB (512). The bounded matrix uses 20-second supporting windows, and minute-long H2D expert/interference headline windows. All performance repetitions are at least ten seconds. Input defaults and effective per-scenario settings are in campaign_config.json and plan.json.

The user explicitly requested comparison of /srv/ai (virtiofs) and /home/user/DEV/test20261001_1 (ext4 on a virtual block device). Private, uniquely named scratch directories hold 16 GiB seeded non-sparse corpora and separate 256 MiB write-control files. Creation is exclusive. Files are retained. No raw devices, global cache drops, host memory pressure, remounts, privilege changes, or deletion of previous runs. The conservative write ledger includes preparation, warmup, and tests; fio write traces and native counters record actual logical volume where available. A 512 GiB ceiling and max(32 GiB,15% capacity) filesystem reserve are enforced. All GPU operations reserve at least 3 GiB, host allocations remain far below the 64 GiB/50% available cap, and MemAvailable reserves max(16 GiB,15% MemTotal). Thermal abort is 80 C. Only owned child process groups can be terminated.

A supervisor enforces a 180-second repetition deadline and saves JSONL after each repetition. SIGINT/SIGTERM stops scheduling and drains/terminates only owned children. Uninterruptible I/O stops scheduling without host recovery attempts. progress.json is atomically replaced. Successful repetitions are not repeated on resume. Keep launch logs open: progress is emitted every five seconds. The campaign deadline is durable and does not reset on resume.

Dependencies are local: CUDA 13.4, GCC 15.2, OpenMP, cuBLAS, pinned fio 3.43, and a uv-created Python environment. No system package upgrades. Exact tool commits, help, build commands, executable hashes, and code snapshots are retained. Build native code with:

```bash
/usr/local/cuda/bin/nvcc -O3 -std=c++17 -arch=sm_89 -Xcompiler=-fopenmp -Xcompiler=-pthread src/hwbench.cu -lcublas -o hwbench
```

Correctness checks compare full completed CUDA buffers to deterministic input after timing, verify sampled GEMM elements against a CPU calculation, check full RAM operation outputs, and validate slot publication sequence numbers. Pipeline buffers cannot be reused until their stream completes. Throughput uses completed batches and host monotonic wall time, never cross-device CUDA timestamps. Batch latency samples use bounded reservoir sampling. Allocation/registration/first touch/process launches are reported separately. Small-GEMM cases are dispatch/cache-sensitive; they do not represent streaming DRAM/VRAM bandwidth.

Pinned bridges count application bytes once per delivered leg and report two physical logical legs per one-way bridged payload. No P2P is forced when capability checks fail. GPU-local and CPU STREAM read/write byte totals are estimated logical traffic, not hardware memory-controller counters. Direct I/O through a guest or virtiofs does not prove a cold host SSD. These paths must be retested after attachment changes. Nondestructive default data preparation can populate caches; first pass means first process read after preparation, not cold media.

Telemetry is approximately 1 Hz (5-second interval for the low-cadence control), includes RSS and ordinary /proc counters, and never polls PSS. GPU utilization is kernel-active percentage, not SM occupancy. PCIe dmon is supplementary and may be unsupported. Synthetic FLOP/s and bytes/s are never called Qwen tokens/s.

This run includes separately hashed immutable-store and rolling-monitor follow-ups. The main native binary/orchestrator are frozen, and follow-ups wait for core completion. See followup-plan.json.
