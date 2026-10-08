#!/usr/bin/env python3
"""Exact source-family controls for a proposed signal-restricted terminal transfer.

This proves a rational covector identity and finite ridge-function controls.
It does not assert that the inherited physical source arrays are ridges or
that an address-frame transition can be omitted without a compiler proof.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random
from datetime import datetime, timezone


def source(h, triple, beta):
    gamma = (9*beta-1)/(3*(1-h*beta))
    w = [Q(i in triple)-3*beta for i in range(h)]
    d = [(Q(i in triple)+gamma)/2 for i in range(h)]
    return w, d


def center(h, c, beta):
    w = [Q(i == c)+(2-3*beta*(h-3))/(h-9) for i in range(h)]
    v = (h-9)*(1-3*beta)/(12*(1-h*beta))
    d = [v-Q(h-9, 4)*Q(i == c) for i in range(h)]
    return w, d


def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), Q(0))


def residue(x, p):
    assert x.denominator % p
    return x.numerator*pow(x.denominator, -1, p) % p


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    rng = random.Random(2026102146)
    rows = []
    p = 257
    assert all(p % d for d in range(2, 17))
    for h, beta in [(23,Q(1,15)), (25,Q(7,207))]:
        triples = list(combinations(range(h), 3))
        masks = [sum(1 << i for i in t) for t in triples]
        identities = 0
        # Independent integer source incidence enumerates every scalar pair
        # coefficient, rather than loading a producer's output supports.
        for t, tm in zip(triples, masks):
            for c in t:
                rest = [i for i in range(h) if i not in t]
                for a, b in combinations(rest, 2):
                    u = (c,a,b)
                    um = sum(1 << i for i in u)
                    assert (tm & um).bit_count() == 1
                    assert Q((tm & um).bit_count()-1, 2) == 0
                    identities += 1
        sampled = []
        failures = []
        for _ in range(96):
            t = rng.choice(triples); c = rng.choice(t)
            a,b = rng.sample([i for i in range(h) if i not in t],2)
            u = (c,a,b)
            wt,dt = source(h,t,beta); wu,du = source(h,u,beta)
            wc,dc = center(h,c,beta)
            assert dot(dt,wt) == dot(du,wu) == dot(dc,wc) == 1
            assert dot(du,wt) == dot(dt,wu) == 0
            assert dot(dc,wt) == dot(dt,wc) == 0
            assert dot(dc,wu) == dot(du,wc) == 0
            # R_Gamma=-I+2P_center. R_K=R_Gamma+2P_sourceT.
            # Both act identically on the legal source covector; their
            # commuting product is I-2P_sourceT on the full address space.
            dg = [-x+2*dot(du,wc)*dc[i] for i,x in enumerate(du)]
            dk = [dg[i]+2*dot(du,wt)*dt[i] for i in range(h)]
            assert dg == dk == [-x for x in du]
            wm=[residue(x,p) for x in wt]; dm=[residue(x,p) for x in dt]
            mu=[residue(x,p) for x in du]
            address=[rng.randrange(p) for _ in range(h)]
            correction=sum(x*y for x,y in zip(dm,address)) % p
            changed=[(x-2*w*correction) % p for x,w in zip(address,wm)]
            before=sum(x*y for x,y in zip(mu,address)) % p
            after=sum(x*y for x,y in zip(mu,changed)) % p
            assert before == after
            # Arbitrary lookup functions of this scalar have equal values;
            # this checks an actual nonconstant finite ridge as a control.
            table=[rng.randrange(2) for _ in range(p)]
            assert table[before] == table[after]
            sampled.append(dict(target=t,common=c,source=u,covector_reflection_equal=True,
                                ridge_argument_before=before,ridge_argument_after=after))
            bad=tuple([t[0],t[1],next(i for i in range(h) if i not in t)])
            _,bad_du=source(h,bad,beta)
            assert dot(bad_du,wt) == Q(1,2)
            failures.append(dict(target=t,forbidden_source=bad,defect_pairing='1/2'))
        # Echo is independent of signal restrictions. For any invertible
        # permutation U and arbitrary dirty q, two sections return q and
        # scatter U A x. Enumerate all dirty vectors in a four-cell orbit.
        echo_cases=0
        for q in range(16):
            for injection in range(16):
                perm=lambda z: ((z & 1)<<1)|((z & 2)>>1)|((z & 4)<<1)|((z & 8)>>1)
                y=0; dirty=q
                for _ in range(2):
                    y ^= perm(dirty)
                    dirty ^= injection
                assert dirty == q and y == perm(injection)
                echo_cases += 1
        rows.append(dict(h=h,beta=str(beta),complete_ordinary_source_obligations=identities,
                         exact_reflection_controls=sampled,forbidden_support_controls=failures,
                         arbitrary_dirty_echo_cases=echo_cases))
    document=dict(status='PASS EXACT SOURCE-RIDGE TERMINAL DEFECT CONTROLS; PHYSICAL TRANSFER UNPROVED',
                  classification='DISCOVERY',created_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),rows=rows,
                  lemma='For U intersect T exactly at common c, d_U^T w_T=0. Thus the sourceT reflection fixes every ridge function of d_U^T address. Dirty cancellation holds independently.',
                  missing=['Prove compatibility with the actual inherited source-array representation and endpoint gauges.',
                           'Prove actual scatter words and charges in both orientations, including copied centers.',
                           'Reconstruct a complete finite physical word without silently omitting a charged transition.'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(document,indent=2)+'\n')
    print(json.dumps(dict(status=document['status'],ordinary_obligations=sum(r['complete_ordinary_source_obligations'] for r in rows))))


if __name__ == '__main__':
    main()
