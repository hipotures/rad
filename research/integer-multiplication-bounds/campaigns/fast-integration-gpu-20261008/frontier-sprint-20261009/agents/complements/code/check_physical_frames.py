#!/usr/bin/env python3
"""Independent exact F2 frame inclusion and complemented-edge checks.

The chronology is imported from the pinned physical search model; elimination,
orthogonal complementation, rank and all mathematical verdicts below are fresh
standard-library calculations. This is a scoped geometric check, not a full
signed/reflected literal-word or all-size transfer proof.
"""
import argparse
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time


def need(value, message):
    if not value:
        raise ValueError(message)


@lru_cache(maxsize=150000)
def echelon(rows):
    pivots = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


@lru_cache(maxsize=150000)
def inside(A, B):
    rows = echelon(B)
    for value in A:
        for row in rows:
            if value & (1 << (row.bit_length() - 1)):
                value ^= row
        if value:
            return False
    return True


@lru_cache(maxsize=100000)
def orthogonal(rows, dimension):
    rows = echelon(rows)
    pivots = {row.bit_length() - 1 for row in rows}
    result = []
    for free in range(dimension):
        if free in pivots:
            continue
        value = 1 << free
        for row in reversed(rows):
            pivot = row.bit_length() - 1
            if (value & row).bit_count() % 2:
                value ^= 1 << pivot
        result.append(value)
    return echelon(tuple(result))


def load(path):
    spec = importlib.util.spec_from_file_location("frame_search", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical(rows):
    reduced = list(echelon(rows))
    for position in range(len(reduced) - 1, -1, -1):
        row = reduced[position]
        pivot = 1 << (row.bit_length() - 1)
        for earlier in range(position):
            if reduced[earlier] & pivot:
                reduced[earlier] ^= row
    return tuple(reduced)


def check(model, frames, complement_override=None):
    h = model.h
    for frame in frames + model.fixed:
        need(all(type(row) is int and 0 < row < (1 << h) for row in frame), "frame coordinate range")
        need(len(echelon(frame)) == len(frame), "frame independent rows")
    spans = []
    for index, operands in enumerate(model.g["args"]):
        spans.append((model.g["inputs"][index],) if operands is None else
                     echelon(spans[operands[0]] + spans[operands[1]]))
    def frame(index):
        return frames[index] if index >= 0 else model.fixed[-index - 1]
    reflected = {}
    for index in set(index for edge in model.edges for index in edge):
        F = frame(index)
        G = orthogonal(F, h)
        need(len(G) + len(F) == h and inside(orthogonal(G, h), F), "double complement")
        reflected[index] = G
    if complement_override is not None:
        index, replacement = complement_override
        reflected[index] = replacement
    for index, (_, _, node) in enumerate(model.ops):
        need(inside(spans[node - 1], frames[index]), "value span outside actual frame")
    for a, b in model.edges:
        need(inside(frame(a), frame(b)), "forward role/pair chain inclusion")
        need(inside(reflected[b], reflected[a]), "reflected complemented chain inclusion")
        need(len(frame(b)) - len(frame(a)) == len(reflected[a]) - len(reflected[b]),
             "reflected transition rank binding")
    return {"operation_value_containments": len(frames), "forward_chain_edges": len(model.edges),
            "reflected_complemented_edges": len(model.edges), "arithmetic": "independent exact F2 elimination"}


def main():
    parser = argparse.ArgumentParser()
    for name in ("source", "export", "placement-code", "frames", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    need(not sys.flags.optimize, "assertion-disabled execution rejected")
    need(not args.output.exists(), "output already exists")
    started = time.monotonic()
    model = load(args.placement_code).Physical(args.source.resolve(), args.export.resolve(), 0.0005885669)
    payload = json.loads(args.frames.read_text())
    def apply(entries):
        result = list(model.original)
        seen = set()
        for index, rows in entries:
            need(type(index) is int and 0 <= index < len(result), "illegal operation index")
            rows = tuple(rows)
            need(index not in seen and canonical(rows) == rows and rows != model.original[index],
                 "duplicate, noncanonical or unmoved frame")
            result[index] = rows
            seen.add(index)
        return result
    frames = apply(payload)
    result = check(model, frames)
    controls = {}
    multiple_rows = next(entry for entry in payload if len(entry[1]) > 1)
    tests = {
        "negative_index": lambda: apply([[-1, [1]]]),
        "noncanonical_rows": lambda: apply([[multiple_rows[0], list(reversed(multiple_rows[1]))]]),
        "bad_value_frame": lambda: check(model, [()] + frames[1:]),
        "omitted_frame_complement": lambda: check(model, frames, (0, frames[0])),
    }
    for name, test in tests.items():
        try:
            test()
        except ValueError as error:
            controls[name] = str(error)
        else:
            raise ValueError("negative control accepted: " + name)
    result.update(status="PASS_EXACT_FRAME_GEOMETRY", negative_controls=controls,
        frames_sha256=hashlib.sha256(args.frames.read_bytes()).hexdigest(),
        elapsed_seconds=time.monotonic() - started,
        scope="Actual changed operation frames, every carrier and pair handoff, and exact reversed complemented edge ranks. "
              "Scalar signs/dirty restoration, target read chronology and global transfer require separate evidence.")
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
