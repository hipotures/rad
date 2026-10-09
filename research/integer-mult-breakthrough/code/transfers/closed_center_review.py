#!/usr/bin/env python3
"""Independent literal interfaces and arbitrary-dirty central-release controls.

No synthesis/complex producer module is imported. Small controls use independently
specified invertible scalar matrices and column-major address coordinates. The
all-size program identity is an analytic lemma, not a native tape certificate.
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

import conditioned_frame_review as arithmetic


TOPIC = Path(__file__).resolve().parents[2]
CONFIG = TOPIC/'configs/transfers/closed-center-review.json'
ZERO, ONE = arithmetic.ZERO, arithmetic.ONE
ALPHA, BETA = (Q(1, 2), Q(1, 2)), (Q(1, 2), Q(-1, 2))
UNITS = [ONE, (Q(0), Q(1)), (Q(-1), Q(0)), (Q(0), Q(-1))]
add, mul = arithmetic.add, arithmetic.multiply


def scale(z, c):
    return z[0]*c, z[1]*c


def vector_add(a, b, c=Q(1)):
    return [add(x, scale(y, c)) for x, y in zip(a, b)]


def inverse(matrix):
    n = len(matrix)
    rows = [list(row)+[Q(int(i == j)) for j in range(n)] for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if rows[i][j])
        rows[j], rows[pivot] = rows[pivot], rows[j]
        coefficient = rows[j][j]
        rows[j] = [x/coefficient for x in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                coefficient = rows[i][j]
                rows[i] = [a-coefficient*b for a, b in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def bank_matrix(matrix, values):
    size = len(values[0])
    return [[arithmetic.sum_complex(scale(values[j][a], coefficient)
             for j, coefficient in enumerate(row) if coefficient)
             for a in range(size)] for row in matrix]


def transform(values, h, columns, label=None, undo=False):
    """Literal 2x2 Gaussian gates, with bit j+column*h address convention."""
    data = list(values)
    masks = [1 << j for j in range(h*columns)] if label is None else [label << (c*h) for c in range(columns)]
    lo, hi = (BETA, ALPHA) if undo else (ALPHA, BETA)
    for mask in masks:
        for a in range(len(data)):
            b = a ^ mask
            if a < b:
                x, y = data[a], data[b]
                data[a] = add(mul(lo, x), mul(hi, y))
                data[b] = add(mul(hi, x), mul(lo, y))
    return data


def relative(values, label, h, columns):
    return transform(transform(values, h, columns, label, True), h, columns)


def scatter(targets, features, decoder, sign):
    return [arithmetic.sum_complex([])] if not targets else [
        [add(target[a], arithmetic.sum_complex(scale(features[j][a], sign*c)
         for j, c in enumerate(row) if c)) for a in range(len(target))]
        for target, row in zip(targets, decoder)]


def program(spec, initial, missing_return=False, powered_decoder=False):
    h, columns, labels, basis, decoder = (spec[k] for k in ['h', 'columns', 'labels', 'basis', 'decoder'])
    q = len(decoder[0]); bi = inverse(basis)
    x, y, z = [[list(row) for row in group] for group in initial]
    if powered_decoder:
        decoder = [[c**columns for c in row] for row in decoder]
    # Early echo at the common literal identity operator.
    z = bank_matrix(basis, z); y = scatter(y, z[:q], decoder, Q(-1)); z = bank_matrix(bi, z)
    # Matching source-line injection, followed by a literal common full operator.
    z = [vector_add(transform(row, h, columns, label), source)
         for row, source, label in zip(z, x, labels)]
    z = [relative(row, label, h, columns) for row, label in zip(z, labels)]
    z = bank_matrix(basis, z)
    for j in range(q):
        z[j] = transform(z[j], h, columns, undo=True)
    y = scatter(y, z[:q], decoder, Q(1))
    for j in range(q):
        if not (missing_return and j == 0):
            z[j] = transform(z[j], h, columns)
    z = bank_matrix(bi, z)
    x = [relative(row, label, h, columns) for row, label in zip(x, labels)]
    z = [vector_add(row, source, Q(-1)) for row, source in zip(z, x)]
    y = [relative(row, label, h, columns) for row, label in zip(y, labels)]
    return [x, y, z]


def endpoint(spec, initial):
    h, columns, labels, basis, decoder = (spec[k] for k in ['h', 'columns', 'labels', 'basis', 'decoder'])
    x, y, z = initial
    virtual = [transform(row, h, columns, label, True) for row, label in zip(x, labels)]
    q = len(decoder[0])
    # Direct independent endpoint K=D*G; this expression has no dirty echo.
    K = [[sum(c*basis[j][s] for j, c in enumerate(row)) for s in range(len(labels))] for row in decoder]
    addition = bank_matrix(K, virtual)
    return [[transform(row, h, columns) for row in virtual],
        [relative(vector_add(row, extra), label, h, columns) for row, extra, label in zip(y, addition, labels)],
        [transform(row, h, columns) for row in z]]


def small_spec(name):
    if name.startswith('color'):
        return dict(name=name, h=3, columns=2 if name.endswith('f2') else 1,
            labels=[1, 2, 4], basis=[[Q(1), Q(1), Q(1)], [Q(0), Q(1), Q(0)], [Q(0), Q(0), Q(1)]],
            decoder=[[Q(1)] for _ in range(3)])
    return dict(name=name, h=2, columns=2, labels=[1, 2],
        basis=[[Q(1), Q(1)], [Q(0), Q(1)]], decoder=[[Q(3, 8)], [Q(-1, 4)]])


def finite_case(name):
    spec = small_spec(name); size = 1 << (spec['h']*spec['columns']); v = len(spec['labels'])
    columns = range(size) if name != 'color-f2' else range(1)
    checked = 0
    for group in range(3):
        for bank in range(v):
            for address in columns:
                initial = [[[ZERO]*size for _ in range(v)] for _ in range(3)]
                initial[group][bank][address] = ONE
                if program(spec, initial) != endpoint(spec, initial):
                    raise ValueError('Literal arbitrary-dirty physical endpoint differs')
                checked += 1
    dirty = [[[(Q((i*7+b*3+g) % 19-9, 8), Q((i*5+b+g*3) % 17-8, 16))
              for i in range(size)] for b in range(v)] for g in range(3)]
    expected = endpoint(spec, dirty)
    if program(spec, dirty) != expected:
        raise ValueError('Full nonzero Gaussian-dyadic field differs')
    if program(spec, dirty, missing_return=True) == expected:
        raise ValueError('Missing full-width return was accepted')
    if expected[2] == dirty[2]:
        raise ValueError('Raw identity dirty endpoint control was not discriminating')
    powered_rejected = None
    if name == 'dyadic-f2':
        powered_rejected = program(spec, dirty, powered_decoder=True) != expected
        if not powered_rejected:
            raise ValueError('Coefficient tensor-power error was accepted')
    # Test a nontrivial simultaneous XOR, with exact endpoint covariance. The
    # all-address covariance itself follows from each literal convolution gate.
    displacement = (1 << (spec['h']*spec['columns']))-3
    translated = [[[row[a ^ displacement] for a in range(size)] for row in group] for group in dirty]
    translated_result = program(spec, translated)
    if translated_result != [[[row[a ^ displacement] for a in range(size)] for row in group] for group in expected]:
        raise ValueError('Simultaneous XOR covariance failed')
    return dict(name=name, actual_initial_columns=checked,
        covariance_determined_columns=3*v*size, address_convention='column-major bit j+column*h',
        full_dirty_fields=1, missing_feature_return_rejected=True, raw_identity_dirty_endpoint_rejected=True,
        powered_decoder_rejected=powered_rejected, generic_scalar_matrix=True,
        scope='Finite literal controls for the generic central lemma; no single-total whole physical word replay')


def integer_mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def integer_unit(phase):
    return [(1, 0), (0, 1), (-1, 0), (0, -1)][phase % 4]


def integer_power(rank):
    value = (1, 0)
    for _ in range(rank):
        value = integer_mul(value, (1, 1))
    return value


def embed(coordinate, columns):
    value = 0
    for j, column in enumerate(columns):
        if coordinate >> j & 1:
            value ^= column
    return value


def phase_interfaces(h=7, labels=None):
    labels = labels or [sum(1 << j for j in subset) for subset in combinations(range(h), 5)]
    entries, blocks, records, phase_required = 0, 0, [], False
    full_numerator = [integer_mul(integer_power(h), integer_unit(-d.bit_count())) for d in range(1 << h)]
    child_numerator = [integer_mul(integer_power(h-1), integer_unit(-d.bit_count())) for d in range(1 << (h-1))]
    for label in labels:
        if label.bit_count() % 4 != 1:
            raise ValueError('No-offset frame has the wrong support coset')
        pivot = (label & -label).bit_length()-1
        S = [(1 << j) ^ ((1 << pivot) if label >> j & 1 else 0) for j in range(h) if j != pivot]
        all_vectors = [embed(a, S) for a in range(1 << (h-1))]
        dual = []
        for j in range(h-1):
            candidates = [a for a in all_vectors if sum(((a & s).bit_count() & 1) << i for i, s in enumerate(S)) == 1 << j]
            if len(candidates) != 1:
                raise ValueError('Restricted perpendicular form is not invertible')
            dual.append(candidates[0])
        if sorted(embed(a, S+[label]) for a in range(1 << h)) != list(range(1 << h)) or \
                sorted(embed(a, dual+[label]) for a in range(1 << h)) != list(range(1 << h)):
            raise ValueError('Input/output affine routing loses complete records')
        for output in range(1 << h):
            for input_ in range(1 << h):
                d = output ^ input_
                # Literal beta*F(d)+alpha*F(d xorT), common denominator2^(h+1).
                left, right = integer_mul((1, -1), full_numerator[d]), integer_mul((1, 1), full_numerator[d ^ label])
                actual = left[0]+right[0], left[1]+right[1]
                target = (2*left[0], 2*left[1]) if not ((d & label).bit_count() & 1) else (0, 0)
                if actual != target:
                    raise ValueError('Actual Gaussian relative frame support/phase failed')
                entries += 1
        for a in range(1 << (h-1)):
            da = embed(a, S)
            for b in range(1 << (h-1)):
                db = embed(b, dual)
                actual = integer_mul((1, -1), full_numerator[da ^ db])
                # common denominator2^h; C_(h-1) numerator is multiplied by2.
                phase = -(da.bit_count()-a.bit_count()+db.bit_count()-b.bit_count())
                child = integer_mul(child_numerator[a ^ b], integer_unit(phase))
                if actual != (2*child[0], 2*child[1]):
                    raise ValueError('One-child chirp/dual routing normal form failed')
                if actual != (2*child_numerator[a ^ b][0], 2*child_numerator[a ^ b][1]):
                    phase_required = True
                blocks += 1
        records.append(dict(label=label, output_columns=S+[label], input_columns=dual+[label],
            child_width=h-1, quotient_blocks=2, global_unit='1', input_and_output_chirps_paid=True))
    if not phase_required:
        raise ValueError('Omitted-chirp control was not discriminating')
    # Weight3 has odd support coset. This is an exact rejection of only the
    # no-offset adapter; a paid affine-offset adapter can still exist.
    wrong_label, wrong_h = 7, 3
    p = integer_power(wrong_h); at_zero = p
    shifted = integer_mul(p, integer_unit(-wrong_label.bit_count()))
    a, b = integer_mul((1, -1), at_zero), integer_mul((1, 1), shifted)
    if (a[0]+b[0], a[1]+b[1]) != (0, 0) or integer_mul((1, -1), p) == (0, 0):
        raise ValueError('Weight3 no-offset negative control failed')
    return dict(name='single-total-h7-relative-interfaces', dimension=h, labels=len(labels),
        literal_gaussian_matrix_entries=entries, routed_child_block_entries=blocks,
        complete_routing_records=records, omitted_chirps_rejected=True,
        weight3_no_offset_rejected=True, full_inverse_interface='C_h^*=C_h X_allones, one full child plus paid translation')


def dispatch(name):
    return phase_interfaces() if name == 'phase-h7' else finite_case(name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--small', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text())
    helper = Path(arithmetic.__file__).resolve()
    if sha256(helper.read_bytes()).hexdigest() != config['arithmetic_sha256']:
        raise ValueError('Independent Gaussian arithmetic source changed')
    paths = [Path(__file__).resolve(), helper, CONFIG]
    hashes = {str(p.relative_to(TOPIC)): sha256(p.read_bytes()).hexdigest() for p in paths}
    tasks = ['color-f1', 'dyadic-f2', 'phase-h7'] if args.small else ['color-f1', 'color-f2', 'dyadic-f2', 'phase-h7']
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        effective_source_config_sha256=hashes, tasks=tasks, seed=None, scope=config['scope'])
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    started = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(dispatch, tasks))
    ledger = []
    for h in [7, 8, 20, 28, 30]:
        v, q = comb(h, 5), comb(h, 2)
        W = 3*v
        charge = v+3*v*(h-1)+2*q*h
        if charge != W*h-2*v+2*q*h:
            raise ValueError('Complete central ledger failed')
        ledger.append(dict(h=h, v=v, q=q, stock=W, child_multiplicities={1:v,h-1:3*v,h:2*q},
            rank_charge=charge, endpoint_floor=W*h-2*v, deficit=W*h-charge,
            same_width_mass=str(Q(2*q, W)), scope='Central component only'))
    if any(sha256((TOPIC/p).read_bytes()).hexdigest() != digest for p, digest in hashes.items()):
        raise ValueError('Source or config changed during immutable attempt')
    receipt = dict(status='INDEPENDENT CENTRAL RELEASE CONTROLS PASS', results=results,
        central_ledger=ledger, seconds=time.monotonic()-started, scope=config['scope'],
        explicit_single_total_whole_physical_replay=False, native_tape_or_guard_certificate=False,
        larger_exponent_claim=False)
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['status','seconds','scope']}))


if __name__ == '__main__':
    main()
