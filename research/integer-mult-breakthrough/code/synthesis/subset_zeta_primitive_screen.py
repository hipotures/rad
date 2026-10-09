#!/usr/bin/env python3
"""Exact subset-zeta transfer and axis-subset center-release preflight.

An independently faster native zeta supplier could transfer to C; none is
supplied here. The involutive signed-zeta axis-subset ansatz is rejected
before a circuit sweep by a point-star fitting-rank obstruction.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import time

import weighted_scan_intertwiners as arithmetic


ARITHMETIC_SHA='0e6e1e3af2da37a0ada5eb599ec568f7125479dd88717148335a7c484f4e12ac'


def unit(power): return ((1,0),(0,1),(-1,0),(0,-1))[power%4]


def signed_zeta(records,mask,inverse=False):
    if inverse: pass  # Every signed one-axis factor is its own inverse.
    out=list(records);e=len(out).bit_length()-1
    for bit in range(e):
        v=1<<bit
        if not mask&v: continue
        for a in range(len(out)):
            if not a&v: out[a|v]=tuple(x-y for x,y in zip(out[a],out[a|v]))
    return out


def probe(task):
    h,k=task;started=time.monotonic();D=1<<h;labels=[sum(1<<j for j in T) for T in combinations(range(h),k)]
    v=len(labels);full=D-1
    if sha256(Path(arithmetic.__file__).read_bytes()).hexdigest()!=ARITHMETIC_SHA:
        raise AssertionError('pinned exact rank source changed')
    # Z diag((-2)^wt) Z^T has entry sum_{a subset i&j}(-2)^wt(a).
    # Compute all terms independently, then bind the exact C normalization.
    numerators=arithmetic.F_numerators(h);alpha=(1,0)
    for _ in range(h): alpha=arithmetic.multiply(alpha,(1,1))
    comparisons=0;wrong_diagonal_reject=False
    for i in range(D):
        for j in range(D):
            common=i&j;sum_value=0;plain=0;a=common
            while True:
                sum_value+=(-2)**a.bit_count();plain+=1
                if a==0: break
                a=(a-1)&common
            expected=-1 if common.bit_count()%2 else 1
            if sum_value!=expected: raise AssertionError('subset-zeta factorization does not equal Hadamard')
            actual=arithmetic.multiply(alpha,unit(-i.bit_count()-j.bit_count()))
            actual=tuple(expected*x for x in actual)
            if actual!=numerators[i][j]: raise AssertionError('C chirps/global dyadic normalization differ from literal C')
            wrong_diagonal_reject|=plain!=expected;comparisons+=1
    if not wrong_diagonal_reject: raise AssertionError('omitting the middle weighted diagonal did not discriminate')
    origins=[[tuple(1 if i==j else 0 for _ in range(2)) for i in range(D)] for j in range(D)]
    origins.append([(a-3,2*a+1) for a in range(D)])
    anchor_comparisons=0
    for S in labels:
        for raw in origins:
            source=signed_zeta(raw,S)
            if signed_zeta(source,S)!=raw: raise AssertionError('signed zeta source anchor is not an involution')
            sink=signed_zeta(signed_zeta(raw,full),S)
            if sink!=signed_zeta(raw,full^S): raise AssertionError('full/signed-source ratio is not the complement primitive')
            # Virtual signed swap under (T_S,I) -> (T_full,T_complement)
            # gives raw (T_full*y,-T_full*x), with no line adapter.
            returned=signed_zeta(source,full^S)
            if returned!=signed_zeta(raw,full): raise AssertionError('physical signed swap leaves an omitted source boundary')
            anchor_comparisons+=6*D
    K=[[(int(S==T)+(1 if k%2 else -1)*int(not(S&T)),0) for S in labels] for T in labels]
    if any(K[i][i]!=(1,0) for i in range(v)): raise AssertionError('central fitting diagonal is not one')
    if any(K[i][j]!=(0,0) for i,T in enumerate(labels) for j,S in enumerate(labels) if i!=j and S&T):
        raise AssertionError('central fitting matrix has a forbidden intersecting off-diagonal')
    point_stars=[[i for i,S in enumerate(labels) if S>>point&1] for point in range(h)]
    for star in point_stars:
        if any(K[i][j]!=((1,0) if i==j else (0,0)) for i in star for j in star):
            raise AssertionError('point-star exact identity minor failed')
    exact_rank=arithmetic.rank(K);lower=max(map(len,point_stars));source_saving=2*k*v
    if lower!=comb(h-1,k-1) or lower*h!=k*v:
        raise AssertionError('point-star incidence double count is not exact')
    if exact_rank<lower: raise AssertionError('finite K rank is below its retained identity minor')
    optimistic_center_loss=2*exact_rank*h
    if optimistic_center_loss<source_saving: raise AssertionError('axis-subset closed-center release crosses its proven first-moment limit')
    # Subset-zeta inverse is diag(sign) Z diag(sign), not raw Z itself.
    ordinary_Z_square=[sum(1 for a in range(D) if (j&~a)==0 and (a&~i)==0) for i in range(D) for j in range(D)]
    if all(value==int(i==j) for (i,j),value in zip(((i,j) for i in range(D) for j in range(D)),ordinary_Z_square)):
        raise AssertionError('ordinary zeta was incorrectly treated as an involution')
    return dict(status='PASS EXACT SUBSET ZETA PRIMITIVE SCREEN',active_dimension=h,subset_weight=k,address_dimension=D,
                C_factorization_entries_compared=comparisons,C_normalization_grid_bits=h,
                C_factorization='D_i^-1 alpha^h Z_h diag((-2)^wt) Z_h^T D_i^-1',
                signed_zeta_involution=True,all_source_and_complement_anchors_verified=v,
                literal_anchor_component_comparisons=anchor_comparisons,
                labels=labels,fitting_matrix_sha256=arithmetic.digest(K),exact_candidate_fitting_rank=exact_rank,
                point_star_identity_minor_sizes=[len(star) for star in point_stars],fitting_rank_lower=lower,
                source_endpoint_saving=source_saving,minimum_closed_center_loss=2*lower*h,
                candidate_closed_center_loss=optimistic_center_loss,candidate_deficit=source_saving-optimistic_center_loss,
                all_size_portfolio_obstruction='For any distinct nonempty coordinate-subset labels, rankK>=max_i incidence_i >= sum_S |S|/h; closed full-center loss2h rankK >= endpoint saving2 sum_S |S|.',
                negative_controls={'omitted_weighted_diagonal':'REJECTED','ordinary_Z_involution':'REJECTED'},
                native_Z_supplier_supplied=False,whole_bulk_word_compiled=False,
                scope='Exact C/Z transfer algebra and signed-zeta anchor operators. Rank obstruction is conditional on coordinate-subset geodesic side and closed full-width center release; general Z suppliers/noncommuting frames/dynamic releases remain open.',
                seconds=time.monotonic()-started)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),Path(arithmetic.__file__)];hashes={p.name:sha256(p.read_bytes()).hexdigest() for p in sources}
    tasks=[(4,2),(5,2),(6,3),(7,3)]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,tasks=tasks,
                  source_sha256=hashes,stdlib_only=True,
                  hypothesis='A directional nonunit subset-zeta primitive has exact C transfer and involutive signed anchors; screen closed-center capacity before investing in native synthesis.',
                  resource_preflight=dict(maximum_address_dimension=128,maximum_subset_labels=35,
                                          expected_aggregate_memory_bytes_upper=128*1024*1024))
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(probe,task):task for task in tasks}
        for future in as_completed(futures):
            result=future.result();results.append(result)
            print(json.dumps({k:result[k] for k in ('status','active_dimension','subset_weight','exact_candidate_fitting_rank','fitting_rank_lower','candidate_deficit','seconds')}),flush=True)
    if any(sha256(p.read_bytes()).hexdigest()!=hashes[p.name] for p in sources): raise AssertionError('effective source changed during zeta preflight')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results),indent=2)+'\n')


if __name__=='__main__': main()
