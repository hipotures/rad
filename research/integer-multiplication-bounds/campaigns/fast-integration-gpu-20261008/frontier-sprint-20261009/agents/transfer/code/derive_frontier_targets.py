#!/usr/bin/env python3
"""Exact paid supplier thresholds from a pinned decoded frontier certificate.

No finite supplier acceptance is inferred. Apache-2.0; OpenAI assistance.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys

sys.dont_write_bytecode = True
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

from check_balanced_composition import OLD, ceil, js, require


def requirements(target, beta, eta, weakening):
    a = target / ((1-2*eta)*(1-eta-target))
    return dict(ideal_ordinary_complex=target/(1-target), ordinary=a,
        complex=(a+weakening)/(1-beta), optimized_coarse=a*(1-OLD)/(1-a))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sprint', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not sys.flags.optimize, 'Optimized Python unsupported')
    require(not args.output.exists(), 'Output must be fresh')
    config = json.loads(args.config.read_bytes())
    pin = config['certificate']
    raw = (args.sprint/pin['path']).read_bytes()
    require(len(raw) == pin['bytes'] and sha256(raw).hexdigest() == pin['sha256'],
            'Decoded frontier certificate changed')
    certificate = json.loads(raw)
    public = Q(certificate['kappa'])
    require(public == Q(config['public_kappa']), 'Source-confirmed score changed')
    beta, eta, weakening, ratio = (Q(config[key]) for key in
        ('phase_stop', 'backoff', 'strict_weakening', 'required_ratio'))
    require(0 < beta < 1 and 0 < eta < Q(1,2) and weakening > 0 and ratio >= 1,
            'Invalid retained paid parameters')
    target = ratio*public
    final_grid = Q(ceil(target*10**12),10**12)
    exact = requirements(target,beta,eta,weakening)
    grid = requirements(final_grid,beta,eta,weakening)
    result = dict(status='PASS exact paid targets from decoded source; no supplier acceptance',
        source_pins=config, config_sha256=sha256(args.config.read_bytes()).hexdigest(),
        public_kappa=public, exact_floor=target, deliberate_final_grid=final_grid,
        exact_floor_requirements=exact, deliberate_final_requirements=grid,
        exact_floor_sufficient_1e12={k:Q(ceil(x*10**12),10**12) for k,x in exact.items()},
        deliberate_final_sufficient_1e12={k:Q(ceil(x*10**12),10**12) for k,x in grid.items()},
        scope='Necessary common ordinary/complex lower bounds and sufficient supplier grids in the retained paid balanced family. Optimized coarse target uses a paid atom strictly above its root; exact supplier moments, full finite bills and all47+7 remain prerequisites.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(js(result),sort_keys=True,indent=2)+'\n')
    print('PASS public κ='+str(public)+'; exact floor='+str(target)+'; final grid='+str(final_grid))


if __name__ == '__main__':
    main()
