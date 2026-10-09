#!/usr/bin/env python3
"""Both zero-border conventions and the input-coordinate scope boundary."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time

import singer_prefix_routes as s


def zero_first(degree):
    polynomial, powers = s.primitive_cycle(degree)
    mapping = [0]+powers
    checked = 0
    for width in range(2, degree+1):
        for start in range(0, len(mapping), 1 << width):
            failed = s.affine_witness(mapping, start, width) is not None
            if failed != (degree >= 3):
                raise AssertionError('Zero-first prefix-affine boundary failed')
            checked += 1
    return dict(degree=degree, primitive_polynomial=polynomial,
                zero_first_chunks=checked, positive_boundary=(degree == 2))


def input_coordinate_control():
    # Arbitrary precomposition can move a prefix cube to a non-axis plane.
    polynomial, powers = s.primitive_cycle(4)
    mapping = powers+[0]
    for a in range(1, 16):
        for b in range(1, a):
            vertices = [0, a, b, a ^ b]
            images = [mapping[i] for i in vertices]
            if s.xor_all(images) == 0:
                # Distinct nonzero a,b extend to a binary input basis; their
                # distinct image differences extend to an output basis.
                if len(set(images)) != 4:
                    raise AssertionError('The affine-plane counterexample is not injective')
                return dict(degree=4, primitive_polynomial=polynomial,
                            input_plane=vertices, output_plane=images,
                            arbitrary_input_linear_change_not_excluded=True)
    raise AssertionError('The input-coordinate scope counterexample was not found')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--bounded', action='store_true')
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    if not 1 <= a.workers <= 16 or (a.output and a.output.exists()):
        raise ValueError('Invalid worker count or reused output path')
    degrees = [2, 3, 4] if a.bounded else [2, 3, 6, 8, 10, 12]
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        cases = list(pool.map(zero_first, degrees))
    # The bounded registered entrypoint also replays the original zero-last
    # cube product formula and corruption controls.
    zero_last = [s.check(n) for n in [2, 3, 4]]
    files = [Path(__file__), Path(s.__file__)]
    result = dict(status='PASS BOTH SINGER ZERO-BORDER CONTROLS',
                  recorded_utc=datetime.now(timezone.utc).isoformat(),
                  workers=a.workers, zero_first_cases=cases,
                  zero_last_cases=zero_last, input_scope_control=input_coordinate_control(),
                  source_sha256={str(f): sha256(f.read_bytes()).hexdigest() for f in files},
                  seconds=time.perf_counter()-started,
                  scope='Both zero placements forbid direct aligned prefix-affine routing at degree>=3. An explicit prelinear input-plane counterexample prevents overgeneralization. No native route or time lower bound.')
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        with a.output.open('x') as f:
            f.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'workers', 'seconds', 'scope')}))


if __name__ == '__main__':
    main()
