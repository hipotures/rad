#!/usr/bin/env python3
"""Independent Fraction Gram and pivot controls for actual joint-word matrices."""
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from math import lcm
from pathlib import Path
import argparse
import json
import os
import struct
import sys
import time

from review_positive_physical_profiles import mm, projector


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--samples', type=int, default=16)
    args = ap.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    start = time.monotonic()
    (args.work/'process.json').write_text(json.dumps(dict(pid=os.getpid(),command=sys.argv,started_utc=datetime.now(timezone.utc).isoformat()),indent=2)+'\n')
    configs = json.loads(args.input.read_text())
    results = []
    for config in configs:
        packed = Path(config['binary']).read_bytes()
        h,v,R,nf,nt,singles,mass,loss = struct.unpack_from('<6I2Q',packed)
        frames = []
        for fid in range(nf):
            forced,cover,rank = struct.unpack_from('<2QI',packed,40+20*fid)
            symbols = []
            label = 2
            for i in range(h):
                if forced>>i&1:symbols.append(1)
                elif cover>>i&1:symbols.append(label);label += 1
                else:symbols.append(0)
            frames.append((forced,tuple(symbols),rank))
        audit = json.loads(Path(config['audit']).read_text())
        assert audit['h'] == h and audit['basis'] == config['basis']
        rows = audit['transitions']
        chosen = []
        signatures = set()
        for row in sorted(rows,key=lambda x:(x['prime_count'],x['rank'],int(x['entry_bound'])),reverse=True):
            signature=(frames[row['a']][0].bit_count(),frames[row['b']][0].bit_count(),row['rank'])
            if signature not in signatures:
                chosen.append(row);signatures.add(signature)
            if len(chosen)>=args.samples//2:break
        for key in [lambda x:(x['rank']==2,x['count']), lambda x:x['count']]:
            for row in sorted(rows,key=key,reverse=True):
                if row not in chosen:chosen.append(row)
                if len(chosen)>=args.samples:break
            if len(chosen)>=args.samples:break
        cache = {}
        checks = []
        for row in chosen:
            for fid in (row['a'],row['b']):
                if fid not in cache:
                    forced,symbols,rank=frames[fid]
                    if fid==0:P=[[Q(0) for j in range(h)] for i in range(h)]
                    elif fid==1:P=[[Q(i==j) for j in range(h)] for i in range(h)]
                    else:P=projector(h,forced,symbols,config['basis'])
                    cache[fid]=P
            A,B=cache[row['a']],cache[row['b']]
            M=[[y-x for x,y in zip(u,v)] for u,v in zip(A,B)]
            assert mm(A,B)==A and mm(B,A)==A
            assert mm(M,M)==M and sum(M[i][i] for i in range(h))==row['rank']
            # Native projectors use reduced common denominators individually.
            den=lcm(*(x.denominator for P in (A,B) for values in P for x in values))
            assert den==int(row['integer_denominator'])
            Z=max(abs(x*den) for values in M for x in values)
            assert Z.denominator==1 and Z==int(row['entry_bound'])
            bound=row['rank']**((row['rank']+1)//2)*int(Z)**row['rank']
            assert bound==int(row['minor_bound'])
            E=[values[:] for values in M];pivots=[]
            for i in range(h):
                nz=[j for j in range(h) if E[i][j]]
                if not nz:continue
                j=nz[-1];pivots.append([i,j])
                for k in range(i+1,h):
                    scale=E[k][j]/E[i][j]
                    if scale:
                        for col in range(j+1):E[k][col]-=scale*E[i][col]
            assert pivots==row['pivots']
            checks.append(dict(a=row['a'],b=row['b'],rank=row['rank'],count=row['count'],
                exact_pivots=pivots,independent_gram_pass=True,nested_idempotent_pass=True,integer_minor_bound_pass=True))
            status=dict(utc=datetime.now(timezone.utc).isoformat(),case=config['case_id'],completed_controls=len(checks),total_controls=len(chosen),
                        completed=len(results),total=len(configs),elapsed_seconds=time.monotonic()-start,workers=1)
            (args.work/'status.json').write_text(json.dumps(status,indent=2)+'\n')
            print(json.dumps(status),flush=True)
        results.append(dict(case=config,checks=checks,audit_sha256=sha256(Path(config['audit']).read_bytes()).hexdigest(),binary_sha256=sha256(packed).hexdigest()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(dict(status='PASS INDEPENDENT RATIONAL ACTUAL JOINT WORD MATRIX CONTROLS',rows=results,
        completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-start,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),input_sha256=sha256(args.input.read_bytes()).hexdigest(),
        scope='Distinct high-bound/high-rank/high-count/rank-two exact Gram and rational ordered-pivot controls. Full native CRT and literal executed-word verification remain separate.'),indent=2)+'\n')


if __name__ == '__main__':
    main()
