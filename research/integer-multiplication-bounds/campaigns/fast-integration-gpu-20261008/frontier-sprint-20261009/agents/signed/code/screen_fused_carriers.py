#!/usr/bin/env python3
"""Fresh carrier-closure variants on the actual fused PR168 scalar DAG.

RaD; GPT-6.1 Sol assistance. Apache-2.0. Pinned upstream PR162 extended
carrier discovery and paired-cube checks are reused with explicit order
adaptations. Placement's component/global APIs are used read-only after
fresh word, frames and pairs; no changed-word frame transplant is allowed.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import sha256
import inspect
import json
from pathlib import Path
import random
import resource
import sys
import time
import types

sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)

import screen_signed_fusion as original_matching
from screen_signed_fusion import numerical_root,moment,finite_scalar_bound
from screen_pr168_modules import full_fusion,load_code,need,write
from check_pr165_signed_control import oriented


def polynomials(graph):
    """Exact signed original-source coefficient maps, encoded as disjoint bits."""
    result=[]
    for node,args in enumerate(graph['args']):
        if args is None:
            result.append((1<<node,0));continue
        ap,an=result[args[0]];bp,bn=result[args[1]]
        need(not (ap|an)&(bp|bn),'signed polynomial supports overlap')
        if graph['signs'][node]<0:bp,bn=bn,bp
        result.append((ap|bp,an|bn))
    return result


def map_public_carriers(old,new,arcs):
    oldexpr,newexpr=polynomials(old),polynomials(new)
    image={expression:node+1 for node,expression in enumerate(newexpr)}
    nodeimage={node+1:image[expression] for node,expression in enumerate(oldexpr) if expression in image}
    mapped=[];used=set();donors=set()
    for donor,code in arcs:
        if donor not in nodeimage or code>>31:continue
        target=code//2;oldvalue=old['args'][target-1][code&1]+1
        if target not in nodeimage or oldvalue not in nodeimage:continue
        nd,nt,nv=nodeimage[donor],nodeimage[target],nodeimage[oldvalue]
        args=new['args'][nd-1];targetargs=new['args'][nt-1]
        if args is None or targetargs is None or nv-1 not in args or nv-1 not in targetargs or nd==nt:continue
        nc=2*nt+targetargs.index(nv-1)
        if nd in donors or nc in used:continue
        mapped.append([nd,nc]);donors.add(nd);used.add(nc)
    return mapped,dict(old_arcs=len(arcs),exact_signed_nodes_mapped=len(nodeimage),mapped_arcs=len(mapped),
                       discarded=len(arcs)-len(mapped),method='Exact signed source polynomials and actual operand incidence; root uses absent from new DAG are dropped.')


def run(task):
    source,export,public,plan_path,audit_path,interval_path,placement = map(Path,task[:7])
    name,target_text,outroot=task[7:];out=Path(outroot)/name;out.mkdir();start=time.monotonic()
    sys.path.insert(0,str(source/'scripts'))
    from paired_cube.graph import Graph
    from paired_cube.modules import restricted_triples_from,pair_module_from,all_but_one_from
    from paired_cube.frames import basis,perp,contained
    from paired_cube.closure import compile_closure
    from paired_cube.gauges import select
    from paired_cube import verify as native_verify
    from paired_cube_physical import physical
    src=source/'references/paired-cube/sources'
    for filename,digest in json.loads((src/'SOURCE.json').read_text())['files'].items():
        need(sha256((src/filename).read_bytes()).hexdigest()==digest,'source module pin')
    builder=Graph(11)
    graph=builder.finish(restricted_triples_from(src/'h20_g1.json.gz',[0,1,2,3,4,5,6,7,8,9,16]),
                         pair_module_from(src/'pmod_G37_w02_5.6098194e-4.json',10),all_but_one_from(src/'qmod_nested_prefix.json',9))
    graph=full_fusion(graph,builder);graph['matching_frames']='coordinate'
    savedgraph=json.loads((export/'graph.json').read_text())
    for key in ('inputs','labels','args','signs','roots','centers'):
        need(json.loads(json.dumps(graph[key]))==savedgraph[key],'fresh fused graph binding: '+key)
    stub=types.ModuleType('cxlinks')
    for key,value in dict(basis=basis,perp=perp,contained=contained,ROOT=source).items():setattr(stub,key,value)
    sys.modules['cxlinks']=stub
    plan=load_code('rad_carrier_plan',plan_path);adaptation={};mapping_stats={}
    print(name+': construct genuinely new carrier closure/word',flush=True)
    if name=='control':
        arcs=json.loads((export/'frames.json').read_text())['matching_arcs'];initial=len(arcs)
    else:
        if name=='mapped_public':
            oldgraph=json.loads((public/'graph.json').read_text());oldarcs=json.loads((public/'frames.json').read_text())['matching_arcs']
            initial_arcs,mapping_stats=map_public_carriers(oldgraph,graph,oldarcs)
        elif name=='reverse_max':
            text=inspect.getsource(original_matching.matching)
            old='adjacent.append(sorted(set(eligible)))';new='adjacent.append(sorted(set(eligible),reverse=True))'
            need(text.count(old)==1,'matching-order adaptation');ns=dict(original_matching.__dict__)
            exec(compile(text.replace(old,new),'[reversed-maximum-use-order]','exec'),ns)
            initial_arcs,_=ns['matching'](graph);adaptation['maximum_matching']=dict(old=old,new=new)
        else:
            initial_arcs,_=original_matching.matching(graph)
        initial=len(initial_arcs)
        if name=='reverse_greedy':
            text=plan_path.read_text();old='for x in sorted(active):\n        if not args[x]: continue\n        for j, y in enumerate(args[x]):'
            new='for x in sorted(active,reverse=True):\n        if not args[x]: continue\n        for j, y in enumerate(args[x]):'
            need(text.count(old)==1,'carrier-order adaptation');ns=dict(__name__='rad_reversed_carrier',__file__=str(plan_path))
            exec(compile(text.replace(old,new),str(plan_path)+'[reversed-carrier-order]','exec'),ns)
            arcs=ns['extended_arcs'](graph,initial_arcs);adaptation['extended_carrier']=dict(old=old,new=new)
        else:arcs=plan.extended_arcs(graph,initial_arcs)
    baseline,witness=compile_closure(graph,arcs);row,word=select(graph,baseline,witness)
    for filename,data in [('graph.json',graph),('baseline.json',baseline),('frames.json',witness),
                          ('selection.json',word),('selected-profile.json',row),('matching.json',arcs)]:write(out/filename,data)
    text=Path(native_verify.__file__).read_text();old="assert record['selected_roles']==len(seen)==2970 and birth==Counter({18:2970})"
    new="assert record['selected_roles']==len(seen) and birth==Counter({int(k):c for k,c in record['selected_rank_histogram'].items()})"
    need(text.count(old)==1,'native verifier count adaptation');ns=dict(__name__='paired_cube.verify_carriers',__package__='paired_cube')
    exec(compile(text.replace(old,new),'[actual-carrier-count]','exec'),ns)
    checks=ns['verify'](graph,baseline,witness,word,row)
    print(name+': entirely fresh frame/pair construction and component/global continuation',flush=True)
    layer=plan.Layer(graph,witness,word,row);layer.build(rounds=3);moved,pairs=layer.export()
    paid=physical(graph,witness,word,row,moved,pairs)
    context=out/'placement-context'
    (context/'certificates').mkdir(parents=True);(context/'references/paired-cube/physical').mkdir(parents=True)
    (context/'scripts').symlink_to(source/'scripts',target_is_directory=True)
    for filename,data in [('certificates/paired-cube-complex-input.json',row),('certificates/paired-cube-physical-input.json',paid),
                          ('references/paired-cube/physical/frames.json',dict(frames=moved)),
                          ('references/paired-cube/physical/pairs.json',dict(pairs=pairs))]:write(context/filename,data)
    sys.path.insert(0,str(placement));from physical_closure import Closure
    model=Closure(context,out,float(Fraction(target_text)));rng=random.Random(20261009);moves=[]
    for sweep in range(6):
        changed=0
        groups=model.groups('components',rng)
        if sweep%2:groups.reverse()
        for group in groups:
            change=model.change(group)
            if change:moves.append(change);changed+=1
        if not changed:break
    model.global_bounds();global_moves=[]
    for seed in range(len(model.ops)):
        proposal,status=model.proposal(seed,'lower',8192)
        if proposal:
            for op,frame in proposal['frames']:model.frames[op]=tuple(frame)
            global_moves.append({k:v for k,v in proposal.items() if k!='frames'})
    model.validate();hist=model.histogram()
    moved=[[op,list(frame)] for op,frame in enumerate(model.frames) if frame!=model.original[op]]
    paid=physical(graph,witness,word,row,moved,pairs)
    need(hist==paid['child_histogram'],'independent full paid component/global recount')
    write(out/'fresh-physical-inputs.json',dict(frames=moved,pairs=pairs))
    write(out/'physical-profile.json',paid)
    audit=load_code('rad_carrier_exact_core',audit_path)
    events,mutations,cleanup,live,_=audit.prepare(graph,word,pairs,row['R'])
    exact=[oriented(audit,graph,events,mutations,cleanup,live,sign) for sign in (1,-1)]
    intervals=load_code('rad_carrier_intervals',interval_path);target=Fraction(target_text)
    lower,upper=intervals.moment(paid['m'],paid['W_per_vertex'],{int(r):n for r,n in paid['child_histogram'].items()},target)
    result=dict(status='EXACT_FINITE_REBUILT_CARRIER_SCREEN',variant=name,initial_arcs=initial,matched=len(arcs),mapping=mapping_stats,
                adaptations=adaptation,finite_checks=checks,exact_signed_core=exact,c=row['c'],q=row['q'],R=row['R'],
                literal_M=row['total_M_operations'],selected_roles=row['selected_roles'],pairs=len(pairs),physical_R=paid['physical_R'],
                W=paid['W_per_vertex'],m=paid['m'],rank_mass=paid['rank_per_vertex'],deficit=paid['deficit_per_vertex'],
                numerical_complex_root_discovery_only=numerical_root(paid),complete_children=paid['child_histogram'],
                component_moves=len(moves),global_lower_moves=len(global_moves),
                exact_target=dict(saving=str(target),lower=str(lower),upper=str(upper),
                                  classification='ACCEPTED' if upper<1 else 'REJECTED' if lower>1 else 'UNRESOLVED'),
                scalar_charge=finite_scalar_bound(row,paid),wall_seconds=time.monotonic()-start,
                peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='Fresh actual fused168 graph; changed legal carrier choices require fresh closure, gauge selection '
                      'and literal word. Physical frames and pairs freshly built from full intersections, then readonly '
                      'placement component/global APIs descend this exact word. Every scalar, support, chronology and '
                      'complete paid check runs; exact signed dirty core checks both signs. No old word/frame/pair/profile '
                      'transplant. Native-public seeds mapped only by exact signed coefficients and actual operand '
                      'incidence, then independently revalidated through full acyclic closure. All-size transfer and '
                      'independent full complemented reflection remain separate.')
    write(out/'result.json',result)
    print('%s COMPLETE arcs%d ops%d W%d root %.12g %s %.3fs' %
          (name,len(arcs),row['total_M_operations'],paid['W_per_vertex'],result['numerical_complex_root_discovery_only'],
           result['exact_target']['classification'],result['wall_seconds']),flush=True)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source','export','public','plan','exact-core','interval-code','placement-code','output'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--workers',type=int,default=4);p.add_argument('--trial-saving',default='617560360/1000000000000')
    a=p.parse_args();need(not sys.flags.optimize,'assertion-disabled execution rejected')
    a.output.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    variants=['control','reverse_greedy','reverse_max','mapped_public']
    deps=[a.plan,a.exact_core,a.interval_code]+list(a.placement_code.glob('*.py'))
    protocol=dict(started_utc=datetime.now(timezone.utc).isoformat(),variants=variants,workers=a.workers,nested_library_threads=1,
                  source=str(a.source.resolve()),export=str(a.export.resolve()),public_export=str(a.public.resolve()),
                  trial_saving=str(Fraction(a.trial_saving)),driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  dependency_pins={str(path):sha256(path.read_bytes()).hexdigest() for path in deps})
    write(a.output/'protocol.json',protocol)
    tasks=[tuple(str(path.resolve()) for path in (a.source,a.export,a.public,a.plan,a.exact_core,a.interval_code,a.placement_code))+
           (name,a.trial_saving,str(a.output.resolve())) for name in variants]
    rows=[]
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        for future in as_completed([pool.submit(run,task) for task in tasks]):rows.append(future.result())
    rows.sort(key=lambda row:variants.index(row['variant']))
    write(a.output/'batch-result.json',dict(status='COMPLETE_REBUILT_CARRIER_BATCH',results=rows,protocol=protocol,
                                          elapsed_seconds=time.monotonic()-start))


if __name__=='__main__':main()
