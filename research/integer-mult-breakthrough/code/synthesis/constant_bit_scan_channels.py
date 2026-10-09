#!/usr/bin/env python3
"""Two scan orders separated by one specified-bit gate, finite control only.

This lifts the growing-f word count of full bit reversal/Gray routing. A
single-bit swap/CNOT still has a paid native contract, and no fast inverse
or complete physical supplier is supplied by the channel-space screen.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time

import two_order_scan_channels as engine


ENGINE_SHA='1fa8acee9498c536cab6c671dfe0327401d64b28f376db4af6c67cb80ab1f71d'
ORIGINAL_ORDER=engine.order_table


def order_table(f,kind):
    D=1<<f;last=1<<(f-1)
    if kind=='end_swap':
        table=[a^((1|last) if ((a&1)!=((a>>(f-1))&1)) else 0) for a in range(D)]
    elif kind=='end_cnot': table=[a^(last if a&1 else 0) for a in range(D)]
    else: return ORIGINAL_ORDER(f,kind)
    if sorted(table)!=list(range(D)): raise AssertionError('specified-bit order is not a bijection')
    return table


def probe(task):
    if sha256(Path(engine.__file__).read_bytes()).hexdigest()!=ENGINE_SHA:
        raise AssertionError('pinned two-order exact engine changed')
    # Only the explicit address map is changed, on a process-local module.
    # All exact class, nullspace, inverse-unit and complete-stack checks remain.
    engine.order_table=order_table
    result=engine.probe(task);f,kind=task
    result['constant_specified_bit_gate']=dict(kind=kind,bit_positions=[0,f-1],gate_count=1,
                                              arbitrary_growing_f_order_not_assumed=True)
    result['status']='PASS EXACT CONSTANT-BIT TWO-SCAN CHANNEL SCREEN'
    result['native_scope']='One specified-bit route has a separate elementary stream obligation; whole scan weighting/layout and inverse/source completion are still unsupplied.'
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),Path(engine.__file__),Path(engine.s.__file__)]
    hashes={p.name:sha256(p.read_bytes()).hexdigest() for p in sources}
    tasks=[(f,kind) for f in (3,4) for kind in ('end_swap','end_cnot')]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,tasks=tasks,
                  source_sha256=hashes,stdlib_only=True,
                  hypothesis='Two weighted scan orders related by one bit swap/CNOT may lift full source capacity without a growing-f permutation gate count.',
                  resource_preflight=dict(maximum_address_dimension=16,expected_aggregate_memory_bytes_upper=512*1024*1024))
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(probe,task):task for task in tasks}
        for future in as_completed(futures):
            result=future.result();results.append(result)
            print(json.dumps({k:result[k] for k in ('status','selected_columns','second_order','exact_channel_dimension','largest_tested_exact_scalar_rank','six_bank_input_column_rank_lower','six_bank_input_column_rank_upper','seconds')}),flush=True)
    if any(sha256(p.read_bytes()).hexdigest()!=hashes[p.name] for p in sources):
        raise AssertionError('a source changed during specified-bit scan screen')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results),indent=2)+'\n')


if __name__=='__main__': main()
