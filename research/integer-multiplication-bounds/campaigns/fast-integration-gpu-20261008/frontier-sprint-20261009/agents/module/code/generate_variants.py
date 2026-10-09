#!/usr/bin/env python3
"""Generate exact structural module alternatives from the pinned public input.

RaD, prepared with OpenAI GPT-6.1 Sol assistance. Apache-2.0.
The original signed cube constructor and positive module loader retain their
upstream Apache-2.0 notices; this script changes only task-owned JSON exports.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
SOURCE_HEAD = 'fd25adb7fbaa12ee761d02c733c54d1d2a7687ee'
TRIPLE_NAME = 'tmod_TB31_L1f8_5.9717259e-4.json'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, separators=(',', ':'))
        stream.write('\n')


def triple_supports(data):
    n = data['input_count']
    need(all(a == [0, 0] for a in data['args'][:n+1]), 'one-based input framing')
    support = [0]+[1 << i for i in range(n)]
    depth = [0]*(n+1)
    for x, (a, b) in enumerate(data['args'][n+1:], n+1):
        need(0 < a < x and 0 < b < x, 'acyclic positive triple gate')
        need(not support[a] & support[b], 'disjoint positive support')
        support.append(support[a] | support[b])
        depth.append(1+max(depth[a], depth[b]))
    return support, depth


def census(data):
    n = data['input_count']
    support, depth = triple_supports(data)
    groups = defaultdict(list)
    for node in range(n+1, len(support)):
        groups[support[node]].append(node)
    live = set()
    pending = list(data['roots'])
    while pending:
        x = pending.pop()
        if x in live:
            continue
        live.add(x)
        if x > n:
            pending.extend(data['args'][x])
    return dict(input_count=n, additions=len(data['args'])-n-1,
                live_additions=sum(x > n for x in live),
                duplicate_support_groups=sum(len(v) > 1 for v in groups.values()),
                duplicate_support_excess=sum(len(v)-1 for v in groups.values()),
                root_depth_histogram=dict(sorted(Counter(depth[r] for r in data['roots']).items())),
                depth_histogram=dict(sorted(Counter(depth[n+1:]).items())),
                support_size_histogram=dict(sorted(Counter(s.bit_count() for s in support[n+1:]).items())))


def balance_single_use(data):
    """One deterministic pass of genuine associative rotations, then prune.

    Only an original internal sum with one consumer and no output use is
    eligible. The deeper child is replaced by a differently grouped sum of
    the same three disjoint positive terms. A rotation is retained only when
    it strictly reduces depth at the parent. New equal supports are interned.
    """
    n = data['input_count']
    old_support, _ = triple_supports(data)
    uses = Counter(x for a in data['args'][n+1:] for x in a)
    uses.update(data['roots'])
    args = [[0, 0] for _ in range(n+1)]
    support = old_support[:n+1]
    depth = [0]*(n+1)
    intern = {s: x for x, s in enumerate(support) if x}
    remap = {x: x for x in range(n+1)}
    rotations = []

    def add(a, b):
        need(not support[a] & support[b], 'rotated disjoint supports')
        joined = support[a] | support[b]
        if joined not in intern:
            intern[joined] = len(args)
            args.append(sorted((a, b)))
            support.append(joined)
            depth.append(1+max(depth[a], depth[b]))
        return intern[joined]

    for x, (oa, ob) in enumerate(data['args'][n+1:], n+1):
        a, b = remap[oa], remap[ob]
        candidates = []
        original_depth = 1+max(depth[a], depth[b])
        for old_inner, inner, other in ((oa, a, b), (ob, b, a)):
            if old_inner <= n or uses[old_inner] != 1:
                continue
            c, d = args[inner]
            for outer, paired in ((c, d), (d, c)):
                new_depth = 1+max(depth[outer], 1+max(depth[paired], depth[other]))
                if new_depth < original_depth:
                    candidates.append((new_depth, support[outer], outer, paired, other, old_inner))
        if candidates:
            new_depth, _, outer, paired, other, old_inner = min(candidates)
            remap[x] = add(outer, add(paired, other))
            rotations.append(dict(original_parent=x, original_inner=old_inner,
                                  old_depth=original_depth, new_depth=depth[remap[x]],
                                  changed_intermediate_support=str(support[paired] | support[other])))
        else:
            remap[x] = add(a, b)
        need(support[remap[x]] == old_support[x], 'exact rotated node identity')
    roots = [remap[x] for x in data['roots']]
    live = set(range(n+1))
    pending = list(roots)
    while pending:
        x = pending.pop()
        if x in live:
            continue
        live.add(x)
        pending.extend(args[x])
    order = sorted(live)
    rename = {x: k for k, x in enumerate(order)}
    new = dict(data, args=[[0, 0] if x <= n else [rename[y] for y in args[x]] for x in order],
               roots=[rename[x] for x in roots])
    final_support, _ = triple_supports(new)
    need([old_support[x] for x in data['roots']] == [final_support[x] for x in new['roots']],
         'exact integer output identity, every coefficient is positive one')
    return new, dict(method='Single deterministic support-exact associativity pass, strict parent-depth reduction, '
                           'single-consumer/no-output-use inner sums only; equal support interning and dead-node pruning.',
                     rotations=rotations, before=census(data), after=census(new))


def local_identity(cfg, Graph):
    graph = Graph(3, local=cfg)
    graph.local_channels()
    vectors = [tuple(int(i == j) for i in range(8)) for j in range(8)]
    for (a, b), sign in zip(graph.a[8:], graph.signs[8:]):
        vectors.append(tuple(x+sign*y for x, y in zip(vectors[a], vectors[b])))
    outputs = {('F',): vectors[graph.F[(0, 1, 2)]]}
    outputs.update({('A', *key[1:]): vectors[node] for key, node in graph.A.items()})
    outputs.update({('G', *key[1:]): vectors[node] for key, node in graph.G.items()})
    pin = {str(key): value for key, value in sorted(outputs.items())}
    return outputs, dict(additions=len(graph.a)-8, signed_additions=sum(s < 0 for s in graph.signs),
                         exact_integer_output_vectors=pin,
                         graph_binding_sha256=sha256(json.dumps(dict(args=graph.a, signs=graph.signs),
                                                                separators=(',', ':')).encode()).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    need(not sys.flags.optimize, 'assertions must remain enabled')
    source = a.source.resolve()
    a.output.mkdir(parents=True, exist_ok=False)
    src = source/'references/paired-cube/sources'
    pins = json.loads((src/'SOURCE.json').read_text())['files']
    for name, digest in pins.items():
        need(sha256((src/name).read_bytes()).hexdigest() == digest, 'source pin '+name)
    sys.path.insert(0, str(source/'scripts'))
    from paired_cube.graph import Graph
    from paired_cube.modules import triple_module_from
    local = json.loads((src/'local_L1.json').read_text())
    triple = json.loads((src/TRIPLE_NAME).read_text())
    rotated, rotation = balance_single_use(triple)
    need(rotation['rotations'], 'rotation discriminator must change the graph')
    base_outputs, _ = local_identity(local, Graph)
    alternatives = dict(control=(local, triple),
                        all_edge=(dict(local, G=dict.fromkeys(local['G'], 'e')), triple),
                        all_long=(dict(local, G=dict.fromkeys(local['G'], 'l')), triple),
                        triple_balanced=(local, rotated))
    rows = {}
    for name, (cfg, tmod) in alternatives.items():
        out = a.output/name
        out.mkdir()
        write(out/'local.json', cfg)
        write(out/'triple.json', tmod)
        outputs, checks = local_identity(cfg, Graph)
        need(outputs == base_outputs, 'exact integer local outputs '+name)
        triple_module_from(out/'triple.json', 11)
        row = dict(local_checks=checks, triple_checks=census(tmod),
                   source_revision=SOURCE_HEAD,
                   input_substitution=dict(local='local.json', triple='triple.json'),
                   exported_pins={path.name:dict(sha256=sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size)
                                  for path in (out/'local.json', out/'triple.json')})
        if name == 'triple_balanced':
            row['transformation'] = rotation
        write(out/'module-checks.json', row)
        rows[name] = row
    write(a.output/'manifest.json', dict(status='MODULE_SCREEN_EXACT_INTEGER_INPUTS', source_revision=SOURCE_HEAD,
                                        source=str(source), source_input_hashes=pins,
                                        generated_utc=datetime.now(timezone.utc).isoformat(),
                                        generator_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                                        random_seed=None, variants=rows,
                                        generator_search='No TMOD or local optimizer shipped in scripts; explicit local '
                                                         'factorization choices and a bounded positive associativity '
                                                         'transform are reconstructed here.'))
    print(json.dumps({name:dict(local_gates=row['local_checks']['additions'],
                               triple_gates=row['triple_checks']['additions'],
                               rotations=len(row.get('transformation', {}).get('rotations', [])),
                               root_depths=row['triple_checks']['root_depth_histogram'])
                      for name, row in rows.items()}, indent=2))


if __name__ == '__main__':
    main()
