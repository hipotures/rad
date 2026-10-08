#!/usr/bin/env python3
"""Exact conjugate-basis transfer plus unchanged literal compiler identity.

No full source-pair data experiment is repeated. Scalar/dirty and physical
closure reuse is accepted only when literal DAG, frame and selected-use
digests equal a named successful independent compiler receipt.
"""
import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
import json
from pathlib import Path
from producer_search import digest


def parameters(h,beta):
    assert 1-h*beta
    gamma=(9*beta-1)/(3*(1-h*beta))
    outside=-beta*(9*beta-1)/(2*(1-h*beta))
    inside=(1-(h-3)*outside)/3
    k=Q(h-9,4); assert k
    c=(2-3*beta*(h-3))/(h-9)
    v=(h-9)*(1-3*beta)/(12*(1-h*beta))
    return dict(beta=beta,gamma=gamma,outside=outside,inside=inside,k=k,c=c,v=v)


def selected_digest(document):
    links=document['selected_links'];canonical=dict(h=links['h'],n=links['n'],links=sorted(links['links']))
    from hashlib import sha256
    return sha256(json.dumps(canonical,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original',type=Path,nargs='+',required=True)
    p.add_argument('--dual',type=Path,nargs='+',required=True)
    p.add_argument('--compiler-receipt',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert len(a.original)==len(a.dual)and not a.output.exists()
    prior=json.loads(a.compiler_receipt.read_text());assert 'complete' in prior['status']
    rows=[]
    for original_path,dual_path in zip(a.original,a.dual):
        old=json.loads(original_path.read_text());new=json.loads(dual_path.read_text());x=old['producer'];y=new['producer'];h=x['h'];assert y['h']==h
        for field in('dag_sha256','positive_sha256'):assert x[field]==y[field],field
        assert selected_digest(old)==selected_digest(new)
        named=next(row for row in prior['rows']if row['h']==h)
        assert named['dag_sha256']==x['dag_sha256'] and 'PASS' in named['status']
        assert named['roles']==x['R']==y['R']
        from hashlib import sha256
        raw_digest=sha256(json.dumps(old['selected_links'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
        assert named['selected_links_sha256']==raw_digest
        for obj in(x,y):
            assert digest(obj['dag_path'])==obj['dag_sha256']
            assert digest(obj['dag_path']+'.positive')==obj['positive_sha256']
        beta=Q(4,3*(h+3));paired=(1-9*beta)/(9*(1-h*beta));assert paired==Q(-1,3)
        A=parameters(h,beta);B=parameters(h,paired)
        assert A['outside']==B['outside'] and A['inside']==B['inside']
        assert B['gamma']==-3*beta and A['gamma']==-3*paired
        assert (1-9*paired)/(9*(1-h*paired))==beta
        source=[];centers=[]
        for delta in(0,1):
            # Source line: primal=1_F-3 beta 1, dual=(1_F+gamma 1)/2.
            primal=delta-3*beta;dual=(delta+A['gamma'])/2
            primal2=delta-3*paired;dual2=(delta+B['gamma'])/2
            assert primal2==2*dual and dual2==primal/2
            assert primal*dual==primal2*dual2
            assert primal and dual and primal2 and dual2
            source.append(dict(inside_triple=bool(delta),product=str(primal*dual)))
            pp=delta+A['c'];qq=A['v']-A['k']*delta
            pp2=delta+B['c'];qq2=B['v']-B['k']*delta
            assert pp2==-qq/A['k'] and qq2==-A['k']*pp
            assert pp*qq==pp2*qq2
            assert pp and qq and pp2 and qq2
            centers.append(dict(at_center_index=bool(delta),product=str(pp*qq)))
        assert 3*A['inside']+(h-3)*A['outside']==1
        rows.append(dict(h=h,R=y['R'],status='literal compiler identity and exact rational basis transfer PASS',
            dag_sha256=y['dag_sha256'],positive_sha256=y['positive_sha256'],
            selected_map_sha256=selected_digest(new),original_witness=str(original_path),dual_witness=str(dual_path),
            beta=str(beta),dual_beta=str(paired),source_weight_classes=source,copied_center_classes=centers,
            projector_identity='P_dual=P_original^T from exchanging w and z in the complete signed-frame formula',
            dirty_closure='Same literal scalar DAG and selected-use map; reuse named independently audited JLV physical compilation',
            local_profile='New dual corner profiles remain the geometry full-CRT certificate; no old NE profile reused',
            data_transfer='Identical weight at each fixed source coordinate and copied-center index; no permutation or source-pair replay',
            finite_field_condition='All stated rational denominators and k nonzero; additional matrix denominator checks are geometry-owned'))
    result=dict(status='complete dual-basis transfer gate PASS',command=__import__('sys').argv,rows=rows,
                completed_utc=datetime.now(timezone.utc).isoformat(),source_sha256=digest(__file__),
                compiler_receipt=str(a.compiler_receipt),compiler_receipt_sha256=digest(a.compiler_receipt),
                scope='Exact finite identity and rational transfer, conditional machine/field realization unchanged')
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['status'])


if __name__=='__main__':main()
