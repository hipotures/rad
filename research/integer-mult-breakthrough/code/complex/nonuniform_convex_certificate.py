#!/usr/bin/env python3
"""Exact convex domination of nonuniform common-frame mean-rank vectors.

Reconstructs all actual edges and searches a fixed equal-weight pair of
Clifford frames per nonlinear candidate. A certificate is a finite scoped
obstruction, not a complete nonlinear-edge routing or multiplication proof.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations_with_replacement
import json
from pathlib import Path
from time import perf_counter

from nonuniform_phase_blocks import classify
from nonlinear_common_frame_screen import (N,compose,inverse,graph_operator,
    clifford_representatives,nonlinear_permutation)
from lagrangian_phase_screen import distance,graph_frames


def run(kind):
    started=perf_counter();reps=clifford_representatives();graphs=graph_frames(N)
    endpoints=[graph_operator(c) for c in range(64)];P,targets=nonlinear_permutation(kind)
    baseline=[[distance(L,G,N) for G in graphs] for L,_,_ in reps]
    pairs=list(combinations_with_replacement(range(len(reps)),2))
    pairrows=[[a+b for a,b in zip(baseline[i],baseline[j])] for i,j in pairs]
    certificates=[];unresolved=[];reasons=Counter()
    for index,(L,F,word) in enumerate(reps):
        common=compose(F,P);cost=[]
        for endpoint in endpoints:
            value,reason=classify(compose(common,inverse(endpoint)));cost.append(value);reasons[reason]+=1
        valid=[c for c,value in enumerate(cost) if value is not None]
        # All observed block rank averages are half-integral; verify this
        # instead of rounding a candidate cost into a favorable inequality.
        assert all((2*cost[c]).denominator==1 for c in valid)
        upper=[int(2*cost[c]) for c in valid]
        found=next((j for j,row in enumerate(pairrows)
                    if all(row[c]<=bound for c,bound in zip(valid,upper))),None)
        if found is None:
            unresolved.append(dict(candidate=index,parent_lagrangian=L,valid_codes=valid,
                                   mean_ranks=[str(cost[c]) for c in valid]));continue
        a,b=pairs[found]
        assert all(2*cost[c]>=baseline[a][c]+baseline[b][c] for c in valid)
        certificates.append(dict(candidate=index,parent_lagrangian=L,parent_word=word,
            valid_graph_codes=valid,mean_ranks=[str(cost[c]) for c in valid],
            dominating_clifford_lagrangians=[reps[a][0],reps[b][0]],weights=['1/2','1/2'],
            dominating_rank_pairs=[[baseline[a][c],baseline[b][c]] for c in valid]))
    return dict(status='EXACT CONVEX MEAN-RANK CERTIFICATES',family=kind,right_toffoli_targets=targets,
                candidate_count=135,graph_endpoint_count=64,edge_classification=dict(reasons),
                certified_candidates=len(certificates),unresolved_candidates=unresolved,
                equal_weight_pair_domain=len(pairs),certificates=certificates,
                elapsed_seconds=perf_counter()-started,
                scope='Finite admitted direct-sum C-block common-frame family. Convex mean-rank domination excludes mean-rank and asymptotic concave-rank-moment gains within its hypotheses, not other frames, multi-child nonblock interfaces, paid tensor routing or integer-multiplication algorithms.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--family',choices=('toffoli0','toffoli1','toffoli2','cycle'),required=True)
    p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    if a.output.exists():raise FileExistsError('Use a fresh output')
    result=run(a.family);result['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('certificates','unresolved_candidates')})+
          ', unresolved='+str(len(result['unresolved_candidates'])),flush=True)


if __name__=='__main__':main()
