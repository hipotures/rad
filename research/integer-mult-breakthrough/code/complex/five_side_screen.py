#!/usr/bin/env python3
"""Bounded exact side-DAG cost screen for the weight-five hypothesis.

Shares every equal ordinary support globally across degree-five deletion,
pair-conditioned triple deletion and four-star leave-one-out outputs.
This is deliberately a scalar screen, not a valid common-frame compiler.
"""
import argparse
from collections import defaultdict
from itertools import combinations
import json
from pathlib import Path
from time import perf_counter

from block_exclusion import BlockExclusion


class FiveSide(BlockExclusion):
    def __init__(self,n,block_size=2,base=2):
        if n<6:raise ValueError('ground set must exceed five')
        self.n=n
        self.block_size=block_size
        self.base=base
        self.combine='balanced'
        self.inputs=list(combinations(range(n),5))
        self.args=[None]+[None]*len(self.inputs)
        self.support=[0]+[1<<j for j in range(len(self.inputs))]
        self.lookup={s:j for j,s in enumerate(self.support)}
        self.variables={s:j+1 for j,s in enumerate(self.inputs)}
        self.calls=defaultdict(int)
        self.outputs=self.deletion(tuple(range(n)),self.variables,5)
        self.zero={s:self.outputs[s] for s in self.inputs}
        self.two_parts=defaultdict(list)
        for pair in combinations(range(n),2):
            rest=tuple(i for i in range(n) if i not in pair)
            weights={triple:self.variables[tuple(sorted(pair+triple))]
                     for triple in combinations(rest,3)}
            answers=self.deletion(rest,weights,3)
            for excluded in combinations(rest,3):
                target=tuple(sorted(pair+excluded))
                self.two_parts[target].append(answers[excluded])
        self.two={s:self.total(parts) for s,parts in self.two_parts.items()}
        self.four_parts=defaultdict(list)
        for four in combinations(range(n),4):
            rest=tuple(i for i in range(n) if i not in four)
            leaves=[self.variables[tuple(sorted(four+(i,)))] for i in rest]
            prefix=[0]
            for leaf in leaves:prefix.append(self.add(prefix[-1],leaf))
            suffix=[0]*(len(leaves)+1)
            for j in range(len(leaves)-1,-1,-1):
                suffix[j]=self.add(leaves[j],suffix[j+1])
            for j,i in enumerate(rest):
                target=tuple(sorted(four+(i,)))
                self.four_parts[target].append(self.add(prefix[j],suffix[j+1]))
        self.four={s:self.total(parts) for s,parts in self.four_parts.items()}

    def exact_screen(self):
        families={0:self.zero,2:self.two,4:self.four}
        roots=[]
        for intersection,outputs in families.items():
            for target,node in outputs.items():
                expected=sum(1<<j for j,source in enumerate(self.inputs)
                             if len(set(source)&set(target))==intersection)
                if self.support[node]!=expected:
                    raise ValueError('incorrect intersection query')
                roots.append(node)
        active=self.active(roots)
        additions=sum(bool(self.args[x]) for x in active)
        v=len(self.inputs)
        roles=additions+len(roots)
        return dict(h=self.n,subset_size=5,block_size=self.block_size,
                    base=self.base,v=v,side_additions=additions,
                    designated_side_outputs=len(roots),
                    unmatched_side_role_count=roles,
                    unmatched_side_roles_per_source=roles/v,
                    exact_intersection_query_checks=len(roots),
                    global_ordinary_support_interning=True,
                    centers_included=False,carrier_matching_included=False,
                    scope='Exact scalar side DAG only; frame feasibility, matched roles and phases open')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h',type=int,required=True)
    parser.add_argument('--block-size',type=int,default=2)
    parser.add_argument('--base',type=int,default=2)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('output must be new')
    start=perf_counter()
    generator=FiveSide(args.h,args.block_size,args.base)
    answer=generator.exact_screen()
    answer['elapsed_seconds']=perf_counter()-start
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(answer,indent=2)+'\n')
    print(json.dumps(answer))


if __name__=='__main__':main()
