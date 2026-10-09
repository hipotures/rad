#!/usr/bin/env python3
"""Stable independent rational moment kernel for the signed-lane receipts.

Retained unchanged from the separate RaD baseline lane's independent_arithmetic.py
moment functions, initially observed at SHA256
02e55816eaa74847f488069cab4144f0a8f44a4240351b1bde5d125e2679f182.
The full baseline utility continues evolving; only the required kernel is
retained here. Method also follows the supplied arithmetic supplement.
Authored by RaD with OpenAI Codex assistance, Apache-2.0. No producer imported.
"""
from fractions import Fraction as Q
from math import factorial

DEN = 1 << 180


def need(condition, message):
    if not condition:
        raise ValueError(message)


def down(x):
    return Q(x.numerator*DEN//x.denominator, DEN)


def up(x):
    return Q(-((-x.numerator*DEN)//x.denominator), DEN)


def log_unit(x):
    need(1 <= x <= 2, 'log range')
    z = (x-1)/(x+1)
    low = sum((2*z**(2*k+1)/Q(2*k+1) for k in range(40)), Q(0))
    return down(low), up(low+2*z**81/(81*(1-z*z)))


def log_bounds(x):
    need(x >= 1, 'log argument')
    k = 0
    while x > 2:
        x /= 2; k += 1
    lo, hi = log_unit(x); l2, h2 = log_unit(Q(2))
    return down(lo+k*l2), up(hi+k*h2)


def exp_bounds(lo, hi):
    need(0 <= lo <= hi < 1, 'exp range')
    low = sum((lo**k/Q(factorial(k)) for k in range(10)), Q(0))
    high = sum((hi**k/Q(factorial(k)) for k in range(10)), Q(0))
    return down(low), up(high+hi**10/Q(factorial(10))/(1-hi/11))


def moment(m, W, hist, saving):
    lo = hi = Q(0)
    for width, count in hist.items():
        need(type(width) is int and type(count) is int and 0 < width < m and count > 0, 'child domain')
        l, h = log_bounds(Q(m, width)); el, eh = exp_bounds(saving*l, saving*h)
        weight = Q(width*count, m*W)
        lo += weight*el; hi += weight*eh
    return down(lo), up(hi)
