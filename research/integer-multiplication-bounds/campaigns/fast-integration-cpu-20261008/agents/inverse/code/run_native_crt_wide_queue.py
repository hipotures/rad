#!/usr/bin/env python3
"""One-slot native discriminator queue, replacing one owned Python slot.

Completed raw outputs remain unchanged under ignored work/. Each completed
certificate is copied to its fresh durable run; source and build provenance
are pinned before execution. This controller is idle while its one compiler
or native child uses the assigned CPU. It restores the paused owned job in
finally, including when a scientifically useful negative fails an assertion.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pause-owned-pid", type=int, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    agent = Path(__file__).resolve().parents[1]
    campaign = agent.parents[1]
    source = agent / "code/compiled_crt_native_wide.cpp"
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    compiler = subprocess.check_output(["g++", "--version"], text=True).splitlines()[0]
    configs = [
        ("inner2outer2-two-nodes", "inner2outer2-bank", 2, 2, None),
        ("outer3-two-nodes", "guard3-bank", 3, 1, None),
    ]
    prepared = []
    for label, family, gout, gin, negative in configs:
        run_id = "20261008T1540Z-native-" + label
        durable = agent / "runs" / run_id
        assert not durable.exists(), ("run already exists", durable)
        (durable / "code").mkdir(parents=True)
        (durable / "results").mkdir()
        shutil.copy2(source, durable / "code/compiled_crt_native_wide.cpp")
        shutil.copy2(__file__, durable / "code/run_native_crt_wide_queue.py")
        raw = args.output_root / run_id
        raw.mkdir(parents=True, exist_ok=False)
        flags = ["--family", family, "--outer-guard", str(gout),
                 "--inner-guard", str(gin)]
        if negative:
            flags.append(negative)
        protocol = {
            "run_id": run_id, "status": "queued", "source_sha256": source_hash,
            "compiler": compiler, "workers": 1, "native_threads": 1,
            "build": "g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic <code/compiled_crt_native_wide.cpp> -o <ignored-work>/compiled_crt_native",
            "arguments": flags,
            "reproduction": "<ignored-work>/compiled_crt_native " + " ".join(flags) + " --output <ignored-work>/certificate.json",
            "scope": "Complete finite payload/address program; no fixed-tape timing or all-size native witness claim",
            "expected": "EXPECTED_NEGATIVE" if negative else "PASS",
            "source_inputs": "Exact scalar k+1 tags and explicit zero padding; prime family is pinned in authored C++",
            "raw_execution_path": str(raw),
        }
        write_json(durable / "protocol.json", protocol)
        prepared.append((durable, raw, protocol))
    process = Path("/proc") / str(args.pause_owned_pid) / "cmdline"
    command = process.read_bytes().replace(b"\x00", b" ").decode()
    assert "compiled_crt_pipeline_guard2.py" in command
    assert "fast-integration-cpu-20261008" in command
    assert "--family bank131" in command
    build = args.output_root / "builds"
    build.mkdir(parents=True, exist_ok=True)
    binary = build / "compiled_crt_native"
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    os.kill(args.pause_owned_pid, signal.SIGSTOP)
    try:
        subprocess.run(["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-Wpedantic",
                        str(source), "-o", str(binary)], check=True, env=env)
        assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
        for durable, raw, protocol in prepared:
            protocol["status"] = "running"
            protocol["start_unix_time"] = time.time()
            write_json(durable / "protocol.json", protocol)
            command = [str(binary)] + protocol["arguments"] + ["--output", str(raw / "certificate.json")]
            print(json.dumps({"run_id": protocol["run_id"], "status": "running", "command": command}), flush=True)
            with (raw / "stdout.log").open("w") as log:
                child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env)
                protocol["native_pid"] = child.pid
                write_json(durable / "protocol.json", protocol)
                code = child.wait()
            protocol["exit_code"] = code
            certificate = raw / "certificate.json"
            if certificate.exists():
                result = json.loads(certificate.read_text())
                shutil.copy2(certificate, durable / "results/certificate.json")
                protocol["status"] = result["status"]
                protocol["expected_matched"] = result["status"] == protocol["expected"]
                protocol["wall_seconds"] = result["wall_seconds"]
                protocol["certificate_sha256"] = hashlib.sha256(certificate.read_bytes()).hexdigest()
            else:
                protocol["status"] = "NO_CERTIFICATE"
            protocol["completed_unix_time"] = time.time()
            write_json(durable / "protocol.json", protocol)
            print(json.dumps({"run_id": protocol["run_id"], "status": protocol["status"], "exit_code": code}), flush=True)
    finally:
        if process.exists():
            current = process.read_bytes().replace(b"\x00", b" ").decode()
            if "compiled_crt_pipeline_guard2.py" in current and "--family bank131" in current:
                os.kill(args.pause_owned_pid, signal.SIGCONT)
                print(json.dumps({"resumed_owned_pid": args.pause_owned_pid}), flush=True)


if __name__ == "__main__":
    main()
