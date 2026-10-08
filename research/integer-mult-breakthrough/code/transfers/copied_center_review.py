#!/usr/bin/env python3
"""Independent finite controls for copied centers and a side-DAG obstruction.

Exact Gaussian dyadics and serialized DAG inputs only. This auxiliary model
does not supply a full native compiler, primitive characteristic or precision
theorem. It imports no complex-track producer or historical implementation.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
import random
import time


ZERO = (Q(), Q())


def basis(values):
    pivots = {}
    for value in values:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return [pivots[p] for p in sorted(pivots, reverse=True)]


def in_span(value, rows):
    for row in basis(rows):
        if value >> (row.bit_length() - 1) & 1:
            value ^= row
    return value == 0


def dot(a, b):
    return (a & b).bit_count() % 2


def labels(h):
    return [sum(1 << i for i in s) for s in combinations(range(h), 5)]


def pair_projector(h, pair):
    if h % 2:
        raise ValueError("this independent explicit projector uses even h")
    full = (1 << h) - 1
    normals = [full ^ (1 << i) for i in pair]
    if len(normals) != 2 or any(dot(a, b) != int(i == j)
                              for i, a in enumerate(normals)
                              for j, b in enumerate(normals)):
        raise ValueError("pair complement is not the claimed orthonormal plane")
    columns = []
    for j in range(h):
        column = 1 << j
        for normal in normals:
            if normal >> j & 1:
                column ^= normal
        columns.append(column)
    return columns


def complement(columns):
    return [column ^ (1 << j) for j, column in enumerate(columns)]


def apply_binary(columns, value):
    output = 0
    for j, column in enumerate(columns):
        if value >> j & 1:
            output ^= column
    return output


def qphase(columns, value):
    total = 0
    for i in range(len(columns)):
        if value >> i & 1:
            total += (columns[i] >> i) & 1
            for j in range(i + 1, len(columns)):
                if value >> j & 1:
                    total += 2 * ((columns[j] >> i) & 1)
    return total % 4


def gaussian_i(value, power):
    a, b = value
    return [(a, b), (-b, a), (-a, -b), (b, -a)][power % 4]


def walsh(values):
    output = [list(packet) for packet in values]
    width, size = 1, len(values)
    while width < size:
        for start in range(0, size, 2 * width):
            for i in range(start, start + width):
                first, second = output[i], output[i + width]
                output[i] = [(a + c, b + d) for (a, b), (c, d) in zip(first, second)]
                output[i + width] = [(a - c, b - d) for (a, b), (c, d) in zip(first, second)]
        width *= 2
    return output


def phase_frame(values, columns, inverse=False):
    size = len(values)
    if size != 1 << len(columns):
        raise ValueError("complete selected address cube was lost")
    spectrum = walsh(values)
    phased = [[gaussian_i(value, (-1 if inverse else 1) * qphase(columns, i))
               for value in packet] for i, packet in enumerate(spectrum)]
    return [[(a / size, b / size) for a, b in packet] for packet in walsh(phased)]


def copy_case(task):
    kind, pair, seed = task
    h, channels = 8, 4
    started = time.monotonic()
    source_labels = labels(h)
    pair_mask = sum(1 << i for i in pair)
    if kind == "pair":
        columns = pair_projector(h, pair)
        support = [x for x in source_labels if x & pair_mask == pair_mask]
        expected_rank = h - 2
    else:
        columns = [1 << j for j in range(h)]
        support = [x for x in source_labels if x & pair_mask != pair_mask]
        expected_rank = h
    comp = complement(columns)
    full = [1 << j for j in range(h)]
    if len(basis(support)) != expected_rank or len(basis(columns)) != expected_rank:
        raise AssertionError("feature support/projector rank mismatch")
    if any(apply_binary(columns, x) != x for x in support):
        raise AssertionError("a source label is outside its feature frame")
    if any(apply_binary(columns, column) != column for column in columns):
        raise AssertionError("not an idempotent feature projector")
    if any((columns[j] >> i & 1) != (columns[i] >> j & 1)
           for i in range(h) for j in range(h)):
        raise AssertionError("not a symmetric feature projector")
    if len(basis(comp)) != h - expected_rank:
        raise AssertionError("complement rank mismatch")
    for address in range(1 << h):
        if (qphase(columns, address) + qphase(comp, address)) % 4 != address.bit_count() % 4:
            raise AssertionError("complement phase composition failed")
    rng = random.Random(seed)
    dirty = [[(Q(rng.randrange(-7, 8), 1 << rng.randrange(4)),
               Q(rng.randrange(-7, 8), 1 << rng.randrange(4)))
              for _ in range(channels)] for _ in range(1 << h)]
    original_u = phase_frame(dirty, columns)
    old_forward_reads = phase_frame(original_u, columns, inverse=True)
    old_forward_end = phase_frame(old_forward_reads, full)
    complete_copy = [list(packet) for packet in original_u]
    new_forward_reads = phase_frame(complete_copy, columns, inverse=True)
    new_forward_end = phase_frame(original_u, comp)
    if old_forward_reads != dirty or new_forward_reads != dirty or new_forward_end != old_forward_end:
        raise AssertionError("forward complete-copy program failed")
    # Erasure is a complete stream write, not another uncharged transform.
    erased = [[ZERO] * channels for _ in complete_copy]
    if any(value != ZERO for packet in erased for value in packet):
        raise AssertionError("complete temporary erasure failed")
    old_reverse_reads = phase_frame(dirty, full)
    old_reverse_end = phase_frame(old_reverse_reads, columns, inverse=True)
    new_reverse_end = phase_frame(dirty, comp)
    reverse_copy = [list(packet) for packet in new_reverse_end]
    new_reverse_reads = phase_frame(reverse_copy, columns)
    if old_reverse_reads != new_reverse_reads or old_reverse_end != new_reverse_end:
        raise AssertionError("reverse complementary complete-copy program failed")
    if phase_frame(new_reverse_end, comp, inverse=True) != dirty:
        raise AssertionError("logical dirty values did not restore under their correct endpoint frame")
    if original_u == dirty:
        raise AssertionError("the missing-copy-transform negative did not discriminate")
    cropped = [[packet[0]] + [ZERO] * (channels - 1) for packet in original_u]
    if phase_frame(cropped, columns, inverse=True) == dirty:
        raise AssertionError("the cropped complete-payload negative did not discriminate")
    return {"kind": kind, "pair": list(pair), "h": h, "channels_per_record": channels,
            "complete_records": len(dirty), "seed": seed,
            "copy_rank": expected_rank, "original_direct_rank": h - expected_rank,
            "new_return_rank_mass": h, "old_return_rank_mass": h + expected_rank,
            "stream_copy_fields_per_orientation": len(dirty) * channels,
            "stream_erase_fields_per_orientation": len(dirty) * channels,
            "missing_transform_rejected": True, "cropped_copy_rejected": True,
            "seconds": time.monotonic() - started,
            "scope": "Canonical exact binary quadratic-phase auxiliary arrays; not the actual Gauss compiler or full native multiplier."}


def scalar_denominator_control():
    h, target = 10, frozenset(range(5))
    replacements = [frozenset((0, 5)), frozenset((6, 7))]
    pairs = [frozenset(pair) for pair in combinations(range(h), 2)]
    def alpha(pair):
        return Q(int(pair <= target), 4) - Q(3 * len(pair & target), 32)
    gamma = Q(3, 8) + sum((alpha(pair) for pair in replacements), Q())
    coefficients = {tuple(sorted(pair)): ((-1 if pair in replacements else 1) *
                    (alpha(pair) + gamma / 8)) for pair in pairs}
    if coefficients[(8, 9)] != Q(9, 256):
        raise AssertionError("eight-bit dyadic denominator witness failed")
    for source_tuple in combinations(range(h), 5):
        source = frozenset(source_tuple)
        total = sum((coefficient * (1 - int(frozenset(pair) <= source)
                                  if frozenset(pair) in replacements
                                  else int(frozenset(pair) <= source))
                     for pair, coefficient in coefficients.items()), Q())
        intersection = len(source & target)
        if total != Q((intersection - 1) * (intersection - 3), 8):
            raise AssertionError("independent substituted central map failed")
    return {"h": h, "target": sorted(target),
            "replaced_pairs": [sorted(pair) for pair in replacements],
            "witness_unreplaced_pair": [8, 9], "coefficient": "9/256",
            "required_denominator_bits": 8, "legacy_seven_bit_allowance_valid": False,
            "checked_source_columns": comb(h, 5),
            "local_center_loss": comb(h, 2) * (h - 2) + 4}


def graph_witness(fixture):
    h, inputs, args = fixture["h"], fixture["input_labels"], fixture["args"]
    if h != 8 or len(set(inputs)) != len(inputs) or any(x.bit_count() != 5 for x in inputs):
        raise ValueError("invalid weighted source family")
    leaves = {row["node"]: row for row in fixture["leaf_inputs"]}
    support, values = [0] * len(args), [None] * len(args)
    for node in range(1, len(args)):
        if args[node] is None:
            leaf = leaves[node]
            index, coefficient = leaf["source_index"], leaf["coefficient"]
            if not 0 <= index < len(inputs) or coefficient not in (-3, 1):
                raise ValueError("invalid weighted source leaf")
            support[node] = 1 << index
            values[node] = {index: coefficient}
        else:
            a, b = args[node]
            if not 0 < a < node or not 0 < b < node or support[a] & support[b]:
                raise ValueError("DAG is not a disjoint-support chronological addition")
            support[node] = support[a] | support[b]
            values[node] = dict(values[a], **{})
            values[node].update(values[b])
    downstream = [set() for _ in args]
    for output in fixture["outputs"]:
        target, root = output["target_label"], output["node"]
        if target not in inputs or not 0 < root < len(args):
            raise ValueError("invalid designated target")
        for i, source in enumerate(inputs):
            intersection = (source & target).bit_count()
            wanted = (-3 if intersection in (0, 4) else 1 if intersection == 2 else 0)
            if values[root].get(i, 0) != wanted:
                raise ValueError("serialized scalar DAG has an incorrect weighted output")
        stack, seen = [root], set()
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            downstream[node].add(target)
            if args[node] is not None:
                stack.extend(args[node])
    witness = fixture["witness"]
    node, value = witness["node"], witness["nonzero_forbidden_vector"]
    source_span = basis([source for i, source in enumerate(inputs) if support[node] >> i & 1])
    target_span = basis(downstream[node])
    if not value or not in_span(value, source_span) or not in_span(value, target_span):
        raise ValueError("forbidden vector is not in the actual source/target spans")
    if any(dot(value, target) for target in target_span):
        raise ValueError("forbidden vector is not in the actual target radical")
    if any(dot(source, target) for source in source_span for target in target_span):
        raise ValueError("source support is not in every downstream target kernel")
    for key, rows in [("input_span_basis", source_span), ("downstream_target_span_basis", target_span)]:
        claimed = witness[key]
        if len(basis(claimed)) != len(rows) or any(not in_span(row, rows) for row in claimed):
            raise ValueError("reported basis does not match independently reconstructed span")
    return {"h": h, "node": node, "forbidden_vector": value,
            "actual_source_span_basis": source_span, "actual_target_span_basis": target_span,
            "verified_source_membership": True, "verified_target_radical_membership": True,
            "independent_weighted_output_entries": len(inputs) * len(fixture["outputs"]),
            "common_kernel_dimension": h - len(target_span),
            "scope": "This serialized weighted DAG with nested nondegenerate source/target frames only; arbitrary quadratic frames and copied common-background schedules are outside this premise."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path,
                        default=Path(__file__).resolve().parents[2] / "fixtures/transfers/weighted-tree-h8-frame-witness.json")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("positive workers required")
    if args.output is not None and args.output.exists():
        parser.error("output must be fresh")
    start = time.monotonic()
    fixture = json.loads(args.fixture.read_text())
    graph = graph_witness(fixture)
    corrupted = json.loads(json.dumps(fixture))
    corrupted["witness"]["nonzero_forbidden_vector"] = 0
    try:
        graph_witness(corrupted)
    except ValueError:
        graph["zero_witness_rejected"] = True
    else:
        raise AssertionError("corrupt radical witness was accepted")
    tasks = [("pair", (0, 1), 2026100821), ("pair", (2, 3), 2026100822),
             ("complement", (0, 1), 2026100823), ("complement", (2, 3), 2026100824)]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        copies = list(pool.map(copy_case, tasks))
    result = {"status": "INDEPENDENT_EXACT_FINITE_COMPONENT_REVIEW",
              "recorded_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Copied-center auxiliary phase identities, exact scalar denominator obligation, and one actual scalar DAG radical witness; no complete new primitive or exponent.",
              "copy_controls": copies, "scalar_denominator": scalar_denominator_control(),
              "side_dag_obstruction": graph, "workers": args.workers,
              "inputs": {str(args.fixture): {"bytes": args.fixture.stat().st_size,
                          "sha256": hashlib.sha256(args.fixture.read_bytes()).hexdigest()},
                         str(Path(__file__)): {"bytes": Path(__file__).stat().st_size,
                          "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}},
              "seconds": time.monotonic() - start}
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "workers": args.workers,
                      "copied_complete_records": sum(x["complete_records"] for x in copies),
                      "scatter_coefficient_witness": result["scalar_denominator"]["coefficient"],
                      "radical_witness": graph["forbidden_vector"], "seconds": result["seconds"]}))


if __name__ == "__main__":
    main()
