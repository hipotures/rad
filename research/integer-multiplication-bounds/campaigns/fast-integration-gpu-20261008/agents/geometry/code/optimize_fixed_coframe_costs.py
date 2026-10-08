#!/usr/bin/env python3
"""Numerical mixed-integer discovery on exact physical old/minimum costs.

No mathematical global-optimum or exponent claim follows from this solver.
Every selected allocation must be independently rebuilt and certified.
"""
import argparse
from collections import defaultdict
from decimal import Decimal, localcontext
from hashlib import sha256
import json
from pathlib import Path
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--solver-package', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--a', default='0.00005140365546')
    parser.add_argument('--seconds', type=float, default=240)
    args = parser.parse_args()
    assert not args.output.exists() and not args.work.exists()
    args.work.mkdir(parents=True)
    sys.path.insert(0, str(args.solver_package))
    import highspy
    started = time.monotonic()
    raw = args.input.read_bytes()
    table = json.loads(raw)
    variables = table['variables']
    index = {node: i for i, node in enumerate(variables)}
    successors = defaultdict(set)
    for a, b in table['implications']:
        successors[a].add(b)
    frames = table['probe_frame_descriptors']
    states = table['variable_states']
    with localcontext() as context:
        context.prec = 100
        exponent = Decimal(args.a)
        weights = {t: Decimal(t) * ((exponent * (Decimal(575) / t).ln()).exp()-1)
                   for t in range(1, table['h']+1)}
        unary = [Decimal(0) for _ in variables]
        constant = Decimal(0)
        quadratic = defaultdict(Decimal)
        for frame, count in table['side_counts'].items():
            frame = int(frame)
            rank0 = frames[states[frame][0]][0]
            rank1 = frames[states[frame][1]][0]
            constant += (table['h']-rank0) * count * weights[1]
            if frame in index:
                unary[index[frame]] += (rank0-rank1) * count * weights[1]
        for row in table['rows']:
            a, b = row['a'], row['b']
            values = {s: Decimal(v['screen_cost']) for s, v in row['states'].items()
                      if v['legal']}
            constant += values['00']
            if a in index and b in index:
                if '10' not in values:
                    values['10'] = values['11']-values['01']+values['00']
                unary[index[a]] += values['10']-values['00']
                unary[index[b]] += values['01']-values['00']
                q = values['11']-values['10']-values['01']+values['00']
                if abs(q) < Decimal('1e-65'):
                    q = Decimal(0)
                assert q >= 0, 'This discovery linearization expects nonnegative couplings'
                if q:
                    quadratic[tuple(sorted((a, b)))] += q
            elif a in index:
                unary[index[a]] += values['10']-values['00']
            elif b in index:
                unary[index[b]] += values['01']-values['00']

        reachable = {}
        def reaches(a, b):
            if a not in reachable:
                seen, stack = set(), list(successors[a])
                while stack:
                    node = stack.pop()
                    if node not in seen:
                        seen.add(node)
                        stack.extend(successors[node]-seen)
                reachable[a] = seen
            return b in reachable[a]

        folded = 0
        remaining = {}
        for (a, b), q in quadratic.items():
            if reaches(a, b):
                unary[index[a]] += q
                folded += 1
            elif reaches(b, a):
                unary[index[b]] += q
                folded += 1
            else:
                remaining[a, b] = q
        quadratic = remaining
        expected = []
        for histogram in table['uniform_histograms_exactly_reconstructed']:
            expected.append(sum(n*weights[t] for t, n in enumerate(histogram) if t and n))
        assert abs(constant-expected[0]) < Decimal('1e-60')
        assert abs(constant+sum(unary)+sum(quadratic.values())-expected[1]) < Decimal('1e-60')
        constant_float = float(constant)
        unary_float = [float(u) for u in unary]
        quadratic_float = {(a, b): float(q) for (a, b), q in quadratic.items()}
    print(json.dumps(dict(phase='numerical integer allocation', variables=len(variables),
        implications=sum(map(len, successors.values())), couplings=len(quadratic),
        transitive_couplings_folded=folded, uniform_moments=list(map(str, expected)))), flush=True)

    solver = highspy.Highs()
    solver.setOptionValue('threads', 1)
    solver.setOptionValue('parallel', 'off')
    solver.setOptionValue('time_limit', args.seconds)
    solver.setOptionValue('mip_rel_gap', 0)
    solver.setOptionValue('mip_abs_gap', 1e-7)
    solver.setOptionValue('log_file', str(args.work/'highs.log'))
    scale = 1e9
    x = {node: solver.addVariable(lb=0, ub=1, obj=unary_float[index[node]]*scale,
            type=highspy.HighsVarType.kInteger) for node in variables}
    for a, targets in successors.items():
        for b in targets:
            solver.addConstr(x[a] <= x[b])
    for (a, b), q in quadratic_float.items():
        z = solver.addVariable(lb=0, ub=1, obj=q*scale)
        solver.addConstr(z >= x[a]+x[b]-1)
    solver.run()
    solution = solver.getSolution()
    assert solution.value_valid
    selected = {node: int(solution.col_value[index[node]] >= .5) for node in variables}
    assert all(selected[a] <= selected[b] for a, targets in successors.items() for b in targets)
    score = constant_float + sum(unary_float[index[n]]*selected[n] for n in variables)
    score += sum(q*selected[a]*selected[b] for (a, b), q in quadratic_float.items())
    exact_histogram = defaultdict(int)
    for frame, count in table['side_counts'].items():
        frame = int(frame)
        state = selected.get(frame, 0)
        exact_histogram[1] += (table['h']-frames[states[frame][state]][0])*count
    for row in table['rows']:
        key = f"{selected.get(row['a'],0)}{selected.get(row['b'],0)}"
        entry = row['states'][key]
        assert entry['legal']
        for width, count in entry['histogram'].items():
            exact_histogram[int(width)] += count*row['count']
    assert sum(t*n for t,n in exact_histogram.items()) == table['physical_rank_mass']
    histogram = [exact_histogram[t] for t in range(table['h']+1)]
    check = sum(n*t*__import__('math').expm1(float(args.a)*__import__('math').log(575/t))
                for t,n in enumerate(histogram) if t and n)
    assert abs(check-score) < 2e-10
    allocation = dict(classification='DISCOVERY; REQUIRES ACTUAL WORD CERTIFICATION',
        h=table['h'], basis=table['basis'], a=args.a,
        parent_word_sha256=table['parent_word_sha256'],
        input_cost_table_sha256=sha256(raw).hexdigest(),
        minimum_frame_ids=[node-2 for node in variables if not selected[node]],
        exact_predicted_child_histogram=histogram,
        physical_R=table['physical_R'], physical_rank_mass=table['physical_rank_mass'])
    allocation_path = args.work/'selected-allocation.json'
    allocation_path.write_text(json.dumps(allocation, indent=2)+'\n')
    info = solver.getInfo()
    args.output.write_text(json.dumps(dict(status='NUMERICAL INTEGER ALLOCATION DISCOVERY',
        h=table['h'], basis=table['basis'], variables=len(variables),
        hard_implications=sum(map(len, successors.values())),
        positive_couplings_after_transitive_reduction=len(quadratic),
        positive_couplings_folded=folded, screen_Phi=check,
        uniform_minimum_Phi=float(expected[0]), uniform_old_Phi=float(expected[1]),
        solver_status=str(solver.getModelStatus()), solver_version=solver.version(),
        numerical_gap=info.mip_gap, numerical_dual_bound=info.mip_dual_bound,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_sha256=sha256(raw).hexdigest(), allocation_path=str(allocation_path),
        allocation_sha256=sha256(allocation_path.read_bytes()).hexdigest(),
        elapsed_seconds=time.monotonic()-started,
        scope='Exact matrix histograms and legal implication closure; numerical '
              'MILP discovery only. No mathematical global-optimum certificate and '
              'no accepted physical network until independent actual-word replay.'), indent=2)+'\n')
    print(json.dumps(dict(status='complete', Phi=check,
        removed_frames=len(allocation['minimum_frame_ids']))), flush=True)


if __name__ == '__main__':
    main()
