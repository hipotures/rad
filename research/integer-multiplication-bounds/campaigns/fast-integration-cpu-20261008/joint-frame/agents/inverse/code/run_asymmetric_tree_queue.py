#!/usr/bin/env python3
"""Asymmetric six-prime full-CRT guard and reversed-order controls, one native slot."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import time

def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")

def main():
    agent = Path(__file__).resolve().parents[1]
    campaign = agent.parents[2]
    old = agent / "code"
    names = ["compiled_crt_native_asymmetric.cpp"]
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    # Observe only this currently verified owned native lane before refill.
    proc = Path('/proc/331439/cmdline')
    while proc.exists():
        try: current=proc.read_bytes().replace(b'\0',b' ').decode()
        except FileNotFoundError: break
        if '20261008T194605Z-tree-inner2outer2-bank-outer1-inner2-complete/control' not in current: break
        time.sleep(1)
    for family, outer, inner, omission, expected in [("asymmetric-six-bank", 2, 1, None, "PASS"), ("asymmetric-six-bank-reversed", 2, 1, None, "PASS")]:
        run_id = f"{stamp}-tree-{family}-outer{outer}-inner{inner}-" + ("complete" if omission is None else "omit-outer")
        durable = agent / "runs" / run_id
        raw = campaign / "work/joint-frame/inverse" / run_id
        (durable / "code").mkdir(parents=True, exist_ok=False)
        (durable / "results").mkdir()
        raw.mkdir(parents=True, exist_ok=False)
        for name in names:
            shutil.copy2(old / name, durable / "code" / name)
        shutil.copy2(__file__, durable / "code" / Path(__file__).name)
        compiler = ["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-Wpedantic", str(durable / "code" / names[0]), "-o", str(raw / "control")]
        flags = ["--family", family, "--outer-guard", str(outer), "--inner-guard", str(inner)]
        if omission:
            flags.append(omission)
        protocol = {"run_id": run_id, "question": "Complete multilevel normalized CRT, nested exact guards and restored original bank fields; independent leaf oracle and reverse on every padded record", "status": "building", "source_sha256": {name: hashlib.sha256((durable / "code" / name).read_bytes()).hexdigest() for name in names}, "compiler_command": compiler, "arguments": flags, "expected_status": expected, "workers": 1, "native_threads": 1, "raw_path": str(raw), "start_utc": datetime.now(timezone.utc).isoformat()}
        save(durable / "protocol.json", protocol)
        subprocess.run(compiler, check=True, env=env)
        command = [str(raw / "control")] + flags + ["--output", str(raw / "certificate.json")]
        with (raw / "stdout.log").open("w") as stream:
            child = subprocess.Popen(command, env=env, stdout=stream, stderr=subprocess.STDOUT)
            protocol.update(status="running", compute_pid=child.pid)
            save(durable / "protocol.json", protocol)
            print(json.dumps({"compute_pid": child.pid, "command": command}), flush=True)
            code = child.wait()
        protocol["exit_code"] = code
        if (raw / "certificate.json").exists():
            result = json.loads((raw / "certificate.json").read_text())
            shutil.copy2(raw / "certificate.json", durable / "results/certificate.json")
            protocol.update(status=result["status"], expected_matched=result["status"] == expected, wall_seconds=result["wall_seconds"], certificate_sha256=hashlib.sha256((raw / "certificate.json").read_bytes()).hexdigest())
        else:
            protocol["status"] = "NO_CERTIFICATE"
        protocol["end_utc"] = datetime.now(timezone.utc).isoformat()
        save(durable / "protocol.json", protocol)
        print(json.dumps({"run_id": run_id, "status": protocol["status"], "exit_code": code}), flush=True)
        if protocol.get("expected_matched") is not True:
            raise RuntimeError("Preserve unexpected outcome and pause queue: " + run_id)

if __name__ == "__main__":
    main()
