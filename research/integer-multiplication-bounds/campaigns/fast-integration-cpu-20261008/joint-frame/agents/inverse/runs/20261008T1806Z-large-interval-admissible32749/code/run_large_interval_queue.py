#!/usr/bin/env python3
"""Large all-alias integer certificates, one lane, full words in raw storage."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


def save(path, value):
    path.write_text(json.dumps(value, indent=2)+"\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--run-prefix", required=True)
    args = parser.parse_args()
    agent = Path(__file__).resolve().parents[1]
    source = agent / "code/dyadic_interval_lower.py"
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    configs = [("near65521", 65521, 65536, 2, 384),
               ("admissible32749", 32749, 32768, 64, 512),
               ("long-word4093", 4093, 4096, 256, 2048)]
    for label, s, t, alpha, q in configs:
        run_id = args.run_prefix+"-large-interval-"+label
        durable, raw = agent/"runs"/run_id, args.work_root/run_id
        (durable/"code").mkdir(parents=True, exist_ok=False)
        (durable/"results").mkdir()
        raw.mkdir(parents=True, exist_ok=False)
        for path in (source, Path(__file__).resolve()):
            shutil.copy2(path, durable/"code"/path.name)
        flags = ["--source", str(s), "--target", str(t), "--alpha", str(alpha),
                 "--target-bits", str(q), "--seed", "202610081806"]
        command = ["python3", "-u", str(source)]+flags+["--output", str(raw/"certificate.json")]
        protocol = {"run_id": run_id, "status": "running", "source_sha256": digest,
                    "controller_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    "arguments": flags, "expected_status": "RIGOROUS_TARGET_CERTIFIED",
                    "start_utc": datetime.now(timezone.utc).isoformat(), "workers": 1, "native_threads": 1,
                    "reproduction": "python3 code/dyadic_interval_lower.py "+" ".join(flags)+" --output <fresh-ignored-work>/certificate.json",
                    "full_frozen_words": str(raw/"certificate.json"), "full_receipt_role": "Archive complete after run; compact readable receipt omits only input/solution arrays"}
        with (raw/"stdout.log").open("w") as stream:
            child = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT, env=env)
            protocol["compute_pid"] = child.pid
            save(durable/"protocol.json", protocol)
            print(json.dumps({"run_id": run_id, "compute_pid": child.pid}), flush=True)
            exit_code = child.wait()
        protocol["exit_code"] = exit_code
        if (raw/"certificate.json").exists():
            result = json.loads((raw/"certificate.json").read_text())
            full_hash = hashlib.sha256((raw/"certificate.json").read_bytes()).hexdigest()
            compact = {k: v for k, v in result.items() if k not in ("rhs_sixteenth_words", "proposed_dyadic_solution_words")}
            compact.update(full_certificate_sha256=full_hash, full_certificate_raw_path=str(raw/"certificate.json"),
                           omitted_arrays=["rhs_sixteenth_words", "proposed_dyadic_solution_words"], complete_arrays_archive_status="pending official pack-text after completion")
            save(durable/"results/compact-certificate.json", compact)
            protocol.update(status=result["status"], full_certificate_sha256=full_hash,
                            full_certificate_bytes=(raw/"certificate.json").stat().st_size, wall_seconds=result["wall_seconds"])
        else:
            protocol["status"] = "NO_CERTIFICATE"
        protocol["completed_utc"] = datetime.now(timezone.utc).isoformat()
        save(durable/"protocol.json", protocol)
        print(json.dumps({"run_id": run_id, "status": protocol["status"], "exit_code": exit_code}), flush=True)
        assert exit_code == 0 and protocol["status"] == protocol["expected_status"], "preserve unexpected outcome and stop queue"
        assert hashlib.sha256(source.read_bytes()).hexdigest() == digest


if __name__ == "__main__":
    main()
