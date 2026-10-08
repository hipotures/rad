#!/usr/bin/env python3
"""Exact rational control for a genuine new-basis prescribed-prefix failure."""
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse,json


def run(left,right):
    a,b,d = 23,25,47
    rows = list(range(a))+[a-1]+list(range(a))
    cols = list(range(a))+[0]+list(range(a))
    x = [Q(a-1,a+3) if i in left else Q(-2,a+3) for i in range(a)]
    y = [Q(b-1,b+3) if i in right else Q(-2,b+3) for i in range(b)]
    matrix = [[Q(rows[i]==cols[j])/x[rows[i]]+Q(i%b==(528+j)%b)/y[i%b]-1 for j in range(d)] for i in range(d)]
    available = set(range(d))
    pivots = []
    prescribed_failure = None
    for i in range(d):
        if i == 27:
            prescribed_failure = dict(row=i,column=19,rational_value=str(matrix[i][19]))
        candidates = [j for j in available if matrix[i][j]]
        if not candidates:
            continue
        j = max(candidates)
        value = matrix[i][j]
        pivots.append(dict(row=i,column=j,value=str(value)))
        available.remove(j)
        for r in range(i+1,d):
            if matrix[r][j]:
                factor = matrix[r][j]/value
                for c in available:
                    matrix[r][c] -= factor*matrix[i][c]
                matrix[r][j] = Q(0)
    runs = []
    length = 0
    for i,pivot in enumerate(pivots):
        if i and pivot['row']==pivots[i-1]['row']+1 and pivot['column']==pivots[i-1]['column']+1:
            length += 1
        else:
            if length:runs.append(length)
            length = 1
    if length:runs.append(length)
    assert len(pivots)==47 and sum(runs)==47
    assert prescribed_failure['rational_value']=='0'
    return dict(status='EXACT GENUINE PRESCRIBED-PREFIX ZERO; ACTUAL FULL RANK RETAINED',
                left=left,right=right,prescribed_failure=prescribed_failure,actual_pivots=pivots,
                null_corner_runs=runs,data_recursive_widths=runs+[481],
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                completed_utc=datetime.now(timezone.utc).isoformat(),
                scope='One exact changed-basis pair; other actual pairs require complete classification')


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    result=run([0,1,22],[0,1,22])
    assert not args.output.exists()
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','prescribed_failure','null_corner_runs')}))
