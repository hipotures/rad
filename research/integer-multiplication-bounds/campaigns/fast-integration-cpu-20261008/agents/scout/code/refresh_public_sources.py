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
import re
from pathlib import Path
import subprocess


OWN = Path(__file__).resolve().parents[1]
CAMPAIGN = OWN.parent.parent
WORK = CAMPAIGN / "work" / "scout"
WATCHED = {
    "CrocSwap/integer-mult-bounds": "main",
    "Swapnil-jain/integer-mult-kappa": "main",
    "platypii/integer-mult-bounds-lean": "master",
}
CAMPAIGN_START = "2026-10-08T12:40:55Z"
KNOWN_EXCLUDED_PRS = {41, 42, 43, 44, 46, 47}


def api(path: str):
    raw = subprocess.check_output(["gh", "api", path], stderr=subprocess.PIPE)
    return json.loads(raw)


def graphql(query: str):
    raw = subprocess.check_output(["gh", "api", "graphql", "-f", "query=" + query],
                                  stderr=subprocess.PIPE)
    return json.loads(raw)["data"]["repository"]


def eligible_pulls():
    # List metadata without requesting any body. An independent RaD campaign
    # may publish during this run; its new branch/results remain excluded.
    meta = graphql('''query { repository(owner:"CrocSwap",name:"integer-mult-bounds") {
      pullRequests(first:100,states:[OPEN,CLOSED,MERGED],
        orderBy:{field:CREATED_AT,direction:DESC}) { nodes {
        number title author {login} state isDraft createdAt updatedAt
        headRefOid headRefName headRepository {nameWithOwner} url
      }} }}''')["pullRequests"]["nodes"]
    prior_path = OWN / "latest-observation.json"
    previous = json.loads(prior_path.read_text()) if prior_path.exists() else {}
    known_excluded = KNOWN_EXCLUDED_PRS | set(previous.get("excluded_campaign_linked_pr_numbers", []))
    eligible, excluded = [], []
    for p in meta:
        author = (p["author"] or {}).get("login", "")
        repository = (p["headRepository"] or {}).get("nameWithOwner", "")
        campaign_linked = (author.lower() == "hipotures"
                           or repository.lower().startswith("hipotures/")
                           or "rad " in p["title"].lower()
                           or bool(re.search(r"(?:^|[-/_])rad(?:$|[-/_])",
                                             p["headRefName"], re.I)))
        if p["createdAt"] >= "2026-10-08T13:35:00Z":
            # Incidental new changed-graph metadata coincided with the excluded
            # independent RaD publication. Conservative quarantine prevents
            # derivative results entering our source set without provenance.
            campaign_linked |= bool(re.search(r"changed[ -]*(?:dag|graph)",
                                              p["title"], re.I))
        if p["number"] in known_excluded or (p["createdAt"] >= CAMPAIGN_START and campaign_linked):
            excluded.append(p["number"])
            continue
        eligible.append(p)
    fields = " ".join(f'p{p["number"]}:pullRequest(number:{p["number"]}){{body}}'
                      for p in eligible)
    bodies = graphql('query {repository(owner:"CrocSwap",name:"integer-mult-bounds") {'
                     + fields + '}}') if fields else {}
    pulls = [{"number":p["number"], "title":p["title"],
              "user":{"login":(p["author"] or {}).get("login")},
              "state":"closed" if p["state"] in ("CLOSED","MERGED") else "open",
              "draft":p["isDraft"], "created_at":p["createdAt"], "updated_at":p["updatedAt"],
              "head":{"sha":p["headRefOid"], "ref":p["headRefName"],
                      "repo":{"full_name":(p["headRepository"] or {}).get("nameWithOwner")}},
              "html_url":p["url"], "body":bodies[f'p{p["number"]}']["body"]}
             for p in eligible]
    # Only this provenance filter sees newly acquired bodies. Repeated passes
    # quarantine references to a quarantined derivative as well as originals.
    while True:
        blocked = "|".join(map(str, sorted(known_excluded | set(excluded))))
        retained, newly_excluded = [], []
        for p in pulls:
            derivative = bool(re.search(r"(?:#|PR\s*#?|pull/)(?:"+blocked+r")\b",
                                        p["body"] or "", re.I))
            if derivative:
                newly_excluded.append(p["number"])
            else:
                retained.append(p)
        pulls = retained
        excluded.extend(newly_excluded)
        if not newly_excluded:
            break
    excluded_branches = {
        ((p["headRepository"] or {}).get("nameWithOwner", ""), p["headRefName"])
        for p in meta if p["number"] in excluded
    }
    return pulls, excluded, excluded_branches


def observed_head(item):
    repository, branch = item
    owner, name = repository.split("/", 1)
    # Commit metadata only: the REST commit response also includes source
    # patches. Aggregate upstream publication can now contain quarantined
    # campaign inputs, so never acquire those patches merely to watch a head.
    query = ('query {repository(owner:'+json.dumps(owner)+',name:'+json.dumps(name)
             +') {object(expression:'+json.dumps(branch)+') {... on Commit {'
              'oid committedDate author {name} messageHeadline url}}}}')
    data = graphql(query)["object"]
    return repository, {
        "branch": branch,
        "sha": data["oid"],
        "commit_utc": data["committedDate"],
        "author": data["author"]["name"],
        "title": data["messageHeadline"],
        "url": data["url"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--forks", action="store_true", help="also query linked fork branches")
    parser.add_argument("--search", action="store_true", help="refresh the broader repository search")
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rawdir = WORK / "observations" / stamp
    rawdir.mkdir(parents=True, exist_ok=False)
    pulls, excluded, excluded_branches = eligible_pulls()
    (rawdir / "pulls.json").write_text(json.dumps(pulls, indent=2) + "\n")
    with ThreadPoolExecutor(max_workers=3) as pool:
        heads = dict(pool.map(observed_head, WATCHED.items()))
    compact = {
        "observed_utc": stamp,
        "excluded_campaign_linked_pr_numbers": excluded,
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
            if name.lower().startswith("hipotures/"):
                # Completed historical snapshots are pinned separately. Never
                # enumerate newly published RaD campaign branches in a live poll.
                continue
            branches = api(f"repos/{name}/branches?per_page=100")
            compact["forks"][name] = {
                b["name"]: b["commit"]["sha"] for b in branches
                if (name, b["name"]) not in excluded_branches
                and not re.search(r"(?:^|[-/_])rad(?:$|[-/_])", b["name"], re.I)
            }
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
