#!/usr/bin/env python3
"""Snapshot GitHub check-run conclusions for selected upstream PR heads.

Usage: fetch_upstream_check_runs.py PULLS_JSON NUMBERS_FILE OUT_JSON

PULLS_JSON is the frozen ``gh api --paginate .../pulls?state=all`` snapshot;
NUMBERS_FILE lists PR numbers (one per line). Each head SHA is queried once
with ``gh api repos/CrocSwap/integer-mult-bounds/commits/<sha>/check-runs``.
The output maps head SHA -> {"summary", "runs"}; failures are recorded, not
skipped, because a missing head (force-pushed or deleted fork) is evidence.
"""
import collections
import json
import subprocess
import sys

REPO = "CrocSwap/integer-mult-bounds"


def main():
    pulls_path, numbers_path, out_path = sys.argv[1:4]
    pulls = {p["number"]: p for p in json.load(open(pulls_path))}
    numbers = [int(line) for line in open(numbers_path) if line.strip()]
    result = {}
    for number in numbers:
        sha = pulls[number]["head"]["sha"]
        if sha in result:
            continue
        proc = subprocess.run(
            ["gh", "api", f"repos/{REPO}/commits/{sha}/check-runs?per_page=100"],
            capture_output=True, text=True)
        if proc.returncode != 0:
            result[sha] = {"summary": "unavailable", "error": proc.stderr.strip()[:300], "runs": []}
            continue
        runs = [{"name": r["name"], "status": r["status"], "conclusion": r["conclusion"],
                 "completed_at": r["completed_at"]}
                for r in json.loads(proc.stdout)["check_runs"]]
        counts = collections.Counter(r["conclusion"] or r["status"] for r in runs)
        if not runs:
            summary = "none"
        elif counts.get("failure") or counts.get("timed_out") or counts.get("cancelled"):
            summary = "failure"
        elif set(counts) <= {"success", "skipped", "neutral"}:
            summary = "success"
        else:
            summary = "pending"
        result[sha] = {"summary": summary,
                       "counts": dict(sorted(counts.items())), "runs": runs}
    with open(out_path, "w") as handle:
        json.dump(result, handle, indent=1, sort_keys=True)
    print(collections.Counter(v["summary"] for v in result.values()))


if __name__ == "__main__":
    main()
