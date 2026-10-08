#!/usr/bin/env python3
"""Close a changed DATA family with all-weight incidence cuts and lower witnesses.

This reads complete retained modular rook arrays; it does not repeat any
unchanged matrix family. All rational zero cuts are independently recomputed.
Credits: James Chang's PR34 cuts, Rohan Arun's PR40 recovery interface, and
this campaign's parameterized source family and exact mixed audit.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import time
import numpy as np


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(4*1024**2), b''):
            h.update(block)
    return h.hexdigest()


def fraction(item):
    return F(item['numerator'], item['denominator'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--mixed-cut-receipt', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    begun = time.monotonic()
    own = Path(__file__).resolve().parent
    helper_path = own/'audit_mixed_fixed_negative_data.py'
    spec = importlib.util.spec_from_file_location('independent_incidence', helper_path)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    protocol = json.loads((args.run/'protocol.json').read_text())
    summary = json.loads((args.run/'summary.json').read_text())
    cuts_receipt = json.loads(args.mixed_cut_receipt.read_text())
    N = 4073300
    assert protocol['source_family_size'] == N
    assert (protocol['source_partition_start_inclusive'], protocol['source_partition_end_exclusive']) == (0, N)
    assert summary['source_pairs_completed'] == N and protocol['mutations'] == 0
    source = own/'gpu_basis_configured_full_family.py'
    assert digest(source) == protocol['source_sha256']
    for path, key in ((own/'gpu_basis_parameter_vectorized.py','helper_sha256'),
                      (own/'gpu_basis_parameter_discovery.py','inherited_helper_sha256'),
                      (own.parents[2]/'code/gpu_changed_basis_repair.py','inherited_source_sha256')):
        assert digest(path) == protocol[key]
    vectorized = (own/'gpu_basis_parameter_vectorized.py').read_text()
    assert "gpu_basis_parameter_discovery.py" in vectorized or 'HELPER' in vectorized
    candidate = Path(protocol['candidate_path'])
    if not candidate.is_absolute():
        candidate = Path('/srv/ai/research')/candidate
    assert digest(candidate) == protocol['candidate_sha256']
    permutation = protocol['actual_permutation']
    assert permutation == json.loads(candidate.read_text())['permutations']
    assert len(permutation) == 25 and all(sorted(row) == list(range(23)) for row in permutation)
    rows = [(permutation[i%25][i//25], i%25) for i in range(47)]
    cols = [(permutation[(528+j)%25][(528+j)//25], (528+j)%25) for j in range(47)]
    assert rows == [tuple(x) for x in cuts_receipt['corner_rows']]
    assert cols == [tuple(x) for x in cuts_receipt['corner_columns']]
    expected = [46]+[i+24 for i in range(1,22)]+[46-i for i in range(22,28)]+[i-26 for i in range(28,45)]+[1,0]
    assert expected == cuts_receipt['uniform_Q_rook_pivots']
    n = 49
    left = [[int(k==r or k==23+b or k==48) for k in range(n)] for r,b in rows]
    right = [[int(k==c or k==23+d or k==48) for k in range(n)] for c,d in cols]
    cuts = []
    for i,q in enumerate(expected):
        preceding = sum(p>q for p in expected[:i])
        if 1 <= i <= 21:
            selected = set(range(i+1,23)) | set(range(23+i+1,48)) | {48}
        elif 28 <= i <= 44:
            t = i-28
            selected = set(range(3+t,23)) | set(range(28+t,48))
        else:
            assert 46-q == preceding
            cuts.append({'row':i,'pivot':q,'bound':preceding,'trivial_suffix_columns':46-q})
            continue
        a = audit.rank([[row[k] for k in range(n) if k in selected] for row in left[:i+1]])
        b = audit.rank([[row[k] for k in range(n) if k not in selected] for row in right[q+1:]])
        assert a+b <= preceding
        cuts.append({'row':i,'pivot':q,'selected':sorted(selected),'left_rank':a,'right_rank':b,'bound':preceding})
    assert cuts == cuts_receipt['universal_rank_cuts']
    betas = [fraction(protocol[k]) for k in ('beta23','beta25')]
    inverse = [tuple(1/z for z in audit.weights(h,beta)) for h,beta in zip((23,25),betas)]
    primes = protocol['primes']
    assert primes == [65521,1000003] and all(audit.prime(p) for p in primes)
    assert all(z.denominator%p for pair in inverse for z in pair for p in primes)
    paths = [args.run/f'pivots-prime{p}.npy' for p in primes]
    arrays = [np.load(path,mmap_mode='r') for path in paths]
    flags_path = args.run/'pair-status.npy'
    flags = np.load(flags_path,mmap_mode='r')
    assert all(x.shape == (N,47) and x.dtype == np.int8 for x in arrays)
    assert flags.shape == (N,) and flags.dtype == np.uint8
    declared = {Path(x['path']).name:x for x in summary['binary_artifacts']}
    binary = []
    for path in paths+[flags_path]:
        entry = {'path':str(path),'bytes':path.stat().st_size,'sha256':digest(path)}
        assert all(entry[k] == declared[path.name][k] for k in ('bytes','sha256'))
        binary.append(entry)
    expected_array = np.asarray(expected,dtype=np.int8)
    successes = [0,0]; bad_sets = [[],[]]; disagreements = 0; uncovered = []
    for first in range(0,N,65536):
        stop = min(first+65536,N)
        a,b = [np.asarray(x[first:stop]) for x in arrays]
        good = [(x == expected_array).all(axis=1) for x in (a,b)]
        valid = [(x >= 0).all(axis=1) for x in (a,b)]
        same = (a == b).all(axis=1)
        status = valid[0].astype(np.uint8)+2*valid[1].astype(np.uint8)+4*same.astype(np.uint8)
        assert np.array_equal(status, flags[first:stop])
        for k in range(2):
            successes[k] += int(good[k].sum())
            bad_sets[k].extend((first+np.flatnonzero(~good[k])).tolist())
        disagreements += int((~same).sum())
        uncovered.extend((first+np.flatnonzero(~good[0]&~good[1])).tolist())
    assert disagreements == summary['field_profile_disagreements']
    assert len(uncovered) <= 1000, 'Further exact work required; retain this failed audit attempt separately.'
    triples = [list(combinations(range(h),3)) for h in (23,25)]
    def matrix(index):
        T,S = triples[0][index//2300],triples[1][index%2300]
        x = [inverse[0][0 if r in T else 1] for r in range(23)]
        y = [inverse[1][0 if r in S else 1] for r in range(25)]
        return [[x[r]*int(r==c)+y[b]*int(b==d)-1 for c,d in cols] for r,b in rows],T,S
    controls = []
    indices = set([0,N-1]+uncovered)
    indices.update(x['pair_index'] for x in summary['bounded_Q_exception_controls'])
    for index in sorted(indices):
        mat,T,S = matrix(index)
        pivots,values = audit.rook([r[:] for r in mat])
        field_controls = []
        for k,p in enumerate(primes):
            mod = [[z.numerator*pow(z.denominator,-1,p)%p for z in row] for row in mat]
            pp,vv = audit.rook(mod,p)
            assert pp == arrays[k][index].tolist()
            field_controls.append({'prime':p,'pivots':pp,'matches_Q':pp == pivots})
        controls.append({'pair_index':index,'T':T,'S':S,'Q_pivots':pivots,
                         'Q_nonzero_pivot_values':[str(z) for z in values],
                         'expected_Q_pivots':pivots == expected,'fields':field_controls})
    exceptional_Q = [x for x in controls if x['pair_index'] in uncovered and not x['expected_Q_pivots']]
    uniform = not exceptional_Q
    runs = [1,21,1,1,1,1,1,1,17,1,1]
    receipt = {'created_utc':datetime.now(timezone.utc).isoformat(),
        'status':'PASS COMPLETE RATIONAL UNIFORM DATA FAMILY' if uniform else 'FAIL UNIFORM FAMILY: EXACT SPECIALIZATION COUNTEREXAMPLES',
        'method':'All47 coefficient-free incidence upper cuts plus an independently audited prescribed complete rook sequence in at least one whole prime field for each lexical source pair; any uncovered pair is resolved directly over Q.',
        'source_sha256':digest(Path(__file__)), 'independent_rank_helper_sha256':digest(helper_path),
        'run_path':str(args.run),'run_protocol_sha256':digest(args.run/'protocol.json'),
        'run_summary_sha256':digest(args.run/'summary.json'),'generator_source_sha256':digest(source),
        'mixed_cut_receipt_path':str(args.mixed_cut_receipt),'mixed_cut_receipt_sha256':digest(args.mixed_cut_receipt),
        'pairs':N,'source_enumeration':'Exact lexicographic combinations(23,3) times combinations(25,3), second coordinate fastest; every array row checked once.',
        'beta23':str(betas[0]),'beta25':str(betas[1]),
        'inverse_source_products':[[str(z) for z in pair] for pair in inverse],
        'actual_common_permutation':permutation,'corner_rows':rows,'corner_columns':cols,
        'universal_upper_identity':cuts_receipt['universal_upper_identity'],'universal_rank_cuts':cuts,
        'expected_rook_pivots':expected,'whole_field_expected_sequence_successes':successes,
        'unlucky_field_indices':dict(zip(map(str,primes),bad_sets)),
        'uncovered_by_whole_field_lower_witness':uncovered,'independent_Q_and_field_controls':controls,
        'exceptional_Q_counterexamples':exceptional_Q,'binary_artifacts':binary,
        'one_front_runs':runs if uniform else None,
        'one_front_histogram':{'1':9*N,'17':N,'21':N,'481':N} if uniform else None,
        'zero_scope':'These fixed R/C incidence upper inequalities hold for all rational diagonal weights. They do not assert nonvanishing at an arbitrary basis parameter; only this independently bound complete lower-witness family supplies that gate.',
        'remaining_gates':'Local projector profiles, actual scalar words, source/center coordinate normalization, compiler recovery and semantic/assembly interfaces remain separate. No new kappa is claimed.',
        'elapsed_seconds':time.monotonic()-begun}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','beta23','beta25','pairs','whole_field_expected_sequence_successes','uncovered_by_whole_field_lower_witness','elapsed_seconds')}))


if __name__ == '__main__':
    main()
