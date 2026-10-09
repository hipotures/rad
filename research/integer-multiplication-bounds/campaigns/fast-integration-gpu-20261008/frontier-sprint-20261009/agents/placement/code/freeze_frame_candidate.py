#!/usr/bin/env python3
"""Freeze one fully priced frame candidate with its coherent input bundle.

The graph, witness, literal word, gauges, aliases and scalar ledger are copied
unchanged. Only the physical frame list and its freshly recounted profile are
replaced together. This copies bytes and verifies provenance; mathematical
geometry, rigorous moment and assembly acceptance belong to independent lanes.
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
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not sys.flags.optimize, "assertion-disabled execution is unsupported")
    require(not args.output.exists(), "frozen candidate export already exists")
    base, candidate = args.base_input.resolve(), args.candidate.resolve()
    base_protocol = json.loads((base / "protocol.json").read_text())
    result = json.loads((candidate / "result.json").read_text())
    names = ("graph", "baseline", "frames", "word", "profile-before",
             "physical-frames", "physical-pairs", "profile")
    for name in names:
        path = base / (name + ".json")
        require(sha(path) == base_protocol["input_pins"][path.name]["sha256"],
                "base decoded pin differs: " + name)
        if name != "baseline":
            require(sha(path) == result["source_context"]["input_sha256"][name],
                    "candidate input identity differs: " + name)
    require(result["frames_sha256"] == sha(candidate / "frames.json"), "candidate frame pin differs")
    require(result["upstream_physical_replay"] is True, "candidate lacks complete physical replay")
    profile = json.loads((candidate / "physical-profile.json").read_text())
    require(profile["child_histogram"] == result["histogram"], "candidate complete histogram differs")
    require(profile["W_per_vertex"] == result["W_per_vertex"]
            and profile["rank_per_vertex"] == result["rank_per_vertex"], "candidate rank/width differs")
    origins = {name + ".json": str(base / (name + ".json")) for name in names}
    origins.update({"physical-frames.json": str(candidate / "frames.json"),
                    "profile.json": str(candidate / "physical-profile.json")})
    args.output.mkdir(parents=True)
    for filename, origin in origins.items():
        (args.output / filename).write_bytes(Path(origin).read_bytes())
    protocol = {"status": "IMMUTABLE_DISCOVERY_FRAME_EXPORT",
                "base_input": str(args.base_input), "candidate": str(args.candidate),
                "base_protocol_sha256": sha(base / "protocol.json"),
                "candidate_result_sha256": sha(candidate / "result.json"),
                "candidate_context_sha256": result["context_sha256"],
                "source_context": result["source_context"],
                "search_sha256": result["search_sha256"],
                "trial_exact": result["trial_exact"],
                "input_pins": {filename: {"sha256": sha(args.output / filename),
                                          "bytes": (args.output / filename).stat().st_size,
                                          "origin": origin} for filename, origin in origins.items()},
                "scope": "Complete unchanged producer/word/gauges/aliases plus one explicit frame plan and full paid recount. Independent signed/reflected geometry, rigorous moments, assembly and accepted final kappa are separate."}
    (args.output / "protocol.json").write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n")
    for path in args.output.glob("*.json"):
        path.chmod(0o444)
    for path in candidate.glob("*.json"):
        path.chmod(0o444)
    print(json.dumps({"status": protocol["status"], "frames_sha256": result["frames_sha256"],
                      "profile_sha256": sha(args.output / "profile.json"),
                      "pairs_sha256": sha(args.output / "physical-pairs.json"),
                      "discovery_complex_root": result["moments"]["discovery_complex_root"]}))


if __name__ == "__main__":
    main()
