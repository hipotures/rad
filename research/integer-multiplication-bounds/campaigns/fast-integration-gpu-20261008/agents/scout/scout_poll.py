#!/usr/bin/env python3
"""Read-only public GitHub scouting; keep compact polls and external raw reads."""
import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
from urllib.parse import quote

HISTORICAL_RAD_SHA = "4f8d6c8272b5ff307a0da51df545ec3cd96a8b6e"
CAMPAIGN_START = "2026-10-08T12:41:06Z"
HELD_DERIVATIVE_BRANCHES = {
    ("rohanarun/integer-mult-bounds", "research/rad-fixed-reversed"),
    ("chafreaky/integer-mult-bounds", "research/alternating-fixed-corners"),
    ("rohanarun/integer-mult-bounds", "research/optimal-carrier-matching"),
    ("chafreaky/integer-mult-bounds", "research/weighted-data-recovery"),
    ("rohanarun/integer-mult-bounds", "research/climbed-producers"),
    ("chafreaky/integer-mult-bounds", "research/exclusion-sum-order"),
}


def allowed_pull(pull):
    """Keep completed public RaD history; exclude every mutable RaD PR."""
    if pull.get("number") in (42, 43, 44, 46, 48, 49, 50, 54):
        return False
    repo = (pull.get("head", {}).get("repo") or {}).get("full_name")
    author = pull.get("user", {}).get("login")
    if author == "hipotures" or repo == "hipotures/integer-mult-bounds":
        return pull.get("number") == 20 and pull.get("head", {}).get("sha") == HISTORICAL_RAD_SHA
    ref = pull.get("head", {}).get("ref", "")
    if (repo, ref) in HELD_DERIVATIVE_BRANCHES:
        return False
    title = pull.get("title", "").lower()
    if pull.get("created_at", "") >= CAMPAIGN_START and (
        "rad " in title or "rad-" in ref or "rad/" in ref
    ):
        return False
    return True


def get(endpoint, jq=None):
    command = ["gh", "api", endpoint]
    if jq is not None:
        command.extend(["--jq", jq])
    result = subprocess.run(
        command, text=True, capture_output=True, check=False
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
    # Select discovery metadata inside gh: do not deliver unreviewed PR bodies
    # or commit patches to the collector or its retained acquisition file.
    pulls = get("repos/CrocSwap/integer-mult-bounds/pulls?state=all&per_page=100",
                '[.[] | {number,title,html_url,state,draft,created_at,updated_at,'
                'user:{login:.user.login},head:{sha:.head.sha,ref:.head.ref,'
                'repo:{full_name:.head.repo.full_name}}}]')
    if isinstance(pulls, list):
        # Do not interpret, persist, or print new RaD submission content.
        pulls = [pull for pull in pulls if allowed_pull(pull)]
    repo_ids = ["CrocSwap/integer-mult-bounds", "Swapnil-jain/integer-mult-kappa"]
    repos = {}
    for repo in repo_ids:
        info = get("repos/" + repo)
        head = get("repos/" + repo + "/commits/" + info.get("default_branch", "main"),
                   '{sha,commit:{committer:.commit.committer,message:.commit.message}}')
        repos[repo] = {
            "url": info.get("html_url"), "description": info.get("description"),
            "pushed_at": info.get("pushed_at"), "head_sha": head.get("sha"),
            "head_date": head.get("commit", {}).get("committer", {}).get("date"),
            "head_message": head.get("commit", {}).get("message"),
            "license": (info.get("license") or {}).get("spdx_id"),
        }
    forks = get("repos/CrocSwap/integer-mult-bounds/forks?sort=newest&per_page=100",
                '[.[] | {full_name,html_url,pushed_at}]')
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
                             for x in branches
                             if (fork["full_name"], x["name"]) not in HELD_DERIVATIVE_BRANCHES]
                            if isinstance(branches, list) else branches,
            })
    query = "search/repositories?q=" + quote(args.search) + "&per_page=20"
    search = get(query, '{total_count,incomplete_results,items:[.items[] | '
                 'select(.full_name | startswith("hipotures/") | not)]}')
    code_query = '"partial-swap" "integer"'
    code_search = get("search/code?q=" + quote(code_query) + "&per_page=20",
                      '{total_count,incomplete_results,items:[.items[] | '
                      'select(.repository.full_name | startswith("hipotures/") | not)]}')
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
           "omission": "Discovery metadata only: PR bodies/patches, mutable RaD PRs, and uncertain current derivatives are excluded; historical source20 only."}
    (raw_dir / "api-responses.json").write_text(json.dumps(raw, indent=2) + "\n")
    record = {
        "observed_utc": observed, "method": "gh api, read-only public sources",
        "scope": "Mutable RaD PRs/fork branches and uncertain current derivatives excluded; completed public source20 only.",
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
