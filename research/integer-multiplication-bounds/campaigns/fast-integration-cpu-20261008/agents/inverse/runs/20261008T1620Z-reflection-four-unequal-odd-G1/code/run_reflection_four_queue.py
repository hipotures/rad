#!/usr/bin/env python3
"""One-slot complete-cube controls of four simultaneous interval reflections.

The controller replaces only its positively identified owned Python job and
restores it in finally. All source snapshots and protocols are written before
compilation. Completed outputs are retained unchanged and copied durably.
"""
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


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pause-owned-pid", type=int, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--run-prefix", required=True)
    args = parser.parse_args()
    agent = Path(__file__).resolve().parents[1]
    files = [agent / "code/compiled_reflection_four.cpp",
             agent / "code/compiled_crt_native_wide.cpp", Path(__file__).resolve()]
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    compiler = subprocess.check_output(["g++", "--version"], text=True).splitlines()[0]
    configs = [
        ("mixed-G1", "mixed-small", 1, 1, None),
        ("source-bank-negative", "mixed-small", 1, 1, "--borrow-left-control"),
        ("mixed-inner-G2", "mixed-small", 1, 2, None),
        ("unequal-odd-G1", "odd-wide", 1, 1, None),
        ("mixed-inner-outer-G2", "mixed-small", 2, 2, None),
    ]
    prepared = []
    for label, family, gout, gin, negative in configs:
        run_id = args.run_prefix + "-reflection-four-" + label
        durable = agent / "runs" / run_id
        assert not durable.exists(), ("run already exists", durable)
        (durable / "code").mkdir(parents=True)
        (durable / "results").mkdir()
        for path in files:
            shutil.copy2(path, durable / "code" / path.name)
        raw = args.output_root / run_id
        raw.mkdir(parents=True, exist_ok=False)
        flags = ["--family", family, "--outer-guard", str(gout),
                 "--inner-guard", str(gin)]
        if negative:
            flags.append(negative)
        protocol = {
            "run_id": run_id, "status": "queued",
            "queued_utc": datetime.now(timezone.utc).isoformat(),
            "source_sha256": hashes, "compiler": compiler,
            "workers": 1, "native_threads": 1, "arguments": flags,
            "build": "g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic <code/compiled_reflection_four.cpp> -o <ignored-work>/control",
            "reproduction": "<ignored-work>/control " + " ".join(flags) + " --output <ignored-work>/certificate.json",
            "scope": "Four independent simultaneous target words, fixed repeated source BIT and original dirty bank; finite address validation only",
            "expected": "EXPECTED_NEGATIVE" if negative else "PASS",
            "input_generator": "Tag physical address+1 exactly at all source=0/1, valid target digits, arbitrary original bank bits; explicit zero elsewhere",
            "independent_oracle": "Source BIT1 decrements every valid target digit, zero wraps to modulus-1; invalid digits fixed; source BIT0 fixes all targets",
            "source_dependency_contract": "All four offsets read the SAME fixed source bit outside target words and legal dirty bank",
            "negative_contract": "The negative deliberately borrows that fixed source bit as U[0], violating endpoint-control exclusion" if negative else None,
            "raw_execution_path": str(raw),
        }
        write_json(durable / "protocol.json", protocol)
        prepared.append((durable, raw, protocol))
    process = Path("/proc") / str(args.pause_owned_pid) / "cmdline"
    command = process.read_bytes().replace(b"\x00", b" ").decode()
    assert "compiled_crt_pipeline_guard2.py" in command
    assert "fast-integration-cpu-20261008" in command and "--family bank131" in command
    build = args.output_root / "builds"
    build.mkdir(parents=True, exist_ok=True)
    binary = build / "compiled_reflection_four"
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
               MKL_NUM_THREADS="1")
    os.kill(args.pause_owned_pid, signal.SIGSTOP)
    try:
        subprocess.run(["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-Wpedantic",
                        str(files[0]), "-o", str(binary)], check=True, env=env)
        for path in files:
            assert hashlib.sha256(path.read_bytes()).hexdigest() == hashes[path.name]
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
                exit_code = child.wait()
            protocol["exit_code"] = exit_code
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
            print(json.dumps({"run_id": protocol["run_id"], "status": protocol["status"], "exit_code": exit_code}), flush=True)
            if protocol.get("expected_matched") is not True:
                raise RuntimeError("New control did not match its predeclared outcome: " + protocol["run_id"])
    finally:
        if process.exists():
            current = process.read_bytes().replace(b"\x00", b" ").decode()
            if "compiled_crt_pipeline_guard2.py" in current and "--family bank131" in current:
                os.kill(args.pause_owned_pid, signal.SIGCONT)
                print(json.dumps({"resumed_owned_pid": args.pause_owned_pid}), flush=True)


if __name__ == "__main__":
    main()
