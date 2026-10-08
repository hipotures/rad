#!/usr/bin/env python3
"""Exact small actual source/descendant span Gram controls.

H=9I-J has at most one negative direction. On an independent indicator
basis B, det(B^T H B)>0 certifies positivity, <0 one negative direction,
and =0 degeneracy. All source/target coefficient families are reconstructed
from the actual monotone DAG. No frame compilation or bound is claimed.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time

import sympy as sp
from finite_intersection_blocks import IntersectionCircuit
from finite_physical_target_kernels import physical_intersections


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--h', type=int, nargs='+', default=[8, 12])
    ap.add_argument('--all-core-zero', action='store_true')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args(); assert not args.output.exists()
    start = time.monotonic(); rows = []
    result = dict(started_utc=datetime.now(timezone.utc).isoformat(), rows=rows,
        source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in
            [Path(__file__).name, 'finite_intersection_blocks.py', 'finite_physical_target_kernels.py']},
        method='Exact source and descendant indicator matrices, actual independent columns, determinant on H=9I-J; no floating arithmetic')
    for h in args.h:
        at = time.monotonic(); circuit = IntersectionCircuit(h); logical = circuit.verify()
        common = physical_intersections(circuit)
        descendants = {node:0 for node in circuit.active}
        for (_, target), node in circuit.outputs.items():
            descendants[node] |= 1 << (circuit.variables[target]-1)
        for node in sorted(circuit.active, reverse=True):
            for child in circuit.args[node] or ():
                descendants[child] |= descendants[node]
        triple_masks = [sum(1 << v for v in triple) for triple in circuit.inputs]
        H = 9*sp.eye(h)-sp.ones(h)
        assert H.det() != 0
        cache = {}

        def span(support):
            if support in cache:
                return cache[support]
            columns = [mask for i,mask in enumerate(triple_masks) if support & (1 << i)]
            M = sp.Matrix(h, len(columns), lambda row,col:(columns[col] >> row)&1)
            independent = M.rref()[1]
            B = M[:, list(independent)]
            determinant = (B.T*H*B).det(method='domain-ge')
            answer = dict(dimension=B.cols, determinant=str(determinant), sign=int(sp.sign(determinant)),
                actual_indicator_basis=[columns[i] for i in independent])
            cache[support] = answer
            return answer

        examined = [node for node in sorted(circuit.active) if not circuit.core[node]
                    and (args.all_core_zero or not common[node])]
        cases = []; signatures = Counter(); singular = []
        for node in examined:
            source = span(circuit.support[node])
            target = span(descendants[node])
            signature = source['sign'], target['sign'], source['dimension'], target['dimension']
            signatures[signature] += 1
            if not source['sign']:
                singular.append(node)
            cases.append(dict(node=node, source_union=circuit.union[node].bit_count(), target_common=common[node].bit_count(),
                source=source, target=target,
                nondegenerate_exact_source=source['sign'] != 0,
                positive_target_complement_available=target['sign'] == 1,
                simultaneous_null_obstruction=source['sign'] == 0 and target['sign'] == 0))
        row = dict(h=h, original=logical, examined_nodes=len(examined), unique_span_descriptors=len(cache),
            signatures={str(key):value for key,value in sorted(signatures.items())}, singular_source_nodes=singular,
            all_examined_sources_nondegenerate=not singular,
            simultaneous_null_obstructions=sum(case['simultaneous_null_obstruction'] for case in cases),
            cases=cases, elapsed_seconds=time.monotonic()-at,
            scope='Exact actual-span controls only; no scalable labels, physical schedule or transferred bound')
        rows.append(row); result['elapsed_seconds'] = time.monotonic()-start
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
        print(json.dumps(dict(h=h, examined=len(examined), singular_sources=len(singular),
            simultaneous_null_obstructions=row['simultaneous_null_obstructions'], seconds=row['elapsed_seconds'])),flush=True)
    result['status'] = 'Terminal exact span controls PASS'
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
