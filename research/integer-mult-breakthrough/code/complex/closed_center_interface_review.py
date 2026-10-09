#!/usr/bin/env python3
"""Import-free literal review of the closed center echo and odd-line kernels.

This verifier consumes scalar gate words as immutable data, reconstructs every
Gaussian operator independently, and explicitly retains the final full frame
on arbitrary dirty helpers.  The odd-weight-three extension requires a paid
affine quotient translation and an i phase for each selected column.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import random
from time import perf_counter


ZERO = (Q(0), Q(0))
ONE = (Q(1), Q(0))
ALPHA = (Q(1, 2), Q(1, 2))
BETA = (Q(1, 2), Q(-1, 2))
ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / 'fixtures' / 'complex'


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def scale(a, c):
    return a[0] * c, a[1] * c


def phase(a, exponent):
    exponent %= 4
    return ((a[0], a[1]), (-a[1], a[0]), (-a[0], -a[1]),
            (a[1], -a[0]))[exponent]


def embed(value, columns):
    result = 0
    for j, column in enumerate(columns):
        if value >> j & 1:
            result ^= column
    return result


def binary_basis(vectors):
    pivots = {}
    for original in vectors:
        value = original
        for bit in sorted(pivots, reverse=True):
            if value >> bit & 1:
                value ^= pivots[bit]
        if value:
            bit = value.bit_length() - 1
            pivots[bit] = value
    return tuple(pivots[bit] for bit in sorted(pivots))


def solve(rows, target):
    """Invert a square GF(2) matrix by independent augmented elimination."""
    n = len(rows)
    augmented = [row | ((target >> j & 1) << n) for j, row in enumerate(rows)]
    for bit in range(n):
        pivot = next((j for j in range(bit, n) if augmented[j] >> bit & 1), None)
        if pivot is None:
            raise ValueError('Restricted form is singular')
        augmented[bit], augmented[pivot] = augmented[pivot], augmented[bit]
        for j in range(n):
            if j != bit and augmented[j] >> bit & 1:
                augmented[j] ^= augmented[bit]
    return sum((augmented[j] >> n & 1) << j for j in range(n))


def line_interface(h, label):
    if not 0 < label < 1 << h or label.bit_count() % 2 != 1:
        raise ValueError('A nonzero odd-norm label is required')
    basis = binary_basis(x for x in range(1 << h) if (x & label).bit_count() % 2 == 0)
    if len(basis) != h - 1:
        raise AssertionError('Perpendicular dimension failed')
    gram = [sum(((x & y).bit_count() % 2) << j for j, y in enumerate(basis))
            for x in basis]
    dual = tuple(embed(solve(gram, 1 << j), basis) for j in range(h - 1))
    if any((x & y).bit_count() % 2 != int(i == j)
           for i, x in enumerate(basis) for j, y in enumerate(dual)):
        raise AssertionError('Input/output dual routing failed')
    offset = (label.bit_count() - 1) // 2 % 2
    return basis, dual, offset


def c_numerator(width, delta):
    """C^width coefficient numerator on the exact grid 2^-width."""
    result = (1, 0)
    for _ in range(width):
        result = mul(result, (1, 1))
    return phase(result, -delta.bit_count())


def kernel_numerator(h, label, delta):
    """F*C_label^-1 numerator on grid 2^-(h+1), without normal-form code."""
    return add(mul((1, -1), c_numerator(h, delta)),
               mul((1, 1), c_numerator(h, delta ^ label)))


def normal_form_probe(h, label):
    basis, dual, offset = line_interface(h, label)
    r = h - 1
    nonzero = checked = 0
    missing_offset = missing_unit = False
    for a in range(1 << r):
        da = embed(a, basis)
        for b in range(1 << r):
            db = embed(b, dual)
            chirp = -(da.bit_count() - a.bit_count()) - (db.bit_count() - b.bit_count())
            coefficient = scale(phase(c_numerator(r, a ^ b), chirp + offset), 4)
            for output_coset in range(2):
                for input_coset in range(2):
                    delta = da ^ db ^ ((output_coset ^ input_coset) * label)
                    actual = kernel_numerator(h, label, delta)
                    wanted = coefficient if output_coset == input_coset ^ offset else (0, 0)
                    if actual != wanted:
                        raise AssertionError(('Literal odd-line normal form failed', h, label, a, b,
                                              output_coset, input_coset, actual, wanted))
                    checked += 1
                    nonzero += actual != (0, 0)
                    no_offset = coefficient if output_coset == input_coset else (0, 0)
                    no_unit = scale(phase(c_numerator(r, a ^ b), chirp), 4)
                    no_unit = no_unit if output_coset == input_coset ^ offset else (0, 0)
                    missing_offset |= actual != no_offset
                    missing_unit |= actual != no_unit
    if offset and not (missing_offset and missing_unit):
        raise AssertionError('Required affine translation or column phase was undetected')
    return dict(h=h, label=label, weight=label.bit_count(), child_width=r,
                output_columns=list(basis) + [label], input_columns=list(dual) + [label],
                quotient_bit_flip=offset, global_i_exponent_per_column=offset,
                exact_matrix_entries=checked, nonzero_matrix_entries=nonzero,
                missing_offset_rejected=missing_offset, missing_unit_rejected=missing_unit)


def tensor_probe(h, label, columns):
    """Compare complete packed matrices; the unit is paid per column."""
    basis, dual, offset = line_interface(h, label)
    r = h - 1
    local = []
    for delta in range(1 << h):
        local.append(kernel_numerator(h, label, delta))
    checked = 0
    charged_once_detected = False
    volume = 1 << (h * columns)
    for output in range(volume):
        oa = [(output >> (h * column)) & ((1 << h) - 1) for column in range(columns)]
        for incoming in range(volume):
            ib = [(incoming >> (h * column)) & ((1 << h) - 1) for column in range(columns)]
            actual = (1, 0)
            child = (1, 0)
            exponent = 0
            admitted = True
            for a, b in zip(oa, ib):
                actual = mul(actual, local[embed(a & ((1 << r) - 1), basis)
                                           ^ embed(b & ((1 << r) - 1), dual)
                                           ^ (((a >> r) ^ (b >> r)) * label)])
                admitted &= (a >> r) == (b >> r) ^ offset
                child = mul(child, c_numerator(r, (a ^ b) & ((1 << r) - 1)))
                exponent += -(embed(a & ((1 << r) - 1), basis).bit_count()
                              - (a & ((1 << r) - 1)).bit_count())
                exponent += -(embed(b & ((1 << r) - 1), dual).bit_count()
                              - (b & ((1 << r) - 1)).bit_count())
            wanted = scale(phase(child, exponent + offset * columns), 4 ** columns) if admitted else (0, 0)
            if wanted != actual:
                raise AssertionError('Complete tensor normal form failed')
            once = scale(phase(child, exponent + offset), 4 ** columns) if admitted else (0, 0)
            charged_once_detected |= once != actual
            checked += 1
    if offset and columns > 1 and not charged_once_detected:
        raise AssertionError('Per-column i phase undercharge was undetected')
    return dict(h=h, label=label, selected_columns=columns,
                complete_matrix_entries=checked, one_child_width=r * columns,
                quotient_bit_flips=offset * columns,
                global_i_exponent=(offset * columns) % 4,
                column_unit_charged_once_rejected=charged_once_detected)


def translate_c(values, mask, inverse=False):
    data = list(values)
    a, b = (BETA, ALPHA) if inverse else (ALPHA, BETA)
    for index in range(len(data)):
        partner = index ^ mask
        if index < partner:
            left, right = data[index], data[partner]
            data[index] = add(mul(a, left), mul(b, right))
            data[partner] = add(mul(b, left), mul(a, right))
    return data


def full_c(values, h, columns, inverse=False):
    data = list(values)
    for bit in range(h * columns):
        data = translate_c(data, 1 << bit, inverse)
    return data


def line_c(values, label, h, columns, inverse=False):
    data = list(values)
    for column in range(columns):
        # Native convention: row-bit-major selected address columns.
        mask = sum((label >> bit & 1) << (bit * columns + column) for bit in range(h))
        data = translate_c(data, mask, inverse)
    return data


def kernel_c(values, label, h, columns):
    return full_c(line_c(values, label, h, columns, True), h, columns)


def reverse_word(word):
    result = []
    for event in reversed(word):
        kind, a, *rest = event
        if kind == 'swap':
            result.append(event)
        elif kind == 'scale':
            result.append((kind, a, 1 / Q(rest[0])))
        elif kind == 'add':
            b, c = rest
            result.append((kind, a, b, -Q(c)))
        else:
            raise ValueError('Unknown gate')
    return result


def apply_word(word, bank):
    for kind, a, *rest in word:
        if kind == 'swap':
            b, = rest
            bank[a], bank[b] = bank[b], bank[a]
        elif kind == 'scale':
            c, = rest
            bank[a] = [scale(z, Q(c)) for z in bank[a]]
        elif kind == 'add':
            b, c = rest
            bank[a] = [add(z, scale(w, Q(c))) for z, w in zip(bank[a], bank[b])]
        else:
            raise ValueError('Unknown scalar gate')


def data_spec(kind):
    if kind == 'orthogonal-color':
        return dict(kind=kind, h=3, labels=[1, 2, 4], q=1,
                    word=[('add', 0, 1, '1'), ('add', 0, 2, '1')],
                    decoder=[[Q(1)] for _ in range(3)])
    if kind == 'triple-total':
        base = json.loads((FIXTURES / 'triple-total-local-word.json').read_text())['base']
        subsets = base['source_order']
        return dict(kind=kind, h=4, labels=[sum(1 << j for j in source) for source in subsets],
                    q=4, word=base['gates'],
                    decoder=[[Q(3 * int(0 in s) - 1, 2)]
                             + [Q(int(i in s) - int(0 in s), 2) for i in range(1, 4)]
                             for s in subsets])
    if kind == 'single-total':
        fixture = json.loads((FIXTURES / 'total-center-local-words.json').read_text())
        subsets = fixture['pivot_source_order']
        pairs = fixture['pair_order']
        decoder = []
        for source in subsets:
            alphas = [8 * int(set(pair).issubset(source)) - 3 * len(set(pair).intersection(source))
                      for pair in pairs]
            decoder.append([Q(12 + 10 * alphas[0], 32)]
                           + [Q(value - alphas[0], 32) for value in alphas[1:]])
        return dict(kind=kind, h=7, labels=[sum(1 << j for j in s) for s in subsets], q=21,
                    word=fixture['base_word'], decoder=decoder)
    raise ValueError('Unknown scalar data fixture')


def central(kind, a, b):
    overlap = (a & b).bit_count()
    if kind == 'orthogonal-color':
        return Q(1)
    if kind == 'triple-total':
        return Q(overlap - 1, 2)
    return Q((overlap - 1) * (overlap - 3), 8)


def scatter(y, z, decoder, sign):
    for row, coefficients in enumerate(decoder):
        for feature, c in enumerate(coefficients):
            if c:
                y[row] = [add(a, scale(b, sign * c)) for a, b in zip(y[row], z[feature])]


def center_echo(spec, initial, columns, omit_return=False):
    """Literal word with input x=C_T*x_virtual, y,z at identity."""
    x, y, z = [[list(row) for row in group] for group in initial]
    h = spec['h']
    inverse = reverse_word(spec['word'])
    apply_word(spec['word'], z)
    scatter(y, z, spec['decoder'], -1)
    apply_word(inverse, z)
    for j, label in enumerate(spec['labels']):
        z[j] = line_c(z[j], label, h, columns)
        z[j] = [add(a, b) for a, b in zip(z[j], x[j])]
        z[j] = kernel_c(z[j], label, h, columns)
    apply_word(spec['word'], z)
    for j in range(spec['q']):
        z[j] = full_c(z[j], h, columns, True)
    scatter(y, z, spec['decoder'], 1)
    for j in range(spec['q']):
        if not (omit_return and j == 0):
            z[j] = full_c(z[j], h, columns)
    apply_word(inverse, z)
    for j, label in enumerate(spec['labels']):
        x[j] = kernel_c(x[j], label, h, columns)
        z[j] = [add(a, scale(b, -1)) for a, b in zip(z[j], x[j])]
        y[j] = kernel_c(y[j], label, h, columns)
    return x, y, z


def direct_endpoint(spec, initial, columns):
    """Polynomial K and literal endpoint convolutions, without B or D."""
    h = spec['h']
    x0, y0, z0 = initial
    x = [line_c(row, label, h, columns, True) for row, label in zip(x0, spec['labels'])]
    y = [list(row) for row in y0]
    for i, target in enumerate(spec['labels']):
        for j, source in enumerate(spec['labels']):
            c = central(spec['kind'], target, source)
            if c:
                y[i] = [add(a, scale(b, c)) for a, b in zip(y[i], x[j])]
    return ([full_c(row, h, columns) for row in x],
            [kernel_c(row, label, h, columns) for row, label in zip(y, spec['labels'])],
            [full_c(row, h, columns) for row in z0])


def physical_probe(kind, columns, complete, dirty_fields=2):
    spec = data_spec(kind)
    h = spec['h']; v = len(spec['labels']); size = 1 << (h * columns)
    digest = sha256(); cases = 0
    for bank in range(3 * v):
        for address in range(size) if complete else (0,):
            data = [[ONE if row == bank and a == address else ZERO for a in range(size)]
                    for row in range(3 * v)]
            initial = data[:v], data[v:2 * v], data[2 * v:]
            actual = center_echo(spec, initial, columns)
            if actual != direct_endpoint(spec, initial, columns):
                raise AssertionError(('Independent physical center echo failed', kind, columns, bank, address))
            digest.update(str(actual).encode())
            cases += 1
    rng = random.Random(20261009 + h * 100 + columns)
    for _ in range(dirty_fields):
        data = [[(Q(rng.randrange(-5, 6), 4), Q(rng.randrange(-5, 6), 8)) for _ in range(size)]
                for _ in range(3 * v)]
        initial = data[:v], data[v:2 * v], data[2 * v:]
        actual = center_echo(spec, initial, columns)
        if actual != direct_endpoint(spec, initial, columns):
            raise AssertionError('Full arbitrary-dirty Gaussian field failed')
        digest.update(str(actual).encode())
    data = [[ONE if row == 2 * v and a == 0 else ZERO for a in range(size)]
            for row in range(3 * v)]
    initial = data[:v], data[v:2 * v], data[2 * v:]
    wanted = direct_endpoint(spec, initial, columns)
    if center_echo(spec, initial, columns, True) == wanted:
        raise AssertionError('Omitted feature return was not rejected')
    if wanted[2] == initial[2]:
        raise AssertionError('Wrong raw dirty identity endpoint was not rejected')
    for final, original in zip(wanted[2], initial[2]):
        if full_c(final, h, columns, True) != original:
            raise AssertionError('Virtual arbitrary-dirty restoration failed')
    q = spec['q']; widths = {1: v, h - 1: 3 * v, h: 2 * q}
    charge = sum(width * multiplicity for width, multiplicity in widths.items())
    if charge != 3 * v * h - 2 * v + 2 * q * h:
        raise AssertionError('Explicit component rank ledger failed')
    return dict(family=kind, h=h, selected_columns=columns, physical_banks=3 * v,
                address_volume=size, explicitly_replayed_basis_columns=cases,
                complete_basis_columns=3 * v * size,
                coverage='All physical basis columns' if complete else 'Origin columns plus proved common-XOR covariance',
                additional_complete_dirty_fields=dirty_fields,
                exact_output_values=(cases + dirty_fields) * 3 * v * size,
                output_sha256=digest.hexdigest(), omitted_feature_return_rejected=True,
                wrong_raw_dirty_identity_rejected=True, virtual_dirty_restored=True,
                child_width_multiplicities=widths, per_column_rank_charge=charge,
                endpoint_floor=3 * v * h - 2 * v, closed_feature_release=2 * q * h)


def worker(task):
    started = perf_counter()
    kind, payload = task
    if kind == 'interfaces':
        cases = [normal_form_probe(h, label) for h, label in payload]
        tensor = [tensor_probe(3, 7, 2), tensor_probe(3, 1, 2)]
        try:
            line_interface(4, 3)
        except ValueError:
            even_rejected = True
        else:
            raise AssertionError('Even-norm label accepted under rank h-1 contract')
        return dict(kind=kind, cases=cases, tensor_cases=tensor,
                    even_norm_label_rejected=even_rejected, seconds=perf_counter() - started)
    family, columns, complete, fields = payload
    return dict(kind=kind, result=physical_probe(family, columns, complete, fields),
                seconds=perf_counter() - started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        raise ValueError('Use one to four workers')
    args.output.mkdir(parents=True, exist_ok=False)
    started_utc = datetime.now(timezone.utc).isoformat()
    started = perf_counter()
    labels = [(h, label) for h in range(1, 5 if args.bounded else 8)
              for label in range(1, 1 << h) if label.bit_count() % 2]
    tasks = [('interfaces', labels),
             ('physical', ('orthogonal-color', 1, not args.bounded, 2)),
             ('physical', ('orthogonal-color', 2, False, 2)),
             ('physical', ('triple-total', 1, not args.bounded, 2))]
    if not args.bounded:
        tasks.append(('physical', ('single-total', 1, False, 1)))
    effective = [Path(__file__), FIXTURES / 'triple-total-local-word.json',
                 FIXTURES / 'total-center-local-words.json']
    hashes = {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in effective}
    protocol = dict(started_utc=started_utc, workers=args.workers, bounded=args.bounded,
                    native_threads_each=1, seeds='20261009 + 100*h + selected_columns',
                    dependency='Python standard library only; no producer imports',
                    effective_sha256=hashes, tasks=tasks,
                    reference_producer_sha256='684cd04a567881dae1c117d9966bbd59a8f9b48f1cfa674bca91ac4968948252',
                    hypothesis='Closed Kx release is physically correct, and every odd label admits one relative rank h-1 child with paid affine/unit corrections.')
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(worker, tasks))
    for p in effective:
        if sha256(p.read_bytes()).hexdigest() != hashes[str(p.relative_to(ROOT))]:
            raise AssertionError('Immutable effective input changed during review')
    result = dict(status='PASS INDEPENDENT EXACT PHYSICAL CENTER AND ODD-LINE REVIEW',
                  started_utc=started_utc, completed_utc=datetime.now(timezone.utc).isoformat(),
                  elapsed_seconds=perf_counter() - started, results=results,
                  scope='Finite exact Gaussian operators and stated algebraic component rank ledger. This is center-only Kx; native routing, chirps, fixed-tape precision and complete multiplier recurrence remain obligations. No larger exponent is asserted.')
    (args.output / 'certificate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'started_utc', 'completed_utc', 'elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    main()
