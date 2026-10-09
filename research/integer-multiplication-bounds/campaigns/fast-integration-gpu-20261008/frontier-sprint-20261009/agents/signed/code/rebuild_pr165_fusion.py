#!/usr/bin/env python3
"""Reconstruct PR165's selected complex fusion and extended carrier closure.

RaD; OpenAI GPT-6.1 Sol assistance. Apache-2.0. The module builders and
closure/gauge compiler are inherited from the pinned PR165/PR162 sources.
This regenerates the finite selected construction from module sources and
saved carrier choices; it does not regenerate the historical carrier search.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode = True


def need(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--export', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    need(not sys.flags.optimize, 'Run without -O: inherited finite assertions are required')
    start = time.monotonic()
    protocol = json.loads((a.export/'protocol.json').read_text())
    for name, pin in protocol['input_pins'].items():
        need(sha256((a.export/name).read_bytes()).hexdigest() == pin['sha256'], 'input pin: '+name)
    src = a.source/'references/paired-cube/sources'
    source_pins = json.loads((src/'SOURCE.json').read_text())['files']
    for name, digest in source_pins.items():
        need(sha256((src/name).read_bytes()).hexdigest() == digest, 'module pin: '+name)
    sys.path.insert(0, str(a.source/'scripts'))
    from paired_cube.graph import Graph
    from paired_cube.modules import restricted_triples_from, pair_module_from, all_but_one
    from paired_cube.gauges import select
    builder = Graph(11)
    graph = builder.finish(restricted_triples_from(src/'h20_g1.json.gz', [0,1,2,3,4,5,6,7,8,9,16]),
                           pair_module_from(src/'pmod_C35_5.483127e-4.json', 10), all_but_one(9))
    initial_nodes = len(graph['args'])
    selected = json.loads((a.export/'graph.json').read_text())
    need(graph['args'] == selected['args'][:initial_nodes], 'unfused scalar producer prefix')
    fusion = ('face2', 'edge02', 'edge12')
    centers = [root for root in graph['roots'] if root['kind'] == 'center']
    roots = []
    for cube in range(graph['v']//8):
        local = [root for root in graph['roots'] if root['kind'] == 'side' and root['targets'][0]//8 == cube]
        broad = [root for root in local if root['channel'] not in fusion]
        channel_order = {'disjoint':0,'face0':1,'face1':2,'edge01':3}
        roots.extend(sorted(broad, key=lambda root: (-len(root['targets']), tuple(root['targets']),
                                                     channel_order[root['channel']])))
        terms = {(root['targets'][0], root['channel']): (root['node'], Fraction(root['coefficients'][0]))
                 for root in local if root['channel'] in fusion}
        for target in range(8*cube, 8*cube+8):
            parts = [terms[target, channel] for channel in fusion]
            need({abs(c) for node,c in parts} == {Fraction(1,2)}, 'fusion coefficient contract')
            positive = [node for node,c in parts if c > 0]
            negative = [node for node,c in parts if c < 0]
            need(bool(positive), 'positive anchor')
            node = positive[0]
            for operand in positive[1:]:
                node = builder.add(node, operand)
            for operand in negative:
                node = builder.add(node, operand, -1)
            roots.append(dict(node=node, targets=[target], coefficients=['1/2'], kind='side',
                              channel='fused:face2,edge02,edge12'))
    graph['roots'] = roots+centers
    graph['args'], graph['signs'] = builder.a, builder.signs
    graph['counts'].update(signed_additions=sum(s < 0 for s in builder.signs),
                           side_root_uses=len(roots), new_fusion_additions=2*graph['v'])
    graph['matching_frames'] = 'coordinate'
    binding_keys = ('inputs','labels','args','signs','roots','centers')
    binding = json.loads(json.dumps({key:graph[key] for key in binding_keys}))
    mismatches = {key: next((i for i,(x,y) in enumerate(zip(binding[key], selected[key])) if x != y),
                            'length '+str(len(binding[key]))+'/'+str(len(selected[key])))
                  for key in binding_keys if binding[key] != selected[key]}
    need(not mismatches, 'complete reconstructed fusion graph: '+str(mismatches))
    need(graph['counts'] == selected['counts'], 'actual fusion operation inventory')
    witness_saved = json.loads((a.export/'frames.json').read_text())
    closure_path = a.source/'research/paired-cube-plateau-162/references/pr162/cxlinks.py'
    spec = importlib.util.spec_from_file_location('rad_pr165_closure', closure_path)
    closure = importlib.util.module_from_spec(spec); spec.loader.exec_module(closure)
    closure.ROOT = a.source
    baseline, witness = closure.compile_closure(graph, witness_saved['matching_arcs'])
    need(json.loads(json.dumps(baseline)) == json.loads((a.export/'baseline.json').read_text()), 'recompiled baseline')
    need(json.loads(json.dumps(witness)) == witness_saved, 'full backward intersections and chronology')
    record, word = select(graph, baseline, witness)
    for key in closure.DIAGNOSTICS:
        record.pop(key, None)
    need(json.loads(json.dumps(record)) == json.loads((a.export/'profile-before.json').read_text()), 'fresh selected paid ledger')
    need(json.loads(json.dumps(word)) == json.loads((a.export/'word.json').read_text()), 'fresh signed word and gauges')
    result = dict(status='PASS_RECONSTRUCTED_FUSION_CLOSURE_WORD',
                  unfused_nodes=initial_nodes, fusion_nodes=len(builder.a)-initial_nodes,
                  roots=len(graph['roots']), matching_arcs=len(witness['matching_arcs']),
                  graph_binding_sha256=sha256(json.dumps(binding,separators=(',',':')).encode()).hexdigest(),
                  counts=graph['counts'], selected_profile=record, source_pins=source_pins,
                  closure_sha256=sha256(closure_path.read_bytes()).hexdigest(),
                  driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  elapsed_seconds=time.monotonic()-start, peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Exact deterministic positive-first signed broadcast fusion on freshly rebuilt source modules; '
                        'all selected graph nodes, roots and centers match. Saved carrier choices independently recompiled '
                        'with full acyclic dependency closure; fresh chronological gauge selection and complete word match. '
                        'No historical matching or physical frame search regeneration is claimed. Independent signed '
                        'arbitrary-dirty scalar and complemented geometry receipts are separate.')
    with a.output.open('x') as stream:
        json.dump(result,stream,indent=2); stream.write('\n')
    print('PASS reconstructed fusion, closure and word; %d appended nodes, %.3fs' %
          (result['fusion_nodes'], result['elapsed_seconds']))


if __name__ == '__main__':
    main()
