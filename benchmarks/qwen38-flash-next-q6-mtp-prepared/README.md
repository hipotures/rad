# Prerequisites

- Two idle RTX 4090 24 GB GPUs with the NVIDIA driver available through `nvidia-smi`.
- At least 140 GB available system RAM and 10 GiB free space under this directory.
- Python 3.11 or newer. The pinned runtime and all model artifacts in `config.json` must remain at their recorded paths.
- No other `llama-server` process may be running. The runner uses `127.0.0.1:18088` and concurrency 1.

# Run

```bash
cd /srv/ai/benchmarks/qwen38-flash-next-q6-mtp-prepared
./run_benchmarks.sh
```

The prepared default reasoning effort is `high`. It can be changed with `--reasoning-effort low|medium|high`; use `--rerun` when intentionally replacing completed experiments. Full artifact hashes were verified during preparation; use `--rehash` to repeat the 158+ GiB hash pass.

# Interrupt and resume

Press Ctrl-C once. The runner stops telemetry and the current server, preserves partial files, marks that experiment `INTERRUPTED`, and exits. Run the same command again to resume; experiments marked `COMPLETE` are skipped. Use `--rerun` only to rerun all nine experiments.

# Results

Machine-readable results are in `results.jsonl`, `summary.csv`, and each `experiments/<experiment-id>/result.json`. Raw server logs are under `logs/`, telemetry is under `telemetry/`, and the final run accounting is in `RUN_COMPLETE.json`.
