#!/usr/bin/env python3
"""Import-free literal review of Gaussian-dyadic conditioned frame fixtures."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time


TOPIC = Path(__file__).resolve().parents[2]
CONFIG = TOPIC/'configs/transfers/conditioned-frame-review.json'
ZERO, ONE, IMAGINARY = (Q(0), Q(0)), (Q(1), Q(0)), (Q(0), Q(1))


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def multiply(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def conjugate(a):
    return a[0], -a[1]


def power(a, e):
    if e < 0:
        norm = a[0]*a[0]+a[1]*a[1]
        a, e = (a[0]/norm, -a[1]/norm), -e
    result = ONE
    for _ in range(e):
        result = multiply(result, a)
    return result


def unit(e, s):
    return multiply(power((Q(1), Q(1)), e), power(IMAGINARY, s % 4))


def extract_unit(a):
    """Recover by rational norm plus four direct candidates, not division signs."""
    norm = a[0]*a[0]+a[1]*a[1]
    if not norm or norm.numerator & (norm.numerator-1) or norm.denominator & (norm.denominator-1):
        return None
    exponent = norm.numerator.bit_length()-norm.denominator.bit_length()
    for phase in range(4):
        if unit(exponent, phase) == a:
            return exponent, phase
    return None


def identity(n):
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]


def matmul(a, b):
    columns = list(zip(*b))
    return [[sum_complex(multiply(x, y) for x, y in zip(row, column) if x != ZERO and y != ZERO)
             for column in columns] for row in a]


def sum_complex(values):
    result = ZERO
    for value in values:
        result = add(result, value)
    return result


def matvec(matrix, values):
    return [sum_complex(multiply(x, y) for x, y in zip(row, values)) for row in matrix]


def adjoint(matrix):
    return [[conjugate(matrix[j][i]) for j in range(len(matrix))] for i in range(len(matrix))]


def decode(operator):
    denominator = 1 << operator['denominator_bits']
    return [[(Q(a, denominator), Q(b, denominator)) for a, b in row]
            for row in operator['numerators']]


def symmetric_rows(n, code):
    result, index = [0]*n, 0
    for i in range(n):
        for j in range(i, n):
            if code >> index & 1:
                result[i] |= 1 << j
                result[j] |= 1 << i
            index += 1
    return result


def graph_operator(n, code):
    size = 1 << n
    rows = symmetric_rows(n, code)
    def phase(x):
        diagonal = sum((rows[i] >> i & 1)*(x >> i & 1) for i in range(n))
        crossing = sum((rows[i] >> j & 1)*(x >> i & 1)*(x >> j & 1)
                       for i in range(n) for j in range(i+1, n))
        return power(IMAGINARY, (diagonal+2*crossing) % 4)
    return [[sum_complex(multiply((Q(-1 if ((a ^ b)&x).bit_count() & 1 else 1, size), Q(0)), phase(x))
                         for x in range(size)) for b in range(size)] for a in range(size)]


def c_entry(rank, a, b):
    # Literal two-by-two factors provide an oracle independent of the producer's
    # valuation/phase formula for C^rank.
    alpha, beta = (Q(1, 2), Q(1, 2)), (Q(1, 2), Q(-1, 2))
    result = ONE
    for j in range(rank):
        result = multiply(result, beta if (a ^ b) >> j & 1 else alpha)
    return result


def reconstruct(normal_form, size):
    matrix = [[ZERO for _ in range(size)] for _ in range(size)]
    inputs, outputs, ranks, wrappers = [], [], set(), []
    for block in normal_form['blocks']:
        rank, volume = block['rank'], 1 << block['rank']
        if block['volume_records'] != volume or any(len(block[k]) != volume for k in
                ['input_addresses', 'output_addresses', 'input_scales', 'output_scales']):
            raise ValueError('Incomplete block stock')
        inputs += block['input_addresses']; outputs += block['output_addresses']; ranks.add(rank)
        for e, s in block['input_scales']+block['output_scales']:
            if extract_unit(unit(e, s)) != (e, s % 4):
                raise ValueError('Unit wrapper failed independent norm extraction')
            wrappers.append((e, s))
        for a in range(volume):
            for b in range(volume):
                value = multiply(unit(*block['output_scales'][a]),
                    multiply(c_entry(rank, a, b), unit(*block['input_scales'][b])))
                matrix[block['output_addresses'][a]][block['input_addresses'][b]] = value
    if sorted(inputs) != list(range(size)) or sorted(outputs) != list(range(size)):
        raise ValueError('Incomplete or repeated address permutation')
    return matrix, ranks, wrappers


def case(item):
    n, size = 3, 8
    if item['parent_clifford_word'] or item['parent_clifford_index'] != 0:
        raise ValueError('This fixture contract expects identity parents')
    G = graph_operator(n, item['terminal_graph_code'])
    if matmul(G, adjoint(G)) != identity(size):
        raise ValueError('Own graph operator is not unitary')
    def predicate(x):
        family = item['family']
        return x == 7 if family == 'singleton' else (x & 3) == 3 if family == 'pair-control' else \
            bool(x.bit_count() & 1) if family == 'parity' else bool(x & 1) if family == 'bit' else None
    weights = [[-1, 0] if predicate(x) else [0, 0] for x in range(size)]
    if weights != item['conditioning_weights']:
        raise ValueError('Conditioning predicate or inverse-(1+i) weights changed')
    D = [[unit(*weights[a]) if a == b else ZERO for b in range(size)] for a in range(size)]
    Di = [[unit(-weights[a][0], -weights[a][1]) if a == b else ZERO for b in range(size)] for a in range(size)]
    expected, expected_inverse = matmul(D, adjoint(G)), matmul(G, Di)
    literal, literal_inverse = decode(item['literal_operator']), decode(item['literal_inverse'])
    if literal != expected or literal_inverse != expected_inverse:
        raise ValueError('Own physical matrix construction differs from retained matrices')
    if matmul(literal, literal_inverse) != identity(size) or matmul(literal_inverse, literal) != identity(size):
        raise ValueError('Complete physical inverse identity failed')
    forward, ranks, wrappers = reconstruct(item['forward_normal_form'], size)
    reverse, inverse_ranks, reverse_wrappers = reconstruct(item['inverse_normal_form'], size)
    if forward != literal or reverse != literal_inverse or ranks != {item['expected_uniform_rank']} or inverse_ranks != ranks:
        raise ValueError('Literal C-block forward/inverse reconstruction failed')
    for value in [x for row in literal+literal_inverse for x in row if x != ZERO]:
        if extract_unit(value) is None:
            raise ValueError('A retained nonzero matrix entry is not a Gaussian-dyadic unit')
    for j in range(size):
        values = [ONE if i == j else ZERO for i in range(size)]
        if matvec(literal_inverse, matvec(literal, values)) != values:
            raise ValueError('Complete basis inverse replay failed')
    for field in range(4):
        values = [(Q(((i+3)*(field+1) % 23)-11, 1 << (field+1)),
                   Q(((i+1)*(field+4) % 19)-9, 1 << (field+2))) for i in range(size)]
        if matvec(literal_inverse, matvec(literal, values)) != values:
            raise ValueError('Arbitrary Gaussian-dyadic dirty stream was not restored')
    return dict(family=item['family'], rank=item['expected_uniform_rank'],
        terminal_graph_code=item['terminal_graph_code'], complete_matrix_entries_checked=128,
        complete_basis_vectors_replayed=8, arbitrary_dirty_fields_replayed=4,
        normal_form_wrapper_count=len(wrappers)+len(reverse_wrappers),
        wrapper_valuation_range=[min(e for e, _ in wrappers+reverse_wrappers),max(e for e, _ in wrappers+reverse_wrappers)],
        dominating_rank=item['dominating_rank'])


def binary_basis(vectors):
    rows = list(vectors); r = 0
    for column in range(5, -1, -1):
        pivot = next((i for i in range(r, len(rows)) if rows[i] >> column & 1), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i] >> column & 1:
                rows[i] ^= rows[r]
        r += 1
    return tuple(rows[:r])


def independent_lagrangians():
    def pairing(a, b):
        return (((a & 7) & (b >> 3)).bit_count()+
                ((b & 7) & (a >> 3)).bit_count()) & 1
    result = set()
    for a, b, c in combinations(range(1, 64), 3):
        if pairing(a, b) or pairing(a, c) or pairing(b, c):
            continue
        basis = binary_basis([a, b, c])
        if len(basis) == 3:
            result.add(basis)
    if len(result) != 135:
        raise ValueError('Independent isotropic subspace count failed')
    return sorted(result)


def dominance_audit(directory, config):
    lags = independent_lagrangians()
    graphs = [binary_basis([(1 << i)|(row << 3) for i, row in enumerate(symmetric_rows(3, code))])
              for code in range(64)]
    baseline = [[len(binary_basis(list(lag)+list(graph)))-3 for graph in graphs] for lag in lags]
    totals, inputs = [], {}
    for family, expected_admitted in zip(config['families'], config['expected_raw_admitted_edges']):
        path = directory/(family+'.json'); raw = path.read_bytes()
        inputs[str(path)] = sha256(raw).hexdigest()
        data = json.loads(raw)
        if data['source_sha256'] != config['producer_source_sha256']:
            raise ValueError('Complete dominance input producer hash changed')
        rows = data['componentwise_dominance_certificates']
        if len(rows) != 540 or data['unresolved_candidates']:
            raise ValueError('Producer candidate stock is incomplete')
        keys = {(row['parent_clifford_candidate'], row['conditioning_exponent'], row['conditioning_phase'])
                for row in rows}
        if keys != {(candidate, e, s) for candidate in range(135)
                    for e, s in [(1, 0), (-1, 0), (2, 3), (-2, 1)]}:
            raise ValueError('Complete distinct candidate stock failed')
        admitted = 0
        for row in rows:
            codes = row['admitted_graph_codes']; costs = [Q(x) for x in row['average_ranks']]
            dominator = row['dominating_clifford_candidate']
            if not codes or len(set(codes)) != len(codes) or len(codes) != len(costs):
                raise ValueError('Empty or inconsistent admitted interface')
            expected = [baseline[dominator][code] for code in codes]
            if expected != row['dominating_ranks'] or any(a > b for a, b in zip(expected, costs)):
                raise ValueError('Independent exact componentwise domination failed')
            if any(x.denominator != 1 or not 0 <= x <= 3 for x in costs):
                raise ValueError('A reported uniform rank is invalid')
            admitted += len(codes)
        if admitted != expected_admitted:
            raise ValueError('Complete admitted count failed')
        profiles = data['block_profiles']
        if any(len({rank for rank, _ in row['profile']}) != 1 for row in profiles):
            raise ValueError('A reported admitted block profile is nonuniform')
        totals.append(dict(family=family, candidate_rows=540, admitted_edges=admitted,
                           uniform_profiles=len(profiles), independent_dominator_ranks=True))
    return dict(complete_rows=2160, admitted_edges=sum(x['admitted_edges'] for x in totals),
                families=totals, input_sha256=inputs,
                scope='Checks all retained dominance rows against independently enumerated isotropic geometry; does not independently classify all screened physical edges.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--dominance-directory', type=Path)
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text()); fixture = TOPIC/config['fixture']
    if sha256(fixture.read_bytes()).hexdigest() != config['fixture_sha256']:
        raise ValueError('Pinned literal fixture changed')
    data = json.loads(fixture.read_text())
    if data['source_sha256'] != config['producer_source_sha256'] or data['dimension'] != 3 or len(data['cases']) != 16:
        raise ValueError('Retained fixture contract changed')
    hashes = {str(p.relative_to(TOPIC)): sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).resolve(), CONFIG, fixture]}
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        source_config_fixture_sha256=hashes, scope=config['scope'], seeds=None)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    started = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(case, data['cases']))
    if {(row['family'], row['rank']) for row in rows} != {(family, r) for family in config['families'] for r in range(4)}:
        raise ValueError('Independent literal coverage is incomplete')
    unit_round_trips = 0
    for e in range(-12, 13):
        for s in range(4):
            if extract_unit(unit(e, s)) != (e, s):
                raise ValueError('Canonical norm-based unit round trip failed')
            unit_round_trips += 1
    if extract_unit((Q(3), Q(0))) is not None or extract_unit(ZERO) is not None:
        raise ValueError('Nonunit Gaussian control was accepted')
    # The failed denominator sign convention would represent 1/2 as -1/2.
    if unit(-2, 3) != (Q(-1, 2), Q(0)) or unit(-2, 1) != (Q(1, 2), Q(0)):
        raise ValueError('Legacy denominator phase negative control failed')
    wrong = json.loads(json.dumps(data['cases'][0]['forward_normal_form']))
    selected = next(block for block in wrong['blocks'] if block['output_scales'][0] != [0, 0])
    selected['output_scales'][0] = [0, 0]
    if reconstruct(wrong, 8)[0] == decode(data['cases'][0]['literal_operator']):
        raise ValueError('Omitted wrapper negative control failed')
    dominance = dominance_audit(args.dominance_directory, config) if args.dominance_directory else None
    if any(sha256((TOPIC/p).read_bytes()).hexdigest() != value for p, value in hashes.items()):
        raise ValueError('Pinned source/config/fixture changed during attempt')
    result = dict(status='INDEPENDENT EXACT CONDITIONED-FRAME LITERAL REVIEW PASS', cases=rows,
        complete_matrix_entries_checked=sum(x['complete_matrix_entries_checked'] for x in rows),
        complete_basis_vectors_replayed=128, arbitrary_dirty_fields_replayed=64,
        canonical_unit_round_trips=unit_round_trips, optional_complete_dominance_audit=dominance,
        negative_controls=['zero and nonunit Gaussian scalar rejected',
            'legacy denominator phase predicts -1/2 rather than 1/2', 'omitted nontrivial wrapper changes physical matrix'],
        seconds=time.monotonic()-started, scope=config['scope'])
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ['status','complete_matrix_entries_checked',
        'complete_basis_vectors_replayed','arbitrary_dirty_fields_replayed','seconds']}))


if __name__ == '__main__':
    main()
