#!/usr/bin/env python3
"""Prepare fresh verifier inputs from source words and native profile files.

Scalar, dirty-word, rational, DATA, stock and assembly checks remain separate.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def write(path, value):
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-receipts', type=Path, nargs=2, required=True)
    parser.add_argument('--profiles', type=Path, nargs=2, required=True)
    parser.add_argument('--audits', type=Path, nargs=2, required=True)
    parser.add_argument('--output-directory', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output_directory.exists()
    args.output_directory.mkdir(parents=True)
    axes, controls = [], []
    for h, source_path, profile_path, audit_path, basis in zip(
            (23, 25), args.source_receipts, args.profiles, args.audits,
            ('beta:1:15', 'beta:-1:15')):
        source_path, profile_path, audit_path = (
            path.resolve() for path in (source_path, profile_path, audit_path))
        source, profile, audit = map(read, (source_path, profile_path, audit_path))
        word = source['independent']
        binary_path = Path(word['transition_path']).resolve()
        assert source['explicit_coframe_allocation'] and source['source_only']
        assert source['h'] == word['h'] == profile['h'] == audit['h'] == h
        assert profile['basis'] == audit['basis'] == basis
        assert digest(binary_path) == word['transition_sha256']
        assert profile['R'] == source['R'] == source['compiled']['roles']
        allocation = read(Path(source['allocation_path']))
        assert profile['blocks'] == allocation['exact_predicted_child_histogram']
        assert profile['rank_sum'] == allocation['physical_rank_mass']
        row = dict(
            config=dict(case_id=f'h{h}-regenerated-selected-source-coframe',
                        basis=basis, transitions=str(binary_path),
                        actual_signed_word_path=source['word_path'],
                        actual_signed_word_sha256=source['word_sha256']),
            profile=profile, profile_path=str(profile_path),
            profile_sha256=digest(profile_path),
            transition_audit=str(audit_path),
            transition_audit_sha256=digest(audit_path),
            input_binary_sha256=digest(binary_path),
            actual_signed_word_path=source['word_path'],
            actual_signed_word_sha256=source['word_sha256'])
        wrapper = dict(
            h=h, coordinate_order=source['source_permutation'], profiles=[row],
            source_only_receipt=str(source_path),
            source_only_receipt_sha256=digest(source_path),
            frame_representation='mixed-signed-complemented-v1',
            classification='EXACT CANDIDATE; independent acceptance required',
            minimum_selected_old_containment=True,
            old_actual_frame_is_upper_bound=True)
        write(args.output_directory / f'axis-{h}.json', wrapper)
        write(args.output_directory / f'word-{h}.json', word)
        axes.append(dict(row, h=h, coordinate_order=source['source_permutation']))
        controls.append(dict(case_id=row['config']['case_id'], basis=basis,
                             binary=str(binary_path), audit=str(audit_path),
                             profile=str(profile_path)))
    write(args.output_directory / 'axes.json', axes)
    write(args.output_directory / 'controls-input.json', controls)
    print(json.dumps(dict(status='PREPARED REGENERATED VERIFIER INPUTS',
                          axes=2, output=str(args.output_directory))))


if __name__ == '__main__':
    main()
