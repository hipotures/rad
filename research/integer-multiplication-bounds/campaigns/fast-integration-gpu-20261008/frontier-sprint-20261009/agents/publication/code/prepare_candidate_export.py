#!/usr/bin/env python3
"""Prepare a provisional source export in a coordinator-owned upstream clone.

This research-only helper performs no network access or Git mutations. It
copies explicitly reviewed inputs; scientific acceptance and release freezing
remain separate coordinator gates. Inventories preserve source SHA-256 pins.
"""
import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

BASE = "d1d6c070f5a8c684727ee7ec35d930f9ebfa9758"
PR161 = "d14e29157bc905be1ced0776dd893d0714013f3a"
PR163 = "15c702a929b7d640107a95e196186ad74e876c82"
METADATA163 = "e1813796ef5c3ca38c5dd7b9e8d81b3908ff5997"
IDENTITY = "balanced-components-bit-complex-161-20261009"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sprint", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args()
    sprint = args.sprint.resolve()
    destination = (args.destination or sprint / "work/publication/unified-provisional/repository").resolve()
    if not destination.is_relative_to(sprint / "work/publication") or not (destination / ".git").is_dir():
        raise ValueError("Coordinator must prepare an isolated upstream Git clone under work/publication")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=destination).decode().strip()
    origin = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=destination).decode().strip()
    if head != BASE or origin != "https://github.com/CrocSwap/integer-mult-bounds.git":
        raise ValueError("Candidate export is not the exact coordinator-inspected upstream base")
    source161 = sprint / "work/repos/pr161-d14e291"
    source163 = Path(json.loads((sprint / "agents/frontier/pr163-archive-manifest.json").read_text())["extracted_root"])
    entries = {}

    def put(name, source, provenance, expected=None, blob=None):
        if name.startswith(("tests/", "upstream/")) or name in {"LICENSE", "NOTICE"}:
            raise ValueError("Inherited tests, upstream and licenses cannot be replaced")
        if source.is_symlink() or not source.is_file() or ".." in Path(name).parts or Path(name).is_absolute():
            raise ValueError("Unsafe/missing export source: " + str(source))
        data = source.read_bytes()
        if expected and sha(data) != expected:
            raise ValueError("Source SHA-256 changed: " + str(source))
        if blob and hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() != blob:
            raise ValueError("Source disagrees with pinned GitHub blob: " + name)
        target = destination / name
        if target.is_symlink() or any(parent.is_symlink() for parent in target.parents):
            raise ValueError("Symlink export target")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        mode = 0o755 if source.stat().st_mode & 0o111 else 0o644
        target.chmod(mode)
        entries[name] = {"path": name, "bytes": len(data), "sha256": sha(data), "mode": mode,
                         "provenance": provenance, "source": str(source.relative_to(sprint))}

    original = json.loads((sprint / "agents/frontier/pr161-file-inventory.json").read_text())
    if original["head_sha"] != PR161:
        raise ValueError("PR161 dependency inventory moved")
    for item in original["files"]:
        if item["status"] not in {"added", "modified"}:
            raise ValueError("A dependency delta deletes or renames an inherited file")
        put(item["path"], source161 / item["path"], f"eumemic/integer-mult-bounds@{PR161}", blob=item["blob_sha"])

    bit_pins = json.loads((sprint / "agents/bit/source-inputs.json").read_text())
    config = json.loads((sprint / "agents/transfer/configs/unified-first.json").read_text())
    required163 = {name: item["sha256"] for name, item in bit_pins["files"].items()}
    for name, item in config["sources"].items():
        if name.startswith("PR163/"):
            required163[name[len("PR163/"):]] = item["sha256"]
    for name, expected in required163.items():
        put(name, source163 / name, f"chafreaky/integer-mult-bounds@{PR163}", expected=expected)
    for name, local, expected in (
        ("research/paired-cube-balanced-161/NOTICE", "pr163-NOTICE", "61c13d602f9f9a6477d84ebd2dd83d6c129c1e63b821a0497cbf88dcd584a5bc"),
        ("research/paired-cube-balanced-161/SOURCE.json", "pr163-SOURCE.json", "836e087c0d747ac06256949593eb35c72e6b3db7502683644d77ffac51f53985")):
        put(name, sprint / "work/frontier/20261009T075600Z" / local,
            f"chafreaky/integer-mult-bounds@{METADATA163} (attribution-only)", expected=expected)

    # Global native complex references preserve their upstream wrapper format.
    put("references/paired-cube/physical/frames.json", sprint / "agents/placement/fixtures/pr161-components-converged-frames.json",
        "RaD/OpenAI-assisted equal-frame component endpoint placement", expected="3dc05748386e9dd5a9eadb227e40c9de2a21aa1e95e90d4bae479951713d1652")
    put("certificates/paired-cube-physical-input.json", sprint / "work/placement/live161-components-converged/physical-profile.json",
        "Fresh complete native complex physical compiler output")

    portable = sprint / "agents/transfer/publication/joint-balanced-frames"
    if not (portable / "verify_transfer.py").is_file():
        raise ValueError("Portable transfer package is not ready")
    for source in sorted(portable.rglob("*")):
        if source.is_file() and "__pycache__" not in source.parts:
            put("research/joint-balanced-frames/" + source.relative_to(portable).as_posix(), source,
                f"RaD/OpenAI-assisted unified candidate {IDENTITY}")
    for name in ("verify_bit_frames.py", "bit_frame_search.py"):
        put("research/paired-component-bit/code/" + name, sprint / "agents/bit/code" / name,
            "RaD/OpenAI-assisted exact binary frame/word/prime verifier")
    for name in ("source-inputs.json", "frame-proof.md"):
        put("research/paired-component-bit/" + name, sprint / "agents/bit" / name,
            "RaD/OpenAI-assisted binary finite proof and immutable dependency inventory")
    for name in ("binary-component-pairs-p12-frames.json", "binary-component-pairs-p12-profile.json"):
        put("research/paired-component-bit/fixtures/" + name, sprint / "agents/bit/fixtures" / name,
            f"Frozen binary component-pair candidate {IDENTITY}")
    put("research/paired-component-bit/NOTICE", portable / "NOTICE", "Unified inherited attribution retained")
    put("research/paired-component-bit/LICENSE", portable / "LICENSE", "Apache-2.0 inherited license retained")

    observed = dt.datetime.now(dt.timezone.utc)
    inventory = {"candidate_id": IDENTITY, "package_alias": "research/joint-balanced-frames",
                 "status": "PROVISIONAL_EXPORT", "scientific_freeze_approved": False,
                 "created_utc": observed.isoformat(), "base_sha": BASE,
                 "default_branch": "main", "destination": str(destination.relative_to(sprint)),
                 "dependency_source": {"PR161": PR161, "PR163_mathematics": PR163, "PR163_attribution": METADATA163},
                 "entries": sorted(entries.values(), key=lambda item: item["path"]),
                 "complex_encodings": {"raw_list_sha256": "f02a59311c667316b1f2e21916cebf71c58f79fbfbd3a126a24743d1d7ff016a",
                                       "upstream_wrapper_sha256": "3dc05748386e9dd5a9eadb227e40c9de2a21aa1e95e90d4bae479951713d1652"}}
    out = sprint / "work/publication" / ("export-inventory-" + observed.strftime("%Y%m%dT%H%M%SZ") + ".json")
    with out.open("x") as file:
        json.dump(inventory, file, indent=2)
        file.write("\n")
    print(json.dumps({"inventory": str(out.relative_to(sprint)), "files": len(entries),
                      "bytes": sum(item["bytes"] for item in entries.values()), "status": inventory["status"]}))


if __name__ == "__main__":
    main()
