#!/usr/bin/env python3
"""Start llama-server, run deterministic HTTP completions, and retain all evidence."""

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import threading
import time
import urllib.error
import urllib.request


ROOT = Path("/srv/ai/benchmarks/qwen38-flash-next-phase2-20260829-211320")
RESULTS = ROOT / "results" / "experiments.jsonl"
LOGS = ROOT / "logs"
REPORT = ROOT / "REPORT.md"


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def next_id():
    highest = 0
    for line in RESULTS.read_text(encoding="utf-8").splitlines():
        try:
            highest = max(highest, int(json.loads(line)["experiment_id"].removeprefix("EXP-")))
        except (ValueError, KeyError, json.JSONDecodeError):
            pass
    return f"EXP-{highest + 1:03d}"


def http_get(url):
    with urllib.request.urlopen(url, timeout=10) as response:
        return response.read().decode("utf-8", "replace")


def http_post(url, body, timeout=1800):
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def gpu_rows():
    query = "index,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw,clocks.sm"
    proc = subprocess.run(
        ["nvidia-smi", f"--query-gpu={query}", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, check=False,
    )
    return proc.stdout.strip().splitlines()


def process_memory(pid):
    """Return process RSS/high-water RSS and system availability in KiB."""
    result = {"pid": pid}
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith(("VmRSS:", "VmHWM:", "VmSize:")):
                key, value, *_ = line.split()
                result[key.removesuffix(":")] = int(value)
    except (FileNotFoundError, ProcessLookupError, ValueError):
        pass
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith(("MemAvailable:", "MemFree:", "Cached:")):
                key, value, *_ = line.split()
                result[key.removesuffix(":")] = int(value)
    except (FileNotFoundError, ValueError):
        pass
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--hypothesis", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--source-repo", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--build-config", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--model-revision", required=True)
    parser.add_argument("--comparison", default="runtime-reference")
    parser.add_argument("--classification", default="NEUTRAL")
    parser.add_argument("--port", type=int, default=18080)
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt-file")
    prompt_group.add_argument("--requests-file", action="append")
    parser.add_argument("--n-predict", type=int, default=512)
    parser.add_argument("--warmup-n", type=int, default=32)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--request-timeout", type=int, default=1800,
                        help="HTTP timeout in seconds for each completion request")
    parser.add_argument("--request-id", action="append", default=[],
                        help="Run only matching request IDs from --requests-file")
    parser.add_argument("--expected-sha256")
    parser.add_argument("--env", action="append", default=[])
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        parser.error("server command required after --")

    exp = next_id()
    stdout_path = LOGS / f"{exp}-server-stdout.log"
    stderr_path = LOGS / f"{exp}-server-stderr.log"
    response_path = LOGS / f"{exp}-responses.json"
    telemetry_path = LOGS / f"{exp}-gpu-telemetry.jsonl"
    if args.requests_file:
        requests_to_run = []
        for requests_file in args.requests_file:
            requests_to_run.extend(json.loads(Path(requests_file).read_text(encoding="utf-8")))
        if args.request_id:
            wanted = set(args.request_id)
            requests_to_run = [item for item in requests_to_run if item.get("id") in wanted]
            missing = wanted.difference(item.get("id") for item in requests_to_run)
            if missing:
                parser.error(f"request IDs not found: {sorted(missing)}")
    else:
        requests_to_run = [{"id": "default", "prompt": Path(args.prompt_file).read_text(encoding="utf-8"),
                            "n_predict": args.n_predict}]
    env = os.environ.copy()
    for item in args.env:
        key, value = item.split("=", 1)
        env[key] = value
    started = now()
    start_mono = time.monotonic()
    telemetry = []
    stop = threading.Event()
    proc_holder = {}

    def monitor():
        while not stop.is_set():
            pid = proc_holder.get("pid")
            telemetry.append({
                "utc": now(), "gpus_csv": gpu_rows(),
                "memory_kib": process_memory(pid) if pid else process_memory(os.getpid()),
            })
            stop.wait(1)

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    server_out = stdout_path.open("w", encoding="utf-8")
    server_err = stderr_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(command, stdout=server_out, stderr=server_err, text=True, env=env)
    proc_holder["pid"] = proc.pid
    base = f"http://127.0.0.1:{args.port}"
    responses = []
    error = None
    ready_seconds = None
    metrics_before = ""
    metrics_after = ""
    try:
        deadline = time.monotonic() + 900
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                raise RuntimeError(f"server exited during load with code {proc.returncode}")
            try:
                health = json.loads(http_get(base + "/health"))
                if health.get("status") == "ok":
                    ready_seconds = time.monotonic() - start_mono
                    break
            except (OSError, urllib.error.URLError, json.JSONDecodeError):
                pass
            time.sleep(1)
        else:
            raise TimeoutError("server did not become healthy within 900 seconds")

        if args.warmup_n:
            http_post(base + "/completion", {
                "prompt": "Reply with exactly: READY", "n_predict": args.warmup_n,
                "temperature": 0, "seed": 4242, "cache_prompt": False,
            })
        try:
            metrics_before = http_get(base + "/metrics")
        except Exception:
            pass
        for request_item in requests_to_run:
            for repeat in range(args.repeats):
                begin = time.monotonic()
                body = {
                    "prompt": request_item["prompt"],
                    "n_predict": request_item.get("n_predict", args.n_predict),
                    "temperature": 0, "seed": 4242, "cache_prompt": False,
                    "ignore_eos": True,
                }
                body.update(request_item.get("body", {}))
                result = http_post(base + "/completion", body, timeout=args.request_timeout)
                elapsed = time.monotonic() - begin
                content = result.get("content", "")
                timings = result.get("timings", {})
                responses.append({
                    "request_id": request_item.get("id", "unnamed"),
                    "repeat": repeat + 1,
                    "wall_seconds": elapsed,
                    "content_sha256": hashlib.sha256(content.encode()).hexdigest(),
                    "content": content,
                    "tokens_predicted": result.get("tokens_predicted"),
                    "tokens_evaluated": result.get("tokens_evaluated"),
                    "timings": timings,
                    "truncated": result.get("truncated"),
                    "stopped_eos": result.get("stopped_eos"),
                })
        try:
            metrics_after = http_get(base + "/metrics")
        except Exception:
            pass
    except Exception as exc:
        error = repr(exc)
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=10)
        server_out.close()
        server_err.close()
        stop.set()
        thread.join(timeout=3)
        telemetry.append({"utc": now(), "gpus_csv": gpu_rows(),
                          "memory_kib": process_memory(proc.pid)})

    output_hashes = [row["content_sha256"] for row in responses]
    hash_ok = not args.expected_sha256 or all(value == args.expected_sha256 for value in output_hashes)
    classification = args.classification if not error and responses and hash_ok else "REJECTED-INCORRECT"
    record = {
        "experiment_id": exp, "label": args.label, "started_utc": started,
        "finished_utc": now(), "wall_seconds": round(time.monotonic() - start_mono, 3),
        "ready_seconds": ready_seconds, "hypothesis": args.hypothesis, "reason": args.reason,
        "classification": classification, "comparison_leaderboard": args.comparison,
        "source_repo": args.source_repo, "source_commit": args.source_commit,
        "build_config": args.build_config, "model_path": args.model,
        "model_revision": args.model_revision, "command": command,
        "command_shell": shlex.join(command), "environment_overrides": args.env,
        "prompt_file": args.prompt_file, "requests_file": args.requests_file,
        "n_predict": args.n_predict, "request_timeout": args.request_timeout,
        "request_ids": args.request_id,
        "responses": [{k: v for k, v in row.items() if k != "content"} for row in responses],
        "expected_sha256": args.expected_sha256, "output_hash_match": hash_ok,
        "error": error, "server_exit_code": proc.returncode,
        "raw_stdout": str(stdout_path), "raw_stderr": str(stderr_path),
        "raw_responses": str(response_path), "raw_gpu_telemetry": str(telemetry_path),
        "peak_process_rss_kib": max((row.get("memory_kib", {}).get("VmRSS", 0)
                                     for row in telemetry), default=0),
        "peak_process_hwm_kib": max((row.get("memory_kib", {}).get("VmHWM", 0)
                                     for row in telemetry), default=0),
        "minimum_mem_available_kib": min((row.get("memory_kib", {}).get("MemAvailable")
                                          for row in telemetry
                                          if row.get("memory_kib", {}).get("MemAvailable") is not None),
                                         default=None),
    }
    response_path.write_text(json.dumps({
        "responses": responses, "metrics_before": metrics_before, "metrics_after": metrics_after,
    }, indent=2), encoding="utf-8")
    telemetry_path.write_text("".join(json.dumps(row) + "\n" for row in telemetry), encoding="utf-8")
    with RESULTS.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")
    rates = [row.get("timings", {}).get("predicted_per_second") for row in responses]
    block = (
        f"\n### {exp} — {args.label}\n\n"
        f"- Hypothesis: {args.hypothesis}\n- Reason: {args.reason}\n"
        f"- Result: {classification}; ready {ready_seconds}; decode rates {rates}; hashes {output_hashes}; error {error}.\n"
        f"- Command: `{shlex.join(command)}`\n"
        f"- Raw logs: `{stdout_path}`, `{stderr_path}`, `{response_path}`, `{telemetry_path}`\n"
    )
    with REPORT.open("a", encoding="utf-8") as handle:
        handle.write(block)
    print(json.dumps(record, indent=2))
    raise SystemExit(0 if classification != "BROKEN" else 1)


if __name__ == "__main__":
    main()
