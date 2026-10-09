#!/usr/bin/env python3
"""Bounded actual dirty words and exact conditional p12 profile arithmetic.

Fresh temporary outputs exercise the paid total root, direct-full word,
shared-helper splice and independent target-cap cut. The four retained p12
histograms/brackets are rebuilt without rerunning the full decoder sweep.
This check does not supply global cap formation, native tape fees, a master
or an integer-multiplication exponent.
"""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import perf_counter

import synchronized_dyadic_total_centers as total
import direct_full_total_centers as direct


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    fixture = directory.parents[1] / 'fixtures/complex/paid-total-direct-full-p12-profiles.json'
    names = ['verify_paid_total_and_splice.py', 'synchronized_dyadic_total_centers.py',
             'direct_full_total_centers.py', 'mixed_source_center_cap_splice.py',
             'mixed_source_cap_target_cut.py', 'synchronized_center_budget.py',
             'synchronized_pair_centers.py', 'canonical_subspace_frames.py',
             'paired_five_cube_discriminator.py', 'scalable_subspace_interfaces.py',
             'paired_cap_side_budget.py', 'paired_five_complete_baseline.py',
             'characteristic.py']
    paths = [directory / name for name in names] + [fixture]
    frozen = {p: p.read_bytes() for p in paths}
    timer, finite = perf_counter(), {}
    with TemporaryDirectory(prefix='rad-paid-total-splice-') as temporary:
        for source, bounded in [('synchronized_dyadic_total_centers.py', True),
                                ('direct_full_total_centers.py', True),
                                ('mixed_source_center_cap_splice.py', True),
                                ('mixed_source_cap_target_cut.py', False)]:
            out = Path(temporary) / (source + '.json')
            cmd = [sys.executable, '-B', str(directory / source)]
            if source != 'mixed_source_cap_target_cut.py':
                cmd.extend(['--workers', '1'])
            if bounded:
                cmd.append('--bounded')
            cmd.extend(['--output', str(out)])
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            data = json.loads(out.read_text())
            if not data['status'].startswith('PASS'):
                raise AssertionError('A bounded literal paid word failed')
            finite[source] = data
    retained = json.loads(frozen[fixture])
    cap = total.budget.side.raw_cap_profile(12)
    geometries = {'growing': total.geometry(12)[0], 'direct_full': direct.geometry(12)}
    arithmetic = []
    for row in retained['models']:
        fixed = total.budget.fixed_profile(geometries[row['schedule']],
                                          split_targets=True, closed_original=row['closed_original'])
        profile = total.budget.profile_with_side(fixed, cap['three_core_optimistic_raw_cap_profile'],
                                                 cap['retained_aggregate_and_kernel_roles'])
        if total.budget.side.characteristic.serializable(profile) != row['complete_profile']:
            raise AssertionError('A paid total/direct-full complete histogram differs')
        saving = Q(row['saving'])
        moment = total.budget.side.characteristic.moment_interval(profile, saving)
        if total.budget.side.serialize_interval(moment) != row['moment_interval_at_saving']:
            raise AssertionError('An exact retained threshold interval changed')
        if row['closed_original']:
            if moment[0] <= 1:
                raise AssertionError('The adverse closed 2qh control fitted b=.001')
        elif moment[1] >= 1:
            raise AssertionError('The stated copied-center model did not fit b=.001')
        bracket = row['exact_root_bracket']
        low = total.budget.side.characteristic.moment_interval(profile, Q(bracket['lower']))
        high = total.budget.side.characteristic.moment_interval(profile, Q(bracket['upper']))
        if low[1] >= 1 or high[0] <= 1:
            raise AssertionError('The exact finite model bracket does not separate one')
        arithmetic.append({'schedule': row['schedule'], 'closed_original': row['closed_original'],
                           'W': profile['W'], 'm': profile['m'], 'rank': profile['complete_rank'],
                           'deficit': profile['deficit'], 'bracket': {k: bracket[k] for k in ('lower', 'upper')}})
    shared = finite['mixed_source_center_cap_splice.py']['cases'][0]
    cut = finite['mixed_source_cap_target_cut.py']['case']
    if (shared['metadata']['roles'], shared['complete_forward_rank']) != (33, 265):
        raise AssertionError('Shared-helper stock/read price changed')
    if (cut['metadata']['roles'], cut['complete_forward_rank']) != (37, 290):
        raise AssertionError('Separate side stock/direct target-cut price changed')
    if any(p.read_bytes() != data for p, data in frozen.items()):
        raise AssertionError('A source/fixture changed during the bounded check')
    result = {'status': 'PASS bounded paid total/direct-full and mixed-source target cuts',
              'seconds': perf_counter() - timer,
              'source_and_fixture_sha256': {p.name: sha256(data).hexdigest() for p, data in frozen.items()},
              'total_toy_all_physical_columns': finite['synchronized_dyadic_total_centers.py']['cases'][0]['complete_physical_input_columns'],
              'direct_toy_all_physical_columns': finite['direct_full_total_centers.py']['cases'][0]['complete_physical_input_columns'],
              'shared_splice_dense_four_field_components': shared['literal_complete_four_field_real_imag_components_forward_and_reverse'],
              'target_cut_dense_four_field_components': cut['four_field_components_forward_and_reverse'],
              'local_trade': {'shared_roles': 33, 'shared_rank': 265, 'separate_roles': 37, 'separate_rank': 290,
                              'separate_cut_removes_extra_rank': 3, 'no_global_master_moment_claim': True},
              'conditional_model_arithmetic': arithmetic,
              'scope': 'Finite physical components and exact hypothetical complete-histogram arithmetic. Source/cap global formation/target clocks, native complete-copy tape costs/precision, canonical master and kappa remain open.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'conditional_models': len(arithmetic), 'shared_roles_rank': [33, 265],
                      'separate_roles_rank': [37, 290]}), flush=True)


if __name__ == '__main__':
    main()
