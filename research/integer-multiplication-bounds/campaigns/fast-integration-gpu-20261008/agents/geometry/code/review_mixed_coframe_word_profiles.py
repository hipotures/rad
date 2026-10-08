#!/usr/bin/env python3
"""Independent explicit Fraction Gram controls for RADCOF01 actual words."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import isqrt, lcm, prod
from pathlib import Path
import struct
import time

from rational_one_core_frame_controls import (explicit_gram_projector, identity,
    mm, ordered_pivots, transpose)
from review_positive_physical_profiles import projector


def proven_prime(value):
    return value >= 2 and all(value % d for d in range(2, isqrt(value)+1))


def read_actual_frames(path):
    data = Path(path).read_bytes()
    assert data[:8] == b'RADCOF01', 'Mixed semantic tag is mandatory'
    h, v, R, nf, nt, singles, rank_mass, loss = struct.unpack_from('<6I2Q', data, 8)
    assert len(data) == 48+nf*(12+h)+nt*16
    frames = []
    for i in range(nf):
        offset = 48+i*(12+h)
        flagged, rank = struct.unpack_from('<QI', data, offset)
        complemented = bool(flagged >> 63)
        forced = flagged & ((1 << 63)-1)
        symbols = struct.unpack_from(f'<{h}b', data, offset+12)
        if complemented:
            assert forced.bit_count() == 1
            classes = {abs(x) for x in symbols if abs(x)>1}
            assert rank == h-1-len(classes)
        frames.append(dict(rank=rank,forced=forced,symbols=symbols,
                           complemented=complemented))
    transitions = []
    offset = 48+nf*(12+h)
    for i in range(nt):
        a,b,count = struct.unpack_from('<2Iq',data,offset+16*i)
        assert a<nf and b<nf and count>0
        assert frames[b]['rank']>frames[a]['rank']
        transitions.append((a,b,count))
    assert sum((frames[b]['rank']-frames[a]['rank'])*count
               for a,b,count in transitions)+singles == rank_mass
    return h, frames, transitions


def normal_rows(h, frame):
    common = frame['forced'].bit_length()-1
    outside = [i for i in range(h) if i != common]
    symbols = frame['symbols']
    classes = sorted({abs(x) for x in symbols if abs(x)>1})
    rows = [[Q(1 if symbols[i]>0 else -1) if abs(symbols[i])==label else Q(0)
             for i in outside] for label in classes]
    return common,outside,rows


def exact_frame(h, frame, basis):
    if frame['forced'] == 0:
        assert frame['rank'] in (0,h) and not frame['complemented']
        return identity(h) if frame['rank'] else [[Q(0)]*h for _ in range(h)]
    if frame['complemented']:
        _, n, d = basis.split(':')
        common, outside, normals = normal_rows(h,frame)
        P,B = explicit_gram_projector(h,common,normals,Q(int(n),int(d)))
        assert len(B[0]) == frame['rank']
        return P
    return projector(h,frame['forced'],frame['symbols'],basis)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--samples',type=int,default=48)
    parser.add_argument('--minimum-coframe-controls',type=int,default=24)
    args = parser.parse_args()
    assert not args.output.exists()
    started = time.monotonic()
    results = []
    for config in json.loads(args.input.read_text()):
        h,frames,transitions = read_actual_frames(config['binary'])
        audit = json.loads(Path(config['audit']).read_text())
        profile = json.loads(Path(config['profile']).read_text())
        assert audit['h']==h and audit['basis']==config['basis']==profile['basis']
        literal = {(a,b):count for a,b,count in transitions}
        rows = audit['transitions']
        assert all(literal[row['a'],row['b']]==row['count'] for row in rows)
        coframes = [row for row in rows if frames[row['a']]['complemented']
                    or frames[row['b']]['complemented']]
        assert len(coframes)>=args.minimum_coframe_controls
        selected = []
        for key in [lambda r:(r['prime_count'],r['rank'],r['count']),
                    lambda r:(r['count'],r['rank']),
                    lambda r:(r['rank']==2,r['rank'],r['count']),
                    lambda r:(r['rank'],r['prime_count'])]:
            for row in sorted(coframes if coframes else rows,key=key,reverse=True)[:args.samples//4+1]:
                if row not in selected:
                    selected.append(row)
        for row in coframes+rows:
            if len(selected)>=args.samples:
                break
            if row not in selected:
                selected.append(row)
        selected = selected[:args.samples]
        assert sum(frames[r['a']]['complemented'] or frames[r['b']]['complemented']
                   for r in selected)>=args.minimum_coframe_controls
        primes = profile['primes']
        assert len(set(primes))==len(primes) and all(proven_prime(p) for p in primes)
        _,n,d = config['basis'].split(':')
        beta = Q(int(n),int(d))
        assert 1-h*beta
        Linverse = [[Q(i==j)+beta/(1-h*beta) for j in range(h)] for i in range(h)]
        H0 = [[Q(i==j)-Q(1,9) for j in range(h)] for i in range(h)]
        metric = mm(mm(transpose(Linverse),H0),Linverse)
        L = [[Q(i==j)-beta for j in range(h)] for i in range(h)]
        cache,frame_receipts,checks = {},{},[]
        for row in selected:
            for fid in (row['a'],row['b']):
                if fid not in cache:
                    P = cache[fid] = exact_frame(h,frames[fid],config['basis'])
                    assert mm(P,P)==P
                    assert sum(P[i][i] for i in range(h))==frames[fid]['rank']
                    assert mm(transpose(P),metric)==mm(metric,P)
                    source_count = 0
                    if frames[fid]['complemented']:
                        common,outside,normals = normal_rows(h,frames[fid])
                        row_sums = [sum(values) for values in P]
                        for a,b in combinations(range(h-1),2):
                            if all(normal[a]+normal[b]==0 for normal in normals):
                                triple = (common,outside[a],outside[b])
                                source = [Q(i in triple)-3*beta for i in range(h)]
                                image = [sum(P[i][j] for j in triple)-3*beta*row_sums[i]
                                         for i in range(h)]
                                assert image==source
                                source_count += 1
                    frame_receipts[fid] = dict(rank=frames[fid]['rank'],
                        complemented=frames[fid]['complemented'],
                        explicit_kernel_B_H0_Gram=True,idempotent=True,
                        trace_rank=True,transformed_H0_selfadjoint=True,
                        compatible_source_lines_independently_included=source_count)
            A,B = cache[row['a']],cache[row['b']]
            assert mm(A,B)==A and mm(B,A)==A
            M = [[y-x for x,y in zip(old,new)] for old,new in zip(A,B)]
            assert mm(M,M)==M
            assert sum(M[i][i] for i in range(h))==row['rank']
            denominator = lcm(*(x.denominator for P in (A,B) for values in P for x in values))
            assert denominator==int(row['integer_denominator'])
            integers = [x*denominator for values in M for x in values]
            assert all(x.denominator==1 for x in integers)
            Z = max(abs(int(x)) for x in integers)
            assert Z==int(row['entry_bound'])
            bound = row['rank']**((row['rank']+1)//2)*Z**row['rank']
            assert bound==int(row['minor_bound'])
            assert prod(primes[:row['prime_count']])>bound
            assert all(denominator%p for p in primes[:row['prime_count']])
            pivots = ordered_pivots(M)
            assert pivots==row['pivots'] and len(pivots)==row['rank']
            checks.append(dict(a=row['a'],b=row['b'],rank=row['rank'],
                prime_count=row['prime_count'],exact_ordered_NE_pivots=pivots,
                contains_complemented_frame=frames[row['a']]['complemented']
                or frames[row['b']]['complemented'],
                both_sided_containment=True,exact_integer_minor_bound=True,
                proven_prime_product_sufficient=True))
            print(json.dumps(dict(case=config['case_id'],completed=len(checks),
                                  total=len(selected))),flush=True)
        results.append(dict(config=config,frames=frame_receipts,checks=checks,
            binary_sha256=sha256(Path(config['binary']).read_bytes()).hexdigest(),
            audit_sha256=sha256(Path(config['audit']).read_bytes()).hexdigest(),
            profile_sha256=sha256(Path(config['profile']).read_bytes()).hexdigest()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(dict(
        status='PASS INDEPENDENT EXACT MIXED COFRAME GRAM AND NE CONTROLS',
        cases=results,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_sha256=sha256(args.input.read_bytes()).hexdigest(),
        elapsed_seconds=time.monotonic()-started,
        completed_utc=datetime.now(timezone.utc).isoformat(),
        scope='Actual RADCOF01 byte-bound transition controls constructed with explicit '
              'kernel B and H0 Gram. Source-line inclusions impose no payload restriction. '
              'Full scalar/physical/source/dirty word, DATA and recurrence assembly '
              'remain separately required.'),indent=2)+'\n')


if __name__ == '__main__':
    main()
