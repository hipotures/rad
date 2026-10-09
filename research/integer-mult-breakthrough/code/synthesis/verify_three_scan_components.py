#!/usr/bin/env python3
"""Bounded exact controls for separately scoped three-scan components.

Finite field exclusions concern real dyadic units in the specified orders.
Written characteristic-zero proofs have separate finite block bindings.
No native tape, recursive supplier, or multiplication exponent is certified.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import nonlex_scan_flux_probe as F
import three_lex_order_block_obstruction as B
import three_scan_dyadic_lift as L

P = F.P


def selected(workers):
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(P.probe, P.tasks()))
    expected = {1: (0, 8), 2: (48, 16), 3: (64, 0)}
    observed = {}
    for f, counts in expected.items():
        selected_rows = [row for row in rows if row['f'] == f]
        negative = sum(row['witness'] is None for row in selected_rows)
        positive = len(selected_rows) - negative
        if (negative, positive) != counts:
            raise AssertionError('The complete selected GF3 count changed')
        if any(row['normalized_left_assignments'] != 2**((1 << f)-1)
               for row in selected_rows if row['witness'] is None):
            raise AssertionError('A finite negative skipped invertible left diagonals')
        observed[f] = {'excluded': negative, 'finite_positive': positive}
    lower = B.V.probe()
    block = B.probe(3)
    if (block['one_reverse_cases'], block['same_order_cases'],
        len(block['consecutive']), len(block['separated'])) != (24, 16, 4, 8):
        raise AssertionError('The characteristic-zero block controls lost a case')
    lift = L.probe()
    if (lift['whole_prefix_calls'], lift['elementary_adds'], lift['explicit_scales'],
        lift['nonunit_power_two_scales'], lift['full_gaussian_fields']) != (3, 9, 9, 4, 48):
        raise AssertionError('The literal dyadic word or complete field ledger changed')
    if lift['forward_guard']['complete_linear_prefix_maximum_l1'] != [6, 1]:
        raise AssertionError('The complete forward prefix guard changed')
    if lift['inverse_guard']['complete_linear_prefix_maximum_l1'] != [4, 1]:
        raise AssertionError('The complete inverse prefix guard changed')
    if any(lift[name]['maximum_fractional_bits'] != 1
           for name in ('forward_guard', 'inverse_guard')):
        raise AssertionError('The complete common-grid fee changed')
    return {'status': 'PASS SELECTED THREE-SCAN BOUNDED CONTROLS',
            'complete_GF3_cases': len(rows), 'counts_by_f': observed,
            'normalization_and_corruption_controls': P.controls(),
            'inherited_complete_two_scan_cases': lower['f2_complete_cases'],
            'characteristic_zero_block_cases': 52,
            'literal_dyadic_lift': lift,
            'written_all_size_proof_not_formally_verified': True,
            'no_native_or_multiplier_exponent_claim': True}


def flux(workers):
    controls = F.flux_controls()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(P.probe, F.selected_tasks()))
    observed = {}
    for f, expected in ((2, (56, 8)), (3, (64, 0))):
        selected_rows = [row for row in rows if row['f'] == f]
        negative = sum(row['witness'] is None for row in selected_rows)
        positive = len(selected_rows)-negative
        if (negative, positive) != expected:
            raise AssertionError('The complete nonlex GF3 count changed')
        observed[f] = {'excluded': negative, 'finite_positive': positive}
    profiles = controls['rows']
    if len(profiles) != 25:
        raise AssertionError('The complete order-flux controls lost a profile')
    for profile in profiles:
        f, n = profile['f'], 1 << profile['f']
        if profile['name'] == 'complement-shear':
            if profile['sum_positive_hamming_flux'] != n*(f-1)//2+1:
                raise AssertionError('The high-flux formula changed')
            if profile['total_hamming_distance'] != n*(f-1)+1:
                raise AssertionError('The high-flux full path bill changed')
    wrong_cut = profiles[10]['cross_cut_ranks'][:]
    wrong_cut[0] -= 1
    if wrong_cut == profiles[10]['cross_cut_ranks']:
        raise AssertionError('The corrupted cut-rank control did not change the witness')
    # Reconstruct the affected actual cut, rather than accepting a saved count.
    profile = profiles[10]
    matrix = P.S.ordered_scan(tuple(profile['order']), 'prefix')
    n = len(matrix)
    actual = len(P.S.R.rref([[matrix[i][j] for j in range(n) if not j & 1]
                           for i in range(n) if i & 1], n//2)[1])
    if actual == wrong_cut[0]:
        raise AssertionError('A corrupted saved rank passed complete exact elimination')
    return {'status': 'PASS HIGH-FLUX THREE-SCAN BOUNDED CONTROLS',
            'complete_GF3_cases': len(rows), 'counts_by_f': observed,
            'exact_order_profiles': len(profiles),
            'corrupted_cut_rank_rejected': True,
            'no_Gaussian_diagonal_or_native_supplier_or_exponent_claim': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--component', choices=('selected', 'flux', 'all'), default='all')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError('Positive workers are required')
    if args.output and args.output.exists():
        raise FileExistsError('A fresh optional output file is required')
    sources = [Path(__file__).resolve()] + [Path(module.__file__).resolve()
        for module in (F, B, L, P, B.V, B.V.T, P.S, P.S.R)]
    hashes = {str(path.relative_to(Path(__file__).resolve().parents[2])):
              sha256(path.read_bytes()).hexdigest() for path in sources}
    started = datetime.now(timezone.utc).isoformat()
    receipt = {'component': args.component, 'started_utc': started,
               'workers': args.workers, 'standard_library_only': True,
               'source_closure': hashes}
    if args.component in ('selected', 'all'):
        receipt['selected'] = selected(args.workers)
    if args.component in ('flux', 'all'):
        receipt['flux'] = flux(args.workers)
    if hashes != {str(path.relative_to(Path(__file__).resolve().parents[2])):
                  sha256(path.read_bytes()).hexdigest() for path in sources}:
        raise AssertionError('The effective source closure changed during verification')
    receipt['status'] = 'PASS SCOPED THREE-SCAN COMPONENTS'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({key: receipt[key] for key in ('status', 'component', 'workers')}, sort_keys=True))


if __name__ == '__main__':
    main()
