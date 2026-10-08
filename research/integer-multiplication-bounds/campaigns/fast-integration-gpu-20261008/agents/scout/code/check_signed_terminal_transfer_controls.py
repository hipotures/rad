#!/usr/bin/env python3
"""Reconstruct signed sink kernels and reject dimension-preserving bad signs."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path

from signed_positive_frame_interfaces import columns, contained, includes, normalize, ordinary_frame


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def terminal_projector(frame, beta):
    rows = columns(frame)
    h = len(rows[0])
    star = (1 - 9 * beta) / (9 * (1 - h * beta))
    sums = list(map(sum, rows))
    norms = []
    for a, x in enumerate(rows):
        norm = sum(z * z for z in x) - F(sums[a] * sums[a], 9)
        assert norm > 0
        norms.append(norm)
        for b, y in enumerate(rows):
            if a != b:
                assert sum(u * v for u, v in zip(x, y)) - F(sums[a] * sums[b], 9) == 0
    left = [[F(z) - beta * sums[a] for z in row] for a, row in enumerate(rows)]
    right = [[F(z) - star * sums[a] for z in row] for a, row in enumerate(rows)]
    return [[sum(left[a][i] * right[a][j] / norms[a] for a in range(len(rows)))
             for j in range(h)] for i in range(h)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--graphs', nargs=2, type=Path, required=True)
    ap.add_argument('--beta23', type=F, required=True)
    ap.add_argument('--beta25', type=F, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    axes = []
    for graph_path in args.graphs:
        graph = json.loads(graph_path.read_text())
        word_path = Path(graph['word_path'])
        raw = gzip.decompress(word_path.read_bytes())
        assert hashlib.sha256(raw).hexdigest() == graph['word_sha256']
        word = json.loads(raw)
        h = word['h']
        assert h in (23, 25) and word['frame_format'] == 'positive-signed-v1'
        beta = args.beta23 if h == 23 else args.beta25
        frames = list(map(normalize, word['frames']))
        ordinary = [row for row in word['outputs'] if len(row[3]) == 3]
        assert len(ordinary) == 3 * word['v']
        checked = 0
        for _, fid, common, target in ordinary:
            frame = frames[fid]
            a, b = sorted(set(target) - {common})
            d = tuple(int(i == a) - int(i == b) for i in range(h))
            old = ordinary_frame(common, {a, b}, h)
            assert frame[0] == h - 2 and frame[1] == 1 << common
            assert contained(old, frame) and includes(d, frame)
            assert all(3 * sum(row[i] for i in target) == sum(row) for row in columns(frame))
            assert sum(d) == d[common] == 0 and sum(x * x for x in d) == 2
            assert all(sum(x * y for x, y in zip(row, d)) == 0 for row in columns(old))
            checked += 1
        sampled = sorted({0, len(ordinary) // 3, 2 * len(ordinary) // 3, len(ordinary) - 1})
        controls = []
        for index in sampled:
            _, fid, common, target = ordinary[index]
            a, b = sorted(set(target) - {common})
            d = tuple(int(i == a) - int(i == b) for i in range(h))
            new = terminal_projector(frames[fid], beta)
            old = terminal_projector(ordinary_frame(common, {a, b}, h), beta)
            assert all(new[i][j] - old[i][j] == F(d[i] * d[j], 2)
                       for i in range(h) for j in range(h))
            controls.append({'ordinary_output_index': index, 'common': common,
                             'target': target, 'exact_projector_difference_entries': h * h})
        _, fid, common, target = ordinary[0]
        frame = frames[fid]
        a, b = sorted(set(target) - {common})
        symbols = list(frame[2])
        assert symbols[a] == -symbols[b] and abs(symbols[a]) > 1
        symbols[a] = symbols[b] = abs(symbols[a])
        bad = frame[0], frame[1], tuple(symbols)
        bad_columns = columns(bad)
        assert len(bad_columns) == frame[0]
        assert contained(ordinary_frame(common, {a, b}, h), bad)
        assert any(3 * sum(row[i] for i in target) != sum(row) for row in bad_columns)
        invalid_rank = (frame[0] + 1, frame[1], frame[2])
        try:
            columns(invalid_rank)
        except AssertionError:
            pass
        else:
            raise AssertionError('Incorrect rank declaration was accepted')
        axes.append({'h': h, 'beta': str(beta), 'graph_receipt_sha256': digest(graph_path),
                     'word_sha256': graph['word_sha256'], 'ordinary_kernels_reconstructed': checked,
                     'projector_difference_controls': controls,
                     'adversarial_same_rank_same_original_envelope_bad_sink_sign': 'REJECTED',
                     'adversarial_inconsistent_rank_declaration': 'REJECTED'})
    assert {row['h'] for row in axes} == {23, 25}
    result = {'utc': datetime.now(timezone.utc).isoformat(), 'status': 'PASS SIGNED TERMINAL TRANSFER AND ADVERSARIAL CONTROLS',
              'source_sha256': digest(Path(__file__)),
              'signed_helper_sha256': digest(Path(__file__).with_name('signed_positive_frame_interfaces.py')),
              'axes': axes,
              'scope': 'All ordinary actual terminal spaces; eight exact rational projector differences; dimension-preserving bad-sign controls. Full literal word, dirty restoration, local transition CRT and complete recurrence assembly are separate gates.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'ordinary_kernels': sum(row['ordinary_kernels_reconstructed'] for row in axes),
                      'exact_matrix_entries': sum(c['exact_projector_difference_entries'] for row in axes for c in row['projector_difference_controls'])}))


if __name__ == '__main__':
    main()
