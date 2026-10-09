#!/usr/bin/env python3
"""Read-only gh collection of source and review receipts for named PR heads.

This does not regenerate mathematics or grant a publication verdict. Every API
response is retained before it can be used by the separately authored assessment.
"""
import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UPSTREAM = "CrocSwap/integer-mult-bounds"


def request(endpoint):
    for attempt in range(3):
        try:
            return json.loads(subprocess.check_output(
                ["gh", "api", endpoint], stderr=subprocess.PIPE, timeout=45))
        except (subprocess.SubprocessError, json.JSONDecodeError):
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def get_pages(endpoint, key=None):
    pages = []
    for page in range(1, 101):
        sep = "&" if "?" in endpoint else "?"
        response = request(f"{endpoint}{sep}per_page=100&page={page}")
        pages.append(response)
        items = response[key] if key else response
        if len(items) < 100:
            return pages
    raise RuntimeError("Pagination limit reached; collection is incomplete")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intake", type=Path, required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--prs", type=int, nargs="+", default=[161, 160, 158, 144])
    args = parser.parse_args()
    intake = json.loads(args.intake.read_text())
    if not intake.get("complete"):
        raise RuntimeError("Intake did not finish successfully")
    prs = {pr["number"]: pr for pr in sum(intake["open_pages"], []) + sum(intake["closed_pages"], [])}
    destination = ROOT / "work/frontier" / args.label
    destination.mkdir(parents=True, exist_ok=False)
    plan = {}
    for number in args.prs:
        pr = prs[number]
        sha = pr["head"]["sha"]
        head_repo = pr["head"]["repo"]["full_name"]
        prefix = f"pr{number}"
        plan[f"{prefix}-metadata"] = (f"repos/{UPSTREAM}/pulls/{number}", None, False)
        plan[f"{prefix}-checks"] = (f"repos/{UPSTREAM}/commits/{sha}/check-runs", "check_runs", True)
        plan[f"{prefix}-statuses"] = (f"repos/{UPSTREAM}/commits/{sha}/statuses", None, True)
        plan[f"{prefix}-reviews"] = (f"repos/{UPSTREAM}/pulls/{number}/reviews", None, True)
        plan[f"{prefix}-comments"] = (f"repos/{UPSTREAM}/issues/{number}/comments", None, True)
        plan[f"{prefix}-files"] = (f"repos/{UPSTREAM}/pulls/{number}/files", None, True)
        # The toll-edge PR computes its new result in a source-bound verifier;
        # the underlying paired-cube certificate remains its predecessor's.
        if number == 158:
            for path in ["research/paired-cube-toll-edge/README.md", "research/paired-cube-toll-edge/verify.py"]:
                name = path.rsplit("/", 1)[-1].replace(".", "-")
                plan[f"{prefix}-{name}"] = (f"repos/{head_repo}/contents/{path}?ref={sha}", None, False)
        else:
            plan[f"{prefix}-certificate"] = (f"repos/{head_repo}/contents/certificates/paired-cube-network.json?ref={sha}", None, False)
    base = intake["default_commit"]
    for path in ["certificates/selected-result.json", "docs/research/community-round6-review.md", "docs/research/community-round6-validation.json", "README.md"]:
        name = path.rsplit("/", 1)[-1].replace(".", "-")
        plan[f"main-{name}"] = (f"repos/{UPSTREAM}/contents/{path}?ref={base}", None, False)
    result = {"started_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "intake": str(args.intake), "default_commit": base, "receipts": {}}

    def collect(item):
        name, (endpoint, key, paginated) = item
        body = get_pages(endpoint, key) if paginated else request(endpoint)
        raw = json.dumps(body, indent=2) + "\n"
        path = destination / f"{name}.json"
        path.write_text(raw)
        return name, {"endpoint": endpoint, "paginated": paginated, "page_count": len(body) if paginated else None,
                      "path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(raw.encode()).hexdigest(),
                      "bytes": len(raw.encode()), "observed_utc": dt.datetime.now(dt.timezone.utc).isoformat()}

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        pending = {pool.submit(collect, item): item[0] for item in plan.items()}
        for future in concurrent.futures.as_completed(pending):
            name = pending[future]
            try:
                name, receipt = future.result()
                result["receipts"][name] = receipt
            except Exception as exc:
                result["receipts"][name] = {"complete": False, "error": f"{type(exc).__name__}: {exc}"}
            (destination / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    result["completed_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    result["complete"] = all("error" not in record for record in result["receipts"].values())
    (destination / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"complete": result["complete"], "requests": len(result["receipts"]), "manifest": str((destination / "manifest.json").relative_to(ROOT)), "observed_utc": result["completed_utc"]}))
    if not result["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
