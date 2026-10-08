#!/usr/bin/env python3
"""Independent finite-grid ceiling audit for a packed recurrence composition."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from review_asymmetric_motif import counts, independent_saving
from review_packed_unrolling import audit, stopped_recurrences


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--certificate', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), 'Use a fresh output path'
    start = time.monotonic()
    raw = args.certificate.read_bytes()
    data = json.loads(raw)
    assert data['provenance']['commit'] == 'bcd4ebde8692383539f8a48734e5fbf3a18a32c2'
    selected = data['best']
    pair = selected['bit_counts']['p'], selected['bit_counts']['q']
    kappa = Q(selected['parameters']['kappa'])
    roles = {int(h):int(r) for h,r in data['verified_role_counts'].items()}
    complex_ = selected['complex_counts']
    b = independent_saving(Q(complex_['eta']), complex_['m'])[1]
    competitors = []
    seen = set()
    for row in data['ranking']:
        p, q = row['p'], row['q']
        assert (p, q) not in seen
        seen.add((p, q))
        if (p, q) == pair:
            assert Q(row['kappa']) == kappa
            continue
        n = counts(p, q, roles[p], roles[q])
        a = independent_saving(n['eta'], n['m'])[1]
        assert 0 < b < a < Q(1, 32)
        # U=a² b/[b(1-a)+5a²] increases separately in a and b.
        # Its derivative numerators are b²(2a-a²) and 5a^4,
        # so independent primitive upper enclosures give upper ceilings.
        upper = a*a*b/(b*(1-a)+5*a*a)
        assert upper < kappa, (p, q)
        competitors.append(dict(p=p, q=q, upper=str(upper)))
    assert seen == {(p,q) for p in roles for q in roles}
    nearest = max(competitors, key=lambda row:Q(row['upper']))
    result = dict(input_sha256=sha256(raw).hexdigest(),
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  best=audit(selected), retained_comparison_rows=[audit(row) for row in data['witnesses'][1:]],
                  exact_stopped_recurrences=stopped_recurrences(),
                  independently_bounded_competitors=len(competitors),
                  selected_exceeds_every_other_guard_family_ceiling=True,
                  closest_competitor=nearest,
                  elapsed_seconds=time.monotonic()-start,
                  scope='Independent retained reviewer arithmetic plus longer primitive enclosures and monotone packed guard-family ceilings on supplied finite grid')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(kappa=result['best']['kappa'], competitors=len(competitors),
                         stopped_recurrences=result['exact_stopped_recurrences']['complete_stopped_recurrences'],
                         closest_pair=[nearest['p'], nearest['q']], status='PASS')))


if __name__ == '__main__':
    main()
