#!/usr/bin/env python3
"""Literal center plus full-materialized side dirty echo, with no deficit.

The source and sink each follow their single endpoint geodesic. Early dirty
echoes share the sink's zero frame. Late side outputs make closed rank-one
excursions, explicitly removing the center component's endpoint saving.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

import closed_center_release as c
import trimmed_zeta_dirty_probe as z

g = c.g


def side_spec(center):
    v = len(center['labels'])
    if center['kind'] == 'single-total':
        dag = z.side.build_dag(center['h'], 5)
        order = {label: j for j, label in enumerate(center['labels'])}
        # The input and target payload banks have the SAME order as the actual
        # total-center word, not an uncharged substitution of lexicographic slots.
        permutation = [order[label] for label in dag['top']]
        def role(i):
            return permutation[i] if i < v else i
        edges = [(role(a), role(b), coeff) for a, b, coeff in z.mixer_edges(dag)]
        outputs = [None] * v
        for j, output in enumerate(dag['outputs']):
            outputs[permutation[j]] = role(output)
        return dict(roles=len(dag['nodes']), edges=edges, outputs=outputs,
                    family='trimmed Newton/Yates side', input_order_reindexed=True)
    # Exact clean SSA for I-J: each output is the negative sum of the other
    # sources. Separate dirty accumulator roles make the mixer reversible.
    edges = []; outputs = []; roles = v
    for target in range(v):
        role = roles; roles += 1
        for source in range(v):
            if source != target:
                edges.append((role, source, Q(-1)))
        outputs.append(role)
    return dict(roles=roles, edges=edges, outputs=outputs,
                family='orthogonal-color I-J accumulators', input_order_reindexed=True)


def mix(values, side, inverse=False):
    for a, b, coeff in reversed(side['edges']) if inverse else side['edges']:
        coeff = -coeff if inverse else coeff
        values[a] = [g.add(x, g.scale(y, coeff)) for x, y in zip(values[a], values[b])]


def side_scatter(y, a, side, sign):
    for target, output in enumerate(side['outputs']):
        y[target] = [g.add(x, g.scale(z, sign)) for x, z in zip(y[target], a[output])]


def execute(center, side, initial, columns, omit_output_return=False):
    h = center['h']; v = len(center['labels']); q = center['q']
    x, y, r, a = [[list(values) for values in group] for group in initial]
    # The two early negative scatters take place at the identical actual I
    # operator. Their inverse words restore every arbitrary dirty helper.
    c.apply_basis(center['basis'], r)
    c.scatter(y, r, center['decoder'], -1)
    c.apply_basis(center['basis'], r, True)
    mix(a, side); side_scatter(y, a, side, -1); mix(a, side, True)
    for j, label in enumerate(center['labels']):
        r[j] = c.c_line(r[j], label, h, columns)
        a[j] = c.c_line(a[j], label, h, columns)
        r[j] = [g.add(z, value) for z, value in zip(r[j], x[j])]
        a[j] = [g.add(z, value) for z, value in zip(a[j], x[j])]
        r[j] = c.to_kernel(r[j], label, h, columns)
        a[j] = c.to_kernel(a[j], label, h, columns)
    for j in range(v, side['roles']):
        a[j] = c.c_full(a[j], h, columns)
    # Central features reset to I while the sinks are still at I.
    c.apply_basis(center['basis'], r)
    for j in range(q):
        r[j] = c.c_full(r[j], h, columns, True)
    c.scatter(y, r, center['decoder'], 1)
    for j in range(q):
        r[j] = c.c_full(r[j], h, columns)
    c.apply_basis(center['basis'], r, True)
    for j, label in enumerate(center['labels']):
        y[j] = c.to_kernel(y[j], label, h, columns)
    # Every SSA gate sees the literal SAME full Gaussian operator. Each final
    # side role then descends to its sink's kernel and RETURNS before inverse M.
    mix(a, side)
    for target, output in enumerate(side['outputs']):
        label = center['labels'][target]
        a[output] = c.c_line(a[output], label, h, columns, True)
        y[target] = [g.add(z, value) for z, value in zip(y[target], a[output])]
        if not (omit_output_return and target == 0):
            a[output] = c.c_line(a[output], label, h, columns)
    mix(a, side, True)
    for j, label in enumerate(center['labels']):
        x[j] = c.to_kernel(x[j], label, h, columns)
        r[j] = [g.add(z, g.neg(value)) for z, value in zip(r[j], x[j])]
        a[j] = [g.add(z, g.neg(value)) for z, value in zip(a[j], x[j])]
    return x, y, r, a


def expected(center, side, initial, columns):
    h = center['h']
    old_x, old_y, old_r, old_a = initial
    vx = [c.c_line(values, label, h, columns, True)
          for label, values in zip(center['labels'], old_x)]
    vy = [[g.add(y, x) for y, x in zip(ys, xs)] for ys, xs in zip(old_y, vx)]
    return ([c.c_full(values, h, columns) for values in vx],
            [c.to_kernel(values, label, h, columns) for label, values in zip(center['labels'], vy)],
            [c.c_full(values, h, columns) for values in old_r],
            [c.c_full(values, h, columns) for values in old_a])


def scalar_replay(center, side):
    v = len(center['labels']); r = side['roles']; stock = 3 * v + r
    rows = [{j: Q(1)} for j in range(stock)]
    def add(a, b, coeff):
        for column, value in list(rows[b].items()):
            new = rows[a].get(column, Q(0)) + coeff * value
            if new:
                rows[a][column] = new
            else:
                rows[a].pop(column, None)
    def basis(inverse=False):
        for event in c.bank.invert(center['basis']) if inverse else center['basis']:
            kind, a, *rest = event; a += 2 * v
            if kind == 'swap':
                b, = rest; b += 2 * v; rows[a], rows[b] = rows[b], rows[a]
            elif kind == 'scale':
                coeff, = rest; rows[a] = {j: value * coeff for j, value in rows[a].items() if value * coeff}
            else:
                b, coeff = rest; add(a, 2 * v + b, coeff)
    def central_scatter(sign):
        for target, coefficients in enumerate(center['decoder']):
            for feature, coeff in enumerate(coefficients):
                if coeff:
                    add(v + target, 2 * v + feature, sign * coeff)
    def mixer(inverse=False):
        for a, b, coeff in reversed(side['edges']) if inverse else side['edges']:
            add(3 * v + a, 3 * v + b, -coeff if inverse else coeff)
    def scatter(sign):
        for target, output in enumerate(side['outputs']):
            add(v + target, 3 * v + output, Q(sign))
    basis(); central_scatter(-1); basis(True)
    mixer(); scatter(-1); mixer(True)
    for j in range(v):
        add(2 * v + j, j, Q(1)); add(3 * v + j, j, Q(1))
    basis(); central_scatter(1); basis(True)
    mixer(); scatter(1); mixer(True)
    for j in range(v):
        add(2 * v + j, j, Q(-1)); add(3 * v + j, j, Q(-1))
    wanted = [{j: Q(1)} for j in range(stock)]
    for j in range(v):
        wanted[v + j][j] = Q(1)
    if rows != wanted:
        raise ValueError('Complete center+side arbitrary-dirty scalar operator failed')
    return dict(all_initial_columns=stock, source_columns=v, sink_columns=v,
                central_dirty_columns=v, side_dirty_columns=r,
                all_sources_and_virtual_dirty_restored=True, sink_addition='x exactly')


def ledger(h, v, q, r):
    stock = 3 * v + r
    hist = Counter()
    hist[1] += 4 * v
    hist[h - 1] += 4 * v
    hist[h] += r - v + 2 * q
    charge = sum(width * count for width, count in hist.items())
    if charge != stock * h + 2 * q * h:
        raise ValueError('Literal full-side output/center release ledger is incomplete')
    return dict(payload_stock=stock, capacity=stock * h,
                endpoint_rank_floor=stock * h - 2 * v, rank_charge=charge,
                closed_center_release=2 * q * h, closed_side_output_excursions=2 * v,
                deficit=stock * h - charge, child_width_histogram=dict(sorted(hist.items())),
                whole_word_recursive_full_width_calls=hist[h],
                full_width_self_mass=str(Q(hist[h], stock)),
                scope='Actual declared four-echo full-materialization chronology, not all native circuits.')


def physical_replay(center, side, columns, all_columns=False):
    v = len(center['labels']); stock = 3 * v + side['roles']; size = 1 << (center['h'] * columns)
    digest = sha256(); checked = 0
    for role in range(stock):
        for address in range(size) if all_columns else (0,):
            data = [[g.ONE if bank_id == role and a == address else g.ZERO for a in range(size)]
                    for bank_id in range(stock)]
            initial = data[:v], data[v:2*v], data[2*v:3*v], data[3*v:]
            observed = execute(center, side, initial, columns)
            if observed != expected(center, side, initial, columns):
                raise ValueError('A physical source, sink, center-dirty or side-dirty column failed')
            digest.update(json.dumps([[g.text_complex(z) for values in group for z in values]
                                     for group in observed], separators=(',', ':')).encode())
            checked += 1
    output = side['outputs'][0]
    data = [[g.ONE if bank_id == 3 * v + output and a == 0 else g.ZERO for a in range(size)]
            for bank_id in range(stock)]
    initial = data[:v], data[v:2*v], data[2*v:3*v], data[3*v:]
    if execute(center, side, initial, columns, True) == expected(center, side, initial, columns):
        raise ValueError('Omitted rank-one side output return was not detected')
    return dict(explicitly_replayed_initial_columns=checked, complete_initial_columns=stock * size,
                coverage='All physical columns' if all_columns else 'Origin-address bank columns plus common-XOR covariance',
                all_actual_dirty_outputs='C_full times original virtual dirty values',
                omitted_side_output_return_detected=True, output_sha256=digest.hexdigest())


def probe(case):
    kind, h, columns, mode = case; started = time.monotonic()
    center = c.component(kind, h); side = side_spec(center); v = len(center['labels'])
    if len(set(side['outputs'])) != v or any(output < v for output in side['outputs']):
        raise ValueError('This closed-output compiler requires distinct non-input side roles')
    scalar = scalar_replay(center, side)
    physical = physical_replay(center, side, columns, mode == 'all-columns') if mode != 'scalar-only' else None
    return dict(status='PASS LITERAL FULL-SIDE SPLICE; NEGATIVE RANK DEFICIT', family=kind,
                h=h, columns=columns, vertices=v, center_rank=center['q'], side_roles=side['roles'],
                side_family=side['family'], scalar_operator=scalar, physical_operator=physical,
                full_materialization_ledger=ledger(h, v, center['q'], side['roles']),
                center_basis_calls=4, side_mixer_calls=4,
                side_shears_per_mixer=len(side['edges']), early_and_late_side_scatters=2 * v,
                complete_source_injection_and_subtraction=4 * v,
                seconds=time.monotonic() - started,
                limitation='This literal word cannot improve the phase exponent because its rank charge exceeds Wh. Rewired nonmonotone joint cancellation, compressed channels with different endpoints, address-dependent gauges and other words remain open.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    cases = [('orthogonal-color', 3, 1, 'all-columns'),
             ('orthogonal-color', 3, 2, 'origin-columns'),
             ('single-total', 7, 1, 'scalar-only'), ('single-total', 8, 1, 'scalar-only')]
    topic_code = Path(__file__).resolve().parents[1]
    sources = sorted({Path(module.__file__).resolve() for module in sys.modules.values()
                      if getattr(module, '__file__', None) and Path(module.__file__).resolve().is_relative_to(topic_code)
                      and Path(module.__file__).suffix == '.py'} | {Path(__file__).resolve()})
    # The reference side source uses importlib and is not stored in sys.modules.
    sources = sorted(set(sources) | {z.SIDE_SOURCE.resolve()})
    hashes = {path: sha256(path.read_bytes()).hexdigest() for path in sources}
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    native_threads_each=1, cases=cases, seed=None,
                    source_sha256={str(path.relative_to(topic_code)): value for path, value in hashes.items()},
                    hypothesis='Early dirty echoes share the zero sink boundary, but closed late side output paths spend 2v rank and erase the center-only endpoint saving.')
    (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    receipts = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(probe, case): case for case in cases}
        for future in as_completed(futures):
            result = future.result(); receipts.append(result)
            print(json.dumps({key:result[key] for key in ('status','family','h','columns','seconds')}
                             | {'deficit':result['full_materialization_ledger']['deficit']}), flush=True)
    if any(sha256(path.read_bytes()).hexdigest() != value for path, value in hashes.items()):
        raise ValueError('An effective source changed during the complete splice run')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=receipts), indent=2)+'\n')


if __name__ == '__main__':
    main()
