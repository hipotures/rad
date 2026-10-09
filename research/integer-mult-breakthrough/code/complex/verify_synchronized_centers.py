#!/usr/bin/env python3
"""Bounded literal center controls and an exact p12 hypothetical moment.

Runs the frozen physical toy in a fresh temporary directory. The larger
center geometry and complete side model are rebuilt and compared against
the retained profile fixture before exact root/threshold checks. Native
copy disposal, cap formation and a completed master are outside this check.
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

import synchronized_center_budget as budget


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    fixture = directory.parent.parent / 'fixtures/complex/synchronized-center-p12-profile.json'
    names = ['verify_synchronized_centers.py', 'synchronized_center_budget.py',
             'synchronized_pair_centers.py', 'canonical_subspace_frames.py',
             'paired_five_cube_discriminator.py', 'scalable_subspace_interfaces.py',
             'paired_cap_side_budget.py', 'paired_five_complete_baseline.py',
             'characteristic.py']
    paths = [directory / name for name in names] + [fixture]
    frozen = {path: path.read_bytes() for path in paths}
    timer = perf_counter()
    with TemporaryDirectory(prefix='rad-synchronized-centers-') as temporary:
        output = Path(temporary) / 'bounded-center.json'
        subprocess.run([sys.executable, '-B', str(directory / 'synchronized_pair_centers.py'),
                        '--workers', '1', '--bounded', '--output', str(output)],
                       check=True, capture_output=True, text=True)
        finite = json.loads(output.read_text())
    if not finite['status'].startswith('PASS'):
        raise AssertionError('The bounded full dirty center component did not pass')
    retained = json.loads(frozen[fixture])
    geometry = budget.center.geometry(12)
    fixed = budget.fixed_profile(geometry, split_targets=True, closed_original=False)
    cap = budget.side.raw_cap_profile(12)
    profile = budget.profile_with_side(fixed, cap['three_core_optimistic_raw_cap_profile'],
                                      cap['retained_aggregate_and_kernel_roles'])
    if budget.side.characteristic.serializable(profile) != retained['complete_profile']:
        raise AssertionError('The retained cap model or complete center/data histogram changed')
    saving = Q(retained['saving'])
    interval = budget.side.characteristic.moment_interval(profile, saving)
    if interval[1] >= 1 or budget.side.serialize_interval(interval) != retained['moment_interval_at_saving']:
        raise AssertionError('The exact requested threshold/profile certificate changed')
    bracket = retained['exact_root_bracket']
    low = budget.side.characteristic.moment_interval(profile, Q(bracket['lower']))
    high = budget.side.characteristic.moment_interval(profile, Q(bracket['upper']))
    if low[1] >= 1 or high[0] <= 1:
        raise AssertionError('The retained exact finite root bracket does not separate one')
    closed = budget.fixed_profile(geometry, split_targets=True, closed_original=True)
    adverse = budget.profile_with_side(closed, cap['three_core_optimistic_raw_cap_profile'],
                                       cap['retained_aggregate_and_kernel_roles'])
    if budget.side.characteristic.moment_interval(adverse, saving)[0] <= 1:
        raise AssertionError('The closed two-qh control unexpectedly fits the target')
    if any(path.read_bytes() != contents for path, contents in frozen.items()):
        raise AssertionError('A source or fixture changed during the bounded check')
    result = {'status': 'PASS bounded synchronized centers and exact hypothetical p12 moment',
              'seconds': perf_counter() - timer,
              'source_and_fixture_sha256': {path.name: sha256(contents).hexdigest()
                                            for path, contents in frozen.items()},
              'literal_toy_complete_physical_columns': finite['cases'][0]['complete_role_address_basis_columns'],
              'literal_toy_negative_controls': finite['cases'][0]['negative_controls'],
              'paired_center_p12_actual_growth_Pauli_images': geometry['root_growth_actual_interface_Pauli_images_checked'],
              'complete_p12_W': profile['W'], 'complete_p12_m': profile['m'],
              'complete_p12_rank': profile['complete_rank'], 'complete_p12_deficit': profile['deficit'],
              'saving': str(saving), 'moment_interval': budget.side.serialize_interval(interval),
              'exact_finite_model_root': {'lower': bracket['lower'], 'upper': bracket['upper']},
              'closed_two_qh_model_rejected': True,
              'scope': 'Literal center component and finite exact model arithmetic. The cap formation/readout model, native copy/time/precision, whole canonical master and exponent remain unverified.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'complete_physical_columns': result['literal_toy_complete_physical_columns'],
                      'exact_model_root': result['exact_finite_model_root']}), flush=True)


if __name__ == '__main__':
    main()
