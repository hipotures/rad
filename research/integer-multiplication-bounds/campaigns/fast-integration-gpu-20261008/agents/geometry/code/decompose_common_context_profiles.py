#!/usr/bin/env python3
"""Reconstruct complete paid child histograms separately by common context.

Native audit tables cover every rank >=2 matrix except the literal identity.
Rank-one transitions, the identity, and every side-growth singleton are read
independently from actual transition bytes and output descriptors. The summed
histogram must equal the complete certified native output exactly.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
import math
from pathlib import Path
import struct


def pivot_run_histogram(pivots, count=1):
    """Return the native contiguous NE-pivot runs, including multiplicity.

    Pivots are ordered by increasing row. A run continues exactly when both
    coordinates increase by one. This agrees with the executed native
    certification; northeast rank alone does not determine these run widths.
    """
    result = Counter()
    previous = None
    run = 0
    for pivot in pivots:
        assert len(pivot) == 2
        if previous is not None:
            assert pivot[0] > previous[0]
        if (previous is not None and pivot[0] == previous[0] + 1
                and pivot[1] == previous[1] + 1):
            run += 1
        else:
            if run:
                result[run] += count
            run = 1
        previous = pivot
    if run:
        result[run] += count
    assert sum(width * multiplicity for width, multiplicity in result.items()) == len(pivots) * count
    return result


def contexts(binary, word_path, audit_path, profile_path):
    data = Path(binary).read_bytes()
    h, _, _, nf, nt, singles, _, _ = struct.unpack_from('<6I2Q', data)
    assert len(data) == 40 + nf * (12 + h) + nt * 16
    frames = [struct.unpack_from('<QI', data, 40 + i * (12 + h)) for i in range(nf)]
    audit = json.loads(Path(audit_path).read_text())
    table = {(row['a'], row['b']): row for row in audit['transitions']}
    histograms = [Counter() for _ in range(h + 1)]
    offset = 40 + nf * (12 + h)
    used = set()
    for i in range(nt):
        a, b, count = struct.unpack_from('<2Iq', data, offset + i * 16)
        commons = {forced.bit_length() - 1 for forced, rank in (frames[a], frames[b])
                   if forced.bit_count() == 1 and rank}
        assert len(commons) <= 1, 'Actual transition crosses independent common contexts'
        context = next(iter(commons)) if commons else h
        rank = frames[b][1] - frames[a][1]
        if rank == 1:
            histograms[context][1] += count
        elif (a, b) == (0, 1):
            histograms[context][h] += count
        else:
            row = table[a, b]
            assert row['count'] == count and row['rank'] == rank
            used.add((a, b))
            assert len(row['pivots']) == rank
            histograms[context].update(pivot_run_histogram(row['pivots'], count))
    assert used == table.keys()
    word = json.loads(gzip.decompress(Path(word_path).read_bytes()))
    side = 0
    for slot, frame, common, target in word['outputs']:
        if len(target) == 3:
            count = h - word['frames'][frame][0]
            histograms[common][1] += count
            side += count
    assert side == singles
    total = Counter()
    for histogram in histograms:
        total.update(histogram)
    profile = json.loads(Path(profile_path).read_text())
    assert [total[t] for t in range(h + 1)] == profile['blocks']
    return [[histogram[t] for t in range(h + 1)] for histogram in histograms]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--next-config', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists() and not args.next_config.exists()
    rows, next_configs = [], []
    for config in json.loads(args.input.read_text()):
        h = config['h']
        a = config.get('screen_a', 1284995399 / 25000000000000)
        histograms = {name: contexts(**case) for name, case in config['variants'].items()}
        global_histogram = next(iter(histograms.values()))[h]
        assert all(rows[h] == global_histogram for rows in histograms.values())
        costs = {name: [sum(t * n * math.expm1(a * math.log(575 / t))
                            for t, n in enumerate(row) if t and n) for row in rows]
                 for name, rows in histograms.items()}
        choices = [min(costs, key=lambda name: costs[name][common]) for common in range(h)]
        chosen_histogram = [sum(histograms[choices[c]][c][t] for c in range(h))
                            + global_histogram[t] for t in range(h + 1)]
        row = dict(h=h, screen_a=a, costs=costs, choices=choices,
                   independently_reconstructed_histograms=histograms,
                   predicted_actual_histogram=chosen_histogram,
                   predicted_screen_Phi=sum(min(costs[name][c] for name in costs)
                                            for c in range(h)) + next(iter(costs.values()))[h])
        rows.append(row)
        next_configs.append(dict(case_id=f'h{h}-common-weighted-core18-balanced12',
                                 parent=config['parent'], basis=config['basis'],
                                 choices=choices, screen_a=a))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.next_config.parent.mkdir(parents=True, exist_ok=True)
    args.next_config.write_text(json.dumps(next_configs, indent=2) + '\n')
    args.output.write_text(json.dumps(dict(status='DISCOVERY COMMON-CONTEXT COST RECONSTRUCTION',
        rows=rows, source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_sha256=sha256(args.input.read_bytes()).hexdigest(),
        completed_utc=datetime.now(timezone.utc).isoformat(),
        scope='Independent complete histogram decomposition from actual words and '
              'CRT audits. Screening choices use floating moments only. A mixed '
              'literal word, full native profile and independent acceptance binder '
              'are required before any conditional exponent claim.'), indent=2) + '\n')
    print(json.dumps([dict(h=row['h'], choices=row['choices'],
                          predicted_Phi=row['predicted_screen_Phi']) for row in rows]), flush=True)


if __name__ == '__main__':
    main()
