#!/usr/bin/env python3
"""Exact D/E helper sharing with checked alternating phases and delayed clones.

The reviewed alternating interface permits every nested nondegenerate binary
interval. Identical scalar D/E pair helpers may therefore share their smaller
E frame even when the strict E-to-D residual is alternating. Every changed
logical map, physical interval, reverse complement, phase, target and guard
is checked by the frozen alternating witness implementation. HiGHS symmetry
preprocessing is disabled by the separately validated fresh selector.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time
from unittest.mock import patch

import finite_complex_alternating_reuse as alternating
import finite_complex_clone_nosym as options
import finite_complex_delayed_clones as witness


class PairSharingView(witness.TripleSideCircuit):
    def __init__(self, original, parity='all', sizes=None):
        assert parity in ('all', 'even', 'odd', 'none')
        self.h=original.h;self.inputs=original.inputs;self.variables=original.variables
        helpers={original.support[node]:node for node in original.active
            if original.args[node] and original.family[node]=='E' and node not in original.special}
        aliases={};records=[]
        for node in sorted(original.active):
            if original.family[node]!='D' or original.core[node].bit_count()!=2:continue
            other=helpers.get(original.support[node])
            if other is None:continue
            assert original.core[node]==original.core[other] and original.union[node]==original.union[other]
            outside=(original.union[node]&~original.core[node]).bit_count()
            smaller=witness.binary.BinaryFrame(self.h,original.frame(other))
            larger=witness.binary.BinaryFrame(self.h,original.frame(node))
            assert witness.binary.contained(smaller,larger) and smaller.dimension<larger.dimension
            residual_alternating=smaller.characteristic==larger.characteristic
            assert residual_alternating==bool(outside%2)
            selected=(parity=='all' or parity=='odd' and outside%2 or parity=='even' and not outside%2)
            selected=bool(selected and (sizes is None or outside in sizes))
            records.append(dict(D=node,E=other,outside_vertices=outside,
                residual_rank=larger.dimension-smaller.dimension,
                strict_residual_alternating=residual_alternating,selected=selected))
            if selected:aliases[node]=other
        self.args=[None]+[None]*len(self.inputs)
        for name in ('core','union','support','family'):
            setattr(self,name,getattr(original,name)[:len(self.inputs)+1])
        self.special={};mapping={node:node for node in range(1,len(self.inputs)+1)};visiting=set()
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
        self.diagnostic=dict(parity=parity,selected_outside_sizes=sorted(sizes) if sizes else None,
            candidate_aliases=len(records),chosen_aliases=len(aliases),
            selected_alternating_aliases=sum(row['selected'] and row['strict_residual_alternating'] for row in records),
            removed_active_additions=original.additions-self.additions,
            alias_records=records,
            proof_scope='Exact scalar helper equality; smaller nondegenerate E frame contained in D frame; all actual phase intervals checked after compilation')


def case(h, baseline, limit=4, policy='wide', seed=0, parity='all', sizes=None, dirty=False, exchange=False):
    at=time.monotonic();plain=witness.TripleSideCircuit(h)
    assert witness.logical_identity(plain)==baseline['logical']['circuit_sha256']
    shared=PairSharingView(plain,parity,sizes)
    # This identity is only a constructor checksum. The final changed-DAG
    # verifier below reconstructs every coefficient, including all aliases.
    identity=dict(logical=dict(circuit_sha256=witness.logical_identity(shared)),
        compiled_roles=baseline['compiled_roles'])
    with patch.object(alternating,'options',options), \
         patch.object(witness,'TripleSideCircuit',lambda ground:shared), \
         patch.object(witness.binary,'admissible',witness.binary.contained):
        row=alternating.case(h,identity,limit,policy,seed,dirty,exchange)
    row.update(cross_DE_sharing=shared.diagnostic,
        original_accepted_logical_sha256=baseline['logical']['circuit_sha256'],
        original_accepted_compiled_sha256=baseline['checked']['compiled_sha256'],
        original_accepted_roles=baseline['compiled_roles'],
        option_selector_source_sha256=sha256(Path(options.__file__).read_bytes()).hexdigest(),
        elapsed_seconds=time.monotonic()-at,
        scientific_scope='Exact shared D/E scalar DAG, actual nondegenerate binary Gram phases including alternating residuals, delayed clones; complete changed scalar/physical/reverse/target/G/E checks; independent transfer pending')
    return row


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',type=Path,required=True)
    parser.add_argument('--h',type=int,nargs='+',default=[8,12])
    parser.add_argument('--clone-limit',type=int,default=4)
    parser.add_argument('--policy',choices=['wide','narrow','seeded'],default='wide')
    parser.add_argument('--seed',type=int,default=0)
    parser.add_argument('--parity',choices=['all','even','odd','none'],default='all')
    parser.add_argument('--outside-size',type=int,nargs='+')
    parser.add_argument('--dirty-ground',type=int,default=8)
    parser.add_argument('--exchange-h8',action='store_true')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();assert not args.output.exists()
    baseline=json.loads(args.baseline.read_text())
    assert baseline['source_sha256']==sha256(Path(witness.binary.__file__).read_bytes()).hexdigest()
    saved={row['h']:row for row in baseline['rows']};at=time.monotonic()
    value=dict(status='Running',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        baseline_input_sha256=sha256(args.baseline.read_bytes()).hexdigest(),rows=[],
        source_dependencies={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in
            ('finite_complex_alternating_reuse.py','finite_complex_clone_nosym.py','finite_complex_delayed_clones.py')},
        started_utc=datetime.now(timezone.utc).isoformat())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for h in args.h:
        row=case(h,saved[h],args.clone_limit,args.policy,args.seed,args.parity,
                 set(args.outside_size) if args.outside_size else None,h==args.dirty_ground,h==8 and args.exchange_h8)
        value['rows'].append(row);args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(h=h,roles=row['compiled_roles'],aliases=row['cross_DE_sharing']['chosen_aliases'],
            alternating_aliases=row['cross_DE_sharing']['selected_alternating_aliases'],
            actual_alternating_transitions=row['phase']['actual_alternating_forward_transitions'],
            seconds=row['elapsed_seconds'])),flush=True)
    value.update(status='Terminal exact joint D/E sharing and alternating phase witness PASS',
        elapsed_seconds=time.monotonic()-at,completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
