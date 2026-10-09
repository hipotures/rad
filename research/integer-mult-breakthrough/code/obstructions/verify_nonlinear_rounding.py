#!/usr/bin/env python3
"""Bounded literal replay of the noncanonical unitary rounding family.

This uses the frozen producer API and verifies its complete scope controls;
it is not an independent operator implementation or a native algorithm.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


TOPIC = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    source = TOPIC/'code/transfers/unitary_rounding_depth.py'
    config = TOPIC/'configs/transfers/unitary-rounding-depth.json'
    paths = [Path(__file__).resolve(), source, config]
    before = {str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest() for p in paths}
    task = (3, 'nonlinear_conjugate', 64, 8)
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                    effective_inputs=before, task=task,
                    scope='Producer replay of bounded nonlinear complete-bank rounding controls; '
                          'not independent operator synthesis, native time or an exponent.')
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    spec = importlib.util.spec_from_file_location('nonlinear_rounding_producer', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.probe(task)
    matrix = result['matrix_certificate']
    if result['family'] != 'nonlinear_conjugate' or result['Gaussian_fields'] != 4:
        raise AssertionError('The declared nonlinear family and all Gaussian fields are required')
    if not matrix['completed_endpoint_unitary'] or matrix['direct_C_target_verified']:
        raise AssertionError('This endpoint is unitary and has its separate noncanonical target')
    if matrix['all_physical_bank_columns'] != 16 or matrix['all_Gaussian_Gram_entries'] != 64:
        raise AssertionError('Every bounded physical column and endpoint Gram entry must be retained')
    if result['premature_zero_bank_projection'] != 'REJECTED ON RETAINED BANK':
        raise AssertionError('Early projection must corrupt the retained data in this control')
    if any(sha256((TOPIC/p).read_bytes()).hexdigest() != digest for p, digest in before.items()):
        raise AssertionError('An effective input changed during bounded replay')
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(status='PASS NONLINEAR UNITARY ROUNDING REPLAY',
                          full_bank_columns=16, Gaussian_fields=4,
                          numerical_contract_only=True, new_exponent=False)))


if __name__ == '__main__':
    main()
