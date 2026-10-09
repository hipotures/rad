#!/usr/bin/env python3
"""Canonical endpoint compatibility of exact nonlinear matching primitives.

All 105 perfect matchings of the three-bit cube are considered. The actual
source primitive and F*A_M^-1 sink must each admit a certified one-C-child
factor with all nonlinear routes and gauges retained. This is a small
structural discriminator, not a native recurrence or exponent claim.
"""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time

import nonlinear_matching_frames as exact


EXACT_SHA = 'e0048d6949270f8e3abd34de7323bde72ff97d66e8b10e80ee20b49e9068b640'


def translation_label(pairs):
    differences = {a^b for a,b in pairs}
    return next(iter(differences)) if len(differences)==1 else None


def supports(A):
    M,_ = A
    return [sum(row[j]!=(0,0) for row in M) for j in range(len(M))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bounded',action='store_true')
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    files = [Path(__file__),Path(exact.__file__),Path(exact.general.__file__),Path(exact.general.exact.__file__),
             Path(exact.general.exact.reference.__file__),Path(exact.wrappers.__file__),Path(exact.wrappers.routes.__file__)]
    before = {p.name:sha256(p.read_bytes()).hexdigest() for p in files}
    if before[Path(exact.__file__).name]!=EXACT_SHA:
        raise AssertionError('pinned nonlinear one-child factor source changed')
    utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    n = 3
    F = exact.matrix_word([('C',1 << j,1) for j in range(n)],n)
    candidates = list(exact.matchings(tuple(range(1 << n))))
    if args.bounded:
        # Odd/even translations and two nonlinear mixed/even matchings retain
        # both acceptance and rejection tests; the full run covers all105.
        candidates = [p for p in candidates if translation_label(p) in (1,2,3,7)]+[
            ((0,1),(2,7),(3,6),(4,5)),((0,2),(1,7),(3,5),(4,6))]
    rows,retained = [],[]
    for pairs in candidates:
        A = exact.matching_matrix(pairs,1 << n)
        source,source_reject = exact.factor_one_child(A)
        if source is None or source['rank']!=1:
            raise AssertionError('a complete matched-pair primitive did not admit exactly one width1 child')
        sink_actual = exact.matrix_product(F,exact.adjoint(A))
        degrees = supports(sink_actual)
        all_odd = all((a^b).bit_count() & 1 for a,b in pairs)
        expected = []
        for address in range(1 << n):
            mate = next(b if address==a else a for a,b in pairs if address in (a,b))
            expected.append(4 if (address^mate).bit_count() & 1 else 8)
        if degrees!=expected:
            raise AssertionError('odd-distance cancellation formula failed on an actual canonical sink')
        sink,reject = exact.factor_one_child(sink_actual)
        admitted = sink is not None and sink['rank']==n-1
        row = dict(pairs=[list(p) for p in pairs],translation=translation_label(pairs),
                   nonclifford=not exact.is_clifford(A),all_pairs_odd=all_odd,
                   canonical_sink_column_supports=degrees,admitted_width2=admitted,
                   actual_sink_rank=None if sink is None else sink['rank'],rejection=reject)
        rows.append(row)
        if admitted:
            retained.append(dict(label=row,source_plan=source,sink_plan=sink,source_matrix=A,
                                 sink_matrix=sink_actual))
    edge_rows = []
    for i,left in enumerate(retained):
        for j,right in enumerate(retained):
            # Source j has A_j; target i ends in F*A_i^-1.
            actual = exact.matrix_product(left['sink_matrix'],exact.adjoint(right['source_matrix']))
            plan,reject = exact.factor_one_child(actual)
            rank = None if plan is None else plan['rank']
            if i==j and rank!=n:
                raise AssertionError('diagonal F*M_i endpoint did not keep full mixing rank')
            edge_rows.append(dict(target=i,source=j,one_child_rank=rank,
                                  orthogonal_saving=rank==n-2,rejection=reject))
    # Complete four-field f1/f2 source/sink payload controls for one example
    # of each accepted kind; any newly accepted nonlinear kind is retained.
    representatives = []
    for nonlinear in (False,True):
        chosen = next((r for r in retained if r['label']['nonclifford']==nonlinear),None)
        if chosen is not None:
            representatives.append(chosen)
    fields = 0
    for entry in representatives:
        for plan,A in ((entry['source_plan'],entry['source_matrix']),(entry['sink_plan'],entry['sink_matrix'])):
            plan['input_route_word'] = exact.route_word(plan['input_route'])
            plan['output_route_word'] = exact.route_word(plan['output_route'])
            for f in (1,2):
                raw = [exact.wrappers.routes.payload(a) for a in range(1 << (n*f))]
                actual,g = exact.execute_plan(plan,raw,f)
                expect,h = exact.tensor_reference(A,raw,f)
                grid = max(g,h)
                if [[x << (grid-g) for x in row] for row in actual] != [[x << (grid-h) for x in row] for row in expect]:
                    raise AssertionError('canonical matching endpoint full payload differs from exact one-child factor')
                fields += 4*len(raw)
    if before!={p.name:sha256(p.read_bytes()).hexdigest() for p in files}:
        raise AssertionError('effective source changed during execution')
    certificate = dict(status='PASS EXACT CANONICAL MATCHING DISCRIMINATOR',started_utc=utc,
                       completed_utc=datetime.now(timezone.utc).isoformat(),effective_sources=before,
                       bounded=args.bounded,candidates=len(rows),parity_flipping_matchings=sum(r['all_pairs_odd'] for r in rows),
                       source_width=1,target_width=2,admitted=len(retained),
                       admitted_nonclifford=sum(r['label']['nonclifford'] for r in retained),
                       all_cases=rows,retained_labels=[r['label'] for r in retained],
                       complete_cross_profile=edge_rows,complete_endpoint_fields=fields,
                       representatives=representatives,seconds=time.monotonic()-started,
                       scope='All three-bit matching primitives in the full run. One-child source/sink/cross factors are exact; native guarded routing, helper chronology, full stock and kappa remain unproved.')
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(certificate,indent=2)+'\n')
    print(json.dumps({k:certificate[k] for k in ('status','candidates','parity_flipping_matchings','admitted','admitted_nonclifford','complete_endpoint_fields','seconds')}),flush=True)


if __name__ == '__main__':
    main()
