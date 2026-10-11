#!/usr/bin/env python3
"""Reconstruct the selected fixed-address permutation from public scalar source.

This replays the selected matrix-weighted parent, then conjugates its complete
physical word. It never recompiles the scalar graph using the new physical Q.
The discovery population, cost tables and saved candidate word are unnecessary.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys


PIN = 'ad0f25ff7b23cff7f08ad237c2254e6ecf74257e'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--campaign', type=Path,
                    default=Path(__file__).resolve().parents[3])
    ap.add_argument('--source', type=Path,
                    help='Immutable full PR62 snapshot; fetched with gh if omitted')
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--prepare-only', action='store_true',
                    help='Check the authored closure and emit commands without executing')
    args = ap.parse_args()
    assert not args.work.exists(), 'Use a fresh external execution directory'
    args.work.mkdir(parents=True)
    campaign = args.campaign.resolve()
    graph = campaign / 'agents/graph'
    geometry = campaign / 'agents/geometry'
    scout = campaign / 'agents/scout'
    manifest_path = scout / 'fixtures/fixed-global-order-regeneration-manifest-20261008T2300.json'
    manifest = json.loads(manifest_path.read_text())
    for item in manifest['authored_closure']:
        path = campaign / item['path']
        assert digest(path) == item['sha256'], f'Authored closure mismatch: {path}'
    parent_manifest_path = graph / 'fixtures/matrix-weighted-selected-regeneration-manifest-2210.json'
    assert digest(parent_manifest_path) == manifest['parent_regeneration_manifest']['sha256']
    parent_manifest = json.loads(parent_manifest_path.read_text())
    matching_record = next(item for item in parent_manifest['portable_inputs']
                           if item['path'].endswith('carriers-h25.json'))
    matching = campaign / matching_record['path']
    if not matching.exists():
        recovery = next(item for item in parent_manifest['published_selected_input_recovery']
                        if item['original_path'] == matching_record['path'])
        matching = args.work / 'selected-matching-h25.json'
        matching.write_bytes(gzip.decompress(
            (campaign / recovery['published_complete_gzip']).read_bytes()))
    assert digest(matching) == matching_record['sha256']
    source = args.source.resolve() if args.source else args.work / 'public-pr62'
    native = args.work / 'signed_joint_word_profiles'
    receipt = args.work / 'weighted-parent-source.json'
    output = args.work / 'fixed-global-order-receipt.json'
    commands = []
    if not args.source:
        commands += [
            ['gh', 'repo', 'clone', 'CrocSwap/integer-mult-bounds', str(source), '--', '--no-checkout'],
            ['git', '-C', str(source), 'checkout', '--detach', PIN],
        ]
    commands += [
        ['g++', '-std=c++17', '-O3', str(geometry / 'code/signed_joint_word_profiles.cpp'),
         '-o', str(native)],
        [sys.executable, str(graph / 'code/source_only_matrix_weighted_joint.py'),
         '--source', str(source), '--choices-file',
         str(graph / 'fixtures/joint-common-multifamily-reproduction-2107.json'),
         '--h', '25', '--work', str(args.work / 'weighted-parent'),
         '--output', str(receipt), '--expected-word-sha256',
         '5f4a4496af267f2e44efb0d67cfd450fe14e7ec841cfa457527b814206f78a93',
         '--selected-matching', str(matching)],
        [sys.executable, str(scout / 'code/conjugate_actual_joint_word_order.py'),
         '--graph-receipt', str(receipt), '--order-config',
         str(scout / 'fixtures/fixed-global-order-h25-three-one-zero-two.json'),
         '--checker', str(graph / 'code/joint_word_check_v4.py'),
         '--native', str(native), '--basis', 'beta:-1:15',
         '--work', str(args.work / 'fixed-global-order'), '--output', str(output)],
    ]
    protocol = {
        'classification': 'SELECTED-ONLY REPRODUCTION; complete assembly remains separate',
        'public_source_pin': PIN, 'commands': commands,
        'manifest_sha256': digest(manifest_path),
        'prepare_only': args.prepare_only,
    }
    (args.work / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    if args.prepare_only:
        print(json.dumps({'status': 'PASS PORTABLE CLOSURE AND COMMAND PREPARATION',
                          'commands': len(commands), 'work': str(args.work)}))
        return
    with (args.work / 'reproduction.log').open('x') as log:
        for command in commands:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    result = json.loads(output.read_text())
    assert result['independent']['word_sha256'] == manifest['expected']['word_sha256']
    assert result['transition']['sha256'] == manifest['expected']['transition_sha256']
    assert result['R'] == 36354 and result['independent']['complete_basis_vectors'] == 40954
    print(json.dumps({'status': 'PASS PUBLIC-SOURCE FIXED-GLOBAL-ORDER REPRODUCTION',
                      'receipt': str(output)}))


if __name__ == '__main__':
    main()
