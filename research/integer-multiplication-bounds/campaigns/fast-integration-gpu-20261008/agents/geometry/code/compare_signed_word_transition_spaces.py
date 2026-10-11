#!/usr/bin/env python3
"""Compare actual signed transition spaces modulo class naming and sign.

Flipping every sign in one signed class multiplies its entire B column by -1,
including its signed-sum core coefficient. Relabeling classes permutes columns.
Both operations preserve the exact rational projector for every admissible beta.
This test proves equality only through these explicit allowed identities.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import struct


def canonical(path):
    packed = path.read_bytes()
    h, vertices, roles, nf, nt, singles, mass, loss = struct.unpack_from('<6I2Q', packed)
    assert len(packed) == 40 + (12 + h) * nf + 16 * nt
    frames = [('ZERO',), ('IDENTITY',)]
    for fid in range(2, nf):
        offset = 40 + fid * (12 + h)
        forced, rank = struct.unpack_from('<QI', packed, offset)
        symbols = struct.unpack_from(f'<{h}b', packed, offset + 12)
        classes = {}
        normalized = []
        for symbol in symbols:
            if abs(symbol) <= 1:
                normalized.append(symbol)
                continue
            if abs(symbol) not in classes:
                classes[abs(symbol)] = (len(classes) + 2, 1 if symbol > 0 else -1)
            label, first_sign = classes[abs(symbol)]
            normalized.append(label * first_sign * (1 if symbol > 0 else -1))
        frames.append((forced, rank, tuple(normalized)))
    transitions = Counter()
    offset = 40 + (12 + h) * nf
    for i in range(nt):
        a, b, count = struct.unpack_from('<2Iq', packed, offset + i * 16)
        transitions[(frames[a], frames[b])] += count
    return dict(h=h, vertices=vertices, roles=roles, singles=singles,
        rank_mass=mass, loss=loss, input_sha256=sha256(packed).hexdigest(),
        serialized_frames=nf, canonical_frames=len(set(frames))), transitions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--left', type=Path, required=True)
    parser.add_argument('--right', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    left, A = canonical(args.left)
    right, B = canonical(args.right)
    same_header = all(left[key] == right[key]
        for key in ('h', 'vertices', 'roles', 'singles', 'rank_mass', 'loss'))
    equal = same_header and A == B
    receipt = dict(status='PASS SIGNED TRANSITION SPACE EQUIVALENCE'
        if equal else 'SIGNED TRANSITION SPACE DIFFERENCE FOUND',
        equivalent_for_every_admissible_beta=equal,
        left=left, right=right, differing_weighted_transition_terms=len(A - B) + len(B - A),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        scope='Complete actual frame-transition multiset compared modulo explicit '
            'signed-class column sign and order changes. Physical-word scalar charges '
            'and source/dirty semantics remain separate receipts.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
