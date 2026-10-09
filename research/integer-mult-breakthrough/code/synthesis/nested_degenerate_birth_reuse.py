#!/usr/bin/env python3
"""One unrestored dirty role reused across strictly growing actual births.

The donor frame has a radical; the recipient is a larger pinned frame.
CUT offsets can be source-dependent. All real gates reverse only at full.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

import degenerate_birth_reuse_probe as b
d = b.d
cf = b.cf


def schedule(reuse):
    h=4; U=(1,7); T=(8,14); E=cf.basis(U)
    recipient=cf.perpendicular((T[1],),h)
    full=tuple(1<<j for j in range(h)); helpers=3 if reuse else 4
    logical=b.clean_events(reuse); responses,sources,rest=b.responses(logical,helpers)
    if sources!=[[1,2],[1,3]] or any(any(row) for row in rest):
        raise ValueError('The CUT map does not give the declared clean side transform')
    frames={0:cf.basis((U[0],)),1:cf.basis((U[1],))}
    frames.update({j:() for j in range(2,4+helpers)}); initial=dict(frames)
    events=[]; forward=[]; operators={}; actual={}; histogram=Counter()
    def frame(E):
        E=cf.basis(E)
        if E not in actual:actual[E]=d.bind_frame(E,h)
        return actual[E]
    def move(role,F):
        F=cf.basis(F); before=frames[role]
        if before==F:return
        key=(before,F)
        if key not in operators:
            rising=len(F)>=len(before); low,high=(before,F) if rising else (F,before)
            nf=cf.compile_nested(low,high,h)
            M,bits=cf.relative_matrix(frame(low),frame(high))
            operators[key]=(M,bits,not rising,nf)
        events.append(('move',role,key)); histogram[operators[key][3]['selected_rank_per_column']]+=1
        frames[role]=F
    def add(a,z,c,remember=False):
        if frames[a]!=frames[z]:raise ValueError('A strictly nested birth has unequal actual gate frames')
        events.append(('add',a,z,Q(c)))
        if remember:forward.append((a,z,Q(c)))
    for index,event in enumerate(logical):
        kind,a,*extra=event; role=4+a
        if index==4:
            for target in (2,3):move(target,E)
            for helper in (4,5):move(helper,E)
        if index==8:
            # The first read is complete. Retire its sink; advance the
            # continuing sink and operands to the larger future birth.
            move(2,cf.perpendicular((T[0],),h)); move(3,recipient)
            for helper in (4,5):move(helper,recipient)
        if kind=='birth':
            if a>=2:move(role,E if index==4 else recipient)
            for target,c in enumerate(responses[index]):
                if c and frames[2+target]!=frames[role]:
                    raise ValueError('The CUT response is not in the actual recipient birth frame')
            events.append(('birth-response',role,index,responses[index]))
        elif kind=='source':
            source,c=extra; move(role,(U[source],)); add(role,source,c,True)
        elif kind=='gate':source,c=extra; add(role,4+source,c,True)
        else:target,c=extra; add(2+target,role,c)
    for source in (0,1):move(source,full)
    for helper in range(4,4+helpers):move(helper,full)
    for a,z,c in reversed(forward):add(a,z,-c)
    for F in set(initial.values())|set(frames.values()):frame(F)
    rank=sum(width*count for width,count in histogram.items()); stock=4+helpers
    if rank!=4*stock-4:raise ValueError('The strict pair did not preserve the first-moment deficit')
    if len(E)!=2 or len(recipient)!=3 or len(cf.basis(E+recipient))!=3:
        raise ValueError('The actual old/new birth is not strictly nested')
    return dict(h=h,U=U,T=T,E=E,recipient=recipient,radical=1,logical=logical,responses=responses,
                events=events,operators=operators,frames=actual,initial=initial,final=frames,
                stock=stock,reuse=reuse,histogram=dict(sorted(histogram.items())),rank=rank,deficit=4)


def grouped_uninject(spec,data,columns):
    data=list(data);last=next(i for i in range(len(spec['events'])-1,-1,-1)
                             if spec['events'][i][0]=='move')+1
    prefix=dict(spec); prefix['events']=spec['events'][:last]
    data,_=b.execute(prefix,data,columns)
    undo=spec['events'][last:]
    source_first=[e for e in undo if e[0]=='add' and e[2]<2]
    others=[e for e in undo if not(e[0]=='add' and e[2]<2)]
    for _,a,z,c in source_first+others:data[a]=d.plus(data[a],data[z],c)
    return data


def probe(case):
    reuse,columns=case;start=time.monotonic();spec=schedule(reuse);stock=spec['stock'];size=1<<(4*columns)
    digest=sha256();checked=0;dependent=0
    for role in range(stock):
        for address in range(size) if columns==1 else (0,):
            initial=[(tuple((int(bank==role and x==address),0) for x in range(size)),0) for bank in range(stock)]
            actual,births=b.execute(spec,initial,columns)
            if actual!=b.expected(spec,initial,columns):raise ValueError('Strict birth failed a complete physical initial column')
            if role<2 and any(index==8 and any(a or z for a,z in value[0]) for index,value in births):dependent+=1
            digest.update(str(actual).encode());checked+=1
    for field in range(3):
        initial=[d.normalize([((x*7+role*11+field*3)%31-15,(x*13+role*5+field*17)%29-14)
                               for x in range(size)],(field+role)%4) for role in range(stock)]
        actual,births=b.execute(spec,initial,columns);wanted=b.expected(spec,initial,columns)
        if actual!=wanted:raise ValueError('Strict birth failed a complete arbitrary-dirty Gaussian field')
        digest.update(str(actual).encode())
    controls={}
    if reuse:
        controls={name:b.execute(spec,initial,columns,name)[0]!=wanted
                  for name in ('no CUT at later births','omit reuse response')}
        if not all(controls.values()) or dependent==0:raise ValueError('The correlated strict birth controls did not discriminate')
    controls['grouped source uninject before workspace undo']=grouped_uninject(spec,initial,columns)!=wanted
    if not controls['grouped source uninject before workspace undo']:
        raise ValueError('A false grouped inverse source schedule passed')
    if all(wanted[j]==initial[j] for j in range(4,stock)):
        raise ValueError('The wrong raw dirty target was not distinguished')
    return dict(status='PASS STRICT NESTED DEGENERATE DIRTY BIRTH REUSE',reuse=reuse,columns=columns,
                source_labels=spec['U'],target_labels=spec['T'],donor_frame=spec['E'],recipient_frame=spec['recipient'],
                donor_dimension=2,donor_radical_dimension=1,recipient_dimension=3,
                explicit_initial_columns=checked,complete_physical_columns=stock*size,
                coverage='All physical basis columns' if columns==1 else 'All bank origins plus3completeGaussianfields; no covariance promotion',
                complete_gaussian_fields=3,full_field_values=3*stock*size,
                payload_stock=stock,capacity=4*stock,rank_charge=spec['rank'],deficit=4,
                child_width_histogram=spec['histogram'],
                removed_child_widths=[2,3] if reuse else None,added_child_width=1 if reuse else None,
                source_dependent_nonzero_recipient_births=dependent,clean_maps=['y0+=x0+x1','y1+=2x0+3x1'],
                actual_dirty_final='C_full times original virtual dirty',all_virtual_dirty_and_sources_restored=True,
                scalar_word_lives_unrestored_until_final_inverse=True,negative_controls=controls,
                all_actual_scalar_frames_equal=True,output_sha256=digest.hexdigest(),seconds=time.monotonic()-start,
                scope='Complete finite two-life side component with strictly nested degenerate donor, source-dependent CUT offset, and one final true-chronology uncompute. No complete identity/SWAP, native tape theorem or multiplier exponent follows.')


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
                  hypothesis='A degenerate donor can continue into a strictly larger actual recipient birth, preserving one geodesic helper path and improving the complete moment profile.',
                  scalar_domain='Exact integer Gaussian numerator/common per-bank dyadic grid')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,case):case for case in cases}
        for future in as_completed(jobs):
            result=future.result();results.append(result)
            print(json.dumps({key:result[key] for key in ('status','reuse','columns','rank_charge','payload_stock','seconds')}),flush=True)
    if any(sha256(p.read_bytes()).hexdigest()!=value for p,value in hashes.items()):
        raise ValueError('A source changed during the strict degenerate birth experiment')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results),indent=2)+'\n')


if __name__=='__main__':main()
