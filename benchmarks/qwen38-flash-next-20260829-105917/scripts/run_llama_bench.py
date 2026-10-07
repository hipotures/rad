#!/usr/bin/env python3
"""Run one llama-bench experiment with raw logs, GPU telemetry, and JSONL bookkeeping."""

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shlex
import statistics
import subprocess
import threading
import time


ROOT = Path("/srv/ai/benchmarks/qwen38-flash-next-20260829-105917")
RESULTS = ROOT / "results" / "experiments.jsonl"
LOGS = ROOT / "logs"
REPORT = ROOT / "REPORT.md"


def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def next_id():
    highest = 0
    if RESULTS.exists():
        for line in RESULTS.read_text(encoding="utf-8").splitlines():
            try:
                value = json.loads(line).get("experiment_id", "")
                highest = max(highest, int(value.removeprefix("EXP-")))
            except (ValueError, json.JSONDecodeError):
                pass
    return f"EXP-{highest + 1:03d}"


def query_gpus():
    query = (
        "index,utilization.gpu,memory.used,memory.total,temperature.gpu,"
        "power.draw,clocks.sm,pcie.link.gen.current,pcie.link.width.current"
    )
    proc = subprocess.run(
        ["nvidia-smi", f"--query-gpu={query}", "--format=csv,noheader,nounits"],
        capture_output=True,
        text=True,
        check=False,
    )
    rows = []
    for line in proc.stdout.splitlines():
        fields = [part.strip() for part in line.split(",")]
        if len(fields) != 9:
            continue
        try:
            rows.append({
                "index": int(fields[0]), "utilization_pct": float(fields[1]),
                "memory_used_mib": float(fields[2]), "memory_total_mib": float(fields[3]),
                "temperature_c": float(fields[4]), "power_w": float(fields[5]),
                "sm_clock_mhz": float(fields[6]), "pcie_gen": int(fields[7]),
                "pcie_width": int(fields[8]),
            })
        except ValueError:
            continue
    return rows


def summarize_gpu(samples):
    summary = {}
    indices = sorted({row["index"] for sample in samples for row in sample["gpus"]})
    for index in indices:
        rows = [row for sample in samples for row in sample["gpus"] if row["index"] == index]
        summary[str(index)] = {
            "samples": len(rows),
            "utilization_median_pct": statistics.median(row["utilization_pct"] for row in rows),
            "utilization_max_pct": max(row["utilization_pct"] for row in rows),
            "memory_max_mib": max(row["memory_used_mib"] for row in rows),
            "temperature_max_c": max(row["temperature_c"] for row in rows),
            "power_median_w": statistics.median(row["power_w"] for row in rows),
            "power_max_w": max(row["power_w"] for row in rows),
            "sm_clock_median_mhz": statistics.median(row["sm_clock_mhz"] for row in rows),
            "pcie_gen_max": max(row["pcie_gen"] for row in rows),
            "pcie_width_max": max(row["pcie_width"] for row in rows),
        }
    return summary


def parse_bench(stdout):
    rows = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and "avg_ts" in value:
            rows.append(value)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--hypothesis", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--classification", default="NEUTRAL")
    parser.add_argument("--source-repo", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--build-config", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--model-revision", required=True)
    parser.add_argument("--comparison", default="runtime-reference")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        parser.error("benchmark command required after --")

    experiment_id = next_id()
    started = utc_now()
    samples = []
    stop = threading.Event()

    def monitor():
        while not stop.is_set():
            samples.append({"time": utc_now(), "gpus": query_gpus()})
            stop.wait(1.0)

    env = os.environ.copy()
    cache_root = ROOT / "tmp"
    env.update({
        "TMPDIR": str(cache_root / "tmp"), "TEMP": str(cache_root / "tmp"),
        "TMP": str(cache_root / "tmp"), "HF_HOME": str(cache_root / "hf"),
        "XDG_CACHE_HOME": str(cache_root / "xdg"),
        "PIP_CACHE_DIR": str(cache_root / "pip"), "CCACHE_DIR": str(cache_root / "ccache"),
    })
    for path in env["TMPDIR"], env["HF_HOME"], env["XDG_CACHE_HOME"], env["PIP_CACHE_DIR"], env["CCACHE_DIR"]:
        Path(path).mkdir(parents=True, exist_ok=True)

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    begin = time.monotonic()
    proc = subprocess.run(command, capture_output=True, text=True, env=env, check=False)
    elapsed = time.monotonic() - begin
    stop.set()
    thread.join(timeout=3)
    samples.append({"time": utc_now(), "gpus": query_gpus()})

    stdout_path = LOGS / f"{experiment_id}-stdout.jsonl"
    stderr_path = LOGS / f"{experiment_id}-stderr.log"
    telemetry_path = LOGS / f"{experiment_id}-gpu-telemetry.jsonl"
    stdout_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")
    telemetry_path.write_text("".join(json.dumps(row) + "\n" for row in samples), encoding="utf-8")
    bench_rows = parse_bench(proc.stdout)
    classification = args.classification if proc.returncode == 0 and bench_rows else "BROKEN"
    record = {
        "experiment_id": experiment_id,
        "label": args.label,
        "started_utc": started,
        "finished_utc": utc_now(),
        "wall_seconds": round(elapsed, 3),
        "hypothesis": args.hypothesis,
        "reason": args.reason,
        "classification": classification,
        "comparison_leaderboard": args.comparison,
        "source_repo": args.source_repo,
        "source_commit": args.source_commit,
        "build_config": args.build_config,
        "model_path": args.model,
        "model_revision": args.model_revision,
        "command": command,
        "command_shell": shlex.join(command),
        "exit_code": proc.returncode,
        "bench_results": bench_rows,
        "gpu_summary": summarize_gpu(samples),
        "raw_stdout": str(stdout_path),
        "raw_stderr": str(stderr_path),
        "raw_gpu_telemetry": str(telemetry_path),
    }
    with RESULTS.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")

    rates = ", ".join(
        f"pp{row.get('n_prompt', 0)}+tg{row.get('n_gen', 0)}={row.get('avg_ts', 0):.2f} tok/s"
        for row in bench_rows
    ) or "no parseable result"
    block = (
        f"\n### {experiment_id} — {args.label}\n\n"
        f"- Hypothesis: {args.hypothesis}\n"
        f"- Reason: {args.reason}\n"
        f"- Result: {classification}; {rates}; wall {elapsed:.1f}s; exit {proc.returncode}.\n"
        f"- Command: `{shlex.join(command)}`\n"
        f"- Raw logs: `{stdout_path}`, `{stderr_path}`, `{telemetry_path}`\n"
    )
    with REPORT.open("a", encoding="utf-8") as handle:
        handle.write(block)
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
