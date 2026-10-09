#!/usr/bin/env python3
"""Exact all-Lagrangian pricing of one shared-helper canonical exchange.

Each of twelve scalar shears can choose its own actual common frame. The
three physical banks are retained throughout, with every source, inter-gate,
sink, helper and monomial-gauge interface explicitly included. This screens
a named scalar chronology, not arbitrary helper circuits.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time

import one_helper_clifford_chronology as control


CONTROL_SHA = 'd9c1935951bfe2664fb2bff8f0cc250cd18f239b5be6b91624af8ff15c015474'
general = control.general
wrappers = control.wrappers


def helper_word(order):
    shears = ((0,1,1),(1,0,-1),(0,1,1)) if order == 'XYX' else ((1,0,-1),(0,1,1),(1,0,-1))
    word = []
    for target, source, c in shears:
        word += [(target,2,-c),(2,source,1),(target,2,c),(2,source,-1)]
    if control.scalar_matrix(word)[0] != [[0,1,0],[-1,0,0],[0,0,1]]:
        raise AssertionError('helper commutator word is not the required signed exchange')
    return tuple(word)


def grouped(word):
    result = []
    for event in word:
        pair = tuple(sorted(event[:2]))
        if result and result[-1][0] == pair:
            result[-1][1].append(event)
        else:
            result.append((pair,[event]))
    return result


def optimize(n, source, sink, word):
    """Dynamic program with exact two-frame state and all terminal ports.

    At a star interaction, two banks have the most recent common frame P;
    the other has Q. On switching pairs to a common frame R, precisely the
    old shared helper and the other data bank move, costing d(P,R)+d(Q,R).
    The untouched bank remains at P. Consecutive identical pairs can use one
    frame by the metric triangle inequality, without changing the minimum.
    """
    labels = general.all_lagrangians(n)
    count = len(labels)
    index = {L:i for i,L in enumerate(labels)}
    D = [[control.distance(A,B,n) for B in labels] for A in labels]
    S = [index[general.inverse_Z_labels(w,n)] for w in source]
    T = [index[general.inverse_Z_labels(w,n)] for w in sink]
    blocks = grouped(word)
    if any(2 not in pair for pair,_ in blocks):
        raise ValueError('this state reduction requires helper-star interactions')
    INF = 10**9
    pair = blocks[0][0]
    other = next(j for j in range(3) if j not in pair)
    dp = [[INF]*count for _ in labels]
    for R in range(count):
        dp[R][S[other]] = D[S[pair[0]]][R]+D[S[pair[1]]][R]
    parents = []
    relaxations = 0
    for next_pair,_ in blocks[1:]:
        if next_pair == pair or len(set(next_pair)&set(pair)) != 1:
            raise AssertionError('grouped helper-star state invariant failed')
        updated = [[INF]*count for _ in labels]
        parent = [[-1]*count for _ in labels]
        for P,row in enumerate(dp):
            finite = [(Q,cost) for Q,cost in enumerate(row) if cost != INF]
            for R in range(count):
                best, bestQ = INF, -1
                for Q,cost in finite:
                    value = cost+D[Q][R]
                    relaxations += 1
                    if value < best:
                        best,bestQ = value,Q
                if bestQ != -1:
                    updated[R][P] = best+D[P][R]
                    parent[R][P] = bestQ
        dp = updated
        parents.append(parent)
        pair = next_pair
    other = next(j for j in range(3) if j not in pair)
    minimum, final = INF, None
    for P,row in enumerate(dp):
        terminal = D[P][T[pair[0]]]+D[P][T[pair[1]]]
        for Q,value in enumerate(row):
            total = value+terminal+D[Q][T[other]]
            if total < minimum:
                minimum,final = total,(P,Q)
    P,Q = final
    path = [P]
    for parent in reversed(parents):
        oldQ = parent[P][Q]
        if oldQ == -1:
            raise AssertionError('optimal frame path has no predecessor')
        P,Q = Q,oldQ
        path.append(P)
    path.reverse()
    if Q != S[next(j for j in range(3) if j not in blocks[0][0])]:
        raise AssertionError('initial off-pair endpoint was not retained')
    return dict(n=n, lagrangians=count, minimum=minimum, path=[labels[j] for j in path],
                groups=blocks, relaxations=relaxations,
                metric_table_sha256=sha256(json.dumps(D).encode()).hexdigest(),
                source_frame_labels=[labels[j] for j in S], sink_frame_labels=[labels[j] for j in T])


def compile_component(n, source, sink, optimum):
    active = [list(w) for w in source]
    events, interfaces, ledger = [], [], []
    actual_entries = 0

    def move(bank, target):
        nonlocal actual_entries
        word = general.inverse_word(active[bank])+list(target)
        normal = general.compile_word(word,n)
        r = normal['selected_rank_per_column']
        expected_r = control.distance(general.inverse_Z_labels(active[bank],n),
                                      general.inverse_Z_labels(target,n),n)
        if r != expected_r:
            raise AssertionError('actual interface rank disagrees with priced metric')
        for x in range(1 << n):
            column,grid = general.literal_column(word,n,x)
            for y in range(1 << n):
                if column[y] != tuple(v << (grid-r) for v in general.exact.reconstructed_entry(normal,y,x)):
                    raise AssertionError('chosen actual interface matrix differs from compiled normal form')
                actual_entries += 1
        plan = wrappers.wrapper_plan(normal,1)
        events.append(('frame',bank,plan))
        interfaces.append(dict(bank=bank,rank=r,source_word=active[bank],target_word=list(target),
                               normal_form=normal))
        ledger.append(r)
        active[bank] = list(target)

    for (pair,scalars),L in zip(optimum['groups'],optimum['path']):
        common = general.frame_word(L,n)['actual_word']
        for bank in pair:
            move(bank,common)
        for scalar in scalars:
            events.append(('scalar',*scalar))
    for bank,target in enumerate(sink):
        move(bank,target)
    if sum(ledger) != optimum['minimum']:
        raise AssertionError('complete physical event ledger differs from dynamic-program minimum')
    return events, interfaces, actual_entries


def execute(events, raw, initial_grids=None, inverse=False):
    banks = [[row for row in bank] for bank in raw]
    grids = [0]*3 if initial_grids is None else list(initial_grids)
    for event in (reversed(events) if inverse else events):
        if event[0] == 'frame':
            _,bank,plan = event
            banks[bank],extra = wrappers.execute(plan,banks[bank],inverse=inverse)
            grids[bank] += extra
        else:
            _,target,source,c = event
            common = max(grids[target],grids[source])
            for bank in (target,source):
                banks[bank] = control.regrid(banks[bank],grids[bank],common)
                grids[bank] = common
            c *= -1 if inverse else 1
            banks[target] = [tuple(a+c*b for a,b in zip(x,y))
                             for x,y in zip(banks[target],banks[source])]
    return banks,grids


def probe(task):
    n,U,order = task
    word = helper_word(order)
    source,sink = control.ports(U,n)
    optimum = optimize(n,source,sink,word)
    events,interfaces,entries = compile_component(n,source,sink,optimum)
    origins = []
    for bank in range(3):
        for address in range(1 << n):
            raw = [[(0,0,0,0)]*(1 << n) for _ in range(3)]
            raw[bank][address] = (1,2,-3,5)
            origins.append(raw)
    origins.append([[wrappers.routes.payload((1 << n)*bank+j) for j in range(1 << n)] for bank in range(3)])
    forward = backward = 0
    for raw in origins:
        actual,grids = execute(events,raw)
        X,gx = control.C_reference(sink[0],raw[1],n)
        shifted = wrappers.routes.scatter(raw[0],lambda a:wrappers.replace_column(
            a,wrappers.column_vector(a,n,1,0)^U,n,1,0))
        Y,gy = control.C_reference(sink[0],shifted,n)
        Y = [tuple(-v for v in row) for row in Y]
        Z,gz = control.C_reference(sink[0],raw[2],n)
        for bank,grid,expected,eg in zip(actual,grids,(X,Y,Z),(gx,gy,gz)):
            control.compare(bank,grid,expected,eg)
            forward += 4*(1 << n)
        back,backgrids = execute(events,actual,grids,inverse=True)
        for bank,grid,original in zip(back,backgrids,raw):
            control.compare(bank,grid,original,0)
            backward += 4*(1 << n)
    if control.scalar_matrix(word[:-1])[0] == control.scalar_matrix(word)[0]:
        raise AssertionError('omitted final scalar cleanup negative did not discriminate')
    capacity = 3*n
    return dict(n=n,U=U,columns=1,shear_order=order,complete_stock=3,capacity=capacity,
                exact_minimum_rank=optimum['minimum'],deficit=capacity-optimum['minimum'],
                full_Lagrangian_candidates=optimum['lagrangians'],scalar_gates=len(word),
                grouped_interactions=len(optimum['groups']),exact_metric_relaxations=optimum['relaxations'],
                metric_table_sha256=optimum['metric_table_sha256'],
                chosen_common_frame_labels=[list(L) for L in optimum['path']],
                scalar_word=[list(g) for g in word],actual_interface_word=interfaces,
                paid_interface_rank_profile={str(r):sum(i['rank']==r for i in interfaces)
                                             for r in sorted({i['rank'] for i in interfaces}) if r},
                helper_paid_path=[i['rank'] for i in interfaces if i['bank']==2],
                exact_interface_entries=entries,complete_physical_origin_cases=len(origins),
                forward_fields=forward,inverse_fields=backward,
                helper_restoration='Exact raw C_full*z on the complete arbitrary initial helper payload.',
                no_truncation=True,missing_scalar_cleanup_negative=True,
                scope='Exact finite optimum for this twelve-shear shared-helper chronology over all Lagrangian frames. No universal helper, simultaneous mixer, nonunit or nonlinear obstruction.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--bounded',action='store_true')
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('positive worker count required')
    files = [Path(__file__),Path(control.__file__),Path(general.__file__),Path(general.exact.__file__),
             Path(general.exact.reference.__file__),Path(wrappers.__file__),Path(wrappers.routes.__file__)]
    before = {p.name:sha256(p.read_bytes()).hexdigest() for p in files}
    if before[Path(control.__file__).name] != CONTROL_SHA:
        raise AssertionError('pinned shared-helper reference changed')
    started = time.monotonic()
    utc = datetime.now(timezone.utc).isoformat()
    tasks = [(2,1,'XYX')] if args.bounded else [(3,U,order) for U in (1,7) for order in ('XYX','YXY')]
    if args.workers == 1:
        cases = [probe(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(probe,tasks))
    if before != {p.name:sha256(p.read_bytes()).hexdigest() for p in files}:
        raise AssertionError('effective source changed during run')
    certificate = dict(status='PASS',started_utc=utc,completed_utc=datetime.now(timezone.utc).isoformat(),
                       workers=args.workers,bounded=args.bounded,effective_sources=before,cases=cases,
                       seconds=time.monotonic()-started,
                       scope='Whole named three-bank, twelve-shear canonical signed exchange; exact finite all-Lagrangian pricing and complete dirty physical operators. Native fixed-tape contracts and different chronologies remain separate.')
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(certificate,indent=2)+'\n')
    print(json.dumps(dict(status='PASS',cases=len(cases),minima=[c['exact_minimum_rank'] for c in cases],
                          capacities=[c['capacity'] for c in cases],
                          fields=sum(c['forward_fields']+c['inverse_fields'] for c in cases),
                          seconds=certificate['seconds'])),flush=True)


if __name__ == '__main__':
    main()
