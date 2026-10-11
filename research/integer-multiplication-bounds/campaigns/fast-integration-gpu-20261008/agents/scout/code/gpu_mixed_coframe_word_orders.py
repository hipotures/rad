#!/usr/bin/env python3
"""Discovery of coordinate orders for an actual rational signed joint word.

All retained transitions and their physical multiplicities are used by default.
The CUDA elimination order is inherited from the separately validated signed
corner kernel. Only its matrix-loading indices change to implement simultaneous
row and column permutation. One-field scores remain DISCOVERY, even for a whole
word. No DATA or assembly certificate is inferred from a numerical score.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import random
import sys
import time

import cupy as cp
import numpy as np

from mixed_coframe_gpu_interfaces import (
    CUDA as ORIGINAL_CUDA, actual_matrix, base_matrix, cpu_pivots, digest,
    read_binary, stamp, FLAG,
)


CUDA = ORIGINAL_CUDA.replace(
    'const int*betas,const int*stars,const int*hints,int h,int nm,int n,unsigned p,',
    'const int*betas,const int*stars,const int*hints,const int*orders,int h,int nm,int n,unsigned p,',
).replace(
    'long long v=base[k*h*h+z];',
    'int r=orders[bid*h+i],c=orders[bid*h+j];long long v=base[k*h*h+r*h+c];',
)


def catalogue(h, count, seed, previous=None):
    rng = random.Random(seed)
    identity = tuple(range(h))
    rows, seen = [], set()

    def append(order):
        order = tuple(order)
        assert sorted(order) == list(range(h))
        if order not in seen and len(rows) < count:
            rows.append(order)
            seen.add(order)

    append(identity)
    parents = [identity]
    if previous is not None:
        doc = json.loads(previous.read_text())
        assert doc['h'] == h
        parents += [tuple(row['order']) for row in doc['best_orders'][:32]]
        for parent in parents:
            append(parent)
    for parent in parents:
        for i in range(h):
            for j in range(i + 1, h):
                order = list(parent)
                order[i], order[j] = order[j], order[i]
                append(order)
    append(reversed(identity))
    for offset in range(1, h):
        append(identity[offset:] + identity[:offset])
    attempts = 0
    while len(rows) < count:
        attempts += 1
        order = list(rng.choice(parents))
        mode = attempts % 8
        if mode == 0:
            rng.shuffle(order)
        elif mode == 1:
            i, j = sorted(rng.sample(range(h + 1), 2))
            order[i:j] = reversed(order[i:j])
        else:
            for _ in range(mode):
                i, j = rng.sample(range(h), 2)
                order[i], order[j] = order[j], order[i]
        append(order)
    return np.asarray(rows, np.int32), attempts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--graph-receipt', type=Path, required=True)
    ap.add_argument('--geometry-fixture', type=Path, required=True)
    ap.add_argument('--device', type=int, choices=(0, 1), required=True)
    ap.add_argument('--basis', type=F, required=True)
    ap.add_argument('--prime', type=int, default=65521)
    ap.add_argument('--bit-saving', type=F, required=True)
    ap.add_argument('--orders', type=int, required=True)
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--batch', type=int, default=8)
    ap.add_argument('--sample', type=int, default=0)
    ap.add_argument('--previous', type=Path)
    ap.add_argument('--wait-summary', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    args.output.mkdir(parents=True)
    p = args.prime
    assert p > 3 and all(p % divisor for divisor in range(2, math.isqrt(p) + 1))
    graph = json.loads(args.graph_receipt.read_text())
    binary = Path(graph['profile_transition_path'])
    assert digest(binary) == graph['profile_transition_sha256']
    assert graph['transition_format'] == 'RADCOF01'
    assert graph['independent']['frame_format'] == 'mixed-signed-complemented-v1'
    h, v, roles, singles, mass, loss, frames, transitions = read_binary(binary)
    geo = json.loads(args.geometry_fixture.read_text())
    old = next(row for row in geo['profiles']
               if row['profile']['basis'] == f'beta:{args.basis.numerator}:{args.basis.denominator}')
    assert old['input_binary_sha256'] == digest(binary)
    selected = [row for row in transitions
                if frames[row[1]][0] - frames[row[0]][0] > 1 and row[:2] != (0, 1)]
    complete = args.sample == 0
    if args.sample:
        rng = random.Random(args.seed)
        selected = rng.sample(selected, args.sample)
    nm = len(selected)
    orders, attempts = catalogue(h, args.orders, args.seed, args.previous)
    np.save(args.output / 'coordinate-orders.npy', orders)
    cache = {fid: base_matrix(frames[fid], h, p)
             for row in selected for fid in row[:2]}
    matrices = np.asarray([(cache[b] - cache[a]) % p for a, b, _ in selected], np.int64)
    b = args.basis.numerator * pow(args.basis.denominator % p, -1, p) % p
    star = (1 - 9 * b) * pow(9 * (1 - h * b) % p, -1, p) % p
    rs, cs = matrices.sum(axis=2) % p, matrices.sum(axis=1) % p
    total = matrices.sum(axis=(1, 2)) % p
    matrices = (matrices - b * cs[:, None, :] - star * rs[:, :, None]
                + (b * star % p) * total[:, None, None]) % p
    ranks = np.asarray([frames[y][0] - frames[x][0] for x, y, _ in selected], np.int32)
    weights = np.asarray([count for _, _, count in selected], np.float64)
    protocol = {'utc': stamp(), 'classification': 'DISCOVERY: ACTUAL SIGNED-WORD COORDINATE ORDERS',
                'h': h, 'v': v, 'R': roles, 'word_sha256': graph['word_sha256'],
                'transition_sha256': digest(binary), 'graph_receipt_sha256': digest(args.graph_receipt),
                'geometry_fixture_sha256': digest(args.geometry_fixture), 'prime': p,
                'basis': str(args.basis), 'bit_saving': str(args.bit_saving),
                'device': args.device, 'seed': args.seed, 'orders': len(orders),
                'generation_attempts': attempts, 'coordinate_orders_sha256': digest(args.output / 'coordinate-orders.npy'),
                'selected_transitions': selected, 'selected_transition_count': nm,
                'complete_actual_word_field_screen': complete, 'actual_rank_mass': mass,
                'source_sha256': digest(__file__), 'parent_source_sha256': digest(Path(__file__).with_name('gpu_signed_complete_word_loci.py')),
                'cuda_sha256': hashlib.sha256(CUDA.encode()).hexdigest(),
                'permutation_convention': 'New matrix(i,j)=old matrix(order[i],order[j]); relative to the frozen actual word coordinates.',
                'geometry_scope': 'The homogeneous rational basis commutes with permutations. Full-family DATA transfer requires an explicit Cartesian triple and copied-center bijection. Discovery alone does not establish that interface.'}
    if args.previous:
        protocol['previous_discovery_sha256'] = digest(args.previous)
    geometry_code = Path(__file__).resolve().parents[2] / 'geometry' / 'code'
    sys.path.insert(0, str(geometry_code))
    from mixed_coframe_gpu_interfaces import projector
    gram_controls = []
    for fid in cache:
        rank, forced, symbols = frames[fid]
        if not forced or rank < 2:
            continue
        exact = projector(h, forced, symbols, f'beta:{args.basis.numerator}:{args.basis.denominator}')
        reduced = np.asarray([[int(x.numerator * pow(x.denominator % p, -1, p) % p)
                               for x in row] for row in exact], np.int64)
        assert np.array_equal(actual_matrix(cache[fid], args.basis, h, p), reduced)
        gram_controls.append({'frame': fid, 'rank': rank, 'entries': h * h})
        if len(gram_controls) == 12:
            break
    protocol['independent_fraction_gram_controls'] = gram_controls
    protocol['mixed_coframe_interface_sha256'] = digest(Path(__file__).resolve().parent / 'mixed_coframe_gpu_interfaces.py')
    protocol['transition_format'] = 'RADCOF01'
    protocol['coframe_scope'] = 'Independent direct source-span Fraction Gram controls; complete mixed literal word and CRT remain separate acceptance gates.'
    assert gram_controls
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    if args.wait_summary:
        while not args.wait_summary.exists():
            time.sleep(5)
    cp.cuda.Device(args.device).use()
    cp.get_default_memory_pool().set_limit(size=8 * 1024 ** 3)
    kernel = cp.RawKernel(CUDA, 'profiles')
    fixed = [cp.asarray(matrices.astype(np.int32)), cp.zeros((nm, h), cp.int32),
             cp.zeros((nm, h), cp.int32), cp.zeros(nm, cp.int32), cp.asarray(ranks)]
    cpweights = cp.asarray(weights)
    exponent = 1 - float(args.bit_saving)
    fixed_moment = 0.0
    if complete:
        fixed_moment = singles + sum(count for x, y, count in transitions
                                    if frames[y][0] - frames[x][0] == 1)
        fixed_moment += sum(count * h ** exponent for x, y, count in transitions if (x, y) == (0, 1))
    scores = np.empty(len(orders), np.float64)
    started = time.monotonic()
    with (args.output / 'progress.jsonl').open('x') as stream:
        for start in range(0, len(orders), args.batch):
            stop = min(start + args.batch, len(orders))
            n = (stop - start) * nm
            out, pivots = cp.empty(n, cp.float64), cp.empty((n, h), cp.int8)
            zeros = cp.zeros(stop - start, cp.int32)
            kernel((n,), (128,), (*fixed[:4], zeros, zeros, fixed[4], cp.asarray(orders[start:stop]),
                   np.int32(h), np.int32(nm), np.int32(n), np.uint32(p), np.float64(exponent), out, pivots))
            if start == 0:
                control_pivots = pivots[:min(32, nm)].get()
                for i, pivot in enumerate(control_pivots):
                    assert pivot.tolist() == cpu_pivots(matrices[i], p)
                if complete:
                    exact_control = math.fsum(count * width ** exponent for width, count
                                             in enumerate(old['profile']['blocks']) if width)
                else:
                    exact_control = None
                # Also test a nonidentity order with independent CPU elimination.
                if stop > 1:
                    altered = pivots[nm:nm + min(32, nm)].get()
                    for i, pivot in enumerate(altered):
                        M = matrices[i][orders[1]][:, orders[1]]
                        assert pivot.tolist() == cpu_pivots(M, p)
            scores[start:stop] = cp.sum(out.reshape(stop - start, nm) * cpweights, axis=1).get() + fixed_moment
            if start == 0 and complete:
                assert abs(scores[0] - exact_control) < 1e-7
            if start % (16 * args.batch) == 0 or stop == len(orders):
                obs = {'utc': stamp(), 'orders_completed': stop, 'actual_matrices_screened': stop * nm,
                       'elapsed_seconds': time.monotonic() - started,
                       'best_field_moment': float(scores[:stop].min()), 'control_field_moment': float(scores[0])}
                stream.write(json.dumps(obs) + '\n')
                stream.flush()
                print(json.dumps(obs), flush=True)
    np.save(args.output / 'order-moments.npy', scores)
    best = [{'order': orders[i].tolist(), 'field_moment': float(scores[i]),
             'field_gain': float(scores[0] - scores[i])} for i in np.argsort(scores)[:64]]
    summary = {**protocol, 'status': 'COMPLETE ACTUAL SIGNED-WORD ORDER DISCOVERY',
               'finish_utc': stamp(), 'orders_completed': len(orders),
               'actual_matrices_screened': len(orders) * nm,
               'elapsed_seconds': time.monotonic() - started, 'control_field_moment': float(scores[0]),
               'identity_exact_histogram_moment': exact_control, 'best_orders': best,
               'cpu_identity_and_nonidentity_pivot_controls': 2 * min(32, nm),
               'limitations': ['One-field rank decreases may be unlucky modular minors.',
                               'A new selected order requires actual frame and source/center permutation receipts, full rational CRT, DATA compatibility, stock and complete assembly.']}
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({'status': summary['status'], 'best_orders': best[:4]}), flush=True)


if __name__ == '__main__':
    main()
