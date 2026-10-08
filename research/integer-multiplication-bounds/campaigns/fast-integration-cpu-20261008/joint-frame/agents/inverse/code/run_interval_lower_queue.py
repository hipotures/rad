#!/usr/bin/env python3
"""Run exact positive/error-lower controls in one owned replacement lane."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pause-owned-pid", type=int, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--run-prefix", required=True)
    args = parser.parse_args()
    agent = Path(__file__).resolve().parents[1]
    source = agent / "code/dyadic_interval_lower.py"
    sources = [source, Path(__file__).resolve()]
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    configs = [
        ("complete127", 127, 128, 2, 128, "complete", "CERTIFIED"),
        ("drop-wrap127", 127, 128, 2, 128, "drop-wrap", "DISPROVED"),
        ("low-precision127", 127, 128, 2, 128, "low-precision", "DISPROVED"),
        ("narrow-proposal127", 127, 128, 2, 128, "narrow-band", "DISPROVED"),
        ("near4093", 4093, 4096, 2, 256, "complete", "CERTIFIED"),
        ("admissible4093", 4093, 4096, 64, 512, "complete", "CERTIFIED"),
    ]
    prepared = []
    for label, s, t, alpha, q, mode, expected in configs:
        run_id = args.run_prefix + "-interval-lower-" + label
        durable, raw = agent / "runs" / run_id, args.output_root / run_id
        (durable / "code").mkdir(parents=True, exist_ok=False)
        (durable / "results").mkdir()
        raw.mkdir(parents=True, exist_ok=False)
        for path in sources:
            shutil.copy2(path, durable / "code" / path.name)
        flags = ["--source", str(s), "--target", str(t), "--alpha", str(alpha),
                 "--target-bits", str(q), "--mode", mode, "--seed", "202610081752"]
        protocol = {
            "run_id": run_id, "status": "queued", "queued_utc": datetime.now(timezone.utc).isoformat(),
            "source_sha256": hashes, "arguments": flags,
            "reproduction": "python3 code/dyadic_interval_lower.py " + " ".join(flags) + " --output <fresh-ignored-work>/certificate.json",
            "dependencies": "Python3 standard library only", "workers": 1, "native_threads": 1,
            "input_generator": "Random sixteenth-grid RHS; frozen exact dyadic words from an untrusted sparse bordered Decimal proposal",
            "methodology": "Integer Machin/exp enclosures, full residual upper/lower, ALL-alias tail, row-DD upper and matrix-norm lower solution-error bounds",
            "expected_status": "RIGOROUS_TARGET_" + expected,
            "negative_control": mode if mode != "complete" else None,
            "raw_execution_path": str(raw),
        }
        save(durable / "protocol.json", protocol)
        prepared.append((durable, raw, protocol))
    process = Path("/proc") / str(args.pause_owned_pid) / "cmdline"

    def identified():
        if not process.exists():
            return False
        cmd = process.read_bytes().replace(b"\x00", b" ").decode()
        return "compiled_crt_pipeline_guard2.py --family bank131 " in cmd and "fast-integration-cpu-20261008" in cmd

    assert identified(), "live process does not match the owned replacement worker"
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    os.kill(args.pause_owned_pid, signal.SIGSTOP)
    try:
        for durable, raw, protocol in prepared:
            assert hashlib.sha256(source.read_bytes()).hexdigest() == hashes[source.name]
            command = ["python3", "-u", str(source)] + protocol["arguments"] + ["--output", str(raw / "certificate.json")]
            protocol.update(status="running", start_unix_time=time.time())
            with (raw / "stdout.log").open("w") as log:
                child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env)
                protocol["compute_pid"] = child.pid
                save(durable / "protocol.json", protocol)
                print(json.dumps({"run_id": protocol["run_id"], "pid": child.pid, "status": "running"}), flush=True)
                exit_code = child.wait()
            protocol["exit_code"] = exit_code
            certificate = raw / "certificate.json"
            if certificate.exists():
                result = json.loads(certificate.read_text())
                assert certificate.stat().st_size < 1048576, "keep larger evidence in raw work and archive explicitly"
                shutil.copy2(certificate, durable / "results/certificate.json")
                protocol.update(status=result["status"], expected_matched=result["status"] == protocol["expected_status"],
                                wall_seconds=result["wall_seconds"], certificate_sha256=hashlib.sha256(certificate.read_bytes()).hexdigest())
            else:
                protocol["status"] = "NO_CERTIFICATE"
            protocol["completed_unix_time"] = time.time()
            save(durable / "protocol.json", protocol)
            print(json.dumps({"run_id": protocol["run_id"], "status": protocol["status"], "exit_code": exit_code}), flush=True)
            assert exit_code == 0 and protocol.get("expected_matched") is True, "control disagrees with its predeclared outcome"
        for index in (0, 1, 3):
            durable, raw, protocol = prepared[index]
            replay = raw / "replay-certificate.json"
            subprocess.run(["python3", str(source), "--verify-certificate", str(durable / "results/certificate.json"),
                            "--output", str(replay)], check=True, env=env)
            result = json.loads(replay.read_text())
            assert result["status"] == protocol["expected_status"]
            shutil.copy2(replay, durable / "results/replay-certificate.json")
            protocol["replay_sha256"] = hashlib.sha256(replay.read_bytes()).hexdigest()
            protocol["replay_reproduction"] = "python3 code/dyadic_interval_lower.py --verify-certificate results/certificate.json --output <fresh-ignored-work>/replay.json"
            save(durable / "protocol.json", protocol)
    finally:
        if identified():
            os.kill(args.pause_owned_pid, signal.SIGCONT)
            print(json.dumps({"resumed_owned_pid": args.pause_owned_pid}), flush=True)


if __name__ == "__main__":
    main()
