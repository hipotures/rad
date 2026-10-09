#!/usr/bin/env python3
"""Target-level helper budgets for an explicitly hypothetical ballot ledger.

This is a complete finite moment discriminator, not a compiled physical
profile. One-helper-per-scalar-gate is a scoped comparison, not a lower
bound on arbitrary birth reuse or joint source/side chronology.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
from time import perf_counter

import characteristic


TARGET = Fraction(20, 189981)
CHARACTERISTIC_SHA = '9acd5ae4f916d902c1c9f904188b3fd38f8f87c4ea7e1276980ef86476f5b5f9'


def hypothetical_profile(h, k, roles, placement):
    r = (k - 1) // 2
    q, v, m = comb(h, r), comb(h, k), h*h
    N, W, loss = v*v, 2*v*v + 2*v*roles, 2*q*h
    children = Counter({m-h:2*v*roles, (h-1)**2:2*N, h-1:4*N, 1:N})
    if placement == 'rankh':
        children[h] += 2*v*(roles + 2*q)
    elif placement == 'rank1':
        children[1] += 2*v*(h*roles + loss)
    else:
        raise ValueError('Unknown local residual placement')
    children = {t:n for t,n in sorted(children.items()) if n}
    total = sum(t*n for t,n in children.items())
    if total != W*m - N + 2*v*loss:
        raise AssertionError('Complete hypothetical rank ledger failed')
    return dict(m=m, W=W, N=N, h=h, k=k, q=q, v=v, roles=roles,
                placement=placement, loss_replacing_previous_cost=loss,
                total_rank=total, deficit=N-2*v*loss,
                child_multiplicities=children)


def ballot_incidence_count(h, k, r):
    # The size-j ballot family has C(h,j)-C(h,j-1) rows; every such
    # feature occurs in exactly C(h-j,k-j) source labels.
    return sum((comb(h,j) - (comb(h,j-1) if j else 0))*comb(h-j,k-j)
               for j in range(r+1))


def incidence_control(h=10, k=7):
    r = (k-1)//2
    F = [s for j in range(r+1) for s in combinations(range(h),j)
         if all(x >= 2*i+1 for i,x in enumerate(s))]
    sources = list(map(set, combinations(range(h),k)))
    observed = sum(set(a) <= s for a in F for s in sources)
    expected = ballot_incidence_count(h,k,r)
    if observed != expected or len(F) != comb(h,r):
        raise AssertionError('Independent ballot incidence count failed')
    return dict(h=h,k=k,features=len(F),source_labels=len(sources),
                all_incidence_entries=len(F)*len(sources),nonzeros=observed)


def role_budget(h, k, placement):
    p0 = hypothetical_profile(h,k,0,placement)
    p1 = hypothetical_profile(h,k,1,placement)
    with localcontext() as context:
        context.prec = 70
        saving = Decimal(TARGET.numerator)/Decimal(TARGET.denominator)
        A0 = characteristic.decimal_moment(p0,saving)*Decimal(p0['W'])
        A1 = characteristic.decimal_moment(p1,saving)*Decimal(p1['W'])
        slope = A1-A0-Decimal(2*p0['v'])
        if slope <= 0:
            raise AssertionError('Role cost has a nonpositive target slope')
        crossing = (Decimal(p0['W'])-A0)/slope
        candidate = int(crossing)
    zero_interval = characteristic.moment_interval(p0,TARGET)
    if zero_interval[0] > 1:
        return dict(placement=placement,maximum_strict_integer_roles=None,
                    zero_role_target_moment=zero_interval,
                    scope='Even the zero-role hypothesis fails this target.')
    if candidate < 0:
        raise AssertionError('A positive zero-role margin has negative budget')
    low = hypothetical_profile(h,k,candidate,placement)
    high = hypothetical_profile(h,k,candidate+1,placement)
    low_interval = characteristic.moment_interval(low,TARGET)
    high_interval = characteristic.moment_interval(high,TARGET)
    if not low_interval[1] < 1 < high_interval[0]:
        raise AssertionError('Role threshold did not separate exactly')
    return dict(placement=placement,maximum_strict_integer_roles=candidate,
                maximum_roles_per_source=Fraction(candidate,p0['v']),
                accepted_role_target_moment=low_interval,
                next_role_target_moment=high_interval,
                target=TARGET,
                scope='Exact strict role threshold for this unattained full profile.')


def case(parameters):
    h,k = parameters
    r=(k-1)//2
    q,v=comb(h,r),comb(h,k)
    incidences=ballot_incidence_count(h,k,r)
    # All q pivot columns may account for at most q^2 incidences, a very
    # generous removal. The remaining literal nonpivot gather gates are
    # therefore at least this count, before every pivot word/sign gate.
    gather_lower=max(0,incidences-q*q)
    optimistic=hypothetical_profile(h,k,gather_lower,'rankh')
    gather_interval=characteristic.moment_interval(optimistic,TARGET)
    budgets=[role_budget(h,k,p) for p in ('rank1','rankh')]
    return dict(h=h,k=k,r=r,v=v,q=q,target=TARGET,
                all_ballot_feature_incidences=incidences,
                incidence_additions_per_source=Fraction(incidences,v),
                direct_nonpivot_gather_lower=gather_lower,
                gather_lower_per_source=Fraction(gather_lower,v),
                rankh_target_moment_at_gather_lower=gather_interval,
                direct_unreused_gate_helper_status=('excluded' if gather_interval[0]>1
                                                    else 'capacity remains'),
                budgets=budgets,
                assumptions=['The old two-axis master admits the stated odd-k profile',
                             'Closed center loss2qh replaces every previous center charge',
                             'All local residual widths are at most h; rankh is optimistic and rank1 conservative',
                             'For the direct-gather comparison only, every scalar gate consumes a distinct physical helper',
                             'No role-reuse, phase, routing, guard or source/sink saving is assumed implicitly'],
                scope='A sensitivity discriminator. A literal scalar gate count does not lower-bound helper stock in a different chronology.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--bounded',action='store_true')
    args=parser.parse_args()
    if not 1<=args.workers<=4:
        raise ValueError('Use one to four workers')
    helper=Path(characteristic.__file__)
    if sha256(helper.read_bytes()).hexdigest()!=CHARACTERISTIC_SHA:
        raise AssertionError('Pinned complete-moment arithmetic changed')
    source=Path(__file__)
    hashes={file.name:sha256(file.read_bytes()).hexdigest() for file in (source,helper)}
    started=datetime.now(timezone.utc).isoformat()
    cases=[(26,7)] if args.bounded else [(22,7),(26,7),(30,7),(36,7),(30,5),(48,3)]
    protocol=dict(started_utc=started,workers=args.workers,native_threads_each=1,
                  source_sha256=hashes,cases=cases,seeds=None,target=str(TARGET))
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    timer=perf_counter()
    control=incidence_control()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows=list(pool.map(case,cases))
    if any(sha256(file.read_bytes()).hexdigest()!=hashes[file.name] for file in (source,helper)):
        raise AssertionError('Effective source changed during the role-budget attempt')
    certificate=characteristic.serializable(dict(status='PASS EXACT HYPOTHETICAL ROLE BUDGETS',
                 protocol=protocol,completed_utc=datetime.now(timezone.utc).isoformat(),
                 elapsed_seconds=perf_counter()-timer,incidence_control=control,cases=rows,
                 scope='No native circuit or exponent is certified. The direct-gather exclusion applies only to one-helper-per-gate stock in the unchanged hypothetical master.'))
    if args.output:
        (args.output/'certificate.json').write_text(json.dumps(certificate,indent=2)+'\n')
    print(json.dumps(certificate,indent=2),flush=True)


if __name__=='__main__':
    main()
