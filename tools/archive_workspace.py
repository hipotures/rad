#!/usr/bin/env python3
"""Select durable research files; inventory local payloads; audit the Git index.

This tool never deletes artifacts, downloads resources, runs research, commits,
or pushes. plan/stage are bulk-import operations; individual tasks stage their
own paths with Git and use audit --staged-only before committing.
"""
import argparse
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
STUDY = "iq3s-residency-20261004T230051Z"
MAX_BYTES = 1024 * 1024
MAX_STAGED_BYTES = 20 * MAX_BYTES
LEGACY_EXTENSIONS = {
    ".md", ".py", ".sh", ".c", ".cpp", ".cu", ".h", ".hpp", ".cuh",
    ".json", ".jsonl", ".csv", ".txt", ".patch", ".diff", ".toml",
    ".yaml", ".yml", ".ini", ".cfg", ".cmake", ".svg", ".png", ".log",
}
EXTENSIONS = LEGACY_EXTENSIONS | {
    ".rs", ".go", ".R", ".r", ".js", ".mjs", ".cjs", ".ts", ".tsx",
    ".jsx", ".html", ".css", ".sql", ".lock", ".ipynb",
}
LEGACY_NAMES = {".gitignore", "LICENSE", "LICENSE.txt", "NOTICE", "CMakeLists.txt", "Makefile"}
NAMES = LEGACY_NAMES | {".gitattributes", "Dockerfile"}
LOCAL_DIRS = {
    ".git", ".venv", ".analysis-venv", "venv", "__pycache__", ".cache",
    "node_modules", "builds", "build", "src", "source", "dependency",
    "dependencies", "vendor", "third_party", "raw", "traces", "telemetry",
    "tapes", "extended", "checkpoints", "token-ids", "corpus", "inputs", "data",
    "datasets", "manual", "work", "downloads", "repos", "envs", "tmp",
    "derived", "dist", "target",
}
# Retain bounded run contracts even when located inside otherwise local raw data.
CONTRACTS = {
    "episode.json", "validation.json", "fidelity.json", "error.json",
    "config.json", "command.json", "results.json", "identity.json",
    "manifest.json", "schema.json", "dataset-manifest.json",
}
SECRETS = [
    ("private-key", re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("github-token", re.compile(rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b")),
    ("huggingface-token", re.compile(rb"\bhf_[A-Za-z0-9]{30,}\b")),
    ("api-key", re.compile(rb"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b")),
    ("aws-access-key", re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
]

def git(*args, binary=False):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=not binary)

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2) + "\n")
    os.replace(temp, path)

def file_limit(path):
    return 4 * MAX_BYTES if path.suffix in {".patch", ".diff"} else MAX_BYTES

def reason(path, data=None):
    """Check artifact role/size; audit can supply the actual indexed bytes."""
    relative = path.relative_to(ROOT)
    parts = relative.parts
    if parts[0] not in {STUDY, "docs", "tools", "research"}:
        if not (len(parts) == 1 and path.name in {"README.md", "AGENTS.md", "LICENSE", ".gitignore"}):
            return "outside-managed-research"
    if path.is_symlink():
        return "local-symlink"
    if any(p.startswith(".env") or p in {"credentials", "secrets", ".ssh"} for p in parts):
        return "private-configuration"
    if any(p.endswith("venv") or p in {"site-packages", "dist-packages"} for p in parts[:-1]):
        return "local-directory:virtual-environment"
    if "sources" in parts and "open-jev" in parts:
        return "third-party-source-snapshot"
    blocked = set(parts[:-1]) & LOCAL_DIRS
    if parts[0] == "research" and "logs" in parts[:-1]:
        blocked.add("logs")
    if parts[0] == STUDY and any(parts[i:i+2] == ("git", "builds") for i in range(len(parts)-2)):
        # This is provenance (commands/patches/logs), not a compiled build tree.
        blocked.discard("builds")
    hard = blocked - {"raw", "data", "inputs"}
    if hard:
        return "local-directory:" + sorted(hard)[0]
    if blocked and path.name not in CONTRACTS and not path.name.endswith("-manifest.json"):
        return "local-payload-directory"
    if path.name == "owned-process.json" or path.name.endswith(".pid"):
        return "transient-process-state"
    if path.name.endswith("-ids.json"):
        return "token-id-payload"
    names = LEGACY_NAMES if parts[0] == STUDY else NAMES
    extensions = LEGACY_EXTENSIONS if parts[0] == STUDY else EXTENSIONS
    if path.name not in names and path.suffix not in extensions:
        return "non-durable-format"
    if path.suffix == ".png" and not ({"plots", "figures"} & set(parts)):
        return "non-research-image"
    size = len(data) if data is not None else path.stat().st_size
    if size > file_limit(path):
        return "large-artifact"
    if data is None:
        data = path.read_bytes()
    if path.suffix != ".png":
        if b"\0" in data:
            return "binary-content"
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            return "non-utf8-content"
    if path.suffix in {".json", ".ipynb"}:
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            return "invalid-notebook" if path.suffix == ".ipynb" else None
        if path.suffix == ".ipynb":
            if not isinstance(parsed, dict) or not isinstance(parsed.get("cells"), list):
                return "invalid-notebook"
            if any(cell.get("outputs") or cell.get("execution_count") is not None
                   for cell in parsed["cells"] if isinstance(cell, dict)):
                return "notebook-execution-payload"
        if isinstance(parsed, dict) and "messages" in parsed and "model" in parsed:
            return "request-payload"
        def rows(value):
            if isinstance(value, list):
                return len(value) > 128 or any(rows(v) for v in value)
            return isinstance(value, dict) and any(rows(v) for v in value.values())
        # Hash/provenance inventories are durable references to local payloads.
        inventory = any(word in path.name for word in ["manifest", "inventory", "index", "catalog"]) or parts[:2] == ("docs", "compact-results")
        if size > 128 * 1024 and not inventory and rows(parsed):
            return "row-level-result-dump"
    return None

def compact_results(excluded):
    """Preserve scalar/header evidence without changing the original dumps."""
    grouped = collections.defaultdict(list)
    for record in excluded:
        path = ROOT / record["path"]
        if record["reason"] not in {"large-artifact", "row-level-result-dump"} or path.suffix != ".json":
            continue
        if path.name.endswith("-ids.json"):
            continue
        try:
            data = path.read_bytes()
            value = json.loads(data)
        except (ValueError, UnicodeDecodeError):
            continue
        if not isinstance(value, dict) or "messages" in value:
            continue
        budget = [800]
        def prune(v, depth=0):
            budget[0] -= 1
            if budget[0] < 0 or depth > 8:
                return {"omitted": "bounded compact export; consult original source"}
            if isinstance(v, list):
                if len(v) > 32:
                    return {"omitted_list_items": len(v)}
                return [prune(x, depth+1) for x in v]
            if isinstance(v, dict):
                return {k: prune(x, depth+1) for k, x in v.items()}
            if isinstance(v, str) and len(v) > 4096:
                return {"omitted_string_characters": len(v)}
            return v
        parts = path.relative_to(ROOT).parts
        group = parts[2] if len(parts)>2 and parts[1] in {"campaigns", "experiments"} else parts[1]
        grouped[group].append({"source": record["path"], "source_bytes": len(data), "source_sha256": hashlib.sha256(data).hexdigest(), "compact_evidence": prune(value)})
    generated = []
    for group, records in sorted(grouped.items()):
        chunk, amount, part = [], 0, 1
        def emit(items, number):
            p = ROOT / "docs/compact-results" / (group + "-part" + str(number) + ".json")
            save(p, {"scope": "Scalar/header export from local originals. Lists over32 items, long strings and depth/node excess are explicitly omitted; this is not the original schema and is not a replacement input for research scripts.", "records": items})
            generated.append(p)
        for record in records:
            size = len(json.dumps(record, indent=2))
            if chunk and amount + size > 700 * 1024:
                emit(chunk, part);chunk=[];amount=0;part+=1
            chunk.append(record);amount+=size
        if chunk:
            emit(chunk, part)
    return generated

def workspace_files():
    for directory in [ROOT / STUDY, ROOT / "docs", ROOT / "tools", ROOT / "research"]:
        if not directory.exists():
            continue
        for parent, dirs, files in os.walk(directory, followlinks=False):
            # Git internals and environment package trees are represented by a
            # directory entry, rather than publishing a dependency-file catalog.
            for name in sorted(dirs):
                p = Path(parent) / name
                if p.is_symlink():
                    yield p
            dirs[:] = sorted(d for d in dirs if d not in {".git", ".venv", ".analysis-venv", "__pycache__", "node_modules", "site-packages", "dist-packages"} and not d.endswith("venv") and not (Path(parent) / d / "pyvenv.cfg").is_file() and not (Path(parent) / d).is_symlink())
            for name in sorted(files):
                yield Path(parent) / name
    for name in ["AGENTS.md", "LICENSE", ".gitignore", "README.md"]:
        if (ROOT / name).is_file():
            yield ROOT / name

def plan():
    selected, excluded, grouped = [], [], collections.defaultdict(lambda: {"files": 0, "bytes": 0})
    last = time.monotonic()
    for p in workspace_files():
        if time.monotonic() - last > 25:
            print("HEARTBEAT inventory", len(selected), "durable files;", len(excluded), "local files", flush=True)
            last = time.monotonic()
        relative = str(p.relative_to(ROOT))
        if p.is_symlink():
            excluded.append({"path": relative, "bytes": 0, "reason": "local-symlink"})
            continue
        why = reason(p)
        size = p.stat().st_size
        if why:
            entry = {"path": relative, "bytes": size, "reason": why}
            excluded.append(entry)
            parts = p.relative_to(ROOT).parts
            if len(parts) > 3 and parts[1] == "campaigns":
                group = "/".join(parts[:3])
            else:
                group = "/".join(parts[:2])
            grouped[group]["files"] += 1
            grouped[group]["bytes"] += size
        else:
            selected.append({"path": relative, "bytes": size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    return selected, excluded, dict(sorted(grouped.items()))

def audit(staged_only=False):
    failures, total, staged_total, largest = [], 0, 0, []
    staged_paths = set(git("diff", "--cached", "--name-only", "--diff-filter=ACMRU", "-z").split("\0")) - {""}
    records = git("ls-files", "--stage", "-z", binary=True).decode().split("\0")
    entries = []
    for record in filter(None, records):
        metadata, relative = record.split("\t", 1)
        mode, oid, stage = metadata.split()
        if staged_only and relative not in staged_paths:
            continue
        if mode not in {"100644", "100755"} or stage != "0":
            failures.append({"path": relative, "reason": "symlink, nested repository or unmerged index"})
            continue
        entries.append((oid, relative))
    # Check sizes before requesting contents: a force-added 30 GiB blob must
    # fail without loading or streaming the payload into this Python process.
    oids = sorted({oid for oid, _ in entries})
    metadata = subprocess.run(
        ["git", "cat-file", "--batch-check"], cwd=ROOT,
        input="".join(oid + "\n" for oid in oids), text=True,
        capture_output=True, check=True,
    ).stdout
    sizes = {}
    for line in metadata.splitlines():
        oid, kind, size = line.split()
        if kind != "blob":
            raise ValueError("Expected an indexed blob")
        sizes[oid] = int(size)
    last = time.monotonic()
    with subprocess.Popen(["git", "cat-file", "--batch"], cwd=ROOT,
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE) as objects:
        for oid, relative in entries:
            p = ROOT / relative
            size = sizes[oid]
            total += size
            if relative in staged_paths:
                staged_total += size
            largest.append((size, relative))
            if size > file_limit(p):
                failures.append({"path": relative, "reason": "large-artifact", "bytes": size})
                continue
            # Inspect indexed bytes, even if the worktree was subsequently
            # changed to hide a credential or binary which was staged earlier.
            objects.stdin.write((oid + "\n").encode())
            objects.stdin.flush()
            header = objects.stdout.readline().decode().split()
            assert header[1] == "blob" and int(header[2]) == size, header
            data = objects.stdout.read(size)
            assert objects.stdout.read(1) == b"\n"
            why = reason(p, data=data)
            if why:
                failures.append({"path": relative, "reason": why})
            for label, pattern in SECRETS:
                if pattern.search(data):
                    failures.append({"path": relative, "reason": label})
            if p.is_symlink() or not p.is_file() or p.stat().st_size != size or p.read_bytes() != data:
                failures.append({"path": relative, "reason": "worktree changed after staging"})
            if time.monotonic() - last > 25:
                print("HEARTBEAT publication audit", len(largest), "files", flush=True)
                last = time.monotonic()
        objects.stdin.close()
        objects.wait(timeout=10)
    if staged_total > MAX_STAGED_BYTES:
        failures.append({"reason": "staged-content-budget", "bytes": staged_total, "limit_bytes": MAX_STAGED_BYTES})
    report = {
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "state": "PASS" if not failures else "FAIL", "files": len(largest),
        "bytes": total, "largest_files": [{"path": p, "bytes": n} for n, p in sorted(largest, reverse=True)[:12]],
        "selection": "staged-changes" if staged_only else "entire-index",
        "staged_content_bytes": staged_total, "staged_content_limit_bytes": MAX_STAGED_BYTES,
        "failures": failures,
        "scope": "Index/worktree equality, role and size policy, no Git links/symlinks, UTF-8 text/bounded plots, recognizable credential formats. This is not a comprehensive secret detection guarantee.",
    }
    save(ROOT / "storage/publication-audit.json", report)
    print(json.dumps(report, indent=2), flush=True)
    return 0 if not failures else 1

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["plan", "stage", "audit"])
    parser.add_argument("--staged-only", action="store_true", help="Audit only changed indexed files; retain unrelated unstaged edits")
    args = parser.parse_args()
    if args.staged_only and args.command != "audit":
        parser.error("--staged-only is only supported by audit")
    if args.command == "audit":
        raise SystemExit(audit(staged_only=args.staged_only))
    selected, excluded, grouped = plan()
    generated = compact_results(excluded)
    save(ROOT / "storage/retention-plan.json", {"selected": selected, "excluded": excluded})
    with (ROOT / "storage/local-inventory.jsonl").open("w") as out:
        for record in excluded:
            out.write(json.dumps(record) + "\n")
    catalog = {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "workspace": str(ROOT / STUDY),
        "storage_policy": "Working payloads remain at their original paths; absence from Git is not deletion. Directory aggregates omit Git internals and virtual-environment package trees. Sizes are apparent file bytes, not unique physical disk usage.",
        "excluded_files": len(excluded), "excluded_apparent_bytes": sum(x["bytes"] for x in excluded),
        "groups": grouped, "largest_local_files": sorted(excluded, key=lambda r: r["bytes"], reverse=True)[:40],
        "existing_hash_manifests": [
            STUDY + "/git/artifact-inventory.jsonl",
            STUDY + "/campaigns/golden-swap-phase0-20261006T185015Z/artifact-manifest.json",
            STUDY + "/campaigns/golden-swap-phase1-20261006T200037Z/artifact-manifest.json",
            STUDY + "/campaigns/golden-swap-phase1-20261006T200037Z/references/reproduction-artifacts.json",
        ],
        "model_provenance": STUDY + "/campaigns/golden-swap-phase0-20261006T185015Z/provenance/model-identity.json",
        "complete_local_inventory": str(ROOT / "storage/local-inventory.jsonl"),
        "regenerate": "python3 tools/archive_workspace.py plan",
    }
    inventory = ROOT / "docs/local-artifacts.json"
    if inventory.exists():
        previous = json.loads(inventory.read_text())
        comparable_old = {k: v for k, v in previous.items() if k != "generated_utc"}
        comparable_new = {k: v for k, v in catalog.items() if k != "generated_utc"}
        if comparable_old == comparable_new:
            catalog["generated_utc"] = previous["generated_utc"]
    save(inventory, catalog)
    # Git cannot ignore by file size. Generate explicit paths for oversized
    # otherwise durable files without editing historical campaign policies.
    ignore = ROOT / ".gitignore"
    start = "# BEGIN generated oversized durable files"
    end = "# END generated oversized durable files"
    text = ignore.read_text()
    def escape(value):
        return "".join("\\" + c if c in "\\*?[] #!" else c for c in value)
    oversized = sorted("/" + escape(r["path"]) for r in excluded if r["reason"] in {"large-artifact", "row-level-result-dump", "token-id-payload", "request-payload"})
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    ignore.write_text(before + start + "\n" + "\n".join(oversized) + "\n" + end + after)
    # The inventory is itself a durable artifact; calculate its final content
    # after generation so the staged snapshot matches the current worktree.
    refreshed = {"docs/local-artifacts.json", ".gitignore"} | {str(p.relative_to(ROOT)) for p in generated}
    selected = [r for r in selected if r["path"] not in refreshed]
    for relative in sorted(refreshed):
        p = ROOT / relative
        selected.append({"path": relative, "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    save(ROOT / "storage/retention-plan.json", {"selected": selected, "excluded": excluded})
    print("SELECTED", len(selected), "files", sum(r["bytes"] for r in selected), "bytes; LOCAL", len(excluded), "files", flush=True)
    if args.command == "stage":
        allowed = {r["path"] for r in selected}
        staged = set(git("diff", "--cached", "--name-only", "-z").split("\0")) - {""}
        if staged - allowed:
            raise SystemExit("Refuse unrelated pre-existing staged changes: " + repr(sorted(staged - allowed)))
        paths = sorted(allowed)
        for i in range(0, len(paths), 100):
            subprocess.run(["git", "add", "-f", "--", *paths[i:i+100]], cwd=ROOT, check=True)
        print("STAGED; run python3 tools/archive_workspace.py audit before committing", flush=True)

if __name__ == "__main__":
    main()
