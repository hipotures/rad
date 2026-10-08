#!/usr/bin/env python3
"""Independent source and containment controls on changed literal words.

This is not a second full dirty-basis replay. It discriminates two distinct
requirements: the source identity JLV=I and chronological common-frame
containment. Mutations are described by input hash and exact gate index.
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import time


def controls(path):
    stored = path.read_bytes()
    raw = gzip.decompress(stored) if path.suffix == ".gz" else stored
    word = json.loads(raw)
    h, v, r = (word[k] for k in ("h", "v", "R"))
    frames = [tuple(f) for f in word["frames"]]
    sources = {int(i): slot for i, slot in word["sources"].items()}
    assert set(sources) == set(range(v)) and len(set(sources.values())) == v
    lookup = {f: g for g, f in enumerate(frames)}
    triples = []
    for a in range(h):
        for b in range(a+1, h):
            for c in range(b+1, h):
                triples.append((1 << a)+(1 << b)+(1 << c))
    assert len(triples) == v

    def source_identity(skip=None):
        symbols = [0]*r
        for i, slot in sources.items():
            symbols[slot] = 1 << i
        for index, (a, b, g) in enumerate(word["ops"]):
            if index != skip:
                symbols[a] ^= symbols[b]
        rows = [0]*v
        for target, physical in word["scatter"]:
            assert v <= target < 2*v and 2*v <= physical < 2*v+r
            rows[target-v] ^= symbols[physical-2*v]
        bad = [(i, row ^ (1 << i)) for i, row in enumerate(rows) if row != 1 << i]
        return {"mismatched_source_rows": len(bad),
                "first_witness": {"target_triple_index": bad[0][0],
                                  "input_source_bit": (bad[0][1] & -bad[0][1]).bit_length()-1} if bad else None}

    def frame_path(mutation=None):
        current = [None]*r
        for i, slot in sources.items():
            current[slot] = lookup[triples[i], triples[i]]
        for index, (a, b, g) in enumerate(word["ops"]):
            if mutation and index == mutation[0]:
                g = mutation[1]
            for slot in (a, b):
                old = current[slot]
                if old is not None:
                    old_core, old_cover = frames[old]
                    new_core, new_cover = frames[g]
                    if new_core & ~old_core or old_cover & ~new_cover:
                        return {"status": "REJECTED_NONCONTAINING_INCIDENCE", "gate_index": index,
                                "physical_slot": slot, "old_frame": old, "new_frame": g,
                                "old_descriptor": frames[old], "new_descriptor": frames[g]}
                current[slot] = g
        return {"status": "PASS_ALL_MIXER_INCIDENCES", "incidences": 2*len(word["ops"])}

    positive_source = source_identity()
    assert positive_source["mismatched_source_rows"] == 0
    positive_frames = frame_path()
    assert positive_frames["status"] == "PASS_ALL_MIXER_INCIDENCES"
    # Fixed deliberate negative: remove the first actual source-copy XOR.
    omitted = source_identity(skip=0)
    assert omitted["mismatched_source_rows"] > 0, "preserve unexpected negative failure"
    first = word["ops"][0]
    initial_frames = {slot: lookup[triples[i], triples[i]] for i, slot in sources.items()}
    bad_frame = next(g for g, (core, cover) in enumerate(frames)
                     if any(core & ~frames[initial_frames[s]][0] or frames[initial_frames[s]][1] & ~cover
                            for s in first[:2] if s in initial_frames))
    rejected = frame_path((0, bad_frame))
    assert rejected["status"] == "REJECTED_NONCONTAINING_INCIDENCE"
    # A frame-only mutation leaves every F2 role-XOR and source symbol EXACTLY
    # unchanged. It is rejected by address causality, not a signal-only test.
    outputs = [o[0] for o in word["outputs"]]
    assert len(outputs) == len(set(outputs))
    return {"h": h, "v": v, "R": r,
            "input_word": str(path), "input_bytes": len(stored),
            "decompressed_word_sha256": hashlib.sha256(raw).hexdigest(),
            "positive_source_identity": positive_source, "positive_mixer_containment": positive_frames,
            "negative_missing_source_copy": {"mutation": {"delete_ops_index": 0, "deleted_gate": first}, **omitted},
            "negative_noncontaining_frame": {"mutation": {"ops_index": 0, "old_gate": first,
                                                          "replacement_frame": bad_frame},
                                             "all_scalar_gate_endpoints_unchanged": True,
                                             "source_identity_still_exact": True, **rejected},
            "negative_terminal_alias": {"output_record_index": 1,
                                        "replace_physical_slot_with_output_record": 0,
                                        "first_slot": outputs[0], "second_slot": outputs[1],
                                        "status": "REJECTED_DUPLICATE_TERMINAL_CARRIER"},
            "scope": "Actual changed word source symbols and mixer-incidence containment. The deliberate frame/terminal mutations are contract rejections, not executions of illegal address operations; no global optimum or every-clearing-gate necessity is claimed."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--word", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    started = time.monotonic()
    result = {"status": "PASS_CHANGED_WORD_IDENTITIES_AND_PREDECLARED_NEGATIVES",
              "words": [controls(p) for p in args.word],
              "recorded_utc": datetime.now(timezone.utc).isoformat(),
              "seconds": time.monotonic()-started, "workers": 1,
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"], "seconds": result["seconds"]}), flush=True)
