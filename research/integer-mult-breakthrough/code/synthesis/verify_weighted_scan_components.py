#!/usr/bin/env python3
"""Bounded weighted-scan controls without changing frozen producer protocols."""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import importlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=('solver', 'structure'), required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output and args.output.exists():
        raise FileExistsError('Use a fresh optional output directory')
    name = 'weighted_scan_intertwiners' if args.case == 'solver' else 'weighted_scan_structure'
    producer = importlib.import_module(name)
    paths = [Path(__file__).resolve(), Path(producer.__file__).resolve()]
    topic = paths[0].parents[2]
    pins = {str(path.relative_to(topic)): sha256(path.read_bytes()).hexdigest() for path in paths}
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(), workers=1,
                    case=args.case, effective_source_sha256=pins,
                    scope='Bounded exact original probes, not independent implementation or native proof')
    if args.case == 'solver':
        rows = [producer.probe(f) for f in (2, 3)]
        if [row['exact_intertwiner_dimension'] for row in rows] != [12, 19]:
            raise AssertionError('The retained small scan-space exceptions changed')
    else:
        rows = [producer.component(f) for f in (4, 5)]
        if [row['exact_full_intertwiner_dimension'] for row in rows] != [34, 66]:
            raise AssertionError('The complete quotient channel dimension changed')
        if any(row['scalar_rank_upper'] != 3 or row['explicit_stack_rank'] != 10
               or not row['complete_input_column_excluded'] for row in rows):
            raise AssertionError('The complete six-bank capacity control failed')
    if any(sha256((topic / path).read_bytes()).hexdigest() != digest for path, digest in pins.items()):
        raise ValueError('A frozen source changed during verification')
    summary = dict(status='PASS BOUNDED WEIGHTED SCAN COMPONENT', case=args.case,
                   cases=rows, complete_native_boundary=False, new_multiplier_exponent=False)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
        (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(dict(status=summary['status'], case=args.case, cases=len(rows))))


if __name__ == '__main__':
    main()
