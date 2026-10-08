#!/usr/bin/env python3
"""Cancellation-free weighted triple exclusion with wider point blocks.

Generalizes the paired-support partition of the inherited PairedTriple
producer (Paureel/icekylinx and retained notices) from pairs to arbitrary
fixed block size. Authored with OpenAI Codex assistance. Exact ordinary
supports are tested; this is a scalar generator, not an exponent proof.
"""
import argparse
from collections import defaultdict
from itertools import combinations
import json
from pathlib import Path
from time import perf_counter


class BlockExclusion:
    def __init__(self,n,block_size=3,base=3,combine='balanced'):
        if n<3 or block_size<2 or base<1 or combine not in ('balanced','serial'):
            raise ValueError('invalid generator configuration')
        self.n=n
        self.block_size=block_size
        self.base=base
        self.combine=combine
        self.inputs=list(combinations(range(n),3))
        self.args=[None]+[None]*len(self.inputs)
        self.support=[0]+[1<<j for j in range(len(self.inputs))]
        self.lookup={s:j for j,s in enumerate(self.support)}
        self.variables={s:j+1 for j,s in enumerate(self.inputs)}
        self.calls=defaultdict(int)
        self.outputs=self.deletion(tuple(range(n)),self.variables,3)

    def add(self,a,b):
        if not a:return b
        if not b:return a
        if self.support[a]&self.support[b]:
            raise ValueError('partition supports overlap')
        s=self.support[a]|self.support[b]
        if s in self.lookup:return self.lookup[s]
        node=len(self.args)
        self.args.append((a,b))
        self.support.append(s)
        self.lookup[s]=node
        return node

    def total(self,nodes):
        nodes=[x for x in nodes if x]
        if not nodes:return 0
        if self.combine=='serial':
            out=nodes[0]
            for node in nodes[1:]:out=self.add(out,node)
            return out
        while len(nodes)>1:
            nodes=[self.add(nodes[i],nodes[i+1]) if i+1<len(nodes) else nodes[i]
                   for i in range(0,len(nodes),2)]
        return nodes[0]

    def deletion(self,points,weights,k):
        self.calls[(len(points),k)]+=1
        omissions=[s for j in range(min(k,len(points))+1)
                   for s in combinations(points,j)]
        if not weights:return {s:0 for s in omissions}
        degree=max(len(edge) for edge in weights)
        if len(points)<=self.base or k==0 or degree==0:
            return {s:self.total([node for edge,node in weights.items()
                                 if set(s).isdisjoint(edge)]) for s in omissions}
        groups=[points[j:j+self.block_size]
                for j in range(0,len(points),self.block_size)]
        ng=len(groups)
        group_of={v:j for j,group in enumerate(groups) for v in group}
        coarse=defaultdict(list)
        components=defaultdict(lambda:defaultdict(list))
        for edge,node in weights.items():
            touched=frozenset(group_of[x] for x in edge)
            coarse[tuple(sorted(touched))].append(node)
            for size in range(1,len(edge)+1):
                for chosen in combinations(edge,size):
                    chosen_set=set(chosen)
                    chosen_groups=frozenset(group_of[x] for x in chosen)
                    if len(chosen_groups)>k:
                        continue
                    # For an output omitting points from each touched block,
                    # at least one point of that block must remain omittable.
                    if any(set(groups[j])<=chosen_set for j in chosen_groups):
                        continue
                    if any(x not in chosen_set and group_of[x] in chosen_groups
                           for x in edge):
                        continue
                    residual=tuple(sorted(touched-chosen_groups))
                    components[chosen][residual].append(node)
        contracted={edge:self.total(nodes) for edge,nodes in coarse.items()}
        empty_answers=self.deletion(tuple(range(ng)),contracted,k)
        part_answers={}
        for chosen,pieces in components.items():
            chosen_groups=frozenset(group_of[x] for x in chosen)
            remaining=tuple(j for j in range(ng) if j not in chosen_groups)
            contracted={edge:self.total(nodes) for edge,nodes in pieces.items()}
            # Wider blocks can retain two vertices of X in one touched
            # block. The number of further OMITTED blocks is controlled by
            # touched blocks, not by the degree drop |X|. Keeping those two
            # quantities separate is essential beyond pair blocks.
            part_answers[chosen]=self.deletion(remaining,contracted,
                                               k-len(chosen_groups))
        answers={}
        for omitted in omissions:
            omitted_set=set(omitted)
            touched=tuple(sorted({group_of[x] for x in omitted}))
            survivors=tuple(x for j in touched for x in groups[j]
                            if x not in omitted_set)
            pieces=[empty_answers[touched]]
            for size in range(1,min(degree,len(survivors))+1):
                for chosen in combinations(survivors,size):
                    if chosen not in part_answers:continue
                    chosen_groups={group_of[x] for x in chosen}
                    remaining=tuple(j for j in touched if j not in chosen_groups)
                    pieces.append(part_answers[chosen][remaining])
            answers[omitted]=self.total(pieces)
        return answers

    def active(self,roots):
        used=set()
        stack=list(roots)
        while stack:
            node=stack.pop()
            if not node or node in used:continue
            used.add(node)
            if self.args[node]:stack.extend(self.args[node])
        return used

    def verify(self,central_disjoint=0):
        roots=[self.outputs[t] for t in self.inputs]
        roots.extend(self.outputs[(i,)] for i in range(central_disjoint))
        active=self.active(roots)
        for omitted in self.inputs+[(i,) for i in range(central_disjoint)]:
            expected=sum(1<<j for j,t in enumerate(self.inputs)
                         if set(omitted).isdisjoint(t))
            if self.support[self.outputs[omitted]]!=expected:
                raise ValueError('wrong exclusion answer '+repr(omitted))
        for node in active:
            if self.args[node]:
                a,b=self.args[node]
                if self.support[a]&self.support[b] or self.support[node] != self.support[a]|self.support[b]:
                    raise ValueError('invalid partition addition')
        return dict(n=self.n,block_size=self.block_size,base=self.base,
                    combine=self.combine,input_count=len(self.inputs),
                    retained_exclusion_outputs=len(roots),
                    active_additions=sum(bool(self.args[x]) for x in active),
                    generated_additions=sum(bool(a) for a in self.args),
                    active_nodes=len(active),
                    recursion_calls={str(k):v for k,v in sorted(self.calls.items())},
                    exact_supports_checked=True,
                    scope='Cancellation-free scalar exclusion DAG only; no physical network or exponent')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--n',type=int,required=True)
    parser.add_argument('--block-size',type=int,default=3)
    parser.add_argument('--base',type=int,default=3)
    parser.add_argument('--combine',choices=('balanced','serial'),default='balanced')
    parser.add_argument('--central-disjoint',type=int,default=0)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('output must be new')
    start=perf_counter()
    generator=BlockExclusion(args.n,args.block_size,args.base,args.combine)
    answer=generator.verify(args.central_disjoint)
    answer['elapsed_seconds']=perf_counter()-start
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(answer,indent=2)+'\n')
    print(json.dumps(answer))


if __name__=='__main__':main()
