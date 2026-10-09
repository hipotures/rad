#!/usr/bin/env python3
"""Import-free exact review of right-reflected actual-frame fixture.

The right inverse is executed in its true temporal order. Pauli conjugation,
small full matrices and independently factorized large literal coefficients
bind monomial and one-child stages, including all global units.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import time

import scalable_frame_review as independent
g=independent.g


TOPIC=Path(__file__).resolve().parents[2]
CONFIG=TOPIC/'configs/transfers/reflected-frame-review.json'


def reduced_basis(rows):
    pivots={}
    for value in rows:
        for bit in sorted(pivots,reverse=True):
            if value>>bit&1:value^=pivots[bit]
        if value:
            new=value.bit_length()-1
            for bit in pivots:
                if pivots[bit]>>new&1:pivots[bit]^=value
            pivots[new]=value
    return tuple(pivots[bit] for bit in sorted(pivots))


def perpendicular(rows,n):
    rows=reduced_basis(rows);pivots={row.bit_length()-1:row for row in rows};out=[]
    for bit in range(n):
        if bit in pivots:continue
        value=1<<bit
        for pivot,row in pivots.items():
            if independent.dot(value,row):value^=1<<pivot
        out.append(value)
    result=reduced_basis(out)
    if len(result)+len(rows)!=n or any(independent.dot(a,b) for a in rows for b in result):
        raise ValueError('Independent perpendicular construction failed')
    return result


def canonical_spec(rows,n):
    rows=reduced_basis(rows);r=len(rows);word=[]
    spec=dict(n=n,subspace=list(rows),rank=r,gaussian_grid_bits=r)
    if r==0:return spec|dict(anchor='identity',word=[])
    if r==n:return spec|dict(anchor='full-C',word=[['C_full',n]])
    if r==1 and rows[0].bit_count()%2:
        return spec|dict(anchor='odd-line-C',line=rows[0],word=[['C_line',rows[0]]])
    opposite=perpendicular(rows,n)
    if len(opposite)==1 and opposite[0].bit_count()%2:
        return spec|dict(anchor='odd-kernel-C',line=opposite[0],word=[['C_line_inverse',opposite[0]],['C_full',n]])
    columns=list(rows)
    for bit in range(n):
        if independent.linear_rank(columns+[1<<bit])>len(columns):columns.append(1<<bit)
    return spec|dict(anchor='generic-dyadic-H',routing_columns=columns,
        word=[['quadratic_phase',-1,'weight-all-bits'],['linear_route_inverse',columns],
              ['H_tilde',r],['linear_route',columns],['quadratic_phase',-1,'weight-all-bits']])


def stage_forms(form):
    return form.get('stages',[form])


def composed_word(forms):
    word=[]
    for form in forms:word+=independent.compiled_word(form)
    return word


def coefficient(forms,output,input_address):
    if len(forms)==1:return independent.candidate_coefficient(forms[0],output,input_address)
    first,second=forms
    if first['selected_rank_per_column']!=0:raise ValueError('Composite fixture must begin with a paid monomial stage')
    coordinate=independent.embed(input_address,independent.inverse_columns(tuple(first['input_columns'])))
    middle=first['output_affine_offset']^independent.embed(coordinate,first['output_columns'])
    left=independent.candidate_coefficient(first,middle,input_address)
    right=independent.candidate_coefficient(second,output,middle)
    return g.multiply(left,right)


def nonzero_output(forms):
    middle=0
    for form in forms:
        rank=form['selected_rank_per_column'];mask=(1<<rank)-1
        coordinate=independent.embed(middle,independent.inverse_columns(tuple(form['input_columns'])))
        output_coordinate=coordinate&~mask
        middle=form['output_affine_offset']^independent.embed(output_coordinate,form['output_columns'])
    return middle


def review(payload):
    index,case=payload;n=case['n'];kind=case['kind'];source=canonical_spec(case['source_subspace'],n)
    if source!=case['source_canonical_spec']:raise ValueError('Retained source is not the reconstructed actual canonical word')
    target=canonical_spec(perpendicular(case['source_subspace'],n),n) if kind=='reflection' else canonical_spec(case['target_subspace'],n)
    if kind!='reflection' and target!=case['target_canonical_spec']:raise ValueError('Retained target canonical word differs')
    source_word=independent.actual_word(source);target_word=independent.actual_word(target)
    full_word=[('C',1<<bit,1) for bit in range(n)]
    inverse_full=independent.invert_word(full_word)
    actual=independent.invert_word(source_word)+(inverse_full if kind=='right-to-canonical' else full_word)+target_word
    if json.loads(json.dumps(actual))!=case['actual_relative_word']:
        raise ValueError('Retained actual right-background word has the wrong temporal inverse order')
    forms=stage_forms(case['normal_form']);candidate=composed_word(forms)
    if kind=='reflection':expected_rank=0
    else:
        a=perpendicular(case['source_subspace'],n) if kind=='right-to-canonical' else tuple(case['source_subspace'])
        b=tuple(case['target_subspace']) if kind=='right-to-canonical' else perpendicular(case['target_subspace'],n)
        expected_rank=2*independent.linear_rank(a+b)-independent.linear_rank(a)-independent.linear_rank(b)
    if sum(form['selected_rank_per_column'] for form in forms)!=expected_rank:
        raise ValueError('Reflected child differs from the exact complementary Grassmann rank')
    if sum(form['one_bulk_child_calls'] for form in forms)!=int(expected_rank>0):
        raise ValueError('Monomial stages have an extra or missing recursive child')
    generators=[(1<<j,0,0) for j in range(n)]+[(0,1<<j,0) for j in range(n)]
    for initial in generators:
        if independent.pauli(actual,initial,n)!=independent.pauli(candidate,initial,n):
            raise ValueError('Reflected Pauli generator differs')
    components=independent.groups(source,target);relatives=[]
    full_spec=dict(n=n,anchor='full-C')
    for group in components:
        a=independent.local_frame(source,group);b=independent.local_frame(target,group)
        full=independent.local_frame(full_spec,group)
        relatives.append(g.matmul(b,g.matmul(g.adjoint(full) if kind=='right-to-canonical' else full,g.adjoint(a))))
    output=nonzero_output(forms)
    original=independent.actual_coefficient(relatives,components,output,0)
    if original==g.ZERO or coefficient(forms,output,0)!=original:
        raise ValueError('Independent local physical coefficient rejects the actual reflected global scalar')
    entries=0
    if n<=4:
        for a in range(1<<n):
            for b in range(1<<n):
                if independent.actual_coefficient(relatives,components,a,b)!=coefficient(forms,a,b):
                    raise ValueError('Complete small reflected matrix coefficient differs')
                entries+=1
    altered=json.loads(json.dumps(forms));altered[0]['input_quadratic']['constant']=(altered[0]['input_quadratic']['constant']+1)%4
    global_negative=coefficient(altered,output,0)!=original
    altered=json.loads(json.dumps(forms));altered[-1]['output_affine_offset']^=1
    affine_negative=any(independent.pauli(composed_word(altered),initial,n)!=independent.pauli(actual,initial,n) for initial in generators)
    wrong_order=None
    if kind=='right-to-canonical':
        wrong=inverse_full+independent.invert_word(source_word)+target_word
        wrong_order=any(independent.pauli(wrong,initial,n)!=independent.pauli(actual,initial,n) for initial in generators)
        if not wrong_order:raise ValueError('The failed inverse order did not discriminate')
    if not global_negative or not affine_negative:raise ValueError('Reflected scalar/affine mutation passed')
    return dict(index=index,kind=kind,n=n,selected_child_rank=expected_rank,monomial_stages=sum(form['selected_rank_per_column']==0 for form in forms),
        complete_Pauli_generators=2*n,small_matrix_coefficients=entries,actual_right_inverse_order_verified=True,
        independent_literal_block_sizes=[len(group) for group in components],exact_global_coefficient=[str(x) for x in original],
        global_unit_corruption_rejected=global_negative,affine_offset_corruption_rejected=affine_negative,
        failed_inverse_order_rejected=wrong_order,complete_operator_bound_by_generators_and_scalar=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workers',type=int,default=4);parser.add_argument('--output',type=Path)
    args=parser.parse_args();config=json.loads(CONFIG.read_text());fixture=TOPIC/config['fixture'];helper=Path(independent.__file__).resolve();arithmetic=Path(g.__file__).resolve()
    for path,digest in config['pinned_inputs'].items():
        if sha256((TOPIC/path).read_bytes()).hexdigest()!=digest:raise ValueError('Pinned fixture/independent helper changed')
    paths=[Path(__file__).resolve(),CONFIG,fixture,helper,arithmetic]
    hashes={str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,source_config_fixture_sha256=hashes,
        seed=None,scope=config['scope'],producer_imports=False)
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False);(args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    started=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:rows=list(pool.map(review,enumerate(json.loads(fixture.read_text())['cases'])))
    if any(sha256((TOPIC/path).read_bytes()).hexdigest()!=digest for path,digest in hashes.items()):raise ValueError('Source changed during immutable review')
    result=dict(status='INDEPENDENT RIGHT-REFLECTED FRAME REVIEW PASS',cases=rows,seconds=time.monotonic()-started,
        scope=config['scope'],native_stream_cost_proved=False,new_exponent=False)
    if args.output:(args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','seconds','scope']}))


if __name__=='__main__':main()
