#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / "q6mtp2_config.json").read_text())
SERVER = None
GPU_TOTAL_MIB = None


def now():
    return datetime.now(timezone.utc).isoformat()


def say(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def atomic_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def gpu_snapshot():
    q = "index,memory.used,memory.free,utilization.gpu,power.draw"
    out = subprocess.check_output(
        ["nvidia-smi", f"--query-gpu={q}", "--format=csv,noheader,nounits"], text=True
    )
    rows = []
    for line in out.splitlines():
        p = [x.strip() for x in line.split(",")]
        rows.append({
            "index": int(p[0]), "used_mib": float(p[1]), "free_mib": float(p[2]),
            "util_pct": float(p[3]), "power_w": float(p[4]),
        })
    return rows


def api(method, endpoint, payload=None, timeout=30):
    s = CFG["server"]
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        f"http://{s['host']}:{s['port']}{endpoint}", data=body, method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        return json.loads(raw) if raw else {}


def conflicts():
    me = os.getpid()
    found = []
    for p in Path("/proc").iterdir():
        if not p.name.isdigit() or int(p.name) == me:
            continue
        try:
            cmd = (p / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
        except OSError:
            continue
        if "llama-server" in cmd:
            found.append((int(p.name), cmd.strip()))
    return found


def wait_ready(proc):
    deadline = time.monotonic() + CFG["safety"]["startup_timeout_seconds"]
    last = time.monotonic()
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"server exited during startup rc={proc.returncode}")
        try:
            api("GET", "/health", timeout=2)
            return
        except Exception:
            pass
        if time.monotonic() - last >= 15:
            say("still waiting for server readiness ...")
            last = time.monotonic()
        time.sleep(1)
    raise TimeoutError("server readiness timeout")


def stop_server():
    global SERVER
    if SERVER is None:
        return
    proc, SERVER = SERVER, None
    if proc.poll() is None:
        os.killpg(proc.pid, signal.SIGINT)
        try:
            proc.wait(timeout=25)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
    if hasattr(proc, "_log_handle"):
        proc._log_handle.close()


def wait_gpu_release(before, timeout=60):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        snap = gpu_snapshot()
        if all(snap[i]["used_mib"] <= before[i]["used_mib"] + 64 for i in range(2)):
            return
        time.sleep(1)
    say(f"WARNING: GPU memory not fully released: {gpu_snapshot()}")


def start_server(cmd, log_path):
    global SERVER
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log = log_path.open("wb", buffering=0)
    SERVER = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    SERVER._log_handle = log
    wait_ready(SERVER)
    return SERVER


def cmd_for(ctx, ncmoe, ts):
    s = CFG["server"]
    return [
        CFG["runtime"]["server_path"],
        "-m", CFG["target"]["first_shard"],
        "--host", s["host"], "--port", str(s["port"]),
        "-c", str(ctx), "-np", "1", "-fa", "on",
        "-ctk", s["cache_type_k"], "-ctv", s["cache_type_v"],
        "-b", str(s["batch"]), "-ub", str(s["ubatch"]),
        "-t", str(s["threads"]), "-tb", str(s["threads_batch"]),
        "-dev", "CUDA0,CUDA1", "-sm", "layer", "-ngl", "all",
        "-ncmoe", str(ncmoe), "-ts", ts,
        "--no-warmup", "-lv", "4",
        "--spec-type", "draft-mtp",
        "--spec-draft-model", CFG["draft"]["path"],
        "--spec-draft-n-max", str(CFG["draft"]["n_max"]),
        "--spec-draft-ngl", "all",
        "--spec-draft-device", CFG["draft"]["device"],
    ]


def parse_draft_placement(log_path):
    text = log_path.read_text(errors="replace")
    marker = text.find("loading draft model")
    section = text[marker:] if marker >= 0 else text
    vals = {"CUDA0": 0.0, "CUDA1": 0.0, "CPU": 0.0}
    pat = r"(CUDA\d+|CPU(?:_Mapped)?|CUDA_Host) model buffer size\s*=\s*([0-9.]+) MiB"
    for dev, mib in re.findall(pat, section):
        key = dev if dev.startswith("CUDA") and dev != "CUDA_Host" else "CPU"
        if key in vals:
            vals[key] += float(mib)
    return vals


class PeakMonitor:
    def __init__(self):
        self.stop_event = threading.Event()
        self.rows = []
        self.thread = threading.Thread(target=self.run, daemon=True)

    def run(self):
        interval = CFG["safety"]["telemetry_interval_seconds"]
        while not self.stop_event.is_set():
            try:
                self.rows.append((time.monotonic(), gpu_snapshot()))
            except Exception:
                pass
            self.stop_event.wait(interval)

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join(timeout=5)

    def peak_used(self):
        if not self.rows:
            snap = gpu_snapshot()
            return [x["used_mib"] for x in snap]
        return [max(snap[i]["used_mib"] for _, snap in self.rows) for i in range(2)]


def smoke():
    p = CFG["smoke"]
    payload = {
        "model": "target",
        "messages": [{"role": "user", "content": p["prompt"]}],
        "stream": False, "max_tokens": p["max_tokens"],
        "temperature": p["temperature"], "top_p": p["top_p"], "top_k": p["top_k"],
        "seed": p["seed"], "chat_template_kwargs": {"enable_thinking": bool(p["thinking"])},
    }
    started = time.monotonic()
    out = api("POST", "/v1/chat/completions", payload, timeout=CFG["safety"]["smoke_timeout_seconds"])
    wall = time.monotonic() - started
    usage = out.get("usage") or {}
    timings = out.get("timings") or {}
    return {
        "wall_seconds": wall,
        "completion_tokens": usage.get("completion_tokens") or timings.get("predicted_n"),
        "server_tg_tps": timings.get("predicted_per_second"),
    }


def load_completed(jsonl_path):
    completed = {}
    if not jsonl_path.exists():
        return completed
    for line in jsonl_path.read_text().splitlines():
        try:
            row = json.loads(line)
        except Exception:
            continue
        if row.get("status") in {"COMPLETE", "FAILED"}:
            completed[row.get("experiment_id")] = row
    return completed


def candidate_key(row):
    min_free = min(row["peak_free_vram_mib"])
    imbalance = abs(row["peak_vram_used_mib"][0] - row["peak_vram_used_mib"][1])
    return (-min_free, imbalance, row.get("smoke_wall_seconds") or 1e9)


def main():
    global GPU_TOTAL_MIB
    outdir = ROOT / "q6mtp2_results"
    logs = outdir / "logs"
    outdir.mkdir(exist_ok=True)
    logs.mkdir(exist_ok=True)
    jsonl = outdir / "results.jsonl"
    csv_path = outdir / "summary.csv"
    selected_path = outdir / "selected_placements.json"

    c = conflicts()
    if c:
        raise RuntimeError(f"conflicting llama-server process(es): {c}")

    idle = gpu_snapshot()
    if len(idle) != 2:
        raise RuntimeError(f"expected exactly 2 GPUs, got {len(idle)}")
    if any(g["used_mib"] > 1024 for g in idle):
        raise RuntimeError(f"GPUs not idle enough: {idle}")
    GPU_TOTAL_MIB = [g["used_mib"] + g["free_mib"] for g in idle]

    completed = load_completed(jsonl)
    all_rows = list(completed.values())
    selected = {}

    total_planned = 0
    for ctx in CFG["search"]["contexts"]:
        start_n = int(CFG["search"]["start_ncmoe"][str(ctx)])
        total_planned += (start_n - CFG["search"]["min_ncmoe"] + 1) * len(CFG["search"]["tensor_splits"])

    say("Q6 + Q8 MTP placement sweep v2")
    say(f"Search: asymmetric -ts up to 92,8; MTP fixed on {CFG['draft']['device']}; n-max={CFG['draft']['n_max']}.")
    say(f"Safety uses PEAK VRAM during smoke, minimum free={CFG['safety']['minimum_peak_free_vram_mib_each_gpu']} MiB/GPU.")
    say(f"Resume state: {len(completed)} previous combinations recorded.")

    attempt = 0
    try:
        for ctx in CFG["search"]["contexts"]:
            start_n = int(CFG["search"]["start_ncmoe"][str(ctx)])
            say("=" * 78)
            say(f"CONTEXT {ctx}: ncmoe {start_n} down to {CFG['search']['min_ncmoe']}")
            last_safe = None

            for ncmoe in range(start_n, CFG["search"]["min_ncmoe"] - 1, -1):
                safe_candidates = []
                say(f"Trying ncmoe={ncmoe} -> {48-ncmoe} routed-expert layers on GPU")

                for ts in CFG["search"]["tensor_splits"]:
                    attempt += 1
                    exp_id = f"ctx{ctx}-ncmoe{ncmoe}-ts{ts.replace(',', '_')}"

                    if exp_id in completed:
                        row = completed[exp_id]
                        say(f"  [{attempt}/{total_planned}] ts={ts}: resume -> {row.get('status')} safe={row.get('safe')}")
                        if row.get("safe"):
                            safe_candidates.append(row)
                        continue

                    say(f"  [{attempt}/{total_planned}] ts={ts}: startup ...")
                    before = gpu_snapshot()
                    log_path = logs / f"{exp_id}.server.log"
                    cmd = cmd_for(ctx, ncmoe, ts)
                    row = {
                        "experiment_id": exp_id, "timestamp": now(), "context": ctx,
                        "ncmoe": ncmoe, "gpu_expert_layers": 48 - ncmoe,
                        "tensor_split": ts, "draft_device": CFG["draft"]["device"],
                        "draft_n_max": CFG["draft"]["n_max"], "status": "RUNNING", "command": cmd,
                    }
                    monitor = None
                    try:
                        t0 = time.monotonic()
                        start_server(cmd, log_path)
                        row["startup_seconds"] = time.monotonic() - t0
                        startup = gpu_snapshot()
                        row["startup_vram_used_mib"] = [x["used_mib"] for x in startup]
                        row["startup_vram_free_mib"] = [x["free_mib"] for x in startup]
                        row["draft_buffers_mib"] = parse_draft_placement(log_path)

                        monitor = PeakMonitor()
                        monitor.start()
                        sm = smoke()
                        monitor.stop()
                        peak_used = monitor.peak_used()
                        peak_free = [GPU_TOTAL_MIB[i] - peak_used[i] for i in range(2)]

                        row["peak_vram_used_mib"] = peak_used
                        row["peak_free_vram_mib"] = peak_free
                        row["smoke_wall_seconds"] = sm["wall_seconds"]
                        row["smoke_completion_tokens"] = sm["completion_tokens"]
                        row["smoke_server_tg_tps"] = sm["server_tg_tps"]

                        draft = row["draft_buffers_mib"]
                        fully_gpu = draft.get(CFG["draft"]["device"], 0) > 2000 and draft.get("CPU", 0) < 1
                        safe = fully_gpu and min(peak_free) >= CFG["safety"]["minimum_peak_free_vram_mib_each_gpu"]
                        row["draft_fully_gpu_resident"] = fully_gpu
                        row["safe"] = safe
                        row["status"] = "COMPLETE"
                        say(
                            f"    startup_used={row['startup_vram_used_mib']} MiB, "
                            f"peak_used={peak_used} MiB, peak_free={peak_free} MiB, "
                            f"draft_gpu={fully_gpu}, safe={safe}, smoke_tg={sm['server_tg_tps']}"
                        )
                        if safe:
                            safe_candidates.append(row)

                    except Exception as e:
                        if monitor is not None:
                            try:
                                monitor.stop()
                                peak_used = monitor.peak_used()
                                row["peak_vram_used_mib"] = peak_used
                                row["peak_free_vram_mib"] = [GPU_TOTAL_MIB[i] - peak_used[i] for i in range(2)]
                            except Exception:
                                pass
                        row["status"] = "FAILED"
                        row["safe"] = False
                        row["error"] = repr(e)
                        say(f"    FAILED: {e!r}")
                    finally:
                        stop_server()
                        wait_gpu_release(before)

                    all_rows.append(row)
                    completed[exp_id] = row
                    with jsonl.open("a") as f:
                        f.write(json.dumps(row, sort_keys=True) + "\n")
                    time.sleep(1)

                if safe_candidates:
                    safe_candidates.sort(key=candidate_key)
                    best_this_n = safe_candidates[0]
                    last_safe = best_this_n
                    say(
                        f"  SAFE ncmoe={ncmoe}; best ts={best_this_n['tensor_split']}, "
                        f"peak_free={best_this_n['peak_free_vram_mib']} MiB. Trying one step more aggressive ..."
                    )
                    continue

                say(f"  No safe split at ncmoe={ncmoe}; stopping this context.")
                break

            if last_safe:
                selected[str(ctx)] = {
                    "ncmoe": last_safe["ncmoe"],
                    "gpu_expert_layers": last_safe["gpu_expert_layers"],
                    "tensor_split": last_safe["tensor_split"],
                    "draft_device": CFG["draft"]["device"],
                    "draft_n_max": CFG["draft"]["n_max"],
                    "startup_vram_used_mib": last_safe["startup_vram_used_mib"],
                    "peak_vram_used_mib": last_safe["peak_vram_used_mib"],
                    "peak_free_vram_mib": last_safe["peak_free_vram_mib"],
                    "smoke_server_tg_tps": last_safe.get("smoke_server_tg_tps"),
                }
                say(
                    f"SELECTED ctx={ctx}: ncmoe={last_safe['ncmoe']} "
                    f"({last_safe['gpu_expert_layers']} expert layers on GPU), "
                    f"ts={last_safe['tensor_split']}, peak_free={last_safe['peak_free_vram_mib']} MiB"
                )
            else:
                say(f"NO SAFE placement found for ctx={ctx}.")

            atomic_json(selected_path, {
                "campaign": CFG["campaign"], "runtime_commit": CFG["runtime"]["commit"],
                "selection_rule": CFG["selection"]["rule"], "selected": selected, "updated_at": now(),
            })

    finally:
        stop_server()

    latest = {}
    for row in all_rows:
        latest[row["experiment_id"]] = row
    rows = [latest[k] for k in sorted(latest)]
    cols = [
        "experiment_id","status","context","ncmoe","gpu_expert_layers","tensor_split",
        "safe","draft_fully_gpu_resident","startup_seconds","smoke_wall_seconds",
        "smoke_server_tg_tps","startup_vram_used_mib","peak_vram_used_mib","peak_free_vram_mib","error"
    ]
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

    atomic_json(selected_path, {
        "campaign": CFG["campaign"], "runtime_commit": CFG["runtime"]["commit"],
        "selection_rule": CFG["selection"]["rule"], "selected": selected, "completed_at": now(),
    })

    say("=" * 78)
    say("PLACEMENT SWEEP V2 COMPLETE")
    for ctx in CFG["search"]["contexts"]:
        v = selected.get(str(ctx))
        if v:
            say(f"ctx={ctx}: ncmoe={v['ncmoe']}, GPU expert layers={v['gpu_expert_layers']}, ts={v['tensor_split']}, peak_free={v['peak_free_vram_mib']} MiB")
        else:
            say(f"ctx={ctx}: no safe placement found")
    say(f"Results: {outdir}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        say("Interrupted; partial results preserved. Re-run the same command to resume.")
        stop_server()
        sys.exit(130)
