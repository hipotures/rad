#!/usr/bin/env python3
"""Exact discovery controls for a complementary-pair producer architecture.

This checks scalar source identities and the structured binary matrix, not
legal address-frame retirement or an accepted physical construction. The
ordinary interval source supports are inherited from Avi Eisenberg's PR62;
the proposed joint synthesis would use eumemic's PR57 mechanisms. Code and
the independent derivation were prepared with Codex assistance.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time


def binary_rank(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length()-1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return len(basis)


def multiply(rows, vector):
    return sum(((row & vector).bit_count() & 1) << i for i,row in enumerate(rows))


def experiment(h):
    started = time.monotonic()
    n = h-1
    assert n % 2 == 0
    pairs = list(combinations(range(n),2))
    q = len(pairs)
    all_bits = (1 << q)-1
    A = [sum(1 << j for j,other in enumerate(pairs) if not(set(pair)&set(other)))
         for pair in pairs]
    B = [sum(1 << j for j,pair in enumerate(pairs) if vertex in pair)
         for vertex in range(n)]
    for i,(a,b) in enumerate(pairs):
        assert A[i] == (1 << i) ^ B[a] ^ B[b] ^ all_bits
        for j,source in enumerate(pairs):
            # Integer inclusion/exclusion, before characteristic-two reduction.
            coefficient = 1-int(a in source)-int(b in source)+int(source==(a,b))
            assert coefficient == int(not(set((a,b)) & set(source)))
            assert coefficient in (0,1)
    for j in range(q):
        squared_column = multiply(A,multiply(A,1 << j))
        assert squared_column == ((1 << j) ^ (all_bits if q % 2 else 0))
    rank = binary_rank(A)
    assert rank == q-(q % 2)
    # Global pair totals are genuinely shared across common-point contexts.
    triples = list(combinations(range(h),3))
    shared = {}
    for a,b in combinations(range(h),2):
        ab = sum(1 << i for i,t in enumerate(triples) if a in t and b in t)
        ba = sum(1 << i for i,t in enumerate(triples) if b in t and a in t)
        assert ab == ba and ab.bit_count() == h-2
        shared[a,b] = ab
    output_checks = 0
    for c in range(h):
        total = sum(1 << i for i,t in enumerate(triples) if c in t)
        for a,b in combinations([i for i in range(h) if i != c],2):
            exact = total ^ shared[tuple(sorted((c,a)))] ^ shared[tuple(sorted((c,b)))] ^ (1 << triples.index(tuple(sorted((c,a,b)))))
            target = sum(1 << i for i,t in enumerate(triples)
                         if c in t and a not in t and b not in t)
            assert exact == target and exact.bit_count() == (h-3)*(h-4)//2
            output_checks += 1
    raw = '\n'.join(map(str,A)).encode()
    return dict(h=h,n=n,pairs=q,rank=rank,involution=(q % 2 == 0),
                squared_identity='I' if q % 2 == 0 else 'I+J',
                integer_coefficient_checks=q*q,all_source_output_checks=output_checks,
                shared_pair_totals=len(shared),sources=len(triples),matrix_sha256=sha256(raw).hexdigest(),
                seconds=time.monotonic()-started)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dimensions',nargs='+',type=int,default=[23,25])
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()
    rows=[]
    for h in a.dimensions:
        row=experiment(h);rows.append(row);print(json.dumps(row),flush=True)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(dict(status='DISCOVERY EXACT COMPLEMENTARY-PAIR IDENTITIES',
        created_utc=datetime.now(timezone.utc).isoformat(),rows=rows,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        missing='Paid source copies, joint physical synthesis, nonmonotone frame retirement, actual transition profiles, both dirty orientations, source-pair/stock/recurrence/assembly acceptance.'),indent=2)+'\n')


if __name__ == '__main__':
    main()
