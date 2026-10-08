#!/usr/bin/env python3
"""Recover the two original-DAG weighted matching witnesses from pinned source.

The producer variation is the selected grouping/association from the authored
changed_dag_seed wrapper. Upstream source remains an eligible pinned Apache-2.0
dependency, with its original author notices. Canonical donor/exact-use streams
are preserved separately from the deterministic search traversal order.
"""
import argparse
import hashlib
import heapq
import json
from pathlib import Path
import struct
import subprocess
import sys

from changed_dag_seed import retain_total
from weighted_native_worker import occurrence_check
from check_changed_fixed_dag import parse_dag


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_pairs(path):
    data=path.read_bytes()
    n,count=struct.unpack_from('<2I',data)
    assert len(data)==8+8*count
    values=struct.unpack_from('<%dI'%(2*count),data,8)
    pairs=sorted(zip(values[::2],values[1::2]))
    canonical=struct.pack('<2I',n,count)+b''.join(struct.pack('<2I',*p) for p in pairs)
    return n,pairs,hashlib.sha256(canonical).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root',required=True,type=Path)
    ap.add_argument('--profiler',required=True,type=Path)
    ap.add_argument('--witness',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--axis',nargs='+',type=int,choices=[0,1],default=[0,1])
    ap.add_argument('--dag-only',action='store_true')
    args=ap.parse_args()
    assert __debug__
    args.output.mkdir(parents=True,exist_ok=False)
    witness=json.loads(args.witness.read_text())
    source=args.source_root.resolve()
    for path,expected in witness['producer_inputs'].items():
        assert digest(source/path)==expected
    sys.path.insert(0,str(source/'scripts'))
    from partial_swap.paired import PairedExclusionCircuit
    from partial_swap.shared import SharedPointCircuit
    from partial_swap.graph import aligned_points,export

    class Selected(PairedExclusionCircuit):
        def __init__(self,n,pattern,association,threshold):
            self.top_pattern=pattern
            self.association=association
            self.base_threshold=threshold
            super().__init__(n)

        def grouping(self,points):
            sizes=self.top_pattern if len(points)==self.n else (2,)*(len(points)//2)+(1,)*(len(points)%2)
            assert sum(sizes)==len(points) and 2 in sizes
            groups,offset=[],0
            for size in sizes:
                groups.append(points[offset:offset+size]);offset+=size
            return groups

        def total(self,values):
            if self.association=='balanced':
                return super().total(values)
            values=[v for v in values if v]
            if self.association in ('left','right'):
                if self.association=='right':
                    values=values[::-1]
                result=0
                for value in values:
                    result=self.add(result,value)
                return result
            heap=[(self.support[x].bit_count(),self.support[x],x) for x in values]
            heapq.heapify(heap)
            while len(heap)>1:
                _,_,left=heapq.heappop(heap);_,_,right=heapq.heappop(heap)
                node=self.add(left,right)
                heapq.heappush(heap,(self.support[node].bit_count(),self.support[node],node))
            return heap[0][2] if heap else 0

    results=[]
    for axis in args.axis:
        row=witness['axes'][axis]
        local=Selected(row['h']-1,tuple(row['grouping']),row['association'],row['threshold'])
        local_check=local.verify()
        retain_total(local)
        circuit=SharedPointCircuit(row['h'],local,point_order=aligned_points)
        scalar,frames=circuit.verify(),circuit.verify_frames()
        dag=args.output/('axis%d.bin'%axis)
        export(circuit,dag)
        assert digest(dag)==row['dag_sha256']
        result=dict(axis=axis,dag_sha256=digest(dag),local=local_check,scalar=scalar,frames=frames)
        if not args.dag_only:
            links=args.output/('axis%d.links'%axis)
            cmd=[str(args.profiler.resolve()),str(dag),str(links),str(row['seed']),str(row['noise_milli'])]
            with (args.output/('axis%d.stdout.json'%axis)).open('w') as out,(args.output/('axis%d.stderr.log'%axis)).open('w') as err:
                subprocess.run(cmd,check=True,stdout=out,stderr=err)
            uses=Path(str(links)+'.uses.bin')
            n,pairs,identity=canonical_pairs(uses)
            assert n==row['n'] and pairs==[tuple(p) for p in row['canonical_donor_exact_use_pairs']]
            assert identity==row['canonical_exact_occurrence_sha256']
            checked=occurrence_check(uses,parse_dag(dag))
            profile=Path(str(dag)+'.fixed_ij_weighted_seed%d_noise%d.json'%(row['seed'],row['noise_milli']))
            assert digest(profile)==row['profile_sha256']
            assert json.loads(profile.read_text())==row['profile']
            result.update(exact_occurrence=checked,profile_sha256=digest(profile),command=cmd)
        results.append(result)
        circuit.support_in.cache_clear()
    (args.output/'receipt.json').write_text(json.dumps(dict(status='recovered_exact_weighted_native_witness',
                    recovery_source_sha256=digest(Path(__file__)),witness_sha256=digest(args.witness),
                    dependency_pin=witness['dependency_pin'],dag_only=args.dag_only,results=results),indent=2)+'\n')
    print(json.dumps(dict(status='exact_recovery_pass',axes=args.axis,dag_only=args.dag_only)))


if __name__=='__main__':
    main()
