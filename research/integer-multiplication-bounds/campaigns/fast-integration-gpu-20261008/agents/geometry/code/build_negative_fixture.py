#!/usr/bin/env python3
"""Recover the exact exception fixture from complete source-pair classification."""
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import argparse,json,struct


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--classification',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert not args.output.exists();r=json.loads(args.classification.read_text())
    left={t:i for i,t in enumerate(combinations(range(23),3))}
    right={t:i for i,t in enumerate(combinations(range(25),3))}
    failures=r['failures'];assert len(failures)==r['unresolved_failures']==192596
    assert sum(r['successful_pairs_by_prime'])+len(failures)==r['pairs']==4073300
    seen=set()
    with args.output.open('wb') as out:
        out.write(struct.pack('<I',len(failures)))
        for row in failures:
            index=row['index'];L=tuple(row['left']);R=tuple(row['right'])
            assert index==left[L]*2300+right[R] and index not in seen
            seen.add(index);out.write(struct.pack('<I6B',index,*L,*R))
    print(json.dumps(dict(pairs=len(seen),source_sha256=sha256(args.classification.read_bytes()).hexdigest(),
                          fixture_sha256=sha256(args.output.read_bytes()).hexdigest())))
