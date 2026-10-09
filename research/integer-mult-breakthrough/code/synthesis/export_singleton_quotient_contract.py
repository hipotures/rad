#!/usr/bin/env python3
"""Export complete source/root chronology and actual paid child adapters.

This is an immutable data contract for independent review, not a native
implementation or an additional circuit search.
"""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import singleton_quotient_copies as producer

PRODUCER_SHA256 = 'b1e3d9688d59a8c1cb78f31063520a3cff226242c8d7bba10d490d595c6e05b9'


def export():
    source = Path(producer.__file__).resolve()
    if sha256(source.read_bytes()).hexdigest() != PRODUCER_SHA256:
        raise AssertionError('The accepted quotient producer changed')
    cases = []
    for k in (1, 3, 5):
        spec = producer.schedule(k)
        adapters = {}
        events = []
        for event in spec['events']:
            retained = dict(event)
            if event['kind'] in ('frame', 'copy-read'):
                key = json.dumps([event['from'], event['to']], separators=(',', ':'))
                if key not in adapters:
                    adapters[key] = producer.normal(tuple(event['from']), tuple(event['to']), spec['h'])
                retained['adapter_key'] = key
            events.append(retained)
        cases.append({
            'k': k, 'selected_width_per_column': spec['h'],
            'source_labels': spec['labels'],
            'source_helper_start': spec['G'], 'quotient_root_start': spec['R'],
            'aggregate_root_start': spec['A'], 'persistent_roles': spec['roles'],
            'source_roles': spec['n'], 'extra_persistent_quotient_roots': spec['q'],
            'source_and_helper_values_are_arbitrary': True,
            'aggregate_buckets': [
                {'coordinate': j, 'bit': bit, 'source_codes': list(codes), 'frame_basis': list(E)}
                for j, bit, codes, E in spec['buckets']],
            'initial_actual_frame_bases': spec['initial'],
            'final_actual_frame_bases': spec['final'],
            'all_chronological_events': events,
            'actual_relative_adapters': adapters,
            'child_histogram_per_column': spec['histogram'],
            'endpoint_baseline_rank': spec['endpoint_baseline_rank'],
            'total_paid_rank_per_column': spec['rank'],
            'paid_rank_above_endpoint_baseline': 2 * k,
            'complete_scalar_operator_audit': producer.scalar_audit(spec)})
    return {
        'schema': 'synchronized-singleton-quotient-contract-v1',
        'generated_utc': datetime.now(timezone.utc).isoformat(),
        'producer_path': 'code/synthesis/singleton_quotient_copies.py',
        'producer_sha256': PRODUCER_SHA256,
        'canonical_actual_frames': 'Pinned F_0=I, F_full=C_h, F_line=C_U; generic F_E is D^-1 P Htilde_dim(E) P^-1 D^-1.',
        'address_convention': 'Bit-major: column c occupies bits h*c through h*c+h-1; all Gaussian fields share the same exact address operator.',
        'copy_semantics': 'Each read owns a complete copy of every signed Gaussian field and common grid. Its actual adapter is F_target F_root^-1. Original roots are retained. Native complete-buffer read/erase and tape geometry are conditional.',
        'persistent_endpoints': 'Original sources and every source helper and quotient root end at F_full; aggregate root j,b ends at its literal F_bucket and gains the sum of source x whose code_j=b. Initial dirty seeds are independent.',
        'inverse': 'Reverse every frame, signed addition and owned-copy read chronologically; negate gates are involutions. No grouped uninject shortcut.',
        'scope': 'Complete finite singleton formation only. Higher-J aggregates, cap continuation, master/side integration and exponent are not supplied.',
        'cases': cases}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('An export must use a fresh output file')
    result = export()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS complete quotient contract export',
                      'cases': len(result['cases']), 'bytes': args.output.stat().st_size,
                      'sha256': sha256(args.output.read_bytes()).hexdigest()}, sort_keys=True))


if __name__ == '__main__':
    main()
