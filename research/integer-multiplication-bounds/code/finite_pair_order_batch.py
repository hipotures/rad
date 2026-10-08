#!/usr/bin/env python3
"""Bounded exact pair-block-order successor using the frozen dispatcher."""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

import finite_pair_block_orders as orders
import finite_singleton_neighborhood as queue
from finite_singleton_successor import predecessor_workers

CONTROL = None
CONFIGURATION = {}
real_write_json = queue.write_json


def candidates(anchor, prior):
    h, base, positions = anchor['h'], anchor['base'], anchor['positions']
    excluded = {row['candidate_id'] for row in prior['candidate_definitions']}
    excluded.add(anchor['candidate_id'])
    settings = [*(dict(kind=kind, seed=0) for kind in
        ['reverse', 'common-reverse', 'parity', 'common-parity']),
        *(dict(kind='rotate', seed=seed) for seed in range(1, h//2-1)),
        *(dict(kind='common-rotate', seed=seed) for seed in range(h//2-1)),
        *(dict(kind='global-permutation', seed=seed) for seed in range(1, 65)),
        *(dict(kind='pair-permutation', seed=seed) for seed in range(1, 97)),
        *(dict(kind='point-permutation', seed=seed) for seed in range(1, 97))]
    rows, seen = [], set()
    for setting in settings:
        value, key = orders.identity(h, base, positions, setting['kind'], setting['seed'])
        if key in seen or key in excluded:
            continue
        seen.add(key)
        rows.append(dict(value, candidate_id=key, neighborhood='pair-block-'+setting['kind'],
                         changed=[dict(field='point_order', kind=setting['kind'], seed=setting['seed'])]))
    assert len(rows) == len(seen) and not seen.intersection(excluded)
    CONFIGURATION['neighborhood_counts'] = dict(Counter(row['neighborhood'] for row in rows))
    return rows, sorted(excluded)


def write_json(path, value):
    if path.name == 'protocol.json' and 'candidate_definitions' in value:
        value = dict(value, pair_block_order_configuration=CONFIGURATION)
    real_write_json(path, value)


def main():
    global CONTROL
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument('--control', type=Path, required=True)
    args, remaining = ap.parse_known_args()
    CONTROL = args.control
    control = json.loads(CONTROL.read_text())
    assert control['status'] == 'Terminal PASS'
    source_hash = sha256(Path(orders.__file__).read_bytes()).hexdigest()
    assert control['source_sha256']['finite_pair_block_orders.py'] == source_hash
    assert len(control['rows']) == 20
    CONFIGURATION.update(source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        constructor_sha256=source_hash, control_path=str(CONTROL),
        control_sha256=sha256(CONTROL.read_bytes()).hexdigest(),
        scientific_scope='Only paired point order changes. Canonical constructor exact-field regression and complete h8/h12 maps/physical/frame/target controls passed; all full candidate verifiers unchanged.',
        transfer_boundary='Exact original target maps and positive source envelopes; unchanged stage matching applies. A new best requires independent dirty/stage and full-map promotion.')
    queue.neighborhood = candidates
    queue.evaluate = orders.evaluate_ordered
    queue.predecessor_workers = predecessor_workers
    queue.write_json = write_json
    sys.argv = [sys.argv[0], *remaining]
    queue.main()


if __name__ == '__main__':
    main()
