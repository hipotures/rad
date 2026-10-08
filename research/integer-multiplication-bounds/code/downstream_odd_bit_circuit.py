#!/usr/bin/env python3
"""Exact odd-ground paired bit circuit and constructive stage matching.

The preserved GroupUnion and upstream pair recursion are not modified. A
local adapter changes the root point order and canonicalizes unordered keys.
All parity-independent scalar/frame checks are retained. Odd h=9 remains
excluded because I-J/9 is singular, not because its matching is unavailable.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import resource
import sys
import time

from downstream_gaussian import check_sources, network_counts, require
from downstream_parameter_optimum import as_strings
from finite_block_search import GroupUnion, install_reference


def even_image(triple, h, inverse=False):
    """Pinned even-ground matching, with its explicit inverse."""
    require(h >= 6 and h % 2 == 0, 'Even matching domain')
    groups = [x//2 for x in triple]
    if len(set(groups)) == 3:
        keep = min(groups)
        return tuple(sorted(x if x//2 == keep else x ^ 1 for x in triple))
    full = next(g for g in groups if groups.count(g) == 2)
    singleton = next(x for x in triple if x//2 != full)
    cycle = [g for g in range(h//2) if g != singleton//2]
    chosen = cycle[(cycle.index(full) + (-1 if inverse else 1)) % len(cycle)]
    return tuple(sorted((2*chosen, 2*chosen+1, singleton)))


def odd_image(triple, h, inverse=False):
    require(h >= 7 and h % 2 == 1, 'Odd matching domain')
    special = h-1
    if special not in triple:
        return even_image(triple, h-1, inverse)
    a, b = [x for x in triple if x != special]
    if a//2 != b//2:
        return tuple(sorted((a ^ 1, b ^ 1, special)))
    group = (a//2 + (-1 if inverse else 1)) % ((h-1)//2)
    return (2*group, 2*group+1, special)


def triple_matching(h):
    triples = list(combinations(range(h), 3))
    index = {triple:i for i,triple in enumerate(triples)}
    images = []
    classes = Counter()
    for triple in triples:
        image = odd_image(triple, h)
        require(len(set(triple) & set(image)) == 1, 'Odd matching is not intersection-one')
        require(odd_image(image, h, True) == triple, 'Constructive matching inverse failed')
        require(odd_image(odd_image(triple,h,True),h) == triple, 'Inverse-surjectivity check failed')
        require(image in index, 'Matching leaves the ground')
        images.append(index[image])
        if h-1 not in triple:
            key = 'avoids_special'
        else:
            a,b = [x for x in triple if x != h-1]
            key = 'special_and_full_pair' if a//2 == b//2 else 'special_and_distinct_pairs'
        classes[key] += 1
    require(sorted(images) == list(range(len(triples))), 'Matching is not a permutation')
    certificate = dict(h=h, triples=len(triples), distinct_images=len(set(images)),
                       all_intersections_one=True, explicit_inverse_verified=True,
                       classes=dict(classes), image_sha256=sha256(json.dumps(images,separators=(',',':')).encode()).hexdigest(),
                       ambient_rational_form_nondegenerate=h != 9)
    return triples, images, certificate


def local_point_order(h, common):
    """Keep all unaffected global pairs; pair the orphan with the special point."""
    require(h >= 7 and h % 2 == 1 and 0 <= common < h, 'Odd local order domain')
    special = h-1
    if common == special:
        order = list(range(special))
    else:
        order = [x for x in range(special) if x//2 != common//2] + [common ^ 1,special]
    require(sorted(order) == [x for x in range(h) if x != common], 'Local point order is not a bijection')
    require(len(order) % 2 == 0, 'Odd ground must have an even local root')
    return order


def build(h):
    require(h >= 7 and h % 2 == 1 and h != 9, 'Odd rational circuit domain excludes singular h9')
    from paired_exclusion_circuit import PairedExclusionCircuit

    class OrderedPaired(PairedExclusionCircuit):
        def __init__(self,n,permutation):
            self.root_permutation = tuple(permutation)
            require(sorted(self.root_permutation) == list(range(n)), 'Root permutation changed local inputs')
            super().__init__(n)

        def pair(self,points):
            ordered = [points[i] for i in self.root_permutation]
            edges = {tuple(sorted((a,b))):self.variables[tuple(sorted((a,b)))]
                     for a,b in combinations(ordered,2)}
            total,single,pairs = self.block(ordered,edges,{a:0 for a in ordered})
            canonical = {tuple(sorted(pair)):value for pair,value in pairs.items()}
            require(len(canonical) == len(pairs) == comb(len(points),2), 'Canonical pair outputs were lost or duplicated')
            return total,single,canonical

    def factory(n,common):
        natural = [x for x in range(h) if x != common]
        permutation = [natural.index(x) for x in local_point_order(h,common)]
        return OrderedPaired(n,permutation)

    return GroupUnion(h,factory,'natural',0,True)


def shared_exchange(h,seed,code,matching):
    """Full finite scalar exchange with the new bijection, on dirty banks."""
    from dag_network import invoke
    v = len(code['triples']); n = v**3; R = code['roles']; q = R+h
    require(v == comb(h,3) and sorted(matching) == list(range(v)), 'Exchange matching/input dimensions differ')
    inverse = [0]*v
    for first,last in enumerate(matching):inverse[last] = first
    def payload(i):return ((i*2654435761+seed*2246822519)^(i*i*97))&0xffffffff
    x = [payload(i) for i in range(n)]; y = [payload(n+i) for i in range(n)]
    shared = [payload(2*n+i) for i in range(v*v*q)]
    middle = [payload(2*n+v*v*q+i) for i in range(v*v*q)]
    before = [list(z) for z in (x,y,shared,middle)]
    def flat(a,b,c):return (a*v+b)*v+c
    for stage in range(3):
        for a in range(v):
            for b in range(v):
                indices = [flat(t,a,b) if stage == 0 else flat(a,t,b) if stage == 1 else flat(a,b,t)
                           for t in range(v)]
                bank = middle if stage == 1 else shared
                offset = (a*v+b if stage < 2 else inverse[b]*v+a)*q
                scratch = bank[offset:offset+R]; centers = bank[offset+R:offset+q]
                xx = [(y if stage == 1 else x)[i] for i in indices]
                yy = [(x if stage == 1 else y)[i] for i in indices]
                invoke(xx,yy,scratch,centers,code,inverse=(stage == 1))
                for i,xvalue,yvalue in zip(indices,xx,yy):
                    if stage == 1:y[i],x[i] = xvalue,yvalue
                    else:x[i],y[i] = xvalue,yvalue
                bank[offset:offset+q] = scratch+centers
    require(x == before[1] and y == before[0], 'Odd complete bank exchange failed')
    require(shared == before[2] and middle == before[3], 'Odd complete dirty auxiliary restoration failed')
    return dict(h=h,seed=seed,side_roles=R,physical_roles=2*n+2*v*v*q,
                scalar_invocations=3*v*v,complete_bank_exchange=True,
                every_shared_and_middle_auxiliary_coordinate_restored=True)


def case(h,small=False,exchange=False,full_coefficients=True):
    from frame_envelope import labels, target_check
    from frame_reuse import compile_reuse, optimize_chains, check, included
    from frame_reuse_certificate import program
    from review_aligned_graph import check as logical_check
    from review_envelopes import graph_envelope_check
    from review_singleton_witness import physical_coefficients
    from review_singleton_positions import compiled_digest, plan_check
    start = time.monotonic(); circuit = build(h)
    graph = circuit.verify()
    print('PASS odd logical constructor',h,'precompile roles',graph['roles'],flush=True)
    frames,metadata = labels(circuit,True)
    plan = optimize_chains(circuit,frames,'rank')
    chain = plan_check(circuit,frames,plan)
    compiled = compile_reuse(circuit,frames,plan)
    checked = check(circuit,frames,compiled)
    targets = target_check(circuit,frames,True)
    rational = graph_envelope_check(circuit,frames,compiled,dense=small)
    triples,matching,matching_certificate = triple_matching(h)
    require(triples == circuit.inputs, 'Odd graph and matching triples differ')
    row = dict(h=h,local_root_n=h-1,local_point_orders=[local_point_order(h,i) for i in range(h)],
               local_recipe='Pinned PairedExclusionCircuit, base4, custom root order only',
               graph=graph,compiled_roles=compiled['roles'],compiled_sha256=compiled_digest(compiled),
               controller_plan=chain,optimizer_summary=compiled['chain_summary'],
               compiled=checked,frames=metadata,physical_targets=targets,rational_frames=rational,
               stage_matching=matching_certificate)
    if full_coefficients:
        row['logical_coefficients'] = logical_check(circuit)
        row['physical_coefficients'] = physical_coefficients(circuit,compiled)
    if small:
        from dag_network import exact_invocation
        from review_frame_reuse import dirty_check
        scalar = program(circuit,compiled)
        row['independent_expansion'] = circuit.verify_small_expansion()
        row['complete_dirty_side_basis'] = dirty_check(circuit,frames,compiled)
        row['complete_invocation_dirty_basis_including_centers'] = [exact_invocation(h,inverse,scalar) for inverse in (False,True)]
        if exchange:
            row['complete_three_stage_exchange'] = [shared_exchange(h,seed,scalar,matching) for seed in (1,109)]
    if h >= 43:
        row['bit_counts'] = network_counts(h,compiled['roles'])
    row['elapsed_seconds'] = time.monotonic()-start
    row['process_peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print('PASS odd complete',h,'actual roles',compiled['roles'],'seconds',row['elapsed_seconds'],flush=True)
    included.cache_clear(); GroupUnion.support_in.cache_clear()
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream',type=Path,required=True)
    ap.add_argument('--h',type=int,nargs='*',default=[])
    ap.add_argument('--matching-only',type=int,nargs='*',default=[])
    ap.add_argument('--small',action='store_true')
    ap.add_argument('--exchange-h',type=int,nargs='*',default=[])
    ap.add_argument('--screen-only',action='store_true')
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args();require(not args.output.exists(),'Use a fresh result path')
    start = time.monotonic();install_reference(str(args.upstream))
    provenance = check_sources(args.upstream)
    begin = datetime.now(timezone.utc).isoformat();source = Path(__file__)
    rows = []
    matchings = [triple_matching(h)[2] for h in args.matching_only]
    for h in args.h:
        rows.append(case(h,args.small,h in args.exchange_h,not args.screen_only))
    names = ['downstream_odd_bit_circuit.py','downstream_gaussian.py','downstream_parameter_optimum.py',
             'finite_block_search.py','frame_envelope.py','frame_reuse.py','frame_reuse_certificate.py',
             'review_aligned_graph.py','review_envelopes.py','review_singleton_witness.py',
             'review_singleton_positions.py','review_frame_reuse.py','review_rational_frames.py']
    result = dict(status='PASS exact odd matching and supplied finite controls; independent promotion/analytic composition remain separate',
                  campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                  campaign_deadline='2026-10-08T08:25:21Z',started_utc=begin,
                  completed_utc=datetime.now(timezone.utc).isoformat(),provenance=provenance,
                  settings={**vars(args),'upstream':str(args.upstream),'output':str(args.output)},
                  source_sha256={name:sha256((source.parent/name).read_bytes()).hexdigest() for name in names},
                  upstream_source_sha256={name:sha256((args.upstream/'scripts'/name).read_bytes()).hexdigest()
                                          for name in ['paired_exclusion_circuit.py','exclusion_circuit.py','dag_network.py','reuse_network.py']},
                  matching_controls=matchings,cases=rows,elapsed_seconds=time.monotonic()-start,
                  process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Rational bit frames allow odd ground except h9; complex circuit stays at independently accepted even h50. No changed Gaussian or general matching-existence assumption.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    print('PASS',args.output,flush=True)


if __name__ == '__main__':main()
