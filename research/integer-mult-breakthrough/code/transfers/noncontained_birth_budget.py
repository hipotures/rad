#!/usr/bin/env python3
"""Exact paid-moment discriminator for noncontained frame birth reuse.

This is a proposed cost-ledger analysis, not a synthesized birth circuit. A
Grassmann move can reduce physical stock but loses endpoint deficit unless the
donor frame is contained. Exact intervals separate this loss from concavity.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import time

import encoding_slack as bounds


TOPIC = Path(__file__).resolve().parents[2]
CONFIG = TOPIC/'configs/transfers/noncontained-birth-budget.json'


def logarithm(ratio):
    scale = 0
    while ratio >= 2:
        ratio /= 2; scale += 1
    lo, hi = bounds.logarithm_interval(ratio, 40)
    two_lo, two_hi = bounds.logarithm_interval(Q(2), 40)
    return lo+scale*two_lo, hi+scale*two_hi


@lru_cache(None)
def normalized_power(t, m, saving):
    if not 0 < t <= m:
        raise ValueError('Paid width is outside the proposed ambient block')
    lo, hi = logarithm(Q(m, t))
    lower = bounds.exponential_interval(saving*lo, 8)[0]
    upper = bounds.exponential_interval(saving*hi, 8)[1]
    return Q(t, m)*lower, Q(t, m)*upper


def merge_moment(h, e, s, d, saving):
    m = h*h; rank = e+s-2*d
    if not 1 <= e < h or not 0 <= s < h or not max(0, e+s-h) <= d <= min(e-1, s):
        raise ValueError('Not a feasible noncontained proper-frame pair')
    a, b, r = [normalized_power(t, m, saving) for t in (h-e, m-h+s, rank)]
    return a[0]+b[0]-r[1], a[1]+b[1]-r[0]


def classify(interval):
    return 'above1' if interval[0] > 1 else 'below1' if interval[1] < 1 else 'unresolved'


def case(payload):
    h, saving = payload; m = h*h
    maximum = merge_moment(h, 1, 0, 0, saving)
    transverse_lines = merge_moment(h, 1, 1, 0, saving)
    # Dropping the transverse rank-two move falsely keeps the contained-pair
    # majorization benefit while deleting its actual endpoint-deficit loss.
    a = normalized_power(h-1, m, saving); b = normalized_power(m-h+1, m, saving)
    fake = a[0]+b[0], a[1]+b[1]
    if classify(maximum) == 'unresolved' or classify(transverse_lines) == 'unresolved' or classify(fake) != 'above1':
        raise ValueError('Exact charged/fake moment comparison is unresolved')
    return dict(h=h,ambient_selected_width=m,saving=str(saving),
        universal_noncontained_upper=bounds.compact_interval(*maximum),
        universal_upper_status=classify(maximum),
        extremal_dimensions=dict(e=1,s=0,d=0,removed=[h-1,m-h],replacement=1),
        transverse_line_dimensions=dict(e=1,s=1,d=0,removed=[h-1,m-h+1],replacement=2),
        transverse_line_moment=bounds.compact_interval(*transverse_lines),
        transverse_line_status=classify(transverse_lines),
        fake_omitted_rank_two_move=bounds.compact_interval(*fake),
        unpaid_move_can_fake_improvement=True,removed_physical_stock_units=1,
        extremal_endpoint_deficit_loss=2,transverse_endpoint_deficit_loss=2,
        ledger_realizable_circuit_proved=False,
        threshold_crossing_possible_from_one_legal_merge=classify(maximum)=='above1')


def small_universal_controls(saving):
    checked = 0
    for h in range(2, 9):
        maximum = merge_moment(h, 1, 0, 0, saving)
        for e in range(1, h):
            for s in range(h):
                for d in range(max(0, e+s-h), min(e-1, s)+1):
                    if (e,s,d) == (1,0,0):
                        continue
                    candidate = merge_moment(h,e,s,d,saving)
                    if candidate[1] >= maximum[0]:
                        raise ValueError('Finite dimension control disagrees with the strict analytical maximum')
                    checked += 1
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args(); config = json.loads(CONFIG.read_text())
    helper = Path(bounds.__file__).resolve(); arithmetic = Path(bounds.gaussian.__file__).resolve()
    for path,digest in [(helper,config['interval_helper_sha256']),(arithmetic,config['gaussian_arithmetic_sha256'])]:
        if sha256(path.read_bytes()).hexdigest()!=digest: raise ValueError('Pinned independent helper changed')
    hashes={str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest()
            for p in [Path(__file__).resolve(),CONFIG,helper,arithmetic]}
    saving=Q(config['saving']); protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),
        workers=args.workers,source_config_sha256=hashes,seed=None,scope=config['scope'])
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False);(args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    started=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows=list(pool.map(case,[(h,saving) for h in config['dimensions']]))
    controls=small_universal_controls(saving)
    if any(sha256((TOPIC/path).read_bytes()).hexdigest()!=digest for path,digest in hashes.items()):
        raise ValueError('Source changed during immutable attempt')
    result=dict(status='NONCONTAINED BIRTH PAID-MOMENT DISCRIMINATOR PASS',cases=rows,
        small_dimension_pairs_below_analytical_maximum=controls,seconds=time.monotonic()-started,
        scope=config['scope'],actual_circuit_or_native_transfer=False,new_exponent=False)
    if args.output:(args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','seconds','scope']}))


if __name__=='__main__':main()
