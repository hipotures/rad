#!/usr/bin/env python3
"""Exact support-span drops in the cancellation-allowing trimmed side DAG.

The scalar DAG is a read-only coordinator input. This audit calculates
actual characteristic-zero coefficients and binary spans at its gates;
it neither assigns physical roles nor infers a global rank lower bound.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
from time import perf_counter

from lagrangian_phase_screen import basis

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'obstructions'))
from trimmed_side_transform import build_dag,side_value


def support_span(values,labels):
    return basis(tuple(label for value,label in zip(values,labels) if value))


def run(h,k):
    started=perf_counter();dag=build_dag(h,k);labels=dag['top'];v=len(labels)
    denominator=max(c.denominator for c in dag['newton'])
    rows=[];spans=[];drop_hist=Counter();drops=[]
    for node_id,node in enumerate(dag['nodes']):
        if node[0]=='input':
            row=[denominator*int(j==node[1]) for j in range(v)]
            span=(labels[node[1]],)
        elif node[0]=='add':
            a,b=node[1:];row=[x+y for x,y in zip(rows[a],rows[b])]
            span=support_span(row,labels);union=basis(spans[a]+spans[b])
            drop=len(union)-len(span)
            assert drop>=0 and len(basis(union+span))==len(union)
            drop_hist[drop]+=1
            if drop:drops.append(dict(node=node_id,parents=[a,b],
                                      union_rank=len(union),output_rank=len(span),rank_drop=drop))
        else:
            a,num,den=node[1:];products=[x*num for x in rows[a]]
            assert all(x%den==0 for x in products)
            row=[x//den for x in products];span=support_span(row,labels)
            assert span==spans[a]
        rows.append(row);spans.append(span)
    frontier=[]
    for target,output_id in zip(labels,dag['outputs']):
        row=rows[output_id];node=dag['nodes'][output_id]
        assert node[0]=='add'
        for source,value in zip(labels,row):
            assert value==denominator*side_value(k,(target&source).bit_count())
        assert row[labels.index(target)]==0
        span=spans[output_id];a,b=node[1:];union=basis(spans[a]+spans[b])
        assert len(span)==h-1 and len(union)==h
        assert all(not ((target&x).bit_count()%2) for x in span)
        # The top identity signal remains in a predecessor until this gate.
        self_index=labels.index(target)
        assert rows[a][self_index] and rows[b][self_index]
        assert rows[a][self_index]==-rows[b][self_index]
        frontier.append(dict(target=target,output_node=output_id,parents=[a,b],
                             parent_span_dimensions=[len(spans[a]),len(spans[b])],
                             union_rank=len(union),output_rank=len(span),
                             canceled_self_coefficients=[rows[a][self_index],rows[b][self_index]],
                             scale_denominator=denominator))
    parent_source=Path(__file__).resolve().parents[1]/'obstructions'/'trimmed_side_transform.py'
    return dict(status='PASS exact cancellation frontier support spans',h=h,k=k,vertices=v,
                scalar_nodes=len(rows),denominator_basis=denominator,
                all_coefficient_checks=v*v,additive_rank_drop_histogram=dict(sorted(drop_hist.items())),
                total_cancellation_rank_drop=sum(x['rank_drop'] for x in drops),
                rank_decreasing_additions=drops,final_output_rank_drops=len(frontier),
                final_output_frontier=frontier,
                producer_input_sha256=sha256(parent_source.read_bytes()).hexdigest(),
                result_sha256=sha256(str(rows).encode()).hexdigest(),
                elapsed_seconds=perf_counter()-started,
                scope='Exact scalar coefficient/spans only. Every final node drops h to h-1 in this DAG. This is not a lower bound on arbitrary global dirty or phase chronologies.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--h',required=True,type=int)
    p.add_argument('--k',required=True,type=int);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    if not 3<=a.k<a.h<=12 or a.k%2!=1:raise ValueError('Unsupported bounded coefficient audit')
    if a.output.exists():raise FileExistsError('Use a fresh output')
    result=run(a.h,a.k);result['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:value for key,value in result.items()
                      if key not in ('rank_decreasing_additions','final_output_frontier')}),flush=True)


if __name__=='__main__':main()
