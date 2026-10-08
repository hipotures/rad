#!/usr/bin/env python3
"""Terminal finite promotion composed with the reviewed exact recurrence.

The input phase composition identifies the promoted finite role counts.
This calculation changes only the independently reviewed packed cost
estimate; finite, Gaussian and upstream proof dependencies remain separate.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from asymmetric_motif import counts
from downstream_gaussian import check_sources
from downstream_packed_unrolling import recurrence_identity_checks, witness


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream', type=Path, required=True)
    ap.add_argument('--phase-composition', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), 'Use a fresh output path'
    start = time.monotonic()
    provenance = check_sources(args.upstream)
    phase = json.loads(args.phase_composition.read_text())
    assert phase['provenance']['commit'] == provenance['commit']
    assert phase['finite_promotions']
    assert len(phase['uniform_phase_regressions']) == 8
    assert all(row['passed'] for row in phase['uniform_phase_regressions'])
    roles = {int(h): int(r) for h, r in phase['verified_role_counts'].items()}
    candidates = []
    for p, rp in sorted(roles.items()):
        for q, rq in sorted(roles.items()):
            n = counts(p, q, rp, rq)
            if n['D'] > 0:
                candidates.append(witness(n, f'promoted-p{p}q{q}'))
    candidates.sort(key=lambda row:Q(row['parameters']['kappa']), reverse=True)
    best = candidates[0]
    best_kappa = Q(best['parameters']['kappa'])
    assert all(Q(row['model_upper']) < best_kappa for row in candidates[1:])
    old_selected = next(row for row in candidates
                        if row['bit_counts']['p'] == 52 and row['bit_counts']['q'] == 48)
    witnesses = [best] if old_selected is best else [best, old_selected]
    result = dict(campaign_id='20261007T222521Z', generated_at=datetime.now(timezone.utc).isoformat(),
                  provenance=provenance, input_phase_composition={
                      'path':str(args.phase_composition),
                      'bytes':args.phase_composition.stat().st_size,
                      'sha256':sha256(args.phase_composition.read_bytes()).hexdigest()},
                  source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in
                                 (Path(__file__), Path(__file__).with_name('downstream_packed_unrolling.py'),
                                  Path(__file__).with_name('asymmetric_motif.py'))},
                  verified_role_counts=roles, finite_promotions=phase['finite_promotions'],
                  recurrence_checks=recurrence_identity_checks(), best=best, witnesses=witnesses,
                  ranking=[dict(p=row['bit_counts']['p'], q=row['bit_counts']['q'],
                                kappa=row['parameters']['kappa'], model_upper=row['model_upper'],
                                baseline_ratio_lower=row['kappa_ratio_decimal_lower']) for row in candidates],
                  elapsed_seconds=time.monotonic()-start,
                  scope='Terminal supplied finite circuits, retained complex h50, reviewed phase inverse and exact growing-geometric recurrence; no general optimum or unconditional main theorem')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(best_pair=[best['bit_counts']['p'], best['bit_counts']['q']],
                         kappa=best['parameters']['kappa'], ratio=best['kappa_ratio_decimal_lower'],
                         log2_b_cutoff=best['common_log2_b_cutoff'],
                         pairs=len(candidates), seconds=result['elapsed_seconds'])))


if __name__ == '__main__':
    main()
