#!/usr/bin/env python3
"""Literal irregular-routing controls for all four width remainders.

Instrumentation counts actual nonzero eight-rotation masks whose finite guard
predicate does or does not require repair. It is not a fixed-tape timing model.
The frozen component's implementation is called unchanged after counting.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time

import irregular_activity_router as I


def measured_probe(task):
    counts=dict(nonzero_uncorrected=0,nonzero_repaired=0,zero_masks=0)
    original=I.w.packed_xor
    def measured(mask,target,companion,width,K,omit_repair=False):
        if not omit_repair:
            if mask:
                raw=I.w.rotations(mask,target,companion,width,K)
                key='nonzero_repaired' if I.w.exceptional(*raw,width,K) else 'nonzero_uncorrected'
                counts[key]+=1
            else:
                counts['zero_masks']+=1
        return original(mask,target,companion,width,K,omit_repair)
    I.w.packed_xor=measured
    try:
        row=I.probe(task)
    finally:
        I.w.packed_xor=original
    I.require(counts['nonzero_uncorrected']>0 and counts['nonzero_repaired']>0,
              'Each tested width remainder must exercise nonzero repaired and uncorrected literal words')
    row['actual_literal_branch_counts']=counts
    row['branch_count_scope']='Extra oracle calls classify the same complete actual inputs; no producer/source mutation or tape-time claim'
    return row


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--bounded',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    I.require(args.workers>0,'A positive worker count is required')
    files=(Path(__file__).resolve(),Path(I.__file__).resolve(),I.WORD,I.BASE)
    closure={str(p.relative_to(I.TOPIC)):sha256(p.read_bytes()).hexdigest() for p in files}
    tasks=((7,10,20261009178),) if args.bounded else tuple((f,10,20261009175+i) for i,f in enumerate((4,5,6,7)))
    started=datetime.now(timezone.utc).isoformat()
    tick=time.monotonic()
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(dict(started_utc=started,source_closure=closure,
            tasks=tasks,workers=args.workers,instrumentation='Count exact finite guard branches before unchanged packed component',
            scope='Exact finite address composition for all width remainder classes; native time and recursive endpoint unsupplied'),indent=2)+'\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows=list(pool.map(measured_probe,tasks))
    I.require(closure=={str(p.relative_to(I.TOPIC)):sha256(p.read_bytes()).hexdigest() for p in files},
              'All effective input sources must remain unchanged')
    result=dict(status='PASS IRREGULAR ROUTE SHAPES AND LITERAL GUARD BRANCHES',cases=rows,
        tested_width_remainders=[row['f']%4 for row in rows],full_address_samples=sum(row['full_address_samples'] for row in rows),
        nonzero_uncorrected=sum(row['actual_literal_branch_counts']['nonzero_uncorrected'] for row in rows),
        nonzero_repaired=sum(row['actual_literal_branch_counts']['nonzero_repaired'] for row in rows),
        elapsed_seconds=time.monotonic()-tick,native_or_exponent=False)
    if args.output:
        (args.output/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:value for key,value in result.items() if key!='cases'},sort_keys=True))


if __name__=='__main__':
    main()
