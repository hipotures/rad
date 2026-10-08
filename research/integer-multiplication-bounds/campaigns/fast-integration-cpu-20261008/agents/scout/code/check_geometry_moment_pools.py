#!/usr/bin/env python3
"""Independently check complete fixed I+J moments for frozen (h,h+2) pools.

No producer, matching, matrix profiler or root controller/search code is
imported. All input bytes are checked against the frozen run protocol. The
complete controller is assembled here from copied internal blocks, both
exterior directions, both growth fronts, actual-pair data and the endpoint.
At the reference saving, separate lower minima for the two axes prove a
strict failure for every pair in the frozen Cartesian pool.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import gzip
import json
from math import comb
from pathlib import Path
import time

from check_changed_fixed_dag import GRID, exact_moment

CAMPAIGN = Path(__file__).resolve().parents[3]


def file_bytes(path, bundle=None):
    if bundle is None:
        return path.read_bytes()
    return bundle[str(path.resolve().relative_to(CAMPAIGN))]


def digest(path, bundle=None):
    return hashlib.sha256(file_bytes(path,bundle)).hexdigest()


def check_row(row, h):
    assert row['h'] == h and row['v'] == comb(h, 3)
    assert row['loss'] == h*(h-1) and row['crt_disagreements'] == 0
    blocks = row['blocks']
    assert len(blocks) == h+1 and blocks[0] == 0
    assert all(isinstance(n, int) and n >= 0 for n in blocks)
    assert blocks[h] >= h
    assert sum(t*n for t,n in enumerate(blocks)) == row['rank_sum'] == h*row['R']+2*row['loss']


def signature(row):
    return row['R'], row['loss'], tuple(row['blocks'])


def load_pool(identities, h, bundle=None):
    pool = {}
    for identity in identities:
        path = CAMPAIGN / identity['path']
        raw = file_bytes(path,bundle)
        assert len(raw) == identity['bytes']
        assert hashlib.sha256(raw).hexdigest() == identity['sha256']
        row = json.loads(raw)
        check_row(row, h)
        pool.setdefault(signature(row), dict(row=row, identity=identity))
    return list(pool.values())


def copied_terms(row, N, m):
    h, copies = row['h'], N//row['v']
    assert copies*row['v'] == N
    blocks = list(row['blocks'])
    blocks[h] -= h
    blocks[1] += h
    assert sum(t*n for t,n in enumerate(blocks)) == h*row['R']+row['loss']
    terms = Counter({t: copies*n for t,n in enumerate(blocks) if t and n})
    bank = copies*row['R']
    terms[h] += bank
    terms[m-2*h] += bank
    return terms, bank, copies*row['loss']


def fixed_terms(dimensions, data, N):
    terms = Counter()
    for h in dimensions:
        terms[1] += 2*N
        terms[h-2] += 2*N
    for t in data:
        terms[t] += 2*N
    terms[1] += N
    return terms


def controller(rows, data):
    dimensions = [r['h'] for r in rows]
    a,b = dimensions
    assert b == a+2
    m,N = a*b, comb(a,3)*comb(b,3)
    widths = fixed_terms(dimensions,data,N)
    banks,L = [],0
    for row in rows:
        check_row(row,row['h'])
        axis,bank,loss = copied_terms(row,N,m)
        widths.update(axis)
        banks.append(bank)
        L += loss
    W = 2*N+sum(banks)
    mass = sum(t*n for t,n in widths.items())
    assert mass == m*W-N+L
    return dict(dimensions=dimensions,m=m,N=N,banks=banks,W=W,L=L,
                total_rank=mass,deficit=N-L,maxchild=max(widths),
                child_multiplicities=dict(sorted(widths.items())))


def minimum_degree(m, child):
    degree=1
    while child**degree*2 >= m**degree:
        degree += 1
    return degree


def check_run(directory, reference, bundle=None):
    directory = directory.resolve()
    start = time.monotonic()
    protocol_path,result_path = directory/'protocol.json',directory/'result.json'
    protocol,result = json.loads(file_bytes(protocol_path,bundle)),json.loads(file_bytes(result_path,bundle))
    dimensions = protocol['dimensions']
    a,b = dimensions
    assert b == a+2 and dimensions == result['dimensions']
    geom_identity = protocol['geometry_certificate']
    geom_path = CAMPAIGN / geom_identity['path']
    assert digest(geom_path,bundle) == geom_identity['sha256']
    geometry = json.loads(file_bytes(geom_path,bundle))
    analytic,actual = geometry['analytic_geometry'],geometry['all_actual_pairs']
    assert analytic['dimensions'] == actual['dimensions'] == dimensions
    assert actual['status'] == 'COMPLETE ACTUAL-PAIR NONVANISHING CERTIFICATE'
    assert actual['unresolved_failures'] == 0
    N = comb(a,3)*comb(b,3)
    assert actual['pairs'] == geom_identity['pairs'] == N
    data = analytic['data_profile']
    assert data == [1]*9+[a-2,a-6,a*b-2*(a+b)+2]
    assert sum(data) == a*b-a-b+1
    pools = [load_pool(ids,h,bundle) for ids,h in zip(protocol['input_files'],dimensions)]
    assert [len(pool) for pool in pools] == protocol['pool_sizes'] == result['pool_sizes']
    selected = [record['profile'] for record in result['selected']]
    for row,pool in zip(selected,pools):
        assert any(signature(row) == signature(record['row']) for record in pool)
    complete = controller(selected,data)
    expected = dict(result['complete_controller'])
    expected['child_multiplicities'] = {int(t):n for t,n in expected['child_multiplicities'].items()}
    for key,value in complete.items():
        assert value == expected[key], key
    saving = F(result['saving'])
    assert saving < reference
    selected_moment = exact_moment(complete['child_multiplicities'],complete['m'],complete['W'],saving)
    assert selected_moment['strictly_passes']
    selected_reference = exact_moment(complete['child_multiplicities'],complete['m'],complete['W'],reference)
    assert selected_reference['strictly_fails']
    # Power intervals all use a common exact dyadic grid. Negative bank terms
    # are integer-exact, so taking an axis minimum preserves a lower bound.
    m = a*b
    constant = fixed_terms(dimensions,data,N)
    axes = [[copied_terms(record['row'],N,m) for record in pool] for pool in pools]
    widths = set(constant)
    for axis in axes:
        for terms,_,_ in axis:
            widths.update(terms)
    lower,upper = {},{}
    for t in widths:
        interval = exact_moment({t:1},m,1,reference)
        lower[t] = int(F(interval['lower'])*GRID)
        upper[t] = int(F(interval['upper'])*GRID)
    axis_minima=[]
    for axis,pool in zip(axes,pools):
        values=[sum(n*lower[t] for t,n in terms.items())-bank*GRID
                for terms,bank,_ in axis]
        index=min(range(len(values)),key=lambda i: (values[i],pool[i]['identity']['path']))
        axis_minima.append(dict(lower_grid_numerator=str(values[index]),
                                profile=pool[index]['identity']))
    constant_lower = sum(n*lower[t] for t,n in constant.items())-2*N*GRID
    whole_lower = constant_lower+sum(int(x['lower_grid_numerator']) for x in axis_minima)
    assert whole_lower > 0
    # The zero-saving exact expression recovers the actual rank deficit;
    # its published endpoints are rounded outward on the dyadic grid.
    zero = exact_moment(complete['child_multiplicities'],m,complete['W'],F(0))
    exact_zero = F(complete['total_rank'],m*complete['W'])
    assert F(zero['lower']) <= exact_zero <= F(zero['upper'])
    degree = minimum_degree(m,complete['maxchild'])
    minimum_W = 2*N+sum(min(bank for _,bank,_ in axis) for axis in axes)
    maximum_W = 2*N+sum(max(bank for _,bank,_ in axis) for axis in axes)
    return dict(run=str(directory.relative_to(CAMPAIGN)),dimensions=dimensions,
                protocol_sha256=digest(protocol_path,bundle),result_sha256=digest(result_path,bundle),
                source_files=[len(ids) for ids in protocol['input_files']],
                unique_pool_sizes=[len(pool) for pool in pools],
                cartesian_pairs=len(pools[0])*len(pools[1]),
                geometry=geom_identity,selected_controller=complete,
                selected_saving=str(saving),selected_moment=selected_moment,
                reference_saving=str(reference),selected_reference_moment=selected_reference,
                all_pairs_failure_lower=str(F(whole_lower,GRID)),
                normalized_expression='sum count*(width/m)^(1-saving)-W',
                exact_axis_minima=axis_minima,
                all_frozen_pairs_strictly_fail_at_reference=True,
                native_halving_degree=degree,
                degree_inequality=dict(previous_fails=(complete['maxchild']**(degree-1)*2 >= m**(degree-1)),
                                       selected_strict=(complete['maxchild']**degree*2 < m**degree)),
                selected_wire_bits=complete['W'].bit_length(),
                frozen_W_range=[minimum_W,maximum_W],
                frozen_wire_bits_range=[minimum_W.bit_length(),maximum_W.bit_length()],
                seconds=time.monotonic()-start,
                scope='Exact complete moment exclusion of this frozen profile pool at the stated reference saving. Input DAGs, fixed matrix profiler, generic row compiler and all-size transfer are inherited, not replayed here.')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--run',action='append',type=Path)
    ap.add_argument('--bundle',type=Path,
                    help='Complete archived input bundle; runs are evaluated in memory without reconstructing execution paths')
    ap.add_argument('--reference',default='40278503243/1000000000000000')
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    assert not args.output.exists()
    bundle = None
    run_paths = args.run
    bundle_identity = None
    if args.bundle:
        raw = gzip.decompress(args.bundle.read_bytes()) if args.bundle.suffix == '.gz' else args.bundle.read_bytes()
        capture = json.loads(raw)
        assert capture['format'] == 'complete-frozen-profile-pools-v1'
        bundle = {}
        for record in capture['files']:
            content = record['text'].encode('utf-8')
            assert hashlib.sha256(content).hexdigest() == record['sha256']
            assert len(content) == record['bytes'] and record['path'] not in bundle
            bundle[record['path']] = content
        run_paths = [CAMPAIGN/path for path in capture['runs']]
        bundle_identity = dict(path=str(args.bundle),
                               decompressed_sha256=hashlib.sha256(raw).hexdigest(),
                               file_count=len(bundle))
    assert run_paths, 'Supply --run or --bundle'
    runs=[check_run(path,F(args.reference),bundle) for path in run_paths]
    result=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),
                source_sha256=digest(Path(__file__)),
                arithmetic_sha256=digest(Path(__file__).with_name('check_changed_fixed_dag.py')),
                bundle=bundle_identity,
                status='INDEPENDENT COMPLETE FROZEN-POOL EXCLUSIONS',runs=runs)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],runs=[
        {k:r[k] for k in ('dimensions','cartesian_pairs','all_pairs_failure_lower','native_halving_degree','selected_wire_bits')}
        for r in runs])))


if __name__ == '__main__':
    main()
