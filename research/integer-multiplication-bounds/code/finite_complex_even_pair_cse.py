#!/usr/bin/env python3
"""Cross-D/E exact support sharing with nonalternating even-pair residuals.

Only E pair helpers with an even number of outside vertices replace an
identical D helper. Odd helpers give alternating strict residuals and are
recorded as exclusions. No cancellation or approximate coefficient maps.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time
from unittest.mock import patch
import frame_reuse
import finite_complex_delayed_clones as witness
from finite_clone_recovered_witness import compiled_hash


class EvenPairCSEView(witness.TripleSideCircuit):
    def __init__(self,original,sizes=None):
        self.h=original.h;self.inputs=original.inputs;self.variables=original.variables
        e_helpers={original.support[node]:node for node in original.active
            if original.args[node] and original.family[node]=='E' and node not in original.special}
        aliases={};odd=[];available=[]
        for node in sorted(original.active):
            if original.family[node]!='D' or original.core[node].bit_count()!=2:continue
            other=e_helpers.get(original.support[node])
            if other is None:continue
            assert original.core[node]==original.core[other] and original.union[node]==original.union[other]
            outside=(original.union[node]&~original.core[node]).bit_count();a=witness.binary.BinaryFrame(self.h,original.frame(other));b=witness.binary.BinaryFrame(self.h,original.frame(node))
            assert witness.binary.contained(a,b) and a.dimension<b.dimension
            if outside%2:
                assert a.characteristic==b.characteristic and not witness.binary.admissible(a,b)
                odd.append(dict(D=node,E=other,outside_vertices=outside,residual_rank=b.dimension-a.dimension))
            else:
                assert witness.binary.admissible(a,b);available.append(dict(D=node,E=other,outside_vertices=outside))
                if sizes is None or outside in sizes:aliases[node]=other
        self.args=[None]+[None]*len(self.inputs);self.core=original.core[:len(self.inputs)+1]
        self.union=original.union[:len(self.inputs)+1];self.support=original.support[:len(self.inputs)+1]
        self.family=original.family[:len(self.inputs)+1];self.special={}
        mapping={node:node for node in range(1,len(self.inputs)+1)};visiting=set()
        def visit(old):
            if old in mapping:return mapping[old]
            if old in aliases:
                new=visit(aliases[old]);mapping[old]=new;return new
            assert old not in visiting;visiting.add(old)
            children=tuple(visit(child) for child in original.args[old]);new=len(self.args)
            self.args.append(children)
            for name in ('core','union','support','family'):getattr(self,name).append(getattr(original,name)[old])
            if old in original.special:self.special[new]=original.special[old]
            mapping[old]=new;visiting.remove(old);return new
        self.outputs={target:visit(node) for target,node in sorted(original.outputs.items())}
        self.active=set();stack=list(self.outputs.values())
        while stack:
            node=stack.pop()
            if node in self.active:continue
            self.active.add(node)
            if self.args[node]:stack.extend(self.args[node])
        self.additions=sum(self.args[node] is not None for node in self.active)
        assert set(range(1,len(self.args)))==self.active
        self.original_mapping=mapping;self.aliases=aliases
        self.diagnostic=dict(available_even_pair_aliases=len(available),chosen_even_pair_aliases=len(aliases),
            excluded_odd_alternating_aliases=len(odd),removed_active_additions=original.additions-self.additions,
            even_alias_records=available,odd_alternating_records=odd,
            selected_outside_sizes=sorted(sizes) if sizes is not None else None)


def case(h,baseline,sizes=None,dirty=False,exchange=False):
    at=time.monotonic();original=witness.TripleSideCircuit(h)
    assert witness.logical_identity(original)==baseline['logical']['circuit_sha256']
    view=EvenPairCSEView(original,sizes)
    if not view.aliases:
        return dict(h=h,status='No new alias; accepted original not replayed',diagnostic=view.diagnostic,
            baseline_roles=baseline['compiled_roles'],compiled_roles=baseline['compiled_roles'],elapsed_seconds=time.monotonic()-at)
    frames,metadata=witness.binary.labels(view)
    with patch.object(frame_reuse,'included',witness.binary.admissible):
        plan=frame_reuse.optimize_chains(view,frames,'rank');code=frame_reuse.compile_reuse(view,frames,plan)
        checked=frame_reuse.check(view,frames,code)
    logical=view.verify();physical=witness.binary.physical_replay(view,code);phase=witness.binary.phase_timeline(view,frames,code)
    independent=witness.independent_physical(view,frames,code)
    from review_complex_frames import complete_scalar_matrix
    dirty_result=complete_scalar_matrix(view,code) if dirty else None
    pi,matching=witness.stage_matching(view);stages=witness.global_exchange(view,code,pi,[5]) if exchange else []
    v=comb(h,3);m=h**3;N=v**3;R=code['roles'];W=2*N+2*v*v*(R+h+1)
    L=3*v*v*(h+1)*h;D=2*N-2*L;s=W*m-D
    G=3*v*v*(4*(view.additions+v)+4*v+4);E=64*(W+m+1)**3;depth=2*G*W*W+4*s+4*W+4;assert depth<E
    counts=dict(h=h,v=v,m=m,N=N,R=R,W=W,L=L,D=D,s=s,eta=Q(D,W*m))
    row=dict(h=h,status='Full changed cross-D/E even-pair CSE witness PASS',baseline_roles=baseline['compiled_roles'],
        compiled_roles=R,role_saving=baseline['compiled_roles']-R,diagnostic=view.diagnostic,logical=logical,
        checked=checked,frames=metadata,physical=physical,phase=phase,independent_actual_frames=independent,
        complete_dirty_scalar_matrix=dirty_result,stage_matching=matching,complete_shared_three_stage=stages,
        shared_complex_counts=counts,guard=dict(actual_grouped_scalar_gates=G,additive_E=E,
            exact_operation_depth_bound=depth,slack=E-depth),
        saving_enclosure=witness.saving_enclosure(counts['eta'],m) if D>0 else None,
        original_coefficients_reused_by_exact_identity=True,original_compiled_sha256=baseline['checked']['compiled_sha256'],
        elapsed_seconds=time.monotonic()-at,
        scientific_scope='Exact disjoint support CSE; actual binary nonalternating residuals; full changed maps/physical/Gram/phase/targets/guard; analytic transfer review separate')
    witness.binary.admissible.cache_clear();witness.binary.contained.cache_clear();witness.binary.basis.cache_clear()
    return witness.as_strings(row)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--baseline',type=Path,required=True)
    ap.add_argument('--h',type=int,nargs='+',default=[8,12]);ap.add_argument('--outside-size',type=int,nargs='+')
    ap.add_argument('--dirty-ground',type=int,default=8);ap.add_argument('--exchange-h8',action='store_true')
    ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists()
    baseline=json.loads(args.baseline.read_text());assert baseline['source_sha256']==sha256(Path(witness.binary.__file__).read_bytes()).hexdigest()
    saved={row['h']:row for row in baseline['rows']};at=time.monotonic();value=dict(status='Running',rows=[],
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),baseline_input_sha256=sha256(args.baseline.read_bytes()).hexdigest(),
        started_utc=datetime.now(timezone.utc).isoformat())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for h in args.h:
        row=case(h,saved[h],set(args.outside_size) if args.outside_size else None,h==args.dirty_ground,h==8 and args.exchange_h8)
        value['rows'].append(row);args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(h=h,roles=row['compiled_roles'],aliases=row['diagnostic']['chosen_even_pair_aliases'],
            excluded_odd=row['diagnostic']['excluded_odd_alternating_aliases'],seconds=row['elapsed_seconds'])),flush=True)
    value.update(status='Terminal exact even-pair cross-D/E CSE discriminator PASS',elapsed_seconds=time.monotonic()-at,
        completed_utc=datetime.now(timezone.utc).isoformat());args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
