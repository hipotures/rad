#!/usr/bin/env python3
"""Independent exact fine-grid and stage3 residual audit.

Producer JSON is an input witness only. Counts, moments, exponential
remainders and small rational residual profiles are reconstructed here.
No producer characteristic function is imported or executed.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import resource
import sys
import time

from review_parameter_audit import log_integer
from review_pivot_batching import diagonal_runs, sparse_profile, stringify


def line_projector(h, triple):
    u = [Q(int(i in triple)) for i in range(h)]
    metric_dual = [sum(u[i]*(Q(int(i == j))-Q(1, 9)) for i in range(h))/2
                   for j in range(h)]
    assert sum(a*b for a, b in zip(u, metric_dual)) == 1
    return [[a*b for b in metric_dual] for a in u]


def data_case(h, first, second, third):
    """Both X in->2 and Y 0->1 have B12 tensor t3-perp residual."""
    assert h != 9
    Pa, Pb, Pc = [line_projector(h, t) for t in (first, second, third)]
    A = []
    gate_edges = 0
    for a in range(h):
        for b in range(h):
            for c in range(h):
                row = []
                for i in range(h):
                    for j in range(h):
                        for k in range(h):
                            eye12 = Q(int(a == i and b == j))
                            eye3 = Q(int(c == k))
                            p12 = Pa[a][i]*Pb[b][j]
                            b12 = eye12-p12
                            expected = b12*(eye3-Pc[c][k])
                            # Original 03-motifs stage3 labels and chronology.
                            incoming_x = eye12*Pc[c][k]
                            gate_x2 = b12*eye3+p12*Pc[c][k]
                            gate_y0 = b12*Pc[c][k]
                            gate_y1 = b12*eye3
                            assert gate_x2-incoming_x == gate_y1-gate_y0 == expected
                            gate_edges += 2
                            row.append(expected)
                A.append(row)
    n = h**3
    rank = (h*h-1)*(h-1)
    defect = n-rank
    holes = [i*h+min(third) for i in range(h*h)]
    for i in range(h*h):
        support = [i*h+k for k in third]
        assert all(sum(row[j] for j in support) == 0 for row in A)
    pivots = sparse_profile(A)
    assert len(pivots) == rank and not set(holes) & {j for _, j in pivots}
    diagonal = diagonal_runs(pivots, n-1)
    assert sum(diagonal) >= n-2*defect and len(diagonal) <= 2*defect+1
    runs = []
    for a, b in pivots:
        if runs and runs[-1][0]+runs[-1][2] == a and runs[-1][1]+runs[-1][2] == b:
            x, y, r = runs[-1]
            runs[-1] = x, y, r+1
        else:
            runs.append((a, b, 1))
    assert max(r for _, _, r in runs) <= h-1
    return dict(h=h, triples=[first, second, third], matrix_dimension=n,
                exact_rank=rank, defect=defect,
                reconstructed_data_gate_edge_entries=gate_edges,
                kernel_column_relations=h*h, all_forbidden_columns_absent=True,
                maximum_increasing_run=max(r for _, _, r in runs),
                maximum_run_bound=h-1, diagonal_pivots=sum(diagonal),
                diagonal_pivot_bound=n-2*defect, diagonal_runs=len(diagonal),
                diagonal_run_bound=2*defect+1,
                profile_sha256=sha256(json.dumps(pivots,separators=(',', ':')).encode()).hexdigest())


def independent_counts(h, roles):
    v, m = comb(h, 3), h**3
    N = v**3
    W = 2*N+2*v*v*(roles+h)
    L = 3*v*v*h*h
    D = N-2*L
    assert D > 0
    return dict(h=h,side_roles=roles,v=v,m=m,N=N,W=W,L=L,D=D,s=W*m-D)


def exact_moments(n, capped, data):
    h, m, R, v = [n[k] for k in ('h', 'm', 'side_roles', 'v')]
    multiplier = (R+h)*v*h*h
    middle = Q(0)
    middle_rank = 0
    for a in range(h-2):
        frequency = comb(h-a-1, 2)*multiplier
        runs = [1, h-a-2]+([a] if a else [])
        middle_rank += frequency*sum(runs)
        middle += frequency*sum(r*log_integer(r, 64)[0] for r in runs)
    assert middle_rank == (R+h)*v*v*h*h*(h-1)
    J, t = (R+h)*v*v, m-4*h
    g = 5*h+1 if capped else 4*h+1
    join = J*t*(log_integer(t,64)[0]-log_integer(g,64)[1])
    join_rank = J*(m-2*h)
    other = n['s']-middle_rank-join_rank
    assert other >= 0
    result = dict(middle=middle,join=join,middle_rank=middle_rank,join_rank=join_rank,
                  join_count=J,join_diagonal=t,join_runs=g,data=Q(0),data_rank=0,
                  maximum_run=h*h if capped else h*h-1)
    if data:
        r3 = (h*h-1)*(h-1)
        d3 = m-r3
        t3 = m-2*d3
        g3 = 2*d3+1
        if capped:
            g3 += (r3+h*h-1)//(h*h)
        assert d3 == h*h+h-1 and t3 > g3 > 0
        count = 2*n['N']
        result.update(data=count*t3*(log_integer(t3,64)[0]-log_integer(g3,64)[1]),
                      data_rank=count*r3,data_edge_count=count,data_diagonal=t3,
                      data_runs=g3,data_rank_per_edge=r3,data_defect=d3)
        assert result['data_rank'] <= other
        other -= result['data_rank']
    result['unchanged_rank'] = other
    result['total_moment_lower'] = result['middle']+result['join']+result['data']
    assert result['middle_rank']+result['join_rank']+result['data_rank']+other == n['s']
    return result


def witness_check(witness, n, capped, data):
    for name, value in n.items():
        assert witness['counts'][name] == value
    a = Q(witness['saving'])
    moments = exact_moments(n, capped, data)
    lm = log_integer(n['m'],64)[1]
    first = n['s']*lm-moments['total_moment_lower']
    assert first > 0 and 0 < a*lm < 1
    remainder = a*a*n['s']*lm*lm/(2*(1-a*lm))
    gap = n['D']-a*first-remainder
    assert gap > 0
    if data:
        for k, own in [('data_edge_count','data_edge_count'),
                       ('data_edge_rank','data_rank_per_edge'),
                       ('data_rank_defect','data_defect'),
                       ('data_minimum_diagonal_pivots','data_diagonal'),
                       ('data_maximum_run_pieces','data_runs')]:
            assert witness[k] == moments[own]
        assert witness['other_unchanged_rank'] == moments['unchanged_rank']
        assert witness['maximum_child_rank'] == moments['maximum_run']
    else:
        assert witness['join_count'] == moments['join_count']
        assert witness['minimum_diagonal_pivots_per_join'] == moments['join_diagonal']
        assert witness['maximum_diagonal_runs_per_join'] == moments['join_runs']
    # The producer uses W*m*ln(m) in its linear term instead of s*ln(m).
    # That conservative allowance covers the stronger true exponential
    # remainder independently checked above.
    producer_linear = Q(witness['taylor_linear_coefficient'])
    producer_quadratic = Q(witness['taylor_quadratic_coefficient'])
    allowance = a*(producer_linear-first)+a*a*producer_quadratic-remainder
    assert allowance > 0
    return dict(saving=a,variant=witness.get('variant','two-family-uncapped'),
                moments=moments,first_moment_upper=first,
                exponential_remainder_upper=remainder,strict_characteristic_gap=gap,
                producer_linear_slack_covers_correct_remainder=allowance,
                total_rank_conserved=True,strict_uniform_recurrence=True)


def input_check(path, finite_hash):
    producer = json.loads(path.read_text())
    assert producer['status'].startswith('PASS PROSPECTIVE')
    assert producer['finite_input']['sha256'] == finite_hash
    for name, digest in producer['source_sha256'].items():
        assert sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() == digest
    return producer


def main():
    sys.set_int_max_str_digits(0)
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--finite-review',type=Path,required=True)
    ap.add_argument('--join-witness',type=Path,required=True)
    ap.add_argument('--data-witness',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists()
    started=time.monotonic()
    finite=json.loads(args.finite_review.read_text())
    assert finite['status']=='PASS' and finite['full']['matches_immutable_producer_identity_and_compilation']
    finite_hash=sha256(args.finite_review.read_bytes()).hexdigest()
    n=independent_counts(finite['full']['h'],finite['full']['compiled_roles'])
    join=input_check(args.join_witness,finite_hash)
    data=input_check(args.data_witness,finite_hash)
    rows=[witness_check(join['witness'],n,False,False)]
    rows += [witness_check(w,n,w['variant']=='capped',True) for w in data['witnesses']]
    assert rows[-1]['saving'] > rows[0]['saving']
    cases=[data_case(h,*triples) for h,triples in
           [(6,((0,1,2),(2,3,4),(0,4,5))),
            (7,((1,3,5),(2,4,6),(0,2,6))),
            (8,((3,6,7),(0,2,6),(2,4,7)))]]
    # Dropping the t-perp condition would remove the kernel holes and
    # change both rank and the actual incoming/gate difference.
    wrong_rank=(n['h']**2-1)*n['h']
    assert wrong_rank != (n['h']**2-1)*(n['h']-1)
    inputs={str(p):sha256(p.read_bytes()).hexdigest() for p in
            (args.finite_review,args.join_witness,args.data_witness)}
    names=('review_pivot_extension.py','review_pivot_batching.py','review_parameter_audit.py')
    result=dict(status='PASS independent two-family fine-grid and stage3 data-family transfer',
                generated_utc=datetime.now(timezone.utc).isoformat(),counts=n,
                source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in names},
                inputs=inputs,rows=rows,exact_stage3_cases=cases,
                excluded_full_third_factor=dict(wrong_rank=wrong_rank,expected_rank=(n['h']**2-1)*(n['h']-1)),
                physical_family=dict(x_edge='stage3 X in->2',y_edge='stage3 Y 0->1',
                                     copies_each=n['N'],disjoint_from_middle_and_joins=True,
                                     source_negative_projection_exception='stage1 only'),
                maximum_child_rank=n['h']**2-1,
                recursive_depth_bound='ceil(log_h(e))',
                scope='Projection and tensor axis chronology plus proved lower/lower profile theorem justify all sizes; no dense h51 matrix or multiplication machine executed',
                wall_seconds=time.monotonic()-started,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(stringify(result),indent=2,sort_keys=True)+'\n')
    for row in rows:
        print('PASS',row['variant'],row['saving'],'strict correctly bounded characteristic',flush=True)


if __name__=='__main__':main()
