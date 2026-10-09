#!/usr/bin/env python3
"""Joint exact-moment frame/pair continuation on one pinned signed DAG/word.

RaD; GPT-6.1 Sol assistance. Apache-2.0. Reuses PR162's lawful endpoint
and birth-cut selection mechanisms and independently checks literal scalar
dirty-state restoration. Every accepted state has a complete paid recount.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import sha256
import json
import math
from pathlib import Path
import resource
import sys
import time
import types

sys.dont_write_bytecode = True
if hasattr(sys,'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

from screen_pr168_modules import load_code,need,write
from screen_signed_fusion import numerical_root,moment,finite_scalar_bound
from check_pr165_signed_control import oriented


def run(task):
    source,export,initial_frames,plan_path,audit_path,interval_path = map(Path,task[:6])
    name,seed,rounds,passes,target_text,outroot = task[6:]
    out = Path(outroot)/name;out.mkdir();start=time.monotonic()
    protocol=json.loads((export/'protocol.json').read_text())
    for filename,pin in protocol['input_pins'].items():
        need(sha256((export/filename).read_bytes()).hexdigest()==pin['sha256'],'input pin: '+filename)
    graph,witness,word,row = [json.loads((export/name).read_text()) for name in
                              ('graph.json','frames.json','word.json','profile-before.json')]
    frames=json.loads(initial_frames.read_text())
    pairs=json.loads((export/'physical-pairs.json').read_text())
    sys.path.insert(0,str(source/'scripts'))
    from paired_cube.frames import basis,perp,contained
    from paired_cube_physical import physical
    stub=types.ModuleType('cxlinks')
    for key,value in dict(basis=basis,perp=perp,contained=contained,ROOT=source).items():setattr(stub,key,value)
    sys.modules['cxlinks']=stub
    plan=load_code('rad_joint_plan',plan_path)
    target=Fraction(target_text);saving=float(target)
    plan.cost=lambda rank,m: rank*math.expm1(saving*math.log(m/rank))/saving if rank else 0.
    layer=plan.Layer(graph,witness,word,row)
    for op,frame in frames:layer.frames[op]=tuple(frame)
    layer.set_pairs([(a,b) for a,b,deadline in pairs])
    initial=physical(graph,witness,word,row,frames,pairs)
    bestframes,bestpairs,bestpaid=frames,pairs,initial
    bestmoment=moment(initial,saving)
    rounds_log=[]
    for iteration in range(rounds if name!='control' else 0):
        before=time.monotonic()
        layer.descend(seed=seed+2*iteration,passes=passes)
        layer.set_pairs([])
        proposed,fit=layer.pair();proposed=layer.chain_safe(proposed);layer.set_pairs(proposed)
        for donor,_ in proposed:layer.frames[layer.last[donor]]=fit[donor]
        layer.descend(seed=seed+2*iteration+1,passes=passes)
        moved,candidate_pairs=layer.export()
        paid=physical(graph,witness,word,row,moved,candidate_pairs)
        score=moment(paid,saving)
        improved=score<bestmoment-1e-15
        rounds_log.append(dict(round=iteration,pairs=len(candidate_pairs),moved_frames=len(moved),
                               complete_moment=score,numerical_root_discovery_only=numerical_root(paid),
                               best_improved=improved,elapsed_seconds=time.monotonic()-before))
        if improved:
            bestframes,bestpairs,bestpaid=moved,candidate_pairs,paid;bestmoment=score
        else:
            layer.frames=list(layer.default)
            for op,frame in bestframes:layer.frames[op]=tuple(frame)
            layer.set_pairs([(a,b) for a,b,deadline in bestpairs])
        print('%s round%d root %.12g pairs%d best%s' %
              (name,iteration,rounds_log[-1]['numerical_root_discovery_only'],len(candidate_pairs),improved),flush=True)
    audit=load_code('rad_joint_exact_core',audit_path)
    events,mutations,cleanup,live,_=audit.prepare(graph,word,bestpairs,row['R'])
    exact=[oriented(audit,graph,events,mutations,cleanup,live,direction) for direction in (1,-1)]
    intervals=load_code('rad_joint_intervals',interval_path)
    lower,upper=intervals.moment(bestpaid['m'],bestpaid['W_per_vertex'],
                                 {int(r):n for r,n in bestpaid['child_histogram'].items()},target)
    for filename,data in [('physical-frames.json',bestframes),('physical-pairs.json',bestpairs),
                          ('profile.json',bestpaid),('rounds.json',rounds_log)]:write(out/filename,data)
    result=dict(status='EXACT_SIGNED_PAID_JOINT_CONTINUATION',variant=name,seed=seed,rounds=rounds_log,
                graph_sha256=protocol['input_pins']['graph.json']['sha256'],word_sha256=protocol['input_pins']['word.json']['sha256'],
                initial_frames_sha256=sha256(initial_frames.read_bytes()).hexdigest(),
                initial_moment=moment(initial,saving),final_moment=bestmoment,
                initial_numerical_root_discovery_only=numerical_root(initial),
                numerical_complex_root_discovery_only=numerical_root(bestpaid),
                exact_target=dict(saving=str(target),lower=str(lower),upper=str(upper),
                                  classification='ACCEPTED' if upper<1 else 'REJECTED' if lower>1 else 'UNRESOLVED'),
                complete_children=bestpaid['child_histogram'],physical_R=bestpaid['physical_R'],
                W=bestpaid['W_per_vertex'],m=bestpaid['m'],rank_mass=bestpaid['rank_per_vertex'],
                deficit=bestpaid['deficit_per_vertex'],pairs=len(bestpairs),moved_frames=len(bestframes),
                exact_signed_core=exact,scalar_charge=finite_scalar_bound(row,bestpaid),
                elapsed_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='Same exact pinned newly fused168 graph, carrier closure, selected gauges and literal word. '
                      'Continues independently checked placement frames with fresh legal pair selection and endpoint '
                      'descent priced at actual complete moment. Every round gets full physical geometry/profile '
                      'and inherited modular dirty controls; frozen best gets exact integer adjoint under both signs. '
                      'No profile deltas or old-DAG frame transplant. Independent full complemented reflection and '
                      'all-size assembly are separate obligations.')
    write(out/'result.json',result)
    print('%s COMPLETE root %.12g %s %.3fs' %
          (name,result['numerical_complex_root_discovery_only'],result['exact_target']['classification'],result['elapsed_seconds']),flush=True)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source','export','initial-frames','plan','exact-core','interval-code','output'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--rounds',type=int,default=6);p.add_argument('--passes',type=int,default=30)
    p.add_argument('--workers',type=int,default=4);p.add_argument('--trial-saving',default='617042388/1000000000000')
    a=p.parse_args();need(not sys.flags.optimize,'assertion-disabled execution rejected')
    a.output.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    variants=[('control',1),('seed1',1),('seed7',7),('seed31',31)]
    protocol=dict(started_utc=datetime.now(timezone.utc).isoformat(),source=str(a.source.resolve()),
                  immutable_export=str(a.export.resolve()),variants=variants,rounds=a.rounds,passes=a.passes,
                  trial_saving=str(Fraction(a.trial_saving)),workers=a.workers,nested_library_threads=1,
                  dependency_pins={str(path):sha256(path.read_bytes()).hexdigest() for path in
                                   (a.initial_frames,a.plan,a.exact_core,a.interval_code)},
                  driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    write(a.output/'protocol.json',protocol)
    tasks=[tuple(str(path.resolve()) for path in (a.source,a.export,a.initial_frames,a.plan,a.exact_core,a.interval_code))+
           (name,seed,a.rounds,a.passes,a.trial_saving,str(a.output.resolve())) for name,seed in variants]
    rows=[]
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        for future in as_completed([pool.submit(run,task) for task in tasks]):rows.append(future.result())
    rows.sort(key=lambda row:[name for name,seed in variants].index(row['variant']))
    write(a.output/'batch-result.json',dict(status='COMPLETE_JOINT_PAID_SCREEN',results=rows,protocol=protocol,
                                          elapsed_seconds=time.monotonic()-start))


if __name__=='__main__':main()
