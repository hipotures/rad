#!/usr/bin/env python3
"""One replacement CPU slot, three distinct all-address mapping diagnostics."""
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
    sources = [agent / "code/compiled_reflection_alltag_probe.cpp",
               agent / "code/compiled_crt_native_recycle.cpp", Path(__file__).resolve()]
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    compiler = subprocess.check_output(["g++", "--version"], text=True).splitlines()[0]
    prepared = []
    for mode in ("completed", "omit-inner", "raw-fanout"):
        run_id = args.run_prefix + "-alltag-" + mode
        durable = agent / "runs" / run_id
        raw = args.output_root / run_id
        (durable / "code").mkdir(parents=True, exist_ok=False)
        (durable / "results").mkdir()
        raw.mkdir(parents=True, exist_ok=False)
        for source in sources:
            shutil.copy2(source, durable / "code" / source.name)
        protocol = {"run_id": run_id, "status": "queued",
                    "queued_utc": datetime.now(timezone.utc).isoformat(),
                    "source_sha256": hashes, "compiler": compiler,
                    "build": "g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic code/compiled_reflection_alltag_probe.cpp -o <ignored-work>/control",
                    "reproduction": "<ignored-work>/control --mode " + mode + " --output <fresh-ignored-work>/certificate.json",
                    "workers": 1, "native_threads": 1,
                    "input_generator": "Tag EVERY physical address a with a+1, including all invalid target slots and original dirty-bank patterns",
                    "scope": "Exploratory all-address distinction between exact outer containment and wrong permutations hidden by equal padding zeros",
                    "predeclared_measurements": ["wrong valid/invalid destinations", "complete literal reverse", "raw standalone fanout wrong records"],
                    "expected_outcome": "exploratory; no forced negative classifier",
                    "raw_execution_path": str(raw)}
        save(durable / "protocol.json", protocol)
        prepared.append((mode,durable,raw,protocol))
    process = Path("/proc") / str(args.pause_owned_pid) / "cmdline"
    def identified():
        if not process.exists():
            return False
        command = process.read_bytes().replace(b"\x00",b" ").decode()
        return ("/code/compiled_crt_pipeline.py --family six " in command
                and "fast-integration-cpu-20261008" in command)
    assert identified(), "live process does not match the owned worker"
    build = args.output_root / "builds"
    build.mkdir(parents=True, exist_ok=True)
    binary = build / "compiled_reflection_alltag"
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1",MKL_NUM_THREADS="1")
    os.kill(args.pause_owned_pid,signal.SIGSTOP)
    try:
        subprocess.run(["g++","-std=c++17","-O2","-Wall","-Wextra","-Wpedantic",
                        str(sources[0]),"-o",str(binary)],check=True,env=env)
        for source in sources:
            assert hashlib.sha256(source.read_bytes()).hexdigest() == hashes[source.name]
        for mode,durable,raw,protocol in prepared:
            protocol.update(status="running",start_unix_time=time.time())
            command = [str(binary),"--mode",mode,"--output",str(raw/"certificate.json")]
            with (raw/"stdout.log").open("w") as log:
                child = subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env=env)
                protocol["native_pid"] = child.pid
                save(durable/"protocol.json",protocol)
                print(json.dumps({"run_id":protocol["run_id"],"pid":child.pid,"status":"running"}),flush=True)
                exit_code = child.wait()
            assert exit_code == 0, "exploratory diagnostic failed before completion"
            certificate = raw/"certificate.json"
            result = json.loads(certificate.read_text())
            shutil.copy2(certificate,durable/"results/certificate.json")
            protocol.update(status=result["status"],exit_code=exit_code,
                            completed_unix_time=time.time(),
                            certificate_sha256=hashlib.sha256(certificate.read_bytes()).hexdigest())
            save(durable/"protocol.json",protocol)
            print(json.dumps({"run_id":protocol["run_id"],"wrong":result["wrong_payload_records"],"status":result["status"]}),flush=True)
    finally:
        if identified():
            os.kill(args.pause_owned_pid,signal.SIGCONT)
            print(json.dumps({"resumed_owned_pid":args.pause_owned_pid}),flush=True)


if __name__ == "__main__":
    main()
