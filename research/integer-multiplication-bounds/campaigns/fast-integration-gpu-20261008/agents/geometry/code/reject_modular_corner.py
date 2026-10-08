#!/usr/bin/env python3
"""Independent integer/Bareiss discriminator for a GPU modular corner.

No supplier code is imported. Two separately normalized rational witnesses
check the complete rightmost-pivot chronology after retained permutations.
"""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import argparse,json,time

def pivots(R,C,a,b,degree):
    d=a+b-1;off=a*b-d
    wa=[(i+1)**degree+1 for i in range(a)];wb=[(2*i+1)**degree+2 for i in range(b)];sa,sb=sum(wa),sum(wb)
    A=[[int(r==c)*wb[(off+j)%b]*sa+int(i%b==(off+j)%b)*wa[c]*sb-wa[c]*wb[(off+j)%b]
        for j,c in enumerate(C)] for i,r in enumerate(R)]
    available=list(range(d));previous=1;pp=[];values=[]
    for i in range(d):
        col=next((j for j in reversed(available) if A[i][j]),None);assert col is not None
        pp.append(col);piv=A[i][col];values.append(str(piv));available.remove(col)
        for k in range(i+1,d):
            for j in available:
                value=piv*A[k][j]-A[k][col]*A[i][j]
                assert value%previous==0
                A[k][j]=value//previous
            A[k][col]=0
        previous=piv
    widths=[]
    for i,j in enumerate(pp):
        if i and j==pp[i-1]+1:widths[-1]+=1
        else:widths.append(1)
    return dict(degree=degree,pivots=pp,widths=widths,pivot_numerators=values,
                left_integer_weights=wa,right_integer_weights=wb,
                left_normalization=sa,right_normalization=sb)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();start=time.monotonic()
    data=json.loads(args.input.read_text());a,b=23,25;d=a+b-1;m=a*b;perms=data['permutations']
    assert len(perms)==b and all(sorted(p)==list(range(a)) for p in perms)
    R=[perms[i%b][i//b] for i in range(d)];C=[perms[(m-d+j)%b][(m-d+j)//b] for j in range(d)]
    assert R==data['rows'] and C==data['cols']
    assert R[:a]==list(range(a)) and C[-a:]==list(range(a))
    controls=[pivots(R,C,a,b,k) for k in (1,2)]
    assert all(x['widths']!=data['runs'] for x in controls)
    result=dict(status='REJECT MODULAR-ONLY EXTRA WIDTH2 BLOCK',input_sha256=sha256(args.input.read_bytes()).hexdigest(),
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),candidate_runs=data['runs'],controls=controls,
                conclusion='Two independent exact rational witnesses contradict the GPU65521 profile; no universal rank cuts are requested for this finite-field artifact.',
                elapsed_seconds=time.monotonic()-start,completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.parent.mkdir(parents=True,exist_ok=True);assert not args.output.exists();args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],widths=[c['widths'] for c in controls],seconds=result['elapsed_seconds'])),flush=True)

if __name__=='__main__':main()
