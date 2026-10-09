#!/usr/bin/env python3
"""Bounded frozen component replay, with effective source/config binding."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', required=True,
                        choices=['scan-order', 'scan-bit', 'zeta', 'matching', 'origin'])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    base = Path(__file__).resolve().parents[2]
    if args.case == 'scan-order':
        import two_order_scan_channels as producer
        argument, config_name = (3, 'bit_reverse'), 'two-order-scan-ci.json'
    elif args.case == 'scan-bit':
        import constant_bit_scan_channels as producer
        argument, config_name = (3, 'end_swap'), 'constant-bit-scan-ci.json'
    elif args.case == 'zeta':
        import subset_zeta_primitive_screen as producer
        argument, config_name = (4, 2), 'subset-zeta-primitive-ci.json'
    elif args.case == 'matching':
        import signed_zeta_matching_boundaries as producer
        argument, config_name = ('cover', 3), 'signed-zeta-matching-boundaries-ci.json'
    else:
        import matching_origin_release_bound as producer
        argument, config_name = 3, 'matching-origin-release-bound-ci.json'
    config_path = base/'configs/synthesis'/config_name
    config = json.loads(config_path.read_text())
    pins = dict(config.get('effective_source_closure', {}))
    if 'source' in config:
        pins[config['source']] = config['source_sha256']
    if 'dependency' in config:
        pins[config['dependency']] = config['dependency_sha256']
    def digest(q):
        return hashlib.sha256(q.read_bytes()).hexdigest()
    for relative, expected in pins.items():
        assert digest(base/relative) == expected, relative
    inputs = {**pins, 'configs/synthesis/'+config_name: digest(config_path)}
    fixture = None
    if args.case == 'matching':
        fixture_path = base/config['fixture']
        inputs[config['fixture']] = digest(fixture_path)
        fixture = json.loads(fixture_path.read_text())
    wrapper = Path(__file__)
    wrapper_hash = digest(wrapper)
    protocol = {'started_utc': datetime.now(timezone.utc).isoformat(),
                'case': args.case, 'argument': argument,
                'producer_inputs_sha256': inputs, 'wrapper_sha256': wrapper_hash,
                'scope': config['scope']}
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    result = producer.probe(argument)
    assert result['status'] == config['expected_status']
    if args.case.startswith('scan-'):
        assert result['exact_channel_dimension'] == 26
        assert result['complete_channels_verified'] == 26
        assert not result['inverse_native_word_supplied']
        assert not result['best_scalar_gaussian_dyadic_invertible']
    elif args.case == 'zeta':
        assert result['C_factorization_entries_compared'] == 256
        assert result['point_star_identity_minor_sizes'] == [3]*4
        assert result['candidate_deficit'] == 0
        assert not result['native_Z_supplier_supplied']
    elif args.case == 'matching':
        assert result['matching_count'] == config['expected_matching_count']
        assert result['all_matching_physical_columns'] == config['expected_physical_columns']
        assert result['optimistic_common_matching_deficit'] == config['expected_deficit']
        assert fixture is not None
        assert fixture['producer_source_sha256'] == pins[config['source']]
        assert not fixture['native_matching_router_proven']
        for case in fixture['cases']:
            h = case['h']
            pairs = case['source_matching']['pairs']
            identity = producer.identity(1 << h)
            F = producer.full_matrix(h)
            assert case['F_matrix'] == F
            assert case['T_M_matrix'] == producer.right_matching(identity, pairs)
            complement = producer.right_matching(F, pairs)
            assert case['complement_matrix'] == complement
            word = identity
            for child in case['complement_operator_word_left_to_right']:
                word = producer.right_matching(word, child['pairs'])
            assert word == complement
    else:
        assert sorted(result['origin_color_sizes'].values()) == config['expected_color_sizes']
        assert result['same_color_ordered_pairs_verified'] == config['expected_same_color_ordered_pairs']
        assert result['maximum_possible_closed_release_deficit'] == config['expected_closed_release_deficit_upper']
    for relative, expected in inputs.items():
        assert digest(base/relative) == expected, relative
    assert digest(wrapper) == wrapper_hash
    summary = {'status': 'PASS FROZEN EXTENDED ZETA COMPONENT',
               'protocol': protocol, 'result': result, 'inputs_unchanged': True,
               'scope': config['scope']}
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({'status': summary['status'], 'case': args.case}))


if __name__ == '__main__':
    main()
