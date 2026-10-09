#!/usr/bin/env python3
"""Bounded fresh carrier choices on the actual PR168 91f6a05 folded DAG.

RaD; OpenAI GPT-6.1 Sol assistance; Apache-2.0. All native local and
module synthesis is retained, including its existing f8:00111100 fold.
Changed carrier choices require newly compiled closures, gauges, literal
words and physical aliases. No prior source's plan or profile is imported.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import inspect
import json
import math
from pathlib import Path
import random
import resource
import sys
import time
import types

sys.dont_write_bytecode = True
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

import screen_signed_fusion as original_matching
from screen_signed_fusion import numerical_root, finite_scalar_bound
from screen_pr168_modules import load_code, need, write
from check_pr165_signed_control import oriented

SOURCE_HEAD = '91f6a059f44fb0513639d5185bde2a38973e99ca'


def run(task):
    source, export, plan_path, audit_path, interval_path, placement = map(Path, task[:6])
    name, target_text, outroot = task[6:]
    out = Path(outroot)/name
    out.mkdir()
    start = time.monotonic()
    protocol = json.loads((export/'protocol.json').read_text())
    need(protocol['source_head'] == SOURCE_HEAD, 'control source head')
    for filename, pin in protocol['input_pins'].items():
        need(sha256((export/filename).read_bytes()).hexdigest() == pin['sha256'], 'control input pin '+filename)
    for filename, digest in protocol['source_pins'].items():
        need(sha256((source/filename).read_bytes()).hexdigest() == digest, 'control source pin '+filename)
    sys.path.insert(0, str(source/'scripts'))
    from paired_cube.graph import Graph
    from paired_cube.modules import triple_module_from, pair_module_from, all_but_one_from, merge_outputs
    from paired_cube.frames import basis, perp, contained
    from paired_cube.closure import compile_closure
    from paired_cube.gauges import select
    from paired_cube import verify as native_verify
    from paired_cube_physical import physical
    src = source/'references/paired-cube/sources'
    builder = Graph(11, local=json.loads((src/'local_L1.json').read_text()))
    graph = builder.finish(triple_module_from(src/'tmod_TA24snap2_L1f8_5.9580885e-4.json', 11),
                           pair_module_from(src/'pmod_H56snap_w02_5.6251423e-4.json', 10),
                           all_but_one_from(src/'qmod_anneal_best01.json', 9))
    graph = merge_outputs(graph, builder, 'f8:00111100')
    graph['matching_frames'] = 'coordinate'
    saved = json.loads((export/'graph.json').read_text())
    need(json.loads(json.dumps(graph)) == saved, 'fresh complete scalar graph equals current source control')
    stub = types.ModuleType('cxlinks')
    for key, value in dict(basis=basis, perp=perp, contained=contained, ROOT=source).items():
        setattr(stub, key, value)
    sys.modules['cxlinks'] = stub
    plan = load_code('rad_changed168_carrier_plan', plan_path)
    target = Fraction(target_text)
    saving = float(target)
    plan.cost = lambda rank, m: rank*math.expm1(saving*math.log(m/rank))/saving if rank else 0.
    native_arcs = json.loads((export/'frames.json').read_text())['matching_arcs']
    adaptations = {}
    if name == 'control':
        initial_arcs = native_arcs
        arcs = native_arcs
    elif name == 'extend_native':
        initial_arcs = native_arcs
        arcs = plan.extended_arcs(graph, initial_arcs)
    elif name == 'reverse_max':
        text = inspect.getsource(original_matching.matching)
        old = 'adjacent.append(sorted(set(eligible)))'
        new = 'adjacent.append(sorted(set(eligible),reverse=True))'
        need(text.count(old) == 1, 'maximum traversal adaptation applies exactly once')
        namespace = dict(original_matching.__dict__)
        exec(compile(text.replace(old, new), '[reversed-maximum-use-order]', 'exec'), namespace)
        initial_arcs, _ = namespace['matching'](graph)
        arcs = plan.extended_arcs(graph, initial_arcs)
        adaptations['maximum_traversal'] = dict(old=old, new=new)
    elif name == 'reverse_extended':
        initial_arcs, _ = original_matching.matching(graph)
        text = plan_path.read_text()
        old = 'for x in sorted(active):\n        if not args[x]: continue\n        for j, y in enumerate(args[x]):'
        new = 'for x in sorted(active,reverse=True):\n        if not args[x]: continue\n        for j, y in enumerate(args[x]):'
        need(text.count(old) == 1, 'extended traversal adaptation applies exactly once')
        namespace = dict(__name__='rad_changed168_reverse_extended', __file__=str(plan_path))
        exec(compile(text.replace(old, new), '[reversed-extension-order]', 'exec'), namespace)
        arcs = namespace['extended_arcs'](graph, initial_arcs)
        adaptations['extended_traversal'] = dict(old=old, new=new)
    else:
        raise ValueError('unknown bounded discriminator')
    print(name+': fresh carrier closure '+str(len(arcs)), flush=True)
    baseline, witness = compile_closure(graph, arcs)
    row, word = select(graph, baseline, witness)
    for filename, data in [('graph.json',graph), ('baseline.json',baseline), ('frames.json',witness),
                           ('selection.json',word), ('selected-profile.json',row), ('matching.json',arcs)]:
        write(out/filename, data)
    # Only the native source's fixed historical selection total is adapted.
    # Actual selection count and full rank histogram are recomputed here.
    text = Path(native_verify.__file__).read_text()
    old = "assert record['selected_roles']==len(seen)==2310 and birth==Counter({18:2310})"
    new = "assert record['selected_roles']==len(seen) and birth==Counter({int(k):c for k,c in record['selected_rank_histogram'].items()})"
    need(text.count(old) == 1, 'declared native count adaptation applies exactly once')
    namespace = dict(__name__='paired_cube.verify_changed168_carriers', __package__='paired_cube')
    adapted = text.replace(old, new)
    exec(compile(adapted, '[actual-selected-count]', 'exec'), namespace)
    checks = namespace['verify'](graph, baseline, witness, word, row)
    layer = plan.Layer(graph, witness, word, row)
    layer.build(rounds=4)
    moved, pairs = layer.export()
    paid = physical(graph, witness, word, row, moved, pairs)
    # This fresh context binds placement's read-only APIs to the new word and
    # its own coherent aliases. It is execution material, not a source patch.
    context = out/'placement-context'
    (context/'certificates').mkdir(parents=True)
    (context/'references/paired-cube/physical').mkdir(parents=True)
    (context/'scripts').symlink_to(source/'scripts', target_is_directory=True)
    for filename, data in [('certificates/paired-cube-complex-input.json',row),
                           ('certificates/paired-cube-physical-input.json',paid),
                           ('references/paired-cube/physical/frames.json',dict(frames=moved)),
                           ('references/paired-cube/physical/pairs.json',dict(pairs=pairs))]:
        write(context/filename, data)
    sys.path.insert(0, str(placement))
    from physical_closure import Closure
    model = Closure(context, out, saving)
    rng = random.Random(20261009)
    component_moves = []
    for sweep in range(6):
        changed = 0
        groups = model.groups('components', rng)
        if sweep % 2:
            groups.reverse()
        for group in groups:
            proposal = model.change(group)
            if proposal:
                component_moves.append(proposal)
                changed += 1
        if not changed:
            break
    model.global_bounds()
    global_moves = []
    for seed in range(len(model.ops)):
        proposal, status = model.proposal(seed, 'lower', 8192)
        if proposal:
            for op, frame in proposal['frames']:
                model.frames[op] = tuple(frame)
            global_moves.append({key:value for key,value in proposal.items() if key != 'frames'})
    model.validate()
    histogram = model.histogram()
    moved = [[op,list(frame)] for op,frame in enumerate(model.frames) if frame != model.original[op]]
    paid = physical(graph, witness, word, row, moved, pairs)
    need(histogram == paid['child_histogram'], 'independent complete inventory agrees')
    write(out/'fresh-physical-inputs.json', dict(frames=moved,pairs=pairs))
    write(out/'physical-profile.json', paid)
    audit = load_code('rad_changed168_exact_core', audit_path)
    events, mutations, cleanup, live, _ = audit.prepare(graph, word, pairs, row['R'])
    exact = [oriented(audit,graph,events,mutations,cleanup,live,direction) for direction in (1,-1)]
    controls = {}
    for mutation in ('omitted_read','bad_sign','illegal_index','omit_cleanup'):
        try:
            audit.check(graph,events,mutations,cleanup,live,mutation=mutation)
        except (ValueError,KeyError) as error:
            controls[mutation] = str(error)
        else:
            raise ValueError('negative scalar control accepted '+mutation)
    intervals = load_code('rad_changed168_intervals', interval_path)
    lower, upper = intervals.moment(paid['m'],paid['W_per_vertex'],
                                   {int(r):n for r,n in paid['child_histogram'].items()},target)
    result = dict(status='EXACT_FINITE_CHANGED168_CARRIER_SCREEN',variant=name,source_head=SOURCE_HEAD,
                  initial_arcs=len(initial_arcs),matched=len(arcs),added_arcs=len(arcs)-len(initial_arcs),
                  carrier_symmetric_difference=len(set(map(tuple,arcs))^set(map(tuple,native_arcs))),
                  adaptations=adaptations,native_verifier_sha256=sha256(text.encode()).hexdigest(),
                  adapted_verifier_sha256=sha256(adapted.encode()).hexdigest(),finite_checks=checks,
                  exact_signed_core=exact,negative_scalar_controls=controls,c=row['c'],q=row['q'],R=row['R'],
                  literal_M=row['total_M_operations'],selected_roles=row['selected_roles'],pairs=len(pairs),
                  physical_R=paid['physical_R'],W=paid['W_per_vertex'],m=paid['m'],rank_mass=paid['rank_per_vertex'],
                  deficit=paid['deficit_per_vertex'],complete_children=paid['child_histogram'],
                  component_moves=len(component_moves),global_lower_moves=len(global_moves),
                  numerical_complex_root_discovery_only=numerical_root(paid),
                  exact_target=dict(saving=str(target),lower=str(lower),upper=str(upper),
                                    classification='ACCEPTED' if upper<1 else 'REJECTED' if lower>1 else 'UNRESOLVED'),
                  scalar_charge=finite_scalar_bound(row,paid),wall_seconds=time.monotonic()-start,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Fresh native91f6a05 local/triple/pair/all-but-one modules and existing signed f8 fold. '
                        'Every variant rebuilds complete closure/gauges/word and then fresh physical pairs and frames '
                        'under the same4round construction and component/global continuation. Complete paid inventory, '
                        'exact source/dirty response and inverse cleanup pass both shear signs. No oldsource plan/profile '
                        'is reused; numerical roots guide discovery only. Independent complemented geometry and '
                        'all-size/analytic composition remain separate.')
    write(out/'result.json',result)
    print('%s COMPLETE arcs%d M%d W%d root%.12g %s %.3fs' %
          (name,len(arcs),row['total_M_operations'],paid['W_per_vertex'],result['numerical_complex_root_discovery_only'],
           result['exact_target']['classification'],result['wall_seconds']),flush=True)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('source','export','plan','exact-core','interval-code','placement-code','output'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--trial-saving',default='652591202/1000000000000')
    a = p.parse_args()
    need(not sys.flags.optimize,'assertion-disabled execution rejected')
    a.output.mkdir(parents=True,exist_ok=False)
    start = time.monotonic()
    variants = ['control','extend_native','reverse_max','reverse_extended']
    dependencies = [a.plan,a.exact_core,a.interval_code]+list(a.placement_code.glob('*.py'))
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(),source_head=SOURCE_HEAD,
                    source=str(a.source.resolve()),immutable_control=str(a.export.resolve()),
                    variants=variants,workers=a.workers,nested_library_threads=1,
                    trial_saving=str(Fraction(a.trial_saving)),driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                    dependency_pins={str(path):sha256(path.read_bytes()).hexdigest() for path in dependencies})
    write(a.output/'protocol.json',protocol)
    tasks = [tuple(str(path.resolve()) for path in
                   (a.source,a.export,a.plan,a.exact_core,a.interval_code,a.placement_code))+
             (name,a.trial_saving,str(a.output.resolve())) for name in variants]
    rows = []
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        for future in as_completed([pool.submit(run,task) for task in tasks]):
            rows.append(future.result())
    rows.sort(key=lambda row:variants.index(row['variant']))
    write(a.output/'batch-result.json',dict(status='COMPLETE_CHANGED168_CARRIER_BATCH',results=rows,
                                          protocol=protocol,elapsed_seconds=time.monotonic()-start))


if __name__ == '__main__':
    main()
