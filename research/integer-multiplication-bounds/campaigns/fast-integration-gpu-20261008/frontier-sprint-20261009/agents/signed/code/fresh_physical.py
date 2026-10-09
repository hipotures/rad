#!/usr/bin/env python3
"""Fresh paid frame descent and chronological reclamation for signed DAGs.

RaD, prepared with OpenAI GPT-6.1 Sol assistance, Apache-2.0.
The admissible frame and compensated reuse conditions are inherited from
eumemic's paired_cube_physical.py, with icekylinx's signed construction,
general Clifford frames, and jamesyc's compensated birth-cut reuse.
No saved frame or reuse proposal is imported.
"""
from collections import defaultdict
import math


def construct(graph, witness, word, row, solve_matching, saving=0.00065):
    from paired_cube.frames import basis, perp, contained
    h, R = graph['h'], row['R']
    args = [None]+[None if a is None else [x+1 for x in a] for a in graph['args']]
    spans = [()]*len(args)
    for x in range(1, len(args)):
        spans[x] = (graph['inputs'][x-1],) if args[x] is None else \
                   basis(spans[args[x][0]]+spans[args[x][1]])
    roots = [dict(root, node=root['node']+1) for root in graph['roots']]
    ops = word['ops']
    full = basis(1 << i for i in range(h))
    initial = [()]*R
    for x, s in word['sources'].items():
        initial[s] = (graph['inputs'][int(x)-1],)
    gauges = {item['role']: perp(tuple(item['annihilator']), h) for item in word['selected']}
    for s, gauge in gauges.items():
        initial[s] = gauge
    caps = {}
    for root, s in zip(roots, word['rootroles']):
        caps[s] = spans[root['node']] if root['kind'] == 'center' else \
                  perp(basis(graph['inputs'][t] for t in root['targets']), h)
    frames = [perp(tuple(witness['annihilators'][x]), h) for _, _, x in ops]
    original = list(frames)
    timeline = defaultdict(list)
    for i, (a, b, _) in enumerate(ops):
        timeline[a].append(i); timeline[b].append(i)
    previous, following = {}, {}
    for s, chain in timeline.items():
        for k, i in enumerate(chain):
            previous[s, i] = chain[k-1] if k else None
            following[s, i] = chain[k+1] if k+1 < len(chain) else None
    def excess(rank):
        return rank*math.expm1(saving*math.log(3*h/rank)) if rank else 0.
    def cost(d, past, future):
        return sum(excess(d-p)+excess(f-d) for p, f in zip(past, future))
    improvements = []
    for sweep in range(6):
        changed = 0
        itinerary = range(len(ops)) if sweep%2 == 0 else reversed(range(len(ops)))
        for i in itinerary:
            a, b, x = ops[i]
            before = [initial[s] if previous[s, i] is None else frames[previous[s, i]] for s in (a,b)]
            after = [caps.get(s, full) if following[s, i] is None else frames[following[s, i]] for s in (a,b)]
            low = basis(spans[x]+before[0]+before[1])
            assert contained(low, frames[i])
            assert all(contained(frames[i], f) for f in after)
            past, future = list(map(len, before)), list(map(len, after))
            oldcost = cost(len(frames[i]), past, future)
            candidates = [low]
            current = low
            for vector in frames[i]:
                enlarged = basis(current+(vector,))
                if len(enlarged) > len(current):
                    current = enlarged; candidates.append(current)
            chosen = min(candidates, key=lambda f: (cost(len(f), past, future), len(f), f))
            if cost(len(chosen), past, future) < oldcost-1e-14:
                frames[i] = chosen; changed += 1
        improvements.append(changed)
        if not changed:
            break
    moved = [(i,list(frame)) for i, frame in enumerate(frames) if frame != original[i]]
    # The physical checker verifies nesting, value support and exact chronology.
    phase = sorted(word['phase1'])
    phase_set = set(phase)
    rest = [i for i in range(len(ops)) if i not in phase_set]
    position = {i: k for k, i in enumerate(phase+rest)}
    donors = sorted(s for s in timeline if s not in gauges and s not in caps)
    recipients = sorted(gauges, key=lambda s: (position[timeline[s][0]],s))
    group = defaultdict(list)
    for s in donors:
        group[frames[timeline[s][-1]]].append(s)
    eligibility = {}
    donor_index = {s: i for i, s in enumerate(donors)}
    for gauge in set(gauges.values()):
        eligible = [s for frame, slots in group.items() if contained(frame, gauge) for s in slots]
        eligibility[gauge] = sorted(eligible)
    adjacent = []
    for s in recipients:
        deadline = timeline[s][0]
        assert deadline not in phase_set
        adjacent.append([donor_index[d] for d in eligibility[gauges[s]]
                         if position[timeline[d][-1]] < position[deadline]])
    matched = solve_matching(adjacent, len(donors))
    pairs = [[donors[d], recipients[i], timeline[recipients[i]][0]]
             for i, d in enumerate(matched) if d >= 0]
    return moved, pairs, dict(frame_sweep_changes=improvements, moved_frames=len(moved),
                             candidate_donors=len(donors), candidate_recipients=len(recipients),
                             alias_eligible_arcs=sum(map(len, adjacent)), aliases=len(pairs),
                             frame_trial_saving=saving,
                             strategy='Monotone shrink only: exact spans plus previous frames, six alternating '
                                      'sweeps of complete neighboring transition cost; fresh maximum '
                                      'matching of eligible donors to late chronological recipients.')
