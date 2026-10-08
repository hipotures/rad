#!/usr/bin/env python3
"""Bind complete pair coverage, lexical indices, fixture and exact histograms."""
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import argparse,json,struct


def audit(classification,fixture,histogram):
    document=json.loads(classification.read_text());result=json.loads(histogram.read_text())
    assert sha256(classification.read_bytes()).hexdigest()==result['classification']['sha256']
    assert sha256(fixture.read_bytes()).hexdigest()==result['exception_fixture_sha256']
    left={t:i for i,t in enumerate(combinations(range(23),3))}
    right={t:i for i,t in enumerate(combinations(range(25),3))}
    N=len(left)*len(right);assert N==4073300==document['pairs']==result['actual_pairs']
    failures=document['failures'];count=len(failures)
    assert count==192596==document['unresolved_failures']==result['exception_pairs']
    assert sum(document['successful_pairs_by_prime'])+count==N
    assert document['nonzero_prefixes']==47*(N-count)
    assert document['ordered_zero_checks']==346*(N-count)
    data=fixture.read_bytes();assert struct.unpack_from('<I',data)[0]==count
    assert len(data)==4+10*count
    seen=set()
    for i,row in enumerate(failures):
        index=row['index'];L=tuple(row['left']);R=tuple(row['right'])
        assert index==left[L]*2300+right[R] and index not in seen
        seen.add(index);assert row['failed_step']==[27,19]
        assert row['witness_prime_for_earlier_prefixes']==1000000007
        assert struct.unpack_from('<I6B',data,4+10*i)==(index,*L,*R)
    profiles=Counter();covered=0
    for part in result['parts']:
        path=Path(part['path']);assert sha256(path.read_bytes()).hexdigest()==part['sha256']
        receipt=json.loads(path.read_text());assert receipt==part['record']
        assert receipt['checked_pairs']==48149 and receipt['field_replays']==1011129
        assert int(receipt['prime_product'])>int(receipt['minor_absolute_bound'])
        covered+=receipt['checked_pairs']
        for row in receipt['profiles']:
            assert sum(row['null_corner_runs'])==47
            assert row['representative_pair_index'] in seen
            profiles[tuple(row['null_corner_runs'])]+=row['count']
    assert covered==count==sum(profiles.values())
    actual=Counter({1:9*(N-count),17:N-count,21:N-count,481:N})
    for runs,frequency in profiles.items():
        for width in runs:actual[width]+=frequency
    assert dict(actual)=={int(w):n for w,n in result['one_data_front_histogram'].items()}
    assert {w:2*n for w,n in actual.items()}=={int(w):n for w,n in result['two_data_front_histogram'].items()}
    assert sum(w*n for w,n in actual.items())==528*N
    return dict(status='PASS COMPLETE SOURCE INDEX AND EXACT HISTOGRAM PROVENANCE',pairs=N,exceptions=count,
                distinct_source_indices=len(seen),exact_profile_classes=len(profiles),all_triple_indices_match_lexical_cartesian_product=True,
                binary_fixture_equals_complete_failure_list=True,successful_regular_plus_exception_coverage_exact=True,
                four_parts_cover_every_exception_once=True,all_child_frequencies_independently_reaggregated=True,
                input_sha256={str(p):sha256(p.read_bytes()).hexdigest() for p in (classification,fixture,histogram)},
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),completed_utc=datetime.now(timezone.utc).isoformat())


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--classification',type=Path,required=True)
    ap.add_argument('--fixture',type=Path,required=True);ap.add_argument('--histogram',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    result=audit(args.classification,args.fixture,args.histogram);assert not args.output.exists()
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
