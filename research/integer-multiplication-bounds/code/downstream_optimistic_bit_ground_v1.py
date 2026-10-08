#!/usr/bin/env python3
"""Exact, explicitly hypothetical role-reduction scenarios for useful grounds."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_gaussian import require
from downstream_generic_ground_screen import checked_case, objective
from downstream_parameter_optimum import as_strings


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--saved-screen', type=Path, required=True)
    ap.add_argument('--new-h53-producer', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args();require(not args.output.exists(), 'Use a fresh output path')
    start = time.monotonic();code = Path(__file__).parent
    old = json.loads(args.saved_screen.read_text())
    require(old['status'] == 'PASS EXACT SAVED GENERIC GROUND SCREEN; NO NEW FINITE PROMOTION OR KAPPA',
            'Saved full actual candidate screen absent')
    for name, digest in old['source_sha256'].items():
        require(sha(code/name) == digest, 'Pinned saved-screen source differs '+name)
    anchor = checked_case(args.new_h53_producer)
    require(anchor['h'] == 53 and anchor['roles'] == 531483 and
            anchor['actual_histogram_audit'] is not None, 'New exact h53 anchor differs')
    anchor['objective'] = objective(53, 531483)
    rows = []
    for h in (54, 56):
        previous = next(row for row in old['rows'] if row['h'] == h)
        for reduction in (0, 7500, 28000, 35500):
            roles = previous['roles']-reduction
            obj = objective(h, roles)
            rows.append(dict(h=h, saved_actual_roles=previous['roles'], role_reduction=reduction,
                             hypothetical_roles=roles, objective=obj,
                             above_new_h53=obj['chosen_saving'] > anchor['objective']['chosen_saving'],
                             source_case=previous['source_case'],
                             construction='ACTUAL SAVED INPUT only' if reduction == 0 else
                             'HYPOTHETICAL COUNT; no edited graph, rank histogram or scalar guard certified')))
    paths = (args.saved_screen, args.new_h53_producer)
    result = dict(status='PASS EXACT OPTIMISTIC GROUND SCENARIOS; NO NEW PRIMITIVE PROMOTION',
                  campaign_start='2026-10-07T22:25:21Z', campaign_original_deadline='2026-10-08T08:25:21Z',
                  campaign_deadline='2026-10-08T10:00:00Z', generated_utc=datetime.now(timezone.utc).isoformat(),
                  input_files={str(p): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in paths},
                  source_sha256={p.name: sha(p) for p in
                                 (Path(__file__), code/'downstream_generic_ground_screen.py')},
                  anchor=anchor, rows=rows, elapsed_seconds=time.monotonic()-start,
                  scope='Useful scenario comparisons, not lower bounds on achievable role counts. Passing needs actual changed graph construction and independent promotion; failure under one hypothesized reduction does not exclude stronger reductions. No graph or optimizer is replayed.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result), indent=2, sort_keys=True)+'\n')
    print('NEW SAVED h53 ANCHOR', anchor['objective']['chosen_saving'], flush=True)
    for row in rows:
        print('SCENARIO', row['h'], row['role_reduction'], row['hypothetical_roles'],
              row['objective']['saving_decimal_lower'], row['above_new_h53'], flush=True)


if __name__ == '__main__':
    main()
