#!/usr/bin/env python3
"""Bounded actual dirty-birth and separately restored signed-SWAP controls.

All physical f=1 columns and explicit f=2 fields are retained. No covariance
shortcut, complete native primitive or multiplier exponent follows.
"""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys


def effective_sources():
    root = Path(__file__).resolve().parents[1]
    paths = {Path(__file__).resolve()}
    for module in tuple(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name:
            path = Path(name).resolve()
            if path.suffix == '.py' and path.is_relative_to(root):
                paths.add(path)
        dynamic = getattr(module, 'SIDE_SOURCE', None)
        if isinstance(dynamic, Path) and dynamic.resolve().is_relative_to(root):
            paths.add(dynamic.resolve())
    return sorted(paths)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', required=True, choices=('equal-birth', 'nested-birth', 'separate-swap'))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output and args.output.exists():
        raise FileExistsError('Use a fresh evidence directory')
    names = {'equal-birth': 'degenerate_birth_reuse_probe',
             'nested-birth': 'nested_degenerate_birth_reuse',
             'separate-swap': 'joint_signed_swap_control'}
    producer = importlib.import_module(names[args.case])
    paths = effective_sources()
    topic = Path(__file__).resolve().parents[2]
    hashes = {str(p.relative_to(topic)): sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(), case=args.case,
                    workers=1, seed=None, source_sha256=hashes,
                    scope='Exact finite physical components; no complete native time or exponent claim')
    if args.case == 'separate-swap':
        cases = [(4, 1, False, True), (4, 1, True, True),
                 (4, 2, False, False), (4, 2, True, False)]
    else:
        cases = [(False, 1), (True, 1), (False, 2), (True, 2)]
    rows = [producer.probe(case) for case in cases]
    if args.case == 'separate-swap':
        if any(row['rank_charge'] != 360 or row['capacity'] != 96 for row in rows):
            raise AssertionError('The separately restored body capacity control changed')
    else:
        for case, row in zip(cases, rows):
            if row['rank_charge'] != (24 if case[0] else 28) or row['deficit'] != 4:
                raise AssertionError('The complete dirty-birth stock ledger changed')
    if any(sha256((topic / name).read_bytes()).hexdigest() != digest for name, digest in hashes.items()):
        raise ValueError('An effective source changed during verification')
    summary = dict(status='PASS BOUNDED ACTUAL COMPONENT', case=args.case, cases=rows,
                   complete_multiplier_exponent_established=False)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
        (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(dict(status=summary['status'], case=args.case, cases=len(rows),
                         effective_sources=len(paths))))


if __name__ == '__main__':
    main()
