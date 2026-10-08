#!/usr/bin/env python3
"""Run distinct certified Gaussian controls in one owned replacement slot."""
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
    source = agent / "code/dyadic_interval_gaussian.py"
    sources = [source,Path(__file__).resolve()]
    hashes = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    configs = [
        ("near127",127,128,2,128,"complete",True),
        ("drop-wrap127",127,128,2,128,"drop-wrap",False),
        ("low-precision127",127,128,2,128,"low-precision",False),
        ("narrow-band127",127,128,2,128,"narrow-band",False),
        ("near251",251,256,2,256,"complete",True),
        ("admissible257",257,264,8,384,"complete",True),
        ("admissible509",509,512,16,512,"complete",True),
        ("near1021",1021,1024,2,384,"complete",True),
    ]
    prepared = []
    for label,s,t,alpha,q,mode,expected in configs:
        run_id = args.run_prefix + "-interval-" + label
        durable,raw = agent/"runs"/run_id,args.output_root/run_id
        (durable/"code").mkdir(parents=True,exist_ok=False)
        (durable/"results").mkdir()
        raw.mkdir(parents=True,exist_ok=False)
        for path in sources:
            shutil.copy2(path,durable/"code"/path.name)
        flags = ["--source",str(s),"--target",str(t),"--alpha",str(alpha),
                 "--target-bits",str(q),"--mode",mode,"--seed","202610081735"]
        protocol = {"run_id":run_id,"status":"queued",
                    "queued_utc":datetime.now(timezone.utc).isoformat(),
                    "source_sha256":hashes,"arguments":flags,
                    "reproduction":"python3 code/dyadic_interval_gaussian.py " + " ".join(flags) + " --output <fresh-ignored-work>/certificate.json",
                    "dependencies":"Python3 standard library only",
                    "workers":1,"native_threads":1,
                    "input_generator":"Random sixteenth-grid RHS with fixed Python random.Random seed; untrusted Decimal proposal frozen as integer words",
                    "methodology":"Directed dyadic Machin/pi and exp Taylor enclosures; exact fixed-word residual; ALL-lifted-alias tail; strict row-DD inverse error bound",
                    "expected_certified":expected,
                    "negative_control":mode if mode!="complete" else None,
                    "raw_execution_path":str(raw)}
        save(durable/"protocol.json",protocol)
        prepared.append((durable,raw,protocol))
    process = Path("/proc")/str(args.pause_owned_pid)/"cmdline"
    def identified():
        if not process.exists():
            return False
        cmd=process.read_bytes().replace(b"\x00",b" ").decode()
        return "compiled_crt_pipeline_guard2.py --family bank131 " in cmd and "fast-integration-cpu-20261008" in cmd
    assert identified(),"live process does not match the owned worker"
    env=dict(os.environ,OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1",MKL_NUM_THREADS="1")
    os.kill(args.pause_owned_pid,signal.SIGSTOP)
    try:
        for durable,raw,protocol in prepared:
            assert hashlib.sha256(source.read_bytes()).hexdigest()==hashes[source.name]
            command=["python3","-u",str(source)]+protocol["arguments"]+["--output",str(raw/"certificate.json")]
            protocol.update(status="running",start_unix_time=time.time())
            with (raw/"stdout.log").open("w") as log:
                child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env=env)
                protocol["compute_pid"]=child.pid
                save(durable/"protocol.json",protocol)
                print(json.dumps({"run_id":protocol["run_id"],"pid":child.pid,"status":"running"}),flush=True)
                exit_code=child.wait()
            protocol["exit_code"]=exit_code
            certificate=raw/"certificate.json"
            if certificate.exists():
                result=json.loads(certificate.read_text())
                shutil.copy2(certificate,durable/"results/certificate.json")
                protocol.update(status=result["status"],
                                expected_matched=result["strict_error_below_2_to_minus_target"]==protocol["expected_certified"],
                                wall_seconds=result["wall_seconds"],
                                certificate_sha256=hashlib.sha256(certificate.read_bytes()).hexdigest())
            else:
                protocol["status"]="NO_CERTIFICATE"
            protocol["completed_unix_time"]=time.time()
            save(durable/"protocol.json",protocol)
            print(json.dumps({"run_id":protocol["run_id"],"status":protocol["status"],"exit_code":exit_code}),flush=True)
            assert exit_code==0 and protocol.get("expected_matched") is True,"certificate control did not match predeclared outcome"
        # Replay frozen proposed words for the first complete receipt.
        durable,raw,protocol=prepared[0]
        replay=raw/"replay-certificate.json"
        subprocess.run(["python3",str(source),"--verify-certificate",str(durable/"results/certificate.json"),
                        "--output",str(replay)],check=True,env=env)
        replay_result=json.loads(replay.read_text())
        assert replay_result["strict_error_below_2_to_minus_target"]
        shutil.copy2(replay,durable/"results/replay-certificate.json")
        protocol["replay_sha256"]=hashlib.sha256(replay.read_bytes()).hexdigest()
        protocol["replay_reproduction"]="python3 code/dyadic_interval_gaussian.py --verify-certificate results/certificate.json --output <fresh-ignored-work>/replay.json"
        save(durable/"protocol.json",protocol)
    finally:
        if identified():
            os.kill(args.pause_owned_pid,signal.SIGCONT)
            print(json.dumps({"resumed_owned_pid":args.pause_owned_pid}),flush=True)


if __name__=="__main__":
    main()
