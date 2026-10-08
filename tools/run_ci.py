#!/usr/bin/env python3
"""Run explicit, bounded research checks. A green result covers registered checks only."""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {"repository", "smoke", "certificates", "full", "formal"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def relative_file(root: Path, value: str) -> Path:
    require(isinstance(value, str) and value and "\\" not in value, "Expected a POSIX relative path")
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts, f"Unsafe path: {value}")
    candidate = root.joinpath(*path.parts)
    require(candidate.resolve().is_relative_to(root.resolve()), f"Path escapes checkout: {value}")
    require(candidate.is_file(), f"Missing registered input: {value}")
    return candidate


def load_registry(root: Path = ROOT) -> list[dict]:
    manifest = root / "tools/ci_checks.json"
    data = json.loads(manifest.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    require(data.get("version") == 1 and isinstance(data.get("checks"), list), "Unsupported registry")
    ids = set()
    for check in data["checks"]:
        require(isinstance(check, dict), "Check must be an object")
        require(set(check) <= {"id", "group", "command", "inputs", "paths", "timeout_seconds", "scope", "sha256"}, "Unknown check field")
        name = check.get("id", "")
        require(isinstance(name, str) and re.fullmatch(r"[a-z][a-z0-9-]{0,63}", name), "Invalid check ID")
        require(name not in ids, f"Duplicate check ID: {name}")
        ids.add(name)
        require(check.get("group") in GROUPS, f"Unknown group in {name}")
        command = check.get("command")
        require(isinstance(command, list) and command and all(isinstance(x, str) and x for x in command), f"Invalid argv: {name}")
        require(type(check.get("timeout_seconds")) is int and 0 < check["timeout_seconds"] <= 1800, f"Invalid timeout: {name}")
        require(isinstance(check.get("scope"), str) and check["scope"].strip(), f"Missing scientific scope: {name}")
        for key in ("inputs", "paths"):
            require(isinstance(check.get(key), list) and check[key] and all(isinstance(x, str) and x for x in check[key]), f"Missing {key}: {name}")
        for item in check["inputs"]:
            relative_file(root, item)
        require(isinstance(check.get("sha256", {}), dict), f"Invalid hashes: {name}")
        for path, digest in check.get("sha256", {}).items():
            require(path in check["inputs"] and isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest), f"Invalid pin: {name}")
            require(hashlib.sha256(relative_file(root, path).read_bytes()).hexdigest() == digest, f"Source pin mismatch: {path}")
    return data["checks"]


def changed_paths(root: Path, base: str | None, head: str = "HEAD") -> list[str] | None:
    if not base or set(base) == {"0"}:
        return None  # First push: run every registered automatic check.
    require(re.fullmatch(r"[0-9a-fA-F]{40,64}", base) is not None, "Base must be a commit SHA")
    try:
        output = subprocess.check_output(["git", "diff", "--name-only", "-z", f"{base}...{head}", "--"], cwd=root, timeout=30)
    except subprocess.CalledProcessError:
        return None  # Missing history is not grounds to omit checks.
    return [x.decode("utf-8") for x in output.split(b"\0") if x]


def selected(check: dict, changes: list[str] | None, all_checks: bool = False) -> bool:
    if all_checks or changes is None:
        return True
    control = ("tools/run_ci.py", "tools/ci_checks.json", "tools/test_ci.py", ".github/workflows/verify.yml")
    return any(path in control or any(fnmatch.fnmatchcase(path, pattern) for pattern in check["paths"]) for path in changes)


def run_command(argv: list[str], cwd: Path, timeout: int, log: Path) -> tuple[str, int | None]:
    command = [sys.executable if x == "{python}" else x for x in argv]
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1", OMP_NUM_THREADS="2", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    with log.open("wb") as output:
        process = subprocess.Popen(command, cwd=cwd, env=environment, stdout=output, stderr=subprocess.STDOUT, start_new_session=(os.name == "posix"))
        try:
            code = process.wait(timeout=timeout)
            return ("pass" if code == 0 else "fail"), code
        except subprocess.TimeoutExpired:
            if os.name == "posix":
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            else:
                process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                if os.name == "posix":
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                else:
                    process.kill()
                process.wait()
            return "timeout", None


def escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def execute(group: str, root: Path, directory: Path, changes: list[str] | None, all_checks: bool) -> int:
    checks = [item for item in load_registry(root) if item["group"] == group]
    require(checks, f"No checks registered for {group}; no verification can be claimed")
    require(not directory.exists(), f"Refusing to overwrite CI evidence: {directory}")
    directory.mkdir(parents=True)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True, timeout=10).strip()
    except subprocess.CalledProcessError:
        commit = "not-a-git-checkout"
    results = []
    for check in checks:
        row = {"id": check["id"], "scope": check["scope"], "command": check["command"]}
        if not selected(check, changes, all_checks):
            row.update(status="skipped-unaffected", seconds=0)
        else:
            row["inputs_sha256"] = {path: hashlib.sha256(relative_file(root, path).read_bytes()).hexdigest() for path in check["inputs"]}
            log = directory / (check["id"] + ".log")
            print(f"RUN {check['id']}: {check['scope']}", flush=True)
            start = time.monotonic()
            try:
                status, code = run_command(check["command"], root, check["timeout_seconds"], log)
                row.update(status=status, exit_code=code)
            except OSError as error:
                row.update(status="error", error=str(error))
            row["seconds"] = round(time.monotonic() - start, 3)
            if log.exists():
                # Print bounded output; preserve the complete log as an artifact.
                print(log.read_text(encoding="utf-8", errors="replace")[-24000:], flush=True)
        print(f"{row['status'].upper()} {check['id']}", flush=True)
        results.append(row)
    failed = any(r["status"] not in {"pass", "skipped-unaffected"} for r in results)
    status = "fail" if failed else "pass" if any(r["status"] == "pass" for r in results) else "skipped-unaffected"
    report = {"version": 1, "commit": commit, "python": sys.version, "group": group, "status": status, "checks": results,
              "scope": "Registered checks only. Not formal verification, external peer review, or validation of unregistered research."}
    (directory / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = f"## RaD: {group} — {status}\n\n| Check | Result | Scope |\n|---|---|---|\n"
    summary += "".join(f"| {r['id']} | {r['status']} | {escape(r['scope'])} |\n" for r in results)
    summary += "\n" + report["scope"] + "\n"
    (directory / "summary.md").write_text(summary, encoding="utf-8")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as handle:
            handle.write(summary)
    return int(failed)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", choices=sorted(GROUPS))
    parser.add_argument("--all", action="store_true", help="Run selected group even when its paths are unchanged")
    parser.add_argument("--base", help="Known comparison commit SHA; omitted means run all registered checks")
    parser.add_argument("--output", type=Path, help="New evidence directory, preferably outside the checkout")
    parser.add_argument("--matrix", choices=("automatic", "full"), help="Emit only registered groups for GitHub Actions")
    args = parser.parse_args()
    try:
        checks = load_registry()
        if args.matrix:
            allowed = GROUPS if args.matrix == "full" else GROUPS - {"full", "formal"}
            groups = sorted({check["group"] for check in checks} & allowed)
            require(groups, "No registered verification groups")
            print(json.dumps({"group": groups, "python": ["3.11", "3.13", "3.14"]}))
            return 0
        require(args.group is not None, "Choose --group or --matrix")
        output = args.output or Path(tempfile.mkdtemp(prefix="rad-ci-")) / args.group
        return execute(args.group, ROOT, output, changed_paths(ROOT, args.base), args.all)
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
