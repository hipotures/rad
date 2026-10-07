#!/usr/bin/env python3
"""Sequential, resumable Qwen3.8 Flash Next target/MTP benchmark campaign.

v2 fixes:
- visible progress/heartbeats on stdout;
- decode TPS no longer includes prompt prefill;
- robust SSE accumulation (usage/timings/finish_reason are not lost);
- MTP counters are nullable and can be recovered from formal-run log slices;
- identical unmeasured warm-up before every formal request;
- old results from the broken runner are not reused;
- xhigh is exposed explicitly;
- per-context target_args from config.json are honored when present.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / "config.json").read_text())
SERVER: subprocess.Popen | None = None
TELEMETRY = None
CURRENT_ID = None
CAMPAIGN_START = datetime.now(timezone.utc).isoformat()
RUNNER_SCHEMA_VERSION = 2
FORMAL_ORDER = [(ctx, mode) for ctx in (32768, 65536, 131072)
                for mode in ("off", "auto", "forced-gpu")]
_PRINT_LOCK = threading.Lock()
_WARNED_LEGACY_PLACEMENT = False


def now():
    return datetime.now(timezone.utc).isoformat()


def say(message: str):
    with _PRINT_LOCK:
        stamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{stamp}] {message}", flush=True)


def fmt_seconds(value):
    if value is None:
        return "?"
    value = float(value)
    if value < 60:
        return f"{value:.1f}s"
    return f"{int(value // 60)}m{value % 60:04.1f}s"


def atomic_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def atomic_text(path: Path, value: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(value)
    os.replace(tmp, path)


def api(method: str, endpoint: str, data=None, timeout=30):
    url = f"http://{CFG['server']['host']}:{CFG['server']['port']}{endpoint}"
    body = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def gpu_snapshot():
    query = "index,memory.used,memory.free,utilization.gpu,power.draw"
    out = subprocess.check_output([
        "nvidia-smi", f"--query-gpu={query}", "--format=csv,noheader,nounits"
    ], text=True)
    rows = []
    for line in out.splitlines():
        p = [x.strip() for x in line.split(",")]
        rows.append({
            "index": int(p[0]), "used_mib": float(p[1]), "free_mib": float(p[2]),
            "util_pct": float(p[3]), "power_w": float(p[4]),
        })
    return rows


def conflicting_servers():
    found = []
    me = os.getpid()
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


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(16 << 20), b""):
            h.update(block)
    return h.hexdigest()


def preflight(rehash=False):
    for d in ("logs", "telemetry", "experiments", "prompts"):
        (ROOT / d).mkdir(exist_ok=True)
    conflicts = conflicting_servers()
    if conflicts:
        raise RuntimeError(f"conflicting llama-server process(es): {conflicts}")
    checks = [
        (CFG["runtime"]["server_path"], None, None),
        (CFG["draft"]["path"], CFG["draft"]["size"], CFG["draft"]["sha256"]),
    ]
    checks += [(s["path"], s["size"], s["sha256"]) for s in CFG["target"]["shards"]]
    for name, size, digest in checks:
        p = Path(name)
        if not p.is_file() or (size is not None and p.stat().st_size != size):
            raise RuntimeError(f"missing/incomplete artifact: {p}")
        if rehash and digest and sha256(p) != digest:
            raise RuntimeError(f"hash mismatch: {p}")
    mem_avail = int(next(
        x.split()[1] for x in Path("/proc/meminfo").read_text().splitlines()
        if x.startswith("MemAvailable:")
    )) * 1024
    disk_free = shutil.disk_usage(ROOT).free
    if mem_avail < CFG["requirements"]["minimum_available_ram_bytes"]:
        raise RuntimeError(f"available RAM {mem_avail} is below requirement")
    if disk_free < CFG["requirements"]["minimum_free_disk_bytes"]:
        raise RuntimeError(f"free disk {disk_free} is below requirement")
    gpus = gpu_snapshot()
    if len(gpus) != 2:
        raise RuntimeError(f"expected exactly two visible GPUs, found {len(gpus)}")
    if any(g["used_mib"] > 1024 for g in gpus):
        raise RuntimeError(f"GPUs are not idle enough for a controlled run: {gpus}")
    return {"available_ram_bytes": mem_avail, "free_disk_bytes": disk_free, "gpus": gpus}


def target_args_for(ctx: int):
    """Use prepared per-context target placement when config.json provides it."""
    global _WARNED_LEGACY_PLACEMENT
    placement = CFG.get("placements", {}).get(str(ctx), {})
    for key in ("target_args", "target_cli_args", "target_extra_args"):
        value = placement.get(key)
        if value:
            return shlex.split(value) if isinstance(value, str) else [str(x) for x in value]

    if not _WARNED_LEGACY_PLACEMENT:
        say("WARNING: config.json has no per-context target_args.")
        say("WARNING: falling back to legacy '-ngl all -cmoe -ts 1,1' (all routed experts on CPU).")
        say("WARNING: valid for controlled A/B, but NOT an optimized 2x4090 target placement.")
        _WARNED_LEGACY_PLACEMENT = True
    return ["-ngl", "all", "-cmoe", "-ts", "1,1"]


def base_command(ctx: int):
    s = CFG["server"]
    cmd = [
        CFG["runtime"]["server_path"], "-m", CFG["target"]["first_shard"],
        "--host", s["host"], "--port", str(s["port"]), "-c", str(ctx),
        "-np", "1", "-fa", "on", "-ctk", "q8_0", "-ctv", "q8_0",
        "-b", str(s["batch"]), "-ub", str(s["ubatch"]),
        "-t", str(s["threads"]), "-tb", str(s["threads_batch"]),
        "-dev", "CUDA0,CUDA1", "-sm", "layer",
    ]
    cmd += target_args_for(ctx)
    cmd += ["--no-warmup", "-lv", "4"]
    return cmd


def command_for(ctx: int, mode: str):
    cmd = base_command(ctx)
    if mode != "off":
        cmd += [
            "--spec-type", "draft-mtp",
            "--spec-draft-model", CFG["draft"]["path"],
            "--spec-draft-n-max", "3",
        ]
    if mode == "forced-gpu":
        gpu = CFG["placements"][str(ctx)]["draft_gpu"]
        cmd += ["--spec-draft-ngl", "all", "--spec-draft-device", gpu]
    return cmd


def wait_ready(proc, timeout=420):
    deadline = time.monotonic() + timeout
    last_notice = time.monotonic()
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"server exited during startup ({proc.returncode})")
        try:
            api("GET", "/health", timeout=2)
            return
        except Exception:
            if time.monotonic() - last_notice >= 15:
                say("Still waiting for server readiness ...")
                last_notice = time.monotonic()
            time.sleep(1)
    raise TimeoutError("server readiness timeout")


def start_server(cmd, log_path: Path):
    global SERVER
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log = log_path.open("wb", buffering=0)
    say("Starting llama-server ...")
    SERVER = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    SERVER._campaign_log = log  # type: ignore[attr-defined]
    say(f"Server PID {SERVER.pid}; waiting for /health ...")
    wait_ready(SERVER)
    say("Server is ready.")
    return SERVER


def stop_server():
    global SERVER
    if SERVER is None:
        return None
    proc, SERVER = SERVER, None
    if proc.poll() is None:
        os.killpg(proc.pid, signal.SIGINT)
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
    proc._campaign_log.close()  # type: ignore[attr-defined]
    return proc.returncode


def wait_gpu_release(before, timeout=60):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        snap = gpu_snapshot()
        if all(snap[i]["used_mib"] <= before[i]["used_mib"] + 64 for i in range(2)):
            return snap
        time.sleep(1)
    raise RuntimeError(f"GPU memory not released: {gpu_snapshot()}")


class Monitor:
    def __init__(self, path: Path, pid: int):
        self.path, self.pid = path, pid
        self.stop_event = threading.Event()
        self.rows = []
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.last_cpu = None

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join(timeout=5)
        fields = list(self.rows[0]) if self.rows else ["timestamp"]
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(self.rows)
        os.replace(tmp, self.path)

    def proc_stats(self):
        try:
            stat = Path(f"/proc/{self.pid}/stat").read_text().split()
            ticks, rss_pages = int(stat[13]) + int(stat[14]), int(stat[23])
            cpu = None
            t = time.monotonic()
            if self.last_cpu:
                cpu = ((ticks - self.last_cpu[0]) / os.sysconf("SC_CLK_TCK") /
                       (t - self.last_cpu[1]) * 100)
            self.last_cpu = (ticks, t)
            return rss_pages * os.sysconf("SC_PAGE_SIZE") / (1024 ** 2), cpu
        except (OSError, IndexError, ValueError):
            return None, None

    def run(self):
        while not self.stop_event.is_set():
            try:
                g = gpu_snapshot()
                rss, cpu = self.proc_stats()
                self.rows.append({
                    "timestamp": now(), "server_rss_mib": rss, "server_cpu_pct": cpu,
                    "cuda0_used_mib": g[0]["used_mib"], "cuda1_used_mib": g[1]["used_mib"],
                    "cuda0_util_pct": g[0]["util_pct"], "cuda1_util_pct": g[1]["util_pct"],
                    "cuda0_power_w": g[0]["power_w"], "cuda1_power_w": g[1]["power_w"],
                })
            except Exception:
                pass
            self.stop_event.wait(1)

    def summary(self):
        def vals(k):
            return [float(r[k]) for r in self.rows if r.get(k) is not None]

        return {
            "process_peak_rss_mib": max(vals("server_rss_mib"), default=None),
            "cpu_utilization_mean_pct": (
                sum(vals("server_cpu_pct")) / len(vals("server_cpu_pct"))
                if vals("server_cpu_pct") else None
            ),
            "peak_vram_cuda0_mib": max(vals("cuda0_used_mib"), default=None),
            "peak_vram_cuda1_mib": max(vals("cuda1_used_mib"), default=None),
            "gpu_utilization_mean_pct": [
                sum(vals(f"cuda{i}_util_pct")) / len(vals(f"cuda{i}_util_pct"))
                if vals(f"cuda{i}_util_pct") else None for i in range(2)
            ],
            "gpu_power_mean_w": [
                sum(vals(f"cuda{i}_power_w")) / len(vals(f"cuda{i}_power_w"))
                if vals(f"cuda{i}_power_w") else None for i in range(2)
            ],
        }


def source_corpus():
    root = Path(CFG["runtime"]["source_path"])
    suffixes = {".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".cu", ".cuh", ".py", ".sh", ".cmake"}
    parts = []
    for p in sorted(root.rglob("*"), key=lambda x: x.as_posix()):
        rel = p.relative_to(root)
        if not p.is_file() or any(x in {".git", "build", "build-prep"} for x in rel.parts):
            continue
        if p.suffix.lower() not in suffixes and p.name != "CMakeLists.txt":
            continue
        try:
            text = p.read_text(errors="replace")
        except OSError:
            continue
        parts.append(f"\n===== FILE: {rel.as_posix()} =====\n{text}\n")
    return "".join(parts)


def chat_payload(content, effort):
    return {
        "messages": [{"role": "user", "content": content}],
        "reasoning_effort": effort,
        "chat_template_kwargs": {"enable_thinking": True},
    }


def token_count(content, effort):
    rendered = api("POST", "/apply-template", chat_payload(content, effort), timeout=60)
    prompt = rendered.get("prompt", rendered.get("content"))
    if not isinstance(prompt, str):
        raise RuntimeError(f"unexpected apply-template response: {rendered}")
    tok = api("POST", "/tokenize", {"content": prompt, "add_special": False}, timeout=60)
    tokens = tok.get("tokens", [])
    return len(tokens), hashlib.sha256(prompt.encode()).hexdigest()


def calibrate_prompts(effort):
    corpus, task = source_corpus(), (ROOT / "prompts/task.txt").read_text()
    outputs = {}
    for ctx_s, goal in CFG["formal"]["target_prompt_tokens"].items():
        say(f"Calibrating prompt for ctx={ctx_s}, target={goal} tokens ...")
        lo, hi, best = 0, len(corpus), None
        while lo <= hi:
            mid = (lo + hi) // 2
            content = corpus[:mid] + "\n\n" + task
            n, digest = token_count(content, effort)
            if best is None or abs(n - goal) < abs(best[0] - goal):
                best = (n, mid, digest)
            if n < goal:
                lo = mid + 1
            elif n > goal:
                hi = mid - 1
            else:
                break
        n, chars, digest = best
        if abs(n - goal) > 16:
            raise RuntimeError(f"unable to calibrate {ctx_s}: got {n}, wanted {goal}")
        obj = {
            "configured_context": int(ctx_s), "target_tokens": goal,
            "calibrated_tokens": n, "corpus_prefix_chars": chars,
            "corpus_sha256": hashlib.sha256(corpus.encode()).hexdigest(),
            "chat_template_prompt_sha256": digest, "reasoning_effort": effort,
            "content": corpus[:chars] + "\n\n" + task,
        }
        atomic_json(ROOT / "prompts" / f"ctx-{ctx_s}-{effort}.json", obj)
        outputs[ctx_s] = {k: v for k, v in obj.items() if k != "content"}
        say(f"Calibration ctx={ctx_s}: {n} tokens.")
    atomic_json(ROOT / "prompts" / f"calibration-{effort}.json", outputs)
    return outputs


def warmup_request(effort: str):
    payload = chat_payload("Warm-up only. Return exactly the word READY and nothing else.", effort)
    payload.update({
        "model": "target", "stream": False, "max_tokens": 32,
        "temperature": 0.0, "top_p": 1.0, "top_k": 1, "min_p": 0.0,
        "presence_penalty": 0.0, "seed": CFG["formal"]["seed"],
    })
    started = time.monotonic()
    api("POST", "/v1/chat/completions", payload, timeout=600)
    return time.monotonic() - started


def parse_placement(log_path: Path, mode: str):
    if mode == "off":
        return {
            "draft_placement_detected": "disabled", "draft_device": None,
            "draft_cuda0_mib": 0, "draft_cuda1_mib": 0, "draft_cpu_mib": 0,
        }
    text = log_path.read_text(errors="replace")
    marker = text.find("loading draft model")
    section = text[marker:] if marker >= 0 else text
    values = {"CUDA0": 0.0, "CUDA1": 0.0, "CPU": 0.0}
    pattern = r"(CUDA\d+|CPU(?:_Mapped)?|CUDA_Host) model buffer size\s*=\s*([0-9.]+) MiB"
    for dev, mib in re.findall(pattern, section):
        key = dev if dev.startswith("CUDA") and dev != "CUDA_Host" else "CPU"
        if key in values:
            values[key] += float(mib)
    devices = [d for d in ("CUDA0", "CUDA1") if values[d] > 1]
    detected = ("GPU-resident:" + ",".join(devices)
                if devices and values["CPU"] < 1 else "mixed-or-cpu")
    return {
        "draft_placement_detected": detected,
        "draft_device": devices[0] if len(devices) == 1 else devices,
        "draft_cuda0_mib": values["CUDA0"], "draft_cuda1_mib": values["CUDA1"],
        "draft_cpu_mib": values["CPU"],
    }


def stream_request(payload, raw_path: Path):
    url = f"http://{CFG['server']['host']}:{CFG['server']['port']}/v1/chat/completions"
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    started = time.monotonic()
    first = None
    content = []
    usage = {}
    timings = {}
    last_choice = None
    last_event = None
    finish_reason = None
    chunks = 0
    last_progress = started

    with urllib.request.urlopen(req, timeout=7200) as resp, raw_path.open("wb") as raw:
        for line in resp:
            raw.write(line)
            raw.flush()
            if not line.startswith(b"data: "):
                continue
            data = line[6:].strip()
            if data == b"[DONE]":
                continue
            try:
                obj = json.loads(data)
            except json.JSONDecodeError:
                continue

            last_event = obj
            if isinstance(obj.get("usage"), dict):
                usage.update(obj["usage"])
            if isinstance(obj.get("timings"), dict):
                timings.update(obj["timings"])

            choices = obj.get("choices") or []
            if choices:
                choice = choices[0]
                last_choice = choice
                if choice.get("finish_reason") is not None:
                    finish_reason = choice.get("finish_reason")
                delta = choice.get("delta") or {}
                piece = delta.get("content") or delta.get("reasoning_content") or ""
                if piece:
                    content.append(piece)
                    chunks += 1
                    if first is None:
                        first = time.monotonic()
                        say(f"First streamed output after {first-started:.2f}s.")

            t = time.monotonic()
            if t - last_progress >= 15:
                out_chars = sum(len(x) for x in content)
                phase = "prefill / waiting for first output" if first is None else "decode"
                say(f"Request heartbeat: {phase}, elapsed={fmt_seconds(t-started)}, "
                    f"stream_chunks={chunks}, output_chars={out_chars}")
                last_progress = t

    ended = time.monotonic()
    merged = {
        "usage": usage, "timings": timings,
        "choices": [last_choice] if last_choice is not None else [],
        "finish_reason": finish_reason, "last_event": last_event,
    }
    return merged, "".join(content), (first-started if first else None), ended-started


def _log_slice(log_path: Path, offset: int):
    try:
        with log_path.open("rb") as f:
            f.seek(offset)
            return f.read().decode(errors="replace")
    except OSError:
        return ""


def parse_mtp_stats(log_text: str):
    drafted = accepted = mean_len = None
    drafted_patterns = [
        r"\bdraft_n\s*[=:]\s*(\d+)",
        r"\bdrafted(?:\s+tokens?)?\s*[=:]\s*(\d+)",
        r"\bdraft(?:ed)?\s+tokens?\s*[=:]\s*(\d+)",
    ]
    accepted_patterns = [
        r"\bdraft_n_accepted\s*[=:]\s*(\d+)",
        r"\baccepted(?:\s+draft)?(?:\s+tokens?)?\s*[=:]\s*(\d+)",
        r"\bdraft(?:ed)?\s+accepted\s*[=:]\s*(\d+)",
    ]
    mean_patterns = [
        r"mean(?:\s+accepted)?(?:\s+draft)?\s+len(?:gth)?\s*[=:]\s*([0-9.]+)",
        r"mean\s+accepted\s+length\s*[=:]\s*([0-9.]+)",
    ]
    for pattern in drafted_patterns:
        m = re.findall(pattern, log_text, re.I)
        if m:
            drafted = int(m[-1])
            break
    for pattern in accepted_patterns:
        m = re.findall(pattern, log_text, re.I)
        if m:
            accepted = int(m[-1])
            break
    for pattern in mean_patterns:
        m = re.findall(pattern, log_text, re.I)
        if m:
            mean_len = float(m[-1])
            break
    if drafted is None or accepted is None:
        pairs = re.findall(r"accepted\s+(\d+)\s*/\s*(\d+)", log_text, re.I)
        if pairs:
            accepted = int(pairs[-1][0])
            drafted = int(pairs[-1][1])
    return drafted, accepted, mean_len


def count_generated_tokens(text: str):
    try:
        tok = api("POST", "/tokenize", {"content": text, "add_special": False}, timeout=60)
        return len(tok.get("tokens", []))
    except Exception:
        return None


def server_metrics(final, log_path, log_offset, generated_text, wall, ttft, mtp_mode):
    timings = final.get("timings") or {}
    usage = final.get("usage") or {}
    prompt = usage.get("prompt_tokens") or timings.get("prompt_n") or timings.get("tokens_evaluated")
    gen = usage.get("completion_tokens") or timings.get("predicted_n")
    if gen is None:
        gen = count_generated_tokens(generated_text)
    gen = int(gen or 0)

    server_decode = timings.get("predicted_per_second")
    try:
        server_decode = float(server_decode) if server_decode is not None else None
    except (TypeError, ValueError):
        server_decode = None

    decode_wall = None
    client_decode = None
    if ttft is not None and wall is not None and wall > ttft:
        decode_wall = wall - ttft
        client_decode = gen / decode_wall if decode_wall > 0 else None
    end_to_end = gen / wall if wall else None

    drafted = timings.get("draft_n")
    accepted = timings.get("draft_n_accepted")
    formal_log = _log_slice(log_path, log_offset)
    log_drafted, log_accepted, log_mean = parse_mtp_stats(formal_log)
    if drafted is None:
        drafted = log_drafted
    if accepted is None:
        accepted = log_accepted

    parser_warning = None
    if mtp_mode != "off" and (drafted is None or accepted is None):
        parser_warning = "MTP counters unavailable in response and not recognized in formal-run log slice"

    drafted_i = int(drafted) if drafted is not None else None
    accepted_i = int(accepted) if accepted is not None else None
    rejected = None
    acceptance = None
    if drafted_i is not None and accepted_i is not None:
        rejected = max(0, drafted_i - accepted_i)
        acceptance = 100.0 * accepted_i / drafted_i if drafted_i else None

    return {
        "actual_prompt_tokens": int(prompt) if prompt is not None else None,
        "generated_tokens": gen,
        "pp_tokens_per_second": timings.get("prompt_per_second"),
        "server_decode_tps": server_decode,
        "client_decode_tps": client_decode,
        "client_decode_wall_seconds": decode_wall,
        "end_to_end_output_tps": end_to_end,
        "effective_tg_tokens_per_second": server_decode if server_decode is not None else client_decode,
        "drafted_token_count": drafted_i,
        "accepted_draft_token_count": accepted_i,
        "rejected_draft_token_count": rejected,
        "acceptance_percentage": acceptance,
        "mean_accepted_draft_length": log_mean,
        "mtp_metrics_parser_warning": parser_warning,
    }


def result_files():
    rows = []
    for p in sorted((ROOT / "experiments").glob("formal-*/result.json")):
        try:
            rows.append(json.loads(p.read_text()))
        except Exception:
            pass
    atomic_text(ROOT / "results.jsonl", "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
    cols = [
        "experiment_id", "status", "configured_context", "actual_prompt_tokens", "mtp_mode",
        "draft_device", "generated_tokens", "pp_tokens_per_second", "server_decode_tps",
        "client_decode_tps", "end_to_end_output_tps", "effective_tg_tokens_per_second",
        "ttft_seconds", "total_wall_seconds", "drafted_token_count", "accepted_draft_token_count",
        "acceptance_percentage", "mean_accepted_draft_length",
        "peak_vram_cuda0_mib", "peak_vram_cuda1_mib", "exit_code",
    ]
    import io
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
    atomic_text(ROOT / "summary.csv", out.getvalue())


def completion_manifest():
    states = []
    for ctx, mode in FORMAL_ORDER:
        p = ROOT / "experiments" / f"formal-{ctx}-{mode}" / "result.json"
        states.append(json.loads(p.read_text()).get("status") if p.exists() else "PLANNED")
    return {
        "total_planned": 9,
        "total_completed": states.count("COMPLETE"),
        "total_failed": states.count("FAILED"),
        "total_interrupted": states.count("INTERRUPTED"),
        "start_time": CAMPAIGN_START, "end_time": now(),
    }


def run_one(ctx, mode, effort, ordinal=None, remaining=None):
    global TELEMETRY, CURRENT_ID
    exp_id = f"formal-{ctx}-{mode}"
    CURRENT_ID = exp_id
    exp = ROOT / "experiments" / exp_id
    exp.mkdir(parents=True, exist_ok=True)
    log_path = ROOT / "logs" / f"{exp_id}.server.log"
    tel_path = ROOT / "telemetry" / f"{exp_id}.csv"
    prompt = json.loads((ROOT / "prompts" / f"ctx-{ctx}-{effort}.json").read_text())
    cmd = command_for(ctx, mode)
    idle = gpu_snapshot()
    started = now()
    requested = ("disabled" if mode == "off" else
                 ("runtime-default" if mode == "auto" else CFG["placements"][str(ctx)]["draft_gpu"]))

    rem = f", {remaining} remaining after this" if remaining is not None else ""
    say("=" * 72)
    say(f"RUN {ordinal}/9: ctx={ctx}, MTP={mode}{rem}")
    say("Command: " + " ".join(shlex.quote(x) for x in cmd))

    result = {
        "runner_schema_version": RUNNER_SCHEMA_VERSION,
        "experiment_id": exp_id, "status": "RUNNING", "timestamp": started,
        "exact_server_command": cmd, "runtime_commit": CFG["runtime"]["commit"],
        "runtime_version": CFG["runtime"]["version"],
        "target_model_identity": CFG["target"]["identity"],
        "target_model_path": CFG["target"]["first_shard"],
        "draft_identity": CFG["draft"]["identity"] if mode != "off" else None,
        "draft_path": CFG["draft"]["path"] if mode != "off" else None,
        "configured_context": ctx, "mtp_mode": mode,
        "requested_draft_placement": requested,
        "draft_n_max": 0 if mode == "off" else 3,
        "idle_vram_mib": [x["used_mib"] for x in idle],
        "reasoning_effort": effort,
        "exit_code": None, "truncation_flag": None, "server_error_flag": False,
    }
    atomic_json(exp / "result.json", result)

    try:
        proc = start_server(cmd, log_path)
        ready = gpu_snapshot()
        result["startup_vram_mib"] = [x["used_mib"] for x in ready]
        result.update(parse_placement(log_path, mode))
        say(f"Startup VRAM MiB: CUDA0={ready[0]['used_mib']:.0f}, CUDA1={ready[1]['used_mib']:.0f}; "
            f"draft={result.get('draft_placement_detected')}")
        if max(ready[0]["used_mib"], ready[1]["used_mib"]) < 8192:
            say("WARNING: target placement is very CPU-heavy (<8 GiB used on each GPU).")
            say("WARNING: check config.json target_args if this was not intentional.")

        say("Running identical unmeasured warm-up ...")
        warm_s = warmup_request(effort)
        result["warmup_wall_seconds"] = warm_s
        say(f"Warm-up complete in {fmt_seconds(warm_s)}.")

        try:
            formal_log_offset = log_path.stat().st_size
        except OSError:
            formal_log_offset = 0
        result["formal_log_offset_bytes"] = formal_log_offset

        TELEMETRY = Monitor(tel_path, proc.pid)
        TELEMETRY.start()

        payload = chat_payload(prompt["content"], effort)
        payload.update({
            "model": "target", "stream": True,
            "stream_options": {"include_usage": True},
            "max_tokens": CFG["formal"]["generation_tokens"],
            "temperature": 1.0, "top_p": 0.95, "top_k": 20,
            "min_p": 0.0, "presence_penalty": 0.0,
            "seed": CFG["formal"]["seed"],
        })
        atomic_json(exp / "request.json", payload)
        say(f"Formal request starting; calibrated prompt={prompt.get('calibrated_tokens')} tokens, "
            f"max_output={CFG['formal']['generation_tokens']}.")

        final, generated_text, ttft, wall = stream_request(payload, exp / "raw-stream.sse")
        atomic_text(exp / "generated.txt", generated_text)
        result.update(server_metrics(
            final, log_path, formal_log_offset, generated_text, wall, ttft, mode
        ))

        if result.get("actual_prompt_tokens") is None:
            result["actual_prompt_tokens"] = prompt.get("calibrated_tokens")
            result["actual_prompt_tokens_source"] = "calibrated"
        else:
            result["actual_prompt_tokens_source"] = "server"

        finish_reason = final.get("finish_reason")
        if finish_reason is None and final.get("choices"):
            finish_reason = (final["choices"][0] or {}).get("finish_reason")
        result.update({
            "ttft_seconds": ttft, "total_wall_seconds": wall,
            "finish_reason": finish_reason,
            "truncation_flag": finish_reason == "length",
        })
        result["status"] = "COMPLETE"
        say(f"Formal request complete: prompt={result.get('actual_prompt_tokens')}, "
            f"generated={result.get('generated_tokens')}, TTFT={fmt_seconds(ttft)}, "
            f"server TG={result.get('server_decode_tps')}, client TG={result.get('client_decode_tps')}, "
            f"acceptance={result.get('acceptance_percentage')}%.")

    except KeyboardInterrupt:
        result.update({"status": "INTERRUPTED", "server_error_flag": True})
        say(f"{exp_id}: INTERRUPTED.")
        raise
    except Exception as e:
        result.update({"status": "FAILED", "server_error_flag": True, "error": repr(e)})
        say(f"{exp_id}: FAILED: {e!r}")
    finally:
        if TELEMETRY:
            TELEMETRY.stop()
            result.update(TELEMETRY.summary())
            TELEMETRY = None
        shutdown_code = stop_server()
        result["server_shutdown_exit_code"] = shutdown_code
        result["exit_code"] = 0 if result.get("status") == "COMPLETE" else shutdown_code
        try:
            result["post_release_vram_mib"] = [x["used_mib"] for x in wait_gpu_release(idle)]
        except Exception as e:
            result["gpu_release_error"] = repr(e)
            result["status"] = "FAILED"

        result["end_timestamp"] = now()
        off_result = ROOT / "experiments" / f"formal-{ctx}-off" / "result.json"
        baseline = CFG["placements"][str(ctx)]["target_only_startup_used_mib"]
        if off_result.exists():
            try:
                off_obj = json.loads(off_result.read_text())
                if off_obj.get("runner_schema_version") == RUNNER_SCHEMA_VERSION:
                    baseline = off_obj.get("startup_vram_mib", baseline)
            except Exception:
                pass
        if result.get("startup_vram_mib"):
            result["mtp_incremental_vram_mib"] = (
                [0, 0] if mode == "off" else
                [result["startup_vram_mib"][i] - baseline[i] for i in range(2)]
            )
        atomic_json(exp / "result.json", result)
        result_files()
        CURRENT_ID = None
        say(f"{exp_id}: status={result['status']}; saved {exp/'result.json'}")
    return result["status"]


def interrupt_handler(signum, frame):
    raise KeyboardInterrupt


def valid_complete(ctx, mode):
    p = ROOT / "experiments" / f"formal-{ctx}-{mode}" / "result.json"
    if not p.exists():
        return False
    try:
        obj = json.loads(p.read_text())
    except Exception:
        return False
    return obj.get("status") == "COMPLETE" and obj.get("runner_schema_version") == RUNNER_SCHEMA_VERSION


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rerun", action="store_true")
    parser.add_argument("--rehash", action="store_true")
    parser.add_argument("--reasoning-effort", choices=("low", "medium", "xhigh"), default="xhigh")
    parser.add_argument("--calibrate-only", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    signal.signal(signal.SIGINT, interrupt_handler)
    signal.signal(signal.SIGTERM, interrupt_handler)

    say("Qwen3.8-Flash-Next Q6 + Q8 MTP benchmark runner v2")
    say("Formal matrix: 9 runs = 32K/64K/128K x off/auto/forced-gpu")
    say("Running preflight ...")
    info = preflight(args.rehash)
    atomic_json(ROOT / "preflight.json", {"timestamp": now(), **info})
    say(f"Preflight OK. RAM available={info['available_ram_bytes']/2**30:.1f} GiB, "
        f"disk free={info['free_disk_bytes']/2**30:.1f} GiB.")

    prompt_file = ROOT / "prompts" / f"ctx-131072-{args.reasoning_effort}.json"
    if not prompt_file.exists():
        say(f"Prompt calibration for reasoning_effort={args.reasoning_effort} is missing.")
        say("Starting temporary 128K server for tokenizer/template calibration only ...")
        proc = start_server(base_command(131072),
                            ROOT / "logs" / f"calibration-{args.reasoning_effort}.server.log")
        try:
            calibrate_prompts(args.reasoning_effort)
        finally:
            stop_server()
        say("Prompt calibration complete.")

    if args.calibrate_only:
        result_files()
        say("Calibration-only mode complete.")
        return 0

    stale = []
    complete = set()
    for ctx, mode in FORMAL_ORDER:
        p = ROOT / "experiments" / f"formal-{ctx}-{mode}" / "result.json"
        if not p.exists():
            continue
        try:
            obj = json.loads(p.read_text())
        except Exception:
            continue
        if obj.get("status") == "COMPLETE" and obj.get("runner_schema_version") == RUNNER_SCHEMA_VERSION:
            complete.add((ctx, mode))
        elif obj.get("status") == "COMPLETE":
            stale.append((ctx, mode))

    if stale:
        say("Found COMPLETE results from the old/broken runner; they will NOT be reused: "
            + ", ".join(f"{c}/{m}" for c, m in stale))

    pending = FORMAL_ORDER if args.rerun else [x for x in FORMAL_ORDER if x not in complete]
    say(f"Resume state: {len(complete)}/9 valid runs already complete; {len(pending)} to execute.")

    try:
        for idx, (ctx, mode) in enumerate(pending, start=1):
            global_idx = FORMAL_ORDER.index((ctx, mode)) + 1
            remaining = len(pending) - idx
            status = run_one(ctx, mode, args.reasoning_effort,
                             ordinal=global_idx, remaining=remaining)
            done_now = sum(1 for c, m in FORMAL_ORDER if valid_complete(c, m))
            say(f"Campaign progress: {done_now}/9 COMPLETE, {9-done_now} not complete.")
            if status != "COMPLETE":
                say("Continuing to next planned arm; failed arm remains resumable.")
    except KeyboardInterrupt:
        atomic_json(ROOT / "RUN_COMPLETE.json", completion_manifest())
        say("Campaign interrupted cleanly. Re-run the same command to resume.")
        return 130

    manifest = completion_manifest()
    atomic_json(ROOT / "RUN_COMPLETE.json", manifest)
    say("=" * 72)
    say(f"Campaign finished: completed={manifest['total_completed']}/9, "
        f"failed={manifest['total_failed']}, interrupted={manifest['total_interrupted']}.")
    say(f"Summary: {ROOT/'summary.csv'}")
    say(f"JSONL:   {ROOT/'results.jsonl'}")
    return 0 if manifest["total_failed"] == 0 and manifest["total_completed"] == 9 else 1


if __name__ == "__main__":
    sys.exit(main())
