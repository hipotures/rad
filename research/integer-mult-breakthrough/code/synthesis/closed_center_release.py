#!/usr/bin/env python3
"""Literal arbitrary-dirty center echo with exactly 2*q*h closed release.

This component adds Kx rather than x. B is an in-place invertible center/null
basis on v dirty helpers and K=D*first_q_rows(B). Early zero-frame and late
full-frame B words remove the initial dirty image. Only the q feature banks
are reset to zero for the late scatter, then restored to full before cleanup.
All source, sink and dirty physical endpoints are retained.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import importlib
import json
from math import comb
from pathlib import Path
import sys
import time

import global_word_frame_search as f
import literal_bank_exchange_control as bank
import pauli_tensor_discriminator as g

COMPLEX = Path(__file__).resolve().parents[1] / 'complex'
sys.path.insert(0, str(COMPLEX))
total = importlib.import_module('total_center_basis')


def component(kind, h):
    if kind == 'orthogonal-color':
        labels = [1 << j for j in range(h)]
        B = [('add', 0, j, Q(1)) for j in range(1, h)]
        return dict(kind=kind, h=h, labels=labels, q=1, basis=B,
                    decoder=[[Q(1)] for _ in labels], central=lambda a, b: Q(1))
    if kind == 'single-total':
        compiled = total.complete_word(h)
        labels = [sum(1 << j for j in source) for source in compiled['source_order']]
        decoder = [[Q(value, 32) for value in total.decoder_numerators(compiled['pair_order'], source)]
                   for source in compiled['source_order']]
        return dict(kind=kind, h=h, labels=labels, q=compiled['center_rank'],
                    basis=[tuple(event) for event in compiled['word']], decoder=decoder,
                    central=lambda a, b: Q(((a & b).bit_count() - 1) * ((a & b).bit_count() - 3), 8))
    raise ValueError('Unknown center family')


def apply_basis(word, values, inverse=False):
    for event in bank.invert(word) if inverse else word:
        kind, a, *rest = event
        if kind == 'swap':
            b, = rest
            values[a], values[b] = values[b], values[a]
        elif kind == 'scale':
            c, = rest
            values[a] = [g.scale(z, c) for z in values[a]]
        else:
            b, c = rest
            values[a] = [g.add(z, g.scale(value, c)) for z, value in zip(values[a], values[b])]


def c_full(values, h, columns, inverse=False):
    data = list(values)
    lo, hi = (g.BETA, g.ALPHA) if inverse else (g.ALPHA, g.BETA)
    for bit in range(h * columns):
        mask = 1 << bit
        for a in range(len(data)):
            if a & mask:
                continue
            b = a | mask
            x, y = data[a], data[b]
            data[a] = g.add(g.mul(lo, x), g.mul(hi, y))
            data[b] = g.add(g.mul(hi, x), g.mul(lo, y))
    return data


def c_line(values, label, h, columns, inverse=False):
    data = list(values)
    lo, hi = (g.BETA, g.ALPHA) if inverse else (g.ALPHA, g.BETA)
    for column in range(columns):
        mask = sum(((label >> bank_id) & 1) << (bank_id * columns + column) for bank_id in range(h))
        for a in range(len(data)):
            b = a ^ mask
            if a > b:
                continue
            x, y = data[a], data[b]
            data[a] = g.add(g.mul(lo, x), g.mul(hi, y))
            data[b] = g.add(g.mul(hi, x), g.mul(lo, y))
    return data


def to_kernel(values, label, h, columns):
    return c_full(c_line(values, label, h, columns, True), h, columns)


def scatter(y, r, decoder, sign):
    for target, coefficients in enumerate(decoder):
        for feature, coefficient in enumerate(coefficients):
            if coefficient:
                c = coefficient * sign
                y[target] = [g.add(z, g.scale(value, c)) for z, value in zip(y[target], r[feature])]


def scalar_columns(spec):
    # independent rational row replay; physical matrix code is not used.
    v = len(spec['labels'])
    rows = [{j: Q(1)} for j in range(3 * v)]
    def basis(inverse=False):
        for event in bank.invert(spec['basis']) if inverse else spec['basis']:
            kind, a, *rest = event
            a += 2 * v
            if kind == 'swap':
                b, = rest; b += 2 * v
                rows[a], rows[b] = rows[b], rows[a]
            elif kind == 'scale':
                c, = rest
                rows[a] = {j: value * c for j, value in rows[a].items() if value * c}
            else:
                b, c = rest; add(a, 2 * v + b, c)
    def add(a, b, c):
        for j, value in list(rows[b].items()):
            updated = rows[a].get(j, Q()) + c * value
            if updated:
                rows[a][j] = updated
            else:
                rows[a].pop(j, None)
    def copy(sign):
        for target, coefficients in enumerate(spec['decoder']):
            for feature, coefficient in enumerate(coefficients):
                if coefficient:
                    add(v + target, 2 * v + feature, sign * coefficient)
    basis(); copy(-1); basis(True)
    for j in range(v):
        add(2 * v + j, j, Q(1))
    basis(); copy(1); basis(True)
    for j in range(v):
        add(2 * v + j, j, Q(-1))
    expected = [{j: Q(1)} for j in range(3 * v)]
    for target, a in enumerate(spec['labels']):
        for source, b in enumerate(spec['labels']):
            coefficient = spec['central'](a, b)
            if coefficient:
                expected[v + target][source] = coefficient
    if rows != expected:
        raise ValueError('All independent source/sink/dirty scalar columns failed')
    return dict(all_initial_columns=3 * v, independent_source_columns=v,
                arbitrary_sink_columns=v, arbitrary_dirty_columns=v,
                source_and_virtual_dirty_fully_restored=True, sink_addition='Kx only')


def execute(spec, initial, columns, omit_feature_return=False):
    h = spec['h']; v = len(spec['labels']); q = spec['q']
    x, y, r = [[list(row) for row in group] for group in initial]
    # B and its inverse see the identical actual identity Gaussian operator.
    apply_basis(spec['basis'], r)
    scatter(y, r, spec['decoder'], -1)
    apply_basis(spec['basis'], r, True)
    for j, label in enumerate(spec['labels']):
        r[j] = c_line(r[j], label, h, columns)
        r[j] = [g.add(a, b) for a, b in zip(r[j], x[j])]
    # Every helper enters the same literal full C_h tensor columns operator.
    for j, label in enumerate(spec['labels']):
        r[j] = to_kernel(r[j], label, h, columns)
    apply_basis(spec['basis'], r)
    # The full-width inverse is actual C_h^*, equivalently C_h followed by
    # the selected all-ones address translation, not a free metadata reset.
    for j in range(q):
        r[j] = c_full(r[j], h, columns, True)
    scatter(y, r, spec['decoder'], 1)
    for j in range(q):
        if not (omit_feature_return and j == 0):
            r[j] = c_full(r[j], h, columns)
    apply_basis(spec['basis'], r, True)
    for j, label in enumerate(spec['labels']):
        x[j] = to_kernel(x[j], label, h, columns)
        r[j] = [g.add(a, g.neg(b)) for a, b in zip(r[j], x[j])]
        y[j] = to_kernel(y[j], label, h, columns)
    return x, y, r


def expected(spec, initial, columns):
    h = spec['h']; v = len(spec['labels'])
    old_x, old_y, old_r = initial
    virtual_x = [c_line(values, label, h, columns, True)
                 for label, values in zip(spec['labels'], old_x)]
    y = [list(values) for values in old_y]
    # Independent center polynomial/class matrix, not the producer decoder.
    for target, a in enumerate(spec['labels']):
        for source, b in enumerate(spec['labels']):
            coefficient = spec['central'](a, b)
            if coefficient:
                y[target] = [g.add(z, g.scale(value, coefficient))
                             for z, value in zip(y[target], virtual_x[source])]
    return ([c_full(values, h, columns) for values in virtual_x],
            [to_kernel(values, label, h, columns) for label, values in zip(spec['labels'], y)],
            [c_full(values, h, columns) for values in old_r])


def matrix_controls(spec):
    h = spec['h']; size = 1 << h
    C = g.tensor_c(h)
    result = []
    for T in sorted(set(spec['labels'])):
        if T.bit_count() % 4 != 1:
            raise ValueError('This exact no-offset interface assumes odd weight1 mod4')
        S = f.perpendicular((T,), h)
        gram = tuple(sum(((a & b).bit_count() % 2) << i for i, a in enumerate(S)) for b in S)
        inverse_columns = []
        for j in range(h - 1):
            # Small finite dual coordinates; the all-h proof uses the exact
            # invertibility of the restricted dot form on T-perp.
            solutions = [value for value in range(1 << (h - 1))
                         if sum(((row & value).bit_count() % 2) << i for i, row in enumerate(gram)) == 1 << j]
            if len(solutions) != 1:
                raise ValueError('Odd-normal perpendicular form is not invertible')
            inverse_columns.append(solutions[0])
        dual = tuple(_embed(value, S) for value in inverse_columns)
        if any((a & b).bit_count() % 2 != int(i == j) for i, a in enumerate(S) for j, b in enumerate(dual)):
            raise ValueError('Paid dual affine input/output routing failed')
        child = g.tensor_c(h - 1)
        units = [g.ONE, (Q(0), Q(1)), (Q(-1), Q(0)), (Q(0), Q(-1))]
        checked = 0
        for a in range(size):
            for b in range(size):
                delta = a ^ b
                actual = g.add(g.mul(g.BETA, C[delta][0]), g.mul(g.ALPHA, C[delta ^ T][0]))
                target = g.scale(g.mul(g.BETA, C[delta][0]), 2) if (delta & T).bit_count() % 2 == 0 else g.ZERO
                if actual != target:
                    raise ValueError('Literal full-to-line-kernel convolution failed')
                checked += 1
        r = h - 1
        for a in range(1 << r):
            for b in range(1 << r):
                da, db = _embed(a, S), _embed(b, dual)
                delta = da ^ db
                actual = g.scale(g.mul(g.BETA, C[delta][0]), 2)
                out_phase = units[(-(da.bit_count() - a.bit_count())) % 4]
                in_phase = units[(-(db.bit_count() - b.bit_count())) % 4]
                if g.mul(g.mul(out_phase, child[a][b]), in_phase) != actual:
                    raise ValueError('Single-child relative rank interface reconstruction failed')
        result.append(dict(label=T, incoming_line_rank=1, relative_child_width=h - 1,
                           output_columns=S + (T,), input_columns=dual + (T,),
                           output_phase_formula='-(weight(S*a)-weight(a)) mod4',
                           input_phase_formula='-(weight(dual*b)-weight(b)) mod4',
                           kernel_entries_checked=checked, normal_form_entries_checked=1 << (2 * r)))
    return result


def _embed(value, columns):
    result = 0
    for j, column in enumerate(columns):
        if value >> j & 1:
            result ^= column
    return result


def physical_probe(spec, columns, full_columns):
    h = spec['h']; v = len(spec['labels']); size = 1 << (h * columns)
    digest = sha256(); checked = 0
    # Every operation commutes with the same address XOR translation on all
    # banks: C_line/C_full are convolutions, and all basis/scatter operations
    # are constant coefficients or raw bank exchanges. Origin-address basis
    # columns therefore determine the complete translation-invariant matrix.
    for role in range(3 * v):
        for address in range(size) if full_columns else (0,):
            data = [[g.ONE if bank_id == role and a == address else g.ZERO for a in range(size)]
                    for bank_id in range(3 * v)]
            initial = (data[:v], data[v:2 * v], data[2 * v:])
            observed = execute(spec, initial, columns)
            wanted = expected(spec, initial, columns)
            if observed != wanted:
                raise ValueError('Complete physical source/sink/dirty center operator failed')
            digest.update(json.dumps([[g.text_complex(z) for values in group for z in values]
                                     for group in observed], separators=(',', ':')).encode())
            checked += 1
    # A required outgoing full-width operation cannot be omitted. One dirty
    # feature input already supplies an exact physical counterexample.
    data = [[g.ONE if bank_id == 2 * v and a == 0 else g.ZERO for a in range(size)]
            for bank_id in range(3 * v)]
    initial = (data[:v], data[v:2 * v], data[2 * v:])
    if execute(spec, initial, columns, True) == expected(spec, initial, columns):
        raise ValueError('Omitted full-width feature return was not detected')
    return dict(status='EXACT LITERAL CENTER OPERATOR PASS', columns=columns,
                address_volume=size, explicitly_replayed_initial_columns=checked,
                complete_initial_columns=3 * v * size,
                coverage='Every address basis column explicitly replayed' if full_columns else 'One origin-address column per bank plus proved common-XOR translation covariance',
                physical_source_final='F_full * initial virtual source',
                physical_sink_final='F_kernel(T) * (initial virtual sink + Kx)',
                physical_dirty_final='F_full * initial virtual dirty, not identity on raw dirty input',
                omitted_feature_return_detected=True, output_sha256=digest.hexdigest())


def ledger(h, v, q):
    hist = Counter()
    hist[1] += v
    hist[h - 1] += 3 * v
    hist[h] += 2 * q
    stock = 3 * v
    charge = sum(width * count for width, count in hist.items())
    if charge != stock * h - 2 * v + 2 * q * h:
        raise ValueError('Complete center endpoint/release ledger failed')
    return dict(payload_stock=stock, capacity=stock * h, endpoint_rank_floor=stock * h - 2 * v,
                rank_charge=charge, deficit=stock * h - charge,
                closed_feature_release=2 * q * h,
                child_width_histogram=dict(sorted(hist.items())), full_width_child_calls=2 * q,
                full_width_self_mass=Q(2 * q, stock),
                scope='Actual declared central-component frame chronology; not the full y+=x circuit or a multiplier exponent profile.')


def probe(case):
    kind, h, columns, mode = case
    started = time.monotonic(); spec = component(kind, h)
    v = len(spec['labels']); q = spec['q']
    scalar = scalar_columns(spec)
    controls = matrix_controls(spec) if mode != 'scalar-only' else []
    physical = physical_probe(spec, columns, mode == 'all-columns') if mode != 'scalar-only' else None
    return dict(status='PASS EXPLICIT CLOSED CENTER RELEASE', family=kind, h=h, columns=columns,
                vertices=v, center_rank=q, scalar_columns=scalar,
                basis_operation_counts=dict(Counter(e[0] for e in spec['basis'])),
                basis_calls=4, scatter_calls=2,
                scatter_nonzero_coefficients=sum(bool(c) for row in spec['decoder'] for c in row),
                source_injections=2 * v, phase_edge_controls=controls,
                physical_operator=physical, actual_chronology=ledger(h, v, q),
                seconds=time.monotonic() - started,
                obligations=['Add the side I-K contribution with the same labeled endpoints',
                             'Count all source/sink returns forced by a combined chronology',
                             'Pay native basis/scatter scales, raw exchanges, affine address routing and chirps',
                             'Prove bounded precision, storage and complete end-to-end recurrence'],
                scope='Center-only Kx component with fully arbitrary source/sink/dirty values. The complete scalar and explicit Gaussian frame equations retain all virtual restoration and physical F_full dirty outputs. Finite operator coverage is stated per case. No larger kappa is asserted.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    cases = [('orthogonal-color', 3, 1, 'all-columns'),
             ('orthogonal-color', 3, 2, 'origin-columns'),
             ('single-total', 7, 1, 'origin-columns'),
             ('single-total', 8, 1, 'scalar-only')]
    source_paths = [Path(__file__), Path(bank.__file__), Path(g.__file__), Path(f.__file__),
                    Path(f.__file__).with_name('lagrangian_graph_completion.py'),
                    Path(f.__file__).with_name('trimmed_zeta_dirty_probe.py'), f.SIDE_SOURCE]
    source_paths += [COMPLEX / name for name in ('total_center_basis.py', 'total_center_capacity.py',
                    'center_native_leverage.py', 'characteristic.py', 'center_basis_scalar_word.py',
                    'structured_center_basis.py', 'center_null_basis.py')]
    hashes = {path: sha256(path.read_bytes()).hexdigest() for path in source_paths}
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    native_threads_each=1, specs=cases,
                    source_sha256={path.name: value for path, value in hashes.items()},
                    hypothesis='Exact closed full-width release of q feature banks replaces a center-only chronology; side integration remains open.')
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs = {pool.submit(probe, case): case for case in cases}
        for future in as_completed(jobs):
            result = future.result(); results.append(result)
            print(json.dumps({key: result[key] for key in ('status', 'family', 'h', 'columns', 'seconds')}
                             | {'rank_charge':result['actual_chronology']['rank_charge']}), flush=True)
    if any(sha256(path.read_bytes()).hexdigest() != value for path, value in hashes.items()):
        raise ValueError('Effective source changed during center-release experiment')
    (args.output / 'certificate.json').write_text(json.dumps(dict(cases=results), indent=2, default=str) + '\n')


if __name__ == '__main__':
    main()
