#!/usr/bin/env python3
"""Independent exact Gram and ordered-pivot controls for signed joint words.

This verifier constructs projectors by rational Gram inversion, independently
of the native closed formula. The input contains actual signed word frames,
not their original envelopes. Full physical-word reconstruction and the full
prime-product rank certificate remain separate acceptance gates.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import lcm
from pathlib import Path
import struct
import time

from review_positive_physical_profiles import mm, projector


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--samples', type=int, default=32)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    started = time.monotonic()
    results = []
    for config in json.loads(args.input.read_text()):
        packed = Path(config['binary']).read_bytes()
        h, vertices, roles, nf, nt, singles, mass, loss = struct.unpack_from('<6I2Q', packed)
        assert len(packed) == 40 + (12 + h) * nf + 16 * nt
        frames = []
        for fid in range(nf):
            offset = 40 + (12 + h) * fid
            forced, rank = struct.unpack_from('<QI', packed, offset)
            symbols = struct.unpack_from(f'<{h}b', packed, offset + 12)
            frames.append((forced, symbols, rank))
        audit = json.loads(Path(config['audit']).read_text())
        assert audit['h'] == h and audit['basis'] == config['basis']
        rows = audit['transitions']
        chosen = []
        signatures = set()
        for row in sorted(rows, key=lambda x: (x['prime_count'], x['rank'], int(x['entry_bound'])), reverse=True):
            a, b = frames[row['a']], frames[row['b']]
            signature = (a[0].bit_count(), b[0].bit_count(), row['rank'],
                sum(x < -1 for x in a[1]), sum(x < -1 for x in b[1]))
            if signature not in signatures:
                chosen.append(row)
                signatures.add(signature)
            if len(chosen) >= args.samples // 2:
                break
        for key in (lambda x: (x['rank'] == 2, x['count']), lambda x: x['count']):
            for row in sorted(rows, key=key, reverse=True):
                if row not in chosen:
                    chosen.append(row)
                if len(chosen) >= args.samples:
                    break
            if len(chosen) >= args.samples:
                break
        cache = {}
        checks = []
        for row in chosen:
            for fid in (row['a'], row['b']):
                if fid not in cache:
                    forced, symbols, rank = frames[fid]
                    if fid == 0:
                        P = [[Q(0) for j in range(h)] for i in range(h)]
                    elif fid == 1:
                        P = [[Q(i == j) for j in range(h)] for i in range(h)]
                    else:
                        P = projector(h, forced, symbols, config['basis'])
                    assert mm(P, P) == P
                    assert sum(P[i][i] for i in range(h)) == rank
                    cache[fid] = P
            A, B = cache[row['a']], cache[row['b']]
            assert mm(A, B) == A and mm(B, A) == A
            M = [[b - a for a, b in zip(u, v)] for u, v in zip(A, B)]
            assert mm(M, M) == M
            assert sum(M[i][i] for i in range(h)) == row['rank']
            den = lcm(*(x.denominator for P in (A, B) for values in P for x in values))
            assert den == int(row['integer_denominator'])
            Z = max(abs(x * den) for values in M for x in values)
            assert Z.denominator == 1 and Z == int(row['entry_bound'])
            bound = row['rank'] ** ((row['rank'] + 1) // 2) * int(Z) ** row['rank']
            assert bound == int(row['minor_bound'])
            E = [values[:] for values in M]
            pivots = []
            for i in range(h):
                nonzero = [j for j in range(h) if E[i][j]]
                if not nonzero:
                    continue
                j = nonzero[-1]
                pivots.append([i, j])
                for k in range(i + 1, h):
                    scale = E[k][j] / E[i][j]
                    if scale:
                        for column in range(j + 1):
                            E[k][column] -= scale * E[i][column]
            assert pivots == row['pivots']
            checks.append(dict(a=row['a'], b=row['b'], rank=row['rank'], count=row['count'],
                exact_pivots=pivots, independent_gram_pass=True,
                nested_idempotent_pass=True, integer_minor_bound_pass=True))
            status = dict(utc=datetime.now(timezone.utc).isoformat(), case=config['case_id'],
                completed_controls=len(checks), total_controls=len(chosen),
                completed=len(results), elapsed_seconds=time.monotonic() - started)
            (args.work / 'status.json').write_text(json.dumps(status, indent=2) + '\n')
            print(json.dumps(status), flush=True)
        results.append(dict(case=config, checks=checks,
            audit_sha256=sha256(Path(config['audit']).read_bytes()).hexdigest(),
            binary_sha256=sha256(packed).hexdigest()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(
        status='PASS INDEPENDENT EXACT SIGNED JOINT WORD GRAM AND ORDERED-PIVOT CONTROLS',
        rows=results, completed_utc=datetime.now(timezone.utc).isoformat(),
        elapsed_seconds=time.monotonic() - started,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        gram_source_sha256=sha256(Path(__file__).with_name('review_positive_physical_profiles.py').read_bytes()).hexdigest(),
        input_sha256=sha256(args.input.read_bytes()).hexdigest(),
        scope='Actual signed frames independently reconstructed by Fraction Gram inversion, '
            'with exact idempotence, nesting, ordered pivots and integer minor bounds. '
            'Full native CRT and complete physical compiler/source/data/moment binding remain separate.'
    ), indent=2) + '\n')


if __name__ == '__main__':
    main()
