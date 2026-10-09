#!/usr/bin/env python3
"""Reproduce frozen arithmetic and the complete independent finite binding.

Apache-2.0. Prepared for RaD with OpenAI GPT-6.1 Sol assistance.
This exports explicit pins to a fresh disposable root. It reruns arithmetic
and identity binding; finite checkers have their separate executed receipts
and reproduction commands, and are not rerun by this command.
"""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from export_fused_review import digest, need, safe


def main():
    need(not sys.flags.optimize, "Assertion-disabled Python is unsupported")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sprint", type=Path, default=Path(__file__).resolve().parents[3])
    for name in ("config", "certificate", "binding", "binding-reference", "destination"):
        p.add_argument("--"+name, type=Path, required=True)
    args = p.parse_args()
    root = args.sprint.resolve()
    binding = json.loads(args.binding.read_text())
    relative = lambda path: str(path.resolve().relative_to(root))
    minimal = {"PATH": os.defpath, "LC_ALL": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1"}
    first = subprocess.run([sys.executable, str(Path(__file__).with_name("export_fused_review.py")),
        "--sprint", str(root), "--config", str(args.config.resolve()),
        "--certificate", str(args.certificate.resolve()),
        "--reference", str(root/binding["receipts"]["arithmetic"]["path"]),
        "--destination", str(args.destination.resolve())],
        env=minimal, capture_output=True, text=True, timeout=120)
    need(first.returncode == 0, "Arithmetic clean reproduction failed: "+first.stderr)
    manifest = json.loads((args.destination/"clean-export-manifest.json").read_text())
    pins = {pin["path"]:pin for pin in manifest["files"]}
    for pin in list(binding["receipts"].values())+list(binding["supplemental_sources"].values()):
        name = str(safe(pin["path"]))
        need(digest(root/name) == pin["sha256"] and (root/name).stat().st_size == pin["bytes"],
             "Supplemental pin changed: "+name)
        if name in pins:
            need(pins[name] == pin, "Conflicting supplemental pin")
        pins[name] = pin
    for path in (relative(args.binding), "agents/assembly/code/bind_fused_reviews.py",
                 "agents/assembly/code/export_fused_acceptance.py"):
        pins[path] = dict(path=path, bytes=(root/path).stat().st_size, sha256=digest(root/path))
    for name, pin in sorted(pins.items()):
        target = args.destination/safe(name)
        if not target.exists():
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(root/name,target)
        need(digest(target) == pin["sha256"], "Supplemental copied bytes differ: "+name)
    command = [sys.executable, "agents/assembly/code/bind_fused_reviews.py", "--sprint", ".",
        "--config", relative(args.config), "--binding", relative(args.binding),
        "--output", "work/independent-finite-binding.json"]
    second = subprocess.run(command, cwd=args.destination, env=minimal,
        capture_output=True,text=True,timeout=120)
    (args.destination/"binding.stdout.log").write_text(second.stdout)
    (args.destination/"binding.stderr.log").write_text(second.stderr)
    need(second.returncode == 0, "Clean finite binding failed: "+second.stderr)
    clean = json.loads((args.destination/"work/independent-finite-binding.json").read_text())
    reference = json.loads(args.binding_reference.read_text())
    need(clean == reference, "Clean finite binding differs")
    output = dict(status="PASS_CLEAN_ARITHMETIC_AND_INDEPENDENT_FINITE_BINDING",
        candidate_id=binding["candidate_id"], source_records=manifest["source_records"],
        input_records=manifest["input_records"], unique_exported_files=len(pins),
        unique_exported_bytes=sum(pin["bytes"] for pin in pins.values()),
        files=list(pins.values()), configuration_sha256=digest(args.config),
        author_receipt_sha256=digest(args.certificate), binding_config_sha256=digest(args.binding),
        original_binding_sha256=digest(args.binding_reference),
        clean_binding_sha256=digest(args.destination/"work/independent-finite-binding.json"),
        checker_sha256=digest(Path(__file__)), mathematical_fields_identical=True,
        binding_byte_output_identical=digest(args.binding_reference)==digest(args.destination/"work/independent-finite-binding.json"),
        finite_binding_command=command, environment=manifest["environment"],
        scope="Entire author141-source24-input arithmetic closure plus exact independent executed finite receipts, reviewer code/pins and native complex-cover proof. Expensive finite executions are documented by their lane receipts and are not repeated by this export.")
    (args.destination/"acceptance-export-manifest.json").write_text(json.dumps(output,sort_keys=True,indent=2)+"\n")
    print("PASS combined clean reproduction: "+str(len(pins))+" files, "+str(output["unique_exported_bytes"])
        +" bytes; mathematics equal and finite binding byte-identical")
    print(first.stdout.rstrip())
    print(second.stdout.rstrip())


if __name__ == "__main__":
    main()
