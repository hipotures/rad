#!/usr/bin/env python3
"""Bind copied-center normalizations to the actual signed-word hyperplanes.

All copied-center descriptors are checked literally. For each selected basis,
one representative projector is independently reconstructed by Fraction Gram
inversion. Permutation covariance gives the other h-1 identical-form identities.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path

from review_positive_physical_profiles import mm, projector


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    rows = []
    for config in json.loads(args.input.read_text()):
        payload = Path(config['word']).read_bytes()
        raw = gzip.decompress(payload)
        word = json.loads(raw)
        h = word['h']
        assert h == config['h'] and word['frame_format'] == 'positive-signed-v1'
        centers = [row for row in word['outputs'] if len(row[3]) == 1]
        assert len(centers) == h
        assert {row[2] for row in centers} == set(range(h))
        for slot, fid, common, target in centers:
            rank, forced, symbols = word['frames'][fid]
            assert target == [common] and rank == h - 1
            assert forced == 1 << common and symbols[common] == 1
            outside = [symbols[i] for i in range(h) if i != common]
            assert all(label > 1 for label in outside)
            assert len(set(outside)) == h - 1
        representative = next(row for row in centers if row[2] == 0)
        rank, forced, symbols = word['frames'][representative[1]]
        checks = []
        for basis in config['bases']:
            _, numerator, denominator = basis.split(':')
            beta = Q(int(numerator), int(denominator))
            c = (2 - 3 * beta * (h - 3)) / (h - 9)
            v = (h - 9) * (1 - 3 * beta) / (12 * (1 - h * beta))
            right = [Q(i == 0) + c for i in range(h)]
            dual = [v - Q(h - 9, 4) * (i == 0) for i in range(h)]
            assert sum(a * b for a, b in zip(right, dual)) == 1
            P = projector(h, forced, tuple(symbols), basis)
            assert mm(P, P) == P
            assert sum(P[i][i] for i in range(h)) == h - 1
            for i in range(h):
                for j in range(h):
                    assert Q(i == j) - P[i][j] == right[i] * dual[j]
            assert all(sum(dual[i] * P[i][j] for i in range(h)) == 0 for j in range(h))
            checks.append(dict(basis=basis, center_offset=str(c), dual_offset=str(v),
                literal_center_frame_rank=h - 1,
                independent_gram_complement_identity=True,
                exact_center_normalization=True))
        rows.append(dict(h=h, actual_center_descriptors_checked=h,
            word_sha256=sha256(raw).hexdigest(), checks=checks))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(
        status='PASS ACTUAL COPIED-CENTER HYPERPLANE AND NORMALIZED COMPLEMENT LINE',
        rows=rows, utc=datetime.now(timezone.utc).isoformat(),
        input_sha256=sha256(args.input.read_bytes()).hexdigest(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        scope='Every actual copied-center endpoint is the full f=1 signed singleton-class '
            'hyperplane. Its complement is exactly the source-center line and normalized '
            'dual used in basis interfaces. Scalar charges and dirty payload restoration '
            'remain separate complete-word gates.'
    ), indent=2) + '\n')


if __name__ == '__main__':
    main()
