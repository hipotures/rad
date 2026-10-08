#!/usr/bin/env python3
"""One lightweight public-source observation; never inspect RaD campaign branches.

Uses gh for public API reads, writes only this scout's owned campaign paths,
and reports changed metadata. Downloading an actionable source is a separate
decision so an unchanged observation cannot duplicate source snapshots.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


OWN = Path(__file__).resolve().parent
CAMPAIGN = OWN.parent.parent
WORK = CAMPAIGN / "work" / "scout"
WATCHED = {
    "CrocSwap/integer-mult-bounds": "main",
    "Swapnil-jain/integer-mult-kappa": "main",
    "platypii/integer-mult-bounds-lean": "master",
}


def api(path: str):
    raw = subprocess.check_output(["gh", "api", path], stderr=subprocess.PIPE)
    return json.loads(raw)


def observed_head(item):
    repository, branch = item
    data = api(f"repos/{repository}/commits/{branch}")
    return repository, {
        "branch": branch,
        "sha": data["sha"],
        "commit_utc": data["commit"]["committer"]["date"],
        "author": data["commit"]["author"]["name"],
        "title": data["commit"]["message"].splitlines()[0],
        "url": data["html_url"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--forks", action="store_true", help="also query linked fork branches")
    parser.add_argument("--search", action="store_true", help="refresh the broader repository search")
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rawdir = WORK / "observations" / stamp
    rawdir.mkdir(parents=True, exist_ok=False)
    pulls = api("repos/CrocSwap/integer-mult-bounds/pulls?state=all&per_page=100")
    (rawdir / "pulls.json").write_text(json.dumps(pulls, indent=2) + "\n")
    with ThreadPoolExecutor(max_workers=3) as pool:
        heads = dict(pool.map(observed_head, WATCHED.items()))
    compact = {
        "observed_utc": stamp,
        "heads": heads,
        "pull_requests": {
            str(p["number"]): {
                "title": p["title"], "author": p["user"]["login"],
                "state": p["state"], "draft": p["draft"],
                "created_utc": p["created_at"], "updated_utc": p["updated_at"],
                "head_sha": p["head"]["sha"], "head_ref": p["head"]["ref"],
                "head_repository": (p["head"]["repo"] or {}).get("full_name"),
                "url": p["html_url"],
                "body_sha256": hashlib.sha256((p["body"] or "").encode()).hexdigest(),
            } for p in pulls
        },
    }
    if args.forks:
        forks = api("repos/CrocSwap/integer-mult-bounds/forks?per_page=100&sort=newest")
        compact["forks"] = {}
        for fork in forks:
            name = fork["full_name"]
            if name.lower() == "hipotures/rad":
                raise RuntimeError("Independent RaD campaigns are not scout inputs")
            branches = api(f"repos/{name}/branches?per_page=100")
            compact["forks"][name] = {b["name"]: b["commit"]["sha"] for b in branches}
    if args.search:
        data = api("search/repositories?q=integer-mult+in:name&sort=updated&per_page=50")
        (rawdir / "search.json").write_text(json.dumps(data, indent=2) + "\n")
        compact["search"] = [
            {key: r.get(key) for key in ("full_name", "pushed_at", "default_branch", "html_url", "description")}
            for r in data["items"]
            if "bound" in r["full_name"].lower() or "kappa" in r["full_name"].lower()
        ]
    current = OWN / "latest-observation.json"
    old = json.loads(current.read_text()) if current.exists() else {}
    changes = []
    for key in ("heads", "pull_requests"):
        for name, value in compact[key].items():
            if value != old.get(key, {}).get(name):
                changes.append({"kind": key, "name": name, "previous": old.get(key, {}).get(name), "current": value})
    if args.forks:
        previous_forks = OWN / "latest-fork-observation.json"
        old_forks = json.loads(previous_forks.read_text())["forks"] if previous_forks.exists() else old.get("forks", {})
        for repository, branches in compact["forks"].items():
            for branch, sha in branches.items():
                before = old_forks.get(repository, {}).get(branch)
                if before != sha:
                    changes.append({"kind": "fork_branches", "name": repository + "/" + branch,
                                    "previous": before, "current": {"sha": sha, "title": branch}})
        previous_forks.write_text(json.dumps({"observed_utc": stamp, "forks": compact["forks"]}, indent=2) + "\n")
    result = {"observation": compact, "changes": changes}
    destination = OWN / "observations" / (stamp + ".json")
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n")
    current.write_text(json.dumps(compact, indent=2) + "\n")
    print(json.dumps({"observed_utc": stamp, "changes": [
        {"kind": c["kind"], "name": c["name"], "head_sha": c["current"].get("head_sha", c["current"].get("sha")), "title": c["current"].get("title")}
        for c in changes
    ], "record": str(destination.relative_to(CAMPAIGN))}, indent=2))


if __name__ == "__main__":
    main()
