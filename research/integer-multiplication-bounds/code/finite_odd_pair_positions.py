#!/usr/bin/env python3
"""Odd bit grounds: move a full orphan/special pair, not a singleton.

The existing odd-ground matcher is reused. The local even-size weighted
pair recursion and the positive rational envelope family remain unchanged.
Only the root ordering and base cutoff are configurable.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import resource
import time

from finite_block_search import GroupUnion,install_reference,make_block_class
from downstream_odd_bit_circuit import triple_matching
from downstream_parameter_optimum import as_strings,saving_enclosure
from finite_residual_rank_histogram import histogram


def orders(h,positions):
    assert h>=7 and h%2 and h!=9 and len(positions)==h
    k=(h-1)//2;special=h-1;values=[]
    for common,position in enumerate(positions):
        assert 0<=position<k
        if common==special:order=list(range(special))
        else:
            others=[x for x in range(special) if x//2!=common//2]
            order=others[:2*position]+[common^1,special]+others[2*position:]
        assert sorted(order)==[x for x in range(h) if x!=common]
        assert all((order[j]//2==order[j+1]//2 or special in order[j:j+2]) for j in range(0,len(order),2))
        values.append(order)
    return values


def build(h,positions,base):
    rootorders=orders(h,positions);parent=make_block_class()
    class Ordered(parent):
        def __init__(self,n,permutation):
            self.permutation=tuple(permutation);super().__init__(n,(2,),base,0)
        def pair(self,points):
            ordered=[points[i] for i in self.permutation]
            edges={tuple(sorted((a,b))):self.variables[tuple(sorted((a,b)))] for a,b in combinations(ordered,2)}
            total,one,pairs=self.block(ordered,edges,{a:0 for a in ordered},0)
            canonical={tuple(sorted(pair)):value for pair,value in pairs.items()}
            assert len(canonical)==len(pairs)
            return total,one,canonical
    def factory(n,common):
        natural=[x for x in range(h) if x!=common]
        return Ordered(n,[natural.index(x) for x in rootorders[common]])
    return GroupUnion(h,factory,'natural',0,True)


def case(h,positions,base,full,small):
    at=time.monotonic();circuit=build(h,positions,base);logical=circuit.verify()
    triples,images,matching=triple_matching(h);assert triples==circuit.inputs
    row=dict(h=h,base=base,positions=positions,logical=logical,stage_matching=matching,
        root_local_size=h-1,root_local_parity='even; no local singleton')
    if full:
        from fast_frame_envelope import labels
        from frame_envelope import target_check
        from frame_reuse import optimize_chains,compile_reuse,check,included
        frames,metadata=labels(circuit,True);plan=optimize_chains(circuit,frames,'rank')
        code=compile_reuse(circuit,frames,plan);checked=check(circuit,frames,code)
        targets=target_check(circuit,frames,True);ranks=histogram(h,circuit,frames,code)
        row.update(compiled_roles=code['roles'],compiled=checked,frames=metadata,targets=targets,
            chains=code['chain_summary'],residual_rank_histogram=ranks)
        if ranks['D']>0:row['supported_uniform_shrink_saving']=saving_enclosure(Fraction(ranks['D'],ranks['W']*ranks['m']),ranks['m'])
        else:row['supported_uniform_shrink_saving']=None
        if small:
            from review_envelopes import graph_envelope_check
            from review_singleton_witness import physical_coefficients
            from review_aligned_graph import check as independent_logical
            from review_frame_reuse import dirty_check
            from frame_reuse_certificate import program
            from dag_network import exact_invocation
            row.update(independent_rational_frames=graph_envelope_check(circuit,frames,code,dense=True),
                independent_logical=independent_logical(circuit),independent_physical=physical_coefficients(circuit,code),
                complete_side_dirty_basis=dirty_check(circuit,frames,code),
                complete_invocation_dirty_basis=[exact_invocation(h,inverse,program(circuit,code)) for inverse in (False,True)])
        included.cache_clear();GroupUnion.support_in.cache_clear()
    row.update(elapsed_seconds=time.monotonic()-at,process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return as_strings(row)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--reference',required=True);ap.add_argument('--h',type=int,nargs='+',required=True)
    ap.add_argument('--positions',type=int,nargs='+',default=[-1,0]);ap.add_argument('--base',type=int,default=2)
    ap.add_argument('--full',action='store_true');ap.add_argument('--small',action='store_true')
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();install_reference(args.reference)
    result=dict(status='Running',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        matching_source_sha256=sha256(Path(__file__).with_name('downstream_odd_bit_circuit.py').read_bytes()).hexdigest(),
        started_utc=datetime.now(timezone.utc).isoformat(),settings={k:str(v) if isinstance(v,Path) else v for k,v in vars(args).items()},rows=[],
        scope='Odd full-pair placement study; positive rational frames and constructive odd matcher retained; no automatic transfer promotion')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for h in args.h:
        for position in args.positions:
            value=(h-3)//2 if position==-1 else position
            row=case(h,[value]*h,args.base,args.full,args.small);result['rows'].append(row)
            args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
            print(json.dumps(dict(h=h,position=value,precompile_roles=row['logical']['roles'],
                compiled_roles=row.get('compiled_roles'),seconds=row['elapsed_seconds'])),flush=True)
    result.update(status='Terminal exact odd full-pair study PASS',completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
