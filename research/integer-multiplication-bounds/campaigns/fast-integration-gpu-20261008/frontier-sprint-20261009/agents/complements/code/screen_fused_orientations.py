#!/usr/bin/env python3
"""Legal equal-rank local subspace variants on a complete frozen fused168 plan.

Each extraction recomputes exact support/incoming lower and outgoing upper
spaces, enumerates all small quotient subspaces, changes the actual physical
frame, and checks its complete carrier chains. Three policies change actual
subspaces before identical bounded component descent. All paid child counts
are rebuilt; numeric scores are DISCOVERY. Prepared with GPT-6.1 Sol assistance.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import resource
import sys
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")


def load(path):
    sys.path.insert(0,str(path.parent.resolve()))
    spec=importlib.util.spec_from_file_location("fused_orientation_model",path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def quotient_choices(model,lower,upper,rank):
    extra=[]
    current=lower
    for vector in upper:
        new=model.basis(current+(vector,))
        if len(new)>len(current):
            extra.append(vector)
            current=new
    q,d=len(extra),rank-len(lower)
    if not (q<=6 and 0<d<q and d<=2):
        return None,{"quotient_dimension":q,"selected_quotient_dimension":d,"reason":"enumeration_bound"}
    vectors=[]
    for mask in range(1,1<<q):
        vector=0
        for i,x in enumerate(extra):
            if mask>>i&1:vector^=x
        vectors.append(vector)
    choices=set()
    for candidate in itertools.combinations(vectors,d):
        frame=model.basis(lower+candidate)
        if len(frame)==rank:
            choices.add(frame)
    return sorted(choices),{"quotient_dimension":q,"selected_quotient_dimension":d,
                            "distinct_choices":len(choices),"quotient_generators":extra}


def run(job):
    context,placement_code,variant,output,passes,target,seed=job
    output.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    module=load(placement_code)
    model=module.Physical(context/'source',context/'export',float(target))
    model.frames=list(model.original)
    for i,rows in json.loads((context/'start-frames.json').read_text()):
        model.frames[i]=tuple(rows)
    model.validate()
    startframes=list(model.frames)
    starthist=model.histogram()
    groups=model.groups('components',random.Random(seed))
    strict=[]
    for group in groups:
        lower,upper,_,_=model.endpoints(group)
        if len(lower)<len(model.frames[group[0]])<len(upper):
            strict.append(group)
    rng=random.Random(seed)
    orientations=[]
    for group in strict:
        lower,upper,_,_=model.endpoints(group)
        original=model.frames[group[0]]
        if not len(lower)<len(original)<len(upper):
            continue
        choices,information=quotient_choices(model,lower,upper,len(original))
        if choices is None:
            orientations.append({"group":group,**information})
            continue
        module.require(original in choices,"original frame absent from quotient enumeration")
        alternatives=[frame for frame in choices if frame!=original]
        selected=(original if variant=='control' else alternatives[0] if variant=='first' else
                  alternatives[-1] if variant=='last' else rng.choice(alternatives))
        module.require(len(selected)==len(original) and model.contained(lower,selected)
                       and model.contained(selected,upper),"illegal equal-rank orientation")
        for index in group:model.frames[index]=selected
        # Exact containment after every extraction, including preceding changes.
        model.validate()
        orientations.append({"group":group,"lower":lower,"upper":upper,"original":original,
                             "selected":selected,**information})
    initialhist=model.histogram()
    module.require(initialhist==starthist,"equal-rank orientations changed initial paid histogram")
    orientation_frames=[[i,list(frame)] for i,frame in enumerate(model.frames) if frame!=model.original[i]]
    write(output/'oriented-frames.json',orientation_frames)
    write(output/'orientations.json',orientations)
    moves,records=[],[]
    for iteration in range(passes):
        groups=model.groups('components',random.Random(seed))
        if iteration%2:groups.reverse()
        before=len(moves)
        for group in groups:
            if len({model.frames[i] for i in group})!=1:continue
            change=model.change(group)
            if change:moves.append(change)
        records.append({"pass":iteration,"groups":len(groups),"accepted_moves":len(moves)-before})
        print(json.dumps({"variant":variant,**records[-1]}),flush=True)
        if len(moves)==before:break
    checks=model.validate()
    histogram=model.histogram()
    frames=[[i,list(frame)] for i,frame in enumerate(model.frames) if frame!=model.original[i]]
    write(output/'frames.json',frames)
    write(output/'moves.json',moves)
    paid=model.compiler.physical(model.g,model.witness,model.word,model.record,frames,model.pairs)
    module.require({int(r):n for r,n in paid['child_histogram'].items()}==histogram,
                   "complete independent paid histogram differs from compiler")
    write(output/'profile.json',paid)
    result={"status":"DISCOVERY","variant":variant,"seed":seed,"requested_passes":passes,
        "actual_passes":records,"strict_components_before_rotations":len(strict),
        "rotated_components":sum(entry.get('original')!=entry.get('selected') for entry in orientations
                                 if 'original' in entry),
        "orientation_frame_sha256":sha(output/'oriented-frames.json'),"frames_sha256":sha(output/'frames.json'),
        "complete_histogram":histogram,"m":model.m,"W":paid['W_per_vertex'],
        "rank_mass":paid['rank_per_vertex'],"deficit":paid['deficit_per_vertex'],
        "target":str(target),"start_moments":model.moments(starthist),"moments":model.moments(histogram),
        "moves":len(moves),"exact_geometry":checks,"compiler_checks":paid['checks'],
        "forward_dirty_controls":paid['scalar_replay'],"wall_seconds":time.monotonic()-started,
        "peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "exclusions":["independent literal reflected geometry audit","rigorous moment enclosure",
                      "assembly certification","accepted final kappa"]}
    write(output/'result.json',result)
    return result


def main():
    p=argparse.ArgumentParser()
    for key in ('context','placement-code','output','summary'):
        p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--passes',type=int,default=3)
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--target',type=Fraction,default=Fraction(617560360,10**12))
    p.add_argument('--seed',type=int,default=20261009)
    args=p.parse_args()
    if sys.flags.optimize:raise ValueError('assertion-disabled execution rejected')
    if args.output.exists() or args.summary.exists():raise ValueError('attempt already exists')
    args.output.mkdir(parents=True)
    started=datetime.now(timezone.utc).isoformat()
    jobs=[(args.context.resolve(),args.placement_code.resolve(),variant,args.output.resolve()/variant,
           args.passes,args.target,args.seed) for variant in ('control','first','last','random')]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results=list(pool.map(run,jobs))
    write(args.summary,{"status":"DISCOVERY","started_at_utc":started,
        "source_pin":"98c115b53742b6613ad630de4d493f37b0119da7","context":str(args.context),
        "context_sha256":sha(args.context/'context.json'),"start_frames_sha256":sha(args.context/'start-frames.json'),
        "source_scripts":json.loads((args.context/'context.json').read_text())['source_sha256'],
        "placement_code_sha256":sha(args.placement_code),"harness_sha256":sha(Path(__file__)),
        "workers":args.workers,"target":str(args.target),"results":results})


if __name__=='__main__':main()
