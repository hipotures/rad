#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import re
import signal
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / "placement_sweep_config.json").read_text())
SERVER: subprocess.Popen | None = None


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
    query = "index,memory.used,memory.free,utilization.gpu,power.draw"
    out = subprocess.check_output(
        ["nvidia-smi", f"--query-gpu={query}", "--format=csv,noheader,nounits"],
        text=True,
    )
    rows = []
    for line in out.splitlines():
        p = [x.strip() for x in line.split(",")]
        rows.append({
            "index": int(p[0]),
            "used_mib": float(p[1]),
            "free_mib": float(p[2]),
            "util_pct": float(p[3]),
            "power_w": float(p[4]),
        })
    return rows


def api(method: str, endpoint: str, payload=None, timeout=30):
    s = CFG["server"]
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        f"http://{s['host']}:{s['port']}{endpoint}",
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        return json.loads(raw) if raw else {}


def conflicting_servers():
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


def start_server(cmd, log_path: Path):
    global SERVER
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log = log_path.open("wb", buffering=0)
    SERVER = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    SERVER._placement_log = log  # type: ignore[attr-defined]
    wait_ready(SERVER)
    return SERVER


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
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
    proc._placement_log.close()  # type: ignore[attr-defined]


def command_for(ctx: int, ncmoe: int, tensor_split: str):
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
        "-ncmoe", str(ncmoe), "-ts", tensor_split,
        "--no-warmup", "-lv", "4",
        "--spec-type", "draft-mtp",
        "--spec-draft-model", CFG["draft"]["path"],
        "--spec-draft-n-max", str(CFG["draft"]["n_max"]),
        "--spec-draft-ngl", "all",
        "--spec-draft-device", CFG["draft"]["device"],
    ]


def smoke_payload():
    p = CFG["smoke"]
    # Enough text to exercise a normal decode without turning this into a long benchmark.
    code = "\n".join([
        "def merge_sorted(a, b):",
        "    out = []",
        "    i = j = 0",
        "    while i < len(a) and j < len(b):",
        "        if a[i] <= b[j]:",
        "            out.append(a[i]); i += 1",
        "        else:",
        "            out.append(b[j]); j += 1",
        "    out.extend(a[i:]); out.extend(b[j:])",
        "    return out",
    ])
    prompt = ("Review this Python function for correctness and complexity. "
              "Return a concise technical assessment and one improved implementation.\n\n" + code)
    return {
        "model": "target",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "max_tokens": p["max_tokens"],
        "temperature": p["temperature"],
        "top_p": p["top_p"],
        "top_k": p["top_k"],
        "seed": p["seed"],
        "chat_template_kwargs": {"enable_thinking": p["thinking_enabled"]},
    }


def run_smoke():
    started = time.monotonic()
    obj = api("POST", "/v1/chat/completions", smoke_payload(), timeout=CFG["safety"]["smoke_timeout_seconds"])
    wall = time.monotonic() - started
    usage = obj.get("usage") or {}
    timings = obj.get("timings") or {}
    return {
        "wall_seconds": wall,
        "completion_tokens": usage.get("completion_tokens") or timings.get("predicted_n"),
        "server_tg_tps": timings.get("predicted_per_second"),
    }


def parse_draft(log_path: Path):
    text = log_path.read_text(errors="replace")
    marker = text.find("loading draft model")
    section = text[marker:] if marker >= 0 else text
    vals = {"CUDA0": 0.0, "CUDA1": 0.0, "CPU": 0.0}
    pat = r"(CUDA\d+|CPU(?:_Mapped)?|CUDA_Host) model buffer size\s*=\s*([0-9.]+) MiB"
    for dev, mib in re.findall(pat, section):
        key = dev if dev.startswith("CUDA") and dev != "CUDA_Host" else "CPU"
        if key in vals:
            vals[key] += float(mib)
    pairs = re.findall(r"accepted\s+(\d+)\s*/\s*(\d+)", section, re.I)
    accepted = drafted = None
    if pairs:
        accepted, drafted = map(int, pairs[-1])
    return vals, drafted, accepted


def choose_best(candidates):
    # For a fixed ncmoe, prefer balanced remaining VRAM, then faster smoke.
    return min(
        candidates,
        key=lambda r: (
            abs(r["post_smoke_vram_free_mib"][0] - r["post_smoke_vram_free_mib"][1]),
            r.get("smoke_wall_seconds") or 1e9,
        ),
    )


def main():
    outdir = ROOT / "placement-sweep-results"
    logs = outdir / "logs"
    outdir.mkdir(exist_ok=True)
    logs.mkdir(exist_ok=True)
    jsonl = outdir / "results.jsonl"
    csv_path = outdir / "summary.csv"

    conflicts = conflicting_servers()
    if conflicts:
        raise RuntimeError(f"conflicting llama-server process(es): {conflicts}")

    initial = gpu_snapshot()
    if len(initial) != 2:
        raise RuntimeError(f"expected exactly 2 GPUs, got {len(initial)}")
    if any(g["used_mib"] > 1024 for g in initial):
        raise RuntimeError(f"GPUs are not idle enough: {initial}")

    contexts = CFG["contexts"]
    splits = CFG["search"]["tensor_splits"]
    min_ncmoe = CFG["search"]["min_ncmoe"]
    current_start = CFG["search"]["start_ncmoe"]
    min_free_required = CFG["safety"]["min_free_vram_mib_each_gpu_after_smoke"]

    rows = []
    selected = {}
    attempt = 0

    say("Qwen3.8-Flash-Next Q6 + Q8 MTP placement sweep")
    say("Purpose: find the smallest safe -ncmoe (most Q6 expert layers on GPU), not benchmark final performance.")
    say(f"Draft fixed on {CFG['draft']['device']}, n-max={CFG['draft']['n_max']}; minimum free VRAM={min_free_required} MiB/GPU.")

    try:
        for ctx in contexts:
            say("=" * 72)
            say(f"CONTEXT {ctx}: starting search at ncmoe={current_start}")
            best_ctx = None
            found_any = False

            for ncmoe in range(current_start, min_ncmoe - 1, -1):
                safe_this_ncmoe = []
                say(f"Trying ncmoe={ncmoe} -> {48 - ncmoe} routed-expert layers remain on GPU")

                for ts in splits:
                    attempt += 1
                    exp_id = f"ctx{ctx}-ncmoe{ncmoe}-ts{ts.replace(',', '_')}"
                    log_path = logs / f"{exp_id}.server.log"
                    cmd = command_for(ctx, ncmoe, ts)
                    say(f"  [{attempt}] ts={ts}: startup ...")
                    row = {
                        "experiment_id": exp_id,
                        "timestamp": now(),
                        "context": ctx,
                        "ncmoe": ncmoe,
                        "gpu_expert_layers": 48 - ncmoe,
                        "tensor_split": ts,
                        "draft_device": CFG["draft"]["device"],
                        "draft_n_max": CFG["draft"]["n_max"],
                        "status": "RUNNING",
                        "command": cmd,
                    }

                    try:
                        t0 = time.monotonic()
                        start_server(cmd, log_path)
                        row["startup_seconds"] = time.monotonic() - t0
                        startup = gpu_snapshot()
                        row["startup_vram_used_mib"] = [x["used_mib"] for x in startup]
                        row["startup_vram_free_mib"] = [x["free_mib"] for x in startup]

                        draft_buf, drafted0, accepted0 = parse_draft(log_path)
                        row["draft_buffers_mib"] = draft_buf
                        full_gpu = (
                            draft_buf.get(CFG["draft"]["device"], 0) > 2000
                            and draft_buf.get("CPU", 0) < 1
                        )
                        row["draft_fully_gpu_resident"] = full_gpu

                        sm = run_smoke()
                        row.update({
                            "smoke_wall_seconds": sm["wall_seconds"],
                            "smoke_completion_tokens": sm["completion_tokens"],
                            "smoke_server_tg_tps": sm["server_tg_tps"],
                        })
                        after = gpu_snapshot()
                        row["post_smoke_vram_used_mib"] = [x["used_mib"] for x in after]
                        row["post_smoke_vram_free_mib"] = [x["free_mib"] for x in after]

                        draft_buf2, drafted, accepted = parse_draft(log_path)
                        row["drafted_tokens_seen"] = drafted
                        row["accepted_draft_tokens_seen"] = accepted
                        row["acceptance_pct_seen"] = (
                            100.0 * accepted / drafted if drafted and accepted is not None else None
                        )

                        min_free = min(row["post_smoke_vram_free_mib"])
                        row["safe"] = bool(full_gpu and min_free >= min_free_required)
                        row["status"] = "COMPLETE"

                        say(
                            f"    used={row['post_smoke_vram_used_mib']} MiB, "
                            f"free={row['post_smoke_vram_free_mib']} MiB, "
                            f"draft_gpu={full_gpu}, safe={row['safe']}, "
                            f"smoke_tg={row['smoke_server_tg_tps']}"
                        )
                        if row["safe"]:
                            safe_this_ncmoe.append(row)

                    except Exception as e:
                        row["status"] = "FAILED"
                        row["safe"] = False
                        row["error"] = repr(e)
                        say(f"    FAILED: {e!r}")
                    finally:
                        stop_server()
                        rows.append(row)
                        with jsonl.open("a") as f:
                            f.write(json.dumps(row, sort_keys=True) + "\n")
                        time.sleep(1)

                if safe_this_ncmoe:
                    found_any = True
                    best_ctx = choose_best(safe_this_ncmoe)
                    say(
                        f"  SAFE ncmoe={ncmoe}; provisional best ts={best_ctx['tensor_split']}, "
                        f"free={best_ctx['post_smoke_vram_free_mib']} MiB. Trying one step more aggressive ..."
                    )
                    continue

                if found_any and CFG["search"]["stop_after_first_ncmoe_without_safe_split"]:
                    say(f"  No safe split at ncmoe={ncmoe}; stopping this context.")
                    break

            if best_ctx is None:
                say(f"NO SAFE placement found for ctx={ctx} in configured range.")
                # Less constrained contexts should still start from the original range.
                current_start = CFG["search"]["start_ncmoe"]
                continue

            selected[str(ctx)] = {
                "ncmoe": best_ctx["ncmoe"],
                "gpu_expert_layers": best_ctx["gpu_expert_layers"],
                "tensor_split": best_ctx["tensor_split"],
                "draft_device": CFG["draft"]["device"],
                "draft_n_max": CFG["draft"]["n_max"],
                "post_smoke_vram_used_mib": best_ctx["post_smoke_vram_used_mib"],
                "post_smoke_vram_free_mib": best_ctx["post_smoke_vram_free_mib"],
            }
            say(
                f"SELECTED ctx={ctx}: ncmoe={best_ctx['ncmoe']} "
                f"({best_ctx['gpu_expert_layers']} expert layers on GPU), "
                f"ts={best_ctx['tensor_split']}"
            )
            # Next, less constrained context begins from this successful ncmoe.
            current_start = best_ctx["ncmoe"]

    finally:
        stop_server()

    cols = [
        "experiment_id", "status", "context", "ncmoe", "gpu_expert_layers",
        "tensor_split", "safe", "draft_fully_gpu_resident", "startup_seconds",
        "smoke_wall_seconds", "smoke_server_tg_tps", "startup_vram_used_mib",
        "post_smoke_vram_used_mib", "post_smoke_vram_free_mib",
        "drafted_tokens_seen", "accepted_draft_tokens_seen", "acceptance_pct_seen", "error"
    ]
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    atomic_json(outdir / "selected_placements.json", {
        "campaign": CFG["campaign"],
        "runtime_commit": CFG["runtime"]["commit"],
        "selection_rule": "lowest safe ncmoe; for that ncmoe choose most balanced free VRAM",
        "selected": selected,
        "completed_at": now(),
    })

    say("=" * 72)
    say("PLACEMENT SWEEP COMPLETE")
    for ctx in contexts:
        v = selected.get(str(ctx))
        if v:
            say(
                f"ctx={ctx}: ncmoe={v['ncmoe']}, GPU expert layers={v['gpu_expert_layers']}, "
                f"ts={v['tensor_split']}, free={v['post_smoke_vram_free_mib']} MiB"
            )
        else:
            say(f"ctx={ctx}: no safe placement found")
    say(f"Results: {outdir}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        say("Interrupted; partial JSONL and logs preserved.")
        stop_server()
        sys.exit(130)
