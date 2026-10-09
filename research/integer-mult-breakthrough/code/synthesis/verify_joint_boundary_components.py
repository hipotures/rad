#!/usr/bin/env python3
"""Bounded actual joint-birth and address-boundary certificates.

The joint case retains both partial and canonical endpoints. The address case
checks its separate post-only, pointwise-sandwich and unitary models. Neither
case supplies a native all-size multiplication theorem.
"""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys


def effective_sources():
    code = Path(__file__).resolve().parents[1]
    paths = {Path(__file__).resolve()}
    for module in tuple(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name:
            path = Path(name).resolve()
            if path.suffix == '.py' and path.is_relative_to(code):
                paths.add(path)
        dynamic = getattr(module, 'SIDE_SOURCE', None)
        if isinstance(dynamic, Path) and dynamic.resolve().is_relative_to(code):
            paths.add(dynamic.resolve())
    return sorted(paths)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', required=True,
                        choices=('joint-mutable', 'address-boundary'))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output and args.output.exists():
        raise FileExistsError('Use a fresh evidence directory')
    module = {'joint-mutable': 'joint_mutable_birth_swap',
              'address-boundary': 'address_boundary_discriminator'}[args.case]
    producer = importlib.import_module(module)
    topic = Path(__file__).resolve().parents[2]
    paths = effective_sources()
    hashes = {str(path.relative_to(topic)): sha256(path.read_bytes()).hexdigest()
              for path in paths}
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(),
                    case=args.case, workers=1, seed=None, source_sha256=hashes,
                    scope='Exact finite components with explicit physical endpoints and separate obstruction models')
    cases = ([(1, 2, 1), (1, 2, 2), (2, 1, 1), (2, 1, 2)]
             if args.case == 'joint-mutable' else [(3, 1), (3, 2), (4, 1), (4, 2)])
    rows = [producer.probe(case) for case in cases]
    for row in rows:
        if args.case == 'joint-mutable':
            if (row['core_rank'], row['canonical_rank'], row['core_deficit'],
                    row['canonical_deficit']) != (22, 24, 2, 0):
                raise AssertionError('The joint core and complete boundary ledgers changed')
            if not all(row['negative_controls'].values()):
                raise AssertionError('A joint physical or forbidden-domain control failed')
        elif (not row['all_source_sink_dirty_channels_retained']
              or row['pointwise_sandwich_rank_range'][1] >= row['payload_stock']):
            raise AssertionError('The scoped complete-channel boundary witness changed')
    if any(sha256((topic / name).read_bytes()).hexdigest() != digest
           for name, digest in hashes.items()):
        raise ValueError('An effective source changed during verification')
    summary = dict(status='PASS BOUNDED ACTUAL COMPONENT', case=args.case,
                   cases=rows, complete_multiplier_exponent_established=False)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
        (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(dict(status=summary['status'], case=args.case,
                         cases=len(rows), effective_sources=len(paths))))


if __name__ == '__main__':
    main()
