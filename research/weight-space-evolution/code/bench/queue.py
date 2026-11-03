"""Run a list of benchmark jobs over the GPUs, one engine per GPU at a time (no VRAM sharing between jobs).

    python -m bench.queue <jobs.json> --campaign <id> [--gpus <uuid0>,<uuid1>]

jobs.json: [{"name": ..., "engine": {...}, "workloads": "A,B", "args": [...], "env": {...}, "model": "<work-relative
dir>", "gpu": 0|1|null, "cache": "<work-relative vLLM cache dir>"}, ...]. A job whose <name>.meta.json already exists
is skipped (results are never overwritten; a repair gets a new name). Jobs pinned to a GPU run only there.
"""
import argparse
import json
import os
import subprocess
import threading
import time
from pathlib import Path

TOPIC = Path(__file__).resolve().parents[2]
W = Path(os.environ.get("WSE_WORK_ROOT", TOPIC / "work"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("jobs")
    ap.add_argument("--campaign", required=True)
    ap.add_argument("--gpus", default="GPU-6c849b47-7111-9265-9d42-ff8eddc05a2d,GPU-81ac6e96-0bfe-390d-beb1-241466569d6b")
    a = ap.parse_args(argv)
    gpus = a.gpus.split(",")
    jobs = json.load(open(a.jobs))
    raw = W / "raw" / a.campaign
    pending = [j for j in jobs if not (raw / f"{j['name']}.meta.json").exists()]
    lock = threading.Lock()
    log = open(W / "logs" / f"{a.campaign}.queue.log", "a")

    def take(gi):
        with lock:
            for j in pending:
                if j.get("gpu") in (None, gi):
                    pending.remove(j)
                    return j
        return None

    def worker(gi):
        while True:
            j = take(gi)
            if j is None:
                return
            env = dict(os.environ, GPU=gpus[gi], CAMPAIGN=a.campaign, **{k: str(v).replace("${WORK}", str(W)) for k, v in j.get("env", {}).items()})
            if j.get("model"):
                env["MODEL"] = str(W / j["model"])
            if j.get("cache"):
                env["CACHE"] = str(W / j["cache"])
            t = time.time()
            r = subprocess.run([str(TOPIC / "code/bench/run_one.sh"), j["name"], json.dumps(j.get("engine", {})),
                                j.get("workloads", "A,B,D,E"), *j.get("args", [])], env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            with lock:
                msg = f"{time.strftime('%H:%M:%S')} gpu{gi} {j['name']} rc={r.returncode} {time.time() - t:.0f}s"
                print(msg, flush=True)
                log.write(msg + "\n")
                log.flush()

    th = [threading.Thread(target=worker, args=(i,)) for i in range(len(gpus))]
    for t in th:
        t.start()
    for t in th:
        t.join()


if __name__ == "__main__":
    main()
