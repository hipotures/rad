#!/usr/bin/env python3
"""Independent literal dirty birth-reuse word through one degenerate frame.

Only independent Gaussian rational arithmetic is imported. Every actual frame
is constructed by literal gates. Relative transitions are independently split
into complete monomial/C blocks. The small component is not a native transfer
or a canonical whole C primitive.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

import conditioned_frame_review as g


TOPIC = Path(__file__).resolve().parents[2]
CONFIG = TOPIC/'configs/transfers/degenerate-birth-review.json'
ZERO, ONE = g.ZERO, g.ONE
ALPHA, BETA = (Q(1, 2), Q(1, 2)), (Q(1, 2), Q(-1, 2))


def divide(a, b):
    norm = b[0]*b[0]+b[1]*b[1]
    if not norm:
        raise ValueError('Zero Gaussian divisor')
    return (a[0]*b[0]+a[1]*b[1])/norm, (a[1]*b[0]-a[0]*b[1])/norm


def scale(a, c):
    return a[0]*c, a[1]*c


def line(label):
    return [[ALPHA if a == b else BETA if a == b ^ label else ZERO
             for b in range(16)] for a in range(16)]


def embed(x, columns):
    value = 0
    for j, column in enumerate(columns):
        if x >> j & 1:
            value ^= column
    return value


def literal_frames():
    I = g.identity(16)
    F = I
    for bit in range(4):
        F = g.matmul(line(1 << bit), F)
    columns = (1, 6, 2, 8)
    routing = [[ONE if a == embed(b, columns) else ZERO for b in range(16)]
               for a in range(16)]
    D_inverse = [[g.power(g.IMAGINARY, -a.bit_count()) if a == b else ZERO
                  for b in range(16)] for a in range(16)]
    H = I
    for bit in range(2):
        S = [[g.IMAGINARY if a == b and a >> bit & 1 else ONE if a == b else ZERO
              for b in range(16)] for a in range(16)]
        H = g.matmul(g.matmul(g.matmul(S, line(1 << bit)), S), H)
    E = g.matmul(D_inverse, g.matmul(routing,
        g.matmul(H, g.matmul(g.adjoint(routing), D_inverse))))
    frames = {'I': I, 'E': E, 'F': F, 'A1': line(1), 'A7': line(7)}
    for label in (8, 14):
        frames['K'+str(label)] = g.matmul(F, g.adjoint(line(label)))
    for matrix in frames.values():
        if g.matmul(matrix, g.adjoint(matrix)) != I or g.matmul(g.adjoint(matrix), matrix) != I:
            raise ValueError('A literal frame is not exactly unitary')
    return frames


def normal_form(matrix):
    """Recover complete small monomial/C blocks by support and character rows.

    The dephased sign group labels both address permutations independently of
    any symplectic producer. Literal reconstruction checks every coefficient.
    Full finite permutations/gauges are paid interfaces, not a tape algorithm.
    """
    unseen = set(range(16)); blocks = []
    while unseen:
        outputs = {min(unseen)}; inputs = set()
        while True:
            new_inputs = {b for a in outputs for b in range(16) if matrix[a][b] != ZERO}
            new_outputs = {a for b in new_inputs for a in range(16) if matrix[a][b] != ZERO}
            if new_inputs == inputs and new_outputs == outputs:
                break
            inputs, outputs = new_inputs, new_outputs
        if not outputs <= unseen or len(inputs) != len(outputs) or len(inputs) & (len(inputs)-1):
            raise ValueError('Relative support is not a complete equal power-two block')
        unseen -= outputs
        ins, outs = sorted(inputs), sorted(outputs)
        r = (len(ins)-1).bit_length(); origin = matrix[outs[0]][ins[0]]
        patterns = []
        for a in outs:
            pattern = 0
            for j, b in enumerate(ins):
                sign = divide(g.multiply(matrix[a][b], origin),
                              g.multiply(matrix[a][ins[0]], matrix[outs[0]][b]))
                if sign not in (ONE, (Q(-1), Q(0))):
                    raise ValueError('Dephased relative block is not a binary character table')
                if sign != ONE:
                    pattern |= 1 << j
            patterns.append(pattern)
        generators = []; combinations = {0: 0}
        for pattern in patterns:
            if pattern in combinations:
                continue
            bit = 1 << len(generators); generators.append(pattern)
            combinations.update({old ^ pattern: coordinate | bit
                                 for old, coordinate in list(combinations.items())})
        if len(generators) != r or len(combinations) != len(outs):
            raise ValueError('Relative sign block does not have exactly the claimed rank')
        input_coordinates = [sum(((row >> j) & 1) << bit for bit, row in enumerate(generators))
                             for j in range(len(ins))]
        output_coordinates = [combinations[row] for row in patterns]
        if sorted(input_coordinates) != list(range(len(ins))) or sorted(output_coordinates) != list(range(len(outs))):
            raise ValueError('Relative adapter omits or repeats an address')
        alpha = g.power(ALPHA, r)
        input_gauges = [divide(matrix[outs[0]][b],
                               g.multiply(alpha, g.power((Q(0), Q(-1)), coordinate.bit_count())))
                        for b, coordinate in zip(ins, input_coordinates)]
        output_gauges = [divide(matrix[a][ins[0]],
            g.multiply(input_gauges[0], g.multiply(alpha,
                g.power((Q(0), Q(-1)), coordinate.bit_count()))))
            for a, coordinate in zip(outs, output_coordinates)]
        phases = []
        for value in input_gauges+output_gauges:
            candidates = [s for s in range(4) if g.power(g.IMAGINARY, s) == value]
            if len(candidates) != 1:
                raise ValueError('Relative gauge is not a literal fourth-root unit')
            phases.append(candidates[0])
        for a, ac, ag in zip(outs, output_coordinates, output_gauges):
            for b, bc, bg in zip(ins, input_coordinates, input_gauges):
                if g.multiply(ag, g.multiply(g.c_entry(r, ac, bc), bg)) != matrix[a][b]:
                    raise ValueError('Independent complete monomial/C reconstruction failed')
        blocks.append(dict(rank=r, input_addresses=ins, output_addresses=outs,
            input_coordinates=input_coordinates, output_coordinates=output_coordinates,
            input_phase_exponents=phases[:len(ins)], output_phase_exponents=phases[len(ins):]))
    ranks = {block['rank'] for block in blocks}
    if len(ranks) != 1:
        raise ValueError('Selected transition is not a uniform one-child width')
    return dict(selected_rank_per_column=next(iter(ranks)), blocks=blocks)


def apply(values, matrix, columns):
    data = list(values)
    for column in range(columns):
        shift = 4*column; mask = 15 << shift
        for base in range(len(data)):
            if base & mask:
                continue
            addresses = [base | (j << shift) for j in range(16)]
            result = g.matvec(matrix, [data[a] for a in addresses])
            for a, value in zip(addresses, result):
                data[a] = value
    return data


def plus(a, b, c):
    return [g.add(x, scale(y, c)) for x, y in zip(a, b)]


def word(reuse, frames):
    # Sources x0/x1, sinks y0/y1, retained dirty a/b, donor c, optional donor d.
    stock = 7 if reuse else 8
    current = ['A1', 'A7']+['I']*(stock-2)
    operations = []; histogram = Counter(); adapters = {}
    def move(role, destination):
        before = current[role]
        if before == destination:
            return
        key = before+'->'+destination
        if key not in adapters:
            matrix = g.matmul(frames[destination], g.adjoint(frames[before]))
            adapters[key] = (matrix, normal_form(matrix))
        operations.append(('move', role, key))
        histogram[adapters[key][1]['selected_rank_per_column']] += 1
        current[role] = destination
    def add(a, b, c, category='scalar'):
        if current[a] != current[b]:
            raise ValueError('A dirty scalar gate has unequal actual frames')
        operations.append(('add', a, b, Q(c), category))
    def cut(role, response, index):
        if any(c and current[2+j] != current[role] for j, c in enumerate(response)):
            raise ValueError('A birth response lacks its common actual frame')
        operations.append(('cut', role, tuple(response), index))
    cut(4, (1, 2), 0); cut(5, (1, 3), 1)
    move(4, 'A1'); add(4, 0, 1, 'source')
    move(5, 'A7'); add(5, 1, 1, 'source')
    for role in (2, 3, 4, 5):
        move(role, 'E')
    move(6, 'E'); cut(6, (1, 0), 2)
    add(6, 4, 1, 'workspace'); add(6, 5, 1, 'workspace'); add(2, 6, 1)
    second = 6 if reuse else 7
    move(second, 'E'); cut(second, (0, 1), 3)
    add(second, 4, 2, 'workspace'); add(second, 5, 3, 'workspace'); add(3, second, 1)
    move(2, 'K8'); move(3, 'K14')
    for role in list(range(2))+list(range(4, stock)):
        move(role, 'F')
    # The genuine reverse order uses original source-copy gates only after all
    # workspace gates have been undone, including the reused donor's history.
    add(second, 5, -3, 'undo-workspace'); add(second, 4, -2, 'undo-workspace')
    add(6, 5, -1, 'undo-workspace'); add(6, 4, -1, 'undo-workspace')
    add(5, 1, -1, 'undo-source'); add(4, 0, -1, 'undo-source')
    return dict(stock=stock, initial=['A1', 'A7']+['I']*(stock-2), final=current,
        operations=operations, histogram=dict(sorted(histogram.items())), adapters=adapters,
        reuse=reuse)


def replay(spec, initial, columns, negative=None):
    data = [list(row) for row in initial]; source_dependent_birth = False
    operations = list(spec['operations'])
    if negative == 'group negative sources before undo':
        first = next(i for i, op in enumerate(operations) if op[0] == 'add' and op[-1] == 'undo-workspace')
        ending = operations[first:]
        operations[first:] = [op for op in ending if op[-1] == 'undo-source']+[op for op in ending if op[-1] != 'undo-source']
    for op in operations:
        if op[0] == 'move':
            _, role, key = op; data[role] = apply(data[role], spec['adapters'][key][0], columns)
        elif op[0] == 'add':
            _, a, b, c, _ = op; data[a] = plus(data[a], data[b], c)
        else:
            _, role, response, index = op
            if spec['reuse'] and index == 3:
                source_dependent_birth = any(value != ZERO for value in data[role])
            if negative == 'omit reuse response' and index == 3:
                continue
            if negative == 'omit later birth cut' and spec['reuse'] and index == 2:
                response = (1, 1)
            for target, coefficient in enumerate(response):
                if coefficient:
                    data[2+target] = plus(data[2+target], data[role], Q(-coefficient))
    return data, source_dependent_birth


def expected(spec, initial, columns, frames):
    raw = [apply(row, g.adjoint(frames[frame]), columns)
           for row, frame in zip(initial, spec['initial'])]
    raw[2] = plus(plus(raw[2], raw[0], Q(1)), raw[1], Q(1))
    raw[3] = plus(plus(raw[3], raw[0], Q(2)), raw[1], Q(3))
    return [apply(row, frames[frame], columns) for row, frame in zip(raw, spec['final'])]


def case(payload):
    reuse, columns = payload; started = time.monotonic(); frames = literal_frames(); spec = word(reuse, frames)
    stock = spec['stock']; size = 1 << (4*columns); checked = 0; dependent = 0; digest = sha256()
    for bank in range(stock):
        for address in range(size) if columns == 1 else (0,):
            data = [[ZERO]*size for _ in range(stock)]; data[bank][address] = ONE
            result, birth = replay(spec, data, columns)
            if result != expected(spec, data, columns, frames):
                raise ValueError('Independent complete physical column failed')
            if bank < 2 and birth:
                dependent += 1
            digest.update(str(result).encode()); checked += 1
    for field in range(3):
        data = [[(Q((a*7+bank*11+field*3) % 31-15, 1 << (bank % 3)),
                  Q((a*13+bank*5+field*17) % 29-14, 1 << ((bank+field) % 4)))
                 for a in range(size)] for bank in range(stock)]
        result, _ = replay(spec, data, columns); wanted = expected(spec, data, columns, frames)
        if result != wanted:
            raise ValueError('Independent full Gaussian dirty field failed')
        digest.update(str(result).encode())
    controls = {}
    if reuse:
        for negative in ('omit reuse response', 'omit later birth cut', 'group negative sources before undo'):
            controls[negative] = replay(spec, data, columns, negative)[0] != wanted
        if not all(controls.values()) or not dependent:
            raise ValueError('A correlated dirty birth control did not discriminate')
    if all(wanted[bank] == data[bank] for bank in range(4, stock)):
        raise ValueError('Wrong raw identity scratch endpoint was not rejected')
    rank = sum(t*n for t, n in spec['histogram'].items())
    if spec['histogram'] != ({1: 6, 2: 6, 3: 2} if reuse else {1: 6, 2: 8, 3: 2}) or rank != 4*stock-4:
        raise ValueError('Independent complete child/stock ledger differs')
    return dict(status='INDEPENDENT LITERAL DEGENERATE BIRTH REVIEW PASS', reuse=reuse,
        columns=columns, selected_width=4, common_frame_subspace=[1, 6],
        common_frame_radical=[6], routing_columns=[1, 6, 2, 8],
        stock=stock, rank_per_column=rank, complete_child_histogram=spec['histogram'],
        unchanged_deficit=4, explicit_physical_columns=checked,
        full_physical_column_coverage=columns == 1, gaussian_dirty_fields=3,
        full_field_values=3*stock*size, source_dependent_reuse_birth_controls=dependent,
        arbitrary_virtual_dirty_restored=True, actual_dirty_endpoint='C_full times original dirty',
        negative_controls=controls, fourth_root_units_retained=True,
        relative_transition_coefficient_checks=256*len(spec['adapters']),
        independent_transition_normal_forms={key: value[1] for key, value in spec['adapters'].items()},
        output_sha256=digest.hexdigest(), seconds=time.monotonic()-started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--small', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(); config = json.loads(CONFIG.read_text())
    helper = Path(g.__file__).resolve()
    if sha256(helper.read_bytes()).hexdigest() != config['gaussian_arithmetic_sha256']:
        raise ValueError('Independent Gaussian helper changed')
    paths = [Path(__file__).resolve(), CONFIG, helper]
    hashes = {str(p.relative_to(TOPIC)): sha256(p.read_bytes()).hexdigest() for p in paths}
    cases = [(False, 1), (True, 1)] if args.small else [(False, 1), (True, 1), (False, 2), (True, 2)]
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        cases=cases, source_config_sha256=hashes, seed=None,
        no_external_producer_imports=True, scope=config['scope'],
        reviewed_producer=config['reviewed_producer'])
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    started = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(case, cases))
    if any(sha256((TOPIC/path).read_bytes()).hexdigest() != digest for path, digest in hashes.items()):
        raise ValueError('Source changed during immutable review attempt')
    summary = dict(status='INDEPENDENT LITERAL DEGENERATE BIRTH REVIEW PASS',
        cases=rows, seconds=time.monotonic()-started, scope=config['scope'],
        formal_or_native_proof=False, canonical_whole_primitive=False, new_exponent=False)
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({key: summary[key] for key in ['status', 'seconds', 'scope']}))


if __name__ == '__main__':
    main()
