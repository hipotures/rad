#!/usr/bin/env python3
"""Bounded structural modules on the actual PR168 fd25adb sink supplier.

RaD; OpenAI GPT-6.1 Sol assistance; Apache-2.0. Task-owned exact local/triple substitutions retain the native pair,
all-but-one modules and existing f8:00111100 fold.
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

SIGNED_CODE = Path(__file__).resolve().parents[2]/'signed/code'
sys.path.insert(0, str(SIGNED_CODE))

import screen_signed_fusion as original_matching
from screen_signed_fusion import numerical_root, finite_scalar_bound
from screen_pr168_modules import load_code, need, write
from check_pr165_signed_control import oriented

SOURCE_HEAD = 'fd25adb7fbaa12ee761d02c733c54d1d2a7687ee'



def map_native_arcs(old,new,arcs):
    from screen_fused_carriers import polynomials
    oldexpr,newexpr = polynomials(old),polynomials(new)
    image = {expr:node+1 for node,expr in enumerate(newexpr)}
    nodes = {node+1:image[expr] for node,expr in enumerate(oldexpr) if expr in image}
    def rootkey(root,expression):
        return (root['kind'],root.get('channel'),root.get('coordinate'),tuple(root['targets']),
                tuple(root['coefficients']),expression[root['node']])
    roots = {rootkey(root,newexpr):j for j,root in enumerate(new['roots'])}
    rootmap = {j:roots[rootkey(root,oldexpr)] for j,root in enumerate(old['roots'])
               if rootkey(root,oldexpr) in roots}
    result=[];donors=set();uses=set()
    for donor,code in arcs:
        if donor not in nodes:continue
        nd=nodes[donor]
        if code>>31:
            j=code&0x7fffffff
            if j not in rootmap:continue
            oldvalue=old['roots'][j]['node']+1
            nc=(1<<31)|rootmap[j]
        else:
            target=code//2
            oldvalue=old['args'][target-1][code&1]+1
            if target not in nodes or oldvalue not in nodes:continue
            nt=nodes[target]
            if new['args'][nt-1] is None or nodes[oldvalue]-1 not in new['args'][nt-1]:continue
            nc=2*nt+new['args'][nt-1].index(nodes[oldvalue]-1)
        if oldvalue not in nodes or new['args'][nd-1] is None:continue
        nv=nodes[oldvalue]
        if nv-1 not in new['args'][nd-1] or (not nc>>31 and nc//2==nd):continue
        if new['signs'][nd-1]<0 and nv-1==new['args'][nd-1][0]:continue
        if nd in donors or nc in uses:continue
        result.append([nd,nc]);donors.add(nd);uses.add(nc)
    return result,dict(native_arcs=len(arcs),exact_signed_nodes=len(nodes),exact_root_uses=len(rootmap),
                       seed_arcs=len(result),method='Exact signed source coefficient vectors, root readouts and actual operand incidences; complete closure is freshly checked')


def exact_star(sink,word):
    """Characteristic-zero identity with independent controls and spectators."""
    from collections import defaultdict
    T=sink['T'];pivot=T.index(sink['c']);writes=sink['writes'];c=Fraction(sink['coeff'])
    original=[{i:Fraction(1)} for i in range(len(T))]
    new=[dict(value) for value in original]
    z={-1:Fraction(1)}
    def add(dst,src,scale):
        for key,value in src.items():
            dst[key]=dst.get(key,Fraction(0))+scale*value
            if not dst[key]:del dst[key]
    for target in range(len(T)):add(original[target],z,-c)
    for target in range(len(T)):
        if target!=pivot:add(new[target],new[pivot],-1)
    for k,op in enumerate(writes):
        ca,cb=word['opcoeff'][op]
        need(ca==1,'sink primitive is an additive shear')
        control={len(T)+k:Fraction(1)}
        add(z,control,cb);add(new[pivot],control,c*cb)
    for target in range(len(T)):add(original[target],z,c)
    for target in range(len(T)):
        if target!=pivot:add(new[target],new[pivot],1)
    need(original==new and all(-1 not in value for value in original),'exact sink pivot-star identity')
    return dict(targets=len(T),writes=len(writes),all_formal_control_and_spectator_coefficients_equal=True,
                old_sink_dirty_variable_cancels=True,coefficient_denominator_divides=6)


def actual_sink_profile(source,graph,witness,word,row,frames,pairs,base):
    from collections import defaultdict
    need(all(ca==1 for ca,cb in word['opcoeff']),'current native sink stage requires shear operations')
    phase=set(word['phase1']);order=sorted(phase)+[i for i in range(len(word['ops'])) if i not in phase]
    pos={op:k for k,op in enumerate(order)};writes=defaultdict(list);controls=set()
    for i,(a,b,x) in enumerate(word['ops']):writes[a].append(i);controls.add(b)
    used=set(s for a,b,t in pairs for s in (a,b));deferred={z['role'] for z in word['selected']}
    sources=set(word['sources'].values());deadlines={b:t for a,b,t in pairs};firstread={}
    for z in word['selected']:
        op=deadlines.get(z['role']);when=pos[op] if op is not None else len(phase)
        for t in z['targets']:firstread[t]=min(firstread.get(t,10**12),when)
    selected=[]
    for root,role in zip(graph['roots'],word['rootroles']):
        if root['kind']!='side' or len(root['targets'])!=8:continue
        if role in used or role in deferred or role in sources or role in controls:continue
        if not writes[role] or any(op in phase for op in writes[role]):continue
        last=max(pos[op] for op in writes[role])
        pivots=[t for t in root['targets'] if firstread.get(t,10**12)>last]
        if pivots:selected.append([role,pivots[0]])
    if not selected:
        return dict(base,sinks=0),dict(status='NO_ELIGIBLE_ALL_EIGHT_SINK',sinks=[])
    gate_path=source/'research/terminal-sinks/sinks_gate.py'
    gate=load_code('rad_changed_local_native_sink_gate',gate_path);captured={}
    def observe(frame,event,arg):
        if event=='return' and frame.f_code is gate.sinks_record.__code__:
            captured['sink']=frame.f_locals['sink']
    previous=sys.getprofile();sys.setprofile(observe)
    try:paid=gate.sinks_record(graph,witness,word,row,frames,pairs,selected,base)
    finally:sys.setprofile(previous)
    exact=[exact_star(sink,word) for sink in captured['sink'].values()]
    return paid,dict(status='EXACT_SYMBOLIC_TERMINAL_SUBSTITUTIONS_WITH_FULL_NATIVE_GEOMETRY',sinks=selected,
                     independent_exact_star_identities=exact,native_gate_sha256=sha256(gate_path.read_bytes()).hexdigest(),
                     scope='Each destination-only non-gauged sink has an exact characteristic-zero formal-control identity; full body exact signed/dirty and inverse checks establish the unchanged remainder. Native gate rechecks all eligibility, complete literal reflected frame scans and paid per-class inventory.')

def run(task):
    source, export, plan_path, audit_path, interval_path, placement, candidates = map(Path, task[:7])
    name, target_text, outroot = task[7:]
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
    candidate = candidates/name
    module_manifest = json.loads((candidates/'manifest.json').read_text())
    module_checks = module_manifest['variants'][name]
    for filename, pin in module_checks['exported_pins'].items():
        need(sha256((candidate/filename).read_bytes()).hexdigest() == pin['sha256'],
             'task-owned module export pin '+name+'/'+filename)
    local = json.loads((candidate/'local.json').read_text())
    builder = Graph(11, local=local)
    graph = builder.finish(triple_module_from(candidate/'triple.json', 11),
                           pair_module_from(src/'pmod_H56snap_w02_5.6251423e-4.json', 10),
                           all_but_one_from(src/'qmod_anneal_best01.json', 9))
    graph = merge_outputs(graph, builder, 'f8:00111100')
    graph['matching_frames'] = 'coordinate'
    saved = json.loads((export/'graph.json').read_text())
    if name == 'control':
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
    adaptations = dict(local_configuration=local, triple_substitution=str(candidate/'triple.json'),
                       module_checks=module_checks)
    native_arcs = json.loads((export/'frames.json').read_text())['matching_arcs']
    if name == 'control':
        initial_arcs = native_arcs
        mapping = {'seed_arcs':len(initial_arcs),'method':'Native unchanged frozen arcs'}
        arcs = native_arcs
    else:
        initial_arcs,mapping = map_native_arcs(saved,graph,native_arcs)
        # Native terminal sinks need shear gates. Avoid transferring the left
        # operand of a negative addition, which would negate a destination.
        text = plan_path.read_text()
        old = "        t = None if code >> 31 else code // 2\n        At = rann[code & 0x7fffffff] if t is None else gann[t]"
        new = "        if g['signs'][x-1] < 0 and value(code) == args[x][0]: return False\n" + old
        need(text.count(old) == 1,'declared shear-preserving carrier condition applies once')
        namespace = dict(__name__='rad_shear_preserving_extended',__file__=str(plan_path))
        adapted_plan = text.replace(old,new)
        seed_old = "    for x, code in frozen: assert add(x, code, True), ('frozen arc rejected', x, code)"
        seed_new = "    global SEED_REJECTIONS\n    SEED_REJECTIONS = []\n    for x, code in frozen:\n        if not add(x, code, True):\n            SEED_REJECTIONS.append([x, code])"
        need(adapted_plan.count(seed_old) == 1,'declared full seed revalidation applies once')
        adapted_plan = adapted_plan.replace(seed_old,seed_new)
        exec(compile(adapted_plan,'[shear-safe-geometry-revalidated-extension]','exec'),namespace)
        arcs = namespace['extended_arcs'](graph,initial_arcs)
        adaptations['shear_preserving_extension'] = dict(old=old,new=new)
        adaptations['seed_revalidation'] = dict(old=seed_old,new=seed_new,
            rejected=namespace['SEED_REJECTIONS'],
            method='Every mapped seed rechecked in sequence against current accumulated spans, frame intersections, acyclicity and unit-destination sign. Rejected seeds cause no state mutation.')
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
    body_paid = paid
    paid,sink_checks = actual_sink_profile(source,graph,witness,word,row,moved,pairs,paid)
    write(out/'sink-profile.json',paid)
    write(out/'sink-checks.json',sink_checks)
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
    binding = {key:graph[key] for key in ('inputs','labels','args','signs','roots','centers')}
    graph_hash = sha256(json.dumps(binding,separators=(',',':')).encode()).hexdigest()
    result = dict(status='EXACT_FINITE_STRUCTURAL_MODULE_SCREEN',variant=name,source_head=SOURCE_HEAD,
                  graph_binding_sha256=graph_hash, graph_counts=graph['counts'],
                  initial_arcs=len(initial_arcs),matched=len(arcs),added_arcs=len(arcs)-len(initial_arcs),
                  mapping=mapping,body_profile=body_paid,sink_checks=sink_checks,
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
                  scope='Fresh fd25adb graph with task-owned exact positive triple/local signed circuit substitutions; native pair/all-but-one modules and f8 fold. '
                        'Every variant rebuilds complete closure/gauges/word and then fresh physical pairs and frames '
                        'under the same4round construction and component/global continuation. Complete paid inventory, '
                        'exact body source/dirty response and inverse cleanup pass both shear signs; terminal substitution '
                        'has an independent exact symbolic pivot-star identity and native full reflected frame scans. '
                        'all-size/analytic composition remain separate.')
    write(out/'result.json',result)
    print('%s COMPLETE arcs%d M%d W%d root%.12g %s %.3fs' %
          (name,len(arcs),row['total_M_operations'],paid['W_per_vertex'],result['numerical_complex_root_discovery_only'],
           result['exact_target']['classification'],result['wall_seconds']),flush=True)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('source','export','plan','exact-core','interval-code','placement-code','candidates','output'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--variants',nargs='+',choices=('control','all_edge','all_long','triple_balanced'),
                   default=['control','all_edge','all_long','triple_balanced'])
    p.add_argument('--trial-saving',default='655861417/1000000000000')
    a = p.parse_args()
    need(not sys.flags.optimize,'assertion-disabled execution rejected')
    need(1 <= a.workers <= 4,'one through four workers are permitted')
    a.output.mkdir(parents=True,exist_ok=False)
    start = time.monotonic()
    variants = a.variants
    need(len(variants) == len(set(variants)),'duplicate variant invocation')
    dependencies = [a.plan,a.exact_core,a.interval_code,SIGNED_CODE/'screen_fused_carriers.py',SIGNED_CODE/'screen_signed_fusion.py']+list(a.placement_code.glob('*.py'))
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(),source_head=SOURCE_HEAD,
                    source=str(a.source.resolve()),immutable_control=str(a.export.resolve()),
                    variants=variants,workers=a.workers,nested_library_threads=1,
                    candidate_manifest=str(a.candidates.resolve()/'manifest.json'),
                    candidate_manifest_sha256=sha256((a.candidates/'manifest.json').read_bytes()).hexdigest(),
                    evaluator_seed=20261009, local_search_rounds=4, component_sweeps=6, global_lower_budget=8192,
                    original_evaluator_sha256='ac1ff39e4af5a507a42f74442a663b024ed704f538cdb814cb1f472c506a1998',
                    trial_saving=str(Fraction(a.trial_saving)),driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                    dependency_pins={str(path):sha256(path.read_bytes()).hexdigest() for path in dependencies})
    write(a.output/'protocol.json',protocol)
    tasks = [tuple(str(path.resolve()) for path in
                   (a.source,a.export,a.plan,a.exact_core,a.interval_code,a.placement_code,a.candidates))+
             (name,a.trial_saving,str(a.output.resolve())) for name in variants]
    rows = []
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        for future in as_completed([pool.submit(run,task) for task in tasks]):
            rows.append(future.result())
    rows.sort(key=lambda row:variants.index(row['variant']))
    write(a.output/'batch-result.json',dict(status='COMPLETE_STRUCTURAL_MODULE_BATCH',results=rows,
                                          protocol=protocol,elapsed_seconds=time.monotonic()-start))


if __name__ == '__main__':
    main()
