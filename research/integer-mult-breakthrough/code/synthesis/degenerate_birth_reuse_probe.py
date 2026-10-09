#!/usr/bin/env python3
"""Birth-cut dirty reuse through a degenerate actual common Clifford frame.

This independent small component combines response cuts with L_E radical
frames. Complete physical controls retain source, sink, old dirty values,
true reverse chronology, all affine/chirp wrappers and payload columns.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

import canonical_geodesic_side_review as d
cf=d.cf


def clean_events(reuse):
    r0,r1=2,2 if reuse else 3
    return [('birth',0),('birth',1),('source',0,0,1),('source',1,1,1),
            ('birth',r0),('gate',r0,0,1),('gate',r0,1,1),('read',r0,0,1),
            ('birth',r1),('gate',r1,0,2),('gate',r1,1,3),('read',r1,1,1)]


def responses(events,roles,cut=True):
    rows=[[0,0] for _ in range(roles)];sources=[[0,0] for _ in range(2)];birth={}
    for index in range(len(events)-1,-1,-1):
        kind,a,*rest=events[index]
        if kind=='read':target,c=rest;rows[a][target]+=c
        elif kind=='gate':b,c=rest;rows[b]=[x+c*y for x,y in zip(rows[b],rows[a])]
        elif kind=='source':b,c=rest;sources[b]=[x+c*y for x,y in zip(sources[b],rows[a])]
        else:
            birth[index]=tuple(rows[a])
            if cut:rows[a]=[0,0]
    return birth,sources,rows


def schedule(reuse):
    h=4;U=(1,7);T=(8,14);E=cf.basis(U);full=tuple(1<<j for j in range(h));roles=3 if reuse else 4
    logical=clean_events(reuse);birth,sources,remaining=responses(logical,roles)
    if sources!=[[1,2],[1,3]] or any(any(row) for row in remaining):
        raise ValueError('Backward CUT responses do not match the complete clean map')
    frames={j:cf.basis((label,)) for j,label in enumerate(U)}
    frames.update({j:() for j in range(2,4+roles)});initial=dict(frames)
    events=[];forward=[];operators={};actual_frames={};hist=Counter();birth_indices={}
    def frame(F):
        F=cf.basis(F)
        if F not in actual_frames:actual_frames[F]=d.bind_frame(F,h)
        return actual_frames[F]
    def move(role,F):
        F=cf.basis(F);before=frames[role]
        if before==F:return
        key=(before,F)
        if key not in operators:
            rising=len(F)>=len(before);low,high=(before,F) if rising else (F,before)
            nf=cf.compile_nested(low,high,h);M,bits=cf.relative_matrix(frame(low),frame(high))
            operators[key]=(M,bits,not rising,nf)
        events.append(('move',role,key));hist[operators[key][3]['selected_rank_per_column']]+=1;frames[role]=F
    def add(a,b,c,remember=False):
        if frames[a]!=frames[b]:raise ValueError('Birth/read/workspace scalar gate has unequal actual operators')
        events.append(('add',a,b,Q(c)))
        if remember:forward.append((a,b,Q(c)))
    for index,event in enumerate(logical):
        kind,a,*rest=event;role=4+a
        if index==4:
            for target in range(2):move(2+target,E)
            for input_role in (4,5):move(input_role,E)
        if kind=='birth':
            if a>=2:move(role,E)
            birth_indices[index]=len(events)
            events.append(('birth-response',role,index,birth[index]))
            for target,c in enumerate(birth[index]):
                if c and frames[2+target]!=frames[role]:raise ValueError('Old response is not paid in a common actual frame')
        elif kind=='source':
            source,c=rest;move(role,(U[source],));add(role,source,c,True)
        elif kind=='gate':b,c=rest;add(role,4+b,c,True)
        else:target,c=rest;add(2+target,role,c)
    for target,label in enumerate(T):move(2+target,cf.perpendicular((label,),h))
    for source in range(2):move(source,full)
    for auxiliary in range(4,4+roles):move(auxiliary,full)
    for a,b,c in reversed(forward):add(a,b,-c)
    for F in set(initial.values())|set(frames.values()):frame(F)
    stock=4+roles;rank=sum(width*count for width,count in hist.items())
    if rank!=stock*h-4:raise ValueError('Actual birth-reuse component did not preserve its endpoint deficit')
    radical=2*len(E)-len(cf.basis(E+cf.perpendicular(E,h)))
    if radical!=1:raise ValueError('The chosen common frame is not genuinely degenerate')
    return dict(h=h,U=U,T=T,E=E,radical=radical,logical=logical,responses=birth,
                events=events,operators=operators,frames=actual_frames,initial=initial,final=frames,
                stock=stock,reuse=reuse,histogram=dict(sorted(hist.items())),rank=rank,deficit=stock*h-rank)


def execute(spec,data,columns,negative=None):
    data=list(data);actual_birth_values=[]
    response=responses(spec['logical'],spec['stock']-4,False)[0] if negative=='no CUT at later births' else spec['responses']
    for event in spec['events']:
        if event[0]=='move':
            _,role,key=event;M,bits,inverse,nf=spec['operators'][key]
            data[role]=d.apply_matrix(data[role],M,bits,spec['h'],columns,inverse)
        elif event[0]=='add':_,a,b,c=event;data[a]=d.plus(data[a],data[b],c)
        else:
            _,role,index,coefficients=event;actual_birth_values.append((index,data[role]))
            if negative=='omit reuse response' and index==8:continue
            for target,c in enumerate(response[index]):
                if c:data[2+target]=d.plus(data[2+target],data[role],Q(-c))
    return data,actual_birth_values


def expected(spec,data,columns):
    virtual=[d.apply_matrix(a,spec['frames'][spec['initial'][role]]['numerator'],
                            spec['frames'][spec['initial'][role]]['denominator_bits'],4,columns,True)
             for role,a in enumerate(data)]
    virtual[2]=d.plus(d.plus(virtual[2],virtual[0],Q(1)),virtual[1],Q(1))
    virtual[3]=d.plus(d.plus(virtual[3],virtual[0],Q(2)),virtual[1],Q(3))
    return [d.apply_matrix(a,spec['frames'][spec['final'][role]]['numerator'],
                            spec['frames'][spec['final'][role]]['denominator_bits'],4,columns)
             for role,a in enumerate(virtual)]


def probe(case):
    reuse,columns=case;start=time.monotonic();spec=schedule(reuse);stock=spec['stock'];size=1<<(4*columns)
    digest=sha256();checked=0;dependent=0
    for role in range(stock):
        for address in range(size) if columns==1 else (0,):
            data=[(tuple((int(bank==role and x==address),0) for x in range(size)),0) for bank in range(stock)]
            actual,births=execute(spec,data,columns)
            if actual!=expected(spec,data,columns):raise ValueError('A complete source/sink/dirty physical basis column failed')
            if role<2 and any(index==8 and any(a or b for a,b in value[0]) for index,value in births):dependent+=1
            digest.update(str(actual).encode());checked+=1
    fields=3
    for field in range(fields):
        data=[d.normalize([((x*7+role*11+field*3)%31-15,(x*13+role*5+field*17)%29-14)
                          for x in range(size)],(field+role)%4) for role in range(stock)]
        actual,births=execute(spec,data,columns);wanted=expected(spec,data,columns)
        if actual!=wanted:raise ValueError('A complete Gaussian arbitrary-dirty field failed')
        digest.update(str(actual).encode())
    controls={}
    if reuse:
        for name in ('no CUT at later births','omit reuse response'):
            controls[name]=execute(spec,data,columns,name)[0]!=wanted
        if not all(controls.values()) or dependent==0:raise ValueError('A correlated reuse birth negative/control did not discriminate')
    # Wrong raw identity on dirty values is independently rejected.
    if all(wanted[role]==data[role] for role in range(4,stock)):
        raise ValueError('The dirty physical full-C endpoint control failed')
    return dict(status='PASS LITERAL DEGENERATE BIRTH-CUT REUSE',reuse=reuse,columns=columns,
                ambient_dimension=4,source_labels=spec['U'],target_labels=spec['T'],common_subspace=spec['E'],
                common_radical_dimension=spec['radical'],payload_stock=stock,capacity=4*stock,
                rank_charge=spec['rank'],deficit=spec['deficit'],child_width_histogram=spec['histogram'],
                complete_physical_columns=stock*size,explicit_initial_columns=checked,
                coverage='All physical basis columns' if columns==1 else 'Origin columns plus3completeGaussianfields; no covariance promotion',
                complete_gaussian_fields=fields,full_field_values=fields*stock*size,
                source_dependent_nonzero_reuse_births=dependent,
                exact_future_birth_cut_responses={str(index):row for index,row in spec['responses'].items()},
                clean_virtual_maps=['y0+=x0+x1','y1+=2x0+3x1'],
                virtual_sources_and_all_dirty_restored=True,actual_dirty_final='C_full times original dirty',
                recipient_direct_source_injections=False,all_actual_gate_frames_equal=True,
                negative_controls=controls,output_sha256=digest.hexdigest(),seconds=time.monotonic()-start,
                scope='A complete finite arbitrary-dirty side component, including a nonzero radical actual frame and dependent birth offsets. It does not implement a whole framed identity/signed exchange, canonical C_h primitive, native tape theorem or new multiplier exponent.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=4);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    cases=[(False,1),(True,1),(False,2),(True,2)];root=Path(__file__).resolve().parents[1]
    sources=sorted({Path(module.__file__).resolve() for module in sys.modules.values()
                    if getattr(module,'__file__',None) and Path(module.__file__).resolve().is_relative_to(root)
                    and Path(module.__file__).suffix=='.py'}|{Path(__file__).resolve(),d.center_word.f.SIDE_SOURCE.resolve()})
    hashes={p:sha256(p.read_bytes()).hexdigest() for p in sources}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,
                  cases=cases,seed=None,source_sha256={str(p.relative_to(root)):value for p,value in hashes.items()},
                  scalar_domain='Exact integer Gaussian numerator/common dyadic bank grid',
                  motivating_readonly_reference='PR127 ca8725485a822769f24c2e4e9b8955b31a42b044 birth-cut lemma; no reference producer imports',
                  hypothesis='A dead role can be reused at a degenerate common birth frame, with exact CUT responses and full dirty restoration, removing one full-width role path.')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,case):case for case in cases}
        for future in as_completed(jobs):
            result=future.result();results.append(result)
            print(json.dumps({key:result[key] for key in ('status','reuse','columns','rank_charge','payload_stock','deficit','seconds')}),flush=True)
    if any(sha256(p.read_bytes()).hexdigest()!=value for p,value in hashes.items()):
        raise ValueError('A source changed during the birth-cut experiment')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results),indent=2)+'\n')


if __name__=='__main__':main()
