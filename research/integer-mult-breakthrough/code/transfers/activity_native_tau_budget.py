#!/usr/bin/env python3
"""Exact constraints of inherited activity routing and two stopping ledgers.

These rational controls compare declared cost contracts. They supply no
native route, shorter scalar word, multiplication algorithm or lower bound.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time


FROZEN_TAU = 1 - Q(1, 2**50)
CASES = [
    ('frozen_small_K', FROZEN_TAU, Q(1, 2**54), Q(1, 2), (1+FROZEN_TAU)/2),
    ('frozen_omitted_K_negative', FROZEN_TAU, Q(1, 2**51), Q(1, 2), (1+FROZEN_TAU)/2),
    ('changed_route_half', Q(1, 2), Q(1, 10), Q(1, 2), Q(97, 100)),
    ('changed_route_near_threshold', Q(95, 100), Q(1, 100), Q(1, 2), Q(97, 100)),
]


def budgets(tau, c, beta, p):
    if not (0 < tau < 1 and c > 0 and 0 < beta < 1 and 0 < p < 1):
        raise ValueError('Cost parameters require tau,p,beta in (0,1) and c>0')
    old_overhead = tau*(1+c/beta)
    old_admissible = old_overhead < p
    H_power = c*tau/(1-tau)
    balanced_admissible = tau <= p and H_power < 1
    old_leaf_saving = (1-beta)*(1-p)
    H_saving = (1-p)*(1-H_power)
    if old_admissible and not 0 < old_leaf_saving < 1-tau:
        raise AssertionError('Old fixed-cutoff slack cap is inconsistent')
    if balanced_admissible and not 0 < H_saving <= 1-tau:
        raise AssertionError('Balanced-cutoff slack cap is inconsistent')
    return dict(tau=str(tau), K_power=str(c), old_cutoff_power=str(beta),
                potential_power=str(p), old_overhead_power=str(old_overhead),
                old_interface_admissible=old_admissible,
                old_leaf_selected_width_saving=str(old_leaf_saving),
                balanced_cutoff_power=str(H_power),
                balanced_interface_admissible=balanced_admissible,
                balanced_selected_width_saving=str(H_saving),
                inherited_selected_width_slack_cap=str(1-tau),
                scope='Conditional cost-ledger slack; not kappa or a routing lower bound')


def probe(case):
    name, tau, c, beta, p = case
    result = budgets(tau, c, beta, p)
    if name == 'frozen_small_K' and not result['old_interface_admissible']:
        raise AssertionError('Compatible tiny K exponent should pass')
    if name == 'frozen_omitted_K_negative':
        if not tau < p or result['old_interface_admissible']:
            raise AssertionError('Omitting K must fake compatibility in this case')
        if not result['balanced_interface_admissible']:
            raise AssertionError('The separate balanced ledger remains admissible')
    if name.startswith('changed_route') and not result['old_interface_admissible']:
        raise AssertionError('The specified improved routing contract should pass')
    result['case'] = name
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('workers must be positive')
    source = Path(__file__).resolve()
    source_hash = sha256(source.read_bytes()).hexdigest()
    started = datetime.now(timezone.utc).isoformat()
    clock = time.monotonic()
    cases = CASES[:2] if args.bounded else CASES
    if args.workers == 1:
        results = list(map(probe, cases))
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            results = list(pool.map(probe, cases))
    if not (1-FROZEN_TAU < Q(1, 10000)):
        raise AssertionError('Frozen direct-interface slack comparison failed')
    hypothetical = 11**100 < 12**97
    ordinary = 12**100 < 12**97
    if not hypothetical or ordinary or not FROZEN_TAU > Q(97, 100):
        raise AssertionError('Word moment and inherited overhead must be distinguished')
    rejected = False
    try:
        budgets(Q(1), Q(1, 10), Q(1, 2), Q(97, 100))
    except ValueError:
        rejected = True
    if not rejected:
        raise AssertionError('Invalid cost contract was accepted')
    if sha256(source.read_bytes()).hexdigest() != source_hash:
        raise AssertionError('Source changed during execution')
    result = dict(status='PASS EXACT CONDITIONAL ACTIVITY ROUTING BUDGET',
                  started_utc=started, completed_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256=source_hash, workers=args.workers, bounded=args.bounded,
                  cases=results, hypothetical_eleven_gate_Jensen=True,
                  actual_twelve_gate_Jensen=False,
                  omitted_K_fake_compatibility_rejected=True,
                  invalid_contract_rejected=True, native_route_implemented=False,
                  new_exponent=False, seconds=time.monotonic()-clock)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as out:
            out.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(status=result['status'], cases=len(results),
                          seconds=result['seconds'], new_exponent=False)), flush=True)


if __name__ == '__main__':
    main()
