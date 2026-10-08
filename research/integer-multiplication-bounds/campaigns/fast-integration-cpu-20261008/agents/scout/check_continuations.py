#!/usr/bin/env python3
"""Independent product enumeration and majorization check of exported edges.

This does not import the coordinator's frontier or matching code. It establishes
a finite generic-profile claim for the supplied graph, not correctness or
completeness of the graph's upstream positive-label generation.
"""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
from itertools import product
import json
from pathlib import Path


def child_list(h, rank):
    assert 0 <= rank <= h
    if 2 * rank <= h:
        return [1] * rank
    return [1] * (h - rank) + [2 * rank - h]


def edge_profile(h, edge):
    ru, rv, rt = (edge[k] for k in ("ru", "rv", "rt"))
    assert rt >= ru >= rv >= 1
    profile = Counter()
    for rank in (h - ru, rv, rt - rv):
        for width in child_list(h, rank):
            profile[width] -= 1
    for width in child_list(h, rt - ru):
        profile[width] += 1
    assert sum(w * n for w, n in profile.items()) == -h
    return profile


def dominates(difference):
    # Positive counts are incumbent, negative counts are alternative.
    a = sorted([w for w, n in difference.items() for _ in range(max(0, n))], reverse=True)
    b = sorted([w for w, n in difference.items() for _ in range(max(0, -n))], reverse=True)
    assert sum(a) == sum(b)
    a += [0] * max(0, len(b) - len(a))
    b += [0] * max(0, len(a) - len(b))
    return all(sum(a[:k]) >= sum(b[:k]) for k in range(1, len(a) + 1))


def check(path, all_degrees=False):
    edges = [{k: int(v) for k, v in row.items()} for row in csv.DictReader(path.open())]
    h = json.loads(Path(str(path) + ".unmatched.json").read_text())["h"]
    baseline = {(int(r["donor"]), int(r["use"])) for r in csv.DictReader(Path(str(path) + ".selected.csv").open())}
    assert len({a for a, b in baseline}) == len(baseline)
    assert len({b for a, b in baseline}) == len(baseline)
    lookup = {(e["donor"], e["use"]): e for e in edges}
    assert len(lookup) == len(edges), "duplicate exported edge"
    assert baseline <= set(lookup)
    adjacency = defaultdict(set)
    for a, b in lookup:
        adjacency[(0, a)].add((1, b))
        adjacency[(1, b)].add((0, a))
    unseen = set(adjacency)
    summaries = []
    while unseen:
        seed = min(unseen)
        reachable = {seed}
        todo = [seed]
        while todo:
            node = todo.pop()
            for neighbor in adjacency[node] - reachable:
                reachable.add(neighbor)
                todo.append(neighbor)
        unseen -= reachable
        donors = sorted(v for side, v in reachable if side == 0)
        choices = [[None] + sorted(b for a, b in lookup if a == donor) for donor in donors]
        base = Counter()
        base_degree = 0
        for a, b in baseline:
            if a in donors:
                base_degree += 1
                base.update(edge_profile(h, lookup[a, b]))
        if all_degrees:
            base[h] -= base_degree
            base[23 * 25 - 2 * h] -= base_degree
            base[23 * 25] += base_degree
            assert sum(w * n for w, n in base.items()) == 0
        valid = []
        for selected in product(*choices):
            uses = [b for b in selected if b is not None]
            if len(set(uses)) == len(uses):
                valid.append(selected)
        maximum = max(sum(b is not None for b in x) for x in valid)
        assert sum(a in donors for a, b in baseline) == maximum
        maximizers = [x for x in valid if sum(b is not None for b in x) == maximum]
        profiles = set()
        for selected in (valid if all_degrees else maximizers):
            profile = Counter()
            degree = 0
            for donor, use in zip(donors, selected):
                if use is not None:
                    degree += 1
                    profile.update(edge_profile(h, lookup[donor, use]))
            if all_degrees:
                profile[h] -= degree
                profile[23 * 25 - 2 * h] -= degree
                profile[23 * 25] += degree
                assert sum(w * n for w, n in profile.items()) == 0
            profiles.add(tuple(sorted((w, n) for w, n in profile.items() if n)))
        nonidentical = 0
        for profile in profiles:
            difference = dict(base)
            for width, count in profile:
                difference[width] = difference.get(width, 0) - count
            difference = {w: n for w, n in difference.items() if n}
            assert dominates(difference), "incumbent fails majorization"
            nonidentical += bool(difference)
        summaries.append((len(valid), maximum, len(maximizers), len(profiles), nonidentical, len(donors)))
    return {
        "h": h, "edge_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "edges": len(edges), "components": len(summaries),
        "all_matchings": sum(x[0] for x in summaries),
        "maximum_cardinality": sum(x[1] for x in summaries),
        "sum_component_maximizer_counts": sum(x[2] for x in summaries),
        "sum_component_profile_counts": sum(x[3] for x in summaries),
        "nonidentical_baseline_majorized_profiles": sum(x[4] for x in summaries),
        "largest_donor_component": max(x[5] for x in summaries),
        "every_incumbent_component_maximal": True,
        "every_alternative_profile_majorized_by_incumbent": True,
        "all_cardinalities": all_degrees,
        "compared_quantity": "numerator minus W*m^tau" if all_degrees else "native inner moment at fixed cardinality",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("edges", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--all-degrees", action="store_true")
    args = parser.parse_args()
    result = {"method": "Cartesian-product matching enumeration, independent child lists and exact majorization", "results": [check(p, args.all_degrees) for p in args.edges]}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
