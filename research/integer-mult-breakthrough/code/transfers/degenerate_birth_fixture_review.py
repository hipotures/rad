#!/usr/bin/env python3
"""Bind retained birth-reuse fixture to independent literal anchors and word.

No producer source is imported. The fixture is data: full affine routes,
quadratic chirps and global phases are reconstructed coefficient by coefficient.
The complete physical event sequence is matched to the independent dirty word.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

import degenerate_birth_review as independent
g = independent.g


TOPIC = Path(__file__).resolve().parents[2]
CONFIG = TOPIC/'configs/transfers/degenerate-birth-fixture-review.json'
FRAME_NAMES = {'F0': 'I', 'F1': 'A1', 'F2': 'A7', 'F3': 'E',
               'F4': 'K8', 'F5': 'K14', 'F6': 'F'}
SOURCE_SUBSPACES = {'F0': [], 'F1': [1], 'F2': [7], 'F3': [1, 6],
                   'F4': [1, 2, 4], 'F5': [1, 6, 10], 'F6': [1, 2, 4, 8]}


def matrix_digest(matrix, bits):
    denominator = 1 << bits; numerators = []
    for row in matrix:
        scaled = [[a*denominator, b*denominator] for a, b in row]
        if any(value.denominator != 1 for pair in scaled for value in pair):
            raise ValueError('Independent literal matrix does not have the retained exact dyadic grid')
        numerators.append([[int(a), int(b)] for a, b in scaled])
    return sha256(json.dumps([numerators, bits], separators=(',', ':')).encode()).hexdigest()


def chirp(spec, address):
    return (spec['constant']+sum(c for bit, c in enumerate(spec['linear']) if address >> bit & 1)
            +sum(c for a, b, c in spec['cross'] if address >> a & 1 and address >> b & 1)) % 4


def reconstruct(form, negative=None):
    rank = form['selected_rank_per_column']; mask = (1 << rank)-1
    if not 0 < rank < 4 or form['one_bulk_child_calls'] != 1:
        raise ValueError('Fixture does not pay exactly one strict selected-width child')
    out = [[g.ZERO]*16 for _ in range(16)]
    offset = 0 if negative == 'omit affine offset' else form['output_affine_offset']
    output_addresses = [offset ^ independent.embed(a, form['output_columns']) for a in range(16)]
    input_addresses = [independent.embed(a, form['input_columns']) for a in range(16)]
    if sorted(output_addresses) != list(range(16)) or sorted(input_addresses) != list(range(16)):
        raise ValueError('Retained affine route omits a complete input/output record')
    for side in ('output', 'input'):
        if [chirp(form[side+'_quadratic'], a) for a in range(16)] != form[side+'_phase_exponents']:
            raise ValueError('Retained quadratic gauge differs from its full finite phase table')
    for a in range(16):
        for b in range(16):
            if a >> rank != b >> rank:
                continue
            phase = form['output_phase_exponents'][a]+form['input_phase_exponents'][b]
            if negative == 'omit global phase':
                phase -= form['output_quadratic']['constant']+form['input_quadratic']['constant']
            out[output_addresses[a]][input_addresses[b]] = g.multiply(g.power(g.IMAGINARY, phase),
                g.c_entry(rank, a & mask, b & mask))
    return out


def pauli_subspace(frame):
    """Recover inverse-Z Pauli labels using literal Gaussian coefficients."""
    labels = []
    for bit in range(4):
        diagonal = [[(Q(-1 if a >> bit & 1 else 1), Q(0)) if a == b else g.ZERO
                     for b in range(16)] for a in range(16)]
        image = g.matmul(g.adjoint(frame), g.matmul(diagonal, frame))
        support = [a for a in range(16) if image[a][0] != g.ZERO]
        if len(support) != 1:
            raise ValueError('Literal inverse-Z image is not a Pauli monomial')
        x = support[0]; unit = image[x][0]
        if unit not in [g.power(g.IMAGINARY, phase) for phase in range(4)]:
            raise ValueError('Pauli image loses a global fourth-root phase')
        z = 0
        for j in range(4):
            if image[x ^ (1 << j)][1 << j] == independent.scale(unit, Q(-1)):
                z |= 1 << j
            elif image[x ^ (1 << j)][1 << j] != unit:
                raise ValueError('Pauli image has an invalid linear sign')
        for a in range(16):
            for b in range(16):
                expected = independent.scale(unit, Q(-1 if (b & z).bit_count() & 1 else 1)) if a == b ^ x else g.ZERO
                if image[a][b] != expected:
                    raise ValueError('Literal Pauli image differs at another complete address')
        labels.append(z | (x << 4))
    span = {0}
    for label in labels:
        span |= {x ^ label for x in list(span)}
    return span


def review(case):
    frames = independent.literal_frames(); spec = independent.word(case['reuse'], frames)
    if case['stock'] != spec['stock'] or case['initial_frame_ids'] != [next(k for k, v in FRAME_NAMES.items() if v == x) for x in spec['initial']]:
        raise ValueError('Retained initial phase anchors or stock differ')
    if [FRAME_NAMES[x] for x in case['final_frame_ids']] != spec['final']:
        raise ValueError('Retained final source/sink/dirty phase anchors differ')
    for item in case['frames']:
        if item['subspace'] != SOURCE_SUBSPACES[item['id']]:
            raise ValueError('Retained actual-frame subspace differs')
        literal = item['literal_spec']; name = FRAME_NAMES[item['id']]
        expected_words = {'I': [], 'A1': [['C_line', 1]], 'A7': [['C_line', 7]],
            'K8': [['C_line_inverse', 8], ['C_full', 4]],
            'K14': [['C_line_inverse', 14], ['C_full', 4]], 'F': [['C_full', 4]]}
        if name != 'E' and literal['word'] != expected_words[name]:
            raise ValueError('Retained source/sink/dirty literal frame word differs')
        if name == 'E' and literal['word'] != [['quadratic_phase', -1, 'weight-all-bits'],
             ['linear_route_inverse', [1, 6, 2, 8]], ['H_tilde', 2],
             ['linear_route', [1, 6, 2, 8]], ['quadratic_phase', -1, 'weight-all-bits']]:
            raise ValueError('Actual common-frame word differs from the independent literal definition')
        if matrix_digest(frames[name], item['coefficient_matrix_bits']) != item['coefficient_matrix_sha256']:
            raise ValueError('Independent frame coefficients differ from retained matrix hash')
    # E contains radical6; no nondegenerate-projector premise is imported.
    E = {0, 1, 6, 7}; perpendicular = {a for a in range(16) if all(not ((a & b).bit_count() & 1) for b in E)}
    expected_lagrangian = {z | (x << 4) for z in range(16) for x in E if z ^ x in perpendicular}
    if E & perpendicular != {0, 6} or pauli_subspace(frames['E']) != expected_lagrangian:
        raise ValueError('Literal common operator does not realize the stated degenerate L_E')
    transitions = {}; affine_negative = False; global_negative = False
    for item in case['transitions']:
        before, after = FRAME_NAMES[item['from_frame']], FRAME_NAMES[item['to_frame']]
        actual = g.matmul(frames[after], g.adjoint(frames[before]))
        candidate = reconstruct(item['one_child_normal_form'])
        rising = g.adjoint(actual) if item['execute_normal_form_inverse'] else actual
        if matrix_digest(rising, item['matrix_bits']) != item['rising_matrix_sha256']:
            raise ValueError('Independent rising transition coefficients differ from the retained matrix hash')
        if item['execute_normal_form_inverse']:
            candidate = g.adjoint(candidate)
        if candidate != actual:
            raise ValueError('Retained producer one-child interface differs from independent literal matrices')
        if item['one_child_normal_form']['output_affine_offset']:
            affine_negative |= reconstruct(item['one_child_normal_form'], 'omit affine offset') != reconstruct(item['one_child_normal_form'])
        if sum(item['one_child_normal_form'][side+'_quadratic']['constant'] for side in ('input', 'output')) % 4:
            global_negative |= reconstruct(item['one_child_normal_form'], 'omit global phase') != reconstruct(item['one_child_normal_form'])
        transitions[item['id']] = before+'->'+after
    translated = []
    for event in case['literal_physical_events']:
        kind = event[0]
        if kind == 'move':
            translated.append(('move', event[1], transitions[event[2]]))
        elif kind == 'add':
            translated.append(('add', event[1], event[2], Q(*event[3])))
        else:
            translated.append(('cut', event[1], tuple(event[3]), {0: 0, 1: 1, 4: 2, 8: 3}[event[2]]))
    word = [tuple(op[:-1]) if op[0] == 'add' else op for op in spec['operations']]
    if translated != word or not affine_negative or not global_negative:
        raise ValueError('Producer physical word or affine/global negative control differs')
    if {int(k): v for k, v in case['child_width_histogram'].items()} != spec['histogram']:
        raise ValueError('Actual event ledger differs from the retained producer histogram')
    return dict(reuse=case['reuse'], retained_transitions=len(transitions),
        literal_transition_coefficients=256*len(transitions), actual_frame_L_E_verified=True,
        common_radical=[6], exact_physical_word_matched=True,
        all_quadratic_tables_and_fourth_root_constants_bound=True,
        omitted_affine_route_rejected=affine_negative, omitted_global_phase_rejected=global_negative,
        producer_matrix_hashes_independently_recomputed=True,
        producer_matrix_hashes_used_as_authority=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(); config = json.loads(CONFIG.read_text())
    fixture = TOPIC/config['fixture']; helper = Path(independent.__file__).resolve(); arithmetic = Path(g.__file__).resolve()
    for path, digest in [(fixture, config['fixture_sha256']), (helper, config['independent_word_sha256']),
                         (arithmetic, config['gaussian_arithmetic_sha256'])]:
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Pinned fixture or independent source changed')
    data = json.loads(fixture.read_text())
    paths = [Path(__file__).resolve(), CONFIG, fixture, helper, arithmetic]
    hashes = {str(p.relative_to(TOPIC)): sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        source_config_fixture_sha256=hashes, seed=None, producer_imports=False,
        scope=config['scope'])
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    started = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(review, data['cases']))
    if any(sha256((TOPIC/path).read_bytes()).hexdigest() != digest for path, digest in hashes.items()):
        raise ValueError('Source changed during immutable fixture review')
    result = dict(status='INDEPENDENT DEGENERATE BIRTH FIXTURE BINDING PASS', cases=rows,
        seconds=time.monotonic()-started, scope=config['scope'], formal_or_native_proof=False)
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'seconds', 'scope')}))


if __name__ == '__main__':
    main()
