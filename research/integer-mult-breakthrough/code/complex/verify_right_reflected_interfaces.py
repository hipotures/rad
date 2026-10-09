#!/usr/bin/env python3
"""Complete small reverse-interface controls for actual right backgrounds.

The expected matrices explicitly multiply C_T*C_full^-1*F_E^-1.
All physical source/address columns are tested. This supplements the
reflection producer's forward-birth checks and larger algebraic controls.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter

import right_reflected_frame_gauges as producer


PRODUCER_SHA = '3e10a8017eb78dce2aaefe7366e6cde32e1e5a1701b209fc5151affb79c8ebf4'


def reverse_matrix(E,T,n):
    exact=producer.exact
    source=exact.reference.frame_matrix(E,n)['numerator']
    background=exact.reference.frame_matrix(producer.full(n),n)['numerator']
    target=exact.reference.frame_matrix((T,),n)['numerator']
    size=1<<n
    def adjoint(A):
        return [[(A[y][x][0],-A[y][x][1]) for y in range(size)] for x in range(size)]
    matrix=producer.matrix_product(target,producer.matrix_product(adjoint(background),adjoint(source)))
    return matrix,len(E)+n+1


def staged_entry(result,x,y):
    exact=producer.exact
    gauge,child=result['stages']
    middle=gauge['output_affine_offset']^exact.embed(y,gauge['output_columns'])
    coefficient=exact.reconstructed_entry(gauge,middle,y)
    return exact.multiply_gaussian(coefficient,exact.reconstructed_entry(child,x,middle))


def probe(n):
    exact=producer.exact
    spaces=exact.reference.all_subspaces(n)
    counts=entries=0
    digest=sha256()
    inverse_order_negative=False
    for T in range(1,1<<n):
        if T.bit_count()%2==0:
            continue
        R=exact.reference.perpendicular((T,),n)
        for E in spaces:
            if len(exact.basis(E+R))!=len(R):
                continue
            result=producer.compile_right_to_canonical(E,(T,),n)
            matrix,grid=reverse_matrix(E,T,n)
            rank=result['selected_rank_per_column']
            for x in range(1<<n):
                for y in range(1<<n):
                    numerator=staged_entry(result,x,y)
                    if matrix[x][y]!=tuple(value << (grid-rank) for value in numerator):
                        raise AssertionError(('Reverse actual matrix failed',n,E,T,x,y))
            correct=(exact.inverse_word(exact.literal_word(E,n))
                     +exact.inverse_word(exact.literal_word(producer.full(n),n))
                     +exact.literal_word((T,),n))
            wrong=(exact.inverse_word(exact.literal_word(producer.full(n),n))
                   +exact.inverse_word(exact.literal_word(E,n))
                   +exact.literal_word((T,),n))
            if exact.tableau(correct,n)!=exact.tableau(wrong,n):
                inverse_order_negative=True
            counts+=1;entries+=(1<<n)**2
            digest.update(json.dumps(result,sort_keys=True).encode())
    if not inverse_order_negative:
        raise AssertionError('Reversed background inverse order was not detected')
    return dict(n=n,all_odd_nested_reverse_births=counts,complete_matrix_entries=entries,
                exact_stages_sha256=digest.hexdigest(),wrong_inverse_order_rejected=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--workers',type=int,default=1)
    parser.add_argument('--bounded',action='store_true')
    args=parser.parse_args()
    if not 1<=args.workers<=4:
        raise ValueError('Use one to four workers')
    files=[Path(__file__),Path(producer.__file__),Path(producer.exact.__file__),
           Path(producer.exact.reference.__file__)]
    if sha256(files[1].read_bytes()).hexdigest()!=PRODUCER_SHA:
        raise AssertionError('Pinned reflection source changed')
    if sha256(files[2].read_bytes()).hexdigest()!=producer.COMPILER_SHA or \
            sha256(files[3].read_bytes()).hexdigest()!=producer.exact.REFERENCE_SHA:
        raise AssertionError('Pinned compiler/canonical dependencies changed')
    hashes={file.name:sha256(file.read_bytes()).hexdigest() for file in files}
    protocol=dict(started_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,
                  native_threads_each=1,source_sha256=hashes,seeds=None,
                  scope='Complete small physical reverse operators; no stock, routing or exponent claim.')
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    start=perf_counter()
    # The producer's first bounded test independently prices forward
    # endpoints; this verifier adds every reverse small matrix coefficient.
    forward=producer.small_probe(3)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        reverse=list(pool.map(probe,[3] if args.bounded else [3,4]))
    if any(sha256(file.read_bytes()).hexdigest()!=hashes[file.name] for file in files):
        raise AssertionError('An effective source changed during reverse controls')
    certificate=dict(status='PASS ACTUAL RIGHT-FRAME FORWARD AND REVERSE CONTROLS',
                     protocol=protocol,completed_utc=datetime.now(timezone.utc).isoformat(),
                     elapsed_seconds=perf_counter()-start,forward=forward,reverse=reverse,
                     scope='Literal exact finite address operators only. Right-body helper reuse remains a separately paid chronological/stock hypothesis.')
    if args.output:
        (args.output/'certificate.json').write_text(json.dumps(certificate,indent=2)+'\n')
    print(json.dumps(certificate,indent=2),flush=True)


if __name__=='__main__':
    main()
