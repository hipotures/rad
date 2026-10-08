#!/usr/bin/env python3
"""Weighted tree-projection side sums for exact five-subset intersections.

Implements the intersection-summation recurrence of Kaski, Koivisto and
Korhonen, arXiv:1208.0554v1 (2012), Section 2.2--2.3. Original authored
implementation, OpenAI Codex assisted. Reuses weighted source coefficients
and exact equal weighted supports. No common-frame or exponent claim.
"""
import argparse
from collections import defaultdict
from itertools import combinations
import json
from pathlib import Path
from time import perf_counter


class TreeIntersection:
    def __init__(self,h,combine='balanced'):
        if h<6 or combine not in ('balanced','serial'):
            raise ValueError('invalid configuration')
        self.h=h
        self.combine=combine
        self.depth=(h-1).bit_length()
        self.inputs=list(combinations(range(h),5))
        self.input_index={t:j for j,t in enumerate(self.inputs)}
        self.args=[None]
        self.negative=[0]
        self.positive=[0]
        self.lookup={(0,0):0}
        self.state_lookup={}
        self.transitions=defaultdict(set)
        self.spans={}
        for triple in self.inputs:
            projections=[tuple(sorted({x>>(self.depth-level) for x in triple}))
                         for level in range(self.depth+1)]
            for level in range(self.depth):
                self.transitions[level,projections[level]].add(projections[level+1])
        self.transitions={key:tuple(sorted(values)) for key,values in self.transitions.items()}
        for level,W in self.transitions:
            self.spans[level,W]=sum(1<<x for x in range(h)
                                   if x>>(self.depth-level) in W)
        self.outputs={target:self.state(0,sum(1<<i for i in target),(0,))
                      for target in self.inputs}

    def source(self,subset,coefficient):
        j=self.input_index[subset]
        negative=(1<<j) if coefficient==-3 else 0
        positive=(1<<j) if coefficient==1 else 0
        key=(negative,positive)
        if key in self.lookup:return self.lookup[key]
        node=len(self.args)
        self.args.append(None)
        self.negative.append(negative)
        self.positive.append(positive)
        self.lookup[key]=node
        return node

    def add(self,a,b):
        if not a:return b
        if not b:return a
        if (self.negative[a]|self.positive[a]) & (self.negative[b]|self.positive[b]):
            raise ValueError('tree-projection parts overlap')
        key=(self.negative[a]|self.negative[b],self.positive[a]|self.positive[b])
        if key in self.lookup:return self.lookup[key]
        node=len(self.args)
        self.args.append((a,b))
        self.negative.append(key[0])
        self.positive.append(key[1])
        self.lookup[key]=node
        return node

    def total(self,nodes):
        nodes=[x for x in nodes if x]
        if not nodes:return 0
        if self.combine=='serial':
            out=nodes[0]
            for node in nodes[1:]:out=self.add(out,node)
            return out
        while len(nodes)>1:
            nodes=[self.add(nodes[j],nodes[j+1]) if j+1<len(nodes) else nodes[j]
                   for j in range(0,len(nodes),2)]
        return nodes[0]

    def state(self,level,A,W):
        if level<self.depth:
            A &= self.spans[level,W]
        key=(level,A,W)
        if key in self.state_lookup:return self.state_lookup[key]
        if level==self.depth:
            intersection=A.bit_count()
            if intersection not in (0,2,4):node=0
            else:node=self.source(W,1 if intersection==2 else -3)
        else:
            node=self.total([self.state(level+1,A & self.child_span(level+1,Z),Z)
                             for Z in self.transitions[level,W]])
        self.state_lookup[key]=node
        return node

    def child_span(self,level,W):
        if level==self.depth:return sum(1<<x for x in W)
        return self.spans[level,W]

    def verify(self):
        v=len(self.inputs)
        full=(1<<v)-1
        point_masks=[sum(1<<j for j,t in enumerate(self.inputs) if i in t)
                     for i in range(self.h)]
        for target,node in self.outputs.items():
            exact=[full]+[0]*5
            # Independent intersection-count partition using point masks.
            for i in target:
                present=point_masks[i]
                exact=[(exact[j]&~present)|((exact[j-1]&present) if j else 0)
                       for j in range(6)]
            if self.negative[node]!=exact[0]|exact[4] or self.positive[node]!=exact[2]:
                raise ValueError('wrong weighted even-intersection side')
        active=set()
        stack=list(self.outputs.values())
        while stack:
            node=stack.pop()
            if not node or node in active:continue
            active.add(node)
            if self.args[node]:stack.extend(self.args[node])
        additions=sum(bool(self.args[x]) for x in active)
        roles=additions+v
        return dict(h=self.h,subset_size=5,v=v,combine=self.combine,
                    memoized_states=len(self.state_lookup),generated_nodes=len(self.args)-1,
                    active_weighted_sources=sum(self.args[x] is None for x in active),
                    active_additions=additions,designated_outputs=v,
                    unmatched_side_roles=roles,unmatched_side_roles_per_source=roles/v,
                    exact_weighted_output_checks=v,
                    source_coefficients=[-3,1],uniform_output_coefficient='1/8',
                    scope='Exact weighted scalar side DAG only; frames, matched carriers, scalar guard and transfer open')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h',type=int,required=True)
    parser.add_argument('--combine',choices=('balanced','serial'),default='balanced')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('output must be new')
    start=perf_counter()
    generator=TreeIntersection(args.h,args.combine)
    answer=generator.verify()
    answer['elapsed_seconds']=perf_counter()-start
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(answer,indent=2)+'\n')
    print(json.dumps(answer))


if __name__=='__main__':main()
