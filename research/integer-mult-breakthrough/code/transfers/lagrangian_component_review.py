#!/usr/bin/env python3
"""Independent literal review of the four-incidence Lagrangian shear witness.

Only serialized candidate adapters are read. Gold matrices, complete payload
execution, unit phase accounting and all Lagrangian geometry are reconstructed
without importing any complex-track implementation. Native routing is paid
conditionally by the stated binary primitives, not by this array timing.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
from itertools import combinations
import json
from pathlib import Path
import random
import time


ZERO = (Q(), Q())
ONE = (Q(1), Q())


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def rotate(value, power):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[power % 4]


def dot(a, b):
    return (a & b).bit_count() % 2


def span(vectors):
    values = {0}
    for v in vectors:
        values |= {w ^ v for w in tuple(values)}
    return frozenset(values)


def embed(columns, value):
    return sum_xor(column for j, column in enumerate(columns) if value >> j & 1)


def sum_xor(values):
    result = 0
    for value in values:
        result ^= value
    return result


def symmetric(code):
    columns, bit = [0] * 3, 0
    for i in range(3):
        for j in range(i, 3):
            if code >> bit & 1:
                columns[i] |= 1 << j
                columns[j] |= 1 << i
            bit += 1
    return columns


def graph_operator(code):
    columns = symmetric(code)
    q = []
    for x in range(8):
        value = sum((columns[i] >> i & 1) for i in range(3) if x >> i & 1)
        value += 2 * sum((columns[j] >> i & 1) for i in range(3)
                         for j in range(i + 1, 3) if x >> i & 1 and x >> j & 1)
        q.append(value % 4)
    kernel = []
    for s in range(8):
        value = ZERO
        for x in range(8):
            value = add(value, rotate(ONE, q[x] + 2 * dot(x, s)))
        kernel.append((value[0] / 8, value[1] / 8))
    return [[kernel[a ^ b] for b in range(8)] for a in range(8)]


def adjoint(matrix):
    return [[(matrix[b][a][0], -matrix[b][a][1]) for b in range(8)] for a in range(8)]


def compose(a, b):
    output = [[ZERO] * 8 for _ in range(8)]
    for y in range(8):
        for x in range(8):
            for k in range(8):
                output[y][x] = add(output[y][x], mul(a[y][k], b[k][x]))
    return output


def dyadic_hadamard_bit_two():
    g = (Q(1, 2), Q(1, 2))
    return [[rotate(g, 2 * int(bool(a & 4) and bool(b & 4)))
             if a & 3 == b & 3 else ZERO for b in range(8)] for a in range(8)]


def gold(fixture):
    frames = [graph_operator(code) for code in fixture["frame_codes"]]
    common = compose(frames[0], dyadic_hadamard_bit_two())
    if compose(common, adjoint(common)) != [[ONE if y == x else ZERO for x in range(8)] for y in range(8)]:
        raise AssertionError("the literal common Gaussian frame is not unitary")
    edges = [compose(common, adjoint(frames[0])), compose(common, adjoint(frames[1])),
             compose(frames[2], adjoint(common)), compose(frames[3], adjoint(common))]
    return frames, common, edges


def symplectic(a, b):
    return dot(a & 7, b >> 3) ^ dot(a >> 3, b & 7)


def geometry(fixture, common):
    # All 3D isotropic subspaces are enumerated through ordinary unordered
    # independent triples, rather than through the producer's generator BFS.
    lagrangians = set()
    for a, b, c in combinations(range(1, 64), 3):
        if c == a ^ b or symplectic(a, b) or symplectic(a, c) or symplectic(b, c):
            continue
        lagrangians.add(span((a, b, c)))
    if len(lagrangians) != 135:
        raise AssertionError("independent full Lagrangian enumeration failed")
    graphs = [span((1 << i) | (symmetric(code)[i] << 3) for i in range(3))
              for code in range(64)]
    endpoints = [graphs[code] for code in fixture["frame_codes"]]
    def distance(a, b):
        return 3 - (len(a & b).bit_length() - 1)
    cost = {candidate: sum(distance(candidate, endpoint) for endpoint in endpoints)
            for candidate in lagrangians}
    claimed = span(fixture["common_lagrangian_basis"])
    ranks = [distance(claimed, endpoint) for endpoint in endpoints]
    if min(cost.values()) != 5 or min(cost[g] for g in graphs) != 6 or ranks != [1, 1, 1, 2]:
        raise AssertionError("the four charged incidences do not reproduce rank5 versus6")
    if [candidate for candidate in lagrangians if cost[candidate] == 5] != [claimed]:
        raise AssertionError("the claimed full-chart minimizer is not unique")
    # Recover exact Pauli images from F^-1 Z_j F. This checks phases as well
    # as a graph-label convention; a finite metric minimum alone is weaker.
    pauli_images = []
    for bit in range(3):
        z = [[rotate(ONE, 2 * int(bool(x & (1 << bit)))) if y == x else ZERO
              for x in range(8)] for y in range(8)]
        image = compose(compose(adjoint(common), z), common)
        found = []
        for label in range(64):
            pz, px = label & 7, label >> 3
            for exponent in range(4):
                pauli = [[rotate(ONE, exponent + 2 * dot(pz, y)) if y == x ^ px else ZERO
                          for x in range(8)] for y in range(8)]
                if pauli == image:
                    found.append((label, exponent))
        if len(found) != 1:
            raise AssertionError("exact common-frame Pauli image is not a unique unit monomial")
        pauli_images.append(found[0])
    if span(label for label, _ in pauli_images) != claimed:
        raise AssertionError("literal common frame does not induce the claimed Lagrangian")
    return {"all_lagrangians": 135, "graph_candidates": 64,
            "full_minimum": 5, "graph_minimum": 6, "incident_ranks": ranks,
            "minimum_unique": True, "exact_pauli_images_label_and_i_exponent": pauli_images}


def selected_positions(f, k, rho):
    return [[slot * f * k + column * k + rho for slot in range(3)] for column in range(f)]


def coordinate(address, positions):
    return sum((address >> bit & 1) << i for i, bit in enumerate(positions))


def address_route(values, columns, affine, f, k, rho, inverse=False):
    mapping = [affine ^ embed(columns, i) for i in range(8)]
    if sorted(mapping) != list(range(8)):
        raise AssertionError("candidate adapter does not retain the full selected cube")
    if inverse:
        mapping = [mapping.index(i) for i in range(8)]
    positions = selected_positions(f, k, rho)
    active = sum(1 << bit for bits in positions for bit in bits)
    output = [None] * len(values)
    for old, packet in enumerate(values):
        new = old & ~active
        for bits in positions:
            mapped = mapping[coordinate(old, bits)]
            new |= sum((mapped >> slot & 1) << bit for slot, bit in enumerate(bits))
        output[new] = list(packet)
    if any(packet is None for packet in output):
        raise AssertionError("the complete adapter is not a bijection")
    return output


def phases(values, table, f, k, rho, sign=1, omit_repeated_constant=False):
    positions = selected_positions(f, k, rho)
    return [[rotate(value, sign * (sum(table[coordinate(a, bits)] for bits in positions)
                                   - ((f - 1) * table[0] if omit_repeated_constant else 0)))
             for value in packet] for a, packet in enumerate(values)]


def tensor_c(values, bits, inverse=False):
    output = [list(packet) for packet in values]
    if inverse:
        output = [[rotate(value, 2 * sum(a >> bit & 1 for bit in bits)) for value in packet]
                  for a, packet in enumerate(output)]
    for bit in bits:
        stride = 1 << bit
        for start in range(0, len(output), 2 * stride):
            for j in range(start, start + stride):
                forward, backward = [], []
                for (a, b), (c, d) in zip(output[j], output[j + stride]):
                    forward.append(((a - b + c + d) / 2, (a + b + d - c) / 2))
                    backward.append(((a + b + c - d) / 2, (b - a + c + d) / 2))
                output[j], output[j + stride] = forward, backward
    if inverse:
        output = [[rotate(value, -len(bits) + 2 * sum(a >> bit & 1 for bit in bits))
                   for value in packet] for a, packet in enumerate(output)]
    return output


def compiled_edge(values, nf, f, k, rho, inverse=False, omit_affine=False,
                  omit_repeated_constant=False):
    bits = [slot * f * k + column * k + rho for slot in range(nf["rank"]) for column in range(f)]
    affine = 0 if omit_affine else nf["output_affine_offset"]
    if not inverse:
        result = address_route(values, nf["input_columns"], 0, f, k, rho, inverse=True)
        result = phases(result, nf["input_phase_exponents"], f, k, rho,
                        omit_repeated_constant=omit_repeated_constant)
        result = tensor_c(result, bits)
        result = phases(result, nf["output_phase_exponents"], f, k, rho,
                        omit_repeated_constant=omit_repeated_constant)
        return address_route(result, nf["output_columns"], affine, f, k, rho)
    result = address_route(values, nf["output_columns"], affine, f, k, rho, inverse=True)
    result = phases(result, nf["output_phase_exponents"], f, k, rho, sign=-1)
    result = tensor_c(result, bits, inverse=True)
    result = phases(result, nf["input_phase_exponents"], f, k, rho, sign=-1)
    return address_route(result, nf["input_columns"], 0, f, k, rho)


def reference_matrix(values, matrix, f, k, rho):
    result = values
    for bits in selected_positions(f, k, rho):
        active = sum(1 << bit for bit in bits)
        output = [[ZERO] * len(values[0]) for _ in values]
        for outside in range(len(values)):
            if outside & active:
                continue
            addresses = [outside | sum((i >> slot & 1) << bit for slot, bit in enumerate(bits))
                         for i in range(8)]
            for y in range(8):
                for x in range(8):
                    if matrix[y][x] == ZERO:
                        continue
                    for field, value in enumerate(result[addresses[x]]):
                        output[addresses[y]][field] = add(output[addresses[y]][field], mul(matrix[y][x], value))
        result = output
    return result


def fixture_checks(fixture):
    frames, common, edges = gold(fixture)
    certificate = geometry(fixture, common)
    basis_values = [[ONE if a == b else ZERO for b in range(8)] for a in range(8)]
    for nf, edge in zip(fixture["compiled_edges"], edges):
        for side in ("input", "output"):
            table, q = nf[side + "_phase_exponents"], nf[side + "_quadratic"]
            if len(table) != 8 or any(cross not in (0, 2) for _, _, cross in q["cross"]):
                raise AssertionError("an outer phase is not a valid Z4 quadratic unit")
            for a in range(8):
                exponent = q["constant"] + sum(q["linear"][i] for i in range(3) if a >> i & 1)
                exponent += sum(cross for i, j, cross in q["cross"] if a >> i & 1 and a >> j & 1)
                if exponent % 4 != table[a]:
                    raise AssertionError("quadratic coefficient list omits a phase")
        if compiled_edge(basis_values, nf, 1, 1, 0) != edge:
            raise AssertionError("literal C-child adapter does not match every exact matrix entry")
    # All 16 physical two-role basis inputs are simultaneous full payloads.
    x = [[ONE if a == b else ZERO for b in range(16)] for a in range(8)]
    y = [[ONE if a + 8 == b else ZERO for b in range(16)] for a in range(8)]
    if gate(x, y, fixture["compiled_edges"], 1, 1, 0) != expected_gate(x, y, frames, 1, 1, 0):
        raise AssertionError("the exact full two-role operator does not match all16 basis inputs")
    return certificate


def gate(x, y, edges, f, k, rho, inverse=False):
    if inverse:
        x = compiled_edge(x, edges[2], f, k, rho, inverse=True)
        y = compiled_edge(y, edges[3], f, k, rho, inverse=True)
        y = [[add(a, rotate(b, 2)) for a, b in zip(pa, pb)] for pa, pb in zip(y, x)]
        return (compiled_edge(x, edges[0], f, k, rho, inverse=True),
                compiled_edge(y, edges[1], f, k, rho, inverse=True))
    x = compiled_edge(x, edges[0], f, k, rho)
    y = compiled_edge(y, edges[1], f, k, rho)
    y = [[add(a, b) for a, b in zip(pa, pb)] for pa, pb in zip(y, x)]
    return compiled_edge(x, edges[2], f, k, rho), compiled_edge(y, edges[3], f, k, rho)


def expected_gate(x, y, frames, f, k, rho):
    ux = reference_matrix(x, adjoint(frames[0]), f, k, rho)
    uy = reference_matrix(y, adjoint(frames[1]), f, k, rho)
    return (reference_matrix(ux, frames[2], f, k, rho),
            reference_matrix([[add(a, b) for a, b in zip(pa, pb)] for pa, pb in zip(uy, ux)],
                             frames[3], f, k, rho))


def case(task):
    fixture, f, k, rho, seed = task
    started = time.monotonic()
    frames, _, edges = gold(fixture)
    size, fields = 1 << (3 * f * k), 4
    rng = random.Random(seed)
    def dirty():
        return [[(Q(rng.randrange(-8, 9), 1 << rng.randrange(4)),
                  Q(rng.randrange(-8, 9), 1 << rng.randrange(4))) for _ in range(fields)]
                for _ in range(size)]
    x, y = dirty(), dirty()
    original = x, y
    actual = gate(x, y, fixture["compiled_edges"], f, k, rho)
    if actual != expected_gate(x, y, frames, f, k, rho):
        raise AssertionError("full dirty-payload literal component failed")
    # Independent elementary-layer guard, not an internal recursive-child
    # precision theorem. Units/routes preserve the grid; each C axis adds at
    # most one denominator and component-magnitude bit, and the shear one
    # magnitude bit. The longest actual path has three f-axis units.
    input_denominator = max(value.denominator for values in original for packet in values
                            for pair in packet for value in pair)
    input_magnitude = max(abs(value) for values in original for packet in values
                          for pair in packet for value in pair)
    for values in actual:
        for packet in values:
            for pair in packet:
                for value in pair:
                    if value.denominator > input_denominator * (1 << (3 * f)):
                        raise AssertionError("actual elementary path violates its complete grid bound")
                    if abs(value) > input_magnitude * (1 << (3 * f + 1)):
                        raise AssertionError("actual elementary path violates its complete magnitude bound")
    if gate(*actual, fixture["compiled_edges"], f, k, rho, inverse=True) != original:
        raise AssertionError("native inverse-C unit wrappers do not restore all dirty fields")
    # Every spectator fiber must be independent. Use actual fields carrying
    # an arbitrary value on one such fiber, not an adapter-only identity test.
    positions = sum(1 << bit for bits in selected_positions(f, k, rho) for bit in bits)
    spectator_mask = ((1 << (3 * f * k)) - 1) ^ positions
    if spectator_mask:
        spectator = spectator_mask & -spectator_mask
        delta = [[ONE] if a == spectator else [ZERO] for a in range(size)]
        output = compiled_edge(delta, fixture["compiled_edges"][3], f, k, rho)
        if any(packet != [ZERO] and a & spectator_mask != spectator for a, packet in enumerate(output)):
            raise AssertionError("bulk child or affine adapter modified a spectator coordinate")
    return {"columns": f, "chunk_width": k, "selected_offset": rho, "seed": seed,
            "complete_records_per_role": size, "fields_per_record": fields,
            "paid_child_widths": [f, f, f, 2 * f], "child_calls": 4,
            "all_physical_operator_values": 2 * size * fields,
            "complete_dirty_reverse_verified": True,
            "spectator_fibers_preserved": True,
            "denominator_bits_added_outside_children": 0,
            "max_child_rank_mass_on_dependency_path": 3 * f,
            "scalar_shear_magnitude_bits": 1,
            "elementary_grid_and_magnitude_bound_verified": True,
            "recursive_child_internal_guard_proved": False,
            "seconds": time.monotonic() - started}


def negatives(fixture):
    nf = fixture["compiled_edges"][3]
    values = [[ONE if a == b else ZERO for b in range(8)] for a in range(8)]
    correct = compiled_edge(values, nf, 1, 1, 0)
    if compiled_edge(values, nf, 1, 1, 0, omit_affine=True) == correct:
        raise AssertionError("omitted output affine translation did not discriminate")
    bulk = [[(Q((a * 5 + b) % 13 - 6), Q((a * 7 + 3 * b) % 11 - 5)) for b in range(4)]
            for a in range(64)]
    exact = compiled_edge(bulk, nf, 2, 1, 0)
    if compiled_edge(bulk, nf, 2, 1, 0, omit_repeated_constant=True) == exact:
        raise AssertionError("unpaid repeated column constant did not discriminate")
    cropped = [[packet[0], ZERO, ZERO, ZERO] for packet in bulk]
    if compiled_edge(cropped, nf, 2, 1, 0) == exact:
        raise AssertionError("omitted full-payload fields did not discriminate")
    return {"omitted_affine_output_translation_rejected": True,
            "single_constant_phase_instead_of_per_column_rejected": True,
            "cropped_complete_payload_rejected": True,
            "reverse_uses_forward_children_and_exact_i_Z_wrappers": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--small", action="store_true")
    parser.add_argument("--fixture", type=Path, default=Path(__file__).resolve().parents[2] / "fixtures/transfers/four-incidence-gate-witness.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    if args.output and args.output.exists():
        raise FileExistsError("Use a fresh output for each attempt")
    utc_started = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    fixture = json.loads(args.fixture.read_text())
    exact_geometry = fixture_checks(fixture)
    shapes = [(1, 1, 0), (2, 1, 0), (1, 2, 0), (1, 2, 1)]
    if not args.small:
        shapes.extend([(3, 1, 0), (2, 2, 1)])
    tasks = [(fixture, f, k, rho, 202610082000 + i) for i, (f, k, rho) in enumerate(shapes)]
    if args.workers == 1:
        cases = [case(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(case, tasks))
    controls = negatives(fixture)
    result = {"status": "PASS", "scope": "Independent literal Gaussian-dyadic full-payload four-incidence component; fixed-tape adapters conditional, complete native motif and exponent unproved.",
              "utc_started_at": utc_started, "utc_completed_at": datetime.now(timezone.utc).isoformat(),
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "fixture_sha256": hashlib.sha256(args.fixture.read_bytes()).hexdigest(),
              "producer_imports": False, "workers": args.workers, "small": args.small,
              "geometry": exact_geometry, "cases": cases, "negative_controls": controls,
              "all_physical_operator_values": sum(c["all_physical_operator_values"] for c in cases),
              "seconds": time.monotonic() - started}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("status", "scope", "workers", "small", "all_physical_operator_values", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
