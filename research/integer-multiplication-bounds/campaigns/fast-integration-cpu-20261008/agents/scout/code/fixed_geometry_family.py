#!/usr/bin/env python3
"""Complete actual fixed-I+J data geometry for reversed (h,h+2) families.

Eligible source: pinned PR40, incorporating James Chang's parameterized PR34
permutations/incidence cuts and icekylinx/rohanarun's complete finite modular
nonvanishing verifier. Original Apache-2.0 notices remain in the dependency.
This wrapper changes dimensions, exact denominators and complete run checks.
It never replaces incidence-cut zero proofs with modular observations.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import types


PIN='43f59ff533598762cbc43a5e14af2bbbc76fabbd'
INPUTS=['research/copied-reversed/pr34/independent_controls.py',
        'research/copied-both-reversed/geometry.cpp']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def controls(source,h):
    # Omit only the historical host's resource setters, preserving all math.
    path=source/INPUTS[0]
    body='\n'.join(s for s in path.read_text().splitlines() if not s.startswith('resource.setrlimit('))
    mod=types.ModuleType('pinned_parameterized_geometry');mod.__file__=str(path)
    exec(compile(body,str(path),'exec'),mod.__dict__)
    a,b=h,h+2;m=a*b;d=a+b-1
    rows,cols=mod.corner_labels(h)
    pivots=mod.expected_pivots(h)
    perms=mod.completion(h,rows,cols)
    cuts=mod.check_cuts(h,rows,cols,pivots)
    assert sorted(pivots)==list(range(d))
    def tree(edges):
        parents=list(range(a+b))
        def find(i):
            while parents[i]!=i:i=parents[i]
            return i
        for left,right in edges:
            u,v=find(left),find(a+right)
            assert u!=v
            parents[u]=v
        assert len(edges)==a+b-1 and len({find(i) for i in range(a+b)})==1
    tree(rows);tree(cols)
    for i in range(a):
        for j in range(a):
            assert (perms[i%b][i//b],perms[(m-a+j)%b][(m-a+j)//b],i%b,(m-a+j)%b)==(i,j,i,j+2)
    r=[perms[i%b][i//b] for i in range(b)]
    c=[perms[(m-b+j)%b][(m-b+j)//b] for j in range(b)]
    assert r==list(range(a))+[a-1,0] and c==[a-1,0]+list(range(a))
    line,centers={},[]
    for n in (a,b):
        inside=Q(6*n-14,3*(n+1));outside=-Q(5,n+1)
        assert inside and outside and 3*inside+(n-3)*outside==1
        line[str(n)]=dict(inside=str(inside),outside=str(outside),
                         all_actual_primal_dual_coordinates_nonzero=True)
        for center in range(n):
            p=[Q(j==center)+Q(2,n-9) for j in range(n)]
            xi=[Q(n-9,12)*(1-3*Q(j==center)) for j in range(n)]
            assert sum(x*y for x,y in zip(p,xi))==1
            assert [x-sum(p)/9 for x in p]==[Q(j==center)-Q(1,3) for j in range(n)]
            v=[x+sum(p) for x in p];nu=[x-sum(xi)/(n+1) for x in xi]
            assert all(v) and all(nu) and sum(x*y for x,y in zip(v,nu))==1
            # First extreme pivot of I-v*nu is nonzero; its central Schur
            # block is identity and the final residue vanishes by nu*v=1.
            pivot=-v[0]*nu[-1]
            assert pivot
            for i in range(1,n-1):
                for j in range(1,n-1):
                    mij=Q(i==j)-v[i]*nu[j]
                    assert mij-(-v[i]*nu[-1])*(-v[0]*nu[j])/pivot==Q(i==j)
            final=(1-sum(x*y for x,y in zip(v,nu)))/(v[0]*nu[-1])
            assert final==0
            centers.append(dict(h=n,center=center,primal=[str(x) for x in v],dual=[str(x) for x in nu],
                                copied_front_rank=1,growth_profile=[1,n-2],
                                growth_extreme_pivot=str(pivot),central_identity=True,last_residue_zero=True))
    runs=[]
    for i,j in enumerate(pivots):
        if i and j==pivots[i-1]+1:runs[-1]+=1
        else:runs.append(1)
    assert sorted(runs)==sorted([1]*9+[h-2,h-6])
    profile=[1]*9+[h-2,h-6,m-2*d]
    assert sum(profile)==m-d and max(profile)<m
    zero_checks=sum(sum(j>p and j not in pivots[:i] for j in range(d)) for i,p in enumerate(pivots))
    assert zero_checks==(h-2)*(h-3)//2+(h-6)*(h-7)//2
    return dict(dimensions=[a,b],m=m,d=d,rank=m-d,data_profile=profile,
                row_edges=rows,column_edges=cols,permutation_completions=perms,
                prescribed_pivots=pivots,incidence_cut_certificates=cuts,
                both_boundary_trees=True,universal_zero_identities='Exact integer incidence-rank cuts; arbitrary diagonal weights',
                all_actual_local_and_auxiliary_index_identities=True,
                source_line_weights=line,copied_centers=centers,
                expected_zero_checks_per_pair=zero_checks)


def generated(source,h):
    original=(source/INPUTS[1]).read_text()
    old='constexpr int a=23,b=25,d=a+b-1;'
    assert original.count(old)==1
    text=original.replace(old,'constexpr int a=%d,b=%d,d=a+b-1;'%(h,h+2))
    text=text.replace('for(int den:{18,24,39,26,31,5,68})',
                      'for(int den:{3*(a+1),2*(3*(a+1)-10),a+1,5,3*(b+1),2*(3*(b+1)-10),b+1})')
    old='if(count!=1771*2300||prefixes!=int64_t(count)*d||zeros!=int64_t(count)*346)return 12;'
    assert text.count(old)==1
    text=text.replace(old,'const int per_pair=(a-2)*(a-3)/2+(a-6)*(a-7)/2;\n if(count!=int(left.size()*right.size())||prefixes!=int64_t(count)*d||zeros!=int64_t(count)*per_pair)return 12;')
    lines=text.splitlines()
    candidates=[i for i,line in enumerate(lines) if line.startswith(' cout<<"{\\"status')]
    assert len(candidates)==1
    lines[candidates[0]]=r''' cout<<"{\"status\":\"COMPLETE ACTUAL-PAIR NONVANISHING CERTIFICATE\",\"dimensions\":["<<a<<","<<b<<"],\"primes\":[1000003,2147483647,1000000007],\"primality_trial_division\":true,\"admissibility_factors\":["<<3*(a+1)<<","<<2*(3*(a+1)-10)<<","<<a+1<<",5,"<<3*(b+1)<<","<<2*(3*(b+1)-10)<<","<<b+1<<"],\"left_triples\":"<<left.size()<<",\"right_triples\":"<<right.size()<<",\"pairs\":"<<count<<",\"nonzero_prefixes\":"<<prefixes<<",\"ordered_zero_checks\":"<<zeros<<",\"unresolved_failures\":0,\"primary_modular_failures\":"<<fallbacks.size()<<",\"successful_pairs_by_prime\":["<<success[0]<<","<<success[1]<<","<<success[2]<<"],\"fallbacks\":[";'''
    return '\n'.join(lines)+'\n'


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root',required=True,type=Path)
    ap.add_argument('--dimensions',nargs='+',type=int,default=[8,10,24,26])
    ap.add_argument('--compiler',default=os.environ.get('CXX','c++'))
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    assert __debug__ and all(h>=8 and h not in (9,) and h+2!=9 for h in args.dimensions)
    args.output.mkdir(parents=True,exist_ok=False)
    protocol=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),pid=os.getpid(),dependency_pin=PIN,
                  dependency_repository='https://github.com/rohanarun/integer-mult-bounds',
                  source_sha256={p:sha(args.source_root/p) for p in INPUTS},
                  wrapper_sha256=sha(Path(__file__)),dimensions=args.dimensions,threads=1,
                  scope='Complete finite fixed-I+J data and corner geometry, separate from producer profiles and tape compiler')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    summaries=[]
    for h in args.dimensions:
        run=args.output/('h%d-h%d'%(h,h+2));run.mkdir()
        analytic=controls(args.source_root,h)
        (run/'controls.json').write_text(json.dumps(analytic,indent=2)+'\n')
        cpp,binary=run/'geometry.cpp',run/'geometry'
        cpp.write_text(generated(args.source_root,h))
        cmd=[args.compiler,'-O3','-std=c++17','-Wall','-Wextra',str(cpp),'-o',str(binary)]
        with (run/'compile.log').open('w') as log:
            subprocess.run(cmd,check=True,stdout=log,stderr=log)
        receipt=dict(source_sha256=sha(cpp),binary_sha256=sha(binary),compile_command=cmd,
                     began_utc=datetime.now(timezone.utc).isoformat())
        (run/'protocol.json').write_text(json.dumps(receipt,indent=2)+'\n')
        with (run/'nonvanishing.json').open('w') as out,(run/'nonvanishing.log').open('w') as log:
            result=subprocess.run([str(binary.resolve())],stdout=out,stderr=log)
        receipt.update(exit_code=result.returncode,completed_utc=datetime.now(timezone.utc).isoformat())
        if result.returncode==0:
            actual=json.loads((run/'nonvanishing.json').read_text())
            assert actual['dimensions']==[h,h+2] and actual['unresolved_failures']==0
            assert actual['nonzero_prefixes']==actual['pairs']*analytic['d']
            assert actual['ordered_zero_checks']==actual['pairs']*analytic['expected_zero_checks_per_pair']
            receipt.update(status='complete_actual_fixed_geometry_pass',pairs=actual['pairs'],
                           prefixes=actual['nonzero_prefixes'],primary_modular_failures=actual['primary_modular_failures'],
                           data_profile=analytic['data_profile'])
        else:
            receipt.update(status='actual_fixed_geometry_unresolved_failure',error_log_sha256=sha(run/'nonvanishing.log'))
        (run/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        summaries.append(dict(run=str(run),**receipt))
        (args.output/'progress.json').write_text(json.dumps(dict(completed=len(summaries),rows=summaries),indent=2)+'\n')
        print(json.dumps(receipt),flush=True)
    (args.output/'summary.json').write_text(json.dumps(dict(status='completed_parameterized_fixed_geometry_family',rows=summaries),indent=2)+'\n')


if __name__=='__main__':
    main()
