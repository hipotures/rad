#!/usr/bin/env python3
"""Independent compact actual-frame fixture review, including exact n16 units.

No producer import or address path-sum algorithm is used. Pauli conjugation
binds every generator. The n16 fixtures factor into literal blocks of at most
three physical bits, fixing the global scalar independently. Small cases are
also checked by every Gaussian matrix coefficient.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import time

import conditioned_frame_review as g


TOPIC = Path(__file__).resolve().parents[2]
CONFIG = TOPIC/'configs/transfers/scalable-frame-review.json'
ALPHA, BETA = (Q(1, 2), Q(1, 2)), (Q(1, 2), Q(-1, 2))


def dot(a, b):
    return (a & b).bit_count() & 1


def embed(value, columns):
    out = 0
    for bit, column in enumerate(columns):
        if value >> bit & 1:
            out ^= column
    return out


def linear_rank(columns):
    pivots = {}
    for value in columns:
        while value:
            bit = value.bit_length()-1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value; break
    return len(pivots)


@lru_cache(None)
def inverse_columns(columns):
    n = len(columns); pivots = {}
    for j, value in enumerate(columns):
        coordinate = 1 << j
        while value:
            bit = value.bit_length()-1
            if bit in pivots:
                value ^= pivots[bit][0]; coordinate ^= pivots[bit][1]
            else:
                pivots[bit] = value, coordinate; break
    if len(pivots) != n:
        raise ValueError('Affine route is not a complete binary permutation')
    inverse = []
    for j in range(n):
        value, coordinate = 1 << j, 0
        while value:
            bit = value.bit_length()-1
            value ^= pivots[bit][0]; coordinate ^= pivots[bit][1]
        inverse.append(coordinate)
    if any(embed(column, columns) != 1 << j for j, column in enumerate(inverse)):
        raise ValueError('Independent route inversion failed')
    return tuple(inverse)


def quadratic(spec, value):
    return (spec['constant']+sum(c for j, c in enumerate(spec['linear']) if value >> j & 1)
            +sum(c for i, j, c in spec['cross'] if value >> i & 1 and value >> j & 1)) % 4


def pauli(word, initial, n):
    x, z, phase = initial
    for gate in word:
        kind = gate[0]
        if kind == 'C':
            label, direction = gate[1:]
            if dot(z, label):
                x ^= label; phase -= direction
        elif kind == 'H':
            bit = gate[1]; a, b = x >> bit & 1, z >> bit & 1
            phase += 2*a*b
            if a != b:
                x ^= 1 << bit; z ^= 1 << bit
        elif kind == 'D':
            phase += gate[1]*x.bit_count(); z ^= x
        elif kind == 'P':
            columns = tuple(gate[1]); inverse = inverse_columns(columns)
            x = embed(x, columns)
            z = sum(dot(z, column) << j for j, column in enumerate(inverse))
        elif kind == 'Q':
            spec = gate[1]; origin = quadratic(spec, 0); value = quadratic(spec, x)
            sign = 0
            for bit in range(n):
                difference = (quadratic(spec, x ^ (1 << bit))-quadratic(spec, 1 << bit)-value+origin) % 4
                if difference not in (0, 2):
                    raise ValueError('Quadratic chirp has a non-Pauli derivative')
                sign |= (difference//2) << bit
            phase += value-origin; z ^= sign
        elif kind == 'X':
            phase += 2*dot(z, gate[1])
        else:
            raise ValueError('Unknown exact elementary address gate')
    return x, z, phase % 4


def actual_word(spec):
    n = spec['n']; out = []
    for gate in spec['word']:
        kind = gate[0]
        if kind == 'C_line': out.append(('C', gate[1], 1))
        elif kind == 'C_line_inverse': out.append(('C', gate[1], -1))
        elif kind == 'C_full': out += [('C', 1 << bit, 1) for bit in range(n)]
        elif kind == 'quadratic_phase': out.append(('D', gate[1]))
        elif kind == 'linear_route': out.append(('P', tuple(gate[1])))
        elif kind == 'linear_route_inverse': out.append(('P', inverse_columns(tuple(gate[1]))))
        elif kind == 'H_tilde': out += [('H', bit, 1) for bit in range(gate[1])]
        else: raise ValueError('Unrecognized canonical literal word')
    return out


def invert_word(word):
    out = []
    for gate in reversed(word):
        if gate[0] in ('C', 'H'): out.append((gate[0], gate[1], -gate[2]))
        elif gate[0] == 'D': out.append(('D', -gate[1]))
        elif gate[0] == 'P': out.append(('P', inverse_columns(tuple(gate[1]))))
        else: raise ValueError('Unsupported literal inverse')
    return out


def compiled_word(form):
    return ([('P', inverse_columns(tuple(form['input_columns']))), ('Q', form['input_quadratic'])]
        + [('C', 1 << j, 1) for j in range(form['selected_rank_per_column'])]
        + [('Q', form['output_quadratic']), ('P', tuple(form['output_columns'])),
           ('X', form['output_affine_offset'])])


def line_matrix(n, label, undo=False):
    alpha, beta = (BETA, ALPHA) if undo else (ALPHA, BETA)
    size = 1 << n
    return [[alpha if a == b else beta if a == b ^ label else g.ZERO
             for b in range(size)] for a in range(size)]


def compress(value, group):
    return sum(((value >> bit) & 1) << j for j, bit in enumerate(group))


def groups(source, target):
    n = source['n']; components = [{j} for j in range(n)]
    for spec in (source, target):
        supports = spec.get('routing_columns', []) if spec['anchor'] == 'generic-dyadic-H' else [spec['line']] if 'line' in spec else []
        for value in supports:
            connected = {j for j in range(n) if value >> j & 1}
            touched = [component for component in components if component & connected]
            if touched:
                merged = set().union(*touched)
                components = [component for component in components if not component & merged]+[merged]
    result = sorted([tuple(sorted(component)) for component in components])
    if max(map(len, result)) > 3:
        raise ValueError('This fixture requires a new independent global-coefficient oracle')
    return result


def local_frame(spec, group):
    n, size = len(group), 1 << len(group); identity = g.identity(size)
    full = identity
    for bit in range(n): full = g.matmul(line_matrix(n, 1 << bit), full)
    anchor = spec['anchor']
    if anchor == 'identity': return identity
    if anchor == 'full-C': return full
    if anchor in ('odd-line-C', 'odd-kernel-C'):
        label = compress(spec['line'], group)
        if anchor == 'odd-line-C': return line_matrix(n, label) if label else identity
        return g.matmul(full, line_matrix(n, label, True)) if label else full
    columns = spec['routing_columns']; mask = sum(1 << bit for bit in group)
    local_columns = [compress(column, group) for column in columns if column & mask]
    if any(column & mask and column & ~mask for column in columns) or len(local_columns) != n:
        raise ValueError('Generic canonical route does not split into independent physical blocks')
    rank = sum(bool(column & mask) for column in columns[:spec['rank']])
    routing = [[g.ONE if a == embed(b, local_columns) else g.ZERO for b in range(size)] for a in range(size)]
    D_inverse = [[g.power(g.IMAGINARY, -a.bit_count()) if a == b else g.ZERO for b in range(size)] for a in range(size)]
    H = identity
    for bit in range(rank):
        S = [[g.IMAGINARY if a == b and a >> bit & 1 else g.ONE if a == b else g.ZERO
              for b in range(size)] for a in range(size)]
        H = g.matmul(g.matmul(g.matmul(S, line_matrix(n, 1 << bit)), S), H)
    # Generic rank-zero local spectators equal D^-2, not the identity override.
    return g.matmul(D_inverse, g.matmul(routing, g.matmul(H, g.matmul(g.adjoint(routing), D_inverse))))


def actual_coefficient(relatives, components, output, input_address):
    value = g.ONE
    for group, relative in zip(components, relatives):
        value = g.multiply(value, relative[compress(output, group)][compress(input_address, group)])
    return value


def candidate_coefficient(form, output, input_address):
    n, rank = form['n'], form['selected_rank_per_column']; mask = (1 << rank)-1
    a = embed(output ^ form['output_affine_offset'], inverse_columns(tuple(form['output_columns'])))
    b = embed(input_address, inverse_columns(tuple(form['input_columns'])))
    if a >> rank != b >> rank: return g.ZERO
    return g.multiply(g.power(g.IMAGINARY, quadratic(form['output_quadratic'], a)+quadratic(form['input_quadratic'], b)),
                      g.c_entry(rank, a & mask, b & mask))


def review(payload):
    index, case = payload; n = case['n']; source, target, form = case['source_actual_spec'], case['target_actual_spec'], case['normal_form']
    actual = invert_word(actual_word(source))+actual_word(target)
    if json.loads(json.dumps(actual)) != case['actual_relative_word']:
        raise ValueError('Retained relative word differs from exact canonical anchor expansion')
    candidate = compiled_word(form)
    expected_rank = 2*linear_rank(case['source_subspace']+case['target_subspace'])-linear_rank(case['source_subspace'])-linear_rank(case['target_subspace'])
    if form['selected_rank_per_column'] != expected_rank:
        raise ValueError('Selected child differs from exact Grassmann distance')
    generators = [(1 << j, 0, 0) for j in range(n)]+[(0, 1 << j, 0) for j in range(n)]
    for initial in generators:
        if pauli(actual, initial, n) != pauli(candidate, initial, n):
            raise ValueError('A complete conjugated Pauli generator differs')
    components = groups(source, target); output = form['output_affine_offset']
    relatives = [g.matmul(local_frame(target, group), g.adjoint(local_frame(source, group))) for group in components]
    original = actual_coefficient(relatives, components, output, 0)
    compiled = candidate_coefficient(form, output, 0)
    if original == g.ZERO or original != compiled:
        raise ValueError('Independent literal block coefficient rejects the retained global unit')
    coefficient_checks = 0
    if n <= 4:
        for a in range(1 << n):
            for b in range(1 << n):
                if actual_coefficient(relatives, components, a, b) != candidate_coefficient(form, a, b):
                    raise ValueError('A complete small physical matrix coefficient differs')
                coefficient_checks += 1
    altered = json.loads(json.dumps(form)); altered['input_quadratic']['constant'] = (altered['input_quadratic']['constant']+1) % 4
    global_negative = candidate_coefficient(altered, output, 0) != original
    altered = json.loads(json.dumps(form)); altered['output_affine_offset'] ^= 1
    affine_negative = any(pauli(compiled_word(altered), initial, n) != pauli(actual, initial, n) for initial in generators)
    if not global_negative or not affine_negative:
        raise ValueError('A global-unit or affine mutation was not rejected')
    return dict(index=index,n=n,selected_child_rank=expected_rank,
        all_conjugated_X_Z_generators=2*n,small_matrix_coefficients=coefficient_checks,
        literal_tensor_block_sizes=[len(group) for group in components],
        exact_nonzero_global_coefficient=[[str(x) for x in original]],
        global_coefficient_oracle='Independent literal tensor blocks, maximum3physicalbits; no producer path-sum imports',
        global_unit_corruption_rejected=global_negative, affine_offset_corruption_rejected=affine_negative,
        complete_operator_equality_up_to_scalar_bound=True, exact_scalar_fixed=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(); config = json.loads(CONFIG.read_text()); fixture = TOPIC/config['fixture']; helper = Path(g.__file__).resolve()
    for path, digest in [(fixture, config['fixture_sha256']), (helper, config['gaussian_arithmetic_sha256'])]:
        if sha256(path.read_bytes()).hexdigest() != digest: raise ValueError('Pinned fixture/arithmetic changed')
    hashes = {str(p.relative_to(TOPIC)): sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).resolve(), CONFIG, fixture, helper]}
    data = json.loads(fixture.read_text()); protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(),
        workers=args.workers,source_config_fixture_sha256=hashes,seed=None,producer_imports=False,scope=config['scope'])
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False); (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    started = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(review, enumerate(data['cases'])))
    if any(sha256((TOPIC/path).read_bytes()).hexdigest() != digest for path,digest in hashes.items()):
        raise ValueError('Source changed during immutable review')
    result = dict(status='INDEPENDENT SCALABLE FRAME FIXTURE PASS',cases=rows,seconds=time.monotonic()-started,
        scope=config['scope'],all_size_compiler_independently_implemented=False,native_transfer_proof=False,new_exponent=False)
    if args.output: (args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','seconds','scope']}))


if __name__ == '__main__': main()
