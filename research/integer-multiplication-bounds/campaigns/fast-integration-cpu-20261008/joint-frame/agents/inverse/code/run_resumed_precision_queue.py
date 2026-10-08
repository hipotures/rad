#!/usr/bin/env python3
"""One-slot long-precision Gaussian residual queue with immutable inputs."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

def save(path, obj):
    path.write_text(json.dumps(obj, indent=2) + "\n")

def main():
    agent = Path(__file__).resolve().parents[1]
    campaign = agent.parents[2]
    source = agent / "code/dyadic_interval_lower.py"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    cases = [(32, 2048, "complete"), (64, 4096, "complete"),
             (128, 8192, "complete"), (256, 16384, "complete"),
             (128, 8192, "low-precision")]
    for alpha, bits, mode in cases:
        run_id = f"{stamp}-resume-s65521-a{alpha}-q{bits}-{mode}"
        durable = agent / "runs" / run_id
        raw = campaign / "work/joint-frame/inverse" / run_id
        (durable / "code").mkdir(parents=True, exist_ok=False)
        (durable / "results").mkdir()
        raw.mkdir(parents=True, exist_ok=False)
        for authored in (source, Path(__file__).resolve()):
            shutil.copy2(authored, durable / "code" / authored.name)
        flags = ["--source", "65521", "--target", "65536", "--alpha", str(alpha), "--target-bits", str(bits), "--mode", mode, "--seed", "202610081925"]
        command = ["python3", "-B", "-u", str(durable / "code" / source.name)] + flags + ["--output", str(raw / "certificate.json")]
        protocol = {"run_id": run_id, "question": "Precision and Gaussian scale growth at a fixed nontrivial cyclic phase family; frozen dyadic residual certifies all aliases independently of Decimal proposal", "status": "running", "source_sha256": digest, "arguments": flags, "workers": 1, "native_threads": 1, "expected_status": "RIGOROUS_TARGET_CERTIFIED" if mode == "complete" else "RIGOROUS_TARGET_DISPROVED", "raw_path": str(raw), "start_utc": datetime.now(timezone.utc).isoformat()}
        with (raw / "stdout.log").open("w") as stream:
            child = subprocess.Popen(command, env=env, stdout=stream, stderr=subprocess.STDOUT)
            protocol["compute_pid"] = child.pid
            save(durable / "protocol.json", protocol)
            print(json.dumps({"compute_pid": child.pid, "command": command}), flush=True)
            code = child.wait()
        protocol["exit_code"] = code
        certificate = raw / "certificate.json"
        if certificate.exists():
            result = json.loads(certificate.read_text())
            omitted = ["rhs_sixteenth_words", "proposed_dyadic_solution_words"]
            compact = {k: v for k, v in result.items() if k not in omitted}
            compact.update(full_certificate_sha256=hashlib.sha256(certificate.read_bytes()).hexdigest(), full_certificate_raw_path=str(certificate), omitted_arrays=omitted, archive_status="pending official pack-text after completion")
            save(durable / "results/compact-certificate.json", compact)
            protocol.update(status=result["status"], expected_matched=result["status"] == protocol["expected_status"], wall_seconds=result["wall_seconds"])
        else:
            protocol["status"] = "NO_CERTIFICATE"
        protocol["end_utc"] = datetime.now(timezone.utc).isoformat()
        save(durable / "protocol.json", protocol)
        print(json.dumps({"run_id": run_id, "status": protocol["status"], "exit_code": code}), flush=True)
        if code or protocol.get("expected_matched") is not True:
            raise RuntimeError("Preserve unexpected outcome and pause queue: " + run_id)

if __name__ == "__main__":
    main()
