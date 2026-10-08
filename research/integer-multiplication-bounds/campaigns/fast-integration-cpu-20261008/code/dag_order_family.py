#!/usr/bin/env python3
"""Different recursive leaf layouts with exact supports and full I+J moments.

Credits: pinned PR40 Apache-2.0 PairedExclusionCircuit and SharedPointCircuit,
icekylinx and the retained PR7 underlying circuit notices. This new wrapper
changes grouping order, canonicalizes pair keys and checks every output.
"""
import argparse
import datetime
from fractions import Fraction
import hashlib
import heapq
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def load(path,name):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',required=True,type=Path)
    parser.add_argument('--profiler',required=True,type=Path)
    parser.add_argument('--dimension',required=True,type=int)
    parser.add_argument('--pattern',required=True)
    parser.add_argument('--association',choices=['left','right','balanced','small-first'],required=True)
    parser.add_argument('--threshold',type=int,default=2)
    parser.add_argument('--scope',choices=['top','all'],default='top')
    parser.add_argument('--partner',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--rotations',nargs='*',type=int,default=list(range(1,24)))
    parser.add_argument('--extra-orders',nargs='*',choices=['zigzag','bit-reversal'],default=['zigzag','bit-reversal'])
    args = parser.parse_args()
    assert not sys.flags.optimize and args.dimension in (23,25)
    pattern = tuple(map(int,args.pattern))
    assert sum(pattern)==args.dimension-1 and set(pattern)<={1,2} and 2 in pattern
    args.output.mkdir(parents=True,exist_ok=False)
    source = args.source_root.resolve()
    sys.path.insert(0,str(source/'scripts'))
    from partial_swap.paired import PairedExclusionCircuit
    from partial_swap.shared import SharedPointCircuit
    from partial_swap.graph import aligned_points,export
    seed = load(ROOT/'agents/scout/code/changed_dag_seed.py','seed')
    scorer = load(ROOT/'agents/scout/code/fixed_controller_score.py','scorer')
    search = load(ROOT/'code/fixed_moment_family.py','search')
    partner = json.loads(args.partner.read_text())

    class Ordered(PairedExclusionCircuit):
        base_threshold = args.threshold

        def __init__(self,n,order):
            self.order = order
            super().__init__(n)

        def grouping(self,points):
            ordered = list(points)
            if args.scope=='all' or len(points)==self.n:
                if self.order.startswith('rotate'):
                    offset = int(self.order[6:]) % len(points)
                    ordered = points[offset:]+points[:offset]
                elif self.order=='zigzag':
                    ordered = []
                    lo,hi = 0,len(points)-1
                    while lo<=hi:
                        ordered.append(points[lo]);lo+=1
                        if lo<=hi:
                            ordered.append(points[hi]);hi-=1
                else:
                    bits = (len(points)-1).bit_length()
                    ordered = [points[i] for i in sorted(range(len(points)),key=lambda i:int(format(i,'0%db'%bits)[::-1],2))]
            sizes = pattern if len(points)==self.n else (2,)*(len(points)//2)+(1,)*(len(points)%2)
            groups,offset = [],0
            for size in sizes:
                groups.append(ordered[offset:offset+size]);offset+=size
            assert offset==len(points)
            return groups

        def block(self,points,edges,weights):
            total,singles,pairs = super().block(points,edges,weights)
            canonical = {tuple(sorted(key)):value for key,value in pairs.items()}
            assert len(canonical)==len(pairs)
            return total,singles,canonical

        def total(self,values):
            if args.association=='balanced':
                return super().total(values)
            values = [v for v in values if v]
            if args.association in ('left','right'):
                if args.association=='right':
                    values = values[::-1]
                result = 0
                for value in values:
                    result = self.add(result,value)
                return result
            heap = [(self.support[x].bit_count(),self.support[x],x) for x in values]
            heapq.heapify(heap)
            while len(heap)>1:
                _,_,left = heapq.heappop(heap);_,_,right = heapq.heappop(heap)
                node = self.add(left,right)
                heapq.heappush(heap,(self.support[node].bit_count(),self.support[node],node))
            return heap[0][2] if heap else 0

    orders = ['rotate%d'%k for k in sorted({k%(args.dimension-1) for k in args.rotations})] + args.extra_orders
    protocol = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    upstream='https://github.com/rohanarun/integer-mult-bounds',
                    pinned_commit=seed.PIN,dimension=args.dimension,pattern=pattern,
                    association=args.association,threshold=args.threshold,scope=args.scope,orders=orders,
                    source=Path(__file__).read_text(),partner=json.loads(args.partner.read_text()),
                    partner_sha256=hashlib.sha256(args.partner.read_bytes()).hexdigest(),
                    profiler_sha256=hashlib.sha256(args.profiler.read_bytes()).hexdigest(),
                    scientific_scope='Full original fixed-basis finite controller; independent compiler/all-size review still required')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    seen = set()
    for order in orders:
        began = time.time()
        identifier = 'h%d-%s-%s'%(args.dimension,args.scope,order)
        local = Ordered(args.dimension-1,order)
        local_check = local.verify()
        seed.retain_total(local)
        circuit = SharedPointCircuit(args.dimension,local,point_order=aligned_points)
        scalar,frames = circuit.verify(),circuit.verify_frames()
        digest = scalar['circuit_sha256']
        if digest in seen:
            (args.output/(identifier+'.json')).write_text(json.dumps(dict(id=identifier,duplicate_exact_dag=True,scalar=scalar),indent=2)+'\n')
            continue
        seen.add(digest)
        dag = args.output/(identifier+'.bin')
        export(circuit,dag)
        with (args.output/(identifier+'.log')).open('w') as log:
            subprocess.run([str(args.profiler),str(dag),str(dag)+'.fixed.links'],stdout=log,stderr=log,check=True)
        profile = json.loads(Path(str(dag)+'.fixed_ij_profiles.json').read_text())
        counts = scorer.profile(profile,partner) if args.dimension==23 else scorer.profile(partner,profile)
        exact = search.safe_search(scorer,counts)
        result = dict(id=identifier,scalar=scalar,frames=frames,local_check=local_check,
                      dag_sha256=hashlib.sha256(dag.read_bytes()).hexdigest(),fixed_profile=profile,
                      complete_controller=scorer.jsonable(counts),**exact,elapsed_seconds=time.time()-began,
                      scope=protocol['scientific_scope'])
        (args.output/(identifier+'.json')).write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(dict(id=identifier,R=profile['R'],safe_saving=exact['safe_saving'],seconds=result['elapsed_seconds'])),flush=True)
        circuit.support_in.cache_clear()


if __name__=='__main__':
    main()
