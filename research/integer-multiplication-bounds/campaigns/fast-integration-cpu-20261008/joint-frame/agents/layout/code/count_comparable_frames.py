#!/usr/bin/env python3
"""Count exact comparable original-frame pairs through core/cover bitset joins.

The binary input is the independently certified edge-cost frame dictionary.
No downloaded source is changed and no profile rank is inferred by counting.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import struct
from time import perf_counter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frame-input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    raw = args.frame_input.read_bytes()
    h, _, _, nf, _, _, _, _ = struct.unpack_from('<6I2Q', raw)
    assert h in (23, 25)
    rows = [struct.unpack_from('<2QI', raw, 40+20*i) for i in range(nf)]
    assert rows[:2] == [(0, 0, 0), (0, 0, h)]
    assert len(set(rows[2:])) == nf-2
    started = perf_counter()
    cores = {}
    covers = [0]*h
    ranks = [0]*(h+1)
    for index, (core, cover, rank) in enumerate(rows[2:]):
        assert core and not (core & ~cover)
        flag = 1 << index
        cores[core] = cores.get(core, 0) | flag
        ranks[rank] |= flag
        bits = cover
        while bits:
            bit = bits & -bits
            covers[bit.bit_length()-1] |= flag
            bits ^= bit
    universe = (1 << (nf-2))-1

    def candidates(frame):
        core, cover, _ = frame
        allowed = 0
        subset = core
        while subset:
            allowed |= cores.get(subset, 0)
            subset = (subset-1) & core
        possible = universe
        while cover:
            bit = cover & -cover
            possible &= covers[bit.bit_length()-1]
            cover ^= bit
        return possible & allowed

    counts = Counter()
    largest = 0
    for frame in rows[2:]:
        mask = candidates(frame)
        largest = max(largest, mask.bit_count())
        for rank in range(frame[2]+1, h+1):
            counts[rank-frame[2]] += (mask & ranks[rank]).bit_count()
    # Independent direct semantic predicate on every target for selected rows.
    rng = random.Random(20261008)
    sampled = rng.sample(range(2, nf), 24)
    for index in sampled:
        old = rows[index]
        direct = 0
        for j, target in enumerate(rows[2:]):
            if not (target[0] & ~old[0]) and not (old[1] & ~target[1]):
                direct |= 1 << j
        assert direct == candidates(old)
    result = dict(status='EXACT COMPARABLE ORIGINAL-FRAME COUNT PASS',
                  recorded_utc=datetime.now(timezone.utc).isoformat(), h=h,
                  frame_input_sha256=hashlib.sha256(raw).hexdigest(),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  original_frames=nf-2,
                  strictly_growing_pairs=sum(counts.values()),
                  larger_than_rank_two_pairs=sum(n for r, n in counts.items() if r > 2),
                  counts_by_rank_increment=dict(sorted(counts.items())),
                  largest_compatible_target_set=largest,
                  independent_full_target_scans=len(sampled),
                  native_threads=1, seconds=perf_counter()-started,
                  scope='Exact containment pairs among the supplied original frames. Rational projector ranks, costs and all-size claims require separate profiling. Zero births and final identity cleanups are not included in this count.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
