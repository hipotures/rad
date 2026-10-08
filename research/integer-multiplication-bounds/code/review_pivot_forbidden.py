#!/usr/bin/env python3
"""Independent exact joined-kernel holes and contiguous-run bound controls.

This supplements a completed batching audit without changing its bytes.
Sparse rows are built from the rational metric I-J/9 and tensor projectors;
direct rational elimination independently determines the small profiles.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import resource
import time

from review_pivot_batching import diagonal_runs, sparse_profile


def joined(h, first, second, matched):
    t = lambda triple: [Q(int(i in triple)) for i in range(h)]
    projectors = []
    for triple in (first, second, matched):
        u = t(triple)
        dual = [sum(u[i]*(Q(int(i == j))-Q(1, 9)) for i in range(h))/2 for j in range(h)]
        assert sum(a*b for a, b in zip(u, dual)) == 1
        projectors.append([[a*b for b in dual] for a in u])
    Pa, Pb, Pc = projectors
    n = h**3
    rows = []
    for a in range(h):
        for b in range(h):
            for c in range(h):
                rows.append([Q(int(a == i and b == j and c == k))-
                    (Pa[b][j]*Pb[c][k] if a == i else 0)-
                    (Pb[a][i]*Pc[b][j] if c == k else 0)
                    for i in range(h) for j in range(h) for k in range(h)])
    assert len(rows) == n
    return rows


def case(h, first, second, matched):
    assert len(set(first) & set(matched)) == 1
    A = joined(h, first, second, matched)
    block = h*h
    offset = h*min(first)+min(second)
    holes = [i*block+offset for i in range(h)]
    support_sets = [[(i*h+j)*h+k for j in first for k in second] for i in range(h)]
    for support in support_sets:
        assert all(sum(row[j] for j in support) == 0 for row in A)
    profile = sparse_profile(A)
    assert len(profile) == h**3-2*h
    assert not set(holes) & {j for _, j in profile}
    runs = []
    for row, column in profile:
        if runs and runs[-1][0]+runs[-1][2] == row and runs[-1][1]+runs[-1][2] == column:
            a, b, length = runs[-1]
            runs[-1] = a, b, length+1
        else:
            runs.append((row, column, 1))
    assert max(length for _, _, length in runs) <= block-1
    diag = diagonal_runs(profile, h**3-1)
    assert sum(diag) >= h**3-4*h and len(diag) <= 4*h+1
    return dict(h=h, first=first, second=second, matched=matched,
        exact_rank=len(profile), exact_kernel_relations=h, forbidden_columns=holes,
        all_forbidden_columns_absent=True, maximum_any_increasing_run=max(r for _, _, r in runs),
        maximum_diagonal_run=max(diag), guaranteed_maximum_run=block-1,
        diagonal_pivots=sum(diag), diagonal_runs=len(diag),
        profile_sha256=sha256(json.dumps(profile,separators=(',', ':')).encode()).hexdigest())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--batch-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    assert not args.output.exists()
    started=time.monotonic()
    data=json.loads(args.batch_review.read_text())
    assert data['status'].startswith('PASS independent pivot batching')
    rows=[case(h,first,second,matched) for h,first,second,matched in
        ((6,(0,1,2),(3,4,5),(2,3,4)),
         (8,(0,1,2),(5,6,7),(2,3,4)),
         (8,(3,6,7),(0,2,6),(0,1,3)))]
    # Binary even-intersection partner matching cannot be silently used
    # for the rational joined projector: its middle orthogonality fails.
    wrong=joined(6,(0,1,2),(3,4,5),(3,4,5))
    support=[j*6+k for j in (0,1,2) for k in (3,4,5)]
    negative=next((i,sum(row[j] for j in support)) for i,row in enumerate(wrong)
                  if sum(row[j] for j in support))
    assert negative[1]
    h=data['rows'][1]['h'];m=h**3
    selected=data['rows'][1]
    assert selected['joined_length_cap'] is None and selected['joined_run_bound']==4*h+1
    result=dict(status='PASS independent joined forbidden-column transfer',
        generated_at=datetime.now(timezone.utc).isoformat(),
        batch_review_sha256=sha256(args.batch_review.read_bytes()).hexdigest(),
        source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                      for name in ('review_pivot_forbidden.py','review_pivot_batching.py')},
        cases=rows, excluded_nonorthogonal_matching=dict(row=negative[0],nonzero_kernel_residual=str(negative[1])),
        promoted_uncapped_primitive_saving=selected['chosen_bit_saving'],
        unchanged_moment_run_bound=4*h+1, strengthened_maximum_run=h*h-1,
        uniform_child_shrink='r*floor(e/m) < e/h', row_depth_bound='ceil(log_h(e))',
        active_campaign_deadline='2026-10-08T10:00:00Z',
        wall_seconds=time.monotonic()-started,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        scope='Kernel column relations and suffix-rank invariance give the all-size proof; small matrices independently falsify its hypotheses')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],selected['chosen_bit_saving'],'maxrun',h*h-1,flush=True)


if __name__=='__main__':main()
