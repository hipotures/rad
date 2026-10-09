#!/usr/bin/env python3
"""Make a pinned derived layout for explicit PR165 physical frame experiments.

This copies checked decoded finite input bytes to an ignored lane-owned layout
and links its scripts to the unchanged approved source. It does not regenerate
the producer or historical search, or modify the source/input directories.
"""
import argparse
import json
from pathlib import Path
import sys

from physical_search import require, sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-repository", default="https://github.com/chafreaky/integer-mult-bounds")
    args = parser.parse_args()
    require(not sys.flags.optimize, "assertion-disabled execution is unsupported")
    require(not args.output.exists(), "derived context already exists")
    source, inputs = args.source.resolve(), args.input.resolve()
    protocol = json.loads((inputs / "protocol.json").read_text())
    payload = {}
    for name in ("graph", "frames", "word", "profile-before", "physical-frames", "physical-pairs", "profile"):
        path = inputs / (name + ".json")
        require(sha(path) == protocol["input_pins"][path.name]["sha256"], "decoded input pin differs: " + name)
        payload[name] = json.loads(path.read_text())
    row, profile = payload["profile-before"], payload["profile"]
    require(row["R"] == profile["R"] and row["total_M_operations"] == len(payload["word"]["ops"]), "context identity")
    output = args.output
    (output / "source/certificates").mkdir(parents=True)
    (output / "source/references/paired-cube/physical").mkdir(parents=True)
    (output / "export").mkdir()
    (output / "source/scripts").symlink_to(source / "scripts", target_is_directory=True)
    mapping = {"graph": "graph", "frames": "frames", "word": "selection"}
    for name, dest in mapping.items():
        (output / "export" / (dest + ".json")).write_bytes((inputs / (name + ".json")).read_bytes())
    files = {
        "source/certificates/paired-cube-complex-input.json": row,
        "source/certificates/paired-cube-physical-input.json": profile,
        "source/references/paired-cube/physical/frames.json": {"frames": payload["physical-frames"]},
        "source/references/paired-cube/physical/pairs.json": {"pairs": payload["physical-pairs"]},
    }
    for name, data in files.items():
        (output / name).write_text(json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n")
    record = {"status": "PIN_CHECKED_DERIVED_CONTEXT", "source_commit": args.source_commit,
              "source_repository": args.source_repository,
              "source_local_path": str(args.source), "input_local_path": str(args.input),
              "input_protocol_sha256": sha(inputs / "protocol.json"),
              "input_sha256": {name: protocol["input_pins"][name + ".json"]["sha256"] for name in payload},
              "source_sha256": {name: sha(source / name) for name in
                                ("scripts/paired_cube_physical.py", "scripts/paired_cube/frames.py")},
              "derived_sha256": {str(p.relative_to(output)): sha(p) for p in output.rglob("*.json")},
              "logical_roles": row["R"], "physical_roles": profile["physical_R"],
              "operation_count": len(payload["word"]["ops"]), "pairs": profile["pairs"],
              "scope": "Byte/pin-checked input layout only; producer, signed/reflected geometry, full moments and assembly are separate."}
    (output / "context.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    for p in output.rglob("*.json"):
        p.chmod(0o444)
    print(json.dumps({k: record[k] for k in ("status", "logical_roles", "physical_roles", "operation_count", "pairs")}))


if __name__ == "__main__":
    main()
