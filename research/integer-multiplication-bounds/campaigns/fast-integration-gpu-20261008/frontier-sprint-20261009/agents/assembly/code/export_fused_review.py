#!/usr/bin/env python3
"""Export only explicitly pinned inputs and independently reproduce arithmetic.

Apache-2.0. Prepared for RaD with OpenAI GPT-6.1 Sol assistance.
Downloaded sources stay in a disposable destination; this tool does not
publish them to Git. The two imports of the mathematical reviewer refer
only to this lane's independent helpers, which are copied explicitly.
"""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def safe(name):
    p = Path(name)
    need(isinstance(name, str) and not p.is_absolute() and ".." not in p.parts,
         "Unsafe export path")
    return p


def main():
    need(not sys.flags.optimize, "Assertion-disabled Python is unsupported")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sprint", type=Path, default=Path(__file__).resolve().parents[3])
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--certificate", type=Path, required=True)
    p.add_argument("--reference", type=Path, required=True)
    p.add_argument("--destination", type=Path, required=True)
    args = p.parse_args()
    root = args.sprint.resolve()
    config_path, certificate_path = (q.resolve().relative_to(root) for q in (args.config, args.certificate))
    config = json.loads(args.config.read_text())
    need(not args.destination.exists(), "A fresh clean destination is required")
    pins = {}
    for record in list(config["sources"].values())+list(config["inputs"].values()):
        name = str(safe(record["path"]))
        if name in pins:
            need(pins[name]["sha256"] == record["sha256"]
                 and pins[name]["bytes"] == record["bytes"], "Conflicting export pin")
        pins[name] = dict(path=name, sha256=record["sha256"], bytes=record["bytes"])
    extra = [config_path, certificate_path]
    extra.extend(Path("agents/assembly/code")/name for name in (
        "review_fused_lifetime.py", "review_balanced_unified.py", "review_rebuilt168_ceiling.py",
        "export_fused_review.py"))
    extra.extend(Path("agents/assembly")/name for name in ("LICENSE", "NOTICE"))
    for path in extra:
        path = safe(str(path))
        pins[str(path)] = dict(path=str(path), sha256=digest(root/path), bytes=(root/path).stat().st_size)
    args.destination.mkdir(parents=True)
    for name, pin in sorted(pins.items()):
        source, target = root/name, args.destination/name
        need(source.is_file() and not source.is_symlink(), "Non-regular source: "+name)
        need(digest(source) == pin["sha256"] and source.stat().st_size == pin["bytes"],
             "Original pin changed: "+name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        need(digest(target) == pin["sha256"], "Copied bytes differ: "+name)
    command = [sys.executable, "agents/assembly/code/review_fused_lifetime.py", "--sprint", ".",
        "--config", str(config_path), "--certificate", str(certificate_path),
        "--output", "work/independent-arithmetic.json"]
    process = subprocess.run(command, cwd=args.destination,
        env={"PATH": os.defpath, "LC_ALL": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True, text=True, timeout=120)
    (args.destination/"reproduction.stdout.log").write_text(process.stdout)
    (args.destination/"reproduction.stderr.log").write_text(process.stderr)
    need(process.returncode == 0, "Clean independent reproduction failed: "+process.stderr)
    clean = json.loads((args.destination/"work/independent-arithmetic.json").read_text())
    reference = json.loads(args.reference.read_text())
    ignored = ["elapsed_seconds", "observation_utc"]
    for row in (clean, reference):
        for name in ignored:
            row.pop(name)
    need(clean == reference, "Clean mathematical, pin or control output differs")
    manifest = dict(status="PASS_CLEAN_INDEPENDENT_ARITHMETIC_REPRODUCTION",
        candidate_id=config["candidate_id"], source_records=len(config["sources"]),
        input_records=len(config["inputs"]), unique_exported_files=len(pins),
        unique_exported_bytes=sum(pin["bytes"] for pin in pins.values()), files=list(pins.values()),
        configuration_sha256=digest(args.config), certificate_sha256=digest(args.certificate),
        original_review_sha256=digest(args.reference),
        clean_review_sha256=digest(args.destination/"work/independent-arithmetic.json"),
        checker_sha256=digest(Path(__file__)), comparison_ignored_fields=ignored,
        command=command, environment="Only PATH, LC_ALL and PYTHONDONTWRITEBYTECODE; no inherited PYTHONPATH or host configuration",
        coverage="Exact physical component histograms, full moments/fallback, raw word inventories,141-source24-input closure, full bridge,47+7 and negative controls. Independent finite review execution is a separate prerequisite.")
    (args.destination/"clean-export-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n")
    print("PASS clean export: "+str(len(pins))+" files, "+str(manifest["unique_exported_bytes"])
        +" bytes; independently recomputed arithmetic and all stable fields identical")
    print(process.stdout.rstrip())


if __name__ == "__main__":
    main()
