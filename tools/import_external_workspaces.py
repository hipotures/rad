#!/usr/bin/env python3
"""Preserve durable files from historical benchmark and launcher workspaces.

Original execution paths remain intact. This tool never stages, commits,
pushes, starts a server or copies oversized execution payloads. Existing
different destination files are preserved and cause copy to stop for review.
"""
import argparse
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path

import archive_workspace as archive

ROOT = archive.ROOT
SOURCES = {"benchmarks": Path("/srv/ai/benchmarks"), "launchers": Path("/srv/ai/launchers")}
PRUNE = {".git", ".venv", ".cache", ".uv-cache", "uv-cache", "venv-hf",
         "node_modules", "__pycache__", "repos", "deps", "vendor", "third_party",
         "build", "builds", "build-default", "python-packages", "hf-xet-env", "hf-xet-lib"}
CATALOG = ROOT / "docs/external-workspaces.json"
MAX_JSON_EXPORT = 64 * archive.MAX_BYTES


def digest(data):
    return hashlib.sha256(data).hexdigest()


def files():
    for namespace, source in SOURCES.items():
        if not source.is_dir():
            raise FileNotFoundError(source)
        for base, dirs, names in os.walk(source):
            dirs.sort()
            for name in list(dirs):
                path = Path(base) / name
                relative = str(Path(namespace) / path.relative_to(source))
                if path.is_symlink() or name in PRUNE or name.endswith("venv") or name.startswith("build-") or (name == "llama.cpp" and Path(base).name == "runtime"):
                    dirs.remove(name)
                    yield path, relative, "local-directory", None
            for name in sorted(names):
                path = Path(base) / name
                relative = str(Path(namespace) / path.relative_to(source))
                if path.is_symlink():
                    yield path, relative, "local-symlink", 0
                elif path.is_file():
                    yield path, relative, None, path.stat().st_size


def reject(path, data):
    why = archive.reason(path, data=data)
    if why:
        return why
    for label, pattern in archive.SECRETS:
        if pattern.search(data):
            return label
    return None


def plan():
    selected, excluded, exports = [], [], []
    for source, relative, why, size in files():
        destination = ROOT / relative
        # Directory/format checks run before reading bytes. Empty JSON is only
        # used to check its location; actual bytes are checked below.
        if why is None:
            why = archive.reason(destination, data=b"")
            if why == "invalid-notebook":
                why = None
        if why is None and size > archive.file_limit(destination):
            why = "large-artifact"
        if why is None:
            data = source.read_bytes()
            why = reject(destination, data)
        if why:
            excluded.append({"path": relative, "bytes": size, "reason": why})
            if why in {"large-artifact", "row-level-result-dump"} and source.suffix == ".json" and size <= MAX_JSON_EXPORT:
                exports.append(relative)
        else:
            selected.append({"path": relative, "bytes": len(data), "sha256": digest(data),
                             "executable": bool(source.stat().st_mode & 0o111)})
    return selected, excluded, exports


def original(relative):
    parts = Path(relative).parts
    return SOURCES[parts[0]].joinpath(*parts[1:])


def write_new_or_identical(path, data, executable=False):
    if path.is_symlink() or (path.exists() and path.read_bytes() != data):
        raise RuntimeError("Preserve different existing destination for review: " + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(data)
        path.chmod(0o755 if executable else 0o644)


def compact(relative):
    source = original(relative)
    data = source.read_bytes()
    try:
        value = json.loads(data)
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(value, dict) or "messages" in value:
        return None
    budget = [4000]

    def prune(value, depth=0):
        budget[0] -= 1
        if budget[0] < 0 or depth > 10:
            return {"omitted": "bounded header export; consult the local original"}
        if isinstance(value, list):
            if len(value) > 32:
                return {"omitted_list_items": len(value)}
            return [prune(item, depth + 1) for item in value]
        if isinstance(value, dict):
            return {key: prune(item, depth + 1) for key, item in value.items()}
        if isinstance(value, str) and len(value) > 4096:
            return {"omitted_string_characters": len(value)}
        return value

    target = Path(relative).parent / "compact-results" / (source.name + ".headers.json")
    record = {"source": str(source), "source_bytes": len(data), "source_sha256": digest(data),
              "scope": "Bounded scalar/header evidence, not the original schema or a replacement input. Lists over 32 items, long strings and node/depth excess are explicitly omitted.",
              "compact_evidence": prune(value)}
    output = (json.dumps(record, indent=2) + "\n").encode()
    why = reject(ROOT / target, output)
    if why:
        raise RuntimeError("Compact export rejected: " + str(target) + ": " + why)
    return target, output, record


def aliases():
    records = []
    for link in sorted(Path("/srv/ai").glob("*LATEST_REPORT.md")):
        if not link.is_symlink():
            continue
        target = link.resolve()
        relative = Path("benchmarks") / target.relative_to(SOURCES["benchmarks"])
        records.append({"original_alias": str(link), "original_target": os.readlink(link),
                        "repository_target": str(relative)})
    return records


def summary(selected, excluded):
    groups = collections.defaultdict(lambda: {"files": 0, "bytes": 0})
    for record in selected:
        parts = Path(record["path"]).parts
        group = "/".join(parts[:2])
        groups[group]["files"] += 1
        groups[group]["bytes"] += record["bytes"]
    return {"selected_files": len(selected), "selected_bytes": sum(r["bytes"] for r in selected),
            "excluded_entries": len(excluded), "groups": dict(sorted(groups.items())),
            "exclusion_reasons": dict(collections.Counter(r["reason"] for r in excluded))}


def copy(selected, excluded, exports):
    for record in selected:
        source = original(record["path"])
        data = source.read_bytes()
        if digest(data) != record["sha256"]:
            raise RuntimeError("Source changed after planning: " + str(source))
        write_new_or_identical(ROOT / record["path"], data, record["executable"])
    generated = []
    for relative in exports:
        result = compact(relative)
        if result is None:
            continue
        target, data, provenance = result
        write_new_or_identical(ROOT / target, data)
        generated.append({"path": str(target), "bytes": len(data), "sha256": digest(data),
                          "source": provenance["source"], "source_sha256": provenance["source_sha256"]})
    report = {"snapshot_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "source_roots": {key: str(value) for key, value in SOURCES.items()},
              "policy": "Durable files are copied verbatim into the Git checkout, with executable bits preserved. Originals and large execution payloads stay at their existing paths. Nested repositories, build trees and environments are not copied. Compact exports explicitly identify omitted data.",
              "recovery_limits": "An excluded local-only artifact is not backed up by a path or hash. Use retained upstream/configuration/reproduction records and keep a separate backup for irreplaceable input/raw data. This import does not certify full regeneration of every historical environment.",
              **summary(selected, excluded), "files": selected, "compact_exports": generated,
              "report_aliases": aliases(),
              "largest_local_files": sorted((r for r in excluded if r["bytes"] is not None), key=lambda r:r["bytes"], reverse=True)[:40],
              "local_inventory": str(ROOT / "storage/external-workspace-exclusions.jsonl")}
    for alias in report["report_aliases"]:
        if not (ROOT / alias["repository_target"]).is_file():
            raise RuntimeError("Missing archived report alias target: " + alias["repository_target"])
    archive.save(CATALOG, report)
    return report


def verify():
    report = json.loads(CATALOG.read_text())
    for record in report["files"] + report["compact_exports"]:
        path = ROOT / record["path"]
        if not path.is_file() or path.is_symlink() or digest(path.read_bytes()) != record["sha256"]:
            raise RuntimeError("Archived file mismatch: " + str(path))
    for record in report["files"]:
        path = original(record["path"])
        if digest(path.read_bytes()) != record["sha256"]:
            raise RuntimeError("Original changed since import: " + str(path))
    print(json.dumps({"state": "PASS", "verbatim_files": len(report["files"]),
                      "compact_exports": len(report["compact_exports"]),
                      "report_aliases": len(report["report_aliases"])}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["plan", "copy", "verify"])
    args = parser.parse_args()
    if args.command == "verify":
        verify()
        return
    selected, excluded, exports = plan()
    archive.save(ROOT / "storage/external-workspace-plan.json", {"selected": selected, "excluded": excluded, "export_candidates": exports})
    with (ROOT / "storage/external-workspace-exclusions.jsonl").open("w") as stream:
        for record in excluded:
            stream.write(json.dumps(record) + "\n")
    if args.command == "copy":
        report = copy(selected, excluded, exports)
        print("COMPACT_EXPORTS", len(report["compact_exports"]), flush=True)
    print(json.dumps(summary(selected, excluded), indent=2), flush=True)


if __name__ == "__main__":
    main()
