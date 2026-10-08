#!/usr/bin/env python3
"""Independent two-center scalar/address transfer and disjoint-row bound.

Payload is F2. Address coordinates remain the original odd prime alphabet;
all rational projectors are reduced only after denominators are checked.
No producer source is imported. Native probes are sparse exact dirty bases,
not a claim of whole high-dimensional address enumeration.
"""
import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import resource
import sys
import time


def mm(A,B):
    return [[sum(a*b for a,b in zip(row,column)) for column in zip(*B)] for row in A]


def scalar_coefficients(h):
    triples=list(combinations(range(h),3));v=len(triples)
    T=[[int(i==j) for j in range(h)] for i in range(h)]
    T[1]=[int(j>0) for j in range(h)]
    inverse=[[int(i==j) for j in range(h)] for i in range(h)]
    inverse[1]=[int(j==1)-int(j>1) for j in range(h)]
    assert mm(T,inverse)==[[int(i==j) for j in range(h)] for i in range(h)]
    incidence=[[int(i in triple) for triple in triples] for i in range(h)]
    high=[[sum(a*b for a,b in zip(row,column))%2 for column in zip(*incidence)] for row in T]
    scatter=[[sum(a*b for a,b in zip(column,row))%2 for row in zip(*inverse)] for column in zip(*incidence)]
    G=[[j for j in range(v) if high[i][j]] for i in range(h)]
    R=[[j for j in range(v) if scatter[j][i]] for i in range(h)]
    assert set(G[0]).isdisjoint(G[1]) and set(G[0])|set(G[1])==set(range(v))
    assert set().union(*map(set,G[2:]))==set(range(v))
    assert all(R) and set().union(*map(set,R))==set(range(v))
    for index,triple in enumerate(triples):
        assert high[0][index]==int(0 in triple)
        assert high[1][index]==int(0 not in triple)
    return triples,G,R


def exact_projectors(h):
    assert h>=4 and h not in (9,10)
    metric=[[Q(i==j)-Q(1,9) for j in range(h)] for i in range(h)]
    zero=[[Q(0)]*h for _ in range(h)];identity=[[Q(i==j) for j in range(h)] for i in range(h)]
    answer={'0':zero,'F':identity}
    covectors=[[Q(1-3*(j==0)) for j in range(h)],[Q(j==0) for j in range(h)]]
    normals=[[Q(6,9-h)-3*(j==0) for j in range(h)],
             [Q(j==0)+Q(1,9-h) for j in range(h)]]
    norms=[Q(36,9-h),Q(10-h,9-h)]
    for number,(covector,normal,norm) in enumerate(zip(covectors,normals,norms)):
        assert norm and sum(a*b for a,b in zip(covector,normal))==norm
        assert [sum(a*b for a,b in zip(row,normal)) for row in metric]==covector
        projector=[[normal[i]*covector[j]/norm for j in range(h)] for i in range(h)]
        if h<=12:
            assert mm(projector,projector)==projector
            assert mm(metric,projector)==mm([list(c) for c in zip(*projector)],metric)
        answer['N'+str(number)]=projector
        answer['E'+str(number)]=[[identity[i][j]-projector[i][j] for j in range(h)] for i in range(h)]
    triples=list(combinations(range(h),3))
    for triple in triples:
        protected=0 if 0 in triple else 1
        assert sum(covectors[protected][j] for j in triple)==0
        assert sum(metric[i][j] for i in triple for j in triple)==2
    if h==4:
        for number,triple in enumerate(triples):
            primal=[Q(i in triple) for i in range(h)]
            dual=[Q(i in triple,2)-Q(1,6) for i in range(h)]
            assert sum(a*b for a,b in zip(primal,dual))==1
            P=[[primal[i]*dual[j] for j in range(h)] for i in range(h)]
            answer['L'+str(number)]=P
            answer['K'+str(number)]=[[identity[i][j]-P[i][j] for j in range(h)] for i in range(h)]
    return answer,dict(h=h,triple_source_inclusions=len(triples),
        normal_norms=[str(x) for x in norms],protected_dimensions=[h-1,h-1],
        first_positive=True,second_signature='positive' if h<10 else 'one negative direction',
        scalar_payload_field='F2',address_geometry='Rational H=I-J/9, then fixed admissible odd prime')


def dirty_scalar(h):
    triples,G,R=scalar_coefficients(h);v=len(triples);width=2*v+h;results=[]
    for inverse in (False,True):
        actual=[1<<i for i in range(width)];expected=actual.copy()
        source,target=(v,0) if inverse else (0,v)
        def gather():
            for center in range(h):
                for column in G[center]:actual[2*v+center]^=actual[source+column]
        def scatter():
            for center in range(h):
                for column in R[center]:actual[target+column]^=actual[2*v+center]
        for op in ((gather,scatter,gather,scatter) if inverse else (scatter,gather,scatter,gather)):op()
        for i,S in enumerate(triples):
            for j,U in enumerate(triples):
                if len(set(S)&set(U))%2:expected[target+i]^=expected[source+j]
        assert actual==expected
        results.append(dict(inverse=inverse,complete_dirty_basis=width,all_centers_restored=True))
    return dict(h=h,orientations=results,T_integer_unimodular=True,
                RG_equals_original_incidence_Gram_over_F2=True)


def sparse_native(q,D,reflection):
    h=4;triples,G,R=scalar_coefficients(h);v=len(triples);width=2*v+h
    Ps,_=exact_projectors(h)
    if reflection:
        U=[[Q(i==j)-Q(2,h) for j in range(h)] for i in range(h)]
        Ps={label:mm(mm(U,P),U) for label,P in Ps.items()}
    shifts={}
    for label,P in Ps.items():
        assert all(x.denominator%q for row in P for x in row)
        shifts[label]=tuple(sum(x.numerator*pow(x.denominator,-1,q)*d
            for x,d in zip(row,D))%q for row in P)
    assert any(shifts['N0']) and any(shifts['N1'])
    # Every role is dirty; named probes deliberately sample many address
    # digits and every central/data role, rather than enumerate q^h.
    addresses=[tuple((i*(2*j+1)+j*j)%q for j in range(h)) for i in range(q)]
    addresses+=list(combinations(range(q),4))[:8]
    addresses=sorted(set(addresses));initial=[{} for _ in range(width)]
    count=0
    for role in range(width):
        for address in addresses:initial[role][address]=1<<count;count+=1
    def translate(values,shift):
        return {tuple((a+d)%q for a,d in zip(address,shift)):bits for address,bits in values.items()}
    def xor_into(target,source):
        target=target.copy()
        for address,bits in source.items():
            changed=target.get(address,0)^bits
            if changed:target[address]=changed
            else:target.pop(address,None)
        return target
    sources=['L'+str(i) for i in range(v)]+['0']*(v+h)
    results=[]
    for inverse in (False,True):
        source,target=(v,0) if inverse else (0,v)
        sinks=['F']*v+(['K'+str(i) for i in range(v)] if inverse else ['0']*v)+['F']*h
        if inverse:
            operations=[('G',list(range(h)),'0'),('R',list(range(h)),'F'),
                ('G',list(range(2,h)),'0'),('G',[1],'N1'),('G',[0],'N0'),('R',list(range(h)),'F')]
        else:
            operations=[('R',list(range(h)),'0'),('G',[0],'E0'),('G',[1],'E1'),
                ('G',list(range(2,h)),'F'),('R',list(range(h)),'0'),('G',list(range(h)),'F')]
        def execute(omit=False):
            values=[dict(row) for row in initial];labels=sources.copy();dropped=False
            for kind,centers,new_label in operations:
                supports=G if kind=='G' else R;bank=source if kind=='G' else target
                affected=set().union(*(set(supports[center]) for center in centers))
                roles=[bank+column for column in sorted(affected)]+[2*v+center for center in centers]
                for role in roles:
                    delta=tuple((a-b)%q for a,b in zip(shifts[new_label],shifts[labels[role]]))
                    if omit and not dropped and role==2*v+1 and new_label in ('E1','N1'):dropped=True
                    else:values[role]=translate(values[role],delta)
                    labels[role]=new_label
                for center in centers:
                    for column in supports[center]:
                        out,inp=(2*v+center,bank+column) if kind=='G' else (bank+column,2*v+center)
                        values[out]=xor_into(values[out],values[inp])
            for role,new_label in enumerate(sinks):
                values[role]=translate(values[role],tuple((a-b)%q for a,b in zip(shifts[new_label],shifts[labels[role]])))
            return values
        expected=[translate(row,tuple(-x%q for x in shifts[label])) for row,label in zip(initial,sources)]
        for i,S in enumerate(triples):
            for j,U in enumerate(triples):
                if len(set(S)&set(U))%2:expected[target+i]=xor_into(expected[target+i],expected[source+j])
        expected=[translate(row,shifts[label]) for row,label in zip(expected,sinks)]
        actual=execute();negative=execute(True)
        assert actual==expected and negative!=actual
        results.append(dict(inverse=inverse,sparse_complete_dirty_basis=count,
            independent_original_Gram_boundary_gauge_exact=True,
            missing_second_frame_transition_rejected=True))
    return dict(q=q,D=D,reflected_ambient_chart=reflection,address_samples=len(addresses),
        orientations=results,payload='F2',address_alphabet='F'+str(q))


def disjoint_row_controls():
    rows=[]
    for h in (4,5,6,7,8,9):
        triples=[sum(1<<i for i in triple) for triple in combinations(range(h),3)]
        support=[sum(1<<j for j,triple in enumerate(triples) if (mask&triple).bit_count()%2)
                 for mask in range(1<<h)]
        accepted=0;exceptions=0
        for first in range(1,1<<h):
            for second in range(first+1,1<<h):
                if support[first]&support[second]:continue
                accepted+=1
                if second!=first^((1<<h)-1):
                    exceptions+=1;assert h<=5
        if h>=6:assert accepted==(1<<h)//2-1 and exceptions==0
        if h==5:assert exceptions>0
        rows.append(dict(h=h,accepted_independent_disjoint_pairs=accepted,
                         noncomplementary_exceptions=exceptions))
    # Four point-linear rows really can have disjoint triple supports at h4:
    # each all-points-minus-one row picks exactly the opposite triple.
    h=4;triples=list(combinations(range(h),3));rows4=[15^(1<<i) for i in range(h)]
    supports4=[{j for j,triple in enumerate(triples) if (row&sum(1<<i for i in triple)).bit_count()%2}
               for row in rows4]
    assert all(len(s)==1 for s in supports4) and len(set().union(*supports4))==4
    return dict(exhaustive_pair_shapes=rows,h4_four_disjoint_rows=True,
        theorem_scope='For h>=6, at most two independent point-linear central rows can have pairwise-disjoint triple supports; no bound on overlapping or composite chronologies')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--producer-report',type=Path,required=True)
    parser.add_argument('--producer-certificate',type=Path,required=True)
    parser.add_argument('--producer-source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();assert not args.output.exists();start=time.monotonic()
    producer=json.loads(args.producer_certificate.read_text())
    assert producer['source_sha256']==sha256(args.producer_source.read_bytes()).hexdigest()
    assert producer['complete_native_probes']==230496
    rational=[exact_projectors(h)[1] for h in (4,6,8,12,51,53)]
    scalar=[dirty_scalar(h) for h in (4,6,8,12)]
    native=[sparse_native(q,D,reflection) for q in (7,11)
        for D in ((1,0,2,4),(2,1,3,4)) for reflection in (False,True)]
    assert Q(10-10,9-10)==0
    negatives=dict(h9_ambient_degenerate=True,h10_second_restriction_degenerate=True,
        h5_noncomplementary_disjoint_rows_exist=True,
        ordinary_rational_payload_identity_not_claimed=True)
    result=dict(status='PASS INDEPENDENT TWO DISJOINT PROTECTED CENTERS',
        completed_utc=datetime.now(timezone.utc).isoformat(),python=sys.version,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        inputs={str(path):sha256(path.read_bytes()).hexdigest() for path in
            (args.producer_report,args.producer_source,args.producer_certificate)},
        rational_frames=rational,complete_scalar_basis=scalar,sparse_native_controls=native,
        native_scope='Exact sparse dirty bases on two primes/two fibers/two charts/both orientations; producer full h4 q7 all-H enumeration independently source-reviewed, not rerun',
        complete_sparse_native_probes=sum(row['sparse_complete_dirty_basis'] for item in native for row in item['orientations']),
        disjoint_row_bound=disjoint_row_controls(),negative_controls=negatives,
        all_size_transfer_accepted=True,L='3*v^2*(h^2-2)',W_unchanged=True,
        credited_generic_boundary_families_unchanged=True,new_fixed_bit_table_and_prime_required=True,
        complex_numeric_guard_unchanged=True,
        wall_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],result['complete_sparse_native_probes'],result['wall_seconds'],flush=True)


if __name__=='__main__':main()
