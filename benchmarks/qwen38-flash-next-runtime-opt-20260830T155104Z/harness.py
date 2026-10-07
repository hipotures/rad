#!/usr/bin/env python3
"""Reproducible controller for the fresh Qwen3.8-Flash-Next campaign."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import os
import pathlib
import signal
import statistics
import subprocess
import threading
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
SERVER = pathlib.Path("/srv/ai/llama.cpp-qwen4exp/build-cuda-sm89/bin/llama-server")
MODEL = pathlib.Path("/srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-IQ4XS/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00003.gguf")
COMMIT = "250b61446efc91e3a179c8677956f2667c8fbda0"
HOST = "127.0.0.1"
PORT = 18080


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write_json(path: pathlib.Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def http_json(path: str, payload: object | None = None, timeout: float = 3600) -> object:
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        f"http://{HOST}:{PORT}{path}", data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read())


def wait_ready(proc: subprocess.Popen[bytes], timeout: float = 900) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"server exited during startup with {proc.returncode}")
        try:
            if http_json("/health", timeout=2).get("status") == "ok":
                return
        except Exception:
            pass
        time.sleep(1)
    raise TimeoutError("server did not become healthy")


def tokenize(content: str) -> list[int]:
    value = http_json("/tokenize", {"content": content, "add_special": False})
    return list(value["tokens"])


CORPUS = """Case file {case}: The application received a request to reconcile inventory, delivery, and billing records. Evidence includes dated events, identifiers, quantities, exceptions, and operator notes. Analyze causal order, retain exact constraints, distinguish observations from conclusions, and identify unresolved contradictions. The response must remain grounded in the supplied record.\n"""


def corpus_tokens(minimum: int) -> list[int]:
    paragraphs = []
    # Numerals and varied sentences make this closer to document/agent context than one repeated token.
    for i in range(max(4000, minimum // 35 + 200)):
        paragraphs.append(CORPUS.format(case=i))
    tokens = tokenize("".join(paragraphs))
    if len(tokens) < minimum:
        raise RuntimeError(f"corpus only produced {len(tokens)} tokens")
    return tokens


def nonce_tokens(label: str) -> list[int]:
    return tokenize(f"Fresh experiment nonce {label} {utc()}\n")


class Telemetry:
    def __init__(self, experiment_id: str, pid: int, profile_tools: bool = False):
        self.experiment_id = experiment_id
        self.pid = pid
        self.stop_event = threading.Event()
        self.rows: list[dict] = []
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.proc_start = self._proc()
        self.profile_tools = profile_tools
        self.profile_processes: list[tuple[subprocess.Popen[bytes], object]] = []

    def _proc(self) -> dict:
        result: dict[str, object] = {}
        try:
            stat = pathlib.Path(f"/proc/{self.pid}/stat").read_text().split()
            status = pathlib.Path(f"/proc/{self.pid}/status").read_text().splitlines()
            io = pathlib.Path(f"/proc/{self.pid}/io").read_text().splitlines()
            result.update({"minflt": int(stat[9]), "majflt": int(stat[11]),
                           "proc_ticks": int(stat[13]) + int(stat[14])})
            for line in status:
                if line.startswith(("VmRSS:", "VmHWM:", "Threads:")):
                    key, value = line.split(":", 1)
                    result[key] = value.strip()
            for line in io:
                key, value = line.split(":", 1)
                if key in ("read_bytes", "rchar"):
                    result[key] = int(value)
            thread_ticks = {}
            for task in pathlib.Path(f"/proc/{self.pid}/task").iterdir():
                fields = (task / "stat").read_text().split()
                thread_ticks[task.name] = int(fields[13]) + int(fields[14])
            result["thread_ticks"] = thread_ticks
        except (FileNotFoundError, ProcessLookupError):
            pass
        return result

    def _loop(self) -> None:
        query = "index,timestamp,utilization.gpu,utilization.memory,power.draw,memory.used,clocks.sm,clocks.mem"
        while not self.stop_event.is_set():
            row: dict[str, object] = {"monotonic": time.monotonic(), "proc": self._proc()}
            try:
                out = subprocess.check_output(
                    ["nvidia-smi", f"--query-gpu={query}", "--format=csv,noheader,nounits"],
                    text=True, timeout=3,
                )
                row["gpu"] = [[x.strip() for x in line.split(",")] for line in out.splitlines()]
            except Exception as exc:
                row["gpu_error"] = repr(exc)
            self.rows.append(row)
            self.stop_event.wait(0.5)

    def __enter__(self) -> "Telemetry":
        if self.profile_tools:
            commands = {
                "nvidia-dmon": ["nvidia-smi", "dmon", "-s", "pucvmt", "-d", "1", "-o", "DT"],
                "pidstat": ["pidstat", "-p", str(self.pid), "-t", "-u", "-r", "-d", "-w", "1"],
                "vmstat": ["vmstat", "1"],
                "iostat": ["iostat", "-dx", "1"],
            }
            snapshots = {}
            for label, command in (("numastat_before", ["numastat", "-p", str(self.pid)]),
                                   ("proc_numa_maps_before", ["head", "-n", "200", f"/proc/{self.pid}/numa_maps"])):
                try:
                    snapshots[label] = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)
                except Exception as exc:
                    snapshots[label] = repr(exc)
            write_json(ROOT / "raw" / f"{self.experiment_id}-profile-snapshots-before.json", snapshots)
            for label, command in commands.items():
                handle = (ROOT / "raw" / f"{self.experiment_id}-{label}.log").open("wb")
                process = subprocess.Popen(command, stdout=handle, stderr=subprocess.STDOUT,
                                           start_new_session=True)
                self.profile_processes.append((process, handle))
        self.thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.stop_event.set()
        self.thread.join(timeout=5)
        for process, handle in self.profile_processes:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
            handle.close()
        if self.profile_tools:
            snapshots = {}
            for label, command in (("numastat_after", ["numastat", "-p", str(self.pid)]),
                                   ("proc_numa_maps_after", ["head", "-n", "200", f"/proc/{self.pid}/numa_maps"])):
                try:
                    snapshots[label] = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)
                except Exception as exc:
                    snapshots[label] = repr(exc)
            write_json(ROOT / "raw" / f"{self.experiment_id}-profile-snapshots-after.json", snapshots)
        write_json(ROOT / "telemetry" / f"{self.experiment_id}.json", {
            "process_start": self.proc_start, "process_end": self._proc(), "samples": self.rows,
        })

    def summary(self) -> dict:
        used = [[], []]
        util = [[], []]
        power = [[], []]
        for row in self.rows:
            for gpu in row.get("gpu", []):
                idx = int(gpu[0])
                util[idx].append(float(gpu[2]))
                power[idx].append(float(gpu[4]))
                used[idx].append(float(gpu[5]))
        result = {
            "vram_peak_mib": [max(x, default=0) for x in used],
            "gpu_util_avg_pct": [statistics.fmean(x) if x else 0 for x in util],
            "gpu_util_peak_pct": [max(x, default=0) for x in util],
            "gpu_power_avg_w": [statistics.fmean(x) if x else 0 for x in power],
            "gpu_power_peak_w": [max(x, default=0) for x in power],
        }
        if self.rows:
            first = self.rows[0].get("proc", {})
            last = self.rows[-1].get("proc", {})
            elapsed = max(1e-9, self.rows[-1]["monotonic"] - self.rows[0]["monotonic"])
            clk = os.sysconf("SC_CLK_TCK")
            result.update({
                "process_cpu_avg_pct": 100 * (last.get("proc_ticks", 0) - first.get("proc_ticks", 0)) / clk / elapsed,
                "major_faults_delta": last.get("majflt", 0) - first.get("majflt", 0),
                "minor_faults_delta": last.get("minflt", 0) - first.get("minflt", 0),
                "storage_read_bytes_delta": last.get("read_bytes", 0) - first.get("read_bytes", 0),
                "rchar_delta": last.get("rchar", 0) - first.get("rchar", 0),
            })
            thread_delta = {tid: ticks - first.get("thread_ticks", {}).get(tid, ticks)
                            for tid, ticks in last.get("thread_ticks", {}).items()}
            result["max_thread_cpu_pct"] = 100 * max(thread_delta.values(), default=0) / clk / elapsed
        return result


def unique_leading_token(label: str) -> int:
    # An ordinary in-vocabulary ID, made deterministic from the experiment ID.
    return 1000 + int.from_bytes(hashlib.sha256(label.encode()).digest()[:3], "big") % 100000


def completion(experiment_id: str, prompt: list[int], n_predict: int, slot: int = -1) -> dict:
    payload = {
        "prompt": prompt, "n_predict": n_predict, "stream": True, "cache_prompt": True,
        "id_slot": slot, "temperature": 0.0, "ignore_eos": True, "timings_per_token": False,
    }
    req = urllib.request.Request(
        f"http://{HOST}:{PORT}/completion", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    started = time.monotonic()
    first = None
    events = []
    text_parts = []
    final = {}
    with urllib.request.urlopen(req, timeout=7200) as response:
        for raw in response:
            line = raw.decode(errors="replace").strip()
            if not line.startswith("data: "):
                continue
            event = json.loads(line[6:])
            events.append(event)
            if event.get("content"):
                if first is None:
                    first = time.monotonic()
                text_parts.append(event["content"])
            if event.get("stop"):
                final = event
    ended = time.monotonic()
    response_obj = {
        "request_payload": payload,
        "events": events,
        "text": "".join(text_parts),
        "final": final,
        "client": {"started_monotonic": started, "first_monotonic": first, "ended_monotonic": ended,
                   "ttft_s": None if first is None else first - started, "wall_s": ended - started},
    }
    write_json(ROOT / "responses" / f"{experiment_id}.json", response_obj)
    return response_obj


def record_from_response(experiment_id: str, cfg: dict, response: dict, telemetry: Telemetry) -> dict:
    final = response.get("final", {})
    timings = final.get("timings", {})
    client = response["client"]
    prompt_tokens = len(response["request_payload"]["prompt"])
    cached = int(timings.get("cache_n") or 0)
    generated = int(timings.get("predicted_n") or 0)
    record = {
        "experiment_id": experiment_id, "hypothesis": cfg.get("hypothesis", ""),
        "runtime_commit": COMMIT, "command": cfg["command"],
        "context_configured": cfg["ctx"], "context_per_slot": cfg["ctx"] // cfg["parallel"],
        "prompt_tokens": prompt_tokens, "generated_tokens": generated,
        "concurrency": cfg.get("concurrency", 1), "shared_prefix_tokens": cfg.get("shared_prefix_tokens", 0),
        "cache_reused_tokens": cached, "newly_processed_tokens": int(timings.get("prompt_n") or 0),
        "batch": cfg["batch"], "ubatch": cfg["ubatch"], "placement": cfg["placement"],
        "kv_type": cfg.get("kv_type", "f16/f16"),
        "pp_tps": float(timings.get("prompt_per_second") or 0),
        "tg_tps": float(timings.get("predicted_per_second") or 0),
        "aggregate_tg_tps": float(timings.get("predicted_per_second") or 0),
        "ttft_s": client["ttft_s"], "wall_s": client["wall_s"],
        "rss_gib": 0.0, "result": "PASS" if generated == cfg["n_predict"] else "FAIL",
        "timings": timings, "telemetry": telemetry.summary(), "recorded_at": utc(),
    }
    samples = telemetry.rows
    rss_values = []
    for row in samples:
        rss = row.get("proc", {}).get("VmRSS", "0 kB")
        try:
            rss_values.append(int(str(rss).split()[0]) / 2**20)
        except Exception:
            pass
    record["rss_gib"] = max(rss_values, default=0)
    write_json(ROOT / "records" / f"{experiment_id}.json", record)
    return record


def server_command(args: argparse.Namespace) -> list[str]:
    cmd = [str(SERVER), "-m", str(MODEL), "--host", HOST, "--port", str(PORT),
           "-c", str(args.ctx), "-np", str(args.parallel), "-b", str(args.batch),
           "-ub", str(args.ubatch), "-t", str(args.threads), "-tb", str(args.threads_batch),
           "-ngl", "all", "-sm", "layer", "-ts", args.tensor_split,
           "-ot", args.placement, "--tensor-read-lazy", args.lazy, "-fa", args.fa,
           "--cache-reuse", str(args.cache_reuse), "--metrics", "--slots", "--perf",
           "--no-warmup", "--log-verbosity", str(args.log_verbosity)]
    return cmd


def run_group(args: argparse.Namespace) -> None:
    group_id = args.group_id
    log_path = ROOT / "logs" / f"{group_id}-server.log"
    cmd = server_command(args)
    cfg_base = {
        "runtime_commit": COMMIT, "command": cmd, "ctx": args.ctx, "parallel": args.parallel,
        "batch": args.batch, "ubatch": args.ubatch, "placement": args.placement,
        "lazy": args.lazy, "fa": args.fa, "kv_type": "f16/f16", "n_predict": args.n_predict,
        "concurrency": args.concurrency, "started_at": utc(),
    }
    write_json(ROOT / "configs" / f"{group_id}.json", cfg_base)
    with log_path.open("wb") as log:
        env = os.environ.copy()
        if args.no_cuda_graphs:
            # This runtime exposes graph control through the CUDA backend environment,
            # not a llama-server CLI flag (common.cuh:1258 at the recorded commit).
            env["GGML_CUDA_DISABLE_GRAPHS"] = "1"
        startup_started = time.monotonic()
        proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT,
                                start_new_session=True, env=env)
        try:
            wait_ready(proc)
            cfg_base["server_ready_at"] = utc()
            cfg_base["server_startup_s"] = time.monotonic() - startup_started
            write_json(ROOT / "configs" / f"{group_id}.json", cfg_base)
            max_prompt = args.ctx // args.parallel - args.n_predict - args.headroom
            corpus = corpus_tokens(max_prompt + 1024)
            if args.mode == "baseline":
                for phase in ("cold", "warm"):
                    exp_id = f"{group_id}-{phase}"
                    nonce = nonce_tokens(f"{group_id}-{phase}")
                    prompt = (nonce + corpus)[:max_prompt]
                    prompt[0] = unique_leading_token(exp_id)
                    write_json(ROOT / "prompts" / f"{exp_id}.json", {"tokens": prompt})
                    cfg = dict(cfg_base, hypothesis=f"{phase.upper()} single-stream near-limit baseline")
                    with Telemetry(exp_id, proc.pid, args.profile_tools) as tel:
                        response = completion(exp_id, prompt, args.n_predict, 0)
                    record_from_response(exp_id, cfg, response, tel)
            elif args.mode == "prefix":
                shared_n = args.shared_prefix
                common = corpus[:shared_n]
                suffix_len = max_prompt - shared_n
                for label in ("A", "B"):
                    exp_id = f"{group_id}-{label}"
                    suffix = (nonce_tokens(f"suffix-{label}") + corpus[::-1])[:suffix_len]
                    prompt = common + suffix
                    write_json(ROOT / "prompts" / f"{exp_id}.json", {"tokens": prompt})
                    cfg = dict(cfg_base, shared_prefix_tokens=shared_n,
                               hypothesis="Exact stable prefix with a genuinely different suffix")
                    with Telemetry(exp_id, proc.pid, args.profile_tools) as tel:
                        response = completion(exp_id, prompt, args.n_predict, 0)
                    record_from_response(exp_id, cfg, response, tel)
                exp_id = f"{group_id}-C-mutated"
                mutated = list(common)
                mutation = nonce_tokens(f"midpoint-mutation-{group_id}")
                midpoint = len(mutated) // 2
                mutated[midpoint:midpoint + len(mutation)] = mutation
                suffix = (nonce_tokens("suffix-C") + corpus[::-1])[:suffix_len]
                prompt = mutated + suffix
                write_json(ROOT / "prompts" / f"{exp_id}.json", {"tokens": prompt})
                cfg = dict(cfg_base, shared_prefix_tokens=shared_n,
                           hypothesis="Mid-prefix mutation should invalidate subsequent KV state")
                with Telemetry(exp_id, proc.pid, args.profile_tools) as tel:
                    response = completion(exp_id, prompt, args.n_predict, 0)
                record_from_response(exp_id, cfg, response, tel)
            elif args.mode == "concurrency":
                prompts = []
                for i in range(args.concurrency):
                    nonce = nonce_tokens(f"{group_id}-client-{i}")
                    # A unique first token guarantees no valid shared prefix.
                    prompt = (nonce + corpus)[:max_prompt]
                    prompt[0] = unique_leading_token(f"{group_id}-client-{i}")
                    prompts.append(prompt)
                start = time.monotonic()
                exp_ids = [f"{group_id}-client-{i}" for i in range(args.concurrency)]
                with Telemetry(group_id, proc.pid, args.profile_tools) as tel:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
                        futures = [pool.submit(completion, eid, prompt, args.n_predict, i)
                                   for i, (eid, prompt) in enumerate(zip(exp_ids, prompts))]
                        responses = [f.result() for f in futures]
                end = time.monotonic()
                records = []
                for eid, response in zip(exp_ids, responses):
                    cfg = dict(cfg_base, hypothesis="Independent simultaneous long-context request")
                    records.append(record_from_response(eid, cfg, response, tel))
                generated = sum(x["generated_tokens"] for x in records)
                # Aggregate output throughput is measured over the interval in
                # which at least one client is producing output. Keep the
                # end-to-end request throughput separately so prompt ingest is
                # not mislabeled as decode throughput.
                output_window_s = max(x["wall_s"] for x in records) - min(x["ttft_s"] for x in records)
                aggregate = generated / output_window_s
                end_to_end = generated / (end - start)
                summary = dict(cfg_base, experiment_id=group_id, result="PASS" if all(x["result"] == "PASS" for x in records) else "FAIL",
                               prompt_tokens=[x["prompt_tokens"] for x in records], generated_tokens=generated,
                               per_user_tg_tps=[x["tg_tps"] for x in records], aggregate_tg_tps=aggregate,
                               end_to_end_output_tps=end_to_end, output_window_s=output_window_s,
                               ttft_s=[x["ttft_s"] for x in records], wall_s=end-start, telemetry=tel.summary())
                write_json(ROOT / "records" / f"{group_id}.json", summary)
            elif args.mode == "single":
                exp_id = group_id
                nonce = nonce_tokens(group_id)
                prompt = (nonce + corpus)[:max_prompt]
                prompt[0] = unique_leading_token(exp_id)
                write_json(ROOT / "prompts" / f"{exp_id}.json", {"tokens": prompt})
                cfg = dict(cfg_base, hypothesis=args.hypothesis)
                with Telemetry(exp_id, proc.pid, args.profile_tools) as tel:
                    response = completion(exp_id, prompt, args.n_predict, 0)
                record_from_response(exp_id, cfg, response, tel)
            else:
                raise ValueError(args.mode)
        except Exception as exc:
            write_json(ROOT / "records" / f"{group_id}-failure.json", {
                **cfg_base, "experiment_id": group_id, "result": "FAIL", "error": repr(exc), "recorded_at": utc(),
            })
            raise
        finally:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
            cfg_base["server_exit_code"] = proc.returncode
            cfg_base["finished_at"] = utc()
            write_json(ROOT / "configs" / f"{group_id}.json", cfg_base)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("baseline", "prefix", "concurrency", "single"))
    parser.add_argument("group_id")
    parser.add_argument("--ctx", type=int, required=True)
    parser.add_argument("--parallel", type=int, default=1)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--batch", type=int, default=2048)
    parser.add_argument("--ubatch", type=int, default=512)
    parser.add_argument("--threads", type=int, default=16)
    parser.add_argument("--threads-batch", type=int, default=16)
    parser.add_argument("--tensor-split", default="1,1")
    parser.add_argument("--placement", required=True)
    parser.add_argument("--lazy", choices=("on", "off", "auto"), default="on")
    parser.add_argument("--fa", choices=("on", "off", "auto"), default="on")
    parser.add_argument("--cache-reuse", type=int, default=0)
    parser.add_argument("--n-predict", type=int, default=512)
    parser.add_argument("--headroom", type=int, default=768)
    parser.add_argument("--shared-prefix", type=int, default=0)
    parser.add_argument("--log-verbosity", type=int, default=5)
    parser.add_argument("--no-cuda-graphs", action="store_true")
    parser.add_argument("--profile-tools", action="store_true")
    parser.add_argument("--hypothesis", default="")
    args = parser.parse_args()
    if args.mode == "prefix" and not args.shared_prefix:
        parser.error("prefix mode requires --shared-prefix")
    if args.mode == "concurrency" and args.parallel != args.concurrency:
        parser.error("concurrency mode requires equal --parallel and --concurrency")
    run_group(args)


if __name__ == "__main__":
    main()
