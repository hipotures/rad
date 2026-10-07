#!/usr/bin/env python3
"""Validate a prepared experiment plan without building or running inference."""

import argparse
import collections
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def check_file(path, item):
    require(path.is_file(), f"Missing input: {path}")
    require(path.stat().st_size == item["bytes"], f"Size mismatch: {path}")
    require(sha256(path) == item["sha256"], f"SHA256 mismatch: {path}")
    if "canonical_json_sha256" in item:
        canonical = json.dumps(read_json(path), sort_keys=True, separators=(",", ":")).encode()
        require(hashlib.sha256(canonical).hexdigest() == item["canonical_json_sha256"],
                f"Canonical payload SHA256 mismatch: {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-inputs", action="store_true",
                        help="Also hash the recorded local tape, binary and source; requires idle GPUs")
    args = parser.parse_args()
    campaign = Path(__file__).resolve().parents[1]
    root = Path(subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], cwd=campaign, text=True, timeout=10).strip())
    protocol = read_json(campaign / "configs/protocol.json")
    order = read_json(campaign / "configs/run-order.json")
    manifest = read_json(campaign / "input-manifest.json")
    workspace = read_json(campaign / "workspace.json")
    require(protocol["state"] == "PLANNED_NOT_STARTED", "This checker validates the frozen plan")
    require(workspace["execution_started_utc"] is None, "Planning workspace has an execution clock")
    require(workspace["execution_deadline_utc"] is None, "Planning workspace has an execution deadline")
    require(protocol["runtime"]["new_binary_sha256"] is None, "Plan unexpectedly claims a new binary")
    require(not protocol["runtime"]["new_instrumentation_implemented"], "Planning implementation state changed")
    require(order["protocol_id"] == protocol["protocol_id"], "Protocol/order mismatch")
    require(order["task"] == protocol["task"]["id"] == "math-rational", "Unexpected task")
    blocks = order["blocks"]
    require([b["block"] for b in blocks] == [1, 2, 3], "Wrong block IDs")
    require([b["arms"] for b in blocks] == [["CONTROL", "TRACE"], ["TRACE", "CONTROL"],
                                           ["CONTROL", "TRACE"]], "Run order changed")
    counts = collections.Counter(arm for block in blocks for arm in block["arms"])
    limits = protocol["request_limits"]
    require(dict(counts) == {"CONTROL": 3, "TRACE": 3}, "Arm counts are not three each")
    require(sum(counts.values()) == limits["planned_requests"] == order["expected_requests"] == 6,
            "Request totals disagree")
    require(max(counts.values()) <= limits["attempts_per_unchanged_point_max"], "Attempt cap exceeded")
    budget = protocol["execution_budget"]
    require(budget["stop_substantial_work_after_seconds"] + budget["finalization_reserve_seconds"]
            == budget["max_wall_seconds"] == 14400, "Execution budget is inconsistent")
    require(protocol["task"]["main_windows"] * 48 == protocol["task"]["main_routed_invocations"],
            "Window/invocation units disagree")
    require(manifest["task_work"]["committed_emitted_output"] == protocol["task"]["emitted_tokens"],
            "Output denominator mismatch")
    require(manifest["task_work"]["windows"] == protocol["task"]["main_windows"], "Tape windows mismatch")
    require(protocol["policy"]["victim_future_queries"] == 0, "Victim information scope changed")
    require("STRATA_VERIFY_PROFILE" in protocol["instrumentation"]["must_be_unset"],
            "Scheduling-changing profiler is not excluded")
    require(not protocol["decision_rules"]["is_measured_speedup"], "Attribution is mislabeled as acceleration")

    for item in manifest["references"]:
        path = (root / item["path"]).resolve()
        require(path.is_relative_to(root), f"Reference outside repository: {path}")
        check_file(path, item)

    linked_files = set()
    for path in campaign.glob("*.md"):
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            linked = (path.parent / target.split("#", 1)[0]).resolve()
            require(linked.is_file(), f"Broken document link: {path.name} -> {target}")
            linked_files.add(str(linked))

    local_count = 0
    if args.local_inputs:
        active = subprocess.check_output(
            ["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader"],
            text=True, timeout=10).strip()
        require(not active, "Local hashing refused while GPU compute processes are present")
        for item in manifest["external_inputs"]:
            check_file(Path(item["path"]), item)
            local_count += 1
        source = manifest["source_checkout"]
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source["path"],
                                       text=True, timeout=10).strip()
        require(head == source["expected_commit"], "Parent source checkout commit changed")
        work = Path(workspace["work_root"])
        require(work.is_dir(), "Planned external work directory is missing")
        require(not work.resolve().is_relative_to(root), "Execution work root must be external")
        for name in workspace["external_subdirectories"]:
            require((work / name).is_dir(), f"Missing work directory: {name}")

    print(json.dumps({
        "state": "PASS",
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": sha256(campaign / "configs/protocol.json"),
        "goal_sha256": sha256(campaign / "GOAL.md"),
        "references_verified": len(manifest["references"]),
        "document_links_verified": len(linked_files),
        "local_inputs_verified": local_count,
        "planned_requests": 6,
        "experiment_started": False,
        "scope": "Planning structure, references and optional local identities only; no runtime or measurement validation",
    }, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print(json.dumps({"state": "FAIL", "error": str(error)}), file=sys.stderr)
        sys.exit(1)
