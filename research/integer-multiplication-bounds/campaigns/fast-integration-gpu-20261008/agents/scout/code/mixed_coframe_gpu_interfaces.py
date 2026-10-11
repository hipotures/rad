"""Strict RADCOF01 input and independently checked coframe matrix interfaces.

Only matrix construction changes. CUDA ordered-rank elimination is inherited
unchanged from the validated signed-word kernel. Discovery scores are not
rational certificates or physical compiler proofs.
"""
from fractions import Fraction as F
from pathlib import Path
import struct
import sys

import numpy as np

from gpu_signed_complete_word_loci import (
    CUDA, actual_matrix, cpu_pivots, digest, stamp,
    base_matrix as signed_base_matrix,
)

FLAG = 1 << 63
geometry_code = Path(__file__).resolve().parents[2] / 'geometry' / 'code'
sys.path.insert(0, str(geometry_code))
from review_positive_physical_profiles import (
    projector as signed_exact_projector, inverse, mm,
)


def read_binary(path):
    raw = path.read_bytes()
    assert raw[:8] == b'RADCOF01', 'Mixed codec must not be treated as signed-v1'
    h, v, roles, nf, nt, singles, mass, loss = struct.unpack_from('<6I2Q', raw, 8)
    assert h in (23, 25)
    offset, frames = 48, []
    for fid in range(nf):
        forced, rank = struct.unpack_from('<QI', raw, offset)
        symbols = struct.unpack_from('<' + str(h) + 'b', raw, offset + 12)
        core = forced & ~FLAG
        assert core < (1 << h) and rank <= h
        if forced & FLAG:
            assert fid >= 2 and core.bit_count() == 1
            assert all(symbols[i] == 1 for i in range(h) if core >> i & 1)
            assert all(symbols[i] == 0 or abs(symbols[i]) >= 2
                       for i in range(h) if not core >> i & 1)
            normal_rank = len({abs(x) for x in symbols if abs(x) > 1})
            assert rank == h-1-normal_rank
        frames.append((rank, forced, symbols))
        offset += 12+h
    assert frames[:2] == [(0, 0, (0,)*h), (h, 0, (0,)*h)]
    transitions = [struct.unpack_from('<IIq', raw, offset+16*i) for i in range(nt)]
    assert offset+16*nt == len(raw)
    assert all(0 <= a < nf and 0 <= b < nf and count > 0
               and frames[b][0] > frames[a][0] for a, b, count in transitions)
    assert sum((frames[b][0]-frames[a][0])*count
               for a, b, count in transitions)+singles == mass
    return h, v, roles, singles, mass, loss, frames, transitions


def base_matrix(frame, h, prime):
    rank, forced, symbols = frame
    if not forced & FLAG:
        return signed_base_matrix(frame, h, prime)
    core = forced & ~FLAG
    normal_rank = len({abs(x) for x in symbols if abs(x) > 1})
    assert rank == h-1-normal_rank and core.bit_count() == 1
    gamma_symbols = tuple(1 if core >> i & 1 else i+2 for i in range(h))
    gamma = signed_base_matrix((h-1, core, gamma_symbols), h, prime)
    normal = signed_base_matrix((normal_rank, core, symbols), h, prime)
    return (gamma-normal) % prime


def source_span_columns(h, core, symbols):
    """Construct the actual space directly, without subtracting projectors.

The normal partition imposes sum(sigma_i*x_i)=0 on each component.
Choose an independent kernel basis on the outside coordinates, then lift
it into Gamma_c by setting x_c=sum(outside)/2. This checks the complement
formula against a separate primitive Gram inverse.
"""
    assert core.bit_count() == 1
    common = core.bit_length()-1
    groups = {}
    columns = []
    for i, symbol in enumerate(symbols):
        if i == common:
            assert symbol == 1
        elif symbol == 0:
            column = [F(0)]*h
            column[i], column[common] = F(2), F(1)
            columns.append(column)
        else:
            assert abs(symbol) >= 2
            groups.setdefault(abs(symbol), []).append((i, 1 if symbol > 0 else -1))
    for group in groups.values():
        anchor, anchor_sign = group[0]
        for i, sign in group[1:]:
            column = [F(0)]*h
            column[i], column[anchor] = F(2*anchor_sign), F(-2*sign)
            column[common] = F(anchor_sign-sign)
            columns.append(column)
    assert len(columns) == h-1-len(groups)
    for column in columns:
        assert sum(column) == 3*column[common]
        assert all(sum(sign*column[i] for i, sign in group) == 0
                   for group in groups.values())
    return columns


def projector(h, forced, symbols, basis):
    if not forced & FLAG:
        return signed_exact_projector(h, forced, symbols, basis)
    core = forced & ~FLAG
    cols = source_span_columns(h, core, symbols)
    if not cols:
        return [[F(0)]*h for _ in range(h)]
    _, numerator, denominator = basis.split(':')
    beta = F(int(numerator), int(denominator))
    star = (1-9*beta)/(9*(1-h*beta))
    assert beta+star-h*beta*star == F(1, 9)
    gram = [[sum(x*y for x, y in zip(a, b))-sum(a)*sum(b)/9
             for b in cols] for a in cols]
    assert all(gram[i][i] > 0 for i in range(len(cols)))
    inverse_gram = inverse(gram)
    primal = [[x-beta*sum(col) for x in col] for col in cols]
    dual = [[x-star*sum(col) for x in col] for col in cols]
    B = [list(row) for row in zip(*primal)]
    out = mm(mm(B, inverse_gram), dual)
    assert sum(out[i][i] for i in range(h)) == len(cols)
    return out
