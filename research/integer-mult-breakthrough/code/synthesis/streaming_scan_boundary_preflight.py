#!/usr/bin/env python3
"""Exact prefix/difference pre/post models with literal record-buffer controls.

The derived postprocessor is not a native implementation. Cut ranks give
necessary bounds only for the declared scan/cyclic-shift ordering model;
global address permutations or large-stride buffers can evade that model.
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

import nonunit_address_amplitude_preflight as p


def scan_matrix(M,bank,f,left=True,inverse=False):
    D=1<<f;start=bank*D;N=len(M)
    if left:
        addresses=range(D-1,0,-1) if inverse else range(1,D)
        for a in addresses:
            M[start+a]=[p.add(x,p.scale(y,-1 if inverse else 1)) for x,y in zip(M[start+a],M[start+a-1])]
    else:
        addresses=range(D-1) if inverse else range(D-2,-1,-1)
        for a in addresses:
            for row in range(N):M[row][start+a]=p.add(M[row][start+a],p.scale(M[row][start+a+1],-1 if inverse else 1))


def route_matrix(M,event,f,left=True,inverse=False):
    D=1<<f;start=event['bank']*D;N=len(M)
    table=[((D-1-a if event['reverse'] else a)+event['offset'])%D for a in range(D)]
    if inverse:
        back=[0]*D
        for a,b in enumerate(table):back[b]=a
        table=back
    if left:
        old=M[start:start+D]
        for a,b in enumerate(table):M[start+b]=old[a]
    else:
        for row in range(N):
            old=M[row][start:start+D]
            M[row][start:start+D]=[old[table[a]] for a in range(D)]


def apply_word(M,events,f,left=True,inverse=False,monitor=False):
    selected=list(reversed(events)) if (inverse if left else not inverse) else events
    peak_grid=0;peak_mass=Q(1)
    for event in selected:
        if event['kind']=='scan':scan_matrix(M,event['bank'],f,left,inverse^event['difference'])
        elif event['kind']=='cyclic_route':route_matrix(M,event,f,left,inverse)
        else:p.apply_event(M,event,f,left,inverse)
        if monitor:
            current=p.ledger(M);peak_grid=max(peak_grid,current['grid_bits']);peak_mass=max(peak_mass,current['component_l1'])
    return dict(grid_bits=peak_grid,component_l1=str(peak_mass))


def word(f,layout):
    events=[dict(kind='scan',bank=b,difference=bool((b+layout)%2)) for b in range(6)]
    for a,b in ((0,2),(1,3),(4,5)):
        events.extend(dict(kind='add',source=s,target=t,coefficient=1) for s,t in ((b,a),(a,b),(a,b)))
    events.extend(dict(kind='cyclic_route',bank=b,offset=(b+1)*(-1 if layout else 1),reverse=bool(layout and b%2)) for b in range(6))
    events.extend(dict(kind='amplitude',bank=b,flip=(b+layout)%2) for b in range(6))
    # Repeated first matching supplies multiple routed paths within the
    # same bank block, lifting the earlier unique-path restriction.
    for a,b in ((0,2),(1,3),(4,5)):
        events.extend(dict(kind='add',source=s,target=t,coefficient=-1) for s,t in ((b,a),(a,b),(a,b)))
    events.extend(dict(kind='scan',bank=b,difference=bool((b+layout+1)%2)) for b in range(6))
    for a,b in ((0,3),(1,4),(2,5)):
        events.extend(dict(kind='add',source=s,target=t,coefficient=1) for s,t in ((b,a),(a,b),(a,b)))
    return events


def fq_add(x,y):return (x%3+y%3)%3+3*((x//3+y//3)%3)
def fq_mul(x,y):return ((x%3)*(y%3)-(x//3)*(y//3))%3+3*(((x%3)*(y//3)+(x//3)*(y%3))%3)
ADD=[[fq_add(x,y) for y in range(9)] for x in range(9)]
MUL=[[fq_mul(x,y) for y in range(9)] for x in range(9)]
NEG=[(-x%3)%3+3*(-(x//3)%3) for x in range(9)]
INV=[0]+[next(y for y in range(1,9) if MUL[x][y]==1) for x in range(1,9)]


def mod_coefficient(z):
    out=[]
    for x in z:
        if x.denominator%3==0:raise ValueError('A coefficient has no Gaussian-dyadic reduction modulo3')
        out.append((x.numerator%3)*pow(x.denominator%3,-1,3)%3)
    return out[0]+3*out[1]


def rank_lower(M,rows,columns):
    A=[[mod_coefficient(M[i][j]) for j in columns] for i in rows];r=0
    for column in range(len(columns)):
        pivot=next((i for i in range(r,len(rows)) if A[i][column]),None)
        if pivot is None:continue
        A[pivot],A[r]=A[r],A[pivot];inverse=INV[A[r][column]]
        A[r]=[MUL[x][inverse] for x in A[r]]
        for i in range(r+1,len(rows)):
            c=A[i][column]
            if c:A[i]=[ADD[x][NEG[MUL[c][y]]] for x,y in zip(A[i],A[r])]
        r+=1
        if r==len(rows):break
    return r


def matrix_vector(M,records):
    fields=len(records[0]);out=[]
    for row in M:
        values=[]
        for field in range(fields):
            total=p.ZERO
            for coefficient,record in zip(row,records):total=p.add(total,p.mul(coefficient,record[field]))
            values.append(total)
        out.append(values)
    return out


def scan_records(records,inverse=False):
    fields=len(records[0]);buffer=[p.ZERO]*fields;out=[];reads=0;writes=0
    for current in records:
        original=list(current);reads+=1
        produced=[p.add(x,p.scale(y,-1 if inverse else 1)) for x,y in zip(original,buffer)]
        out.append(produced);writes+=1
        buffer=original if inverse else list(produced)
    buffer=[p.ZERO]*fields
    return out,dict(input_records_read=reads,output_records_written=writes,
                    complete_gaussian_fields=fields,scratch_record_buffers=2,
                    scratch_fields_erased=all(z==p.ZERO for z in buffer),
                    scope='Literal Gaussian record arithmetic and buffer lifecycle; not a bit-level fixed-tape implementation')


def encode_record(values,bank,address,f,grid_bits,magnitude_bits):
    header=format(bank,'03b')+format(address,f'0{f}b')+format(grid_bits,'08b')
    width=1+magnitude_bits+grid_bits;fields=[]
    for z in values:
        for component in z:
            scaled=component*(1<<grid_bits)
            if scaled.denominator!=1 or not -(1<<(width-1))<=scaled<(1<<(width-1)):
                raise ValueError('A record field overflows the declared exact common format')
            fields.append(format(scaled.numerator%(1<<width),f'0{width}b'))
    return header+''.join(fields)


def record_controls(f,forward,pre,events):
    D=1<<f;N=6*D;rng=Random(712003+f)
    records=[[(Q(rng.randrange(-8,9),4),Q(rng.randrange(-8,9),4)) for _ in range(3)] for _ in range(N)]
    original=[list(row) for row in records];apply_word(records,events,f,left=True)
    if records!=matrix_vector(pre,original):raise ValueError('Complete multi-field preword differs from its full matrix')
    restored=[list(row) for row in records];apply_word(restored,events,f,left=True,inverse=True)
    if restored!=original:raise ValueError('Complete Gaussian fields/metadata do not restore under the inverse preword')
    traffic=[]
    for bank in range(6):
        old=original[bank*D:(bank+1)*D]
        prefix,description=scan_records(old);back,back_description=scan_records(prefix,True)
        if back!=old:raise ValueError('Saved-original difference buffer does not invert the scan')
        traffic.append(dict(bank=bank,forward=description,inverse=back_description))
    max_mass=Q(forward['component_l1']);extra=0
    while 1<<extra<max_mass:extra+=1
    common_grid=2+forward['grid_bits'];magnitude_bits=32+extra+1
    encoded=[encode_record(row,i//D,i%D,f,common_grid,magnitude_bits) for i,row in enumerate(records)]
    if len({len(s) for s in encoded})!=1:raise ValueError('The complete per-record metadata/field layout is not uniform')
    return dict(fields_per_record=3,real_imaginary_components=6,actual_common_grid_bits=common_grid,
                declared_magnitude_bits=magnitude_bits,one_record_bits=len(encoded[0]),metadata_bits=3+f+8,
                complete_records_encoded=N,all_fields_and_inverse_restored=True,scan_buffer_traffic=traffic,
                buffer_precision='Prefix sum adds at most f magnitude bits; saved-original difference adds at most one; two complete record buffers and arithmetic temporaries paid.',
                fixed_tape_scope='A contiguous full-record pass with explicit buffer copies has O(V) traffic. Counter/serialization and row-layout/native integration need their own all-size compiler; the finite codec is checked here.')


def probe(case):
    f,layout=case;started=time.monotonic();D=1<<f;W=6;N=W*D;events=word(f,layout)
    pre=p.identity(N);forward=apply_word(pre,events,f,monitor=True)
    inverse=p.identity(N);backward=apply_word(inverse,events,f,inverse=True,monitor=True)
    check=[list(row) for row in inverse];apply_word(check,events,f,left=False)
    if check!=p.identity(N):raise ValueError('The complete scan/mixing preword inverse failed')
    required=[list(row) for row in inverse]
    p.c_side(required,f,range(2,W),left=False,inverse=True);p.c_side(required,f,range(W),left=True)
    recovered=[list(row) for row in required]
    p.c_side(recovered,f,range(2,W),left=False);apply_word(recovered,events,f,left=False)
    target=p.identity(N);p.c_side(target,f,range(W),left=True)
    if recovered!=target:raise ValueError('The complete true pre/post operator does not close')
    broken=[list(row) for row in required];p.c_side(broken,f,range(2,W),left=False)
    apply_word(broken,[event for event in events if event['kind']!='scan'],f,left=False)
    if broken==target:raise ValueError('Omitting every streaming scan incorrectly closes the target')
    lower=[bank*D+a for bank in range(W) for a in range(D//2,D)]
    upper=[bank*D+a for bank in range(W) for a in range(D//2)]
    core=p.identity(N);p.c_side(core,f,range(2,W),left=True)
    cut=dict(field='F3[i]/(i^2+1), irreducible over F3; nonzero minors certify characteristic-zero lower bounds',
             target_lower_rank=rank_lower(target,lower,upper),core_lower_rank=rank_lower(core,lower,upper),
             pre_lower_rank=rank_lower(pre,lower,upper),required_post_lower_rank=rank_lower(required,lower,upper),
             required_post_upper_rank=rank_lower(required,upper,lower))
    if cut['target_lower_rank']!=3*D or cut['core_lower_rank']!=2*D:raise ValueError('The full/missing-line cut capacities differ from their exact tensor ranks')
    record=record_controls(f,forward,pre,events)
    return dict(status='PASS EXACT STREAMING PREPOST PREFLIGHT',selected_columns=f,layout=layout,
                physical_banks=W,operator_dimension=N,complete_target_coefficients_compared=N*N,
                quotient_model='diag(I,I,C_f,C_f,C_f,C_f) -> diag(C_f,...,C_f); distinct-label joint core not identified',
                preword_events=events,forward_prefix=forward,inverse_prefix=backward,
                required_post_operator_sha256=p.matrix_digest(required),required_post_support=p.support_summary(required,W),
                cut_rank_lower_certificates=cut,record_layout_and_buffers=record,
                post_native_word_supplied=False,negative_controls={'omit_all_scans':'COMPLETE OPERATOR REJECTED'},
                scope='Exact finite true pre/post equations, every input bank/field and literal record scan buffers. Derived post is a dense matrix, not a fixed-tape word. Sparse-layer models do not exclude scans.',
                seconds=time.monotonic()-started)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),Path(p.__file__)];hashes={source.name:sha256(source.read_bytes()).hexdigest() for source in sources}
    cases=[(2,0),(2,1),(4,0),(4,1)]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,cases=cases,
                  source_sha256=hashes,stdlib_only=True,seed_rule='712003+selected_columns',
                  hypothesis='One-pass nonunit scans supply dense address mixing outside bounded-fanin models. Test exact multipath prewords and derive complete required post before claiming an adapter.',
                  resource_preflight={'maximum_operator_dimension':96,'expected_aggregate_memory_bytes_upper':256*1024*1024})
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,case):case for case in cases}
        for future in as_completed(jobs):
            result=future.result();results.append(result)
            print(json.dumps({key:result[key] for key in ('status','selected_columns','layout','seconds')}|{'post_support':result['required_post_support']['maximum_coordinate_support'],'post_cut_rank_lower':result['cut_rank_lower_certificates']['required_post_lower_rank']}),flush=True)
    if any(sha256(source.read_bytes()).hexdigest()!=hashes[source.name] for source in sources):raise ValueError('An effective source changed during scan preflight')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results),indent=2)+'\n')


if __name__=='__main__':main()
