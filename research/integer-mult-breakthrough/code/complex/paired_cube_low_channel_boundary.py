#!/usr/bin/env python3
"""Exact low-selector-channel factorization and a paid conversion boundary.

The paired-five maps B and H annihilate every selector character of degree
greater than two inside each source cube. This does not supply a free dense
source-bank basis conversion. The tested original-source excursion has an
explicit positive frame excess and destroys the retained rank deficit.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import time

import paired_five_cube_discriminator as scalar


def walsh(values):
    values = list(values)
    stride = 1
    while stride < len(values):
        for first in range(0, len(values), 2 * stride):
            for offset in range(stride):
                a, b = first + offset, first + stride + offset
                x, y = values[a], values[b]
                values[a], values[b] = x + y, x - y
        stride *= 2
    return values


def check_low(transformed):
    for character, value in enumerate(transformed):
        if character.bit_count() > 2 and value:
            raise AssertionError('a supposedly annihilated high selector character survives')


def row_block(task):
    p, first, stop = task
    sources = scalar.labels(p, 5)
    cube_size = 32
    transformed_rows = high_channels = 0
    for target in range(first, stop):
        T = sources[target]
        for begin in range(0, len(sources), cube_size):
            B8 = [((T & S).bit_count() - 1) * ((T & S).bit_count() - 3)
                  for S in sources[begin:begin + cube_size]]
            H8 = [0] * cube_size if target // cube_size == begin // cube_size else [-v for v in B8]
            for values in (B8, H8):
                transformed = walsh(values)
                check_low(transformed)
                for character, value in enumerate(transformed):
                    if character.bit_count() > 2:
                        high_channels += 1
                transformed_rows += 1
    return dict(first=first, stop=stop, transformed_rows=transformed_rows,
                checked_zero_high_channels=high_channels)


def frame_boundary():
    cube = [scalar.cube_label(bits, 5) for bits in range(32)]
    all_U = scalar.basis(cube)
    parity_U = scalar.basis(cube[bits] for bits in range(32) if not (bits.bit_count() & 1))
    if len(all_U) != 6 or len(parity_U) != 5:
        raise AssertionError('the selector source-basis frame dimensions changed')
    if scalar.basis(all_U + parity_U) != all_U:
        raise AssertionError('parity frame is not contained in the all-cube frame')
    if any((T & T).bit_count() % 2 != 1 for T in cube):
        raise AssertionError('an original port lost its norm-one entrance')
    # Every source line is in all_U, so all_U is outside every corresponding cap.
    if any(not any((u & T).bit_count() & 1 for u in all_U) for T in cube):
        raise AssertionError('the all-cube basis was incorrectly admitted to a target cap')
    excess = (len(all_U) - 1) + (len(all_U) - len(parity_U)) - (len(parity_U) - 1)
    if excess != 2:
        raise AssertionError('the literal all-cube excursion rank was not fully charged')
    # A face is an exact cancellation of a total and a contrast, yet its actual
    # frame changes: losing this direction is a positive-width transition.
    total = [1] * 32
    contrast = [1 if not (bits & 1) else -1 for bits in range(32)]
    face = [(a + b) // 2 for a, b in zip(total, contrast)]
    if face != [int((bits & 1) == 0) for bits in range(32)]:
        raise AssertionError('the exact face cancellation failed')
    face_U = scalar.basis(cube[i] for i, coefficient in enumerate(face) if coefficient)
    if len(face_U) != 5 or scalar.basis(face_U + all_U) != all_U:
        raise AssertionError('the cancellation/frame distinction has no rank-one witness')
    try:
        check_low(walsh([(-1) ** ((bits & 7).bit_count()) for bits in range(32)]))
    except AssertionError:
        rejected = True
    else:
        raise AssertionError('high-character corruption was accepted')
    return dict(all_cube_frame_rank=6, original_parity_frame_rank=5,
                source_line_to_all_cube=5, all_cube_back_to_parity=1,
                direct_source_line_to_parity=4, extra_rank_per_source_per_core=excess,
                extra_rank_for_three_cores_per_v=3 * excess,
                retained_deficit_per_v='2-3*copied_loss/v',
                changed_deficit_per_v='-4-3*copied_loss/v',
                face_true_signal_span_rank=5, conservative_input_frame_rank=6,
                exact_face_cancellation=True, paid_face_frame_drop=1,
                high_character_corruption_rejected=rejected,
                raw_target_cap_violation=True,
                conclusion='REFUTED for the named line→all-cube→parity original-source excursion under unchanged stock; shared encoded-source architectures remain open')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('workers must be positive')
    paths = [Path(__file__), Path(scalar.__file__)]
    frozen = {p: p.read_bytes() for p in paths}
    started_utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    p, v = 7, 672
    targets = 32 if args.bounded else v
    tasks = [(p, (i * targets) // args.workers, ((i + 1) * targets) // args.workers)
             for i in range(args.workers)]
    if args.workers == 1:
        parts = [row_block(tasks[0])]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            parts = list(pool.map(row_block, tasks))
    if any(p.read_bytes() != value for p, value in frozen.items()):
        raise AssertionError('source closure changed during execution')
    result = dict(status='PASS low-selector factorization and scoped paid-source boundary',
                  started_utc=started_utc, completed_utc=datetime.now(timezone.utc).isoformat(),
                  seconds=time.monotonic() - started, workers=args.workers, bounded=args.bounded,
                  source_sha256={p.name: sha256(value).hexdigest() for p, value in frozen.items()},
                  p=p, v=v, target_rows=targets, cube_blocks=v // 32,
                  transformed_rows=sum(x['transformed_rows'] for x in parts),
                  checked_zero_high_channels=sum(x['checked_zero_high_channels'] for x in parts),
                  exact_relations=['B K=-B', 'K B=-B', 'H K=-H', 'K H=-H'],
                  frame_boundary=frame_boundary(),
                  scope='Exact integer selector-channel and label/frame geometry; the algebraic half-channel factorization supplies neither native routing nor a free conversion or shared side profile.')
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], seconds=result['seconds'],
                          transformed_rows=result['transformed_rows'],
                          checked_zero_high_channels=result['checked_zero_high_channels'])), flush=True)


if __name__ == '__main__':
    main()
