#!/usr/bin/env python3
"""Exact small pre/post tests for nonlinear address-dependent amplitude words.

The six-bank quotient model is diag(I,I,C_f,C_f,C_f,C_f), not the existing
joint word with two distinct source labels. A sparse required postprocessor
would still need a native factorization; a dense one rejects only the named
preword and requested post-depth. No new supplier or exponent is certified.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from random import Random
import time


ZERO=(Q(0),Q(0));ONE=(Q(1),Q(0))
def add(a,b):return a[0]+b[0],a[1]+b[1]
def mul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def scale(a,c):return a[0]*c,a[1]*c
def norm(a):return a[0]*a[0]+a[1]*a[1]
def unit(k):return ((Q(1),Q(0)),(Q(0),Q(1)),(Q(-1),Q(0)),(Q(0),Q(-1)))[k%4]
def power(a,n):
    result=ONE
    for _ in range(n):result=mul(result,a)
    return result


def identity(N):return [[ONE if i==j else ZERO for j in range(N)] for i in range(N)]


def butterfly(a,b,inverse=False):
    if inverse:
        return ((a[0]+b[0]+a[1]-b[1])/2,(a[1]+b[1]-a[0]+b[0])/2), \
               ((a[0]+b[0]-a[1]+b[1])/2,(a[1]+b[1]+a[0]-b[0])/2)
    return ((a[0]+b[0]-a[1]+b[1])/2,(a[1]+b[1]+a[0]-b[0])/2), \
           ((a[0]+b[0]+a[1]-b[1])/2,(a[1]+b[1]-a[0]+b[0])/2)


def c_side(M,f,banks,left=True,inverse=False):
    D=1<<f;N=len(M)
    for bank in banks:
        for bit in range(f):
            direction=1<<bit
            for address in range(D):
                if address&direction:continue
                i=bank*D+address;j=i+direction
                if left:
                    first=[];second=[]
                    for a,b in zip(M[i],M[j]):
                        p,q=butterfly(a,b,inverse);first.append(p);second.append(q)
                    M[i]=first;M[j]=second
                else:
                    for row in range(N):M[row][i],M[row][j]=butterfly(M[row][i],M[row][j],inverse)


def qvalue(address,f):
    return sum(((address>>(2*j))&1)*((address>>(2*j+1))&1) for j in range(f//2))%2


def route_columns(f,bank,layout):
    columns=[1<<j for j in range(f)]
    # Fixed invertible linear routes differ between banks. The selected
    # column pairs are explicit, rather than silently applying a transpose.
    for step in range(f-1):
        source=(step+bank+layout)%f;target=(source+1)%f
        columns[source]^=columns[target]
    return columns


def image(address,columns,offset=0):
    out=offset
    for j,col in enumerate(columns):
        if address>>j&1:out^=col
    return out


def word(f,layout):
    events=[]
    for bank in range(6):events.append(dict(kind='amplitude',bank=bank,flip=(bank+layout)%2))
    for a,b in ((0,2),(1,3),(4,5)):
        if layout==0:
            events.extend(dict(kind='add',source=s,target=t,coefficient=1) for s,t in ((b,a),(a,b),(a,b)))
        else:
            events.extend(dict(kind='add',source=s,target=t,coefficient=1) for s,t in ((b,a),(b,a),(a,b)))
    for bank in range(6):events.append(dict(kind='route',bank=bank,columns=route_columns(f,bank,layout),offset=(bank+2*layout)%(1<<f)))
    for bank in range(6):events.append(dict(kind='amplitude',bank=bank,flip=(bank+layout+1)%2))
    for a,b in ((0,3),(1,4),(2,5)):
        events.extend(dict(kind='add',source=s,target=t,coefficient=(-1 if layout else 1)) for s,t in ((b,a),(a,b),(a,b)))
    return events


def apply_event(M,event,f,left=True,inverse=False):
    D=1<<f;N=len(M);kind=event['kind']
    if kind=='add':
        source=event['source'];target=event['target'];c=event['coefficient']*(-1 if inverse else 1)
        for address in range(D):
            s=source*D+address;t=target*D+address
            if left:M[t]=[add(x,scale(y,c)) for x,y in zip(M[t],M[s])]
            else:
                for row in range(N):M[row][s]=add(M[row][s],scale(M[row][t],c))
    elif kind=='amplitude':
        for address in range(D):
            high=qvalue(address,f)^event['flip'];c=Q(1,2) if high else Q(2)
            if inverse:c=1/c
            i=event['bank']*D+address
            if left:M[i]=[scale(x,c) for x in M[i]]
            else:
                for row in range(N):M[row][i]=scale(M[row][i],c)
    elif kind=='route':
        table=[image(a,event['columns'],event['offset']) for a in range(D)]
        if sorted(table)!=list(range(D)):raise ValueError('A retained native route is not bijective')
        if inverse:
            inv=[0]*D
            for a,b in enumerate(table):inv[b]=a
            table=inv
        start=event['bank']*D
        if left:
            old=M[start:start+D]
            for a,b in enumerate(table):M[start+b]=old[a]
        else:
            for row in range(N):
                old=M[row][start:start+D]
                M[row][start:start+D]=[old[table[a]] for a in range(D)]
    else:raise ValueError('Unknown preword event')


def ledger(M):
    denominators=[v.denominator for row in M for z in row for v in z if v]
    if any(d&(d-1) for d in denominators):raise ValueError('The candidate left the Gaussian-dyadic grid')
    return dict(grid_bits=max((d.bit_length()-1 for d in denominators),default=0),
                component_l1=max(sum(abs(z[0])+abs(z[1]) for z in row) for row in M))


def apply_word(M,events,f,left=True,inverse=False,monitor=False):
    selected=list(reversed(events)) if (inverse if left else not inverse) else events
    peak_grid=0;peak_mass=Q(1)
    for event in selected:
        apply_event(M,event,f,left,inverse)
        if monitor:
            current=ledger(M);peak_grid=max(peak_grid,current['grid_bits']);peak_mass=max(peak_mass,current['component_l1'])
    return dict(grid_bits=peak_grid,component_l1=str(peak_mass))


def pauli_matrix(coefficients,f):
    D=1<<f;M=[[ZERO for _ in range(D)] for _ in range(D)]
    for (p,q),coefficient in coefficients.items():
        for column in range(D):M[column^p][column]=add(M[column^p][column],scale(coefficient,-1 if (column&q).bit_count()%2 else 1))
    return M


def conjugate_coefficients(coefficients,inverse=False):
    return {(p^q,q):mul(coefficient,unit((1 if inverse else -1)*q.bit_count()))
            for (p,q),coefficient in coefficients.items()}


def right_line_product(coefficients,f,inverse=False,selected=None):
    selected=list(range(f)) if selected is None else selected
    alpha=(Q(1,2),Q(-1 if inverse else 1,2));beta=(alpha[0],-alpha[1])
    out=dict(coefficients)
    for bit in selected:
        new={};v=1<<bit
        for (p,q),c in out.items():
            for key,value in (((p,q),mul(c,alpha)),((p^v,q),scale(mul(c,beta),-1 if q&v else 1))):
                new[key]=add(new.get(key,ZERO),value)
        out={key:value for key,value in new.items() if value!=ZERO}
    return out


def pauli_uncertainty(f):
    D=1<<f;checked=[];rng=Random(20261009+f)
    inputs=[]
    for r in range(f+1):
        output_basis={(0,D-1):ONE}
        X=right_line_product(conjugate_coefficients(output_basis,True),f,True,range(r))
        inputs.append(X)
    for _ in range(6):
        keys=rng.sample([(p,q) for p in range(D) for q in range(D)],min(2*f,D*D))
        inputs.append({key:(Q(rng.choice((-2,-1,1,2)),2),Q(rng.choice((-1,0,1)),2)) for key in keys})
    for X in inputs:
        Y=right_line_product(conjugate_coefficients(X),f)
        norm_x=sum(norm(v) for v in X.values());norm_y=sum(norm(v) for v in Y.values())
        if norm_x!=norm_y:raise ValueError('The Pauli coefficient map does not preserve exact Hilbert-Schmidt norm')
        if len(X)*len(Y)<D:raise ValueError('The nonunit Pauli support uncertainty inequality failed')
        actual=pauli_matrix(X,f)
        c_side(actual,f,[0],left=False)
        c_side(actual,f,[0],left=False,inverse=True)
        c_side(actual,f,[0],left=True)
        if actual!=pauli_matrix(Y,f):raise ValueError('The Pauli coefficient map differs from the complete literal operator')
        checked.append([len(X),len(Y),str(norm_x)])
    if any(x*y!=D for x,y,_ in checked[:f+1]):raise ValueError('The exact tensor equality witnesses do not attain the bound')
    # The right multiplication and inverse must be exact on arbitrary
    # Gaussian-dyadic coefficients, including cancellations.
    for X in inputs:
        if right_line_product(right_line_product(X,f),f,True)!=X:raise ValueError('The line product inverse leaked a coefficient')
    return dict(nonunit_samples=len(inputs),support_norm_receipts=checked,
                equality_cases=f+1,complete_operator_dimension=D,
                conclusion='For every nonzero X, s_Pauli(X)*s_Pauli(F*X*A*F^-1)>=2^f; arbitrary coefficients permitted')


def amplitude_control(f):
    D=1<<f;values=[Q(2) if qvalue(a,f)==0 else Q(1,2) for a in range(D)]
    inverse=[1/v for v in values];phase_spectrum=[];amplitude_spectrum=[]
    for z in range(D):
        phase_spectrum.append(Q(sum((-1 if qvalue(a,f)^((z&a).bit_count()%2) else 1) for a in range(D)),D))
        amplitude_spectrum.append(sum(values[a]*(-1 if (z&a).bit_count()%2 else 1) for a in range(D))/D)
    if any(abs(v)!=Q(1,1<<(f//2)) for v in phase_spectrum):raise ValueError('The paired quadratic phase is not exactly bent')
    if any(v==0 for v in amplitude_spectrum):raise ValueError('The compact amplitude does not have full Pauli support')
    if any(values[a]*inverse[a]!=1 for a in range(D)):raise ValueError('The actual address amplitude inverse differs')
    return dict(values=['2','1/2'],inverse_values=['1/2','2'],condition_number=4,
                selected_columns=f,quadratic_cross_column_pairs=[[2*j,2*j+1] for j in range(f//2)],
                exact_bent_coefficient_magnitude=str(Q(1,1<<(f//2))),pauli_support=D,
                address_rule='5/4+(3/4)*(-1)^q; inverse 5/4-(3/4)*(-1)^q',
                metadata_scope='All f selected bits and f/2 cross-column products are explicit. A native counter/control compiler and complete per-record layout remain unproved.')


def support_summary(M,W):
    N=len(M);row=[sum(z!=ZERO for z in values) for values in M]
    column=[sum(M[i][j]!=ZERO for i in range(N)) for j in range(N)]
    rows_to_columns=[{j for j,z in enumerate(values) if z!=ZERO} for values in M]
    columns_to_rows=[{i for i in range(N) if M[i][j]!=ZERO} for j in range(N)]
    unseen=set(range(N));components=[]
    while unseen:
        selected={min(unseen)};columns=set();frontier=set(selected)
        while frontier:
            for i in frontier:columns.update(rows_to_columns[i])
            new=set().union(*(columns_to_rows[j] for j in columns))-selected
            selected.update(new);frontier=new
        unseen-=selected;components.append([len(selected),len(columns)])
    def histogram(values):return {str(v):values.count(v) for v in sorted(set(values))}
    max_support=max(max(row),max(column));minimum=0
    while W**minimum<max_support:minimum+=1
    return dict(row_support_histogram=histogram(row),column_support_histogram=histogram(column),
                maximum_coordinate_support=max_support,necessary_post_Wwide_layers=minimum,
                connected_bipartite_component_sizes=components,
                one_Wwide_layer_up_to_arbitrary_coordinate_routes=all(a==b and a<=W for a,b in components),
                scope='Only the unique postprocessor for the retained preword is tested. Coordinate routes may mix bank selectors in the one-layer support criterion.')


def matrix_digest(M):
    digest=sha256()
    for row in M:
        digest.update(json.dumps([[[v.numerator,v.denominator] for v in z] for z in row],separators=(',',':')).encode()+b'\n')
    return digest.hexdigest()


def probe(case):
    f,layout=case;started=time.monotonic();D=1<<f;W=6;N=W*D;events=word(f,layout)
    pre=identity(N);forward_guard=apply_word(pre,events,f,monitor=True)
    pre_inverse=identity(N);inverse_guard=apply_word(pre_inverse,events,f,inverse=True,monitor=True)
    cancel=[list(row) for row in pre_inverse];apply_word(cancel,events,f,left=False)
    if cancel!=identity(N):raise ValueError('The complete preword forward/inverse contract failed')
    required=[list(row) for row in pre_inverse]
    c_side(required,f,range(2,W),left=False,inverse=True)
    c_side(required,f,range(W),left=True)
    summary=support_summary(required,W)
    # Exact full post*core*pre operator check. The required post is a
    # derived dense matrix, not a paid native post word.
    recovered=[list(row) for row in required]
    c_side(recovered,f,range(2,W),left=False)
    apply_word(recovered,events,f,left=False)
    target=identity(N);c_side(target,f,range(W),left=True)
    if recovered!=target:raise ValueError('The required pre/post word does not match the complete target')
    corrupt=[list(row) for row in required]
    c_side(corrupt,f,range(2,W),left=False)
    without_amplitude=[event for event in events if event['kind']!='amplitude']
    apply_word(corrupt,without_amplitude,f,left=False)
    if corrupt==target:raise ValueError('Omitted nonlinear amplitude control incorrectly passes the complete target')
    amplitude=amplitude_control(f);uncertainty=pauli_uncertainty(f)
    return dict(status='PASS EXACT NONUNIT PREPOST PREFLIGHT',selected_columns=f,layout=layout,
                quotient_model='diag(I,I,C_f,C_f,C_f,C_f) -> diag(C_f,C_f,C_f,C_f,C_f,C_f)',
                original_joint_source_labels_not_identified=True,physical_banks=W,operator_dimension=N,
                complete_target_coefficients_compared=N*N,preword_events=events,
                native_preword_unit_shears=sum(event['kind']=='add' for event in events),
                native_preword_amplitude_bank_calls=sum(event['kind']=='amplitude' for event in events),
                native_preword_routing_bank_calls=sum(event['kind']=='route' for event in events),
                preword_forward_prefix=forward_guard,preword_inverse_prefix=inverse_guard,
                preword_condition_upper=3600,condition_proof='Two block S layers, each condition<=15, and two amplitude layers, each condition4; permutations unitary.',
                required_post_condition_upper=3600,required_post_complete_operator_sha256=matrix_digest(required),
                required_post_support=summary,post_native_word_supplied=False,
                amplitude=amplitude,pauli_uncertainty=uncertainty,
                complete_common_grid='All stored operator coefficients are Gaussian dyadic; exact maximum prefix grid and component-L1 bounds retained. No sampled floating matrix used.',
                native_time_scope='The finite scalar/address events are declared, but complete fixed-tape routing/control and per-record metadata are not certified. No cost or primitive is asserted for the derived dense postprocessor.',
                target_capacity_scope='An O(log f) complete native boundary could preserve the favorable core moment, but none is found here. Exact algebraic compatibility alone is insufficient.',
                seed=20261009+f,negative_controls={'omit_nonlinear_amplitudes':'COMPLETE OPERATOR REJECTED'},seconds=time.monotonic()-started)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=4);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    source=Path(__file__);source_hash=sha256(source.read_bytes()).hexdigest();cases=[(2,0),(2,1),(4,0),(4,1)]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,cases=cases,
                  source_sha256={source.name:source_hash},stdlib_only=True,seed_rule='20261009+selected_columns',
                  hypothesis='Simple bounded-condition nonlinear amplitude rules may make a deeper native pre/post boundary possible; derive the exact required post for two fixed interleaved families before deeper search.',
                  scope='Common missing-line quotient model; not the distinct-label joint core or an accepted supplier',
                  resource_preflight={'maximum_dense_operator_dimension':96,'four_workers_operator_entries_upper':4*96*96,'expected_memory_bytes_upper':128*1024*1024},
                  command_from_topic_root='python3 -B code/synthesis/nonunit_address_amplitude_preflight.py --workers 4 --output <fresh ignored directory>')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,case):case for case in cases}
        for future in as_completed(jobs):
            result=future.result();results.append(result)
            print(json.dumps({key:result[key] for key in ('status','selected_columns','layout','operator_dimension','seconds')}|{'required_post_support':result['required_post_support']['maximum_coordinate_support']}),flush=True)
    if sha256(source.read_bytes()).hexdigest()!=source_hash:raise ValueError('Source changed during amplitude preflight')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results),indent=2)+'\n')


if __name__=='__main__':main()
