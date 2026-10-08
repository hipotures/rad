#!/usr/bin/env python3
"""Compose terminal promoted finite circuits with the reviewed phase inverse.

Original counts and phase regressions remain immutable inputs. A promotion
must carry full scalar/frame/target/matching checks and bounded dirty tests;
this arithmetic does not replace its separately recorded mathematical proof.
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
from asymmetric_phase import compose
from downstream_gaussian import check_sources
from downstream_parameter_optimum import as_strings


def load_promotions(paths, provenance, roles):
    promoted = []
    for path in paths:
        data = json.loads(path.read_text())
        assert data['upstream_reference_commit'] == provenance['commit']
        assert data['completed_utc'] and data['small_checks']
        assert data['asymmetric_small_exchange']
        assert data['transfer']['rank'] and data['transfer']['dirty_identity']
        for row in data['full_checks']:
            h, r = row['h'], row['roles']
            assert row['checked']['all_scalar_coefficients_exact']
            assert row['checked']['forward_frames_nested']
            assert row['checked']['reverse_complement_frames_nested']
            assert row['targets']['all_output_envelopes_orthogonal_to_physical_targets']
            audit = row['independent_envelope_check']
            assert audit['all_input_frames_original_lines']
            assert audit['all_output_frames_exact']
            assert audit['every_designated_target_orthogonal']
            assert audit['forward_and_reverse_complement_nesting']
            assert row['stage_matching']['intersection_one']
            assert row['stage_matching']['distinct'] == row['stage_matching']['images']
            expected = counts(h, h, r, r)
            retained = data['equal_ground_counts'][str(h)]
            for key in ('N', 'm', 'W', 'L', 'D', 's', 'eta'):
                assert Q(retained[key]) == Q(expected[key])
            previous = roles.get(h)
            if previous is None or r < previous:
                roles[h] = r
            promoted.append(dict(ground=h, roles=r, previous_roles=previous,
                                 gap=row['gap'], certificate=str(path),
                                 circuit_sha256=row['graph']['circuit_sha256'],
                                 compiled_sha256=row['checked']['compiled_sha256'],
                                 logical_frames=audit['logical_frames'],
                                 physical_frame_transitions=audit['physical_frame_transitions'],
                                 full_dense_constraints=audit['unique_dense_constraint_checks'],
                                 verification_scope='Full symbolic scalar map and independent envelope timeline; bounded dense frames and complete dirty scalar controls separately retained'))
    return promoted


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream', type=Path, required=True)
    ap.add_argument('--motif-certificate', type=Path, required=True)
    ap.add_argument('--phase-certificate', type=Path, required=True)
    ap.add_argument('--promoted-certificate', type=Path, action='append', required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), 'Use a fresh output path'
    start = time.monotonic()
    provenance = check_sources(args.upstream)
    motif = json.loads(args.motif_certificate.read_text())
    phase = json.loads(args.phase_certificate.read_text())
    assert motif['provenance']['commit'] == phase['provenance']['commit'] == provenance['commit']
    regressions = []
    for row in phase['witnesses']:
        h, r, mode = row['bit_ground'], row['physical_side_roles'], row['mode']
        actual = compose(counts(h, h, r, r), mode)
        assert all(Q(actual['parameters'][k]) == Q(v) for k, v in row['parameters'].items())
        assert Q(actual['minimum_margin']) == Q(row['minimum_margin'])
        assert actual['cutoff_log2_b']['common'] == row['common_log2_b_cutoff']
        regressions.append(dict(ground=h, roles=r, mode=mode, passed=True))
    roles = {int(h): int(r) for h, r in motif['verified_role_counts'].items()}
    promotions = load_promotions(args.promoted_certificate, provenance, roles)
    candidates = [compose(counts(p, q, rp, rq))
                  for p, rp in sorted(roles.items()) for q, rq in sorted(roles.items())
                  if counts(p, q, rp, rq)['D'] > 0]
    candidates.sort(key=lambda row:row['parameters']['kappa'], reverse=True)
    best = candidates[0]
    inputs = [args.motif_certificate, args.phase_certificate]+args.promoted_certificate
    result = dict(campaign_id='20261007T222521Z', generated_at=datetime.now(timezone.utc).isoformat(),
                  provenance=provenance, inputs={str(p):{
                      'bytes':p.stat().st_size, 'sha256':sha256(p.read_bytes()).hexdigest()} for p in inputs},
                  source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in
                                 (Path(__file__), Path(__file__).with_name('asymmetric_phase.py'),
                                  Path(__file__).with_name('asymmetric_motif.py'))},
                  best=best, conservative_selected=compose(best['counts'], 'conservative'),
                  uniform_phase_regressions=regressions, verified_role_counts=roles,
                  finite_promotions=promotions,
                  ranking=[dict(p=row['counts']['p'], q=row['counts']['q'],
                                kappa=row['parameters']['kappa'],
                                baseline_ratio_lower=row['kappa_ratio_decimal_lower']) for row in candidates],
                  elapsed_seconds=time.monotonic()-start,
                  scope='Terminal finite promotion inputs composed with original packed recurrence and independently reviewed phase inverse; main theorem remains conditional')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result), indent=2)+'\n')
    print(json.dumps(as_strings(dict(best_pair=[best['counts']['p'], best['counts']['q']],
                                    kappa=best['parameters']['kappa'],
                                    ratio=best['kappa_ratio_decimal_lower'],
                                    promotions=len(promotions), candidates=len(candidates),
                                    seconds=result['elapsed_seconds']))))


if __name__ == '__main__':
    main()
