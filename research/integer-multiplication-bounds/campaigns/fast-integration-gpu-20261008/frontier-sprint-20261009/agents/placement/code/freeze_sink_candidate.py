#!/usr/bin/env python3
"""Freeze one coherent eight-file body bundle plus actual sink list/profile.

This verifies recorded input identities and complete paid recount consistency,
then preserves exact bytes. It does not rerun mathematics already recorded by
the candidate or assign a rigorous moment/assembly certificate. Prepared with
OpenAI assistance; inherited source attribution is in physical_sinks.py.
"""
import argparse
import json
from pathlib import Path
import sys

from physical_search import require, sha


def main():
    parser = argparse.ArgumentParser()
    for name in ("base-input", "sink-input", "candidate", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    require(not sys.flags.optimize, "assertion-disabled execution is unsupported")
    require(not args.output.exists(), "frozen sink candidate export already exists")
    base, sink, candidate = [p.resolve() for p in (args.base_input, args.sink_input, args.candidate)]
    base_protocol = json.loads((base / "protocol.json").read_text())
    sink_protocol = json.loads((sink / "protocol.json").read_text())
    result = json.loads((candidate / "result.json").read_text())
    names = ("graph", "baseline", "frames", "word", "profile-before",
             "physical-frames", "physical-pairs", "profile")
    require(result["source_context"]["source_commit"] == sink_protocol["source_head"], "body/sink heads differ")
    require(sha(sink / "protocol.json") == result["sink_pins"]["protocol"], "sink protocol differs")
    for name in names:
        path = base / (name + ".json")
        digest = sha(path)
        require(digest == base_protocol["input_pins"][path.name]["sha256"] ==
                sink_protocol["body_input_pins"][path.name]["sha256"], "base decoded pin differs: " + name)
        if name != "baseline":
            require(digest == result["source_context"]["input_sha256"][name], "candidate input differs: " + name)
    require(sha(sink / "sinks.json") == result["sink_pins"]["sinks"] ==
            sink_protocol["input_pins"]["sinks.json"]["sha256"], "sink list differs")
    require(sha(sink / "profile.json") == result["sink_pins"]["reference"], "sink reference differs")
    require(result["frames_sha256"] == sha(candidate / "frames.json"), "candidate frame pin differs")
    require(result["full_body_and_sink_replay"] is True, "candidate lacks complete body and sink replay")
    body = json.loads((candidate / "body-profile.json").read_text())
    physical = json.loads((candidate / "sink-profile.json").read_text())
    sinks = json.loads((sink / "sinks.json").read_text())
    require(physical["child_histogram"] == result["histogram"], "candidate complete sink histogram differs")
    require(physical["W_per_vertex"] == result["W_per_vertex"] == result["literal_registers"] and
            physical["rank_per_vertex"] == result["rank_per_vertex"], "candidate rank/width differs")
    require(physical["sink_substitution"]["sinks"] == sinks and
            physical["sinks"] == len(sinks) == result["sinks"], "candidate sink state differs")
    require(body["R"] == physical["R"] == result["source_context"]["logical_roles"] and
            body["pairs"] == physical["pairs"] == result["source_context"]["pairs"], "body/sink identity differs")
    require(body["physical_R"] - len(sinks) == physical["physical_R"] == result["physical_roles"] and
            body["W_per_vertex"] - len(sinks) == physical["W_per_vertex"], "sink register removal differs")
    origins = {name + ".json": base / (name + ".json") for name in names}
    origins.update({"physical-frames.json": candidate / "frames.json",
                    "profile.json": candidate / "body-profile.json",
                    "sinks.json": sink / "sinks.json",
                    "sink-profile.json": candidate / "sink-profile.json"})
    args.output.mkdir(parents=True)
    for filename, origin in origins.items():
        (args.output / filename).write_bytes(origin.read_bytes())
    protocol = {"status": "IMMUTABLE_DISCOVERY_COMPLETE_SINK_EXPORT",
                "base_input": str(args.base_input), "sink_input": str(args.sink_input),
                "candidate": str(args.candidate), "source_context": result["source_context"],
                "base_protocol_sha256": sha(base / "protocol.json"),
                "sink_protocol_sha256": sha(sink / "protocol.json"),
                "candidate_result_sha256": sha(candidate / "result.json"),
                "candidate_context_sha256": result["context_sha256"],
                "search_sha256": result["search_sha256"], "sink_source_pins": sink_protocol["source_pins"],
                "trial_exact": result["trial_exact"], "native_discovery_moments": result["moments"],
                "input_pins": {filename: {"sha256": sha(args.output / filename),
                                          "bytes": (args.output / filename).stat().st_size,
                                          "origin": str(origin)} for filename, origin in origins.items()},
                "scope": "One fixed producer/gauge/alias/word/sink topology with explicit moved frames and both complete body and actual sink paid profiles. Independent signed/reflected review, rigorous moments and final assembly acceptance remain separate."}
    (args.output / "protocol.json").write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n")
    for path in args.output.glob("*.json"):
        path.chmod(0o444)
    for path in candidate.glob("*.json"):
        path.chmod(0o444)
    print(json.dumps({"status": protocol["status"], "frames_sha256": result["frames_sha256"],
                      "sink_profile_sha256": sha(args.output / "sink-profile.json"),
                      "pairs_sha256": sha(args.output / "physical-pairs.json"),
                      "discovery_complex_root": result["moments"]["discovery_complex_root"]}))


if __name__ == "__main__":
    main()
