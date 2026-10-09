#!/usr/bin/env python3
"""Exact fanout flags and a terminal full-cap common-frame reader boundary.

This screen charges a named whole-source-cube ordering: all earlier cube
supports remain in each target's monotonically growing address frame. A
single retained scalar channel is read into its targets at their actual
current frames. Target mixing, copied readers and changed chronologies are
outside this screen. No scalar-rank count is promoted to physical stock.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import time

import paired_cap_dirty_completion as completion


def label_on_pairs(pairs, selector):
    return sum(1 << (2 * pair + ((selector >> i) & 1))
               for i, pair in enumerate(pairs))


def pair_set(label, p):
    return tuple(i for i in range(p) if label & (3 << (2 * i)))


def ranks(values):
    return len(completion.binary_basis(values))


def previous_support_witness(p, target, last_cube):
    """Retain actual source labels, never an arbitrary span completion."""
    target_cube = pair_set(target, p)
    pivots, witnesses = {}, []
    for cube in combinations(range(p), 5):
        if cube == last_cube or cube == target_cube:
            continue
        for selector in range(32):
            source = label_on_pairs(cube, selector)
            overlap = (source & target).bit_count()
            if overlap & 1:
                continue
            # Distinct source cubes: every even overlap gives a nonzero H.
            if not completion.central(overlap):
                raise AssertionError('A retained literal side source has zero coefficient')
            value = source
            while value:
                pivot = value.bit_length() - 1
                if pivot in pivots:
                    value ^= pivots[pivot]
                else:
                    pivots[pivot] = value
                    witnesses.append(source)
                    break
            if len(pivots) == 2 * p - 1:
                if ranks(witnesses) != 2 * p - 1:
                    raise AssertionError('Full-cap source witness was not independent')
                return witnesses
    raise AssertionError('Previous whole-cube side supports do not span the final target cap')


def parity_block(j, parity):
    n, source_parity = 1 << (j - 1), parity ^ (j & 1)
    sources = [completion.parity_selector(j, source_parity, u) for u in range(n)]
    targets = [completion.parity_selector(j, parity, t) for t in range(n)]
    matrix = [[-completion.central(j - (s ^ t).bit_count()) for s in sources]
              for t in targets]
    decoder = [completion.solve_decoder(matrix[:3], row) for row in matrix]
    return sources, targets, decoder


def probe(p):
    if p < 7:
        raise ValueError('At least seven paired coordinates required')
    main_cube, h = tuple(range(5)), 2 * p
    all_supports, summaries, digest_rows = {}, [], []
    single_cube_excess = 0
    for j in (3, 4):
        source_selectors, targets, decoders = parity_block(j, 0)
        buckets = [[label_on_pairs(main_cube, s | (u << j))
                    for u in range(1 << (5 - j))] for s in source_selectors]
        cap = completion.binary_basis(s for bucket in buckets for s in bucket)
        if len(cap) != 5:
            raise AssertionError('The retained root source cap changed')
        actual_spans, raw_spans, all_target_counts = [], [], []
        root_rows = []
        for root in range(3):
            patterns = [targets[t] for t, decoder in enumerate(decoders) if decoder[root]]
            fanout, single_pattern = [], []
            for outside_pairs in combinations(range(5, p), 5 - j):
                cube = tuple(range(j)) + outside_pairs
                for outside in range(1 << (5 - j)):
                    fanout.extend(label_on_pairs(cube, t | (outside << j)) for t in patterns)
                    single_pattern.append(label_on_pairs(cube, targets[root] | (outside << j)))
            if len(set(fanout)) != len(fanout):
                raise AssertionError('Merged target reads were counted twice')
            target_span = completion.binary_basis(fanout)
            if any((s & t).bit_count() & 1 for s in cap for t in target_span):
                raise AssertionError('Actual root fanout lies outside the common cap')
            for target in fanout:
                if target not in all_supports:
                    all_supports[target] = previous_support_witness(p, target, main_cube)
            raw_span = ranks(single_pattern)
            actual_spans.append(len(target_span)); raw_spans.append(raw_span)
            all_target_counts.append(len(fanout))
            # Hyperplanes T^perp are distinct; their Grassmann distances are2.
            if len(fanout) < 2:
                raise AssertionError('No genuine multi-target boundary')
            first, second = fanout[0], fanout[1]
            if ranks([first, second]) != 2:
                raise AssertionError('Distinct binary target lines were dependent')
            geodesic_remaining = h - 5
            paid_path = (h - 1 - 5) + 2 * (len(fanout) - 1) + 1
            excess = paid_path - geodesic_remaining
            if excess != 2 * (len(fanout) - 1):
                raise AssertionError('Terminal reader did not pay every target-frame change')
            root_rows.append({'retained_actual_row': root,
                              'target_reads': len(fanout),
                              'global_target_label_span': len(target_span),
                              'maximum_common_frame_inside_all_target_caps': h - len(target_span),
                              'raw_single_pattern_global_target_span': raw_span,
                              'remaining_geodesic_rank_cap_to_full': geodesic_remaining,
                              'terminal_common_frame_path_rank': paid_path,
                              'extra_rank_for_one_core': excess,
                              'first_target': first, 'second_target': second,
                              'previous_source_witness_for_first_target': all_supports[first]})
        fourier_fanout = [label_on_pairs(tuple(range(j)) + outside_pairs,
                                       t | (outside << j))
                         for outside_pairs in combinations(range(5, p), 5 - j)
                         for outside in range(1 << (5 - j)) for t in targets]
        fourier_span = ranks(fourier_fanout)
        multiplicity = comb(5, j)
        # The other parity is conjugate under flipping one common paired bit.
        weighted = 2 * multiplicity * sum(row['extra_rank_for_one_core'] for row in root_rows)
        single_cube_excess += weighted
        summaries.append({'j': j, 'J_subsets': multiplicity, 'parity_blocks': 2,
                          'root_rows': root_rows,
                          'all_selector_Fourier_global_target_span': fourier_span,
                          'maximum_Fourier_common_frame': h - fourier_span,
                          'extra_rank_for_both_parities_all_J_one_core': weighted})
    for target, sources in sorted(all_supports.items()):
        if any((target & s).bit_count() & 1 for s in sources):
            raise AssertionError('Final-cap witness contains an ineligible source')
        digest_rows.append([target, sources])
    v, q = 32 * comb(p, 5), 2 * p * (p - 1)
    copied_loss = q * (h - 4)
    retained_deficit = 2 * v - 3 * copied_loss
    changed_deficit = retained_deficit - 3 * single_cube_excess
    if p in (9, 12) and not (retained_deficit > 0 and changed_deficit < 0):
        raise AssertionError('Promising retained deficit was not erased by the named terminal reader')
    # A zero-rank target switch would hide its different codimension-one line.
    if summaries[0]['root_rows'][0]['terminal_common_frame_path_rank'] == h - 5:
        raise AssertionError('Omitted inter-target frame changes were accepted')
    return {'pair_count': p, 'h': h, 'v': v, 'q': q,
            'copied_center_loss': copied_loss,
            'source_cube_processed_last': list(main_cube),
            'distinct_complete_target_caps_independently_witnessed': len(all_supports),
            'actual_previous_source_witness_entries': sum(len(s) for s in all_supports.values()),
            'complete_witness_digest_sha256': sha256(json.dumps(digest_rows, separators=(',', ':')).encode()).hexdigest(),
            'overlap_blocks': summaries,
            'terminal_one_cube_extra_rank_per_core': single_cube_excess,
            'terminal_one_cube_extra_rank_three_cores': 3 * single_cube_excess,
            'retained_three_core_rank_deficit': retained_deficit,
            'changed_deficit_after_only_terminal_j3_j4_reader_charges': changed_deficit,
            'named_readout_architecture': 'Every earlier whole-source-cube literal support remains in each target frame; one physical scalar-channel carrier visits each final target hyperplane at an actual same-frame read and then goes to full.',
            'exclusion_scope': 'Named monotone whole-cube block ordering and independent common-frame scalar readers only; target-bank mixing, separate copies, changed endpoints, early/interleaved readouts and shared parking are open.',
            'zero_cost_target_switch_rejected': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('At least one worker required')
    paths = [Path(__file__).resolve(), Path(completion.__file__).resolve()]
    frozen = {p: p.read_bytes() for p in paths}
    started, timer = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    pairs = [7] if args.bounded else [7, 8, 9, 12]
    if args.workers == 1:
        rows = list(map(probe, pairs))
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(pairs))) as pool:
            rows = list(pool.map(probe, pairs))
    if any(p.read_bytes() != b for p, b in frozen.items()):
        raise AssertionError('Effective source closure changed')
    result = {'status': 'PASS exact global fanout flags and scoped terminal-reader exclusion',
              'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.perf_counter() - timer, 'workers': args.workers,
              'bounded': args.bounded, 'source_sha256': {p.name: sha256(b).hexdigest() for p, b in frozen.items()},
              'cases': rows,
              'scope': 'Exact scalar decoder fanout/support flags, previous-source final-cap witnesses, and a named complete-reader rank excess. No native supplier or universal lower bound.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'changed_deficits': [row['changed_deficit_after_only_terminal_j3_j4_reader_charges'] for row in rows]}), flush=True)


if __name__ == '__main__':
    main()
