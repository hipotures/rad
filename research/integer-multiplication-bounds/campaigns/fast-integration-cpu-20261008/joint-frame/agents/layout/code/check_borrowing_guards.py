#!/usr/bin/env python3
"""Independent small rational-frame and arbitrary-dirty guard discriminators."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from time import perf_counter


def mask(items):
    return sum(1 << i for i in items)


def contained(source, destination):
    c, u = source
    cc, uu = destination
    return not (cc & ~c) and not (u & ~uu)


def coordinates(bits, h):
    return [i for i in range(h) if bits >> i & 1]


def positive_basis(frame, h):
    """Solve x_C=t, support U, sum(x)=3t directly over the integers."""
    c, u = frame
    common = coordinates(c, h)
    free = coordinates(u & ~c, h)
    if not free:
        assert len(common) == 3
        return [[int(i in common) for i in range(h)]]
    pivot = free[-1]
    first = [0] * h
    for i in common:
        first[i] = 1
    first[pivot] = 3 - len(common)
    rows = [first]
    for i in free[:-1]:
        row = [0] * h
        row[i], row[pivot] = 1, -1
        rows.append(row)
    return rows


def accepts(vector, frame):
    c, u = frame
    first = (c & -c).bit_length() - 1
    value = vector[first]
    return (all(not x or u >> i & 1 for i, x in enumerate(vector))
            and all(x == value for i, x in enumerate(vector) if c >> i & 1)
            and sum(vector) == 3 * value)


def exact_inclusion(source, destination, h):
    return all(accepts(row, destination) for row in positive_basis(source, h))


def frames(h):
    result = []
    for size in (1, 2):
        for core in itertools.combinations(range(h), size):
            remaining = [i for i in range(h) if i not in core]
            for extra_size in range(1, len(remaining) + 1):
                for extra in itertools.combinations(remaining, extra_size):
                    result.append((mask(core), mask(core + extra)))
    for triple in itertools.combinations(range(h), 3):
        result.append((mask(triple), mask(triple)))
    return result


def dirty_controls():
    # Roles are source x, target y, and two arbitrary scratch values a,b.
    # L:a^=b, J:y^=a, V:b^=x give JLV=I on x.
    word = [(2, 3), (1, 2), (2, 3), (3, 0),
            (2, 3), (1, 2), (2, 3), (3, 0)]
    initial = [1 << i for i in range(4)]
    expected = [initial[0], initial[1] ^ initial[0], initial[2], initial[3]]

    def execute(gates):
        values = initial.copy()
        for a, b in gates:
            values[a] ^= values[b]
        return values

    assert execute(word) == expected
    missing_old_dirty_scatter = execute(word[:1] + word[2:])
    missing_last_injection = execute(word[:-1])
    assert missing_old_dirty_scatter != expected
    assert missing_last_injection != expected
    assert missing_last_injection[1] == expected[1]
    assert missing_last_injection[2:] != expected[2:]
    return dict(basis_columns=4, complete_wrapper_pass=True,
                missing_first_scatter_output=missing_old_dirty_scatter,
                missing_final_injection_output=missing_last_injection,
                expected=expected)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--word', help='Optional completed word for shape discriminator')
    args = parser.parse_args()
    output = Path(args.output)
    assert not output.exists()
    output.parent.mkdir(parents=True, exist_ok=True)
    started = perf_counter()
    checks = []
    for h in (4, 5):
        choices = frames(h)
        geometric_pairs = 0
        guarded_pairs = 0
        conservative_misses = 0
        for source in choices:
            for destination in choices:
                actual = exact_inclusion(source, destination, h)
                simple = contained(source, destination)
                if simple:
                    assert actual
                    guarded_pairs += 1
                geometric_pairs += actual
                conservative_misses += actual and not simple
        checks.append(dict(h=h, frames=len(choices), ordered_pairs=len(choices)**2,
                           guarded_pairs=guarded_pairs, geometric_pairs=geometric_pairs,
                           conservative_misses=conservative_misses))

    # The current frame is accepted by G, but the terminal frame H is smaller.
    f = (mask((0, 1)), mask((0, 1, 2, 3)))
    g = (mask((0,)), mask((0, 1, 2, 3)))
    terminal = f
    assert contained(f, g) and not contained(g, terminal)
    assert exact_inclusion(f, g, 4) and not exact_inclusion(g, terminal, 4)
    witness = next(row for row in positive_basis(g, 4) if not accepts(row, terminal))
    assert accepts(witness, g) and not accepts(witness, terminal)

    result = dict(status='PASS', seconds=perf_counter()-started,
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  exact_rational_frame_checks=checks,
                  ignored_terminal_guard_negative=dict(current=f, borrowing=g,
                      terminal=terminal, illegal_future_vector=witness),
                  dirty_controls=dirty_controls(),
                  limitation='Independent local geometric and restoration controls; not a full native-address execution or recurrence certificate.')
    if args.word:
        raw = Path(args.word).read_bytes()
        word = json.loads(raw)
        degenerate = sum(c.bit_count() == 2 and u.bit_count() == 3
                         for c, u in word['frames'])
        result['completed_word_shape'] = dict(h=word['h'], word_sha256=hashlib.sha256(raw).hexdigest(),
                                              equivalent_core_pair_triple_frames=degenerate,
                                              interpretation='The simplest omitted exact equal-space containment requires these frames; absence rules out this local canonicalization gain.')
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
