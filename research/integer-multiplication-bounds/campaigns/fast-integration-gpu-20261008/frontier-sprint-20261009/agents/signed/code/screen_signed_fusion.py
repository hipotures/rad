#!/usr/bin/env python3
"""Rebuild exact signed-output variants of PR161's paired-cube complex DAG.

RaD; prepared with OpenAI GPT-6.1 Sol assistance. Apache-2.0.
Uses icekylinx/eumemic paired_cube modules and finite checks (Apache-2.0),
eumemic's physical ledger, and RaD's separate exact integer adjoint checker.
Every changed DAG has a fresh deterministic maximum matching and new frames;
no frozen descended frames or compensated aliases are transplanted.
"""
import argparse
from collections import Counter, deque
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from hashlib import sha256
from datetime import datetime, timezone
import importlib.util
import json
import math
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode = True
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, separators=(',', ':'))
        stream.write('\n')


def hopcroft_karp(adj, nright):
    """Deterministic maximum cardinality matching; iterative augmenting paths."""
    nleft = len(adj)
    inf = 1 << 30
    left, right = [-1]*nleft, [-1]*nright
    while True:
        dist = [inf]*nleft
        queue = deque(i for i in range(nleft) if left[i] < 0)
        for i in queue:
            dist[i] = 0
        found = False
        while queue:
            i = queue.popleft()
            for j in adj[i]:
                matched = right[j]
                if matched < 0:
                    found = True
                elif dist[matched] == inf:
                    dist[matched] = dist[i]+1
                    queue.append(matched)
        if not found:
            return left
        cursor = [0]*nleft
        for first in range(nleft):
            if left[first] >= 0:
                continue
            stack = [first]
            while stack:
                i = stack[-1]
                if cursor[i] < len(adj[i]):
                    j = adj[i][cursor[i]]
                    cursor[i] += 1
                    matched = right[j]
                    if matched < 0:
                        vacant = j
                        for item in reversed(stack):
                            previous = left[item]
                            left[item], right[vacant] = vacant, item
                            vacant = previous
                        break
                    if dist[matched] == dist[i]+1:
                        stack.append(matched)
                else:
                    dist[i] = inf
                    stack.pop()


def matching(g):
    """Reconstruct compiler eligibility instead of reusing another DAG's arcs."""
    from paired_cube.frames import basis, perp, contained
    h, v = g['h'], g['v']
    args = [None]+[None if a is None else [x+1 for x in a] for a in g['args']]
    roots = [dict(r, node=r['node']+1) for r in g['roots']]
    n = len(args)
    spans = [()]*n
    for i, value in enumerate(g['inputs']):
        spans[i+1] = (value,)
    for x in range(v+1, n):
        a, b = args[x]
        spans[x] = basis(spans[a]+spans[b])
    rootann = [perp(spans[r['node']], h) if r['kind'] == 'center' else
               basis(g['inputs'][t] for t in r['targets']) for r in roots]
    active = set(range(1, v+1))
    todo = [r['node'] for r in roots]
    while todo:
        x = todo.pop()
        if x in active:
            continue
        active.add(x)
        if args[x]:
            todo.extend(args[x])
    successors, constraints = [[] for _ in args], [[] for _ in args]
    for x in sorted(active):
        if args[x]:
            for y in args[x]:
                successors[y].append(x)
    for r, ann in zip(roots, rootann):
        constraints[r['node']].extend(ann)
    preann, initial = [None]*n, [()]*n
    for x in sorted(active, reverse=True):
        preann[x] = basis(constraints[x]+[z for y in successors[x] for z in preann[y]])
        cover = 0
        for value in spans[x]:
            cover |= value
        initial[x] = perp(preann[x]+tuple(1 << j for j in range(h) if not cover >> j & 1), h)
        need(contained(spans[x], initial[x]), 'source support outside fresh matching frame')
    order = sorted(active, key=lambda x: (len(initial[x]), x))
    position = {x: i for i, x in enumerate(order)}
    uses, value, target, frame, code = [[] for _ in args], [], [], [], []
    for x in order:
        if args[x]:
            for j, y in enumerate(args[x]):
                uses[y].append(len(value)); value.append(y); target.append(x)
                frame.append(initial[x]); code.append(2*x+j)
    for j, r in enumerate(roots):
        x = r['node']
        uses[x].append(len(value)); value.append(x); target.append(n+j)
        frame.append(perp(rootann[j], h)); code.append((1 << 31)|j)
    donors = [x for x in order if args[x]]
    adjacent = []
    for x in donors:
        eligible = []
        for y in args[x]:
            for use in uses[y]:
                t = target[use]
                if t < n and position[t] <= position[x]:
                    continue
                if contained(initial[x], frame[use]):
                    eligible.append(use)
        adjacent.append(sorted(set(eligible)))
    solved = hopcroft_karp(adjacent, len(value))
    arcs = [[donors[i], code[u]] for i, u in enumerate(solved) if u >= 0]
    return arcs, dict(eligible_arcs=sum(map(len, adjacent)), donors=len(donors),
                      uses=len(value), matched=len(arcs), algorithm='deterministic iterative Hopcroft-Karp')


def merge_edge_pair(g, builder):
    """Fuse edge02 +/- edge12, leaving face2; signed contributions stay exact."""
    found, keep = {}, []
    for root in g['roots']:
        if root.get('channel') in ('edge02', 'edge12'):
            need(len(root['targets']) == 1, 'expected singleton edge use')
            found[tuple(root['targets']), root['channel']] = root
        else:
            keep.append(root)
    merged = []
    for target in sorted({tg for tg, _ in found}):
        first, second = (found[target, channel] for channel in ('edge02', 'edge12'))
        c0, c1 = Fraction(first['coefficients'][0]), Fraction(second['coefficients'][0])
        ratio = c1/c0
        need(ratio in (-1, 1), 'nonunit signed fusion')
        node = builder.add(first['node'], second['node'], int(ratio))
        merged.append(dict(node=node, targets=list(target), coefficients=[str(c0)],
                           kind='side', channel='edge02_edge12'))
    # All multi-target roots precede singleton roots; target caps remain nested.
    side = [r for r in keep if r['kind'] == 'side']+merged
    side.sort(key=lambda r: -len(r['targets']))
    centers = [r for r in keep if r['kind'] == 'center']
    return dict(g, roots=side+centers, args=builder.a, signs=builder.signs)


def moment(row, saving):
    return math.fsum(int(n)*int(r)*math.exp(saving*math.log(row['m']/int(r)))
                     for r, n in row['child_histogram'].items())/(row['m']*row['W_per_vertex'])


def numerical_root(row):
    lo, hi = 0., .1
    if moment(row, 0.) >= 1:
        return None
    for _ in range(75):
        middle = (lo+hi)/2
        if moment(row, middle) < 1:
            lo = middle
        else:
            hi = middle
    return lo


def finite_scalar_bound(row, physical):
    """Retain the source's full conservative expansion; this is not assembly."""
    h, v, R = row['h'], row['v'], row['R']
    m, Wlocal = physical['m'], physical['W_per_vertex']
    half = m//2
    vertices = 2**(m-1+(half-1)**2)*math.prod(2**(2*i)-1 for i in range(1, half))
    W = vertices*Wlocal
    local = 4*(row['c']+v)+10*v+4*h*v+4*h*h+8*h+8+2*h
    local += 8*R*v*(row['total_M_operations']+16)+32*v
    logical = 3*vertices*local+8*W+4*vertices*v+8*m*R*vertices
    router = 64*(m+1)**3*(logical+1)*(W+1)**2
    semantic_E = 64*(W+m+router+1)**3
    mass = vertices*physical['rank_per_vertex']
    charge = 2*router*W*W+8*mass+4*W+4+32*m
    need(charge < semantic_E, 'conservative expanded scalar charge exceeds semantic guard')
    return dict(local_expanded_group_upper=local, literal_core_operations=row['total_M_operations'],
                cleanup_operations=row['total_M_operations']+v,
                center_scatter_entries=h*v, original_X_group_upper=32*v,
                group_order_bits=vertices.bit_length(), global_logical_group_upper=str(logical),
                router_group_upper=str(router), literal_scalar_charge=str(charge),
                semantic_guard_E=str(semantic_E), scalar_guard_passed=True,
                scope='Unchanged inherited conservative finite-bridge expansion with this DAG counts, '
                      'ordinary centers, expanded old-value readouts, copies, K/endpoints, exact cleanup, '
                      'routing and three stages charged. Uniform recursion/ordinary leaves/analytic '
                      'assembly remain inherited or independent obligations; no final kappa claimed.')


def run_variant(task):
    tree, audit_file, name, runroot, fresh = task
    tree, audit_file, runroot = Path(tree), Path(audit_file), Path(runroot)
    out = runroot/name
    out.mkdir()
    started = time.monotonic()
    timings = {}
    sys.path.insert(0, str(tree/'scripts'))
    from paired_cube.graph import Graph
    from paired_cube.modules import restricted_triples_from, pair_module_from, all_but_one, merge_outputs
    from paired_cube.frames import compile_graph
    from paired_cube.gauges import select
    from paired_cube_physical import physical
    from paired_cube import verify as source_verifier
    print(name+': build DAG', flush=True)
    source = tree/'references/paired-cube/sources'
    pin = json.loads((source/'SOURCE.json').read_text())['files']
    for filename, digest in pin.items():
        need(sha256((source/filename).read_bytes()).hexdigest() == digest, 'input source hash mismatch')
    builder = Graph(11)
    graph = builder.finish(restricted_triples_from(source/'h20_g1.json.gz', [0,1,2,3,4,5,6,7,8,9,16]),
                           pair_module_from(source/'pmod_C35_5.483127e-4.json', 10), all_but_one(9))
    if name == 'e02_e12':
        graph = merge_edge_pair(graph, builder)
    else:
        graph = merge_outputs(graph, builder, name)
    graph['matching_frames'] = 'coordinate'
    graph['gauge_trial_saving'] = 0.00065
    binding = {key: graph[key] for key in ('inputs','labels','args','signs','roots','centers')}
    graph_hash = sha256(json.dumps(binding, separators=(',', ':')).encode()).hexdigest()
    if name == 'w02':
        frozen = json.loads((tree/'references/paired-cube/selected-module/SOURCE.json').read_text())
        need(graph_hash == frozen['graph_sha256'], 'unchanged control DAG differs from PR161')
    write(out/'graph.json', graph)
    timings['dag'] = time.monotonic()-started
    before = time.monotonic()
    print(name+': reconstruct matching and frames', flush=True)
    arcs, matchstats = matching(graph)
    baseline, witness = compile_graph(graph, arcs)
    write(out/'matching.json', dict(arcs=arcs, stats=matchstats))
    write(out/'frames.json', witness)
    write(out/'baseline.json', baseline)
    timings['matching_and_frames'] = time.monotonic()-before
    before = time.monotonic()
    selected, word = select(graph, baseline, witness)
    write(out/'selection.json', word)
    write(out/'selected-profile.json', selected)
    timings['gauges'] = time.monotonic()-before
    print(name+': verify all scalar coefficients and complete geometry', flush=True)
    before = time.monotonic()
    # The source checker has one certificate-specific final count assertion.
    # Generalize that comparison; every prior scalar/frame/lifetime check is kept.
    original = Path(source_verifier.__file__).read_text()
    old = "assert record['selected_roles']==len(seen)==2970 and birth==Counter({18:2970})"
    new = "assert record['selected_roles']==len(seen) and birth==Counter({int(k):c for k,c in record['selected_rank_histogram'].items()})"
    need(original.count(old) == 1, 'unexpected verifier source; exact adaptation unavailable')
    generalized = original.replace(old, new)
    namespace = dict(__name__='paired_cube.verify_general', __package__='paired_cube')
    exec(compile(generalized, str(tree/'scripts/paired_cube/verify.py')+'[count-generalized]', 'exec'), namespace)
    checks = namespace['verify'](graph, baseline, witness, word, selected)
    timings['finite_geometry_verify'] = time.monotonic()-before
    before = time.monotonic()
    print(name+': reconstruct literal paid physical profile', flush=True)
    moved, pairs, fresh_stats = [], [], {}
    if fresh:
        from fresh_physical import construct
        moved, pairs, fresh_stats = construct(graph, witness, word, selected, hopcroft_karp)
        write(out/'fresh-physical-inputs.json', dict(frames=moved, pairs=pairs, stats=fresh_stats))
    paid = physical(graph, witness, word, selected, moved, pairs)
    write(out/'physical-profile.json', paid)
    selected_children = {int(r): n for r, n in selected['child_histogram'].items() if int(r) and n}
    if not fresh:
        need(paid['child_histogram'] == selected_children, 'unaliased paid profile mismatch')
    timings['physical_recount_and_modular_controls'] = time.monotonic()-before
    before = time.monotonic()
    print(name+': independent exact integer dirty/cleanup audit', flush=True)
    spec = importlib.util.spec_from_file_location('rad_exact_adjoints', audit_file)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    events, mutations, cleanup, live, response = audit.prepare(graph, word, pairs, selected['R'])
    exact = audit.check(graph, events, mutations, cleanup, live)
    controls = {}
    for mutation in ('omitted_read','bad_sign','illegal_index','omit_cleanup'):
        try:
            audit.check(graph, events, mutations, cleanup, live, mutation=mutation)
        except (ValueError, KeyError) as error:
            controls[mutation] = str(error)
        else:
            raise ValueError('exact audit accepted mutation: '+mutation)
    exact.update(negative_controls=controls)
    write(out/'exact-integer-core.json', exact)
    timings['exact_integer_audit'] = time.monotonic()-before
    root = numerical_root(paid)
    result = dict(variant=name, status='EXACT_FINITE_LOCAL_FRESH_PHYSICAL' if fresh else 'EXACT_FINITE_LOCAL_UNALIASED', graph_binding_sha256=graph_hash,
                  source_head='d14e29157bc905be1ced0776dd893d0714013f3a',
                  source_input_hashes=pin, matching=matchstats, h=selected['h'], v=selected['v'],
                  c=selected['c'], q=selected['q'], R=selected['R'], W=paid['W_per_vertex'],
                  m=paid['m'], rank_mass=paid['rank_per_vertex'], deficit=paid['deficit_per_vertex'],
                  maxchild=max(int(r) for r in paid['child_histogram']),
                  selected_roles=selected['selected_roles'], selected_rank_histogram=selected['selected_rank_histogram'],
                  numerical_complex_root_discovery_only=root,
                  common_trial_H={str(s): moment(paid, s) for s in (0.0005885669,0.0006,0.00065)},
                  complete_children=paid['child_histogram'], finite_checks=checks, exact_integer_checks=exact,
                  fresh_physical_stats=fresh_stats, physical_R=paid['physical_R'],
                  scalar_charge=finite_scalar_bound(selected, paid), timings_seconds=timings,
                  wall_seconds=time.monotonic()-started, peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  workers=1, nested_library_threads=1, verifier_source_sha256=sha256(original.encode()).hexdigest(),
                  verifier_adaptation=dict(old=old,new=new),
                  comparison_scope='Common rebuilt deterministic matching and chronological gauge policy; '
                      'operation frames and aliases freshly solved when fresh_physical_stats is populated; '
                      'otherwise no descent or aliases. No frozen physical inputs transplanted. '
                      'Numerical moments are discovery only; '
                      'no accepted conditional exponent, no general all-size theorem.')
    write(out/'result.json', result)
    print(name+': complete root %.12g R %d W %d gauges %d wall %.3fs' %
          (root or 0, selected['R'], paid['W_per_vertex'], selected['selected_roles'], result['wall_seconds']), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree', type=Path, required=True)
    parser.add_argument('--exact-audit', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--variants', nargs='+', default=['w02','w12','s','e02_e12'])
    parser.add_argument('--fresh-physical', action='store_true')
    parser.add_argument('--manifest', type=Path, default=Path(__file__).resolve().parent.parent/'input-manifest.json')
    args = parser.parse_args()
    need(not sys.flags.optimize, 'assertion-disabled execution rejected')
    need(1 <= args.workers <= 4, 'worker count must be one through four')
    need(not args.output.exists(), 'run directory already exists; use a fresh attempt')
    manifest = json.loads(args.manifest.read_text())
    for item in manifest['inputs']:
        need(sha256((args.tree/item['path']).read_bytes()).hexdigest() == item['sha256'],
             'source fingerprint mismatch: '+item['path'])
    dependency = next(item for item in manifest['independent_dependencies'] if item['path'].endswith('exact_aliased_core.py'))
    need(sha256(args.exact_audit.read_bytes()).hexdigest() == dependency['sha256'], 'exact adjoint checker fingerprint mismatch')
    args.output.mkdir(parents=True)
    write(args.output/'protocol.json', dict(variants=args.variants, workers=args.workers,
          started_utc=datetime.now(timezone.utc).isoformat(),
          source_head='d14e29157bc905be1ced0776dd893d0714013f3a',
          driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
          exact_audit_sha256=sha256(args.exact_audit.read_bytes()).hexdigest(),
          python_version=sys.version, nested_library_threads=1,
          matching='fresh deterministic maximum matching; coordinate eligibility',
          physical='fresh descent and chronological aliases' if args.fresh_physical else 'fresh backward-intersection operation frames, zero aliases',
          gauge_trial_saving=0.00065))
    before = time.monotonic()
    tasks = [(str(args.tree.resolve()),str(args.exact_audit.resolve()),name,str(args.output.resolve()),args.fresh_physical)
             for name in args.variants]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(run_variant, tasks))
    write(args.output/'batch-result.json', dict(results=results, wall_seconds=time.monotonic()-before,
                                              workers=args.workers))


if __name__ == '__main__':
    main()
