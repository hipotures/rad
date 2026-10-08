#!/usr/bin/env python3
"""Exact scoped test: free scalar output mixing cannot erase paid correction.

The two-stage endpoint A=Fy, B=Fx+Ey and paid T-copy are Paureel's
mechanism, preserved in PR29/36. The present six-mixer exclusion addresses
an attempted new removal of that charged interface, not all compilers.
"""
import argparse
import json
from pathlib import Path


def permutation(vector,m,swapped):
    result=vector
    for k in swapped:
        if ((vector>>k)^(vector>>(m+k)))&1:
            result^=(1<<k)|(1<<(m+k))
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    mixers=[(a,b,c,d) for a in (0,1) for b in (0,1) for c in (0,1) for d in (0,1) if (a*d-b*c)%2]
    assert len(mixers)==6
    cases=[];probes=0
    for m in range(2,14):
        for rank in range(1,m):
            failures={str(M):0 for M in mixers};paid_failures=0
            for field in (0,1):
                for k in range(2*m):
                    x=(1<<k) if field==0 else 0;y=(1<<k) if field==1 else 0
                    F=lambda z:permutation(z,m,range(m))
                    E=lambda z:permutation(z,m,range(rank,m))
                    T=lambda z:permutation(z,m,range(rank))
                    A,B=F(y),F(x)^E(y);target=(F(y),F(x))
                    for M in mixers:
                        a,b,c,d=M
                        result=((A if a else 0)^(B if b else 0),(A if c else 0)^(B if d else 0))
                        failures[str(M)]+=int(result!=target)
                    paid_failures+=int((A,B^T(A))!=target);probes+=1
            assert min(failures.values())>0 and paid_failures==0
            cases.append(dict(m=m,projector_rank=rank,no_free_mixer_succeeds=True,failed_basis_probes=failures,paid_copy_failures=0))
    result=dict(scope='Only constant pointwise GL2(F2) output mixers, unchanged A/B endpoints and no address action',
                cases=cases,total_basis_probes=probes,paid_rank_correction_retained=True,
                conclusion='A stronger construction needs a changed endpoint/chronology or an explicitly charged address action; no uncharged saving established')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),basis_probes=probes,status='SCOPED NEGATIVE; paid correction verified')))


if __name__=='__main__':main()
