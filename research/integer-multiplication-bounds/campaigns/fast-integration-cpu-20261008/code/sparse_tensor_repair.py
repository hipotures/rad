#!/usr/bin/env python3
"""Exact controls for source-closed sparse tensor repair, independent of kernels.

This validates finite movement/support identities, not Gaussian error or a
multitape running time. Integer row stencils deliberately vary with output row.
"""
import argparse
import concurrent.futures
import hashlib
import itertools
import json
import pathlib
import time


CASES = [
    (2, 24, 8, 1), (3, 16, 8, 1), (4, 16, 8, 1),
    (2, 32, 16, 2), (3, 24, 8, 1), (3, 24, 12, 2),
    (4, 12, 6, 1),
]


def run_case(spec):
    began = time.monotonic()
    d, period, cell, radius = spec
    assert period % cell == 0 and 4 * radius <= cell
    coords = list(itertools.product(range(period), repeat=d))
    strides = [period ** (d - 1 - i) for i in range(d)]

    def index(x):
        return sum(a * b for a, b in zip(x, strides))

    def phase(j):
        # Two short periodic exceptional strips, including a physical cut.
        return j in (0, period // 2)

    def row_radius(j):
        return 2 * radius + 1 if phase(j) else radius

    def coefficients(axis, j):
        r = row_radius(j)
        return [(h, 19 + axis if h == 0 else
                 ((axis + 3) * (j + 2) + h * h) % 5 - 2)
                for h in range(-r, r + 1)]

    rows = [[coefficients(i, j) for j in range(period)] for i in range(d)]
    original = [((k * 1103515245 + 12345) % 29) - 14 for k in range(len(coords))]
    reference = original[:]
    # Full rectangular streaming oracle, using integer addresses rather than
    # the sparse tuple-key representation below.
    for axis, stride in enumerate(strides):
        result = [0] * len(reference)
        for address in range(len(reference)):
            j = (address // stride) % period
            result[address] = sum(c * reference[address +
                (((j + h) % period) - j) * stride]
                for h, c in rows[axis][j])
        reference = result

    def face(j, shifted):
        residue = (j - (cell // 2 if shifted else 0)) % cell
        return residue < radius or residue >= cell - radius

    target = {x for x in coords if
              (any(face(j, False) for j in x) and
               any(face(j, True) for j in x)) or any(phase(j) for j in x)}

    # E_k contains final destinations expanded only in axes not yet applied.
    # Radius is the FINAL row's radius, not the radius of a source neighbor.
    needed = []
    for completed in range(d + 1):
        support = set()
        for x in target:
            ranges = [[j] if i < completed else
                      [(j + h) % period for h, _ in rows[i][j]]
                      for i, j in enumerate(x)]
            support.update(itertools.product(*ranges))
        needed.append(support)

    current = {x: original[index(x)] for x in needed[0]}
    source_reads = 0
    for axis in range(d):
        after = {}
        for x in needed[axis + 1]:
            total = 0
            for h, c in rows[axis][x[axis]]:
                y = list(x)
                y[axis] = (y[axis] + h) % period
                y = tuple(y)
                assert y in current, (spec, axis, x, y)
                total += c * current[y]
                source_reads += 1
            after[x] = total
        current = after
    assert all(current[x] == reference[index(x)] for x in target)

    # Separate direct tensor oracle on bounded selected outputs.
    sample = sorted(target)[::max(1, len(target) // 41)][:43]
    direct_probes = 0
    for x in sample:
        total = 0
        for terms in itertools.product(*(rows[i][j] for i, j in enumerate(x))):
            y = tuple((j + h) % period for j, (h, _) in zip(x, terms))
            weight = 1
            for _, c in terms:
                weight *= c
            total += weight * original[index(y)]
            direct_probes += 1
        assert total == current[x]

    # Retained negative: crop to final targets after EVERY axis, replacing
    # missing inputs by zero. This loses not-yet-used coordinate halos.
    wrong = {x: original[index(x)] for x in target}
    for axis in range(d):
        after = {}
        for x in target:
            total = 0
            for h, c in rows[axis][x[axis]]:
                y = list(x)
                y[axis] = (y[axis] + h) % period
                total += c * wrong.get(tuple(y), 0)
            after[x] = total
        wrong = after
    negative_mismatches = sum(wrong[x] != current[x] for x in target)
    assert negative_mismatches > 0

    # Packet-volume bound charges copies, rather than only a union of targets.
    # Phase packets are full slabs in every other axis. Regular pair packets
    # have two constrained expanded face fields on DISTINCT axes.
    phase_expanded = set()
    for j in range(period):
        if phase(j):
            phase_expanded.update((j + h) % period
                                  for h in range(-row_radius(j), row_radius(j) + 1))
    pair_sum = 0
    pair_union = set()
    expanded_faces = []
    for shifted in (False, True):
        expanded_faces.append({(j + h) % period for j in range(period)
                               if face(j, shifted)
                               for h in range(-radius, radius + 1)})
    for i in range(d):
        for j in range(d):
            if i == j:
                continue
            packet = {x for x in coords if x[i] in expanded_faces[0]
                      and x[j] in expanded_faces[1]}
            pair_union.update(packet)
            pair_sum += len(packet)
    phase_packets = {x for x in coords if any(j in phase_expanded for j in x)}
    phase_sum = d * len(phase_expanded) * period ** (d - 1)
    regular_targets = {x for x in target if not any(phase(j) for j in x)}
    regular_sources = set()
    for x in regular_targets:
        regular_sources.update(itertools.product(*[
            [(j + h) % period for h in range(-radius, radius + 1)] for j in x]))
    assert regular_sources <= pair_union
    assert needed[0] <= pair_union | phase_packets
    assert len(needed[0]) <= pair_sum + phase_sum

    return dict(shape=dict(d=d, period=period, cell=cell, radius=radius),
                full_records=len(coords), final_targets=len(target),
                support_sizes=[len(s) for s in needed], sparse_stencil_reads=source_reads,
                direct_tensor_terms=direct_probes, direct_outputs=len(sample),
                wrong_early_crop_mismatches=negative_mismatches,
                charged_pair_copies=pair_sum, charged_phase_copies=phase_sum,
                all_checks_passed=True, elapsed_seconds=time.monotonic() - began)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=7)
    parser.add_argument('--output', type=pathlib.Path, required=True)
    args = parser.parse_args()
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(run_case, CASES))
    result = dict(schema=1, scientific_scope='finite source/support and ordering controls',
                  source_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
                  cases=results, aggregate=dict(
                      full_records=sum(r['full_records'] for r in results),
                      sparse_outputs=sum(r['final_targets'] for r in results),
                      direct_tensor_terms=sum(r['direct_tensor_terms'] for r in results),
                      negative_mismatches=sum(r['wrong_early_crop_mismatches'] for r in results)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['aggregate']))


if __name__ == '__main__':
    main()
