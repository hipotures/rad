#!/usr/bin/env python3
"""Three bounded actual binary experiments on the current pinned PR168 graph.

Endpoint continuation and transitive unequal-frame joins/meets retain the
actual public physical word, gauges, aliases and compensated read deadlines.
The third-channel experiment builds a new graph and carrier/frame chronology:
face0 terms are added into the edge12 two-target roots, preserving the receiver
pair used by each source-register partner delivery. Every added role is paid.
No source IDs, frame ranks or histograms from an older word are transplanted.

Prepared for RaD with OpenAI assistance. The transitive closure algorithm is
adapted from this sprint's physical_closure.py; source170 supplies exact frame
algebra, complete F2 replay and supplier moments. All source credits persist.
"""
import argparse
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import random
import resource
import sys
import time

sys.dont_write_bytecode = True
from bit_current_control import HEAD, METHOD_HEAD, need, sha, read, modules, source_pins


def encoded(hist):
    return {str(r): n for r, n in sorted(hist.items()) if r and n}


def physical_experiment(lifetime, physical, control):
    """Initialize the exact frame search on the public late-copy literal word.

    The public physical checker first checks the actual opcode/frame/read/alias
    obligations. The virtual baseline checker's ordinary chains do not model
    late copies, so its run() is not substituted as a physical certificate.
    """
    c = physical.loaded(control / 'physical-exports', control / 'logical-exports')
    verified = physical.physical(c)
    expected = read(control / 'receipt.json')['physical_profile']
    need(json.loads(json.dumps(verified)) == expected, 'regenerated physical control profile')
    e = lifetime.Experiment.__new__(lifetime.Experiment)
    e.base, e.p = control / 'physical-exports', 12
    e.c = c
    e.baseline_checks = verified['checks']
    e.target_histogram = Counter({int(r): n for r, n in verified['target_data_histogram'].items()})
    e.source_histogram = Counter({int(r): n for r, n in verified['source_data_histogram'].items()})
    e.g, e.w, e.record = c.g, c.w, c.prof
    e.h, e.v, e.R = c.h, c.v, c.prof['R']
    e.T = lifetime.Frames(c)
    e.ops = [tuple(o) for o in e.w['ops']]
    e.N = len(e.ops)
    e.base_frames = [c.nf[x] for _, _, x in e.ops]
    e.frames = list(e.w['op_frame'])
    e.sources = {int(x): s for x, s in e.w['sources'].items()}
    e.gauges = {z['role']: z for z in e.w['gauges']}
    e.start = [e.T.zero] * e.R
    for x, s in e.sources.items():
        e.start[s] = e.w['source_frame'][x]
    for s, z in e.gauges.items():
        e.start[s] = z['frame']
    e.role_ops = defaultdict(list)
    for i, (a, b, _) in enumerate(e.ops):
        e.role_ops[a].append(i)
        e.role_ops[b].append(i)
    e.rootframe, e.rootkind = {}, {}
    for j, (r, s) in enumerate(zip(e.g['roots'], e.w['rootroles'])):
        need(s not in e.rootframe, 'unique physical root roles')
        e.rootframe[s] = c.rf[j]
        e.rootkind[s] = r['kind']
    e.pairs, e.donors, e.merge, e.deadline = [], {}, {}, {}
    phase = set(e.w['phase1'])
    e.order = sorted(phase) + [i for i in range(e.N) if i not in phase]
    e.position = {i: t for t, i in enumerate(e.order)}
    e.build_edges()
    trial = 0.000655401120
    e.cost = [r * math.expm1(trial * math.log(3 * e.h / r)) if r else 0.
              for r in range(e.h + 1)]
    e.spans = list(e.w['source_frame'])
    for a, b in e.g['args'][e.v:]:
        e.spans.append(e.T.join(e.spans[a], e.spans[b]))
    e.node_spans = [e.spans[x] for _, _, x in e.ops]
    e.check()
    pairs = read(control / 'receipt.json')['physical_pairs_with_op_deadlines']
    e.set_pairs(pairs)
    got = e.profile()
    for key in ('R', 'physical_R', 'W_per_vertex', 'rank_per_vertex', 'deficit_per_vertex',
                'changed_operation_frames', 'pairs', 'local_histogram', 'source_data_histogram',
                'target_data_histogram', 'physical_gauge_histogram', 'child_histogram'):
        need(got[key] == expected[key], 'physical initialization recount ' + key)
    return e


def global_bounds(e):
    low = [e.T.zero] * e.N
    high = [e.w['full_frame']] * e.N
    for i in range(e.N):
        need(all(e.edges[k][0] < i for k in e.inc[i]), 'chronological incoming boundary')
        low[i] = e.T.join_all([e.node_spans[i]] + [
            low[a] if a >= 0 else e.F(a) for k in e.inc[i] for a, _ in [e.edges[k]]])
    for i in reversed(range(e.N)):
        need(all(b < 0 or b > i for k in e.out[i] for _, b in [e.edges[k]]),
             'chronological outgoing boundary')
        high[i] = e.T.meet_all([
            high[b] if b >= 0 else e.F(b) for k in e.out[i] for _, b in [e.edges[k]]])
    need(all(e.T.sub(a, f) and e.T.sub(f, b) for a, f, b in zip(low, e.frames, high)),
         'transitive endpoints contain current actual frames')
    return low, high


def closure_proposal(e, low, high, seed, direction, max_nodes):
    """Propagate only the nesting violations, with independent exact G gates."""
    goal = high[seed] if direction == 'raise' else low[seed]
    if goal == e.frames[seed]:
        return None, 'at_endpoint'
    changed, queue = {seed: goal}, deque([seed])
    while queue:
        i = queue.popleft()
        f = changed[i]
        ks = e.out[i] if direction == 'raise' else e.inc[i]
        for k in ks:
            a, b = e.edges[k]
            neighbor = b if direction == 'raise' else a
            old = changed.get(neighbor, e.F(neighbor))
            fits = e.T.sub(f, old) if direction == 'raise' else e.T.sub(old, f)
            if fits:
                continue
            need(neighbor >= 0, 'closure crosses fixed source, gauge or root boundary')
            new = e.T.join(old, f) if direction == 'raise' else e.T.meet(old, f)
            need(e.T.sub(low[neighbor], new) and e.T.sub(new, high[neighbor]),
                 'closure leaves transitive interval')
            changed[neighbor] = new
            queue.append(neighbor)
        if len(changed) > max_nodes:
            return None, 'size_bound'
    if any(not e.T.nondeg(f) for f in changed.values()):
        return dict(seed=seed, direction=direction,
                    degenerate_spaces=[e.T.record(f) for f in sorted(set(changed.values())) if not e.T.nondeg(f)]), 'degenerate'
    affected = set(k for i in changed for k in e.inc[i] + e.out[i])
    frame = lambda i: changed.get(i, e.F(i))
    need(all(e.T.sub(e.node_spans[i], f) for i, f in changed.items()), 'closure retains all value spaces')
    need(all(e.T.sub(frame(a), frame(b)) for k in affected for a, b in [e.edges[k]]),
         'all affected actual edges remain nested')
    old = math.fsum(e.cost[e.T.dim(e.F(b)) - e.T.dim(e.F(a))]
                    for k in affected for a, b in [e.edges[k]])
    new = math.fsum(e.cost[e.T.dim(frame(b)) - e.T.dim(frame(a))]
                    for k in affected for a, b in [e.edges[k]])
    if new >= old - 1e-12:
        return None, 'no_gain'
    return dict(seed=seed, direction=direction, frames=sorted(changed.items()),
                affected_edge_occurrences=len(affected), delta_excess_local=new-old), 'accepted'


def closure_batch(e, seed, seed_limit, max_nodes):
    low, high = global_bounds(e)
    rng = random.Random(seed)
    moves, obstruction, summaries = [], [], []
    for direction in ('raise', 'lower'):
        seeds = list(range(e.N))
        rng.shuffle(seeds)
        seeds.sort(key=lambda i: -(e.T.dim(high[i])-e.T.dim(e.frames[i]) if direction == 'raise'
                                  else e.T.dim(e.frames[i])-e.T.dim(low[i])))
        counts = Counter()
        for i in seeds[:seed_limit]:
            plan, status = closure_proposal(e, low, high, i, direction, max_nodes)
            counts[status] += 1
            if status == 'accepted':
                for j, f in plan['frames']:
                    e.frames[j] = f
                moves.append(plan)
            elif status == 'degenerate' and len(obstruction) < 8:
                obstruction.append(plan)
        e.check()
        summary = dict(direction=direction, seeds=min(seed_limit, e.N), counts=dict(counts),
                       root=e.profile()['numerical_root'])
        summaries.append(summary)
        print(json.dumps(summary), flush=True)
    return dict(passes=summaries, accepted=len(moves), moves=moves,
                exact_degenerate_examples=obstruction)


def third_fusion(gen):
    """Fuse face0 into edge12 at the existing partner receiver-pair caps."""
    pair = read(gen.HERE / 'data' / gen.MODULES[12])
    b = gen.BitGraph(12)
    g = b.finish(pair, gen.nested_prefix(10), merge=True, l1=True)
    need(gen.check_decoder(g) == 0, 'current unfurther-fused decoder')
    face = [r for r in g['roots'] if r.get('channel') == 'face0']
    targets = {tuple(r['targets']): r for r in face}
    roots, count = [], 0
    for r in g['roots']:
        if r.get('channel') == 'face0':
            continue
        if r.get('channel') == 'edge12':
            t = set(r['targets'])
            containing = [f for ts, f in targets.items() if t < set(ts)]
            need(len(containing) == 1 and len(t) == 2, 'unique face0 over the receiver pair')
            f = containing[0]
            need(not b.s[f['node']] & b.s[r['node']], 'third fusion inputs support-disjoint')
            node = b.add(f['node'], r['node'])
            r = dict(r, node=node, channel='face0-edge12')
            count += 1
        roots.append(r)
    new = dict(g, args=b.a, roots=roots)
    need(count == 880, 'every edge12 receiver pair merged')
    need(gen.check_decoder(new) == 0, 'complete third-fusion decoder')
    need(new['partner_mix'] == g['partner_mix'], 'source partner mixer retained')
    return new, dict(old_roots=len(g['roots']), roots=len(roots), merged_receiver_pairs=count,
                     removed_face0_roots=len(face), new_additions=len(new['args'])-len(g['args']),
                     delivery_policy='Same two-target edge12 receiver pairs; fresh chronology indices.')


def main():
    need(not sys.flags.optimize, 'assertions enabled')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--source170', type=Path, required=True)
    ap.add_argument('--control', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--variant', choices=['endpoints', 'transitive', 'third-fusion'], required=True)
    ap.add_argument('--seed', type=int, default=20261009)
    ap.add_argument('--seed-limit', type=int, default=8000)
    ap.add_argument('--max-nodes', type=int, default=128)
    args = ap.parse_args()
    src, method, control = args.source.resolve(), args.source170.resolve(), args.control.resolve()
    output = args.output.resolve()
    need(not output.exists(), 'fresh attempt required')
    output.mkdir(parents=True)
    started = time.monotonic()
    protocol = dict(source_head=HEAD, method_head=METHOD_HEAD, variant=args.variant, seed=args.seed,
                    max_nodes=args.max_nodes, seed_limit=args.seed_limit, endpoint_rounds=4,
                    started_utc=datetime.now(timezone.utc).isoformat(), workers=1, numerical_library_threads=1,
                    source_files=source_pins(src, method),
                    code_sha256={p.name: sha(p) for p in [Path(__file__), Path(__file__).with_name('bit_current_control.py')]},
                    control_receipt_sha256=sha(control / 'receipt.json'),
                    inherited_closure_method_sha256=sha(Path(__file__).parents[2] / 'placement/code/physical_closure.py'),
                    scope='Actual regenerated public word or fresh third-fusion DAG; paid full histogram.')
    (output / 'protocol.json').write_text(json.dumps(protocol, indent=2, sort_keys=True) + '\n')
    gen, physical, lifetime, params = modules(src, method)
    mechanism = {}
    if args.variant == 'third-fusion':
        graph, mechanism = third_fusion(gen)
        profile, witness = gen.compile_word(graph, frozen=None, plain_k=8)
        gauges, internal, target, word = gen.select_gauges(graph, profile, witness)
        row = gen.profile(profile, gauges, internal, target)
        exports = gen.export(12, graph, profile, witness, word, row)
        exports['profile'] = row
        export = output / 'exports'
        export.mkdir()
        for name, data in exports.items():
            (export / (name + '_p12.json')).write_text(gen.dumps(data))
        (output / 'arcs.json').write_text(gen.dumps(exports['word']['arcs']))
        e = lifetime.Experiment(export, 12, alpha=.000655401120, quiet=True)
        e.optimize(rounds=4, seed=args.seed)
        e.match_pairs(gauge_rank=21)
        e.optimize(rounds=4, seed=args.seed+1)
    else:
        e = physical_experiment(lifetime, physical, control)
        initial = e.profile()
        if args.variant == 'endpoints':
            e.optimize(rounds=4, seed=args.seed)
        else:
            mechanism = closure_batch(e, args.seed, args.seed_limit, args.max_nodes)
        mechanism['initial_profile'] = initial
    accepted = e.save(output / 'selected', replay=True)
    native = params.select_supplier(params.counts(accepted), bit=True)
    atom = params.choose_atom(native['saving'])
    result = dict(status='PASS_SOURCE_BOUND_FINITE_DISCOVERY', variant=args.variant, protocol=protocol,
                  mechanism=mechanism, profile=accepted, native_moment=native, paid_atom=atom,
                  plan_sha256=sha(output / 'selected/frames.json'), profile_sha256=sha(output / 'selected/profile.json'),
                  wall_seconds=time.monotonic()-started, peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  exclusions=['independent full reflected physical event replay', 'exact new-frame prime presentations',
                              'complete same-source final multiplication assembly'])
    (output / 'result.json').write_text(json.dumps(params.js(result), indent=2, sort_keys=True) + '\n')
    (output / 'moment.json').write_text(json.dumps(params.js(native), indent=2, sort_keys=True) + '\n')
    print(json.dumps(dict(status=result['status'], variant=args.variant, seconds=result['wall_seconds'],
                         R=accepted['physical_R'], W=accepted['W_per_vertex'], pairs=accepted['pairs'],
                         coarse=str(native['saving']), ordinary=str(atom['effective_saving']),
                         changed_frames=accepted['changed_operation_frames'])), flush=True)


if __name__ == '__main__':
    main()
