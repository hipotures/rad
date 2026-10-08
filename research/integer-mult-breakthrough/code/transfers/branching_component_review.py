#!/usr/bin/env python3
"""Independent full-payload binding of the degenerate three-helper component.

Candidate adapters only are imported as data. The literal matrices, phase
anchors, chronology, dirty restoration and graph-chart comparison are rebuilt.
Only previous transfer-track arithmetic helpers are imported, never producers.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import random
import time

from lagrangian_component_review import add, mul, rotate, span, embed, tensor_c


ZERO, ONE = (Q(), Q()), (Q(1), Q())
ROLES = ("x0", "x1", "y0", "y1", "a", "b", "p")


def adjoint(a):
    return [[(a[y][x][0], -a[y][x][1]) for y in range(16)] for x in range(16)]


def compose(a, b):
    result = [[ZERO] * 16 for _ in range(16)]
    for y in range(16):
        for k in range(16):
            if a[y][k] == ZERO:
                continue
            for x in range(16):
                if b[k][x] != ZERO:
                    result[y][x] = add(result[y][x], mul(a[y][k], b[k][x]))
    return result


def identity():
    return [[ONE if y == x else ZERO for x in range(16)] for y in range(16)]


def line(v):
    if not v.bit_count() % 2:
        raise ValueError("this witness requires odd source and target directions")
    a, b = (Q(1, 2), Q(1, 2)), (Q(1, 2), Q(-1, 2))
    return [[a if y == x else b if y == x ^ v else ZERO for x in range(16)] for y in range(16)]


def permutation(mapping):
    if sorted(mapping) != list(range(16)):
        raise AssertionError("literal routing matrix is not a complete permutation")
    return [[ONE if y == mapping[x] else ZERO for x in range(16)] for y in range(16)]


def frames(candidate):
    basis_values = [[ONE if a == b else ZERO for b in range(16)] for a in range(16)]
    full = tensor_c(basis_values, (0, 1, 2, 3))
    g = (Q(1, 2), Q(1, 2))
    ht = [[rotate(g, 2 * int(bool(y & 2) and bool(x & 2))) if y & ~2 == x & ~2 else ZERO
           for x in range(16)] for y in range(16)]
    cn = permutation([x ^ (4 if x & 2 else 0) for x in range(16)])
    common = compose(line(1), compose(ht, cn))
    if candidate["source_directions"] == [8, 14]:
        swap = permutation([(x & 6) | ((x & 1) << 3) | ((x & 8) >> 3) for x in range(16)])
        common = compose(swap, compose(common, swap))
    result = {"zero": identity(), "full": full, "common": common}
    for j, v in enumerate(candidate["source_directions"]):
        result["line" + str(j)] = line(v)
    for j, v in enumerate(candidate["target_directions"]):
        result["kernel" + str(j)] = compose(full, adjoint(line(v)))
    if compose(common, adjoint(common)) != identity():
        raise AssertionError("literal common frame is not unitary")
    return result


def positions(f, k, rho):
    return [[slot * f * k + column * k + rho for slot in range(4)] for column in range(f)]


def coordinate(address, bits):
    return sum((address >> bit & 1) << j for j, bit in enumerate(bits))


def route(values, columns, affine, f, k, rho, inverse=False):
    mapping = [affine ^ embed(columns, i) for i in range(16)]
    if sorted(mapping) != list(range(16)):
        raise AssertionError("candidate route loses a selected address")
    if inverse:
        mapping = [mapping.index(i) for i in range(16)]
    selected = positions(f, k, rho)
    active = sum(1 << bit for bits in selected for bit in bits)
    output = [None] * len(values)
    for old, packet in enumerate(values):
        new = old & ~active
        for bits in selected:
            image = mapping[coordinate(old, bits)]
            new |= sum((image >> j & 1) << bit for j, bit in enumerate(bits))
        output[new] = list(packet)
    if any(packet is None for packet in output):
        raise AssertionError("affine adapter is not a complete stream permutation")
    return output


def phases(values, table, f, k, rho, sign=1, omit_column_constant=False):
    selected = positions(f, k, rho)
    return [[rotate(value, sign * (sum(table[coordinate(a, bits)] for bits in selected)
                                   - ((f - 1) * table[0] if omit_column_constant else 0)))
             for value in packet] for a, packet in enumerate(values)]


def edge(values, nf, f, k, rho, inverse=False, omit_affine=False, omit_column_constant=False):
    selected = [slot * f * k + column * k + rho for slot in range(nf["rank"]) for column in range(f)]
    affine = 0 if omit_affine else nf["output_affine_offset"]
    if inverse:
        result = route(values, nf["output_columns"], affine, f, k, rho, inverse=True)
        result = phases(result, nf["output_phase_exponents"], f, k, rho, sign=-1)
        result = tensor_c(result, selected, inverse=True)
        result = phases(result, nf["input_phase_exponents"], f, k, rho, sign=-1)
        return route(result, nf["input_columns"], 0, f, k, rho)
    result = route(values, nf["input_columns"], 0, f, k, rho, inverse=True)
    result = phases(result, nf["input_phase_exponents"], f, k, rho,
                    omit_column_constant=omit_column_constant)
    result = tensor_c(result, selected)
    result = phases(result, nf["output_phase_exponents"], f, k, rho,
                    omit_column_constant=omit_column_constant)
    return route(result, nf["output_columns"], affine, f, k, rho)


def matrix_apply(values, matrix, f, k, rho):
    result = values
    for bits in positions(f, k, rho):
        active = sum(1 << bit for bit in bits)
        output = [[ZERO] * len(values[0]) for _ in values]
        for outside in range(len(values)):
            if outside & active:
                continue
            addresses = [outside | sum((i >> j & 1) << bit for j, bit in enumerate(bits)) for i in range(16)]
            for y in range(16):
                for x in range(16):
                    if matrix[y][x] != ZERO:
                        for field, value in enumerate(result[addresses[x]]):
                            output[addresses[y]][field] = add(output[addresses[y]][field], mul(matrix[y][x], value))
        result = output
    return result


def events():
    # Independent chronology from the physical anchor contract. Every move
    # index is checked against the proposed edge's role/before/after below.
    return [["shear", "a", "b", 1], ["shear", "p", "a", 1],
            ["inject", "y0", "a", -1], ["inject", "y1", "p", -1],
            ["shear", "p", "a", -1], ["shear", "a", "b", -1],
            ["move", "a", 0], ["move", "b", 1],
            ["shear", "a", "x0", 1], ["shear", "b", "x1", 1],
            ["move", "a", 2], ["move", "b", 3], ["shear", "a", "b", 1],
            ["move", "b", 4], ["move", "p", 5], ["shear", "p", "a", 1],
            ["move", "a", 6], ["move", "y0", 7], ["inject", "y0", "a", 1],
            ["move", "p", 8], ["move", "y1", 9], ["inject", "y1", "p", 1],
            ["move", "a", 10], ["move", "p", 11],
            ["shear", "p", "a", -1], ["shear", "a", "b", -1],
            ["move", "x0", 12], ["move", "x1", 13],
            ["shear", "a", "x0", -1], ["shear", "b", "x1", -1]]


def execute(data, candidate, f, k, rho, inverse=False, omit_retirement=False):
    data = {role: [list(packet) for packet in values] for role, values in data.items()}
    chronology = events()
    if omit_retirement:
        chronology = [event for event in chronology if event != ["move", "b", 4]]
    if inverse:
        chronology = list(reversed(chronology))
    injection = -1 if candidate["source_directions"] == [8, 14] else 1
    for event in chronology:
        if event[0] == "move":
            _, role, index = event
            data[role] = edge(data[role], candidate["edges"][index]["normal_form"], f, k, rho, inverse)
        else:
            kind, dest, source, sign = event
            sign *= injection if kind == "inject" else 1
            if inverse:
                sign = -sign
            data[dest] = [[add(a, rotate(b, 0 if sign == 1 else 2)) for a, b in zip(pa, pb)]
                          for pa, pb in zip(data[dest], data[source])]
    return data


def expected(data, candidate, f, k, rho):
    anchor = frames(candidate)
    virtual = {role: [list(packet) for packet in values] for role, values in data.items()}
    for j in range(2):
        virtual["x" + str(j)] = matrix_apply(data["x" + str(j)], adjoint(anchor["line" + str(j)]), f, k, rho)
    sign = -1 if candidate["source_directions"] == [8, 14] else 1
    for role in ("y0", "y1"):
        virtual[role] = [[add(y, rotate(add(a, b), 0 if sign == 1 else 2))
                          for y, a, b in zip(py, p0, p1)]
                         for py, p0, p1 in zip(virtual[role], virtual["x0"], virtual["x1"])]
    return {role: matrix_apply(values, anchor["kernel" + role[1]] if role.startswith("y") else anchor["full"], f, k, rho)
            for role, values in virtual.items()}


def lagrangian_bits(vectors):
    return sum(1 << value for value in span(vectors))


def graph(code):
    columns, bit = [0] * 4, 0
    for i in range(4):
        for j in range(i, 4):
            if code >> bit & 1:
                columns[i] |= 1 << j
                columns[j] |= 1 << i
            bit += 1
    return lagrangian_bits((1 << i) | (columns[i] << 4) for i in range(4))


def distance(a, b):
    return 4 - ((a & b).bit_count().bit_length() - 1)


def independent_geometry():
    zero = lagrangian_bits((1, 2, 4, 8))
    full = lagrangian_bits((17, 34, 68, 136))
    def line_label(v):
        return lagrangian_bits((1 << i) | ((v if v >> i & 1 else 0) << 4) for i in range(4))
    def kernel_label(v):
        return lagrangian_bits((1 << i) | (((1 << i) ^ (v if v >> i & 1 else 0)) << 4) for i in range(4))
    c1, c7, k8, k14 = line_label(1), line_label(7), kernel_label(8), kernel_label(14)
    common = lagrangian_bits((96, 17, 8, 6))
    gs = [graph(code) for code in range(1024)]
    incoming = [distance(c1, g) + distance(c7, g) + distance(g, full) for g in gs]
    outgoing = [distance(zero, g) + distance(g, k8) + distance(g, k14) for g in gs]
    minimum, witness = 99, None
    for i, a in enumerate(gs):
        for j, b in enumerate(gs):
            cost = 4 + incoming[i] + outgoing[j] + distance(a, b)
            if cost < minimum:
                minimum, witness = cost, [i, j]
    common_cost = 4 + distance(c1, common) + distance(c7, common) + distance(common, full)
    common_cost += distance(zero, common) + distance(common, k8) + distance(common, k14)
    if minimum != 14 or common_cost != 12:
        raise AssertionError("independent full two-mixer graph ledger does not give14 versus12")
    return {"symmetric_graph_frames": 1024, "exact_two_mixer_pairs": 1024 ** 2,
            "graph_minimum": minimum, "graph_minimizer_codes": witness,
            "common_frame_auxiliary_cost": common_cost, "three_role_metric_lower_bound": 12,
            "scope": "This fixed branching chronology and its charged auxiliary incidences; four external rank3 transitions retained separately"}


def pauli(label):
    # Z^z X^x convention: the sign is evaluated at the output address.
    z, x = label & 15, label >> 4
    return [[rotate(ONE, 2 * ((z & y).bit_count() % 2)) if y == a ^ x else ZERO
             for a in range(16)] for y in range(16)]


def verify_common_paulis(candidate, common):
    images = []
    for i in range(4):
        actual = compose(adjoint(common), compose(pauli(1 << i), common))
        found = []
        for label in range(256):
            p = pauli(label)
            for power in range(4):
                if [[rotate(value, power) for value in row] for row in p] == actual:
                    found.append((label, power))
        if len(found) != 1:
            raise AssertionError("literal common frame has an ambiguous Pauli image")
        images.append(found[0])
    u = span(candidate["source_directions"])
    orthogonal = [z for z in range(16) if all((z & v).bit_count() % 2 == 0 for v in u)]
    literal_l = lagrangian_bits(label for label, _ in images)
    prescribed_l = lagrangian_bits(orthogonal + [v | (v << 4) for v in u])
    if literal_l != prescribed_l or literal_l != lagrangian_bits(candidate["common_lagrangian"]):
        raise AssertionError("actual full common frame does not induce L_U")
    return {"pauli_convention": "Z^z X^x; label=z+16*x",
            "conjugated_Z_generator_label_and_unit_exponent": images,
            "full_L_U_independently_bound": True}


def verify_candidate(candidate):
    anchor = frames(candidate)
    basis_values = [[ONE if a == b else ZERO for b in range(16)] for a in range(16)]
    current = dict(x0="line0", x1="line1", y0="zero", y1="zero", a="zero", b="zero", p="zero")
    injection = -1 if candidate["source_directions"] == [8, 14] else 1
    expected_events = []
    for event in events():
        if event[0] == "move":
            _, role, index = event
            item = candidate["edges"][index]
            if item["role"] != role or item["before"] != current[role]:
                raise AssertionError("candidate chronology changes a different phase anchor")
            nf = item["normal_form"]
            exact = compose(anchor[item["after"]], adjoint(anchor[item["before"]]))
            if edge(basis_values, nf, 1, 1, 0) != exact:
                raise AssertionError("literal one-child edge does not match every matrix entry")
            for side in ("input", "output"):
                q, table = nf[side + "_quadratic"], nf[side + "_phase_exponents"]
                if any(v not in (0, 2) for _, _, v in q["cross"]):
                    raise AssertionError("invalid unit quadratic phase")
                for a in range(16):
                    power = q["constant"] + sum(q["linear"][i] for i in range(4) if a >> i & 1)
                    power += sum(v for i, j, v in q["cross"] if a >> i & 1 and a >> j & 1)
                    if power % 4 != table[a]:
                        raise AssertionError("normal form dropped a quadratic or global unit")
            current[role] = item["after"]
            expected_events.append(event)
        else:
            kind, dest, source, sign = event
            if anchor[current[dest]] != anchor[current[source]]:
                raise AssertionError("a scalar incidence uses unequal physical frames")
            expected_events.append(["shear", dest, source, sign * (injection if kind == "inject" else 1)])
    if expected_events != candidate["events"]:
        raise AssertionError("independent literal word differs from the candidate event list")
    if current != dict(x0="full", x1="full", y0="kernel0", y1="kernel1", a="full", b="full", p="full"):
        raise AssertionError("a retired role is missing its final phase anchor")
    auxiliary = sum(item["normal_form"]["rank"] for item in candidate["edges"] if item["auxiliary"])
    external = sum(item["normal_form"]["rank"] for item in candidate["edges"] if not item["auxiliary"])
    if auxiliary != 12 or external != 12:
        raise AssertionError("the literal child ledger is incomplete")
    # Exact complete 7-role basis operator, rather than zero helper tests.
    data = {role: [[ONE if field == 16 * j + a else ZERO for field in range(112)] for a in range(16)]
            for j, role in enumerate(ROLES)}
    actual = execute(data, candidate, 1, 1, 0)
    if actual != expected(data, candidate, 1, 1, 0) or execute(actual, candidate, 1, 1, 0, inverse=True) != data:
        raise AssertionError("complete112-dimensional physical operator or inverse failed")
    # Distinct controls for a lost affine coset and a lost quadratic unit.
    nf = candidate["edges"][4]["normal_form"]
    if edge(basis_values, nf, 1, 1, 0, omit_affine=True) == edge(basis_values, nf, 1, 1, 0):
        raise AssertionError("affine omission negative did not discriminate")
    nf = json.loads(json.dumps(candidate["edges"][2]["normal_form"]))
    for side in ("input", "output"):
        q = nf[side + "_quadratic"]
        nf[side + "_phase_exponents"] = [(q["constant"] + sum(q["linear"][i] for i in range(4) if a >> i & 1)) % 4
                                         for a in range(16)]
    if edge(basis_values, nf, 1, 1, 0) == edge(basis_values, candidate["edges"][2]["normal_form"], 1, 1, 0):
        raise AssertionError("quadratic cross-term omission negative did not discriminate")
    return {"orientation": candidate["orientation"], "all_exact_edge_entries": 14 * 16 * 16,
            "complete_physical_basis_inputs": 112, "auxiliary_rank": auxiliary, "external_data_rank": external,
            "child_rank_distribution": {str(r): sum(item["normal_form"]["rank"] == r for item in candidate["edges"]) for r in (1, 2, 3)},
            "common_lagrangian_basis": candidate["common_lagrangian"],
            "literal_common_frame_paulis": verify_common_paulis(candidate, anchor["common"]),
            "affine_offset_omission_rejected": True, "quadratic_cross_omission_rejected": True,
            "scalar_chronology_and_retired_roles_verified": True}


def case(task):
    candidate, f, k, rho, seed = task
    started = time.monotonic()
    size, fields = 1 << (4 * f * k), 4
    rng = random.Random(seed)
    data = {role: [[(Q(rng.randrange(-8, 9), 1 << rng.randrange(4)),
                     Q(rng.randrange(-8, 9), 1 << rng.randrange(4))) for _ in range(fields)]
                   for _ in range(size)] for role in ROLES}
    actual = execute(data, candidate, f, k, rho)
    if actual != expected(data, candidate, f, k, rho):
        raise AssertionError("complete arbitrary dirty phase-anchor endpoint failed")
    if execute(actual, candidate, f, k, rho, inverse=True) != data:
        raise AssertionError("literal inverse-C units/routes do not restore the initial physical data")
    if execute(data, candidate, f, k, rho, omit_retirement=True) == actual:
        raise AssertionError("omitted retirement negative did not discriminate on dirty data")
    constant_rejected = None
    if f > 1:
        nf = candidate["edges"][4]["normal_form"]
        if edge(data["b"], nf, f, k, rho, omit_column_constant=True) == edge(data["b"], nf, f, k, rho):
            raise AssertionError("single-copy column constant negative did not discriminate")
        constant_rejected = True
    return {"orientation": candidate["orientation"], "columns": f, "chunk_width": k, "selected_offset": rho,
            "seed": seed, "complete_records_per_role": size, "fields_per_record": fields,
            "exact_forward_and_inverse_values": 2 * 7 * size * fields,
            "all_dirty_virtual_auxiliaries_restored_at_full_anchor": True,
            "literal_inverse_restores_physical_inputs": True, "retired_b_omission_rejected": True,
            "single_column_global_unit_omission_rejected": constant_rejected,
            "seconds": time.monotonic() - started}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--small", action="store_true")
    parser.add_argument("--fixture", type=Path, default=Path(__file__).resolve().parents[2] / "fixtures/transfers/degenerate-branching-candidates.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    if args.output and args.output.exists():
        raise FileExistsError("Use a fresh output for each attempt")
    utc_started, started = datetime.now(timezone.utc).isoformat(), time.monotonic()
    fixture = json.loads(args.fixture.read_text())
    geometry = independent_geometry()
    candidate_checks = [verify_candidate(candidate) for candidate in fixture["candidates"]]
    forward, reverse = fixture["candidates"]
    if compose(frames(forward)["common"], frames(reverse)["common"]) == frames(forward)["full"]:
        raise AssertionError("complementary frame product negative stopped discriminating")
    tasks = [(forward, 1, 1, 0, 202610085000), (reverse, 1, 2, 1, 202610085001)]
    if not args.small:
        tasks.extend([(forward, 2, 1, 0, 202610085002), (forward, 1, 2, 0, 202610085003)])
    if args.workers == 1:
        results = [case(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            results = list(pool.map(case, tasks))
    result = {"status": "PASS", "scope": "Independent literal full-payload branching component and complete phase-anchor/inverse review; fixed-tape adapters conditional, whole native motif and exponent unproved.",
              "utc_started_at": utc_started, "utc_completed_at": datetime.now(timezone.utc).isoformat(),
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "arithmetic_helper_source_sha256": hashlib.sha256(Path(__file__).with_name("lagrangian_component_review.py").read_bytes()).hexdigest(),
              "fixture_sha256": hashlib.sha256(args.fixture.read_bytes()).hexdigest(),
              "producer_imports": False, "workers": args.workers, "small": args.small,
              "geometry": geometry, "candidate_checks": candidate_checks, "cases": results,
              "complementary_frame_product_is_not_full_anchor": True,
              "exact_forward_and_inverse_values": sum(c["exact_forward_and_inverse_values"] for c in results),
              "seconds": time.monotonic() - started}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("status", "scope", "workers", "small", "exact_forward_and_inverse_values", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
