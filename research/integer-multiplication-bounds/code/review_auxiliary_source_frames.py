#!/usr/bin/env python3
"""Independent auxiliary-source endpoint, rational projector and moment review.

No new upstream producer is imported. Uses the frozen independent rational
reflection/profile lemma and exact logarithm enclosures from this campaign.
"""
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from math import comb
from pathlib import Path
import argparse, json, resource, time
from review_generic_metric_basis import dual, simultaneous_reflections, complementary_profile
from review_parameter_audit import log_integer

def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def mm(A,B):return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]
def trans(A):return list(map(list,zip(*A)))
def kron(A,B):return [[a*b for a in rowa for b in rowb] for rowa in A for rowb in B]
def add(A,B,sign=1):return [[a+sign*b for a,b in zip(ra,rb)] for ra,rb in zip(A,B)]

def rational_model(h):
    I=eye(h);G=[[Q(i==j)-Q(1,9) for j in range(h)] for i in range(h)]
    t=[[Q(i<3)] for i in range(h)];V=dual(G,t);P=mm(t,V);B=add(I,P,-1)
    D0=kron(kron(B,I),P);D1=kron(kron(I,I),P);m=h**3
    E=add(add(eye(m),D0),D1,-1)
    U=kron(kron(t,I),t);GT=kron(kron(G,G),G);DU=dual(GT,U)
    assert E==add(eye(m),mm(U,DU),-1)
    assert mm(D1,D0)==D0 and mm(D0,D1)==D0
    assert mm(DU,U)==eye(h)
    assert sum(E[i][i] for i in range(m))==m-h
    assert (h*h-h)+h+(m-h*h)==h+(m-h)==m
    ans=dict(h=h,dimension=m,old_entrance=h*h-h,old_exit=m-h*h,
        new_entrance=0,new_exit=m-h,kernel_dimension=h,rank_sum_preserved=True,
        exit_exact_complementary_projector=True)
    if h==3:
        pairs,T,proof=simultaneous_reflections(GT,[(U,DU)],104729)
        ans['generic_profile']=complementary_profile(*pairs[0])
        ans['reflection_proof']=proof
        assert mm(mm(trans(T),GT),T)==GT
        ans['whole_tensor_metric_isometry_exact']=True
    return ans

def native_endpoint():
    # Complete dirty basis for a five-role, three transparent side invocations.
    # Arrays have three odd-prime address digits. Payload additions are XOR.
    q=5;n=3;W=5;addresses=list(product(range(q),repeat=n));basis=W*len(addresses)
    initial=[{a:1<<(r*len(addresses)+i) for i,a in enumerate(addresses)} for r in range(W)]
    zero=(0,0,0);I=(1,2,3);M=(1,0,0)
    def plus(a,b):return tuple((x+y)%q for x,y in zip(a,b))
    def minus(a,b):return tuple((x-y)%q for x,y in zip(a,b))
    def shift(row,v):return {plus(a,v):bits for a,bits in row.items()}
    def xor(a,b):
        a=a.copy()
        for k,v in b.items():
            x=a.get(k,0)^v
            if x:a[k]=x
            else:a.pop(k,None)
        return a
    def execute(new,omit=False):
        values=[x.copy() for x in initial];labels=[zero]*W
        if new:labels[3]=M
        for stage,(x,y) in enumerate(((0,1),(1,0),(0,1))):
            scratch=2+stage
            for out,inp,frame in ((y,scratch,M),(scratch,x,I),(y,scratch,I),(scratch,x,I)):
                for r in (out,inp):values[r]=shift(values[r],minus(frame,labels[r]));labels[r]=frame
                values[out]=xor(values[out],values[inp])
        sinks=[I]*W
        if new and not omit:sinks[3]=plus(I,M)
        for r in range(W):values[r]=shift(values[r],minus(sinks[r],labels[r]))
        return values
    expected=[shift(initial[1],I),shift(initial[0],I)]+[shift(r,I) for r in initial[2:]]
    old,new,bad=execute(False),execute(True),execute(True,True)
    assert old==new==expected and bad!=expected
    return dict(address_alphabet='F5',address_digits=n,payload='F2',
        complete_dirty_basis=basis,nonzero_auxiliary_source_only_middle=True,
        all_auxiliary_final_shears_I=True,full_data_role_exchange=True,
        omitted_I_plus_M_sink_rejected=True)

def rounded_log(n,lower):
    lo,hi=log_integer(n,160);x=lo if lower else hi;scale=2**448
    return Q(x.numerator*scale//x.denominator,scale) if lower else Q(-((-x.numerator*scale)//x.denominator),scale)

def characteristic(promotion,protected):
    raw=promotion['full'];n=dict(raw['exact_counts']);h=n['h'];v=n['v'];m=n['m'];R=n['R']
    assert h==53 and R==529181 and raw['current_actual_frames_retained_at_all_stages']
    assert n['s']==raw['independent_actual_rank_timeline']['rank_sum']
    n['L']-=3*protected*v*v;n['D']+=6*protected*v*v;n['s']-=6*protected*v*v
    J=(R+h)*v*v
    dims=dict(new_middle=h,joined=2*h,data=h*h+h-1)
    copies=dict(new_middle=J,joined=J,data=2*n['N'])
    runs={k:m-2*d for k,d in dims.items()}
    mass=sum(copies[k]*runs[k] for k in dims);single=n['s']-mass
    assert single>0 and n['s']==n['W']*m-n['D']
    lm=rounded_log(m,False)
    M=sum(copies[k]*runs[k]*rounded_log(runs[k],True) for k in dims)
    linear=n['s']*lm-M;quadratic=Q(n['s'],2)*lm*lm
    def gap(a):return n['D']-a*linear-a*a*quadratic/(1-a*lm)
    scale=10**24;lo=0;hi=10**20
    assert gap(Q(hi,scale))<0
    while hi-lo>1:
        mid=(lo+hi)//2
        if gap(Q(mid,scale))>0:lo=mid
        else:hi=mid
    a=Q(lo,scale);assert gap(a)>0>=gap(Q(lo+1,scale))
    rmax=max(runs.values());D=1
    while m**D<=2*rmax**D:D+=1
    bits=n['W'].bit_length();coefficient=Q(51,25)*(bits*D+41*272)
    degree=1000*(-(-coefficient.numerator//(1000*coefficient.denominator)))
    return dict(protected_centers=protected,counts=n,source_frame_changed_roles=J,
        old_middle_kernel_dimension=h*h,new_middle_kernel_dimension=h,
        kernel_dimensions=dims,family_multiplicities=copies,runs=runs,
        individual_pivots=single,rank_mass_preserved=n['s'],saving=str(a),
        strict_normalized_Taylor_gap=str(gap(a)),next_grid_gap=str(gap(Q(lo+1,scale))),
        maximum_child=rmax,least_halving_degree=D,wire_log2_ceiling=bits,
        joint_row_coefficient=str(coefficient),joint_row_degree=degree,
        reservoir_slope=4*degree,log_terms=160,dyadic_log_bits=448,
        final_multiplication_kappa_claimed=False)

def main():
    p=argparse.ArgumentParser();p.add_argument('--promotion',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert not a.output.exists();start=time.monotonic();b=a.promotion.read_bytes()
    assert sha256(b).hexdigest()=='c957b06e16a781c11bc2a454b6c323a666e8ec2d47a17af7fe89089f3518939e'
    x=json.loads(b);assert x['status']=='PASS INDEPENDENT CLOSING DIRECT-FIRST-ALLOCATION COMPOUND'
    result=dict(status='PASS INDEPENDENT NONZERO AUXILIARY SOURCE TRANSFER COMPONENT',
        completed_utc=datetime.now(timezone.utc).isoformat(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_sha256={str(a.promotion):sha256(b).hexdigest()},
        rational_controls=[rational_model(h) for h in (3,4)],native=native_endpoint(),
        variants=[characteristic(x,j) for j in (0,1,2)],
        chronology='Stage2 begins with inverse late FULL gather at D0 even for protected centers; normal protected return slots occur later; last gate D1 unchanged',
        limitations=['New fixed rational address table and admissible odd prime required',
            'All-size constructive simultaneous flags theorem applies; giant h53 basis not instantiated',
            'Primitive component only; full phase/leaf/row/assembly must be independently composed'],
        wall_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,default=str,sort_keys=True)+'\n')
    print('PASS',[(v['protected_centers'],v['saving'],v['least_halving_degree'],v['joint_row_degree']) for v in result['variants']],flush=True)

if __name__=='__main__':main()
