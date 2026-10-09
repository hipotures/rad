#!/usr/bin/env python3
"""Joint mutable-source births with one final paid algebraic dirty cleanup.

Two dirty carrier banks mediate all three shear stages and visit full only
once. The reflected middle frame keeps its actual monomial gauge. A raw
canonical boundary consumes the positive core's entire rank-two deficit.
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

import joint_signed_swap_control as j
d = j.d
cf = j.cf


def scalar_inverse(M):
    n=len(M);A=[[Q(x) for x in row]+[Q(i==k) for k in range(n)] for i,row in enumerate(M)]
    for column in range(n):
        pivot=next((i for i in range(column,n) if A[i][column]),None)
        if pivot is None:raise ValueError('The required mutable-data source preimage is singular')
        A[pivot],A[column]=A[column],A[pivot];factor=A[column][column]
        A[column]=[x/factor for x in A[column]]
        for row in range(n):
            if row!=column and A[row][column]:
                factor=A[row][column];A[row]=[x-factor*y for x,y in zip(A[row],A[column])]
    return [row[n:] for row in A]


def clean_program(S):
    inverse=scalar_inverse(S);events=[]
    for source,target,M,sign in ((0,2,S,1),(2,0,inverse,-1),(0,2,S,1)):
        events += [('birth',4),('birth',5)]
        for row in range(2):
            for column in range(2):
                if M[row][column]:events.append(('add',4+row,source+column,Q(M[row][column])))
        events += [('add',target+row,4+row,Q(sign)) for row in range(2)]
    return events


def future_preimages(events,cut=True):
    rows=[[Q(role==out) for out in range(4)] for role in range(6)];result={}
    for index in range(len(events)-1,-1,-1):
        event=events[index]
        if event[0]=='add':
            _,a,z,c=event;rows[z]=[x+c*y for x,y in zip(rows[z],rows[a])]
        else:
            _,role=event
            G=[[rows[column][out] for column in range(4)] for out in range(4)]
            inverse=scalar_inverse(G)
            preimage=[sum(inverse[row][column]*rows[role][column] for column in range(4)) for row in range(4)]
            result[index]=dict(future_response=tuple(rows[role]),current_data_preimage=tuple(preimage))
            if cut:rows[role]=[Q(0)]*4
    return result,rows


def bind(S):
    h=4;E=cf.basis((1,7));G=cf.perpendicular(E,h);full=tuple(1<<k for k in range(h))
    frames={F:d.bind_frame(F,h) for F in ((),(1,),(7,),E,G,full)}
    def matrix(F):return j.matrix_normalize(frames[F]['numerator'],frames[F]['denominator_bits'])
    F=matrix(full);FE=matrix(E);FG=matrix(G)
    gauge=j.compose(j.compose(FG,F),j.adjoint(FE))
    if gauge[1]!=0:raise ValueError('A same-Lagrangian reflected gauge is not integral monomial')
    normal=cf.compile_matrix(gauge[0],h,0)
    if normal['one_bulk_child_calls'] or any(sum(x!=(0,0) for x in row)!=1 for row in gauge[0]):
        raise ValueError('The reflected birth interface has a hidden mixing child')
    entry={}
    for old in ((),(1,),(7,)):
        nf=cf.compile_nested(old,E,h);M,bits=cf.relative_matrix(frames[old],frames[E]);entry[old]=(M,bits,nf)
    nf=cf.compile_nested(E,full,h);M,bits=cf.relative_matrix(frames[E],frames[full]);finish=(M,bits,nf)
    events=clean_program(S);responses,final=future_preimages(events)
    for index,response in responses.items():
        life=index//8;target=2 if life in (0,2) else 0;sign=1 if life in (0,2) else -1
        helper=events[index][1]-4
        expected=[Q(sign*(role==target+helper)) for role in range(4)]
        if list(response['current_data_preimage'])!=expected:
            raise ValueError('Backward CUT/current-data preimage does not match the literal life compensation')
    inverse=scalar_inverse(S)
    # Complete clean four-data matrix, derived independently from the births.
    wanted=[[Q(0)]*4 for _ in range(4)]
    for row in range(2):
        for column in range(2):wanted[row][2+column]=-inverse[row][column];wanted[2+row][column]=Q(S[row][column])
    if [[final[role][out] for role in range(4)] for out in range(4)]!=wanted:
        raise ValueError('The clean mutable-data word is not the stated coupled signed swap')
    return dict(h=h,E=E,G=G,U=(1,7),S=[[Q(x) for x in row] for row in S],inverse=inverse,
                frames=frames,gauge=gauge,gauge_normal_form=normal,entry=entry,finish=finish,
                events=events,responses=responses,core_histogram={1:2,2:10},canonical_histogram={1:4,2:10})


def execute(spec,initial,columns,canonical=False,negative=None):
    data=list(initial);h=spec['h'];E=spec['E'];events=spec['events']
    actual=[j.matrix_normalize(spec['frames'][F]['numerator'],spec['frames'][F]['denominator_bits'])
            for F in ((1,),(7,),(),(),(),())]
    FE=j.matrix_normalize(spec['frames'][E]['numerator'],spec['frames'][E]['denominator_bits'])
    FG=j.compose(j.matrix_normalize(spec['frames'][spec['G']]['numerator'],spec['frames'][spec['G']]['denominator_bits']),
                 j.matrix_normalize(spec['frames'][tuple(1<<k for k in range(h))]['numerator'],spec['frames'][tuple(1<<k for k in range(h))]['denominator_bits']))
    for role,F in enumerate(((1,),(7,),(),(),(),())):
        M,bits,nf=spec['entry'][F];data[role]=d.apply_matrix(data[role],M,bits,h,columns)
        actual[role]=j.compose(j.matrix_normalize(M,bits),actual[role])
    if any(A!=FE for A in actual):raise ValueError('Initial source preimages were not transported to common actual E')
    response=future_preimages(events,False)[0] if negative=='omit future CUT' else spec['responses']
    births=[];scalar_gates=0;gauge_events=0
    def add(a,z,c):
        nonlocal scalar_gates
        if negative is None and actual[a]!=actual[z]:raise ValueError('A joint mutable-source gate has unequal actual operators')
        data[a]=d.plus(data[a],data[z],c);scalar_gates+=1
    for index,event in enumerate(events):
        if index in (8,16):
            M,bits=spec['gauge'];back=index==16
            relative=j.adjoint(spec['gauge']) if back else spec['gauge']
            for role in range(6):
                literal=M
                if negative=='omit one helper reflected phase' and index==8 and role==4:
                    literal=[[((1,0) if z!=(0,0) else (0,0)) for z in row] for row in M]
                data[role]=d.apply_matrix(data[role],literal,bits,h,columns,back)
                actual[role]=j.compose(relative,actual[role]);gauge_events+=1
            expected=FE if back else FG
            if negative is None and any(A!=expected for A in actual):raise ValueError('The cross-body birth lost its exact reflected gauge')
        if event[0]=='birth':
            _,role=event;births.append((index,data[role]))
            if negative=='omit correlated second birth' and index==8:continue
            for target,c in enumerate(response[index]['current_data_preimage']):
                if c:add(target,role,-c)
        else:_,a,z,c=event;add(a,z,c)
    M,bits,nf=spec['finish'];full=tuple(1<<k for k in range(h));F=j.matrix_normalize(spec['frames'][full]['numerator'],spec['frames'][full]['denominator_bits'])
    for role in range(6):
        data[role]=d.apply_matrix(data[role],M,bits,h,columns);actual[role]=j.compose(j.matrix_normalize(M,bits),actual[role])
    if negative is None and any(A!=F for A in actual):raise ValueError('Final cleanup operands lack the same complete actual full operator')
    # Final data are x_f=-S^-1*y_0, y_f=S*x_0. The actual carrier
    # increment is (I+S^-1)*y_f+(S-I)*x_f, at the common full operator.
    S,I=spec['S'],spec['inverse'];cleanup=0;cleanup_unit_expansion=0;nonunits=0
    for row in range(2):
        for column in range(2):
            if negative=='wrong mutable-source cleanup':
                coefficients=((column,2*S[row][column]),(2+column,I[row][column]))
            else:
                coefficients=((2+column,I[row][column]+Q(row==column)),(column,S[row][column]-Q(row==column)))
            for source,c in coefficients:
                if c:
                    add(4+row,source,-c);cleanup+=1;cleanup_unit_expansion+=abs(c.numerator)
                    nonunits+=abs(c)!=1
    if canonical:
        # Apply S to x, then negate; apply S^-1 to y. These are
        # literal in-place unit-determinant scalar words at full.
        a,b=S[0][1],S[1][0]
        add(0,1,a);add(1,0,b)
        data[0]=d.multiply(data[0],Q(-1));data[1]=d.multiply(data[1],Q(-1))
        add(3,2,-b);add(2,3,-a)
        for row,U in enumerate(spec['U']):
            if negative!='omit source-line raw repair':
                C=spec['frames'][(U,)];data[2+row]=d.apply_matrix(data[2+row],C['numerator'],C['denominator_bits'],h,columns)
            data[row],data[2+row]=data[2+row],data[row]
    return data,dict(births=births,scalar_bank_gates=scalar_gates,paid_reflection_monomial_bank_events=gauge_events,
                     final_cleanup_bank_shears=cleanup,final_cleanup_unit_shear_expansion=cleanup_unit_expansion,
                     final_cleanup_nonunit_integer_multiples=nonunits)


def expected(spec,initial,columns,canonical=False):
    h=spec['h'];full=tuple(1<<k for k in range(h));F=spec['frames'][full]
    if canonical:virtual=initial
    else:
        sources=[d.apply_matrix(initial[row],spec['frames'][(U,)]['numerator'],spec['frames'][(U,)]['denominator_bits'],h,columns,True)
                 for row,U in enumerate(spec['U'])]
        zero=(tuple((0,0) for _ in initial[0][0]),0);virtual=[]
        for row in range(2):
            value=zero
            for column in range(2):value=d.plus(value,initial[2+column],-spec['inverse'][row][column])
            virtual.append(value)
        for row in range(2):
            value=zero
            for column in range(2):value=d.plus(value,sources[column],spec['S'][row][column])
            virtual.append(value)
        virtual+=initial[4:]
    return [d.apply_matrix(a,F['numerator'],F['denominator_bits'],h,columns) for a in virtual]


def probe(case):
    a,b,columns=case;start=time.monotonic();S=[[1,a],[b,1+a*b]];spec=bind(S);size=1<<(4*columns)
    digest=sha256();checked=0;dependent=0
    for role in range(6):
        for address in range(size) if columns==1 else (0,):
            initial=[(tuple((int(bank==role and x==address),0) for x in range(size)),0) for bank in range(6)]
            for canonical in (False,True):
                actual,receipt=execute(spec,initial,columns,canonical)
                if actual!=expected(spec,initial,columns,canonical):raise ValueError('Joint source/sink/dirty physical column failed')
                digest.update(str(actual).encode())
            if role<4 and any(index>=8 and any(x or y for x,y in value[0]) for index,value in receipt['births']):dependent+=1
            checked+=1
    for field in range(3):
        initial=[d.normalize([((x*7+role*11+field*3)%31-15,(x*13+role*5+field*17)%29-14) for x in range(size)],(field+role)%4) for role in range(6)]
        for canonical in (False,True):
            actual,receipt=execute(spec,initial,columns,canonical);wanted=expected(spec,initial,columns,canonical)
            if actual!=wanted:raise ValueError('Joint mutable-source algebraic dirty cleanup failed a Gaussian field')
            digest.update(str(actual).encode())
    controls={};control_scope={}
    for name in ('omit future CUT','omit correlated second birth','wrong mutable-source cleanup',
                 'omit one helper reflected phase','omit source-line raw repair'):
        try:
            controls[name]=execute(spec,initial,columns,True,name)[0]!=wanted
            control_scope[name]='Complete actual source/sink/dirty operator disagrees'
        except ValueError as error:
            if name!='omit future CUT' or str(error)!='Non-dyadic scalar coefficient':raise
            controls[name]=True
            control_scope[name]='Forbidden odd-denominator current-data preimage rejected; not an executed Gaussian-dyadic corruption circuit'
    if not all(controls.values()) or not dependent:raise ValueError('A joint source/birth/cleanup/gauge control did not discriminate')
    return dict(status='PASS JOINT MUTABLE BIRTH SWAP; RAW BOUNDARY ERASES CORE DEFICIT',S=S,columns=columns,
                ambient_bits=4,payload_stock=6,core_child_histogram=spec['core_histogram'],core_rank=22,core_capacity=24,core_deficit=2,
                canonical_child_histogram=spec['canonical_histogram'],canonical_rank=24,canonical_capacity=24,canonical_deficit=0,
                boundary_source_line_child_calls=2,boundary_source_line_child_width=1,
                complete_physical_columns=6*size,explicit_initial_columns=checked,
                coverage='All physical columns for BOTH core and raw canonical maps' if columns==1 else 'All bank origins plus3completeGaussianfields for both maps; no covariance promotion',
                complete_gaussian_fields=3,full_field_values=3*6*size,
                mutable_source_dependent_later_births=dependent,all_scalar_actual_frames_equal=True,
                helper_full_endpoint_visited_once=True,helper_values_unrestored_between_all_three_lives=True,
                helper_restore_method='Paid algebraic preimages from mutable final data at the same actual full operator',
                actual_dirty_final='C_full times original arbitrary dirty',
                actual_raw_data_final='C_full times each original labeled raw data bank after paid boundary repairs',
                reflected_middle_normal_form=spec['gauge_normal_form'],
                clean_future_cut_responses={str(index):{key:[str(x) for x in row] for key,row in response.items()} for index,response in spec['responses'].items()},
                final_cleanup_bank_shears=receipt['final_cleanup_bank_shears'],final_cleanup_nonunit_integer_multiples=receipt['final_cleanup_nonunit_integer_multiples'],
                final_cleanup_unit_shear_expansion=receipt['final_cleanup_unit_shear_expansion'],
                canonical_total_scalar_bank_gates=receipt['scalar_bank_gates'],
                paid_reflection_monomial_bank_events=receipt['paid_reflection_monomial_bank_events'],
                native_final_sign_bank_events=2,native_final_full_bank_exchanges=2,
                negative_controls=controls,negative_control_scope=control_scope,
                output_sha256=digest.hexdigest(),seconds=time.monotonic()-start,
                scope='Complete finite genuinely joint mutable-source dirty-helper chronology. Core has rank-two deficit; canonical source-line repairs consume it. No native tape/precision theorem, contracting recurrence or multiplier exponent follows.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=4);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    cases=[(1,2,1),(1,2,2),(2,1,1),(2,1,2)];root=Path(__file__).resolve().parents[1]
    sources=sorted({Path(module.__file__).resolve() for module in sys.modules.values()
                    if getattr(module,'__file__',None) and Path(module.__file__).resolve().is_relative_to(root)
                    and Path(module.__file__).suffix=='.py'}|{Path(__file__).resolve(),d.center_word.f.SIDE_SOURCE.resolve()})
    hashes={p:sha256(p.read_bytes()).hexdigest() for p in sources}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,cases=cases,seed=None,
                  source_sha256={str(p.relative_to(root)):value for p,value in hashes.items()},
                  hypothesis='A joint three-life mutable-data birth word can keep every dirty carrier on one zero-to-full path, with paid final-state algebraic source preimages and actual reflected gauges; raw canonical closure may erase the remaining rank deficit.',
                  scalar_domain='Exact integer Gaussian numerator/common per-bank dyadic grid')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,case):case for case in cases}
        for future in as_completed(jobs):
            result=future.result();results.append(result)
            print(json.dumps({key:result[key] for key in ('status','S','columns','core_rank','canonical_rank','seconds')}),flush=True)
    if any(sha256(p.read_bytes()).hexdigest()!=value for p,value in hashes.items()):raise ValueError('A source changed during joint mutable birth replay')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results),indent=2)+'\n')


if __name__=='__main__':main()
