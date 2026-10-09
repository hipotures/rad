#!/usr/bin/env python3
"""One dirty side helper per orthogonal edge, with geodesic helper paths.

Coordinate-color cases have literal Gaussian operator replay. Larger odd-
weight cases have exact scalar/orthogonality/L_E rank ledgers; their generic
canonical Clifford representatives and native wrappers are separate.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb, log
from pathlib import Path
import sys
import time

import closed_center_release as c
from lagrangian_graph_completion import basis, solve

g = c.g


def central_value(k, a, b):
    value = Q(1)
    intersection = (a & b).bit_count()
    for root in range(1, k, 2):
        value *= Q(intersection - root, k - root)
    return value


def edge_set(labels, central):
    edges = []
    for source, U in enumerate(labels):
        for target, T in enumerate(labels):
            coefficient = Q(source == target) - central(T, U)
            if coefficient:
                if (T & U).bit_count() % 2:
                    raise ValueError('A side edge has nonorthogonal input/output labels')
                edges.append((target, source, coefficient))
    return edges


def subspace_frame(values, E, h, columns):
    # These bounded color cases use coordinate subspaces only. No arbitrary
    # degenerate E representative is silently replaced by a projector.
    if any(a & (a - 1) for a in E):
        raise ValueError('Literal bounded coordinate representative only')
    out = list(values)
    for a in E:
        out = c.c_line(out, a, h, columns)
    return out


def move_coordinate(values, before, after, h, columns):
    if any(a & (a - 1) for a in before + after):
        raise ValueError('Noncoordinate move requires a generic Clifford lift')
    out = list(values)
    for a in before:
        if a not in after:
            out = c.c_line(out, a, h, columns, True)
    for a in after:
        if a not in before:
            out = c.c_line(out, a, h, columns)
    return out


def execute(center, edges, initial, columns, omit_cleanup=False):
    h = center['h']; v = len(center['labels']); q = center['q']
    x, y, r, a = [[list(values) for values in group] for group in initial]
    full = tuple(1 << j for j in range(h))
    # Both arbitrary-dirty negative echoes share the sinks' identity frame.
    c.apply_basis(center['basis'], r); c.scatter(y, r, center['decoder'], -1)
    c.apply_basis(center['basis'], r, True)
    for j, (target, _, coefficient) in enumerate(edges):
        y[target] = [g.add(z, g.scale(value, -coefficient)) for z, value in zip(y[target], a[j])]
    # Hold all source banks at their line operators through every injection.
    for j, label in enumerate(center['labels']):
        r[j] = c.c_line(r[j], label, h, columns)
        r[j] = [g.add(z, value) for z, value in zip(r[j], x[j])]
        r[j] = c.to_kernel(r[j], label, h, columns)
    for j, (_, source, _) in enumerate(edges):
        a[j] = c.c_line(a[j], center['labels'][source], h, columns)
        a[j] = [g.add(z, value) for z, value in zip(a[j], x[source])]
    # The late central image is supplied before any sink leaves zero.
    c.apply_basis(center['basis'], r)
    for j in range(q):
        r[j] = c.c_full(r[j], h, columns, True)
    c.scatter(y, r, center['decoder'], 1)
    for j in range(q):
        r[j] = c.c_full(r[j], h, columns)
    c.apply_basis(center['basis'], r, True)
    frames = [() for _ in range(v)]
    for j, (target, source, coefficient) in enumerate(edges):
        U = center['labels'][source]
        grown = basis(frames[target] + (U,), h)
        y[target] = move_coordinate(y[target], frames[target], grown, h, columns)
        a[j] = move_coordinate(a[j], (U,), grown, h, columns)
        y[target] = [g.add(z, g.scale(value, coefficient)) for z, value in zip(y[target], a[j])]
        a[j] = move_coordinate(a[j], grown, full, h, columns)
        frames[target] = grown
    for target, T in enumerate(center['labels']):
        kernel = tuple(1 << j for j in range(h) if not (T >> j & 1))
        y[target] = move_coordinate(y[target], frames[target], kernel, h, columns)
    for j, label in enumerate(center['labels']):
        x[j] = c.to_kernel(x[j], label, h, columns)
        r[j] = [g.add(z, g.neg(value)) for z, value in zip(r[j], x[j])]
    for j, (_, source, _) in enumerate(edges):
        if not (omit_cleanup and j == 0):
            a[j] = [g.add(z, g.neg(value)) for z, value in zip(a[j], x[source])]
    return x, y, r, a


def expected(center, initial, columns):
    h = center['h']; old_x, old_y, old_r, old_a = initial
    vx = [c.c_line(values, label, h, columns, True) for label, values in zip(center['labels'], old_x)]
    vy = [[g.add(y, x) for y, x in zip(ys, xs)] for ys, xs in zip(old_y, vx)]
    return ([c.c_full(values, h, columns) for values in vx],
            [c.to_kernel(values, label, h, columns) for label, values in zip(center['labels'], vy)],
            [c.c_full(values, h, columns) for values in old_r],
            [c.c_full(values, h, columns) for values in old_a])


def physical_probe(h, columns, all_columns):
    center = c.component('orthogonal-color', h); v = len(center['labels'])
    edges = edge_set(center['labels'], center['central']); stock = 3 * v + len(edges)
    volume = 1 << (h * columns); digest = sha256(); checked = 0
    for role in range(stock):
        for address in range(volume) if all_columns else (0,):
            data = [[g.ONE if role == bank and a == address else g.ZERO for a in range(volume)]
                    for bank in range(stock)]
            initial = data[:v], data[v:2*v], data[2*v:3*v], data[3*v:]
            observed = execute(center, edges, initial, columns)
            if observed != expected(center, initial, columns):
                raise ValueError('Literal geodesic side echo failed a physical initial column')
            digest.update(json.dumps([[g.text_complex(z) for values in group for z in values]
                                     for group in observed], separators=(',', ':')).encode())
            checked += 1
    # A source input exposes the indispensable outgoing cleanup shear.
    source = edges[0][1]
    data = [[g.ONE if bank == source and address == 0 else g.ZERO for address in range(volume)]
            for bank in range(stock)]
    initial = data[:v], data[v:2*v], data[2*v:3*v], data[3*v:]
    if execute(center, edges, initial, columns, True) == expected(center, initial, columns):
        raise ValueError('Omitted side-helper source cleanup was not detected')
    return dict(h=h, columns=columns, payload_stock=stock, side_helpers=len(edges),
                explicitly_replayed_physical_columns=checked, complete_physical_columns=stock*volume,
                coverage='All initial physical columns' if all_columns else 'Origin-address bank columns plus common-XOR covariance',
                virtual_sink_addition='x exactly', virtual_sources_and_all_dirty_restored=True,
                actual_dirty_endpoint='C_full * original virtual dirty',
                all_actual_scalar_gate_frames_equal=True, omitted_cleanup_detected=True,
                output_sha256=digest.hexdigest())


def rank_ledger(h, k, q, labels, edges):
    v = len(labels); m = len(edges); stock = 3*v+m
    frames = [() for _ in labels]; hist = Counter(); dimensions = Counter()
    hist[1] += v; hist[h-1] += 2*v; hist[h] += 2*q
    for target, source, coefficient in edges:
        T, U = labels[target], labels[source]
        old = frames[target]; new = basis(old+(U,), h); d = len(new)
        if any((a&T).bit_count()%2 for a in new):
            raise ValueError('A sink left its endpoint geodesic')
        if len(new)-len(old) not in (0,1):
            raise ValueError('A one-edge update has invalid subspace growth')
        if d > h-1:
            raise ValueError('A helper injection is not inside the target frame')
        solve(new,U)
        if len(new)>len(old): hist[1]+=1
        for width in (1,d-1,h-d):
            if width: hist[width]+=1
        if 1+(d-1)+(h-d) != h:
            raise ValueError('An edge helper does not follow a zero-to-full geodesic')
        dimensions[d] += 1; frames[target] = new
    final_dims = Counter(len(E) for E in frames)
    for E in frames:
        width=h-1-len(E)
        if width: hist[width]+=1
    charge=sum(width*count for width,count in hist.items())
    expected_charge=stock*h-2*v+2*q*h
    if charge != expected_charge:
        raise ValueError('Whole center plus edge-helper rank telescope failed')
    # Floating screen only; exact interval certificates are separate.
    def moment(saving):
        return sum(count*width**(1-saving) for width,count in hist.items())/(stock*h**(1-saving))
    lo,hi=0.0,0.1
    if moment(0)<1:
        for _ in range(70):
            mid=(lo+hi)/2
            if moment(mid)<1:lo=mid
            else:hi=mid
        numerical_root=(lo,hi)
    else:numerical_root=None
    return dict(h=h,k=k,vertices=v,center_rank=q,side_edge_helpers=m,payload_stock=stock,
                side_helpers_per_vertex=str(Q(m,v)),capacity=stock*h,rank_charge=charge,
                deficit=stock*h-charge,closed_center_release=2*q*h,
                child_width_histogram=dict(sorted(hist.items())),
                side_meeting_dimension_histogram=dict(sorted(dimensions.items())),
                final_sink_span_rank_histogram=dict(sorted(final_dims.items())),
                all_side_helpers_endpoint_geodesic=True,full_width_child_calls=hist[h],
                full_width_self_mass=str(Q(hist[h],stock)),
                numerical_normalized_moment_at_1e_4=moment(1e-4),
                numerical_normalized_moment_at_2e_4=moment(2e-4),
                numerical_characteristic_root_interval=numerical_root,
                screen_label='Floating necessary sensitivity only; not an exact exponent certificate',
                scope='Complete abstract L_E rank ledger and scalar identity for the declared edge-by-edge chronology. Larger arbitrary E actual Gaussian representatives, local fees, precision and full primitive architecture remain obligations.')


def probe(case):
    kind,h,k,columns=case;start=time.monotonic()
    if kind=='physical':
        center=c.component('orthogonal-color',h);labels=center['labels'];q=center['q'];central=center['central']
    else:
        labels=[sum(1<<i for i in subset) for subset in combinations(range(h),k)]
        q=comb(h,(k-1)//2);central=lambda a,b:central_value(k,a,b)
    edges=edge_set(labels,central)
    ledger=rank_ledger(h,k,q,labels,edges)
    physical=physical_probe(h,columns,columns==1) if kind=='physical' else None
    return dict(status='PASS GEODESIC EDGE SIDE CHRONOLOGY',kind=kind,rank_ledger=ledger,
                physical_operator=physical,seconds=time.monotonic()-start)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    cases=[('physical',3,1,1),('physical',3,1,2),('rank',9,3,1),('rank',12,3,1),('rank',16,3,1)]
    code_root=Path(__file__).resolve().parents[1]
    sources=sorted({Path(module.__file__).resolve() for module in sys.modules.values()
                    if getattr(module,'__file__',None) and Path(module.__file__).resolve().is_relative_to(code_root)
                    and Path(module.__file__).suffix=='.py'}|{Path(__file__).resolve(),c.f.SIDE_SOURCE.resolve()})
    hashes={p:sha256(p.read_bytes()).hexdigest() for p in sources}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,
                  cases=cases,seed=None,source_sha256={str(p.relative_to(code_root)):value for p,value in hashes.items()},
                  hypothesis='One separate dirty side helper per orthogonal edge keeps every helper on a geodesic and removes the per-output closed side fee.')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');receipts=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,case):case for case in cases}
        for future in as_completed(jobs):
            result=future.result();receipts.append(result);ledger=result['rank_ledger']
            print(json.dumps(dict(status=result['status'],kind=result['kind'],h=ledger['h'],deficit=ledger['deficit'],
                                  stock=ledger['payload_stock'],moment_2e_4=ledger['numerical_normalized_moment_at_2e_4'],
                                  seconds=result['seconds'])),flush=True)
    if any(sha256(p.read_bytes()).hexdigest()!=value for p,value in hashes.items()):
        raise ValueError('An effective source changed during geodesic side experiment')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=receipts),indent=2)+'\n')


if __name__=='__main__':main()
