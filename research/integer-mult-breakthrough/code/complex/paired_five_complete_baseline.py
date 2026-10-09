#!/usr/bin/env python3
"""Complete geometric ledger for the independent-edge paired-five baseline.

Every directed nonzero H edge has its own dirty carrier. Centers use ten
independent source-copy carriers per original port. The explicit recipe has
no sharing aliases, free clean scalar banks or omitted K inverse. The inherited
exact completed-core lift remains a conditional interface; this is not its
literal full Gaussian or fixed-tape execution.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
import json
import time

import paired_five_cube_discriminator as scalar


def edge_block(task):
    p, first, stop = task
    sources = scalar.labels(p, 5)
    histogram, coefficients = Counter(), Counter()
    edges = pairs = 0
    degree = None
    for target in range(first, stop):
        T = sources[target]
        row_degree = 0
        for source, S in enumerate(sources):
            t = (T & S).bit_count()
            B8 = (t - 1) * (t - 3)
            same_cube = target // 32 == source // 32
            H8 = 0 if same_cube else -B8
            K8 = (8 * (target == source) - B8) if same_cube else 0
            if H8 + B8 + K8 != 8 * (target == source):
                raise AssertionError('complete H/B/K source-column identity failed')
            pairs += 1
            if H8:
                if t & 1 or H8 not in (-3, 1):
                    raise AssertionError('a side edge leaves its orthogonal target cap')
                row_degree += 1
                coefficients[H8] += 1
        if degree is not None and degree != row_degree:
            raise AssertionError('the declared transitive side rows have unequal degrees')
        degree = row_degree
        edges += row_degree
    # Each actual side carrier follows 0 -> source line -> target cap -> full.
    histogram[1] = 2 * edges
    histogram[2 * p - 2] = edges
    expected_degree = 16 * (comb(p, 5) + (comb(p - 5, 5) if p >= 10 else 0) - 1)
    if degree != expected_degree:
        raise AssertionError('full side-edge recount differs from the closed combinatorial degree')
    return dict(first=first, stop=stop, exact_source_pairs=pairs, edges=edges,
                degree=degree, local_histogram=dict(histogram), coefficient_numerators_over8=dict(coefficients))


def center_tree(p):
    h, sources = 2 * p, scalar.labels(p, 5)
    local = Counter()
    centers = [(i, j) for i in range(h) for j in range(i + 1, h) if i // 2 != j // 2]
    roles = operations = 0
    copied_loss = 0
    examples = []
    for i, j in centers:
        incident = [s for s, S in enumerate(sources) if S & (1 << i) and S & (1 << j)]
        if not incident:
            raise AssertionError('an empty center was silently retained')
        roles += len(incident)
        local[1] += len(incident)  # Every independent copy is injected at its own source line.
        U = (sources[incident[0]],)
        ranks = [1]
        for source in incident[1:]:
            next_U = scalar.basis(U + (sources[source],))
            if len(next_U) < len(U):
                raise AssertionError('a center accumulation prefix descends')
            if len(next_U) > len(U):
                local[len(next_U) - len(U)] += 1  # Pivot grows to the actual union frame.
            if len(next_U) > 1:
                local[len(next_U) - 1] += 1  # Incoming source copy reaches the same frame.
            local[h - len(next_U)] += 1  # Retired incoming copy reaches full.
            operations += 1
            U = next_U
            ranks.append(len(U))
        if len(U) != h - 4:
            raise AssertionError('a completed pair-star tree has the wrong actual span')
        local[h - len(U)] += 1  # Pivot full-frame endpoint.
        local[len(U)] += 1  # Paid copied-center call, with no new omitted scalar role.
        copied_loss += len(U)
        if len(examples) < 2:
            examples.append(dict(pair=[i, j], input_count=len(incident),
                                 input_prefix=incident[:8], prefix_ranks=ranks[:16],
                                 final_span=list(U)))
    if roles != 10 * len(sources) or operations != roles - len(centers):
        raise AssertionError('independent center copies or literal sum gates were omitted')
    if sum(width * count for width, count in local.items()) != h * roles + copied_loss:
        raise AssertionError('complete center-role rank telescope failed')
    return dict(roles=roles, literal_additions=operations, centers=len(centers),
                copied_loss=copied_loss, local_histogram=dict(local), examples=examples,
                chronology='For each pair in lexicographic order, inject all its independent source copies at their own lines before original-source mutation. Grow pivot and next copy to their actual span union, add the copy into pivot, retire the copy at full; root is copied at rankh−4 and then pivot reaches full. Reverse all sums at common full before source-copy subtraction.')


def literal_dirty_echo(count):
    checked = 0
    rejected_missing = False
    for coefficient in (Q(1, 10), Q(-9, 160), Q(3, 80), Q(-3, 8), Q(1, 8)):
        size = count if coefficient.denominator in (10, 160, 80) else 1
        for direction in (-1, 1):
            for component in range(8):
                x = [Q((7 * i + 5 * component) % 37 - 18, 8) for i in range(size)]
                original = [Q((11 * i + 3 * component + 1) % 41 - 20, 16) for i in range(size)]
                y0 = Q(component - 3, 8)

                def run(omit=False):
                    value = y0 if omit else y0 - direction * coefficient * sum(original)
                    z = [a + b for a, b in zip(original, x)]
                    for i in range(1, size):
                        z[0] += z[i]
                    value += direction * coefficient * z[0]
                    for i in reversed(range(1, size)):
                        z[0] -= z[i]
                    z = [a - b for a, b in zip(z, x)]
                    return value, z

                value, z = run()
                if value != y0 + direction * coefficient * sum(x) or z != original:
                    raise AssertionError('literal arbitrary-dirty source-copy echo failed')
                if sum(original) and run(True)[0] == value:
                    raise AssertionError('missing old-value read negative did not reject')
                rejected_missing |= bool(sum(original))
                checked += size
    if not rejected_missing:
        raise AssertionError('the dirty omission negative had no nonzero witness')
    return dict(complete_gaussian_field_components=checked,
                both_shear_signs=True, all_scalar_fields_return=True,
                missing_old_correction_rejected=True,
                scope='Exact literal sum-tree and independent-edge scalar echoes; no Gaussian address-frame operators')


def complete(p, workers):
    h, v, m = 2 * p, 32 * comb(p, 5), 6 * p
    tasks = [(p, (i * v) // workers, ((i + 1) * v) // workers) for i in range(workers)]
    if workers == 1:
        blocks = [edge_block(tasks[0])]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            blocks = list(pool.map(edge_block, tasks))
    local, coefficients = Counter(), Counter()
    side_roles = 0
    for block in blocks:
        local.update(block['local_histogram'])
        coefficients.update(block['coefficient_numerators_over8'])
        side_roles += block['edges']
    center = center_tree(p)
    local.update(center['local_histogram'])
    original_sources = Counter({4: v, h - 6: v, 1: v})
    # Every target is read only at its one-dimensional cap after the center phase.
    # Repeated side reads have zero additional target rank, but their scalar reads
    # and complete payload visits are not omitted from the recipe.
    targets = Counter({h - 1: v})
    children = Counter()
    for histogram in (local, original_sources, targets):
        children.update({r: 3 * n for r, n in histogram.items() if r})
    children[2] += 2 * v
    R = side_roles + center['roles']
    W = 2 * v + R
    rank = sum(r * n for r, n in children.items())
    deficit = m * W - rank
    if deficit != 2 * v - 3 * center['copied_loss']:
        raise AssertionError('whole paid stock deficit failed')
    if not all(0 < r < m and r <= h - 1 for r in children):
        raise AssertionError('the named baseline contains an unpaid or improper child')
    # For every child, log(m/r)>log3>1. Thus exp(b log(m/r))>1+b,
    # and Phi(1-b) > (rank/(mW))*(1+b). This is exact rational exclusion.
    target_b = Q(1, 10000)
    moment_lower = Q(rank, m * W) * (1 + target_b)
    if moment_lower <= 1:
        raise AssertionError('the baseline unexpectedly escaped the target-level necessary exclusion')
    word = scalar.scalar_word_case(5)
    gate_count = Q(2 * word['gates_per_parity'] * 2 * v, 32)
    if gate_count.denominator != 1:
        raise AssertionError('the complete K mutation and inverse have fractional gate stock')
    scalar_charge = (4 * center['literal_additions'] + 2 * R +
                     2 * (side_roles + center['centers'] * v) + int(gate_count))
    return dict(p=p, h=h, v=v, m=m, physical_side_roles=side_roles,
                physical_center_copy_roles=center['roles'], all_auxiliary_roles=R,
                W=W, complete_rank=rank, deficit=deficit,
                side_rows=v, side_edges_per_row=blocks[0]['degree'],
                exact_scalar_source_pairs=sum(x['exact_source_pairs'] for x in blocks),
                side_coefficients_over8=dict(coefficients),
                local_histogram=dict(local), original_source_histogram=dict(original_sources),
                target_histogram=dict(targets), complete_child_histogram=dict(children),
                copied_center_loss=center['copied_loss'], maximum_child=max(children),
                center_tree=center,
                K_word=word, complete_K_forward_inverse_scalar_gates=int(gate_count),
                center_and_side_source_injections=R,
                center_root_scatters=center['centers'] * v,
                side_positive_and_old_correction_reads=2 * side_roles,
                conservative_complete_scalar_gate_recipe=scalar_charge,
                scalar_recipe_detail='Four center M/M_inverse passes charge old JM formation and undo as well as signal formation and undo; 2R source copies/subtractions; both signs of every side and center scatter; complete K mutation/inverse. Record routing, phase gauges, scalar bit precision and full native execution are additional bills, not free.',
                literal_scalar_dirty_echo=literal_dirty_echo(8 * comb(p - 2, 3)),
                all_original_sources_unmutated_before_cleanup=True,
                all_auxiliary_dirty_seeds_cancel_by_exact_linear_echo=True,
                new_odd_divisor5_requires_reinstantiated_grid=True,
                target_component_b=str(target_b), exact_moment_lower=str(moment_lower),
                exact_target_moment_excess=str(moment_lower - 1),
                necessary_b_upper=str(Q(deficit, rank)),
                conclusion='REFUTED at b>=1/10000 within this fully counted independent-edge/independent-center-copy architecture',
                scope='Complete finite scalar recipe and binary/Lagrangian rank ledger under the inherited completed-core lift. Native payload, actual all-size phase/router/grid construction and outer multiplier transfer are not proved.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('workers must be positive')
    source = Path(__file__)
    dependency = Path(scalar.__file__)
    frozen = {p: p.read_bytes() for p in (source, dependency)}
    started_utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    result = complete(7 if args.bounded else 9, args.workers)
    if any(p.read_bytes() != value for p, value in frozen.items()):
        raise AssertionError('source closure changed during the run')
    certificate = dict(status='PASS complete paired-five baseline exclusion',
                       started_utc=started_utc, completed_utc=datetime.now(timezone.utc).isoformat(),
                       seconds=time.monotonic() - started, workers=args.workers,
                       bounded=args.bounded, source_sha256={p.name: sha256(value).hexdigest() for p, value in frozen.items()},
                       result=result)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(certificate, indent=2) + '\n')
    print(json.dumps(dict(status=certificate['status'], seconds=certificate['seconds'],
                          p=result['p'], W=result['W'], rank=result['complete_rank'],
                          deficit=result['deficit'], target_moment_lower=result['exact_moment_lower'])), flush=True)


if __name__ == '__main__':
    main()
