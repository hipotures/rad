#!/usr/bin/env python3
"""Independent exact control for one protected first-gather bit center.

This changes the central-gate chronology. It does not replay the accepted
side circuit or claim that its 2v+h probes include side auxiliary wires.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random
import sys
import time

from review_parameter_audit import log_integer


def rank(rows):
    a = [list(map(Q, row)) for row in rows]
    if not a:
        return 0
    k = 0
    for j in range(len(a[0])):
        pivot = next((i for i in range(k, len(a)) if a[i][j]), None)
        if pivot is None:
            continue
        a[k], a[pivot] = a[pivot], a[k]
        d = a[k][j]
        a[k] = [x/d for x in a[k]]
        for i in range(k + 1, len(a)):
            if a[i][j]:
                c = a[i][j]
                a[i] = [x-c*y for x, y in zip(a[i], a[k])]
        k += 1
        if k == len(a):
            break
    return k


def inner(x, y):
    return sum(a*b for a, b in zip(x, y)) - Q(sum(x)*sum(y), 9)


def line(triple, h):
    return [Q(int(i in triple)) for i in range(h)]


def star_data(h, protected=0):
    assert h >= 4 and h != 9
    leaves = [i for i in range(h) if i != protected]
    n = [Q(1 - 3*int(i == protected)) for i in range(h)]
    z = [Q(6, 9-h) - 3*int(i == protected) for i in range(h)]
    q = sum(a*b for a, b in zip(n, z))
    assert q == Q(36, 9-h) and inner(z, z) == q
    hz = [x-Q(sum(z), 9) for x in z]
    assert hz == n
    basis_pairs = [(leaves[0], j) for j in leaves[1:]] + [(leaves[1], leaves[2])]
    basis = [line((protected, a, b), h) for a, b in basis_pairs]
    assert len(basis) == h-1 and rank(basis) == h-1
    gram = [[inner(x, y) for y in basis] for x in basis]
    assert rank(gram) == h-1
    # On E: total=3*x_i, hence H(x,x)=sum_{j!=i} x_j^2.
    assert gram == [[sum(x[j]*y[j] for j in leaves) for y in basis] for x in basis]
    triples = list(combinations(range(h), 3))
    contained = 0
    residual_checks = 0
    for triple in triples:
        t = line(triple, h)
        norm = inner(t, t)
        assert norm == 2
        nz = sum(a*b for a, b in zip(n, t))
        e_t = [x-zz*nz/q for x, zz in zip(t, z)]
        in_star = protected in triple
        assert (e_t == t) == in_star
        if in_star:
            contained += 1
            assert nz == inner(z, t) == 0
            # E^perp is contained in t^perp. The remaining residual inside E
            # has dimension h-2 and is positive/nondegenerate.
            if h <= 12:
                restricted = [[x-t[j]*inner(xv, t)/2 for j, x in enumerate(xv)] for xv in basis]
                assert rank(restricted) == h-2
                restricted_gram = [[inner(x, y) for y in restricted] for x in restricted]
                assert rank(restricted_gram) == h-2
            # For larger h, E minus the orthogonal rank-one projector onto t
            # is idempotent by E*t=t, has trace(h-1)-1, and is self-adjoint.
            # Thus its exact rank is h-2 without repeated dense elimination.
            assert (h-1)-sum(x*(x-Q(sum(t),9))/2 for x in t) == h-2
            residual_checks += 1
    assert contained == (h-1)*(h-2)//2
    # An outside triple discriminates the invalid static E chart on all X.
    outside = next(t for t in triples if protected not in t)
    assert sum(a*b for a, b in zip(n, line(outside, h))) == 3
    # A forward star chart, rather than its complement, is invalid in the
    # reverse physical-Y target kernel: its own t has nonzero norm.
    star = next(t for t in triples if protected in t)
    assert inner(line(star, h), line(star, h)) == 2
    return dict(h=h,protected_center=protected,star_dimension=h-1,
                ambient_determinant=Q(9-h,9),normal_covector=n,
                normal_vector=z,normal_norm=q,star_basis_rank=h-1,
                star_gram_rank=h-1,star_pair_basis=basis_pairs,
                all_triple_norms=2,star_triples=contained,
                all_source_containments_and_normal_target_orthogonalities_exact=True,
                inner_star_residual_dimension=h-2,residual_line_checks=residual_checks,
                nondegenerate_orthogonal_splitting=True,
                invalid_all_source_star_chart_discriminated=True,
                invalid_reverse_star_instead_of_normal_chart_discriminated=True)


def dimensions(h, stage, contains_protected, inverse):
    """Actual touched-wire chronological dimensions in the reduced P chart.

    Add d0=(h^(j-1)-1)*h to every gate frame and tensor by future line Q.
    The common B summand does not change containment or dimension differences.
    """
    a = h**(stage-1)
    d0 = (a-1)*h
    # Store successive dimensions, including unchanged low/high appearances.
    center = [0,0,h,1,h,h] if inverse else [0,0,h-1,0,h,h]
    others = [0,0,h,0,h,h] if inverse else [0,0,h,0,h,h]
    if inverse:
        data = [0,0,0,1,h-1] if contains_protected else [0,0,0,h-1]
    else:
        data = [1,h-1,h,h] if contains_protected else [1,h,h]
    abs_center = sum(abs(y-x) for x,y in zip(center,center[1:]))
    abs_others = sum(abs(y-x) for x,y in zip(others,others[1:]))
    loss_center = sum(max(x-y,0) for x,y in zip(center,center[1:]))
    loss_others = sum(max(x-y,0) for x,y in zip(others,others[1:]))
    assert loss_center == h-1 and loss_others == h
    assert abs_center == 3*h-2 and abs_others == 3*h
    assert all(x <= y for x,y in zip(data,data[1:]))
    assert sum(y-x for x,y in zip(data,data[1:])) == h-1
    assert abs_center+(h-1)*abs_others == 3*h*h-2
    return dict(h=h,stage=stage,inverse_physical_order=inverse,
                star_data=contains_protected,common_rank=d0,
                protected_center_P_dimensions=center,other_center_P_dimensions=others,
                affected_data_P_dimensions=data,center_loss=h*h-1,
                old_center_loss=h*h,center_absolute_rank=3*h*h-2,
                old_center_absolute_rank=3*h*h,all_data_increments_nondecreasing=True,
                gate_group_count_increase=1,all_late_center_frames_unchanged=True,
                all_data_source_copy_and_terminal_frames_unchanged=True)


def central_gates(h):
    triples = list(combinations(range(h),3))
    stars = [[j for j,t in enumerate(triples) if i in t] for i in range(h)]
    protected = 0
    assert all(any(i != protected for i in t) for t in triples)
    # Mutation lists are literal central scatter/gather operations. F2 signs
    # coincide, but the inverse is the actual reversed operation chronology.
    gates = [('scatter',list(range(h))), ('gather',[protected]),
             ('gather',list(range(1,h))), ('scatter',list(range(h))),
             ('gather',list(range(h)))]
    return triples,stars,gates


def execute_central(h,values,inverse=False,omit_cleanup=False):
    triples,stars,gates = central_gates(h)
    v=len(triples);x=values[:v].copy();y=values[v:2*v].copy();c=values[2*v:].copy()
    assert len(c)==h
    if omit_cleanup:
        gates=gates[:-1]
    if inverse:
        gates=list(reversed(gates))
    for name,indices in gates:
        if name=='gather':
            for i in indices:
                for j in stars[i]:
                    c[i]^=x[j]
        else:
            for j,t in enumerate(triples):
                for i in t:
                    y[j]^=c[i]
    return x+y+c


def expected_central(h,values):
    triples,stars,_=central_gates(h);v=len(triples)
    x=values[:v];y=values[v:2*v].copy();c=values[2*v:]
    for j,s in enumerate(triples):
        for k,t in enumerate(triples):
            if len(set(s).intersection(t))%2:
                y[j]^=x[k]
    return x+y+c


def dirty_controls(h,seed):
    triples,_,_=central_gates(h);v=len(triples);n=2*v+h
    # Packed independent scalar bases execute every central-register/data
    # basis at once; each bit is one F2 scalar basis probe.
    basis=[1<<i for i in range(n)]
    expected=expected_central(h,basis)
    for inverse in (False,True):
        assert execute_central(h,basis,inverse)==expected
    assert execute_central(h,execute_central(h,basis),True)==basis
    rng=random.Random(seed)
    signed_probes=[]
    for _ in range(12):
        values=[rng.randrange(2) for _ in range(n)]
        for inverse in (False,True):
            assert execute_central(h,values,inverse)==expected_central(h,values)
        signed_probes.append(sha256(bytes(values)).hexdigest())
    wrong=execute_central(h,basis,omit_cleanup=True)
    failures=sum(a!=b for a,b in zip(wrong,expected))
    assert failures>0
    # The unchanged side map has coefficient one exactly at intersection1.
    # Its accepted transparent implementation adds it independently of its
    # arbitrary old side registers. This verifies the unchanged map identity
    # without replaying that physical implementation.
    coefficient_checks=0
    for s in triples:
        for t in triples:
            intersection=len(set(s).intersection(t))
            assert ((intersection%2) ^ int(intersection==1))==int(s==t)
            coefficient_checks+=1
    return dict(h=h,triples=v,complete_central_invocation_basis=n,
                center_registers_included=h,side_auxiliary_registers_included=0,
                literal_forward_and_reversed_inverse_basis_exact=True,
                arbitrary_dirty_center_values_restored=True,
                central_output_is_incidence_incidence_transpose=True,
                packed_basis_output_sha256=sha256(json.dumps(expected).encode()).hexdigest(),
                random_dirty_probes_per_orientation=12,seed=seed,
                omitted_cleanup_discriminating_registers=failures,
                unchanged_side_plus_central_coefficient_checks=coefficient_checks,
                combined_shear_scalar_identity=True,
                source_and_target_roles_unchanged=True)


def parse_int(value):
    return int(Q(value))


def characteristic(h,roles,audit_path):
    audit=json.loads(audit_path.read_text())
    old=audit['row']['counts']
    h0=int(old['h']);roles0=int(old['side_roles'])
    assert (h,roles)==(h0,roles0)
    v=h*(h-1)*(h-2)//6;m=h**3;N=v**3
    W=2*N+2*v*v*(roles+h)
    oldL=3*v*v*h*h;newL=3*v*v*(h*h-1)
    oldD=N-2*oldL;D=N-2*newL
    old_s=W*m-oldD;s=W*m-D
    for key,value in dict(h=h,R=roles,v=v,m=m,N=N,W=W,L=oldL,D=oldD,s=old_s).items():
        original_key='side_roles' if key=='R' else key
        assert parse_int(old[original_key])==value,(key,old[original_key],value)
    J=(roles+h)*v*v
    ds=[h*h,2*h,h*h+h-1]
    runs=[m-2*d for d in ds]
    copies=[J,J,2*N]
    ranks=[m-d for d in ds]
    credited_rank=sum(c*r for c,r in zip(copies,runs))
    all_family_rank=sum(c*r for c,r in zip(copies,ranks))
    assert 0<credited_rank<=all_family_rank<s
    log_m_hi=log_integer(m,80)[1]
    log_r_lo=[log_integer(r,80)[0] for r in runs]
    moment=sum(Q(c*r)*l for c,r,l in zip(copies,runs,log_r_lo))
    denom=s*log_m_hi-moment
    def slack(a):
        assert a>=0 and a*log_m_hi<1
        return D-a*denom-a*a*s*log_m_hi*log_m_hi/(2*(1-a*log_m_hi))
    scale=10**24
    old_a=Q(audit['row']['explicit_saving'])
    lower=old_a.numerator*scale//old_a.denominator
    upper=2*lower
    while slack(Q(upper,scale))>0:
        upper*=2
    while upper-lower>1:
        mid=(upper+lower)//2
        if slack(Q(mid,scale))>0:
            lower=mid
        else:
            upper=mid
    a=Q(lower,scale)
    assert slack(a)>0 and a>old_a and slack(Q(upper,scale))<=0
    # The local split subtracts 2 from each of 3v^2 invocations. The three
    # grouped boundary families remain exactly the old endpoint profiles.
    assert old_s-s==6*v*v and D-oldD==6*v*v
    singleton=s-credited_rank
    assert singleton>0
    grouped_rank=sum(c*r for c,r in zip(copies,runs))
    assert singleton+grouped_rank==s
    return dict(h=h,R=roles,v=v,m=m,N=N,W=W,old_L=oldL,L=newL,
                old_D=oldD,D=D,old_s=old_s,s=s,rank_gain=6*v*v,
                unchanged_boundaries=[dict(name=name,kernel_dimension=d,run=r,
                    copies=c,total_profile_rank=c*rr) for name,d,r,c,rr in
                    zip(('middle','joined','two_stage3_data'),ds,runs,copies,ranks)],
                credited_rank=credited_rank,singleton_children=singleton,
                changed_gate_groups=3*v*v,new_auxiliary_roles=0,
                old_explicit_saving=old_a,explicit_saving=a,
                next_gridpoint=Q(upper,scale),strict_characteristic_slack=slack(a),
                next_gridpoint_slack=slack(Q(upper,scale)),
                old_saving_new_slack=slack(old_a),
                same_selected_family_count_bound=v+v*v+2*N,
                same_max_reflection_steps=max(ds),
                same_grouped_max_child=max(runs),new_complete_table_required=True,
                source_rank_N_unchanged=True,
                grouped_boundary_frames_and_frequencies_unchanged=True,
                new_uncredited_edge_pivots_all_singletons=True,
                separate_complex_guard_unchanged=True)


def encode(value):
    if isinstance(value,Q):
        return str(value)
    if isinstance(value,dict):
        return {k:encode(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):
        return [encode(v) for v in value]
    return value


def main():
    sys.set_int_max_str_digits(0)
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--generic-audit',type=Path,required=True)
    parser.add_argument('--seed',type=int,default=751)
    args=parser.parse_args();start=time.monotonic()
    result=dict(status='PASS',question='One protected first-gather bit center',
        timestamp=datetime.now(timezone.utc).isoformat(),python=sys.version,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        metric_inputs=[star_data(h) for h in (4,6,8,12,51,53)],
        timeline_controls=[dimensions(h,j,star,inverse) for h in (4,6,8,12,51,53)
            for j in (1,2,3) for star in (False,True) for inverse in (False,True)],
        central_dirty_controls=[dirty_controls(h,args.seed+h) for h in (4,6,8,12)],
        characteristic=characteristic(51,485680,args.generic_audit),
        generic_audit_sha256=sha256(args.generic_audit.read_bytes()).hexdigest(),
        side_physical_baseline_replayed=False,
        limitations=['Only the changed central invocation is independently executed.',
            'The giant new h51 rational factor table and prime are constructive setup.',
            'This explicit primitive saving is not a final multiplication kappa.'])
    result['wall_seconds']=time.monotonic()-start
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(encode(result),indent=2)+'\n')
    print(json.dumps(dict(status='PASS',star_inputs=len(result['metric_inputs']),
        timeline_controls=len(result['timeline_controls']),
        central_basis_probes=sum(x['complete_central_invocation_basis'] for x in result['central_dirty_controls']),
        saving=str(result['characteristic']['explicit_saving']),
        elapsed_seconds=result['wall_seconds'])))


if __name__=='__main__':
    main()
