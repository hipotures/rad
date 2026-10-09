#!/usr/bin/env python3
"""Read all open upstream PRs through gh; retain immutable observation receipts.

This is an intake tool, not an automatic mathematical comparability oracle.
Unreviewed or changed heads keep the publication comparison unresolved.
"""
import argparse
import datetime as dt
import hashlib
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = "CrocSwap/integer-mult-bounds"


def api(endpoint):
    for attempt in range(3):
        try:
            return json.loads(subprocess.check_output(
                ["gh", "api", endpoint], timeout=45, stderr=subprocess.PIPE))
        except (subprocess.SubprocessError, json.JSONDecodeError):
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def pages(endpoint):
    result = []
    for page in range(1, 101):
        batch = api(f"{endpoint}&per_page=100&page={page}")
        result.append(batch)
        if len(batch) < 100:
            return result
    raise RuntimeError("Pagination limit reached; incomplete collection")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label")
    args = parser.parse_args()
    started = dt.datetime.now(dt.timezone.utc)
    label = args.label or started.strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "work/receipts" / label
    out.mkdir(parents=True, exist_ok=False)
    record = {"started_utc": started.isoformat(), "upstream": UPSTREAM}
    try:
        record["repository"] = api(f"repos/{UPSTREAM}")
        default = record["repository"]["default_branch"]
        record["default_commit"] = api(f"repos/{UPSTREAM}/commits/{default}")["sha"]
        record["open_pages"] = pages(f"repos/{UPSTREAM}/pulls?state=open&sort=updated&direction=desc")
        record["closed_pages"] = pages(f"repos/{UPSTREAM}/pulls?state=closed&sort=updated&direction=desc")
        record["completed_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        record["complete"] = True
    except Exception as exc:
        record["complete"] = False
        record["failure"] = f"{type(exc).__name__}: {exc}"
        (out / "api.json").write_text(json.dumps(record, indent=2) + "\n")
        raise
    raw = json.dumps(record, indent=2) + "\n"
    (out / "api.json").write_text(raw)
    prs = sum(record["open_pages"], [])
    compact = {
        "observed_utc": record["completed_utc"], "collection_started_utc": record["started_utc"],
        "default_branch": default, "default_commit": record["default_commit"],
        "open_pages": len(record["open_pages"]), "open_count": len(prs),
        "receipt": str((out / "api.json").relative_to(ROOT)),
        "receipt_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "comparison_resolved": False,
        "reason": "Source-aware assessment is separate; a successful API read is not a publication gate.",
        "claims": [{"pr": r["number"], "author": r["user"]["login"], "head_sha": r["head"]["sha"],
                    "head_repository": r["head"]["repo"]["full_name"] if r["head"]["repo"] else None,
                    "state": r["state"], "draft": r["draft"], "merged": bool(r["merged_at"]),
                    "updated_at": r["updated_at"], "title": r["title"], "exact_kappa": None,
                    "certificate_source": None, "construction_family": None,
                    "conditional_assumptions": "Not yet individually assessed in this observation",
                    "evidence_observed": ["Current PR body and metadata"],
                    "comparability": "pending source assessment"} for r in prs]
    }
    (out / "intake.json").write_text(json.dumps(compact, indent=2) + "\n")
    print(json.dumps({"receipt": compact["receipt"], "observed_utc": compact["observed_utc"],
                      "open_count": len(prs), "default_commit": record["default_commit"]}))


if __name__ == "__main__":
    main()
