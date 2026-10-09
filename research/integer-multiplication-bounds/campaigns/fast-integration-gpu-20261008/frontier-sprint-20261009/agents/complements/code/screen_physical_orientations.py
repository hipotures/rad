#!/usr/bin/env python3
"""Enumerate legal equal-rank quotient lines, followed by fixed endpoint descent.

The paired-cube physical compiler permits general Clifford frames. These
orientations therefore do not assert the obsolete nondegenerate-projector
condition. Exact value containment and every role/pair chain are checked.
Numerical moments are discovery scores, never final kappa.
Prepared with OpenAI assistance; inherited compiler attribution is unchanged.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import resource
import time


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def load_search(path):
    spec = importlib.util.spec_from_file_location("orientation_physical_search", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(job):
    source, export, search, output, orientation, passes, trial, group = job
    output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    module = load_search(search)
    model = module.Physical(source, export, trial)
    lower, upper, _, _ = model.endpoints(group)
    old = model.frames[group[0]]
    quotient = []
    accumulated = lower
    for vector in upper:
        extended = model.basis(accumulated + (vector,))
        if len(extended) > len(accumulated):
            quotient.append(vector)
            accumulated = extended
    module.require(len(quotient) == 2 and len(old) == len(lower) + 1,
                   "expected a two-dimensional quotient and one-dimensional extension")
    choices = sorted({model.basis(lower + (vector,)) for vector in
                      (quotient[0], quotient[1], quotient[0] ^ quotient[1])})
    module.require(len(choices) == 3 and old in choices, "quotient-line enumeration")
    choices = [old] + [frame for frame in choices if frame != old]
    selected = choices[orientation]
    for index in group:
        model.frames[index] = selected
    before = model.validate()
    initial_histogram = model.histogram()
    module.require(initial_histogram == model.initial_histogram,
                   "equal-rank orientation changed the initial complete histogram")
    write(output / "orientation.json", {"group": group, "lower": lower, "upper": upper,
        "original": old, "selected": selected, "quotient_generators": quotient,
        "all_three_choices": choices, "exact_geometry": before})
    moves, pass_records = [], []
    for iteration in range(passes):
        groups = model.groups("components", random.Random(20261009))
        if iteration % 2:
            groups.reverse()
        count = len(moves)
        for component in groups:
            if len({model.frames[index] for index in component}) != 1:
                continue
            change = model.change(component)
            if change:
                moves.append(change)
        pass_records.append({"pass": iteration, "groups": len(groups),
                             "accepted_moves": len(moves) - count})
        print(json.dumps({"orientation": orientation, **pass_records[-1]}), flush=True)
        if len(moves) == count:
            break
    checks = model.validate()
    histogram = model.histogram()
    changed = [[index, list(frame)] for index, frame in enumerate(model.frames)
               if frame != model.original[index]]
    write(output / "frames.json", changed)
    write(output / "moves.json", moves)
    replay = model.compiler.physical(model.g, model.witness, model.word, model.record,
                                     changed, model.pairs)
    module.require({int(rank): count for rank, count in replay["child_histogram"].items()}
                   == histogram, "independent complete ledger disagrees with physical compiler")
    write(output / "physical-profile.json", replay)
    result = {"status": "DISCOVERY", "orientation": orientation, "passes": pass_records,
        "moves": len(moves), "changed_frames_from_public": sum(a != b for a, b in
             zip(model.frames, model.initial)), "frames_sha256": digest(output / "frames.json"),
        "histogram": histogram, "moments": model.moments(histogram),
        "control_moments": model.moments(model.initial_histogram), "checks": checks,
        "upstream_physical_replay": replay["scalar_replay"],
        "wall_seconds": time.monotonic() - start,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "exclusions": ["independent reflected audit", "rigorous moment enclosure",
                       "assembly certificate", "accepted final kappa"]}
    write(output / "result.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--export", type=Path, required=True)
    parser.add_argument("--placement-code", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--passes", type=int, default=3)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--trial", type=float, default=5885669 / 10**10)
    args = parser.parse_args()
    if args.output.exists() or args.summary.exists():
        raise ValueError("attempt/summary already exists")
    args.output.mkdir(parents=True)
    group = [19964, 19965, 19966]
    jobs = [(args.source.resolve(), args.export.resolve(), args.placement_code.resolve(),
             args.output.resolve() / f"orientation-{i}", i, args.passes, args.trial, group)
            for i in range(3)]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(run, jobs))
    write(args.summary, {"status": "DISCOVERY", "source_pin":
        "d14e29157bc905be1ced0776dd893d0714013f3a", "source_repository":
        "https://github.com/CrocSwap/integer-mult-bounds", "workers": args.workers,
        "passes": args.passes, "group": group,
        "placement_code_sha256": digest(args.placement_code),
        "harness_sha256": digest(Path(__file__)),
        "export_sha256": {name: digest(args.export / name) for name in
                          ("graph.json", "frames.json", "selection.json")},
        "orientations": [json.loads((job[3] / "orientation.json").read_text()) for job in jobs],
        "results": results})


if __name__ == "__main__":
    main()
