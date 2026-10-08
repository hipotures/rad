#!/usr/bin/env python3
"""Bounded live-campaign API poll cadence; no compute workers or Git writes."""
import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-root", required=True)
    parser.add_argument("--until", help="Optional UTC stopping time; omit only for an authorized indefinite extension")
    parser.add_argument("--interval", type=int, default=600)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    deadline = dt.datetime.fromisoformat(args.until.replace("Z", "+00:00")) if args.until else None
    prior_path = sorted((here/"polls").glob("*.json"))[-1]
    prior = json.loads(prior_path.read_text())
    due = max(time.time(), dt.datetime.fromisoformat(prior["observed_utc"].replace("Z", "+00:00")).timestamp() + args.interval)
    queries = ["integer-mult-bounds fork:true", "integer multiplication kappa",
               '"Gaussian resampling"', "integer-mult-kappa"]
    query_index = 0
    while deadline is None or dt.datetime.now(dt.timezone.utc) < deadline:
        time.sleep(min(max(0, due-time.time()), 60))
        if time.time() < due:
            continue
        if deadline is not None and dt.datetime.now(dt.timezone.utc) >= deadline:
            break
        result = subprocess.run(
            [sys.executable, str(here/"scout_poll.py"), "--work-root", args.work_root,
             "--search", queries[query_index % len(queries)]],
            text=True, capture_output=True, check=False,
        )
        query_index += 1
        due += args.interval
        if result.returncode:
            print(json.dumps({"poll_error": result.stderr.strip()}), flush=True)
            continue
        receipt = json.loads(result.stdout)
        current = json.loads(Path(receipt["poll"]).read_text())
        old_pulls = {x["number"]: x for x in prior["pulls"]}
        changed = [x for x in current["pulls"]
                   if old_pulls.get(x["number"]) != x]
        old_forks = {x["repository"]: x for x in prior.get("fork_heads", [])}
        changed_forks = [x for x in current.get("fork_heads", [])
                         if old_forks.get(x["repository"]) != x]
        print(json.dumps({"observed_utc": current["observed_utc"],
                          "poll": receipt["poll"], "changed_pulls": changed,
                          "changed_forks": changed_forks,
                          "repositories": current["repositories"]}), flush=True)
        prior = current
    print("Scout watcher completed at campaign closing phase", flush=True)


if __name__ == "__main__":
    main()
