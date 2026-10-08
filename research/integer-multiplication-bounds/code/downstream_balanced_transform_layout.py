#!/usr/bin/env python3
"""Exact named-slot controls for a balanced synthetic-transform layout.

Only long-axis leading bits enter the individually processed prefix. All
remaining slots are split into equal-across-axis chunks whose widths differ
by at most one and remain in [K,2K). This source checks the layout, actual
unequal-chunk movement schedule and butterfly/twiddle address chronology;
the uniform compact-layer transfer is a written proof obligation.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
from itertools import product
import json
from pathlib import Path
import time

from downstream_gaussian import check_sources, require


def balanced_widths(ell,K):
    require(ell >= 2 and 1 <= K <= ell-1, 'Invalid transform width')
    q = (ell-1)//K
    lo, extra = divmod(ell-1,q)
    widths = [lo+1]*extra+[lo]*(q-extra)
    require(sum(widths) == ell-1 and min(widths) >= K and max(widths) < 2*K,
            'Balanced widths escaped [K,2K)')
    require(max(widths)-min(widths) <= 1, 'Balanced widths differ by more than one')
    return widths


def layout(ell,K,long_axes):
    D = len(long_axes)
    original = [(i,h) for i,long in enumerate(long_axes) for h in range(ell-2+long,-1,-1)]
    current = original[:]
    prefix = [(i,ell-1) for i,long in enumerate(long_axes) if long]
    operations = []
    for end,slot in enumerate(prefix):
        pos = current.index(slot)
        current.insert(end,current.pop(pos))
        operations.append(dict(kind='single_bit_move',slot=slot,old=pos,new=end))
    widths = balanced_widths(ell,K)
    chunks = {}
    high = ell-2
    for j,width in enumerate(widths):
        for i in range(D):
            chunks[i,j] = [(i,h) for h in range(high,high-width,-1)]
        high -= width
    require(high == -1, 'Balanced chunks omitted a low slot')
    ordering = [(i,j) for i in range(D) for j in range(len(widths))]
    target = [(i,j) for j in range(len(widths)) for i in range(D)]
    require(current == prefix+sum((chunks[t] for t in ordering),[]), 'Prefix moves changed chunk order')
    chunk_swaps = mismatched = 0
    for left,name in enumerate(target[:-1]):
        right = ordering.index(name)
        if left == right:
            continue
        A,B = chunks[ordering[left]],chunks[ordering[right]]
        pA = len(prefix)+sum(len(chunks[t]) for t in ordering[:left])
        pB = len(prefix)+sum(len(chunks[t]) for t in ordering[:right])
        before = current[:]
        gap = before[pA+len(A):pB]
        if len(A) == len(B)+1:
            # a0 x M y -> x M a0 y -> y M a0 x.
            bit = current.pop(pA)
            current.insert(pB-1,bit)
            operations.append(dict(kind='single_bit_move',slot=bit,old=pA,new=pB-1))
            xstart,ystart = pA,pB
            width = len(B)
            current[xstart:xstart+width],current[ystart:ystart+width] = \
                current[ystart:ystart+width],current[xstart:xstart+width]
            mismatched += 1
        elif len(B) == len(A)+1:
            # x M b0 y -> b0 x M y -> b0 y M x.
            bit = current.pop(pB)
            current.insert(pA,bit)
            operations.append(dict(kind='single_bit_move',slot=bit,old=pB,new=pA))
            xstart,ystart = pA+1,pB+1
            width = len(A)
            current[xstart:xstart+width],current[ystart:ystart+width] = \
                current[ystart:ystart+width],current[xstart:xstart+width]
            mismatched += 1
        else:
            require(len(A) == len(B), 'Unexpected chunk mismatch')
            xstart,ystart,width = pA,pB,len(A)
            current[xstart:xstart+width],current[ystart:ystart+width] = \
                current[ystart:ystart+width],current[xstart:xstart+width]
        operations.append(dict(kind='equal_width_chunk_swap',left=xstart,right=ystart,width=width))
        require(current == before[:pA]+B+gap+A+before[pB+len(B):],
                'Actual one-bit plus equal-width swap did not exchange unequal chunks')
        ordering[left],ordering[right] = ordering[right],ordering[left]
        chunk_swaps += 1
    desired = prefix+sum((chunks[t] for t in target),[])
    require(ordering == target and current == desired, 'Balanced positional layout failed')
    require(chunk_swaps <= D*len(widths)-1, 'Selection ordering exceeded swap bound')
    reverse = current[:]
    for op in reversed(operations):
        if op['kind'] == 'single_bit_move':
            reverse.insert(op['old'],reverse.pop(op['new']))
        else:
            a,b,w = op['left'],op['right'],op['width']
            reverse[a:a+w],reverse[b:b+w] = reverse[b:b+w],reverse[a:a+w]
    require(reverse == original, 'Inverse positional operations did not restore all named slots')
    rounds = []
    if prefix:
        rounds.append(dict(h=ell-1,individual=True,axes=[i for i,long in enumerate(long_axes) if long]))
    for j,width in enumerate(widths):
        for h in range(chunks[0,j][0][1],chunks[0,j][-1][1]-1,-1):
            rho = h-chunks[0,j][-1][1]
            group_start = len(prefix)+D*sum(widths[:j])
            group = current[group_start:group_start+D*width]
            selected = [group[i*width+width-1-rho] for i in range(D)]
            require(selected == [(i,h) for i in range(D)], 'A round selected the wrong named slots')
            rounds.append(dict(h=h,individual=False,axes=list(range(D)),chunk_width=width,offset=rho))
    require([r['h'] for r in rounds] == list(range(ell-1 if prefix else ell-2,-1,-1)),
            'Balanced round chronology skipped or reordered a level')
    return dict(original=original,physical=current,operations=operations,rounds=rounds,widths=widths,
                prefix_moves=len(prefix),chunk_swaps=chunk_swaps,mismatched_chunk_swaps=mismatched)


def chronology(control,ell,long_axes):
    positions = {slot:i for i,slot in enumerate(control['physical'])}
    bits = len(positions)
    # Exhaustive tiny addresses; larger shapes retain deterministic boundary
    # patterns because the symbolic slot schedule already covers all slots.
    addresses = range(1<<bits) if bits <= 8 else [0,(1<<bits)-1,1,1<<(bits-1),
                 sum(1<<i for i in range(0,bits,2)),sum(1<<i for i in range(1,bits,2))]
    checks = 0
    for address in addresses:
        value = {slot:(address>>pos)&1 for slot,pos in positions.items()}
        forward_done = [set() for _ in long_axes]
        a = [ell-1+long for long in long_axes]
        for round_ in control['rounds']:
            h = round_['h']
            for i in round_['axes']:
                require(forward_done[i] == set(range(h+1,a[i])), 'Earlier branch-bit set differs')
                lower = sum(value[i,v]<<v for v in range(h))
                axis_index = sum(value[i,v]<<v for v in range(a[i]))
                logical_lower = axis_index % (1<<h)
                require(lower == logical_lower < 1<<h, 'Descriptor changed a twiddle lower index')
                require(a[i]-1-h == len(forward_done[i]), 'Frequency-bit significance changed')
                forward_done[i].add(h)
                checks += 1
        reverse_done = [set() for _ in long_axes]
        for round_ in reversed(control['rounds']):
            h = round_['h']
            for i in round_['axes']:
                require(reverse_done[i] == set(range(h)), 'Inverse round did not recover lower slots first')
                lower = sum(value[i,v]<<v for v in range(h))
                branch = value[i,h]
                E = -(2*(1<<ell)//(1<<(h+1)))*branch*lower
                axis_index = sum(value[i,v]<<v for v in range(a[i]))
                reference_E = -2**(ell-h)*((axis_index>>h)&1)*(axis_index % (1<<h))
                require(E == reference_E, 'Reordered descriptor changed a synthetic twiddle exponent')
                reverse_done[i].add(h)
                checks += 1
        require(all(done == set(range(a[i])) for i,done in enumerate(forward_done)) and
                forward_done == reverse_done, 'A transform direction omitted an axis slot')
    return checks,len(addresses)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args()
    require(not args.output.exists(), 'Use a fresh output path')
    started = time.monotonic()
    cases = address_cases = chronological = equal_swaps = unequal_swaps = prefix = 0
    negative_old_prefix = 0
    samples = []
    for ell in range(2,21):
        for K in range(1,ell):
            for D in range(1,6):
                choices = (list(product((False,True),repeat=D)) if D <= 3 else
                    [tuple(False for _ in range(D)),tuple(True for _ in range(D)),
                     tuple(i%2 == 0 for i in range(D))])
                for long_axes in choices:
                    c = layout(ell,K,long_axes)
                    n,addresses = chronology(c,ell,long_axes)
                    chronological += n; address_cases += addresses; cases += 1
                    equal_swaps += c['chunk_swaps']; unequal_swaps += c['mismatched_chunk_swaps']
                    prefix += c['prefix_moves']
                    old_prefix = sum(long_axes)+D*((ell-1)%K)
                    if old_prefix > c['prefix_moves']:
                        negative_old_prefix += 1
                    if (ell,K,D,long_axes) in ((6,2,2,(True,False)),(9,3,3,(True,False,True))):
                        samples.append(dict(ell=ell,K=K,D=D,long_axes=long_axes,
                                            widths=c['widths'],physical_slots=c['physical'],
                                            old_prefix_slots=old_prefix,new_prefix_slots=c['prefix_moves'],
                                            equal_width_swaps=c['chunk_swaps'],
                                            one_bit_mismatch_moves=c['mismatched_chunk_swaps']))
    # Removing the O(dK) cost still leaves K=o(ell). Therefore
    # epsilon*c < 1-epsilon and the g2 margin is below a(1-epsilon).
    # Together g3<epsilon*a this gives the declared ceiling a/2.
    a = Q(3,10**9)
    old_ceiling = a/(2+a)
    new_ceiling = a/2
    require(new_ceiling-old_ceiling == a*a/(2*(2+a)), 'Scoped ceiling comparison failed')
    result = dict(status='PASS exact balanced named-slot/movement/chronology controls; analytic transfer review pending',
                  campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                  campaign_deadline='2026-10-08T08:25:21Z',generated_at=datetime.now(timezone.utc).isoformat(),
                  provenance=check_sources(args.upstream),
                  source_sha256={Path(__file__).name:hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
                  cases=cases,address_patterns=address_cases,exact_axis_round_chronology_checks=chronological,
                  completed_equal_width_swaps=equal_swaps,one_bit_unequal_width_moves=unequal_swaps,
                  long_extra_bit_prefix_moves=prefix,old_prefix_strictly_larger_cases=negative_old_prefix,
                  samples=samples,illustrative_exact_ceiling=dict(a=str(a),old=str(old_ceiling),
                    balanced=str(new_ceiling),strict_gain=str(new_ceiling-old_ceiling)),
                  elapsed_seconds=time.monotonic()-started,
                  scope='Exact symbolic layout and elementary operation inverse, exhaustive tiny addresses and deterministic large patterns; full transform/precision/compact-layer transfer is written separately; no promoted kappa or universal routing claim')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS balanced layout',cases,'shapes',chronological,'axis-round checks',unequal_swaps,'unequal-width moves',flush=True)


if __name__ == '__main__':
    main()
