#!/usr/bin/env python3
"""Exact category exhaustion of ORIGINAL rank-two frames at native h23/h25.

I+J and I-J/9 commute with coordinate permutations. Thus entrywise density
can be checked on one canonical representative of each nested frame family,
including diagonal/off-diagonal representatives of each membership class.
The closed formulas below follow independent orthogonal/Gram bases.
"""
import argparse
from collections import defaultdict
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path


def rank(frame, h):
    if frame is None:
        return 0
    if frame == 'identity':
        return h
    core, outside = frame
    return 1 if len(core) == 3 else len(outside)


def entry(frame, h, i, j):
    if frame is None:
        return F()
    if frame == 'identity':
        return F(i == j)
    core, outside = frame
    oi, oj, n = int(i in outside), int(j in outside), len(outside)
    if len(core) == 1:
        # H-orthonormal basis e_k+e_core/2. Transform its primal/dual
        # coordinates by L=I+J and L^-1=I-J/(h+1).
        wi = F(3,2)+F(i in core,2)
        zj = F(j in core,2)-F(5,3*(h+1))
        return n*wi*zj+wi*oj+oi*zj+F(i == j)*oi
    if len(core) == 2:
        # Triple basis e_core0+e_core1+e_k has Gram I+J_n,
        # whose inverse is I-J_n/(n+1).
        wi = F(3+int(i in core))
        zj = F(int(j in core))-F(10,3*(h+1))
        return (n*wi*zj+wi*oj+oi*zj+F(i == j)*oi
                -(n*wi+oi)*(n*zj+oj)/(n+1))
    assert len(core) == 3 and not outside
    return F(3+int(i in core))*(F(j in core,2)-F(5,3*(h+1)))


def cases(h):
    yield 'source_to_core1', ({0,1,2},set()), ({0},{1,2,3})
    yield 'source_to_core2', ({0,1,2},set()), ({0,1},{2,3,4})
    yield 'core1_complement', ({0},set(range(1,h-1))), 'identity'
    yield 'core2_complement', ({0,1},set(range(2,h))), 'identity'
    for c in (1,2):
        core = set(range(c))
        for n in range(h-c-1):
            outside = set(range(c,c+n))
            yield 'core%d_same_growth_n%d' % (c,n), (core,outside), (core,outside|{c+n,c+n+1})
    for n in range(1,h-2):
        old = set(range(2,n+2))
        yield 'core2_to_core1_n%d' % n, ({0,1},old), ({0},old|{1,n+2})


def membership(frame, i):
    if frame is None:
        return 'zero'
    if frame == 'identity':
        return 'identity'
    core, outside = frame
    return 'core' if i in core else 'outside' if i in outside else 'unused'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    assert __debug__, 'Run without Python -O'
    rows = []
    for h in (23,25):
        for name, a, b in cases(h):
            assert rank(b,h)-rank(a,h) == 2
            assert sum(entry(b,h,i,i)-entry(a,h,i,i) for i in range(h)) == 2
            groups = defaultdict(list)
            for i in range(h):
                groups[membership(a,i),membership(b,i)].append(i)
            reps = [i for members in groups.values() for i in members[:2]]
            zero_entries = [(i,j) for i in reps for j in reps
                            if entry(b,h,i,j)-entry(a,h,i,j) == 0]
            rows.append(dict(h=h,family=name,membership_classes=len(groups),
                             representative_entries=len(reps)**2,zero_entries=zero_entries))
    assert not any(row['zero_entries'] for row in rows)
    result = dict(status='exact_native_original_rank_two_family_density_pass',
                  cases=len(rows),representative_entries=sum(r['representative_entries'] for r in rows),
                  rows=rows,all_entrywise_nonzero=True,
                  checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='All original nested source/envelope rank-two differences at h23/h25, any coordinate permutation; does not address other dimensions/bases/enlarged positive frames',
                  conclusion='First rightmost pivot is column h-1; rank two admits no increasing consecutive two-pivot run')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','cases','representative_entries','conclusion')},indent=2))


if __name__ == '__main__':
    main()
