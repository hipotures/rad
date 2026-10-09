#!/usr/bin/env python3
"""Export one coherent alias/frame continuation on an unchanged finite word.

Copy the pinned producer graph, witness, literal word and logical record; take
the physical frames, pairs and complete profile together from one continuation.
Verify the continuation's explicit graph/word hashes before producing new pins.
The resulting input layout is compatible with prepare_context.py. It is a
provenance transformation, not an independent mathematical acceptance gate.
Prepared with OpenAI assistance.
"""
import argparse
import json
from pathlib import Path
import sys

from physical_search import require, sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-input", type=Path, required=True)
    parser.add_argument("--continuation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not sys.flags.optimize, "assertion-disabled execution is unsupported")
    require(not args.output.exists(), "alias input export already exists")
    base, continuation = args.base_input.resolve(), args.continuation.resolve()
    base_protocol = json.loads((base / "protocol.json").read_text())
    result = json.loads((continuation / "result.json").read_text())
    names = ("graph", "baseline", "frames", "word", "profile-before",
             "physical-frames", "physical-pairs", "profile")
    for name in names:
        path = base / (name + ".json")
        require(sha(path) == base_protocol["input_pins"][path.name]["sha256"],
                "base decoded pin differs: " + name)
    require(result["graph_sha256"] == sha(base / "graph.json"), "continuation graph differs")
    require(result["word_sha256"] == sha(base / "word.json"), "continuation literal word differs")
    changed = {"physical-frames", "physical-pairs", "profile"}
    origins = {name + ".json": str((continuation if name in changed else base) / (name + ".json"))
               for name in names}
    profile = json.loads((continuation / "profile.json").read_text())
    logical = json.loads((base / "profile-before.json").read_text())
    word = json.loads((base / "word.json").read_text())
    pairs = json.loads((continuation / "physical-pairs.json").read_text())
    require(profile["R"] == logical["R"] and logical["total_M_operations"] == len(word["ops"]),
            "continuation finite identity differs")
    require(profile["pairs"] == len(pairs) == result["pairs"], "continuation alias count differs")
    require(profile["W_per_vertex"] == result["W"] and profile["physical_R"] == result["physical_R"]
            and profile["rank_per_vertex"] == result["rank_mass"], "continuation profile/result differs")
    args.output.mkdir(parents=True)
    for filename, origin in origins.items():
        (args.output / filename).write_bytes(Path(origin).read_bytes())
    protocol = {"status": "COHERENT_PINNED_ALIAS_CONTINUATION_EXPORT",
                "base_input": str(args.base_input), "continuation": str(args.continuation),
                "base_protocol_sha256": sha(base / "protocol.json"),
                "continuation_result_sha256": sha(continuation / "result.json"),
                "continuation_scope": result["scope"],
                "input_pins": {filename: {"sha256": sha(args.output / filename),
                                          "bytes": (args.output / filename).stat().st_size,
                                          "origin": origin} for filename, origin in origins.items()},
                "scope": "Complete physical frames, pairs and profile are copied as one state on the unchanged pinned graph/word. Independent reflection, exact moments and assembly remain separate."}
    (args.output / "protocol.json").write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n")
    for path in args.output.glob("*.json"):
        path.chmod(0o444)
    print(json.dumps({"status": protocol["status"], "pairs": len(pairs),
                      "logical_roles": logical["R"], "physical_roles": profile["physical_R"],
                      "operation_count": len(word["ops"])}))


if __name__ == "__main__":
    main()
