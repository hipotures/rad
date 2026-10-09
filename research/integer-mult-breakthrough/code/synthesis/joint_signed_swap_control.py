#!/usr/bin/env python3
"""Complete three-body signed exchange with RIGHT-composed actual frames.

This positive operator control pays every body and helper traversal. The
shared-helper profile is a negative capacity result, not a new primitive.
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

import canonical_geodesic_side_review as d
cf = d.cf


def matrix_normalize(M, bits):
    while bits and all(not (a % 2 or b % 2) for row in M for a, b in row):
        M = [[(a // 2, b // 2) for a, b in row] for row in M]
        bits -= 1
    return tuple(tuple(row) for row in M), bits


def compose(A, B):
    M, e = A; N, f = B; size = len(M)
    out = []
    for row in range(size):
        values = []
        for column in range(size):
            total = (0, 0)
            for j in range(size):
                if M[row][j] != (0, 0) and N[j][column] != (0, 0):
                    total = cf.add(total, cf.mul(M[row][j], N[j][column]))
            values.append(total)
        out.append(values)
    return matrix_normalize(out, e + f)


def adjoint(A):
    M, bits = A
    return tuple(tuple(cf.conj(M[j][i]) for j in range(len(M))) for i in range(len(M))), bits


def shift(a, direction, h, columns):
    values, bits = a
    mask = sum(1 << (j * columns + column)
               for j in range(h) if direction >> j & 1 for column in range(columns))
    return tuple(values[address ^ mask] for address in range(len(values))), bits


def shift_matrix(A, direction):
    M, bits = A
    return tuple(M[row ^ direction] for row in range(len(M))), bits


def operator(spec, E):
    frame = spec['frames'][E]
    return matrix_normalize(frame['numerator'], frame['denominator_bits'])


def body(spec, data, actual_frames, columns, background, reverse=False,
         negative=None):
    v = spec['v']; roles = list(range(spec['stock']))
    if reverse:roles[:2*v] = list(range(v, 2*v)) + list(range(v))
    expected_frames = {E: compose(operator(spec, E), background) for E in spec['frames']}
    check_frames = negative is None
    if check_frames and any(actual_frames[roles[j]] != expected_frames[E]
                            for j, E in spec['initial'].items()):
        raise ValueError('A body input is not its exact RIGHT-background actual frame')
    if reverse:
        for role in roles[:v]:data[role] = d.multiply(data[role], Q(-1))
    for event in spec['events']:
        kind = event[0]
        if kind == 'move':
            _, local, key = event; role = roles[local]
            M, bits, inverse, nf = spec['relative'][key]
            relative = adjoint((M, bits)) if inverse else matrix_normalize(M, bits)
            if negative == 'LEFT background during middle pass' and reverse:
                relative = compose(compose(background, relative), adjoint(background))
                M, bits = relative; inverse = False
            data[role] = d.apply_matrix(data[role], M, bits, spec['h'], columns, inverse)
            actual_frames[role] = compose(relative, actual_frames[role])
            if check_frames and actual_frames[role] != expected_frames[key[1]]:
                raise ValueError('An actual relative operator lost its RIGHT-background gauge')
        elif kind == 'scale':
            _, local, c = event; data[roles[local]] = d.multiply(data[roles[local]], c)
        else:
            _, a, b, c = event; a, b = roles[a], roles[b]
            if check_frames and actual_frames[a] != actual_frames[b]:
                raise ValueError('A complete body scalar gate has unequal ACTUAL operators')
            data[a] = d.plus(data[a], data[b], c)
    if reverse:
        for role in roles[:v]:data[role] = d.multiply(data[role], Q(-1))
    if check_frames and any(actual_frames[roles[j]] != expected_frames[E]
                            for j, E in spec['final'].items()):
        raise ValueError('A body output is not its exact RIGHT-background actual frame')


def execute(spec, initial, columns, negative=None):
    data = list(initial); actual = [operator(spec, spec['initial'][j]) for j in range(spec['stock'])]
    h, v = spec['h'], spec['v']; full = tuple(1 << j for j in range(h))
    identity = operator(spec, ()); F = operator(spec, full)
    def native_shift(role, direction):
        data[role] = shift(data[role], direction, h, columns)
        actual[role] = shift_matrix(actual[role], direction)
    body(spec, data, actual, columns, identity, negative=negative)
    # The first sink has F*A^-1. X_T=A^2 changes this to A*F,
    # the second source endpoint, preserving its virtual coefficient.
    for j, T in enumerate(spec['labels']):
        if negative != 'omit first line alignment':native_shift(v+j, T)
    body(spec, data, actual, columns, F, True, negative)
    # All second-body helpers are F^2*z. Pay their literal X_all
    # permutation as well as the data permutations; no virtual reset.
    for role in range(spec['stock']):
        if negative != 'omit helper F-squared repair' or role < 2*v:
            native_shift(role, (1 << h) - 1)
    for j, T in enumerate(spec['labels']):native_shift(j, T)
    body(spec, data, actual, columns, identity, negative=negative)
    for j, T in enumerate(spec['labels']):
        native_shift(v+j, T)
        data[j] = d.multiply(data[j], Q(-1))
        data[j], data[v+j] = data[v+j], data[j]
        actual[j], actual[v+j] = actual[v+j], actual[j]
    return data


def expected(spec, initial, columns):
    full = tuple(1 << j for j in range(spec['h'])); F = spec['frames'][full]
    return [d.apply_matrix(a, F['numerator'], F['denominator_bits'], spec['h'], columns)
            for a in initial]


def bind_right_background(spec):
    full = tuple(1 << j for j in range(spec['h'])); F = operator(spec, full)
    right_checked = 0; left_different = 0
    for key, (M, bits, inverse, nf) in spec['relative'].items():
        A, B = operator(spec, key[0]), operator(spec, key[1])
        direct = compose(B, adjoint(A))
        right = compose(compose(B, F), adjoint(compose(A, F)))
        if right != direct:raise ValueError('RIGHT background failed literal coefficient cancellation')
        left = compose(compose(F, B), adjoint(compose(F, A)))
        left_different += left != direct; right_checked += 1
    if not left_different:raise ValueError('The selected generic frames did not distinguish LEFT from RIGHT')
    return right_checked, left_different


def probe(case):
    h, columns, reverse_order, all_columns = case; start = time.monotonic()
    spec = d.schedule(h, reverse_order); stock = spec['stock']; volume = 1 << (h*columns)
    right_checked, left_different = bind_right_background(spec)
    digest = sha256(); checked = 0
    for role in range(stock):
        for address in range(volume) if all_columns else (0,):
            initial = [(tuple((int(bank == role and a == address), 0) for a in range(volume)), 0)
                       for bank in range(stock)]
            actual = execute(spec, initial, columns)
            if actual != expected(spec, initial, columns):
                raise ValueError('The complete signed exchange failed a source/sink/dirty physical column')
            digest.update(str(actual).encode()); checked += 1
    fields = 3
    for field in range(fields):
        initial = [d.normalize([((a*7+bank*11+field*3)%31-15,
                                (a*13+bank*5+field*17)%29-14) for a in range(volume)],
                               (field+bank)%4) for bank in range(stock)]
        actual = execute(spec, initial, columns); wanted = expected(spec, initial, columns)
        if actual != wanted:raise ValueError('Complete signed exchange failed an arbitrary-dirty Gaussian field')
        digest.update(str(actual).encode())
    controls = {name: execute(spec, initial, columns, name) != wanted
                for name in ('omit first line alignment', 'omit helper F-squared repair')}
    if not all(controls.values()):raise ValueError('A signed-exchange orientation/helper/alignment control did not discriminate')
    # LEFT conjugation changes individual frames/relative ranks, yet the
    # complete framed shear has convolution end blocks commuting with F.
    # Consequently an end-operator mismatch is the WRONG orientation test.
    left_end_agrees = execute(spec, initial, columns, 'LEFT background during middle pass') == wanted
    if not left_end_agrees:raise ValueError('The independently expected full-word F covariance failed')
    histogram = {width: 3*count for width, count in spec['histogram'].items()}
    rank = 3*spec['rank']; capacity = stock*h
    if rank <= capacity:raise ValueError('Three individually restored bodies unexpectedly contracted')
    # Every body has source/sink endpoint rank >=2v(h-1) and each
    # helper pays >=h, so three bodies cost >=3Wh-6v >=Wh for h>=2,W>=3v.
    if h < 2 or stock < 3*spec['v'] or 3*stock*h-6*spec['v'] <= capacity:
        raise ValueError('The stated all-size independent-body capacity lower bound failed')
    return dict(status='PASS COMPLETE RIGHT-BACKGROUND SIGNED EXCHANGE; CAPACITY FAIL',
                h=h, columns=columns, reverse_edge_order=reverse_order,
                vertices=spec['v'], center_features=spec['q'], side_helpers=len(spec['edges']),
                payload_stock=stock, explicit_initial_columns=checked,
                all_physical_columns=stock*volume,
                coverage='All physical columns' if all_columns else 'All bank origins plus3completeGaussianfields; no covariance promotion',
                complete_gaussian_fields=fields, full_field_values=fields*stock*volume,
                exact_right_background_relatives_checked=right_checked,
                left_background_relative_counterexamples=left_different,
                recursive_child_histogram=histogram, rank_charge=rank, capacity=capacity,
                deficit=capacity-rank, normalized_first_moment=str(Q(rank,capacity)),
                full_width_self_call_count=histogram.get(h,0),
                full_width_self_mass=str(Q(histogram.get(h,0),stock)),
                native_permutation_bank_events=3*spec['v']+stock,
                native_constant_sign_bank_events=3*spec['v'],
                native_full_bank_exchanges=spec['v'],
                scalar_body_count=3, actual_helper_return_paths_paid=3*(stock-2*spec['v']),
                actual_data_outputs='C_full applied to each original raw labeled bank after literal sign/permutation/exchange repairs',
                actual_dirty_outputs='C_full applied to original arbitrary dirty bank',
                negative_controls=controls, left_conjugated_complete_end_operator_agrees=left_end_agrees,
                orientation_scope='RIGHT preserves each exact relative and paid rank. LEFT changes intermediate relatives but common conjugation cancels in this convolution complete end operator.',
                output_sha256=digest.hexdigest(),
                seconds=time.monotonic()-start,
                scope='Exact finite raw-input canonical full-C operator with paid three-body recursive rank and explicit native event counts. Three individually dirty-restored bodies fail necessary capacity at all nonnegative savings under fixed stock. Native tape/precision costs are not derived, and this is not a useful C_h recurrence or new multiplier exponent.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    cases = [(4,1,False,True),(4,1,True,True),(4,2,False,False),(4,2,True,False)]
    root = Path(__file__).resolve().parents[1]
    sources = sorted({Path(module.__file__).resolve() for module in sys.modules.values()
                      if getattr(module,'__file__',None) and Path(module.__file__).resolve().is_relative_to(root)
                      and Path(module.__file__).suffix=='.py'} | {Path(__file__).resolve(), d.center_word.f.SIDE_SOURCE.resolve()})
    hashes = {p:sha256(p.read_bytes()).hexdigest() for p in sources}
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,
                    native_threads_each=1,cases=cases,seed=None,
                    source_sha256={str(p.relative_to(root)):value for p,value in hashes.items()},
                    hypothesis='Three separately dirty-restored framed shears can close raw-input C_h through RIGHT backgrounds, but their fixed-stock paid recursion may fail necessary capacity.',
                    scalar_domain='Exact integer Gaussian numerators with per-bank dyadic grid',
                    native_event_timing='Permutations/signs/exchanges are literal and counted; no native tape-time claim')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,case):case for case in cases}
        for future in as_completed(jobs):
            result=future.result();results.append(result)
            print(json.dumps({key:result[key] for key in ('status','h','columns','rank_charge','capacity','seconds')}),flush=True)
    if any(sha256(p.read_bytes()).hexdigest()!=value for p,value in hashes.items()):
        raise ValueError('A source changed during complete signed-exchange replay')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results),indent=2)+'\n')


if __name__ == '__main__':main()
