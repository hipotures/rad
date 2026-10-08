#!/usr/bin/env python3
"""Independent primitive endpoint controls for actual signed terminal frames."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path

from signed_positive_frame_interfaces import columns, normalize, ordinary_frame
from check_signed_terminal_transfer_controls import terminal_projector


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def gram(x, y):
    return sum(a * b for a, b in zip(x, y)) - F(sum(x) * sum(y), 9)


def conjugate_vector(x, beta):
    return [F(a) - beta * sum(x) for a in x]


def projector(x, beta, star):
    left = conjugate_vector(x, beta)
    right = conjugate_vector(x, star)
    norm = gram(x, x)
    assert norm != 0
    return [[a * b / norm for b in right] for a in left]


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
        raw = gzip.decompress(Path(graph['word_path']).read_bytes())
        assert hashlib.sha256(raw).hexdigest() == graph['word_sha256']
        word = json.loads(raw)
        assert word['frame_format'] == 'positive-signed-v1'
        h = word['h']
        beta = args.beta23 if h == 23 else args.beta25
        star = (1 - 9 * beta) / (9 * (1 - h * beta))
        gamma = (9 * beta - 1) / (3 * (1 - h * beta))
        frames = list(map(normalize, word['frames']))
        ordinary = [r for r in word['outputs'] if len(r[3]) == 3]
        checked_columns = 0
        ranks = {}
        for _, fid, common, target in ordinary:
            s = tuple(int(i in target) for i in range(h))
            z = tuple(F(i == common) + F(2, h - 9) for i in range(h))
            assert common in target and gram(s, s) == 2
            assert gram(z, z) == F(-4, h - 9) and gram(s, z) == 0
            dual = [F(i in target, 2) + gamma / 2 for i in range(h)]
            assert dual == [a / 2 for a in conjugate_vector(s, star)]
            source = conjugate_vector(s, beta)
            assert sum(a * b for a, b in zip(source, dual)) == 1
            frame = frames[fid]
            ranks[frame[0]] = ranks.get(frame[0], 0) + 1
            for x in columns(frame):
                assert gram(x, s) == gram(x, z) == 0
                checked_columns += 1
        controls = []
        for index in sorted({0, len(ordinary) // 3, 2 * len(ordinary) // 3, len(ordinary) - 1}):
            _, fid, common, target = ordinary[index]
            a, b = sorted(set(target) - {common})
            symbols = tuple(1 if i == common else 2 if i == a else -2 if i == b else i + 3
                            for i in range(h))
            maximal = (h - 2, 1 << common, symbols)
            s = tuple(int(i in target) for i in range(h))
            z = tuple(F(i == common) + F(2, h - 9) for i in range(h))
            d = tuple(int(i == a) - int(i == b) for i in range(h))
            pk = terminal_projector(maximal, beta)
            pe = terminal_projector(ordinary_frame(common, {a, b}, h), beta)
            ps = projector(s, beta, star)
            pz = projector(z, beta, star)
            assert all(F(i == j) - pk[i][j] == ps[i][j] + pz[i][j]
                       for i in range(h) for j in range(h))
            assert all(F(i == j) - pe[i][j] == ps[i][j] + pz[i][j] + F(d[i] * d[j], 2)
                       for i in range(h) for j in range(h))
            # The scalar annihilation and orthogonality above also cover partial frames.
            # Only their actual projector and complementary rank may be used downstream.
            controls.append({'ordinary_index': index, 'common': common, 'target': target,
                             'actual_selected_rank': frames[fid][0],
                             'maximal_endpoint_matrix_entries': h * h,
                             'original_endpoint_matrix_entries': h * h})
        _, _, common, target = ordinary[0]
        wrong = next(i for i in range(h) if i not in target)
        s = tuple(int(i in target) for i in range(h))
        bad_center = tuple(F(i == wrong) + F(2, h - 9) for i in range(h))
        assert gram(s, bad_center) == -1
        assert gram(s, bad_center) != 0
        axes.append({'h': h, 'beta': str(beta), 'conjugate': str(star),
                     'graph_receipt_sha256': digest(graph_path), 'word_sha256': graph['word_sha256'],
                     'ordinary_output_count': len(ordinary), 'actual_rank_counts': ranks,
                     'all_actual_terminal_columns_annihilated': checked_columns,
                     'exact_endpoint_matrix_controls': controls,
                     'adversarial_center_outside_source_triple': 'REJECTED: exact Gram product -1'})
    assert {r['h'] for r in axes} == {23, 25}
    result = {'utc': datetime.now(timezone.utc).isoformat(),
              'status': 'PASS EXACT PRIMITIVE SOURCE AND CENTER ENDPOINT DECOMPOSITION',
              'source_sha256': digest(__file__),
              'helper_sha256': digest(Path(__file__).with_name('signed_positive_frame_interfaces.py')),
              'projector_control_source_sha256': digest(Path(__file__).with_name('check_signed_terminal_transfer_controls.py')),
              'axes': axes,
              'scope': 'All literal ordinary terminal columns, normalized source/target identity, primitive orthogonality, eight exact full endpoint matrices and adversarial wrong-center controls. No deletion of executed operations, no claim of unchanged ordered child widths, no exponent certificate.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'ordinary_outputs': sum(r['ordinary_output_count'] for r in axes),
                      'actual_columns': sum(r['all_actual_terminal_columns_annihilated'] for r in axes)}))


if __name__ == '__main__':
    main()
