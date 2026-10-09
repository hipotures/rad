#!/usr/bin/env python3
"""Literal triple-center/edge-side word through pinned actual Clifford frames.

Bounded physical evidence for a framed identity shear. Generic intermediate
frames need not be convolutions, so origin columns alone are not promoted
to full physical coverage. Canonical C_h wrapper costs remain separate.
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

COMPLEX=Path(__file__).resolve().parents[1]/'complex'
sys.path.insert(0,str(COMPLEX))
import canonical_subspace_frames as cf
import triple_total_centers as triple
import closed_center_release as center_word
import geodesic_edge_side_splice as side_word


def normalize(vector, exponent):
    if not any(a or b for a,b in vector):return tuple(vector),0
    while exponent and all(not(a%2 or b%2) for a,b in vector):
        vector=[(a//2,b//2) for a,b in vector];exponent-=1
    return tuple(vector),exponent


def plus(a,b,coefficient):
    values,e=a;other,f=b;n,d=coefficient.numerator,coefficient.denominator
    k=(d-1).bit_length()
    if d != 1<<k:raise ValueError('Non-dyadic scalar coefficient')
    target=max(e,f+k);left=target-e;right=target-f-k
    return normalize([((x<<left)+n*(u<<right),(y<<left)+n*(v<<right))
                      for (x,y),(u,v) in zip(values,other)],target)


def multiply(a,coefficient):
    zero=(tuple((0,0) for _ in a[0]),0)
    return plus(zero,a,coefficient)


def line(a,direction,inverse=False):
    values,e=a;out=list(values);lo,hi=((1,-1),(1,1)) if inverse else ((1,1),(1,-1))
    for x in range(len(out)):
        y=x^direction
        if x>=y:continue
        u,v=values[x],values[y]
        first=cf.add(cf.mul(lo,u),cf.mul(hi,v));second=cf.add(cf.mul(hi,u),cf.mul(lo,v))
        out[x],out[y]=first,second
    return normalize(out,e+1)


def literal_frame_column(spec,a):
    values,e=a;n=spec['n'];size=1<<n
    for event in spec['word']:
        kind=event[0]
        if kind=='quadratic_phase':
            values=tuple(cf.phase(z,event[1]*address.bit_count()) for address,z in enumerate(values))
        elif kind in ('linear_route','linear_route_inverse'):
            columns=event[1];permutation=[cf.embed(x,columns) for x in range(size)]
            if kind.endswith('_inverse'):
                values=tuple(values[permutation[x]] for x in range(size))
            else:
                out=[(0,0)]*size
                for x,z in enumerate(values):out[permutation[x]]=z
                values=tuple(out)
        elif kind=='H_tilde':
            for bit in range(event[1]):
                mask=1<<bit;out=list(values)
                for x in range(size):
                    if x&mask:continue
                    y=x|mask;u,v=values[x],values[y]
                    out[x]=cf.mul((1,1),cf.add(u,v))
                    out[y]=cf.mul((1,1),(u[0]-v[0],u[1]-v[1]))
                values,e=normalize(out,e+1)
        elif kind=='C_full':
            for bit in range(n):values,e=line((values,e),1<<bit)
        elif kind in ('C_line','C_line_inverse'):
            values,e=line((values,e),event[1],kind.endswith('_inverse'))
        else:raise ValueError('Unknown literal canonical frame gate')
    return normalize(values,e)


def bind_frame(E,n):
    frame=cf.frame_matrix(E,n);spec=frame['spec'];r=frame['denominator_bits'];size=1<<n
    for column in range(size):
        initial=(tuple((int(x==column),0) for x in range(size)),0)
        values,e=literal_frame_column(spec,initial)
        if e>r:raise ValueError('Literal frame lost the promised dyadic grid')
        if any((a<<(r-e),b<<(r-e))!=frame['numerator'][row][column]
               for row,(a,b) in enumerate(values)):
            raise ValueError('Literal D/P/H gate word differs from the canonical coefficient API')
    return frame


def apply_matrix(a,M,bits,h,columns,inverse=False):
    values,e=a;volume=len(values);size=1<<h
    if not any(x or y for x,y in values):return a
    if inverse:M=[[cf.conj(M[j][i]) for j in range(size)] for i in range(size)]
    for column in range(columns):
        positions=[bit*columns+column for bit in range(h)]
        mask=sum(1<<position for position in positions);out=[(0,0)]*volume
        for outside in range(volume):
            if outside&mask:continue
            addresses=[outside|sum(((x>>bit)&1)<<positions[bit] for bit in range(h)) for x in range(size)]
            for x,address in enumerate(addresses):
                total=(0,0)
                for y,other in enumerate(addresses):
                    if M[x][y]!=(0,0):total=cf.add(total,cf.mul(M[x][y],values[other]))
                out[address]=total
        values,e=normalize(out,e+bits)
    return values,e


def schedule(h,reverse=False):
    compiled=triple.word(h);labels=[sum(1<<j for j in source) for source in compiled['source_order']]
    v=len(labels);q=h;full=tuple(1<<j for j in range(h));zero=()
    central=lambda a,b:Q((a&b).bit_count()-1,2)
    edges=side_word.edge_set(labels,central)
    if reverse:edges=list(reversed(edges))
    current={j:cf.basis((T,)) for j,T in enumerate(labels)}
    current.update({j:zero for j in range(v,3*v+len(edges))});initial=dict(current)
    events=[];moves=[];frame_cache={};edge_cache={};hist=Counter()
    def frame(E):
        E=cf.basis(E)
        if E not in frame_cache:frame_cache[E]=bind_frame(E,h)
        return frame_cache[E]
    def move(role,E):
        E=cf.basis(E);before=current[role]
        if before==E:return
        key=(before,E)
        if key not in edge_cache:
            rising=len(E)>=len(before);low,high=(before,E) if rising else (E,before)
            nf=cf.compile_nested(low,high,h)
            M,bits=cf.relative_matrix(frame(low),frame(high))
            edge_cache[key]=(M,bits,not rising,nf)
        M,bits,inverse,nf=edge_cache[key]
        index=len(moves);moves.append(dict(role=role,before=before,after=E,normal_form=nf,inverse=inverse))
        events.append(('move',role,key));hist[nf['selected_rank_per_column']]+=1;current[role]=E
    def add(a,b,coefficient):
        if current[a]!=current[b]:raise ValueError('Scalar gate sees unequal ACTUAL pinned operators')
        events.append(('add',a,b,coefficient))
    def basis(inverse=False):
        word=compiled['gates']
        if inverse:word=center_word.bank.invert(word)
        for event in word:
            kind,a,*rest=event;a+=2*v
            if kind=='add':b,c=rest;add(a,2*v+b,c)
            elif kind=='scale':
                c,=rest;events.append(('scale',a,c))
            else:raise ValueError('Unexpected triple basis event')
    decoder=[]
    for target in compiled['source_order']:
        zero_member=int(0 in target)
        decoder.append([Q(3*zero_member-1,2)]+[Q(int(i in target)-zero_member,2) for i in range(1,h)])
    def scatter(sign):
        for target,coefficients in enumerate(decoder):
            for feature,c in enumerate(coefficients):
                if c:add(v+target,2*v+feature,sign*c)
    basis();scatter(-1);basis(True)
    for j,(target,source,c) in enumerate(edges):add(v+target,3*v+j,-c)
    for source,T in enumerate(labels):
        move(2*v+source,(T,));add(2*v+source,source,Q(1));move(2*v+source,full)
    for j,(_,source,_) in enumerate(edges):
        move(3*v+j,(labels[source],));add(3*v+j,source,Q(1))
    basis()
    for feature in range(q):move(2*v+feature,zero)
    scatter(1)
    for feature in range(q):move(2*v+feature,full)
    basis(True)
    for j,(target,source,c) in enumerate(edges):
        E=cf.basis(current[v+target]+(labels[source],))
        move(v+target,E);move(3*v+j,E);add(v+target,3*v+j,c);move(3*v+j,full)
    for target,T in enumerate(labels):move(v+target,cf.perpendicular((T,),h))
    for source,T in enumerate(labels):
        move(source,full);add(2*v+source,source,Q(-1))
    for j,(_,source,_) in enumerate(edges):add(3*v+j,source,Q(-1))
    rank=sum(width*count for width,count in hist.items());stock=3*v+len(edges)
    if rank!=stock*h-2*v+2*q*h:raise ValueError('Actual pinned frame histogram differs from geometric ledger')
    for E in set(initial.values())|set(current.values()):frame(E)
    return dict(h=h,v=v,q=q,labels=labels,edges=edges,events=events,moves=moves,
                frames=frame_cache,relative=edge_cache,initial=initial,final=current,
                histogram=dict(sorted(hist.items())),stock=stock,rank=rank,deficit=stock*h-rank)


def execute(spec,data,columns,omit_cleanup=False,omit_generic_move=False):
    data=list(data);skipped=False
    last_cleanup=len(spec['events'])-len(spec['edges'])
    for index,event in enumerate(spec['events']):
        if event[0]=='move':
            _,role,key=event;M,bits,inverse,nf=spec['relative'][key]
            if omit_generic_move and not skipped and spec['frames'][key[1]]['spec']['anchor']=='generic-dyadic-H':
                skipped=True;continue
            data[role]=apply_matrix(data[role],M,bits,spec['h'],columns,inverse)
        elif event[0]=='scale':_,role,c=event;data[role]=multiply(data[role],c)
        else:
            _,a,b,c=event
            if omit_cleanup and index==last_cleanup:continue
            data[a]=plus(data[a],data[b],c)
    if omit_generic_move and not skipped:raise ValueError('No generic move for this negative control')
    return data


def expected(spec,data,columns):
    virtual=[apply_matrix(a,spec['frames'][spec['initial'][role]]['numerator'],
                          spec['frames'][spec['initial'][role]]['denominator_bits'],spec['h'],columns,True)
             for role,a in enumerate(data)]
    for target in range(spec['v']):virtual[spec['v']+target]=plus(virtual[spec['v']+target],virtual[target],Q(1))
    return [apply_matrix(a,spec['frames'][spec['final'][role]]['numerator'],
                         spec['frames'][spec['final'][role]]['denominator_bits'],spec['h'],columns)
            for role,a in enumerate(virtual)]


def probe(case):
    h,columns,reverse,all_columns=case;start=time.monotonic();spec=schedule(h,reverse)
    size=1<<(h*columns);stock=spec['stock'];checked=0;digest=sha256()
    # h4/f1 is complete. h5 finite field probes and selected origins do not
    # claim full column coverage through nonconvolution intermediate gates.
    column_cases=((role,address) for role in range(stock) for address in range(size)) if all_columns else ((role,0) for role in range(min(stock,3*spec['v']+5)))
    for role,address in column_cases:
        data=[(tuple((int(bank==role and a==address),0) for a in range(size)),0) for bank in range(stock)]
        actual=execute(spec,data,columns);wanted=expected(spec,data,columns)
        if actual!=wanted:raise ValueError('A literal framed source/sink/dirty physical column failed')
        digest.update(str(actual).encode());checked+=1
    fields=3
    for field in range(fields):
        data=[normalize([((a*7+bank*11+field*3)%31-15,(a*13+bank*5+field*17)%29-14)
                         for a in range(size)],(bank+field)%4) for bank in range(stock)]
        actual=execute(spec,data,columns);wanted=expected(spec,data,columns)
        if actual!=wanted:raise ValueError('A complete arbitrary-dirty Gaussian field failed')
        digest.update(str(actual).encode())
    if execute(spec,data,columns,True)==wanted:raise ValueError('Omitted helper cleanup was not detected')
    if execute(spec,data,columns,False,True)==wanted:raise ValueError('A free generic gauge jump was not detected')
    # Independently bind a nonconvolution degenerate representative.
    witness=bind_frame((3,),h)['numerator']
    if all(witness[x][1]==witness[x^1][0] for x in range(1<<h)):
        raise ValueError('The false per-gate XOR covariance control did not discriminate')
    generic=sum(frame['spec']['anchor']=='generic-dyadic-H' for frame in spec['frames'].values())
    if not generic:raise ValueError('The complete word did not exercise a generic actual frame')
    return dict(status='PASS LITERAL PINNED CLIFFORD GEODESIC SIDE WORD',h=h,columns=columns,
                reverse_source_order=reverse,vertices=spec['v'],center_features=spec['q'],side_helpers=len(spec['edges']),
                payload_stock=stock,all_physical_columns=stock*size,explicit_initial_columns=checked,
                coverage='All physical columns' if all_columns else 'Selected origin columns and complete Gaussian dyadic fields only; no origin-only covariance promotion',
                complete_gaussian_fields=fields,full_field_payload_values_checked=fields*stock*size,
                chosen_actual_frames=len(spec['frames']),generic_frames_exercised=generic,
                distinct_exact_relative_operators=len(spec['relative']),actual_frame_moves=len(spec['moves']),
                scalar_additions=sum(event[0]=='add' for event in spec['events']),
                child_width_histogram=spec['histogram'],rank_charge=spec['rank'],capacity=stock*h,deficit=spec['deficit'],
                source_and_virtual_dirty_restored=True,actual_dirty_final='C_full times original virtual dirty',
                actual_source_final='C_full times initial virtual source',actual_sink_final='C_full C_T^-1 times (initial virtual sink+source)',
                all_scalar_frames_identical=True,literal_frame_specs_bound_to_all_coefficients=True,
                omitted_cleanup_detected=True,free_generic_gauge_jump_detected=True,
                per_gate_covariance_shortcut_rejected=True,output_sha256=digest.hexdigest(),seconds=time.monotonic()-start,
                scope='Exact finite framed identity shear through noncoordinate/degenerate actual operators. It is not a raw-input C_h primitive, native fixed-tape compiler, asymptotic guard proof or multiplier exponent.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=4);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    cases=[(4,1,False,True),(4,2,False,False),(5,1,False,False),(5,1,True,False)]
    root=Path(__file__).resolve().parents[1]
    sources=sorted({Path(module.__file__).resolve() for module in sys.modules.values()
                    if getattr(module,'__file__',None) and Path(module.__file__).resolve().is_relative_to(root)
                    and Path(module.__file__).suffix=='.py'}|{Path(__file__).resolve(),center_word.f.SIDE_SOURCE.resolve()})
    hashes={p:sha256(p.read_bytes()).hexdigest() for p in sources}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,
                  cases=cases,seed=None,source_sha256={str(p.relative_to(root)):value for p,value in hashes.items()},
                  scalar_domain='Integer Gaussian numerators with explicit common dyadic denominator per bank',
                  no_origin_only_covariance_assumption=True)
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');receipts=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,case):case for case in cases}
        for future in as_completed(jobs):
            result=future.result();receipts.append(result)
            print(json.dumps({key:result[key] for key in ('status','h','columns','reverse_source_order','explicit_initial_columns','generic_frames_exercised','seconds')}),flush=True)
    if any(sha256(p.read_bytes()).hexdigest()!=value for p,value in hashes.items()):
        raise ValueError('An effective canonical/word source changed during physical replay')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=receipts),indent=2)+'\n')


if __name__=='__main__':main()
