#!/usr/bin/env python3
"""Exact weighted-union product, changed-basis and complete record controls.

The y=t-i basis of t^2=-1 has y^2=-2iy. Its rank-D evaluator is
subset zeta with diagonal weights; its direct incidence floors are 3^s.
The original q basis conversion is paid explicitly. No native tensor
supplier or activity compaction is inferred from these scalar checks.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from random import Random
import time

import partial_polynomial_product_packets as records


RECORD_SHA = 'b9fff086ff47cf80cdb0073bd9cc62f4d3b62f45236fbaf2794a5bdd529bc0f7'
SEED = 202610090615
UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def plus(a, b):
    return (a[0] + b[0], a[1] + b[1])


def minus(a, b):
    return (a[0] - b[0], a[1] - b[1])


def times(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def c_power(weight, negate=False):
    unit = UNITS[(weight if negate else -weight) % 4]
    return (unit[0] << weight, unit[1] << weight)


def weighted_basis_product(a, b):
    return a | b, c_power((a & b).bit_count())


def scalar_decode(values):
    out = list(values)
    s = len(out).bit_length() - 1
    for bit in range(s):
        for index in range(len(out)):
            if index & (1 << bit):
                out[index] = minus(out[index], out[index ^ (1 << bit)])
    for index, value in enumerate(out):
        weight = index.bit_count()
        value = times(value, UNITS[weight % 4])
        divisor = 1 << weight
        if value[0] % divisor or value[1] % divisor:
            raise AssertionError('weighted-union decoder lost exact divisibility')
        out[index] = (value[0] // divisor, value[1] // divisor)
    return out


def all_coefficients(s):
    D = 1 << s
    eval_matrix = [[c_power(a.bit_count()) if a & ~z == 0 else (0, 0)
                   for a in range(D)] for z in range(D)]
    for a in range(D):
        for b in range(D):
            product = [times(eval_matrix[z][a], eval_matrix[z][b]) for z in range(D)]
            decoded = scalar_decode(product)
            target, coefficient = weighted_basis_product(a, b)
            if any(value != (coefficient if z == target else (0, 0))
                   for z, value in enumerate(decoded)):
                raise AssertionError('zeta evaluation product has a wrong weighted-union coefficient')
    for coordinate in range(D):
        basis = [[(int(index == coordinate), 0)] for index in range(D)]
        changed, grid = basis_change(basis)
        literal, literal_grid = records.transform(basis)
        if grid != s or literal_grid != s or evaluator(changed) != literal:
            raise AssertionError('an E B matrix column differs from literal C')
        restored, inverse_grid = basis_change(changed, inverse=True)
        if inverse_grid or restored != [[(int(index == coordinate) << s, 0)] for index in range(D)]:
            raise AssertionError('a tensor source B inverse column failed')
    input_rank_sum = 0
    identity_minor_entries = 0
    for a in range(D):
        complement = (D - 1) ^ a
        columns = [b for b in range(D) if b & ~complement == 0]
        input_rank_sum += len(columns)
        for row_label in columns:
            for column in columns:
                target, coefficient = weighted_basis_product(a, column)
                actual = coefficient if target == (a | row_label) else (0, 0)
                if actual != ((1, 0) if row_label == column else (0, 0)):
                    raise AssertionError('input-slice exact identity minor failed')
                identity_minor_entries += 1
    # Every output slice has zero rows/columns outside subsets of z. On
    # those subsets its local factors are [[0,1],[1,c]], inverse [[-c,1],[1,0]].
    # Check one complete exact tensor inverse for each possible weight;
    # identical weights need not repeat an identical matrix multiplication.
    inverse_entries = 0
    for weight in range(s + 1):
        size = 1 << weight
        full = size - 1
        matrix = [[c_power((a & b).bit_count()) if a | b == full else (0, 0)
                   for b in range(size)] for a in range(size)]
        inverse = [[c_power(weight - (a | b).bit_count(), negate=True)
                    if a & b == 0 else (0, 0) for b in range(size)] for a in range(size)]
        for a in range(size):
            for b in range(size):
                value = (0, 0)
                for k in range(size):
                    value = plus(value, times(matrix[a][k], inverse[k][b]))
                if value != ((1, 0) if a == b else (0, 0)):
                    raise AssertionError('an exact output-slice tensor inverse failed')
                inverse_entries += 1
    output_rank_sum = sum(1 << z.bit_count() for z in range(D))
    nnz_evaluator = sum(value != (0, 0) for row in eval_matrix for value in row)
    if input_rank_sum != 3 ** s or output_rank_sum != 3 ** s or nnz_evaluator != 3 ** s:
        raise AssertionError('weighted-union slice incidence floor differs from 3^s')
    return dict(complete_basis_product_coefficients=D ** 3,
                complete_E_B_C_matrix_entries=D ** 2,
                complete_B_inverse_matrix_entries=D ** 2,
                input_slice_identity_minor_entries=identity_minor_entries,
                output_tensor_inverse_entries=inverse_entries,
                both_input_rank_sums=input_rank_sum, output_rank_sum=output_rank_sum,
                rank_D_evaluator_nonzeros=nnz_evaluator)


def scale_polynomial(values, coefficient):
    return [times(value, coefficient) for value in values]


def zeta(polynomials, inverse=False):
    values = [list(p) for p in polynomials]
    for bit in range(len(values).bit_length() - 1):
        for index in range(len(values)):
            if index & (1 << bit):
                source = values[index ^ (1 << bit)]
                operation = minus if inverse else plus
                values[index] = [operation(a, b) for a, b in zip(values[index], source)]
    return values


def basis_change(polynomials, inverse=False):
    values = [list(p) for p in polynomials]
    s = len(values).bit_length() - 1
    for bit in range(s):
        for index in range(len(values)):
            if index & (1 << bit):
                continue
            other = index | (1 << bit)
            a, b = values[index], values[other]
            if inverse:
                values[index] = [plus(x, times((1, -1), y)) for x, y in zip(a, b)]
                values[other] = [minus(x, times((1, 1), y)) for x, y in zip(a, b)]
            else:
                values[index] = [plus(times((1, 1), x), times((1, -1), y))
                                 for x, y in zip(a, b)]
                values[other] = [minus(x, y) for x, y in zip(a, b)]
    return values, 0 if inverse else s


def evaluator(polynomials):
    return zeta([scale_polynomial(p, c_power(index.bit_count()))
                 for index, p in enumerate(polynomials)])


def multiplication(polynomials_a, polynomials_b, audit):
    a, b = evaluator(polynomials_a), evaluator(polynomials_b)
    products = [records.encoded_gaussian_product(x, y, audit, False) for x, y in zip(a, b)]
    decoded = zeta(products, inverse=True)
    out = []
    for index, polynomial in enumerate(decoded):
        weight = index.bit_count()
        numerator = scale_polynomial(polynomial, UNITS[weight % 4])
        divisor = 1 << weight
        if any(x % divisor or y % divisor for x, y in numerator):
            raise AssertionError('complete polynomial decoder division was not exact')
        out.append([(x // divisor, y // divisor) for x, y in numerator])
    return out


def direct_union(a, b):
    r = len(a[0])
    out = [[(0, 0)] * r for _ in a]
    for x, left in enumerate(a):
        for y, right in enumerate(b):
            target, coefficient = weighted_basis_product(x, y)
            product = scale_polynomial(records.direct_polynomial_product(left, right), coefficient)
            out[target] = [plus(u, v) for u, v in zip(out[target], product)]
    return out


def audit_record():
    return dict(integer_products=0, maximum_radix_bits=0,
                maximum_product_operand_signed_bits=0,
                maximum_integer_product_signed_bits=0,
                complete_decoded_real_coefficients=0, polynomial_leaf_products=0)


def probe(task):
    s, r, p = task
    D = 1 << s
    coefficients = all_coefficients(s)
    rng = Random(SEED + 100 * s + 10 * r + p)
    limit = 1 << (p - 1)
    a = [[(rng.randrange(-limit, limit), rng.randrange(-limit, limit)) for _ in range(r)] for _ in range(D)]
    b = [[(rng.randrange(-limit, limit), rng.randrange(-limit, limit)) for _ in range(r)] for _ in range(D)]
    y_a, grid = basis_change(a)
    y_b, other_grid = basis_change(b)
    if grid != s or other_grid != s:
        raise AssertionError('tensor source B grid differs from s')
    literal_ca, literal_grid = records.transform(a)
    if evaluator(y_a) != literal_ca or literal_grid != s:
        raise AssertionError('complete literal E B equals C identity failed')
    back, inverse_grid = basis_change(y_a, inverse=True)
    if inverse_grid or back != [[(x << s, y << s) for x, y in row] for row in a]:
        raise AssertionError('tensor B inverse did not recover every input coefficient')
    union_audit = audit_record()
    union_product = multiplication(a, b, union_audit)
    if union_product != direct_union(a, b):
        raise AssertionError('whole weighted-union polynomial record product is wrong')
    canonical_audit = audit_record()
    canonical_product = multiplication(y_a, y_b, canonical_audit)
    restored, _ = basis_change(canonical_product, inverse=True)
    literal_q, literal_q_grid = records.literal(a, b)
    if literal_q_grid != 3 * s or not records.equal(restored, 2 * s, literal_q, literal_q_grid):
        raise AssertionError('paid changed-basis word differs from canonical q polynomial product')
    if any(x % (1 << s) or y % (1 << s) for row in restored for x, y in row):
        raise AssertionError('canonical endpoint failed its known s trailing-zero removal')
    for audit in (union_audit, canonical_audit):
        if audit['integer_products'] != 3 * D or audit['polynomial_leaf_products'] != D:
            raise AssertionError('minimum-rank evaluation omitted a full Gaussian product')
        if audit['complete_decoded_real_coefficients'] != 3 * D * (2 * r - 1):
            raise AssertionError('complete signed product decode was cropped')
    # B's local cross ratio is -i. A full-support Clifford/C kernel has
    # cross ratios in {+1,-1}; monomial row/column gauges cannot change it.
    ratio_numerator = times((1, 1), (-1, 0))
    ratio_denominator = times((1, -1), (1, 0))
    if ratio_numerator == ratio_denominator or ratio_numerator == (-ratio_denominator[0], -ratio_denominator[1]):
        raise AssertionError('B cross-ratio discriminator collapsed to a Clifford sign')
    if records.equal(union_product, 0, restored, 2 * s):
        raise AssertionError('omitted source basis conversion negative did not discriminate')
    return dict(packet_axes=s, dimension=D, polynomial_coefficients=r,
                input_component_signed_bits=p, seed=SEED + 100 * s + 10 * r + p,
                **coefficients,
                literal_E_B_equals_C=True, all_tensor_B_input_coefficients_restored=True,
                whole_union_product_fields=2 * D * r,
                canonical_q_product_fields=2 * D * r,
                union_product_audit=union_audit, paid_canonical_product_audit=canonical_audit,
                B_forward_grid_bits=s, B_inverse_additional_grid_bits=0,
                paid_canonical_product_grid_before_known_zeros=2 * s,
                decoder_literal_temporary_grid_bits=3 * s,
                canonical_endpoint_grid_bits=s,
                B_cross_ratio='-i; reciprocal under local row/column swaps is i',
                omitted_basis_change_rejected=True,
                scope='Exact scalar coefficient/rank minors, full Gaussian polynomial record products and paid source/output basis changes. Native tensor B/Z time, activity compaction, all algorithm prefixes and complete asymptotic ledger remain open.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('workers must be positive')
    sources = (Path(__file__).resolve(), Path(records.__file__).resolve())
    hashes = {p.name: sha256(p.read_bytes()).hexdigest() for p in sources}
    if hashes[sources[1].name] != RECORD_SHA:
        raise AssertionError('frozen full-record product source changed')
    started_utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    tasks = [(1, 3, 4), (2, 5, 8)] if args.bounded else [(1, 3, 4), (2, 5, 8), (4, 3, 16), (6, 3, 32)]
    if args.workers == 1:
        cases = list(map(probe, tasks))
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(probe, tasks))
    if any(sha256(p.read_bytes()).hexdigest() != hashes[p.name] for p in sources):
        raise AssertionError('source closure changed during weighted-union controls')
    result = dict(status='PASS EXACT WEIGHTED-UNION BASIS AND COMPLETE POLYNOMIAL CONTROLS',
                  source_sha256=hashes, started_utc=started_utc,
                  completed_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                  bounded=args.bounded, cases=cases, seconds=time.monotonic() - started,
                  scope='Changed product basis with paid canonical source/output maps; no faster native B/Z supplier, complete child profile or new kappa.')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], cases=len(cases),
                          coefficient_controls=sum(c['complete_basis_product_coefficients'] for c in cases),
                          seconds=result['seconds'])), flush=True)


if __name__ == '__main__':
    main()
