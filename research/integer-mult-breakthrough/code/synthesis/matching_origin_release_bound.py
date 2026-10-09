#!/usr/bin/env python3
"""Origin-color obstruction for a restricted cover-matching center release.

General nonlinear matching frames are allowed. The conclusion still requires
whole-payload scalar side transfers of total width h-2 and closed full-width
central releases. Address-dependent intertwiners and dynamic births are open.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import time

import signed_zeta_matching_boundaries as matching


MATCHING_SHA = '17e5450553bb08b77683526006f7f8920b2d26c9ffb7e93f29280bea4fd5fefd'


def action(vector, pairs, coefficient=Fraction(1)):
    out = list(vector)
    for low, high in pairs:
        out[high] = coefficient*vector[low] - vector[high]
    return out


def probe(h):
    started = time.monotonic()
    if sha256(Path(matching.__file__).read_bytes()).hexdigest() != MATCHING_SHA:
        raise AssertionError('Pinned matching generator changed')
    size = 1 << h; matches = matching.cover_matchings(h)
    classes = Counter(); origin = [Fraction(a == 0) for a in range(size)]
    full = matching.full_matrix(h); tested_pairs = 0; weighted_cases = 0
    first = {}
    for index, pairs in enumerate(matches):
        pair = next((low, high) for low, high in pairs if low == 0)
        coordinate = pair[1]
        if coordinate.bit_count() != 1:
            raise AssertionError('Origin pair is not a Boolean cover edge')
        classes[coordinate] += 1; first.setdefault(coordinate, index)
    for left, pairs in enumerate(matches):
        left_coordinate = next(high for low, high in pairs if low == 0)
        for right, other in enumerate(matches):
            right_coordinate = next(high for low, high in other if low == 0)
            if left_coordinate != right_coordinate:
                continue
            vector = action(action(origin, pairs), other)
            if vector != origin:
                raise AssertionError('Same-color involutions did not cancel the complete origin column')
            returned = [sum(c*x for c, x in zip(row, vector)) for row in full]
            if returned != [Fraction(1)]*size:
                raise AssertionError('Full origin response has an omitted nonzero sector')
            tested_pairs += 1
    # A triangular involution [[1,0],[c,-1]] with arbitrary dyadic c
    # cannot defeat the color obstruction: the lower i-sector remains 1.
    weights = [Fraction(1), Fraction(-1), Fraction(2), Fraction(1, 2), Fraction(3, 2)]
    for coordinate, index in first.items():
        pairs = matches[index]
        for left_weight in weights:
            for right_weight in weights:
                vector = action(action(origin, pairs, left_weight), pairs, right_weight)
                returned = [sum(c*x for c, x in zip(row, vector)) for row in full]
                expected = [Fraction(1) if not a & coordinate
                            else 1-(right_weight-left_weight) for a in range(size)]
                if returned != expected or sum(bool(x) for x in returned) < size//2:
                    raise AssertionError('Weighted origin-sector proof failed')
                if sum(bool(x) for x in returned) <= size//4:
                    raise AssertionError('A weighted same-color side reached its forbidden h-2 width')
                weighted_cases += 1
    v = len(matches); q_lower = max(classes.values())
    if h*q_lower < v:
        raise AssertionError('Origin-color pigeonhole bound failed')
    return dict(status='PASS COVER MATCHING ORIGIN RELEASE BOUND', h=h,
                all_cover_matching_labels=v, origin_color_sizes=dict(sorted(classes.items())),
                same_color_ordered_pairs_verified=tested_pairs,
                arbitrary_dyadic_weight_controls=weighted_cases,
                closed_center_rank_lower=q_lower,
                endpoint_saving=2*v, closed_full_center_loss_lower=2*h*q_lower,
                maximum_possible_closed_release_deficit=2*v-2*h*q_lower,
                all_size_proof='Every cover matching pairs origin0 with some e_i. Same-color T_N T_M e0=e0, so F T_N T_M e0 has 2^h nonzeros. Weighted triangular involutions retain at least2^(h-1) nonzeros. Either exceeds the 2^(h-2) branching limit for a whole-payload geodesic side. Every color class is an identity fitting minor; rankK>=max class>=v/h.',
                source_sha256=MATCHING_SHA,
                scope='Arbitrary nonlinear cover matching labels and constant whole-payload complex central coefficients, under h-2 side width and closed full-width center release. Not arbitrary address-dependent intertwiners, other endpoint words or dynamic/reused central lifecycles.',
                seconds=time.monotonic()-started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__), Path(matching.__file__)]
    hashes = {source.name: sha256(source.read_bytes()).hexdigest() for source in sources}
    cases = [3, 4]
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    native_threads_each=1, cases=cases, seed=None, stdlib_only=True,
                    source_sha256=hashes,
                    hypothesis='Nonlinear cover matching anchors escape global coordinate labels but a same-origin color identity minor may still forbid a closed full-width center-release deficit.',
                    resource_preflight=dict(aggregate_memory_bytes_upper=64*1024*1024))
    (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(probe, h) for h in cases]; results = []
        for future in as_completed(futures):
            result = future.result(); results.append(result)
            print(json.dumps(result), flush=True)
    if any(sha256(source.read_bytes()).hexdigest() != hashes[source.name] for source in sources):
        raise AssertionError('Effective origin-bound source changed during execution')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results), indent=2)+'\n')


if __name__ == '__main__':
    main()
