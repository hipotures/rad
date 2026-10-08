#!/usr/bin/env python3
"""One-slot controls of high outer-U bank recycling inside exact inner shears.

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
    parser.add_argument("--resume-unstarted", action="store_true")
    parser.add_argument("--wait-owned-native-pid", type=int)
    args = parser.parse_args()
    agent = Path(__file__).resolve().parents[1]
    files = [agent / "code/compiled_reflection_four_recycle.cpp",
             agent / "code/compiled_crt_native_recycle.cpp", Path(__file__).resolve()]
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    compiler = subprocess.check_output(["g++", "--version"], text=True).splitlines()[0]
    configs = [
        ("two-target-smoke", "two-small", 2, 3, None, "PASS"),
        ("two-target-missing-inner", "two-small", 2, 3, "--omit-inner-repair", "EXPECTED_NEGATIVE"),
        ("two-target-source-bank", "two-small", 2, 3, "--borrow-left-control", "FAIL"),
        ("four-target-inner-G3", "mixed-small", 2, 3, None, "PASS"),
    ]
    prepared = []
    for label, family, gout, gin, negative, expected in configs:
        run_id = args.run_prefix + "-reflection-recycle-" + label
        durable = agent / "runs" / run_id
        if args.resume_unstarted and durable.exists():
            protocol = json.loads((durable / "protocol.json").read_text())
            if protocol["status"] != "queued":
                print(json.dumps({"run_id":run_id,"status":"retained_without_rerun",
                                  "original_status":protocol["status"]}),flush=True)
                continue
            for path in files[:2]:
                assert protocol["source_sha256"][path.name] == hashes[path.name]
                assert hashlib.sha256((durable / "code" / path.name).read_bytes()).hexdigest() == hashes[path.name]
            raw = Path(protocol["raw_execution_path"])
            assert raw.is_dir() and not (raw / "certificate.json").exists()
            resume_source = durable / "code/run_reflection_recycle_queue_resume.py"
            assert not resume_source.exists()
            shutil.copy2(__file__, resume_source)
            protocol["resume_controller_sha256"] = hashes[Path(__file__).name]
            protocol["resumed_utc"] = datetime.now(timezone.utc).isoformat()
            prepared.append((durable,raw,protocol))
            continue
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
            "build": "g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic <code/compiled_reflection_four_recycle.cpp> -o <ignored-work>/control",
            "reproduction": "<ignored-work>/control " + " ".join(flags) + " --output <ignored-work>/certificate.json",
            "scope": "Two or four independent target words; outer U high bits and T recycled by exact completed inner F_u; finite address validation only",
            "expected": expected,
            "expected_error_prefix": "nonbijective native map at " if negative == "--borrow-left-control" else None,
            "input_generator": "Tag physical address+1 exactly at all source=0/1, valid target digits, arbitrary original bank bits; explicit zero elsewhere",
            "independent_oracle": "Source BIT1 decrements every valid target digit, zero wraps to modulus-1; invalid digits fixed; source BIT0 fixes all targets",
            "source_dependency_contract": "All offsets read the same fixed BIT outside targets/bank; inner fanout reads ONLY outer U parity bits, which are excluded from inner scratch",
            "negative_contract": negative,
            "bank_recycling_contract": "Inner exact repair completes and restores ALL non-target bits before outer additions read U/T; no partial state is consumed",
            "raw_execution_path": str(raw),
        }
        write_json(durable / "protocol.json", protocol)
        prepared.append((durable, raw, protocol))
    if args.wait_owned_native_pid:
        native = Path("/proc") / str(args.wait_owned_native_pid) / "cmdline"
        while native.exists():
            try:
                current = native.read_bytes().replace(b"\x00", b" ").decode()
            except FileNotFoundError:
                break
            if not current:
                break
            assert "compiled_reflection_four" in current
            assert "fast-integration-cpu-20261008" in current
            assert "--inner-guard 2" in current and "--outer-guard 2" in current
            time.sleep(2)
        # The previous controller returns the Python slot in finally. Wait
        # for that completed handoff rather than overlap its native worker.
        status = Path("/proc") / str(args.pause_owned_pid) / "status"
        handoff_started = time.time()
        while status.exists() and "State:\tT" in status.read_text():
            assert time.time() - handoff_started < 30, "previous controller did not restore owned Python slot"
            time.sleep(0.1)
    process = Path("/proc") / str(args.pause_owned_pid) / "cmdline"
    command = process.read_bytes().replace(b"\x00", b" ").decode()
    assert "compiled_crt_pipeline_guard2.py" in command
    assert "fast-integration-cpu-20261008" in command and "--family bank131" in command
    build = args.output_root / "builds"
    build.mkdir(parents=True, exist_ok=True)
    binary = build / "compiled_reflection_recycle"
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
                if protocol.get("expected_error_prefix"):
                    protocol["expected_matched"] &= result["error"].startswith(protocol["expected_error_prefix"])
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
