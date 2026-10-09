#!/usr/bin/env python3
"""Recover exactly the 75 public predecessor files of the unified review.

Read-only GitHub CLI contents requests; no fork, branch, comment or PR writes.
Apache-2.0; prepared for RaD with OpenAI GPT-6.1 Sol assistance.
Finite changed inputs are restored separately from their lane archives.
"""

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import quote

SOURCES = {
    "PR163": ("chafreaky/integer-mult-bounds", "15c702a929b7d640107a95e196186ad74e876c82"),
    "PR161": ("eumemic/integer-mult-bounds", "d14e29157bc905be1ced0776dd893d0714013f3a"),
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    need(not sys.flags.optimize, "Assertion-disabled Python is unsupported")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    need(1 <= args.workers <= 4, "Use one through four read workers")
    need(not args.output.exists(), "Recovery output must be fresh")
    config = json.loads(args.config.read_text())
    need(len(config["sources"]) == 75, "Frozen 75-source inventory required")
    jobs = []
    seen = set()
    for identity, pin in config["sources"].items():
        relative = Path(pin["path"])
        need(not relative.is_absolute() and ".." not in relative.parts
             and str(relative) not in seen, "Unsafe or duplicate recovery path")
        seen.add(str(relative))
        tag, name = ("PR163", identity[6:]) if identity.startswith("PR163/") else ("PR161", identity)
        namepath = Path(name)
        need(not namepath.is_absolute() and ".." not in namepath.parts, "Unsafe predecessor path")
        repo, revision = SOURCES[tag]
        endpoint = "repos/"+repo+"/contents/"+quote(name,safe="/")+"?ref="+revision
        jobs.append((identity, pin, relative, repo, revision, endpoint))
    args.output.mkdir(parents=True)

    def fetch(job):
        identity, pin, relative, repo, revision, endpoint = job
        result = subprocess.run(["gh", "api", endpoint],
                                capture_output=True, timeout=60, check=True)
        metadata = json.loads(result.stdout)
        need(metadata.get("type") == "file", "Expected predecessor file: " + identity)
        if metadata.get("encoding") != "base64":
            # Large contents responses omit inline content. The Git blob API
            # still returns the exact bytes and avoids gh's raw gzip transform.
            blob = "repos/"+repo+"/git/blobs/"+metadata["sha"]
            result = subprocess.run(["gh", "api", blob],capture_output=True,timeout=60,check=True)
            metadata = json.loads(result.stdout)
        need(metadata.get("encoding") == "base64", "Expected inline base64 bytes: " + identity)
        data = base64.b64decode("".join(metadata["content"].split()),validate=True)
        need(sha256(data).hexdigest() == pin["sha256"], "Recovered hash mismatch: " + identity)
        path = args.output/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            handle.write(data)
        return identity, dict(path=str(relative), bytes=len(data), sha256=pin["sha256"],
            repository=repo, revision=revision, source_path=endpoint.split("/contents/",1)[1].split("?ref=",1)[0])

    recovered = {}
    print("Recovering 75 hash-pinned public sources with " + str(args.workers) + " read workers", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(fetch, job) for job in jobs]):
            identity, receipt = future.result()
            recovered[identity] = receipt
            if len(recovered)%15 == 0:
                print("Validated " + str(len(recovered)) + "/75 sources", flush=True)
    manifest = dict(status="PASS", sources=recovered, file_count=len(recovered),
        total_bytes=sum(pin["bytes"] for pin in recovered.values()), workers=args.workers,
        config_sha256=sha256(args.config.read_bytes()).hexdigest(),
        own_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        scope="Public predecessor source recovery only; seven finite input pins require intact lane archives or recorded deterministic regeneration")
    (args.output/"review-source-recovery.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print("PASS 75 source hashes; " + str(manifest["total_bytes"]) + " bytes", flush=True)


if __name__ == "__main__":
    main()
