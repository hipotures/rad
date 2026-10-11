#!/usr/bin/env python3
"""Content signatures for actual signed transition spaces, independent of aliases.

Only explicit signed class permutation and whole-column sign changes are
identified. Equal signatures certify the same ordered matrix profiles for every
admissible beta, subject to the SHA256 collision assumption. Scalar source and
dirty-state semantics remain independent obligations.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

from compare_signed_word_transition_spaces import canonical


def signature(path):
    header, transitions = canonical(Path(path))
    hashed_header = {key: header[key] for key in
                     ('h', 'vertices', 'roles', 'singles', 'rank_mass', 'loss')}
    digest = sha256()
    digest.update(b'signed-B-column-space-v1\n')
    digest.update(json.dumps(hashed_header, sort_keys=True,
                             separators=(',', ':')).encode() + b'\n')
    rows = [(json.dumps(a, separators=(',', ':')),
             json.dumps(b, separators=(',', ':')), count)
            for (a, b), count in transitions.items() if count]
    for a, b, count in sorted(rows):
        digest.update(f'{a}\t{b}\t{count}\n'.encode())
    return dict(header, canonical_signature_sha256=digest.hexdigest(),
                distinct_weighted_transitions=len(rows), binary_path=str(path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, nargs='+', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    rows = []
    representatives = {}
    paths = []
    for entry in args.input:
        if entry.is_file():
            paths.append(entry)
        else:
            for receipt in sorted(entry.glob('raw/*/result.json')):
                document = json.loads(receipt.read_text())
                if 'PASS' not in document.get('status', '').upper():
                    continue
                binary = receipt.with_name('signed-transitions.bin')
                if binary.exists():
                    paths.append(binary)
    for path in dict.fromkeys(paths):
        row = signature(path)
        key = row['canonical_signature_sha256']
        row['profile_reuse_reference'] = representatives.get(key)
        representatives.setdefault(key, str(path))
        rows.append(row)
        print(json.dumps(dict(binary_path=str(path), signature=key,
                              equivalent_to=row['profile_reuse_reference'])), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(
        status='COMPLETE EXACT SIGNED SPACE SIGNATURE MANIFEST', rows=rows,
        unique_signatures=len(representatives),
        completed_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        canonicalizer_sha256=sha256(Path(__file__).with_name(
            'compare_signed_word_transition_spaces.py').read_bytes()).hexdigest(),
        scope='Header and complete weighted frame-transition multiset; explicit '
              'signed column permutation and sign identities only. Equal spaces '
              'permit matrix profile reuse at the same coherent coordinate order '
              'and rational beta. Scalar charges, source/data compatibility and '
              'dirty-state gates require separate proof.'), indent=2) + '\n')


if __name__ == '__main__':
    main()
