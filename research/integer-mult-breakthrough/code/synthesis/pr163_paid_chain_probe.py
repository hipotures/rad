#!/usr/bin/env python3
"""Bounded constructive paid-chain endpoint probe on the retained bit word.

This tests a general rational completion mechanism at fixed neighboring frames.
Only ideal child moments are optimized; no whole asymptotic claim is made.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

import pr163_bit_frame_review as V
import rational_frame_completion as F
import rational_paid_chain_endpoints as P


STATE = None


def initialize(reference, numerator, denominator):
    global STATE
    graph, word, records, partners, profile, descent = V.read_inputs(reference)
    h = graph['h']
    frames = V.Frames(records['frames'], h)
    nf = {int(key): frame for key, frame in word['node_frame'].items()}
    chosen = [nf[node] for a, b, node in word['ops']]
    for i, rows in descent['frames']:
        chosen[i] = frames.add(rows)
    source_roles = {int(s): role for s, role in word['sources'].items()}
    starts = {role: word['source_frame'][s] for s, role in source_roles.items()}
    starts.update({g['role']: g['frame'] for g in word['gauges']})
    # Events bind both neighbors in the literal two-phase chronology.
    p1 = set(word['phase1'])
    chronological = []
    chronological.extend(('op', i, chosen[i]) for i in sorted(p1))
    chronological.extend(('root', j, frame) for j, (root, frame) in
                         enumerate(zip(graph['roots'], word['root_frame'])) if root['kind'] == 'center')
    chronological.extend(('op', i, chosen[i]) for i in range(len(chosen)) if i not in p1)
    chronological.extend(('root', j, frame) for j, (root, frame) in
                         enumerate(zip(graph['roots'], word['root_frame'])) if root['kind'] != 'center')
    previous, before = dict(starts), {}
    for kind, index, frame in chronological:
        roles = word['ops'][index][:2] if kind == 'op' else (word['rootroles'][index],)
        for role in roles:
            if kind == 'op':
                before[index, role] = previous.get(role)
            previous[role] = frame
    following, after = {}, {}
    for kind, index, frame in reversed(chronological):
        roles = word['ops'][index][:2] if kind == 'op' else (word['rootroles'][index],)
        for role in roles:
            if kind == 'op':
                after[index, role] = following.get(role, word['full_frame'])
            following[role] = frame
    chi = [tuple(int(j in label) for j in range(h)) for label in graph['labels']]
    STATE = dict(graph=graph, word=word, frames=frames, chosen=chosen, before=before,
                 after=after, chi=chi, supports=V.supports(graph), G=F.form(h),
                 numerator=numerator, denominator=denominator)


def probe(index):
    s, started = STATE, time.monotonic()
    graph, word, frames, chosen = s['graph'], s['word'], s['frames'], s['chosen']
    h = graph['h']
    receiver, donor, node = word['ops'][index]
    before = [s['before'][index, role] for role in (receiver, donor)]
    after = [s['after'][index, role] for role in (receiver, donor)]
    rows = [row for frame in before if frame is not None for row in frames.B[frame]]
    rows.extend(s['chi'][source] for source in V.bits(s['supports'][node]))
    lower, unused = V.echelon(rows, h)
    upper = V.annihilator(list(frames.A[after[0]]) + list(frames.A[after[1]]), h)
    result = P.endpoint_frames(lower, upper, s['G'])
    V.require(result['minimal_dimension'] is not None, 'Current admissible frame cannot have an impossible cut')
    current_dimension = frames.dim[chosen[index]]
    minimal, maximal = result['minimal_dimension'], result['maximum_dimension']
    V.require(minimal <= current_dimension <= maximal, 'Retained frame lies between the exact endpoints')
    previous_dimensions = [0 if frame is None else frames.dim[frame] for frame in before]
    next_dimensions = [frames.dim[frame] for frame in after]
    current_widths = P.widths(current_dimension, previous_dimensions, next_dimensions)
    if minimal == maximal == current_dimension:
        return dict(operation=index, dimensions=[minimal, current_dimension, maximal],
                    previous=previous_dimensions, following=next_dimensions,
                    source_span_dimension=len(lower), lower_radical_dimension=len(result['lower_radical']),
                    status='LOCKED BY BOTH CHAIN BOUNDARIES', seconds=time.monotonic() - started)
    power = (s['numerator'], s['denominator'], 48)
    current_interval = P.moment_interval(current_widths, *power)
    candidates = []
    for name, dimension, basis in [('minimum', minimal, result['completion']),
                                   ('maximum', maximal, result['maximum_completion'])]:
        rank_widths = P.widths(dimension, previous_dimensions, next_dimensions)
        interval = P.moment_interval(rank_widths, *power)
        # Every proposed frame is independently bound to its lower and upper cut.
        V.require(F.contained(lower, basis, h) and F.contained(basis, upper, h), 'Endpoint literal containment')
        integer_basis, denominators = P.cleared_basis(basis)
        sums = list(map(sum, integer_basis))
        gram = [[9 * V.dot(a, b) - sums[i] * sums[j]
                 for j, b in enumerate(integer_basis)] for i, a in enumerate(integer_basis)]
        gram_determinant = V.determinant(gram)
        V.require(gram_determinant != 0, 'Explicit cleared proposed Gram witness')
        gain = 3 * (current_interval[0] - interval[1])
        candidates.append(dict(endpoint=name, dimension=dimension, widths=rank_widths,
                               ideal_moment_gain_lower=str(gain),
                               strict_ideal_improvement=gain > 0,
                               changed_positive_edge_count=3 * (len(rank_widths) - len(current_widths)),
                               clearing_denominators=list(denominators),
                               cleared_Gram_determinant=gram_determinant,
                               cleared_Gram_bits=abs(gram_determinant).bit_length(),
                               basis=F.encoded(basis) if gain > 0 else None))
    return dict(operation=index, dimensions=[minimal, current_dimension, maximal],
                previous=previous_dimensions, following=next_dimensions,
                source_span_dimension=len(lower), lower_radical_dimension=len(result['lower_radical']),
                candidates=candidates, seconds=time.monotonic() - started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--limit', type=int, default=128)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--power', type=Q, default=Q(999, 1000))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    V.require(args.limit > 0 and args.workers > 0 and 0 < args.power < 1, 'Positive bounded probe configuration')
    data = V.read_inputs(args.reference)
    indices = [index for index, basis in data[-1]['frames'][:args.limit]]
    files = [Path(__file__).resolve(), Path(V.__file__).resolve(), Path(F.__file__).resolve(), Path(P.__file__).resolve()]
    hashes = {file.name: sha256(file.read_bytes()).hexdigest() for file in files}
    args.output.mkdir(parents=True, exist_ok=False)
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(), source_closure=hashes,
                    reference_inputs=V.INPUTS, power=str(args.power), selected_operation_indices=indices,
                    workers=args.workers, scope='Fixed-neighbor constructive rational endpoint probe; ideal costs only')
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    started = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize,
                             initargs=(str(args.reference), args.power.numerator, args.power.denominator)) as pool:
        rows = list(pool.map(probe, indices))
    V.read_inputs(args.reference)
    V.require(hashes == {file.name: sha256(file.read_bytes()).hexdigest() for file in files}, 'Endpoint source closure unchanged')
    improved = [(row['operation'], candidate) for row in rows for candidate in row.get('candidates', [])
                if candidate['strict_ideal_improvement']]
    summary = dict(status='PASS EXACT LOCAL ENDPOINT PROBE', cases=len(rows),
                   locked_cases=sum(row.get('status') == 'LOCKED BY BOTH CHAIN BOUNDARIES' for row in rows),
                   lower_radical_histogram=dict(Counter(row['lower_radical_dimension'] for row in rows)),
                   strictly_improving_ideal_candidates=len(improved),
                   candidate_new_Gram_max_bits=max((candidate['cleared_Gram_bits'] for index, candidate in improved), default=0),
                   complete_paid_or_exponent_claim=False, seconds=time.monotonic() - started)
    (args.output / 'certificate.json').write_text(json.dumps(dict(summary=summary, cases=rows), indent=2) + '\n')
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()
