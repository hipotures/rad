#!/usr/bin/env python3
"""Source-only coherent coordinate permutation of an executed joint word.

Input and target physical bank locations and every XOR remain unchanged.
Their full triple labels, all address masks and all endpoint labels are
permuted by one common Q. This binds the actual source family bijection;
Q commutes with I-betaJ and the full triple-pair data family is invariant.
The source compiler is pinned PR62/PR57 with original E(C,M) frames.
"""
import argparse
from datetime import datetime,timezone
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time
import joint_region_search_v3 as region
from joint_word_check_v4 import check


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--h',type=int,required=True);p.add_argument('--order',nargs='+',type=int,required=True);p.add_argument('--profile-transitions',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--region-policy',default='baseline');p.add_argument('--region-limit',type=int,default=0);p.add_argument('--rank-delta',type=int,default=1);p.add_argument('--expected-source-word-sha256')
    a=p.parse_args();assert sorted(a.order)==list(range(a.h));assert not a.work.exists();a.work.mkdir(parents=True);start=time.monotonic();region.initialize(a.source,a.work)
    config=dict(h=a.h,policy=a.region_policy,rank_delta=a.rank_delta,sweeps=1,limit=a.region_limit);region.COMPILER.build=lambda h:region.build_regions(h,config)
    compiled,word=region.COMPILER.compile_(a.h,matching=True,reclaim=True,dirty=True)
    original_raw=(json.dumps(word,separators=(',',':'))+'\n').encode();reference=a.source/f'research/pair-assembly/frame/frame-word-{a.h}.json.gz'
    expected=a.expected_source_word_sha256 or sha256(gzip.decompress(reference.read_bytes())).hexdigest()
    assert sha256(original_raw).hexdigest()==expected,'Source-only regenerated parent word differs from selected exact parent'
    scalar=region.graph(a.h).verify()
    def mask(old):return sum(1<<a.order[i]for i in range(a.h)if old>>i&1)
    word['frames']=[(mask(c),mask(m))for c,m in word['frames']]
    word['outputs']=[(s,g,a.order[c],tuple(sorted(a.order[i]for i in t)))for s,g,c,t in word['outputs']]
    triples=list(combinations(range(a.h),3));lookup={t:i for i,t in enumerate(triples)};labels=[lookup[tuple(sorted(a.order[i]for i in t))]for t in triples];inverse=[0]*len(labels)
    for i,j in enumerate(labels):inverse[j]=i
    word.update(source_permutation=a.order,source_label_permutation=labels,source_label_inverse=inverse)
    raw=(json.dumps(word,separators=(',',':'))+'\n').encode();path=a.work/'word.json.gz'
    with path.open('wb')as stream:
        with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0)as out:out.write(raw)
    audit=check(path,a.work/'transitions.bin')
    if a.profile_transitions:
        assert(a.work/'transitions.bin').read_bytes()==a.profile_transitions.read_bytes(),'Profile packed executed-word transition bytes differ'
    result=dict(status='fresh source-only word regeneration, coherent Q source/output/address and complete both-dirty PASS',configuration=config,source_head='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',source_permutation=a.order,source_label_permutation=labels,source_label_inverse=inverse,source_word_sha256=sha256(original_raw).hexdigest(),word_path=str(path),word_sha256=sha256(raw).hexdigest(),compiled=compiled,scalar=scalar,independent=audit,profile_transition_path=str(a.profile_transitions)if a.profile_transitions else None,seconds=time.monotonic()-start,completed_utc=datetime.now(timezone.utc).isoformat(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),limitations='Finite full dirty/address/word and coherent data bijection. Matrix CRT, infinite-dimensional dirty lifting and complete recurrence closure are separately reviewed.')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(status=result['status'],h=a.h,R=compiled['roles'],seconds=result['seconds'])),flush=True)


if __name__=='__main__':main()
