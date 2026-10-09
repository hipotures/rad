#!/usr/bin/env python3
"""Independent exact moments of rebuilt signed-lane physical inventories.

Imports only RaD's separate rational interval implementation, not the producer.
No saved PASS or numerical moment is consumed. Apache-2.0; GPT-6.1 Sol assistance.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True


def need(value, message):
    if not value:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', type=Path, required=True)
    parser.add_argument('--interval-code', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    need(not sys.flags.optimize, 'assertion-disabled execution rejected')
    sys.set_int_max_str_digits(0)
    started = time.monotonic()
    spec = importlib.util.spec_from_file_location('rad_independent_intervals', args.interval_code)
    independent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(independent)
    result = []
    for folder in sorted(path for path in args.batch.iterdir() if path.is_dir()):
        path = folder/'physical-profile.json'
        if not path.exists():
            continue
        physical = json.loads(path.read_text())
        row = json.loads((folder/'selected-profile.json').read_text())
        h, v, m = physical['h'], physical['v'], physical['m']
        W, R = physical['W_per_vertex'], physical['physical_R']
        hist = Counter()
        for part in ('local_histogram','source_data_histogram','target_data_histogram'):
            hist.update({int(r):3*n for r,n in physical[part].items() if int(r) and n})
        hist.update({3*int(r):n for r,n in physical['physical_gauge_histogram'].items() if int(r) and n})
        hist[2] += 2*v
        need(dict(hist) == {int(r):n for r,n in physical['child_histogram'].items() if int(r) and n},
             'complete physical histogram differs')
        mass = sum(r*n for r,n in hist.items())
        need(m == 3*h and W == 2*v+R and R == row['R']-physical['pairs'], 'physical dimensions')
        need(m*W-mass == physical['deficit_per_vertex'] == 2*v-3*physical['loss'], 'exact deficit')
        need(sum(int(r)*n for r,n in physical['source_data_histogram'].items()) == v*(h-1), 'ordinary K/source itinerary')
        trials = {}
        for saving in (Fraction(5885669,10**10),Fraction(5878747,10**10)):
            lower, upper = independent.moment(m, W, dict(hist), saving)
            need(lower > 1, 'negative-result public component comparison not separated')
            trials[str(saving)] = dict(lower=str(lower), upper=str(upper),
                                      excess_lower=str(lower-1), excess_lower_decimal=float(lower-1),
                                      classification='REJECTED_STRICTLY_ABOVE_ONE')
        # Numerically locate a useful grid, then rigorously check both ends.
        lo, hi = 0., .1
        for _ in range(75):
            middle = (lo+hi)/2
            value = math.fsum(n*r*math.exp(middle*math.log(m/r)) for r,n in hist.items())/(m*W)
            if value < 1:
                lo = middle
            else:
                hi = middle
        grid = math.floor(lo*10**12)
        accepted, rejected = Fraction(grid,10**12), Fraction(grid+1,10**12)
        _, accepted_upper = independent.moment(m, W, dict(hist), accepted)
        rejected_lower, _ = independent.moment(m, W, dict(hist), rejected)
        need(accepted_upper < 1 < rejected_lower, 'root grid enclosure unresolved')
        result.append(dict(variant=folder.name, complete_children=dict(hist), m=m, W=W,
                           mass=mass, deficit=m*W-mass, root_grid_lower=str(accepted),
                           root_grid_upper=str(rejected), accepted_gap_lower=str(1-accepted_upper),
                           rejected_excess_lower=str(rejected_lower-1), shared_trials=trials,
                           input_sha256={file.name:sha256(file.read_bytes()).hexdigest() for file in
                                         (path,folder/'selected-profile.json')}))
    need(len(result) == 4, 'expected unchanged control and three variants')
    output = dict(status='EXACT_RATIONAL_LOCAL_PROFILE_OBSTRUCTION', results=result,
                  rounding_denominator=str(1 << 180), interval_source_sha256=sha256(args.interval_code.read_bytes()).hexdigest(),
                  elapsed_seconds=time.monotonic()-started,
                  scope='Independently recounts complete saved physical inventories and rigorously '
                        'encloses their moments. Local program/geometry checked separately. All four '
                        'fail the current supplied complex saving and final-public numeric milestone; '
                        'no final kappa or all-size theorem is established here.')
    with args.output.open('x') as stream:
        json.dump(output, stream, indent=2); stream.write('\n')
    for row in result:
        print(row['variant']+': root in ('+row['root_grid_lower']+', '+row['root_grid_upper']+'); '
              'both shared public trial moments strictly exceed one')


if __name__ == '__main__':
    main()
