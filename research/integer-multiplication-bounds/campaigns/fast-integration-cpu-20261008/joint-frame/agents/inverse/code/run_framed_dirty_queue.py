#!/usr/bin/env python3
"""Freeze and run three distinct physical joint-frame controls on one CPU."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def main():
    agent = Path(__file__).resolve().parent.parent
    campaign = agent.parents[2]
    work = campaign / "work/joint-frame/inverse"
    source = agent / "code/framed_dirty_cube.py"
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
               MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    for prime, basis in ((5, True), (7, False), (11, False)):
        run_id = utc()+"-framed-dirty-q"+str(prime)+("-basis" if basis else "-words")
        durable = agent / "runs" / run_id
        raw = work / run_id
        (durable / "code").mkdir(parents=True)
        (durable / "results").mkdir()
        raw.mkdir(parents=True)
        frozen = durable / "code/framed_dirty_cube.py"
        shutil.copy2(source, frozen)
        command = [sys.executable, "-u", str(frozen), "--prime", str(prime),
                   "--output", str(raw / "result.json")]
        if basis:
            command.append("--full-basis")
        protocol = {"run_id": run_id, "question": "Does the four-mixer dirty word equal the required complete physical array map after the explicit frame schedule?",
                    "source_sha256": digest, "prime": prime,
                    "all_basis_columns": basis, "command": command,
                    "workers": 1, "native_threads": 1,
                    "state": "running", "started_utc": utc(),
                    "raw_result": str((raw / "result.json").relative_to(campaign))}
        with (raw / "stdout.log").open("w") as log:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env)
            protocol["pid"] = process.pid
            (durable / "protocol.json").write_text(json.dumps(protocol, indent=2)+"\n")
            print(json.dumps({"run_id": run_id, "pid": process.pid, "command": command}), flush=True)
            returncode = process.wait()
        protocol.update(state="complete" if returncode == 0 else "failed",
                        returncode=returncode, finished_utc=utc())
        (durable / "protocol.json").write_text(json.dumps(protocol, indent=2)+"\n")
        if (raw / "result.json").is_file():
            shutil.copy2(raw / "result.json", durable / "results/result.json")
            print((raw / "result.json").read_text(), flush=True)
        if returncode:
            print((raw / "stdout.log").read_text(), flush=True)
            raise SystemExit(returncode)


if __name__ == "__main__":
    main()
