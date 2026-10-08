#!/usr/bin/env python3
"""Independent source-delta and exact dirty-completion discriminators."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

OLD="   for i in range(len(ins)):\n    if independent(echelon,1<<i):rows.append(1<<i);labels.append(('retire',i));echelon=basis(rows)"
NEW="   for i,r in enumerate(future_candidates(b,g,blocks,uses,value_uses,order,contains,signal)):\n    if independent(echelon,r):rows.append(r);labels.append(('retire',i));echelon=basis(rows)"

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def rank(rows):
    pivots={}
    for value in rows:
        while value:
            p=value.bit_length()-1
            if p not in pivots:pivots[p]=value;break
            value^=pivots[p]
    return len(pivots)

def inverse(rows):
    n=len(rows); augmented=[v|(1<<(n+i)) for i,v in enumerate(rows)]
    for bit in range(n):
        pivot=next(i for i in range(bit,n) if augmented[i]>>bit&1)
        augmented[bit],augmented[pivot]=augmented[pivot],augmented[bit]
        for j in range(n):
            if j!=bit and augmented[j]>>bit&1:augmented[j]^=augmented[bit]
    assert [v&((1<<n)-1) for v in augmented]==[1<<i for i in range(n)]
    return [v>>n for v in augmented]

def synthesize(rows):
    n=len(rows); work=rows.copy(); word=[]; swaps=0
    for i in range(n):
        j=next(j for j in range(i,n) if work[j]>>i&1)
        if i!=j:
            swaps+=1
            for a,b in [(i,j),(j,i),(i,j)]:work[a]^=work[b];word.append((a,b))
        for j in range(n):
            if i!=j and work[j]>>i&1:work[j]^=work[i];word.append((j,i))
    assert work==[1<<i for i in range(n)]
    return list(reversed(word)),swaps

def execute(word,n,dual=False):
    columns=[1<<i for i in range(n)]
    for a,b in reversed(word) if dual else word:
        if dual:a,b=b,a
        columns[a]^=columns[b]
    return columns

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--sum-base',type=Path,required=True)
    ap.add_argument('--sum-variant',type=Path,required=True)
    ap.add_argument('--pair-base',type=Path,required=True)
    ap.add_argument('--pair-variant',type=Path,required=True)
    ap.add_argument('--helper',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert __debug__ and not args.output.exists()
    audit=[]
    for base,variant in [(args.sum_base,args.sum_variant),(args.pair_base,args.pair_variant)]:
        before,after=base.read_text(),variant.read_text()
        assert before.count(OLD)==1 and after.count(NEW)==1
        assert after.replace(NEW,OLD)==before
        acquire_before=before.split(' def acquire(g,anchors):',1)[1].split(' for step,g in enumerate(order):',1)[0]
        acquire_after=after.split(' def acquire(g,anchors):',1)[1].split(' for step,g in enumerate(order):',1)[0]
        assert acquire_before==acquire_after
        audit.append(dict(base=str(base),base_sha256=digest(base),variant=str(variant),variant_sha256=digest(variant),sole_change='unused complement row enumeration',complete_acquire_body_unchanged=True,acquire_body_sha256=hashlib.sha256(acquire_after.encode()).hexdigest()))
    pair=args.pair_variant.read_text()
    assert 'if terminal is None and place[target]<=step:continue' in pair
    assert 'if not all(contains(blocks[g][\'frame\'],blocks[target][\'frame\']) for target in targets):continue' in pair
    assert 'if s in retired or s in anchors:continue' in pair
    assert 'xor(s,a,g)' in pair
    helper=args.helper.read_text()
    assert 'return answer+[1<<i for i in range(len(b[\'inputs\']))]' in helper
    assert 'row=sum(1<<i for i in set(by_target[target]))' in helper
    assert '(1<<i)^(1<<j)' in helper
    fixtures=[]
    # Desired and carry rows are fixed. The non-unit complement has a genuine
    # arbitrary dirty component; it is never treated as an initialized zero.
    for n in range(3,9):
        desired=[3]; carry=[2]; candidate=5
        selected=desired+carry
        assert rank(selected+[3])==rank(selected), 'dependent future row must be rejected'
        assert rank(selected+[candidate])==rank(selected)+1
        selected.append(candidate)
        for i in range(n):
            row=1<<i
            if rank(selected+[row])>rank(selected):selected.append(row)
        assert len(selected)==rank(selected)==n
        matrix=selected; mix,swaps=synthesize(matrix)
        columns=execute(mix,n);assert columns==matrix
        inv=inverse(matrix);r=2
        M=[(2*r+a,2*r+b) for a,b in mix]
        J=[(r+i,2*r+j) for i in range(r) for j in range(n) if inv[i]>>j&1]
        V=[(2*r+i,i) for i in range(r)]
        full=M+J+list(reversed(M))+V+M+J+list(reversed(M))+V
        count=2*r+n; initial=[1<<i for i in range(count)]
        expect=initial.copy()
        for i in range(r):expect[r+i]^=initial[i]
        assert execute(full,count)==expect
        opposite=initial.copy()
        for i in range(r):opposite[i]^=initial[r+i]
        assert execute(full,count,True)==opposite
        bad=execute(full[1:],count)
        witnesses=[i for i in range(count) if bad[i]!=expect[i]]
        assert witnesses, 'unpaid basis XOR must have a counterexample'
        singular=desired+carry+[1]+[1<<i for i in range(3,n)]
        assert len(singular)==n and rank(singular)==n-1
        fixtures.append(dict(n=n,rows=matrix,required_rows=desired,carry_rows=carry,independent_nonunit_complement=candidate,mixer_xors=len(mix),paid_three_xor_swaps=swaps,wrapped_xors=len(full),dirty_basis_columns=count,both_orientations_exact=True,negative_dependent_complement_rank=rank(singular),negative_omitted_paid_mixer_xor_witnesses=witnesses))
    result=dict(status='PASS_INDEPENDENT_COMPLEMENT_SOURCE_AND_DIRTY_CONTROLS',recorded_utc=datetime.now(timezone.utc).isoformat(),source_audit=audit,helper=dict(path=str(args.helper),sha256=digest(args.helper)),fixtures=fixtures,all_terminal_and_unconsumed_ordinary_guards_retained=True,live_anchor_is_readonly_source=True,source_sha256=digest(Path(__file__)),scope='Source equivalence and exact small F2 counterexamples. Full candidate word/frame/profile/moment and all-size tape contracts are separate independently reviewed evidence.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],fixtures=len(fixtures),scalar_and_dirty_basis_columns=sum(x['dirty_basis_columns'] for x in fixtures),actual_variants_only_complement_patch=True)))

if __name__=='__main__':main()
