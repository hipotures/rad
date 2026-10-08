#!/usr/bin/env python3
"""Nested nondegenerate frames for whole intersection-one sums.

Common-source nodes use their exact positive indicator span. Source-core
zero nodes use the orthogonal complement of their complete physical target
family, which this finite constructor checks has one or two triples. The
Gram of any two distinct triple indicators under H=9I-J is positive:
9[[2,r-1],[r-1,2]], r=0,1,2. Thus every kernel is nondegenerate, including
the cases whose exact source spans are singular. No positive-envelope
assumption is substituted for actual rational source spans.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import random
import time
from unittest.mock import patch

from finite_block_search import install_reference
from finite_intersection_blocks import IntersectionCircuit
import frame_reuse

positive_included = frame_reuse.included


@dataclass(frozen=True)
class Kernel:
    h: int
    targets: tuple[int, ...]

    @property
    def dimension(self):
        return self.h-len(self.targets)


@lru_cache(maxsize=500000)
def included(a, b):
    if isinstance(a, Kernel):
        if isinstance(b, Kernel):
            assert a.h == b.h
            # A two-dimensional span contains no third distinct constant-
            # weight 0/1 triple: the coefficients sum to1 and any coordinate
            # where its two generators differ forces a coefficient0 or1.
            return set(b.targets).issubset(a.targets)
        # Positive common-point spans lie in sum(x)=3*x_common. The H-normal
        # to that hyperplane has nonzero coordinates outside one/two triples,
        # or separates one vertex within a disjoint triple. It cannot lie in
        # the target span. Hence its kernel cannot lie in a common-point span.
        return False
    if isinstance(b, Kernel):
        return all((source & target).bit_count() == 1
                   for source in a.basis for target in b.targets)
    return positive_included(a, b)


def labels(circuit):
    h = circuit.h; assert h != 9
    zero = {node for node in circuit.active if not circuit.core[node]}
    descendants = {node:set() for node in zero}
    for (_, target), node in circuit.outputs.items():
        assert node in zero
        descendants[node].add(sum(1 << v for v in target))
    for node in sorted(circuit.active, reverse=True):
        if node not in zero:
            continue
        assert 1 <= len(descendants[node]) <= 2, 'Whole target family has more than two triples'
        for child in circuit.args[node] or ():
            if child in zero:
                descendants[child].update(descendants[node])
                assert len(descendants[child]) <= 2, 'Core-zero child reaches more than two targets'
    frames, intern = {}, {}
    kernels = Counter(); disjoint_pairs = 0
    for node in sorted(circuit.active):
        if node in zero:
            targets = tuple(sorted(descendants[node])); frame = Kernel(h, targets)
            kernels[len(targets)] += 1
            disjoint_pairs += int(len(targets) == 2 and not targets[0] & targets[1])
            if len(targets) == 2:
                intersection = (targets[0] & targets[1]).bit_count()
                assert intersection in (0,1,2)
                assert 4-(intersection-1)**2 > 0
            key = ('K', targets)
        else:
            if circuit.args[node] is None:
                generators = (circuit.core[node],)
            else:
                a,b = (frames[child] for child in circuit.args[node])
                assert not isinstance(a,Kernel) and not isinstance(b,Kernel)
                generators = a.basis+b.basis
            common = (circuit.core[node] & -circuit.core[node]).bit_length()-1
            frame = frame_reuse.space_of(generators, common, h)
            assert frame.core == circuit.core[node] and frame.vertices == circuit.union[node]
            key = ('P',frame.common,frame.tags)
        frames[node] = intern.setdefault(key,frame)
        if circuit.args[node]:
            for child in circuit.args[node]:
                assert included(frames[child],frames[node]), 'Original frame edge is not nested'
        else:
            assert frames[node].dimension == 1 and frames[node].basis == (circuit.core[node],)
    for (_, target), node in circuit.outputs.items():
        assert frames[node] == Kernel(h,(sum(1 << v for v in target),))
    return frames, dict(frame_family='Exact positive common-source spans; exact complements of at-most-two complete physical targets at core-zero nodes',
        unique_frames=len(intern),positive_nodes=len(circuit.active)-len(zero),kernel_nodes=len(zero),
        singleton_target_kernels=kernels[1],two_target_kernels=kernels[2],disjoint_two_target_kernels=disjoint_pairs,
        every_source_copy_line_exact=True,every_original_frame_edge_nested=True,every_output_kernel_is_exact_target_perp=True,
        nondegeneracy='Ambient H=9I-J nondegenerate h!=9; common-source spans positive; all one/two triple target Grams positive; their kernels nondegenerate')


def physical_map(circuit, code):
    values = [0]*code['roles']; additions = copies = 0
    for node, ins, outs in code['gates']:
        if circuit.args[node] is None:
            assert len(ins) == 1 and not values[ins[0]]
            values[ins[0]] = circuit.support[node]
        else:
            a,b = circuit.args[node]
            assert {values[ins[0]],values[ins[1]]} == {circuit.support[a],circuit.support[b]}
            assert not values[ins[0]] & values[ins[1]]
            values[ins[0]] |= values[ins[1]]; additions += 1
        assert values[ins[0]] == circuit.support[node]
        for slot in outs[1:]:
            assert not values[slot]
            values[slot] = values[ins[0]]; copies += 1
    for target,slot in code['outputs'].items():
        assert values[slot] == circuit.support[circuit.outputs[target]]
    return dict(all_physical_input_coefficients_exact=True,all_additions_disjoint=True,
        every_copy_destination_fresh=True,all_whole_outputs_exact=True,physical_additions=additions,physical_copies=copies)


def independent(circuit, frames, plan, seed=109):
    import sympy as sp
    from finite_target_complements import inertia, primitive
    h = circuit.h; H = 9*sp.eye(h)-sp.ones(h)
    assert H.det() != 0
    unique = list(set(frames.values())); bases, constraints = {}, {}
    counts = Counter()
    for frame in unique:
        if isinstance(frame,Kernel):
            T = sp.Matrix(h,len(frame.targets),lambda row,col:(frame.targets[col] >> row)&1)
            assert T.rank() == len(frame.targets)
            assert inertia(T.T*H*T) == (len(frame.targets),0,0)
            B = sp.Matrix.hstack(*(T.T*H).nullspace())
            expected_negative = int(h > 9)
            assert inertia(B.T*H*B) == (frame.dimension-expected_negative,expected_negative,0)
        else:
            B = sp.Matrix(h,frame.dimension,lambda row,col:(frame.basis[col] >> row)&1)
            assert inertia(B.T*H*B) == (frame.dimension,0,0)
        assert B.rank() == frame.dimension
        bases[frame] = tuple(primitive(B[:,col]) for col in range(B.cols))
        constraints[frame] = tuple(primitive(v) for v in B.T.nullspace())
        counts['kernel' if isinstance(frame,Kernel) else 'positive'] += 1

    def contains(a,b):
        return all(sum(x*y for x,y in zip(column,normal)) == 0
                   for column in bases[a] for normal in constraints[b])

    decisions = set()
    for node in circuit.active:
        for child in circuit.args[node] or ():
            decisions.add((frames[child],frames[node]))
    _,descriptions,successor,_,_ = plan
    for first,second in successor.items():
        _,previous,_ = descriptions[first];node,following,_ = descriptions[second]
        decisions.add((frames[previous],frames[following if following is not None else node]))
    rng = random.Random(seed)
    for _ in range(512):
        decisions.add((rng.choice(unique),rng.choice(unique)))
    for a,b in decisions:
        assert included(a,b) == contains(a,b), 'Independent rational inclusion mismatch'
    return dict(exact_restricted_frame_grams=len(unique),frame_types=dict(counts),
        exact_original_and_retained_rational_inclusions=len(decisions),seed=seed)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference',required=True)
    ap.add_argument('--h',type=int,nargs='+',default=[8,12])
    ap.add_argument('--independent',action='store_true')
    ap.add_argument('--dirty',action='store_true')
    ap.add_argument('--stage-h6',action='store_true')
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args(); install_reference(args.reference); assert not args.output.exists()
    start = time.monotonic();rows=[]
    result = dict(campaign_id='20261007T222521Z',started_utc=datetime.now(timezone.utc).isoformat(),rows=rows,
        source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in
            [Path(__file__).name,'finite_intersection_blocks.py','finite_complex_blocks.py','frame_reuse.py']})
    for h in args.h:
        at = time.monotonic();circuit=IntersectionCircuit(h);graph=circuit.verify();marks={}
        tick=time.monotonic();frames,metadata=labels(circuit);marks['labels']=time.monotonic()-tick
        tick=time.monotonic()
        with patch.object(frame_reuse,'included',included):
            plan=frame_reuse.optimize_chains(circuit,frames,'rank')
            marks['flow']=time.monotonic()-tick;tick=time.monotonic()
            code=frame_reuse.compile_reuse(circuit,frames,plan)
            checked=frame_reuse.check(circuit,frames,code)
        marks['compile_and_frame_check']=time.monotonic()-tick
        checked['nondegeneracy']=metadata['nondegeneracy']
        tick=time.monotonic();physical=physical_map(circuit,code);marks['independent_physical_coefficients']=time.monotonic()-tick
        row=dict(h=h,graph=graph,roles=code['roles'],frames=metadata,chains=code['chain_summary'],checked=checked,
            physical=physical,phase_seconds=marks,
            scope='Exact finite whole-map mixer with positive/indefinite frames; final rank/join transfer and analytic composition require separate acknowledgement')
        if args.independent:
            row['independent']=independent(circuit,frames,plan)
        if args.dirty or args.stage_h6:
            from frame_reuse_certificate import program
            from dag_network import exact_invocation,shared_scalar_model
            scalar=program(circuit,code)
            if args.dirty and h<=12:
                row['dirty_basis']=[exact_invocation(h,inverse,scalar) for inverse in (False,True)]
            if args.stage_h6 and h==6:
                row['three_stage']=[shared_scalar_model(h,seed,scalar) for seed in (1,109)]
        row['elapsed_seconds']=time.monotonic()-at;rows.append(row);result['elapsed_seconds']=time.monotonic()-start
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(h=h,roles=code['roles'],links=code['chain_summary']['selected_links'],seconds=row['elapsed_seconds'])),flush=True)
        included.cache_clear();positive_included.cache_clear()
    result['status']='Terminal finite nondegenerate-frame witness PASS'
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
