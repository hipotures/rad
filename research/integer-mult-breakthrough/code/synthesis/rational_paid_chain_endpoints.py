#!/usr/bin/env python3
"""Constructive minimum/maximum rational frames for a fixed paid-chain cut.

Ideal concave child moments are certified by integer power bounds. New Gram
denominators, exceptional classes and native routing remain separately paid.
"""

from fractions import Fraction as Q
from functools import lru_cache

from rational_frame_completion import complete, contained, radical, rref


def endpoint_frames(V, U, G):
    """Both attained dimension endpoints, or the exact shared-radical obstruction."""
    result = complete(V, U, G)
    if result['minimal_dimension'] is None:
        return result
    h = len(G)
    lower, unused = rref(V, h)
    upper, unused = rref(U, h)
    R = radical(upper, G)
    maximum = list(lower)
    span, unused = rref(list(maximum) + list(R), h)
    for row in upper:
        extended, unused = rref(list(span) + [row], h)
        if len(extended) > len(span):
            maximum.append(row)
            span = extended
    maximum, unused = rref(maximum, h)
    if (len(maximum) != len(upper) - len(R) or radical(maximum, G)
            or not contained(lower, maximum, h) or not contained(maximum, upper, h)):
        raise AssertionError('The exact maximum nondegenerate complement failed')
    result.update(maximum_completion=maximum, maximum_dimension=len(maximum), upper_radical=R)
    return result


def widths(dimension, previous_dimensions, next_dimensions):
    if len(previous_dimensions) != len(next_dimensions):
        raise ValueError('One previous and next frame per participating role is required')
    values = []
    for before, after in zip(previous_dimensions, next_dimensions):
        if not 0 <= before <= dimension <= after:
            raise ValueError('The local frame lies outside its chronological dimension interval')
        values.extend([dimension - before, after - dimension])
    return tuple(value for value in values if value)


@lru_cache(maxsize=None)
def power_interval(rank, numerator=999, denominator=1000, bits=48):
    """Exact enclosing interval for rank**(numerator/denominator)."""
    if rank < 0 or not 0 < numerator <= denominator or bits < 1:
        raise ValueError('Nonnegative rank, exponent in (0,1], and positive grid precision required')
    if rank == 0:
        return Q(0), Q(0)
    grid = 1 << bits
    target = pow(rank, numerator) * pow(grid, denominator)
    low, high = 0, rank * grid + 1
    while high - low > 1:
        middle = (low + high) // 2
        if pow(middle, denominator) <= target:
            low = middle
        else:
            high = middle
    if pow(low, denominator) == target:
        value = Q(low, grid)
        return value, value
    return Q(low, grid), Q(high, grid)


def moment_interval(rank_widths, numerator=999, denominator=1000, bits=48):
    bounds = [power_interval(rank, numerator, denominator, bits) for rank in rank_widths]
    return sum((bound[0] for bound in bounds), Q(0)), sum((bound[1] for bound in bounds), Q(0))


def cleared_basis(rows):
    """Explicit integer basis and every row denominator; no prime fee is hidden."""
    from math import gcd, lcm
    integer_rows, denominators = [], []
    for row in rows:
        denominator = 1
        for entry in row:
            denominator = lcm(denominator, Q(entry).denominator)
        values = [int(Q(entry) * denominator) for entry in row]
        common = 0
        for value in values:
            common = gcd(common, abs(value))
        # Retain the original clearing denominator even if primitive normalization shrinks it.
        if common > 1:
            values = [value // common for value in values]
        integer_rows.append(tuple(values))
        denominators.append(denominator)
    return tuple(integer_rows), tuple(denominators)
