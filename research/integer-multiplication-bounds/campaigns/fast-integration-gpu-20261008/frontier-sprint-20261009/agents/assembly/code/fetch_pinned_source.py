#!/usr/bin/env python3
"""Recover only the allowlisted predecessor files through authenticated gh.

Apache-2.0. Prepared for RaD with OpenAI GPT-6.1 Sol assistance.
This makes read-only GitHub requests and never creates a fork or PR.
"""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import time


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pin", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    if not shutil.which("gh"):
        raise SystemExit("GitHub CLI is required and must already be authenticated")
    if args.output.exists():
        raise SystemExit("Refusing to replace an existing source export")
    if not 1 <= args.workers <= 4:
        raise SystemExit("Choose one to four download workers")
    pin = json.loads(args.pin.read_text())
    repo, revision = pin["source_repository"], pin["source_revision"]
    if len(repo.split("/")) != 2 or any(not p or not p.replace("-", "").replace("_", "").replace(".", "").isalnum() for p in repo.split("/")):
        raise SystemExit("Invalid pinned repository")
    if len(revision) != 40 or any(c not in "0123456789abcdef" for c in revision):
        raise SystemExit("Invalid pinned revision")
    items = sorted(pin["source_sha256"].items())
    for name, expected in items:
        p = PurePosixPath(name)
        if p.is_absolute() or ".." in p.parts or str(p) != name:
            raise SystemExit("Unsafe allowlist path")
        if len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
            raise SystemExit("Invalid expected SHA-256")
    args.output.mkdir(parents=True)

    def fetch(item):
        name, expected = item
        endpoint = "repos/"+repo+"/contents/"+name+"?ref="+revision
        for attempt in range(3):
            try:
                response = subprocess.run(["gh", "api", endpoint], check=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
                metadata = json.loads(response.stdout)
                if metadata.get("type") != "file" or metadata.get("encoding") != "base64":
                    raise ValueError("GitHub did not return an inline file: "+name)
                data = base64.b64decode(metadata["content"])
                if sha256(data).hexdigest() != expected:
                    raise ValueError("Pinned source SHA-256 mismatch: "+name)
                path = args.output/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                return name, len(data)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                if attempt == 2:
                    raise RuntimeError("GitHub read failed; partial export retained: "+name) from None
                time.sleep(attempt+1)

    print("Recovering pinned source "+revision+" ("+str(len(items))+" allowlisted files)", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(fetch, items))
    print("PASS pinned source hashes; "+str(sum(size for _, size in results))+" bytes", flush=True)


if __name__ == "__main__":
    main()
