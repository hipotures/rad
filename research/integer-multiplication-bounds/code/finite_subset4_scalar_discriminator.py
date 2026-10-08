#!/usr/bin/env python3
"""Exact scalar obstruction and separate D-only counts for four-subset labels.

The rational geometry at intersection1 is valid, but the unchanged binary
side/point-center commutator does not compute an identity shear. No new
motif rank formula or multiplication saving is asserted.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import time

from downstream_complex_circuit import TripleSideCircuit,masks


def rank(rows):
    pivots={}
    for row in rows:
        while row:
            leading=row.bit_length()-1
            if leading in pivots:row^=pivots[leading]
            else:pivots[leading]=row;break
    return len(pivots)


def scalar_control(h,k):
    sets=list(combinations(range(h),k));indicators=[masks(t) for t in sets];v=len(sets)
    neighbors=[];point=[];third=[]
    for a in indicators:
        intersections=[(a&b).bit_count() for b in indicators]
        neighbors.append(sum((r==1)<<j for j,r in enumerate(intersections)))
        point.append(sum((r%2)<<j for j,r in enumerate(intersections)))
        third.append(sum((comb(r,3)%2 if r>=3 else 0)<<j for j,r in enumerate(intersections)))
    side_plus_centers=[a^b for a,b in zip(neighbors,point)]
    desired=[1<<i for i in range(v)]
    correction=[a^b for a,b in zip(neighbors,desired)]
    if k==3:
        assert correction==point and side_plus_centers==desired
    else:
        assert k==4 and neighbors==[a^b for a,b in zip(point,third)]
        assert side_plus_centers==third and side_plus_centers!=desired
        assert all(not(row>>i)&1 for i,row in enumerate(side_plus_centers))
        assert rank(correction)>=v-h-comb(h,3)
    return dict(h=h,k=k,v=v,rank_point_incidence_gram=rank(point),
        rank_required_identity_correction=rank(correction),
        rank_side_plus_point_center_operator=rank(side_plus_centers),
        actual_identity_shear=side_plus_centers==desired,
        binary_coefficients_checked=3*v*v,all_diagonal_coefficients=[(row>>i)&1 for i,row in enumerate(side_plus_centers)],
        exact_k4_identity='B_intersection1=A_1*A_1^T+A_3*A_3^T' if k==4 else 'B_intersection1+I=A_1*A_1^T')


class DisjointTripleOnly(TripleSideCircuit):
    """Scalar D recursion only; it does not invoke or claim binary frames."""
    def __init__(self,n):
        assert n>=6
        self.h=n;self.inputs=list(combinations(range(n),3));self.variables={t:i+1 for i,t in enumerate(self.inputs)}
        self.support=[0]+[1<<i for i in range(len(self.inputs))];self.args=[None]*len(self.support)
        self.union=[0]+[masks(t) for t in self.inputs];self.core=list(self.union)
        self.family=['zero']+['input']*len(self.inputs);self.lookup={(None,s):i for i,s in enumerate(self.support)}
        self.special={};self.namespace='D'
        table=self.hyper(list(range(n)),dict(self.variables),3)
        self.outputs={('D',t):table[t] for t in self.inputs};self.active=set();stack=list(self.outputs.values())
        while stack:
            node=stack.pop()
            if not node or node in self.active:continue
            self.active.add(node)
            if self.args[node]:stack.extend(self.args[node])
        self.additions=sum(self.args[node] is not None for node in self.active)


def counts(h):
    circuit=DisjointTripleOnly(h-1);checked=circuit.verify();v=comb(h,4)
    assert len(circuit.inputs)==comb(h-1,3)
    upper=h*(circuit.additions+len(circuit.outputs));rmin=max(0,v-h-comb(h,3))
    return dict(h=h,k=4,v=v,local_n=h-1,local_disjoint3_map=checked,
        unshared_common_point_roles_upper_bound=upper,
        generic_global_CSE_warning='Core/union alone no longer identifies a shared four-subset support; exact pair-support or complete formal support is needed',
        scalar_correction_rank_lower_bound=rmin,proposed_point_centers=h,
        unchanged_scalar_identity_shear_impossible=rmin>h,
        ambient_rational_H_nondegenerate=h!=16,
        scope='Exact D-only scalar counts, not a full four-subset motif or supported saving')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--count-h',type=int,nargs='+',default=[17,20,22,26,28]);args=ap.parse_args();assert not args.output.exists()
    begin=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    rows=[scalar_control(h,k) for h in range(6,11) for k in (3,4)]
    numbers=[counts(h) for h in args.count_h]
    value=dict(status='Terminal exact scalar obstruction and separate D-only count PASS',
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        imported_D_recursion_sha256=sha256(Path(__file__).with_name('downstream_complex_circuit.py').read_bytes()).hexdigest(),
        started_utc=started,completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-begin,
        controls=rows,count_screens=numbers,
        conclusion='Unchanged point-center identity shear fails for four-subset labels; low raw role counts do not transfer the triple bit motif',
        scope='Exact F2 scalar interface, independently distinct from rational nondegenerate-frame geometry')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status=value['status'],seconds=value['elapsed_seconds'],counts=numbers)),flush=True)


if __name__=='__main__':main()
