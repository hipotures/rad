#!/usr/bin/env python3
"""Bounded exact nonunit pre/post, path, scan and fixed-grid components.

Derived dense postprocessors are verification oracles. None of these cases
supplies a fast complete native boundary or multiplication exponent.
"""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys

MODULES = {'amplitude': 'nonunit_address_amplitude_preflight',
           'paths': 'single_route_prepost_obstruction',
           'scan': 'streaming_scan_boundary_preflight',
           'scan-grid': 'audit_streaming_scan_precision'}
CERTIFICATE = 'runs/20261009T033016Z-synthesis-nonunit-amplitude-preflight/results/certificate.json'
CERTIFICATE_SHA = '7bf6b5e41c361a2e4a01de0ed9cf7bd372d56706a922d6a87510a58091ae8892'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', required=True, choices=tuple(MODULES))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output and args.output.exists():
        raise FileExistsError('Use a fresh evidence directory')
    producer = importlib.import_module(MODULES[args.case])
    topic = Path(__file__).resolve().parents[2]
    code = topic / 'code'
    paths = {Path(__file__).resolve()}
    for module in tuple(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name:
            path = Path(name).resolve()
            if path.suffix == '.py' and path.is_relative_to(code):
                paths.add(path)
    if args.case == 'paths':
        path = topic / CERTIFICATE
        if sha256(path.read_bytes()).hexdigest() != CERTIFICATE_SHA:
            raise ValueError('The immutable unique-path input certificate changed')
        paths.add(path)
    hashes = {str(path.relative_to(topic)): sha256(path.read_bytes()).hexdigest()
              for path in sorted(paths)}
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(),
                    workers=1, case=args.case, source_and_input_sha256=hashes,
                    scope='Exact finite models; separately scoped analytical path or scan restrictions')
    if args.case == 'paths':
        rows = [producer.verify_case(case)
                for case in json.loads((topic / CERTIFICATE).read_text())['cases']]
        if sum(len(row['source_block_paths']) for row in rows) != 32:
            raise AssertionError('The complete unique-path coverage changed')
    else:
        rows = [producer.probe(case) for case in [(2, 0), (2, 1), (4, 0), (4, 1)]]
        if any(row.get('post_native_word_supplied', False) for row in rows):
            raise AssertionError('A dense oracle cannot be relabeled a supplied native word')
    if len(rows) != 4:
        raise AssertionError('All four original cases must be retained')
    if any(sha256((topic / name).read_bytes()).hexdigest() != digest
           for name, digest in hashes.items()):
        raise ValueError('An effective source or input changed during verification')
    summary = dict(status='PASS BOUNDED NONUNIT COMPONENT', case=args.case,
                   cases=rows, complete_native_boundary=False,
                   new_multiplier_exponent=False)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
        (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(dict(status=summary['status'], case=args.case,
                         cases=len(rows), effective_inputs=len(paths))))


if __name__ == '__main__':
    main()
