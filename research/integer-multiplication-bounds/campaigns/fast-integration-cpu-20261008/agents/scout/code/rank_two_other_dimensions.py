#!/usr/bin/env python3
"""Exact non-native controls preventing overbroad rank-two exclusion claims."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
from rank_two_native_family import entry


def pivots(matrix):
    a = [row[:] for row in matrix]
    h, result = len(a), []
    for i in range(h):
        cols = [j for j in range(h) if a[i][j]]
        if not cols:
            continue
        j = max(cols)
        result.append([i,j])
        for k in range(i+1,h):
            if a[k][j]:
                q = a[k][j]/a[i][j]
                for col in range(j+1):
                    a[k][col] -= q*a[i][col]
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    rows = []
    for h,n,forced in ((11,7,{2:0,0:1,9:9,3:10}),
                       (19,11,{13:0,2:1,0:17,3:18})):
        mapping = dict(forced)
        targets = iter(i for i in range(h) if i not in mapping.values())
        for i in range(h):
            if i not in mapping:
                mapping[i] = next(targets)
        inverse = {j:i for i,j in mapping.items()}
        old = set(range(2,n+2))
        first,second = ({0,1},old),({0},old|{1,n+2})
        matrix = [[entry(second,h,inverse[i],inverse[j])-entry(first,h,inverse[i],inverse[j])
                   for j in range(h)] for i in range(h)]
        actual = pivots(matrix)
        assert actual == [[0,h-2],[1,h-1]]
        assert sum(matrix[i][i] for i in range(h)) == 2
        rows.append(dict(h=h,old_outside_count=n,coordinate_permutation=mapping,
                         pivots=actual,blocks=[2],
                         matrix=[[str(x) for x in row] for row in matrix]))
    result = dict(status='exact_non_native_rank_two_run_controls_pass',rows=rows,
                  checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  frame_helper_sha256=hashlib.sha256(Path(__file__).with_name('rank_two_native_family.py').read_bytes()).hexdigest(),
                  scope='Explicit original frame increments at h11/h19, without a full producer, physical data geometry or multiplication-saving claim')
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],cases=[{'h':r['h'],'pivots':r['pivots']} for r in rows]),indent=2))


if __name__ == '__main__':
    main()
