"""Independent integer subspace checks for actual signed positive frames.

For c forced coordinates, each signed component has outside coefficient
3-c and forced coefficient equal to its signed cardinality. Thus every
column satisfies sum(x)=3*x_common. Components have disjoint nonempty
outside supports, proving linear independence and strict positivity of
the sum of squares away from the common coordinate.
"""
from functools import lru_cache


def normalize(frame):
    assert len(frame) == 3
    r, forced, symbols = frame
    assert type(r) is int and type(forced) is int
    assert all(type(x) is int for x in symbols)
    return r, forced, tuple(symbols)


@lru_cache(maxsize=None)
def columns(frame):
    r, forced, symbols = frame
    h = len(symbols)
    assert 0 < forced < 1 << h and 0 < r < h
    fixed = tuple(i for i in range(h) if forced >> i & 1)
    assert len(fixed) in (1, 2, 3)
    assert all(symbols[i] == 1 for i in fixed)
    if len(fixed) == 3:
        assert r == 1 and symbols == tuple(int(i in fixed) for i in range(h))
        return (symbols,)
    assert all(symbols[i] == 0 or abs(symbols[i]) >= 2 for i in range(h) if i not in fixed)
    labels = sorted({abs(symbols[i]) for i in range(h) if i not in fixed and symbols[i]})
    assert len(labels) == r
    result = []
    for label in labels:
        signs = tuple(1 if x == label else -1 if x == -label else 0 for x in symbols)
        cardinality = sum(signs)
        row = tuple(cardinality if i in fixed else (3 - len(fixed)) * signs[i] for i in range(h))
        assert sum(row) == 3 * row[fixed[0]]
        assert sum(x * x for i, x in enumerate(row) if i != fixed[0]) > 0
        result.append(row)
    return tuple(result)


def includes(vector, frame):
    _, forced, symbols = frame
    fixed = tuple(i for i in range(len(symbols)) if forced >> i & 1)
    if len(fixed) == 3:
        return all(x == (vector[fixed[0]] if i in fixed else 0) for i, x in enumerate(vector))
    value = vector[fixed[0]]
    if sum(vector) != 3 * value or any(vector[i] != value for i in fixed):
        return False
    coefficients = {}
    for i, symbol in enumerate(symbols):
        if i in fixed:
            continue
        if symbol == 0:
            if vector[i] != 0:
                return False
        else:
            coefficient = vector[i] if symbol > 0 else -vector[i]
            previous = coefficients.setdefault(abs(symbol), coefficient)
            if previous != coefficient:
                return False
    return True


@lru_cache(maxsize=300000)
def contained(a, b):
    return all(includes(vector, b) for vector in columns(a))


def ordinary_frame(common, omitted, h):
    forced = 1 << common
    symbols = tuple(1 if i == common else 0 if i in omitted else i + 2 for i in range(h))
    return h - 1 - len(omitted), forced, symbols
