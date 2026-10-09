#!/usr/bin/env python3
"""Exact odd-weight spectral channels and dyadic projection discriminator.

The inclusion-Gram eigenformula is pinned to its primary paper. Complement
reduction, Newton coefficients, direct finite ranks and a non-dyadic projector
are independently reconstructed. No native coordinate transport is supplied.
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


TOPIC = Path(__file__).resolve().parents[2]
CONFIG = TOPIC/'configs/transfers/odd-weight-spectrum.json'


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


def dyadic(value):
    return value.denominator & (value.denominator-1) == 0


def central_value(k, overlap):
    value = Q(1)
    for j in range((k-1)//2):
        value *= Q(overlap-(2*j+1), 2*(j+1))
    return value


def newton(values):
    coefficients = []
    values = list(values)
    while values:
        coefficients.append(values[0])
        values = [b-a for a, b in zip(values, values[1:])]
    return coefficients


def spectrum(h, k):
    if not 1 <= k <= h or k % 2 == 0:
        raise ValueError('Expected an odd positive weight within the ambient set')
    ell = min(k, h-k)
    shift = 2*k-h if k > h//2 else 0
    coefficients = newton([central_value(k, shift+j) for j in range(ell+1)])
    if any(not dyadic(z) for z in coefficients):
        raise ValueError('Central Newton coefficient left the Gaussian-dyadic ring')
    eigenvalues = [sum(coefficients[t]*choose(ell-j, t-j)*choose(h-t-j, ell-t)
                     for t in range(j, ell+1)) for j in range(ell+1)]
    multiplicities = [choose(h, j)-choose(h, j-1) for j in range(ell+1)]
    volume = choose(h, k)
    trace = sum(x*m for x, m in zip(eigenvalues, multiplicities))
    square_trace = sum(x*x*m for x, m in zip(eigenvalues, multiplicities))
    direct_row_square = sum(choose(k, t)*choose(h-k, k-t)*central_value(k, t)**2
                            for t in range(max(0, 2*k-h), k+1))
    if sum(multiplicities) != volume or trace != volume or square_trace != volume*direct_row_square:
        raise ValueError('Independent multiplicity/trace/row-square controls failed')
    center_rank = sum(m for x, m in zip(eigenvalues, multiplicities) if x)
    side_nullity = sum(m for x, m in zip(eigenvalues, multiplicities) if x == 1)
    center_nullity = volume-center_rank
    unit_projector_diagonal = Q(side_nullity, volume)
    zero_projector_diagonal = Q(center_nullity, volume)
    return dict(h=h, k=k, volume=volume, complement_working_weight=ell,
        shifted_overlap=shift, Newton_coefficients=[str(z) for z in coefficients],
        eigenvalues=[str(z) for z in eigenvalues], multiplicities=multiplicities,
        center_rank=center_rank, center_nullity=center_nullity,
        side_rank=volume-side_nullity, side_nullity=side_nullity,
        unit_projector_diagonal=str(unit_projector_diagonal),
        unit_projector_dyadic_diagonal=dyadic(unit_projector_diagonal),
        zero_projector_diagonal=str(zero_projector_diagonal),
        zero_projector_dyadic_diagonal=dyadic(zero_projector_diagonal),
        exact_controls=dict(trace=str(trace), square_trace=str(square_trace),
                            independent_overlap_row_square=str(direct_row_square)))


def scan_weight(task):
    k, maximum_h = task
    started = time.monotonic()
    rows = [spectrum(h, k) for h in range(k, maximum_h+1)]
    # Only exceptional low channels are retained, with a digest of the complete
    # deterministic scan. Generic zero channels beyond the polynomial degree
    # are expected and do not alone constitute a new candidate.
    candidates = [row for row in rows if row['side_nullity'] or any(
        Q(row['eigenvalues'][j]) == 0 for j in range(min((k-1)//2,
            row['complement_working_weight'])+1))]
    digest = sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return dict(weight=k, ambient_range=[k, maximum_h], cases=len(rows),
        complete_scan_sha256=digest, exceptional_rows=candidates,
        seconds=time.monotonic()-started,
        omitted='Generic scan rows are deterministic from retained source/config; only exceptional low zero/one channels are retained.')


def rank(matrix):
    rows = [[Q(z) for z in row] for row in matrix]
    r = 0
    for j in range(len(rows[0])):
        pivot = next((i for i in range(r, len(rows)) if rows[i][j]), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        factor = rows[r][j]
        rows[r] = [z/factor for z in rows[r]]
        for i in range(r+1, len(rows)):
            if rows[i][j]:
                factor = rows[i][j]
                rows[i] = [a-factor*b for a, b in zip(rows[i], rows[r])]
        r += 1
        if r == len(rows):
            break
    return r


def matrix_product(a, b):
    columns = list(zip(*b))
    return [[sum(x*y for x, y in zip(row, column) if x and y)
             for column in columns] for row in a]


def direct_case(task):
    h, k = task
    started = time.monotonic()
    spec = spectrum(h, k)
    sources = [sum(1 << x for x in s) for s in combinations(range(h), k)]
    V = len(sources)
    if V > 150:
        raise ValueError('Direct matrix discriminator is capped at 150 coordinates')
    matrix = [[central_value(k, (s&t).bit_count()) for t in sources] for s in sources]
    side = [[Q(int(i == j))-matrix[i][j] for j in range(V)] for i in range(V)]
    center_rank, side_rank = rank(matrix), rank(side)
    if center_rank != spec['center_rank'] or side_rank != spec['side_rank']:
        raise ValueError('Direct rational matrix ranks differ from spectral prediction')
    projector = None
    if (h, k) == (8, 5):
        H = [[int(8*z) for z in row] for row in matrix]
        H2, H3 = matrix_product(H, H), None
        H3 = matrix_product(H2, H)
        numerator = [[H3[i][j]-78*H2[i][j]+1505*H[i][j] for j in range(V)] for i in range(V)]
        denominator = 8*945
        squared = matrix_product(numerator, numerator)
        HP = matrix_product(H, numerator)
        if any(squared[i][j] != denominator*numerator[i][j] or
               HP[i][j] != 8*numerator[i][j] for i in range(V) for j in range(V)):
            raise ValueError('Exact unit-eigenspace projector identities failed')
        diagonal = [Q(numerator[i][i], denominator) for i in range(V)]
        if set(diagonal) != {Q(5, 14)} or sum(diagonal) != 20 or dyadic(diagonal[0]):
            raise ValueError('Non-dyadic projector discriminator failed')
        projector = dict(polynomial='(64*K^3-624*K^2+1505*K)/945',
            integer_matrix_numerator_denominator=denominator,
            matrix_sha256=sha256(json.dumps(numerator, separators=(',', ':')).encode()).hexdigest(),
            exact_idempotence=True, exact_KP_equals_P=True, exact_trace=20,
            diagonal='5/14', direct_non_dyadic_witness=dict(input='delta_0', output_coordinate=0, output='5/14'),
            scope='Refutes Gaussian-dyadic invariant spectral similarity for this eigenspace, not every kernel completion, encoded rational interface or native algorithm.')
    return dict(h=h, k=k, volume=V, exact_center_rank=center_rank, exact_side_rank=side_rank,
        spectral_match=True, unit_projector=projector, seconds=time.monotonic()-started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--small', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text())
    paths = [Path(__file__).resolve(), CONFIG]
    hashes = {str(p.relative_to(TOPIC)): sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        native_threads_per_worker=1, source_and_config_sha256=hashes,
        primary_source=config['primary_source'], seeds=None,
        scope='Scalar spectral leverage and ring obstructions; all complete phase/row/precision/native transfer contracts remain open.')
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    started = time.monotonic()
    tasks = [(5, 16)] if args.small else [(k, config['maximum_ambient_h']) for k in config['odd_weights']]
    matrix_cases = [(8, 5)] if args.small else [tuple(pair) for pair in config['exact_matrix_cases']]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        scans = list(pool.map(scan_weight, tasks))
        exact_cases = list(pool.map(direct_case, matrix_cases))
    if any(sha256((TOPIC/p).read_bytes()).hexdigest() != digest for p, digest in hashes.items()):
        raise ValueError('Effective source/config changed during attempt')
    control = spectrum(8, 5)
    if control['eigenvalues'] != ['43/8', '35/8', '1', '0'] or control['multiplicities'] != [1, 7, 20, 28]:
        raise ValueError('Matched h8 spectrum control failed')
    # Omitting the diagonal identity is not an innocuous side rank convention.
    if control['side_rank'] == control['center_rank']:
        raise ValueError('Center/side identity omission control lost its distinction')
    result = dict(status='EXACT SCALAR SPECTRAL AND DYADIC-PROJECTION DISCRIMINATOR PASS',
        scans=scans, direct_cases=exact_cases, negative_controls=['center and side ranks remain distinct',
            'unit-channel orthogonal projector leaves the Gaussian-dyadic ring'],
        seconds=time.monotonic()-started,
        conclusion='Rank-zero/one channels are hypotheses for paid coupled circuits; a dyadic invariant spectral split is refuted at h8,k5. No new characteristic root or kappa.')
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(status=result['status'], scanned_cases=sum(r['cases'] for r in scans),
        direct_matrix_cases=len(exact_cases), seconds=result['seconds'], conclusion=result['conclusion'])))


if __name__ == '__main__':
    main()
