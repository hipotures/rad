#!/usr/bin/env python3
"""Four fresh paid constructions on PR168 modules, without frame transplants.

RaD; OpenAI GPT-6.1 Sol assistance. Apache-2.0. Reuses pinned paired-cube
builders/checkers, PR162's extended carrier and joint frame/reuse discovery,
and RaD's independently authored exact adjoint and rational moment kernels.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time
import types

sys.dont_write_bytecode = True
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

from screen_signed_fusion import matching, numerical_root, moment, finite_scalar_bound
from check_pr165_signed_control import oriented


def need(condition, message):
    if not condition:
        raise ValueError(message)


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, separators=(',', ':')); stream.write('\n')


def direct_module(n, association):
    """Positive all-but-one module with an explicit disjoint-support contract."""
    args = [None]*n; support = [1 << i for i in range(n)]; intern = {s:i for i,s in enumerate(support)}
    def add(a,b):
        need(not support[a] & support[b], 'module overlap')
        joined = support[a] | support[b]
        if joined not in intern:
            intern[joined] = len(args); args.append([a,b]); support.append(joined)
        return intern[joined]
    prefix = list(range(n)); suffix = list(range(n))
    for i in range(1,n-1):
        prefix[i] = add(prefix[i-1], i)
    for i in reversed(range(1,n-1)):
        suffix[i] = add(i, suffix[i+1])
    roots = [suffix[1]]
    for omitted in range(1,n-1):
        if association == 'flat' or omitted == n-2:
            roots.append(add(prefix[omitted-1], suffix[omitted+1]))
        else:
            roots.append(add(add(prefix[omitted-1], omitted+1), suffix[omitted+2]))
    roots.append(prefix[n-2])
    full = (1 << n)-1
    need(all(support[node] == full ^ (1 << i) for i,node in enumerate(roots)), 'all-but-one outputs')
    active = set(range(n)); pending = list(roots)
    while pending:
        node = pending.pop()
        if node in active:
            continue
        active.add(node); pending.extend(args[node])
    order = sorted(active); rename = {node:i for i,node in enumerate(order)}
    return dict(input_count=n, args=[None if args[node] is None else [rename[x] for x in args[node]]
                                    for node in order], roots=[rename[node] for node in roots],
                contract='Root i is the positive sum of every input except i; disjoint supports at each gate.',
                association=association)


def full_fusion(graph, builder):
    """Positive-first exact assembly of all three singleton signed channels."""
    channels = ('face2','edge02','edge12')
    roots = []
    channel_order = {'disjoint':0,'face0':1,'face1':2,'edge01':3}
    for cube in range(graph['v']//8):
        local = [root for root in graph['roots'] if root['kind'] == 'side' and root['targets'][0]//8 == cube]
        broad = [root for root in local if root['channel'] not in channels]
        roots.extend(sorted(broad,key=lambda root:(-len(root['targets']),tuple(root['targets']),channel_order[root['channel']])))
        terms = {(root['targets'][0],root['channel']):(root['node'],Fraction(root['coefficients'][0]))
                 for root in local if root['channel'] in channels}
        for target in range(8*cube,8*cube+8):
            parts = [terms[target,channel] for channel in channels]
            need({abs(coef) for node,coef in parts} == {Fraction(1,2)}, 'unit fusion coefficients')
            positive = [node for node,coef in parts if coef > 0]
            negative = [node for node,coef in parts if coef < 0]
            node = positive[0]
            for operand in positive[1:]:
                node = builder.add(node,operand)
            for operand in negative:
                node = builder.add(node,operand,-1)
            roots.append(dict(node=node,targets=[target],coefficients=['1/2'],kind='side',channel='complete_signed_fusion'))
    return dict(graph,args=builder.a,signs=builder.signs,
                roots=roots+[root for root in graph['roots'] if root['kind'] == 'center'])


def load_code(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def run_variant(task):
    source,plan_path,audit_path,interval_path = map(Path,task[:4]); name,outroot,trial = task[4:]
    out = Path(outroot)/name; out.mkdir()
    start = time.monotonic(); timings = {}
    sys.path.insert(0,str(source/'scripts'))
    from paired_cube.graph import Graph
    from paired_cube.modules import restricted_triples_from,pair_module_from,all_but_one_from,merge_outputs
    from paired_cube.frames import basis,perp,contained
    from paired_cube.closure import compile_closure
    from paired_cube.gauges import select
    from paired_cube import verify as native_verify
    from paired_cube_physical import physical
    src = source/'references/paired-cube/sources'
    pins = json.loads((src/'SOURCE.json').read_text())['files']
    for filename,digest in pins.items():
        need(sha256((src/filename).read_bytes()).hexdigest() == digest,'source pin: '+filename)
    print(name+': reconstruct module/DAG',flush=True)
    q = all_but_one_from(src/'qmod_nested_prefix.json',9) if name in ('unchanged','complete_fusion') else \
        direct_module(9,'flat' if name == 'flat_bridge' else 'right_nested')
    builder = Graph(11)
    graph = builder.finish(restricted_triples_from(src/'h20_g1.json.gz',[0,1,2,3,4,5,6,7,8,9,16]),
                           pair_module_from(src/'pmod_G37_w02_5.6098194e-4.json',10),q)
    graph = full_fusion(graph,builder) if name == 'complete_fusion' else merge_outputs(graph,builder,'w02')
    graph['matching_frames'] = 'coordinate'
    binding = {key:graph[key] for key in ('inputs','labels','args','signs','roots','centers')}
    graph_hash = sha256(json.dumps(binding,separators=(',',':')).encode()).hexdigest()
    if name == 'unchanged':
        pin = json.loads((source/'references/paired-cube/selected-module/SOURCE.json').read_text())
        need(graph_hash == pin['graph_sha256'],'unchanged PR168 graph binding')
    write(out/'qmodule.json',q); write(out/'graph.json',graph)
    timings['dag'] = time.monotonic()-start
    before = time.monotonic()
    print(name+': fresh maximum matching plus extended dependency closure',flush=True)
    fresh_arcs,matchstats = matching(graph)
    stub = types.ModuleType('cxlinks')
    for key,value in dict(basis=basis,perp=perp,contained=contained,ROOT=source).items():
        setattr(stub,key,value)
    sys.modules['cxlinks'] = stub
    plan = load_code('rad_pr162_discovery',plan_path)
    arcs = plan.extended_arcs(graph,fresh_arcs)
    baseline,witness = compile_closure(graph,arcs)
    selected,word = select(graph,baseline,witness)
    write(out/'baseline.json',baseline); write(out/'frames.json',witness)
    write(out/'matching.json',dict(initial=fresh_arcs,arcs=arcs,stats=matchstats))
    write(out/'selected-profile.json',selected); write(out/'selection.json',word)
    timings['matching_closure_gauges'] = time.monotonic()-before
    print(name+': exact finite signed source/geometry and fresh joint physical construction',flush=True)
    before = time.monotonic()
    verifier_text = Path(native_verify.__file__).read_text()
    old = "assert record['selected_roles']==len(seen)==2970 and birth==Counter({18:2970})"
    new = "assert record['selected_roles']==len(seen) and birth==Counter({int(k):c for k,c in record['selected_rank_histogram'].items()})"
    need(verifier_text.count(old) == 1,'unexpected finite verifier fixed-count assertion')
    namespace = dict(__name__='paired_cube.verify_fresh_module',__package__='paired_cube')
    exec(compile(verifier_text.replace(old,new),str(native_verify.__file__)+'[count-generalized]','exec'),namespace)
    finite = namespace['verify'](graph,baseline,witness,word,selected)
    layer = plan.Layer(graph,witness,word,selected)
    layer.build(rounds=3)
    moved,pairs = layer.export()
    write(out/'fresh-physical-inputs.json',dict(frames=moved,pairs=pairs))
    paid = physical(graph,witness,word,selected,moved,pairs)
    write(out/'physical-profile.json',paid)
    timings['finite_geometry_and_fresh_physical'] = time.monotonic()-before
    print(name+': exact arbitrary-dirty core under both orientations',flush=True)
    before = time.monotonic()
    audit = load_code('rad_exact_integer_core',audit_path)
    events,mutations,cleanup,live,_ = audit.prepare(graph,word,pairs,selected['R'])
    exact = [oriented(audit,graph,events,mutations,cleanup,live,sign) for sign in (1,-1)]
    controls = {}
    for mutation in ('omitted_read','bad_sign','illegal_index','omit_cleanup'):
        try:
            audit.check(graph,events,mutations,cleanup,live,mutation=mutation)
        except (ValueError,KeyError) as error:
            controls[mutation] = str(error)
        else:
            raise ValueError('negative control accepted: '+mutation)
    timings['exact_signed_core'] = time.monotonic()-before
    root = numerical_root(paid)
    intervals = load_code('rad_interval_moments',interval_path)
    target = Fraction(trial)
    target_lo,target_hi = intervals.moment(paid['m'],paid['W_per_vertex'],
                                           {int(r):n for r,n in paid['child_histogram'].items()},target)
    result = dict(variant=name,status='EXACT_FINITE_FRESH_MODULE_SCREEN',source_head_prefix='98c115b',
                  source_input_hashes=pins,graph_binding_sha256=graph_hash,qmodule_additions=len(q['args'])-9,
                  c=selected['c'],q=selected['q'],matched=len(arcs),fresh_initial_matched=len(fresh_arcs),
                  physical_R=paid['physical_R'],R=selected['R'],W=paid['W_per_vertex'],m=paid['m'],
                  h=paid['h'],v=paid['v'],rank_mass=paid['rank_per_vertex'],deficit=paid['deficit_per_vertex'],
                  moved_frames=len(moved),pairs=len(pairs),selected_roles=selected['selected_roles'],
                  numerical_complex_root_discovery_only=root,complete_children=paid['child_histogram'],
                  common_trial_H=moment(paid,float(target)),
                  exact_target=dict(saving=str(target),lower=str(target_lo),upper=str(target_hi),
                                    classification='ACCEPTED' if target_hi < 1 else 'REJECTED' if target_lo > 1 else 'UNRESOLVED'),
                  exact_integer_checks=exact,negative_controls=controls,finite_checks=finite,
                  verifier_adaptation=dict(old=old,new=new),verifier_sha256=sha256(verifier_text.encode()).hexdigest(),
                  scalar_charge=finite_scalar_bound(selected,paid),timings_seconds=timings,
                  wall_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  workers=1,nested_library_threads=1,
                  comparison_scope='Same immutable PR168 pair/triple modules, fresh deterministic maximum matching '
                        'followed by extended acyclic carrier closure, fresh chronological gauges, three joint '
                        'operation-frame/pair rounds. No saved frames, aliases or profile splice. This common '
                        'fresh control differs from optimized public168 physical choices. Exact scalar/support '
                        'checks pass; full independently complemented/reflected replay and all-size assembly '
                        'remain separate. Numerical root is discovery only; target moment is rationally enclosed.')
    write(out/'result.json',result)
    print(name+': exact finite complete; root %.12g, target %s, W%d, %.3fs' %
          (root,result['exact_target']['classification'],paid['W_per_vertex'],result['wall_seconds']),flush=True)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--exact-core',type=Path,required=True)
    p.add_argument('--interval-code',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--trial-saving',default='617042388/1000000000000')
    a = p.parse_args(); need(not sys.flags.optimize,'assertion-disabled execution rejected')
    start = time.monotonic(); a.output.mkdir(parents=True,exist_ok=False)
    variants = ['unchanged','flat_bridge','right_nested','complete_fusion']
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(),source=str(a.source.resolve()),
                    variants=variants,workers=a.workers,nested_library_threads=1,
                    source_head_prefix='98c115b',driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                    dependency_pins={str(path):sha256(path.read_bytes()).hexdigest()
                                     for path in (a.plan,a.exact_core,a.interval_code)},
                    common_trial_saving=str(Fraction(a.trial_saving)),
                    fresh_matching=True,fresh_extended_closure=True,fresh_frames_and_aliases=True)
    write(a.output/'protocol.json',protocol)
    tasks = [(str(a.source.resolve()),str(a.plan.resolve()),str(a.exact_core.resolve()),
              str(a.interval_code.resolve()),name,str(a.output.resolve()),a.trial_saving) for name in variants]
    rows = []
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        for future in as_completed([pool.submit(run_variant,task) for task in tasks]):
            rows.append(future.result())
    rows.sort(key=lambda row:variants.index(row['variant']))
    write(a.output/'batch-result.json',dict(status='FOUR_FRESH_COMPLETE_CONSTRUCTIONS',results=rows,
                                          elapsed_seconds=time.monotonic()-start,protocol=protocol))


if __name__ == '__main__':
    main()
