#!/usr/bin/env python3
"""Small discriminator for odd-ground core-two envelope parity.

No flow, coefficient replay, physical schedule or claimed role change.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

from finite_block_search import install_reference
from fast_frame_envelope import labels
from review_odd_pair_witness import build
from review_compound_bit_witness import logical_identity


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists();install_reference(a.reference);start=time.monotonic();rows=[]
    for h in (7,11,13):
        circuit=build(h,2,[0]*h);frames,_=labels(circuit,True)
        counts=Counter();bad=[]
        for node,frame in frames.items():
            if frame.core.bit_count()!=2:continue
            n=frame.vertices.bit_count();counts[n]+=1
            if h-n==8:
                C=[i for i in range(h) if frame.core>>i&1]
                W=[i for i in range(h) if not(frame.vertices>>i&1)]
                radical=[2 if i in C else int(i in W) for i in range(h)]
                targets=[tuple(sorted((p,a,b))) for p in C for a,b in combinations(W,2)]
                assert len(targets)==56 and sum(radical)==12
                assert sum(x*x for x in radical)==sum(radical)**2//9
                assert all(3*sum(radical[i] for i in T)==sum(radical) for T in targets)
                # Sum of every target divided by14 is exactly this radical.
                assert [sum(i in T for T in targets) for i in range(h)]==[14*x for x in radical]
                if not bad:bad.append(dict(node=node,args=circuit.args[node],core=frame.core,vertices=frame.vertices,
                    core_points=C,outside_points=W,radical=radical,target_count=56,
                    target_generator_sum_divisor=14,exact_target_Gram_radical=True))
        rows.append(dict(h=h,base=2,positions=[0]*h,logical_sha256=logical_identity(circuit),
            logical_nodes=len(circuit.active),core_two_union_sizes=dict(sorted(counts.items())),
            all_core_two_unions_even=all(n%2==0 for n in counts),outside_eight_example=bad))
    out=dict(status='PASS small exact parity discriminator',completed_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),rows=rows,
        wall_seconds=time.monotonic()-start,
        conclusion='Odd ground alone does not certify the larger complement family when odd core-two unions are present',
        scope='Original small odd DAG core/union count and explicit rational radical; no full graph/source-frame transfer or bound')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out),flush=True)


if __name__=='__main__':main()
