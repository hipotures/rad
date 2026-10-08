#!/usr/bin/env python3
"""Faithful p=q=2 endpoint packing from Sergeev arXiv1209.1645v1.

This implements the September 2012 primary precursor, not the unacquired
2014 IPL construction. All additions have disjoint formal supports. Local
and global CSE, positive envelopes and actual retained-controller roles are
measured separately from the paper's addition-count upper bound.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

from finite_block_search import GroupUnion,install_reference
from finite_clone_batch import build,dirty_controls
from finite_clone_gate_screen import compile_checked


def make_endpoint_class():
    from exclusion_circuit import ExclusionCircuit
    class EndpointCircuit(ExclusionCircuit):
        def pair(self,points):
            edges={tuple(sorted(pair)):self.variables[tuple(sorted(pair))] for pair in combinations(points,2)}
            return 0,{},self.endpoint(points,edges)

        def endpoint(self,points,edges):
            def e(a,b):return edges[tuple(sorted((a,b)))]
            if len(points)==4:
                return {tuple(sorted(pair)):e(*[x for x in points if x not in pair]) for pair in combinations(points,2)}
            assert len(points)>4
            first,second,last=points[0],points[1],points[-1]
            middle=points[1:-1]
            packed={tuple(sorted((a,b))):e(a,b) for a,b in combinations(points[:-1],2)}
            for other in middle:
                packed[tuple(sorted((first,other)))]=(self.total([e(first,second),e(first,last),e(second,last)])
                    if other==second else self.add(e(first,other),e(last,other)))
            old=self.endpoint(points[:-1],packed)
            out={}
            for a,b in combinations(middle,2):
                value=old[tuple(sorted((a,b)))]
                if second in (a,b):value=self.add(value,e(first,last))
                out[tuple(sorted((a,b)))]=value
            # Step2 uses two B_1,1 rows, i.e. exact leave-one sums.
            _,last_rows,_=self.vector([e(last,x) for x in middle],False)
            _,first_rows,_=self.vector([e(first,x) for x in middle],False)
            for index,other in enumerate(middle):
                value=old[tuple(sorted((first,other)))]
                out[tuple(sorted((first,other)))]=self.add(value,last_rows[index])
                out[tuple(sorted((last,other)))]=self.add(value,first_rows[index])
            # Step3 reuses the old {first,second} query and adds the row2 sum.
            repair=self.total([e(second,x) for x in middle if x!=second])
            out[tuple(sorted((first,last)))]=self.add(old[tuple(sorted((first,second)))],repair)
            assert len(out)==len(points)*(len(points)-1)//2
            return out
    return EndpointCircuit


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference',required=True);ap.add_argument('--h',nargs='+',type=int,default=[8,12,20])
    ap.add_argument('--local-n',nargs='+',type=int,default=[4,5,6,7,10,20,49])
    ap.add_argument('--dirty-ground',type=int);ap.add_argument('--primary-pdf',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();install_reference(args.reference)
    cls=make_endpoint_class();at=time.monotonic();value=dict(status='Running',rows=[],local=[],
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),started_utc=datetime.now(timezone.utc).isoformat(),
        primary_source=dict(title='On additive complexity of a sequence of matrices',author='Igor S. Sergeev',
            arxiv='https://arxiv.org/abs/1209.1645',version='v1,2012-09-07',construction='Section2 p=q=2 endpoint packing',
            distinction='This is not an implementation of the 2014 IPL paper'),
        scientific_scope='Exact cancellation-free scalar maps and unchanged positive-envelope/retained-role compiler; no downstream bound claimed')
    if args.primary_pdf:value['primary_source']['pdf_sha256']=sha256(args.primary_pdf.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for n in args.local_n:
        circuit=cls(n);checked=circuit.verify()
        upper=sum(11*k-35 for k in range(5,n+1))
        assert circuit.additions<=upper
        value['local'].append(dict(n=n,exact=checked,recurrence_addition_upper=upper))
    for h in args.h:
        started=time.monotonic();positions=[0]*(h//2-1)+[h//2-2]*(h//2+1)
        baseline=build(h,2,positions);base,_,_=compile_checked(baseline)
        row=dict(h=h,paired_base2_positions=positions,paired=base,endpoint=[])
        for ordering in ('natural','paired'):
            circuit=GroupUnion(h,cls,ordering);checked,frames,code=compile_checked(circuit)
            case=dict(ordering=ordering,checked=checked,role_difference=checked['roles']-base['roles'])
            if h==args.dirty_ground:case['complete_dirty_controls']=dirty_controls(circuit,frames,code,False)
            row['endpoint'].append(case)
        row['elapsed_seconds']=time.monotonic()-started;value['rows'].append(row)
        args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(h=h,paired=base['roles'],endpoint=[x['checked']['roles'] for x in row['endpoint']],seconds=row['elapsed_seconds'])),flush=True)
    value.update(status='Terminal exact Sergeev2012 endpoint discriminator PASS',completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-at)
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
