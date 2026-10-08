#!/usr/bin/env python3
"""Read-only public GitHub scouting; keep compact polls and external raw reads."""
import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
from urllib.parse import quote

HISTORICAL_RAD_SHA = "4f8d6c8272b5ff307a0da51df545ec3cd96a8b6e"


def allowed_pull(pull):
    """Keep completed public RaD history; exclude every mutable RaD PR."""
    repo = (pull.get("head", {}).get("repo") or {}).get("full_name")
    author = pull.get("user", {}).get("login")
    if author == "hipotures" or repo == "hipotures/integer-mult-bounds":
        return pull.get("number") == 20 and pull.get("head", {}).get("sha") == HISTORICAL_RAD_SHA
    return True


def get(endpoint):
    result = subprocess.run(
        ["gh", "api", endpoint], text=True, capture_output=True, check=False
    )
    if result.returncode:
        return {"error": result.stderr.strip(), "endpoint": endpoint}
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--search", default="integer multiplication kappa")
    args = parser.parse_args()
    observed = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    stamp = observed.replace("-", "").replace(":", "")
    output = Path(__file__).resolve().parent / "polls" / (stamp + ".json")
    output.parent.mkdir(parents=True, exist_ok=True)
    raw_dir = args.work_root / "raw" / "scout" / stamp
    raw_dir.mkdir(parents=True, exist_ok=True)
    pulls = get("repos/CrocSwap/integer-mult-bounds/pulls?state=all&per_page=100")
    if isinstance(pulls, list):
        # Do not interpret, persist, or print new RaD submission content.
        pulls = [pull for pull in pulls if allowed_pull(pull)]
    repo_ids = ["CrocSwap/integer-mult-bounds", "Swapnil-jain/integer-mult-kappa"]
    repos = {}
    for repo in repo_ids:
        info = get("repos/" + repo)
        head = get("repos/" + repo + "/commits/" + info.get("default_branch", "main"))
        repos[repo] = {
            "url": info.get("html_url"), "description": info.get("description"),
            "pushed_at": info.get("pushed_at"), "head_sha": head.get("sha"),
            "head_date": head.get("commit", {}).get("committer", {}).get("date"),
            "head_message": head.get("commit", {}).get("message"),
            "license": (info.get("license") or {}).get("spdx_id"),
        }
    forks = get("repos/CrocSwap/integer-mult-bounds/forks?sort=newest&per_page=100")
    fork_heads = []
    if isinstance(forks, list):
        for fork in forks:
            # Consume only the completed public RaD source. Mutable RaD fork
            # branches could belong to the independent campaign and are excluded.
            if fork["full_name"] == "hipotures/integer-mult-bounds":
                fork_heads.append({
                    "repository": fork["full_name"], "url": fork["html_url"],
                    "branches": [{"name": "rad-source-framed-2pow20",
                                  "head_sha": HISTORICAL_RAD_SHA}],
                    "scope": "Completed published source only; mutable RaD branches excluded",
                })
                continue
            branches = get("repos/" + fork["full_name"] + "/branches?per_page=100")
            fork_heads.append({
                "repository": fork["full_name"], "url": fork["html_url"],
                "pushed_at": fork["pushed_at"],
                "branches": [{"name": x["name"], "head_sha": x["commit"]["sha"]}
                             for x in branches] if isinstance(branches, list) else branches,
            })
    query = "search/repositories?q=" + quote(args.search) + "&per_page=20"
    search = get(query)
    code_query = '"partial-swap" "integer"'
    code_search = get("search/code?q=" + quote(code_query) + "&per_page=20")
    compact_pulls = []
    if isinstance(pulls, list):
        for pull in pulls:
            compact_pulls.append({
                "number": pull["number"], "title": pull["title"],
                "url": pull["html_url"], "author": pull["user"]["login"],
                "state": pull["state"], "draft": pull.get("draft"),
                "updated_at": pull["updated_at"], "head_sha": pull["head"]["sha"],
                "head_ref": pull["head"]["ref"],
                "head_repo": (pull["head"].get("repo") or {}).get("full_name"),
            })
    raw = {"observed_utc": observed, "pulls": pulls, "repository_search": search,
           "forks": forks, "code_search": code_search,
           "omission": "Mutable RaD PRs are excluded; historical source20 only."}
    (raw_dir / "api-responses.json").write_text(json.dumps(raw, indent=2) + "\n")
    record = {
        "observed_utc": observed, "method": "gh api, read-only public sources",
        "scope": "Mutable RaD PRs and fork branches excluded; completed public source20 only.",
        "repositories": repos, "pulls": compact_pulls,
        "fork_heads": fork_heads,
        "search_query": args.search,
        "search_results": [{"name": x["full_name"], "url": x["html_url"],
                            "description": x.get("description"),
                            "pushed_at": x.get("pushed_at")}
                           for x in search.get("items", [])
                           if not x["full_name"].startswith("hipotures/")],
        "search_error": search.get("error"),
        "code_search_query": code_query,
        "code_search_results": [{"repository": x["repository"]["full_name"],
                                 "path": x["path"], "url": x["html_url"]}
                                for x in code_search.get("items", [])
                                if not x["repository"]["full_name"].startswith("hipotures/")],
        "code_search_error": code_search.get("error"),
        "raw_path": str(raw_dir / "api-responses.json"),
    }
    output.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"poll": str(output), "observed_utc": observed,
                      "pull_count": len(compact_pulls), "repositories": repos,
                      "search_count": len(record["search_results"]),
                      "fork_count": len(fork_heads),
                      "code_search_count": len(record["code_search_results"]),
                      "search_error": record["search_error"]}, indent=2))


if __name__ == "__main__":
    main()
