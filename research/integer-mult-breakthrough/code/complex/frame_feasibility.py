#!/usr/bin/env python3
"""Find exact nodewise obstructions to monotone nondegenerate frame labels.

For scalar DAG node n, let U be the binary span of all contributing input
labels, and H the intersection of all downstream target kernels. A nested
nondegenerate frame would obey U<=F_n<=H. If U intersects rad(H), no such
frame exists. This is a necessary local test, not a synthesis algorithm.
"""
import argparse
import json
from pathlib import Path
from time import perf_counter

from tree_intersection import TreeIntersection


def basis(rows):
    pivots={}
    for row in rows:
        while row:
            j=row.bit_length()-1
            if j not in pivots:
                pivots[j]=row
                break
            row ^= pivots[j]
    return tuple(pivots[j] for j in sorted(pivots,reverse=True))


def merge(left,right):return basis(left+right)


def nullspace(rows,columns):
    pivots={}
    for row in rows:
        while row:
            j=row.bit_length()-1
            if j not in pivots:
                pivots[j]=row
                break
            row ^= pivots[j]
    result=[]
    for free in range(columns):
        if free in pivots:continue
        value=1<<free
        for j in sorted(pivots):
            if (pivots[j]&value).bit_count()%2:value |=1<<j
        result.append(value)
    return result


def radical(rows):
    gram=[sum(((a&b).bit_count()%2)<<j for j,b in enumerate(rows)) for a in rows]
    coefficients=nullspace(gram,len(rows))
    output=[]
    for coeff in coefficients:
        value=0
        for j,row in enumerate(rows):
            if coeff>>j&1:value ^=row
        output.append(value)
    return tuple(output)


def intersection_witness(U,R):
    pivots={}
    def reduce_U(value):
        for row in U:
            j=row.bit_length()-1
            if value>>j&1:value ^=row
        return value
    for j,row in enumerate(R):
        value=reduce_U(row)
        coefficients=1<<j
        while value:
            pivot=value.bit_length()-1
            if pivot not in pivots:
                pivots[pivot]=(value,coefficients)
                break
            old,mask=pivots[pivot]
            value ^=old
            coefficients ^=mask
        if not value:
            witness=0
            for k,v in enumerate(R):
                if coefficients>>k&1:witness ^=v
            if witness:return witness
    return 0


def check_graph(generator,maximum_witnesses=8):
    n=len(generator.args)
    input_spans=[()]*n
    target_spans=[()]*n
    active=set()
    roots=[]
    for target,node in generator.outputs.items():
        mask=sum(1<<i for i in target)
        target_spans[node]=merge(target_spans[node],(mask,))
        roots.append(node)
    stack=list(roots)
    while stack:
        node=stack.pop()
        if not node or node in active:continue
        active.add(node)
        if generator.args[node]:stack.extend(generator.args[node])
    for node in range(1,n):
        if generator.args[node]:
            a,b=generator.args[node]
            input_spans[node]=merge(input_spans[a],input_spans[b])
        else:
            bit=generator.negative[node]|generator.positive[node]
            source=generator.inputs[bit.bit_length()-1]
            input_spans[node]=(sum(1<<i for i in source),)
    for node in range(n-1,0,-1):
        if generator.args[node]:
            for child in generator.args[node]:
                target_spans[child]=merge(target_spans[child],target_spans[node])
    failures=degenerate_common=0
    witnesses=[]
    for node in sorted(active):
        U=input_spans[node]
        M=target_spans[node]
        # H=M^perp and rad(H)=M intersect M^perp=rad(M).
        if any((u&m).bit_count()%2 for u in U for m in M):
            raise ValueError('scalar supports do not fit downstream target kernels')
        R=radical(M)
        if R:degenerate_common+=1
        witness=intersection_witness(U,R)
        if witness:
            failures+=1
            if len(witnesses)<maximum_witnesses:
                witnesses.append(dict(node=node,input_span_basis=list(U),
                    downstream_target_span_basis=list(M),common_kernel_radical_basis=list(R),
                    nonzero_forbidden_vector=witness,
                    input_span_dimension=len(U),common_kernel_dimension=generator.h-len(M)))
    return dict(h=generator.h,combine=generator.combine,active_nodes=len(active),
                common_kernel_degenerate_nodes=degenerate_common,
                nodewise_nonintersecting_frame_obstructions=failures,
                exact_witnesses=witnesses,
                scope='Necessary obstruction to nested nondegenerate frames for this scalar DAG only; changed phase schedules unrestricted')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h',type=int,required=True)
    parser.add_argument('--combine',choices=('balanced','serial'),default='balanced')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('output must be new')
    start=perf_counter()
    generator=TreeIntersection(args.h,args.combine)
    generator.verify()
    result=check_graph(generator)
    result['elapsed_seconds']=perf_counter()-start
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='exact_witnesses'}))


if __name__=='__main__':main()
