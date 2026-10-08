#!/usr/bin/env python3
"""Encode original E(C,M) spaces for the independent integer-basis checker.

This creates a disposable binary label file, never changes the input DAG, and
does not import the producer, matching selector, or projector implementation.
The signed-component encoding gives each outside coordinate its own component.
"""
import argparse
import array
import struct
import sys
from pathlib import Path


def take(data, offset, kind, count):
    values = array.array(kind)
    end = offset + values.itemsize * count
    values.frombytes(data[offset:end])
    assert len(values) == count
    if sys.byteorder != 'little' and values.itemsize > 1:
        values.byteswap()
    return values, end


def encode(dag, output):
    data = dag.read_bytes()
    h, v, n, q = struct.unpack_from('<4I', data)
    args, offset = take(data, 16, 'I', 2*n)
    core, offset = take(data, offset, 'Q', n)
    cover, offset = take(data, offset, 'Q', n)
    ranks = array.array('I', [0])*n
    symbols = array.array('b', [0])*(n*h)
    for node in range(1, n):
        ranks[node] = cover[node].bit_count()-core[node].bit_count() if args[2*node] else 1
        component = 2
        for i in range(h):
            if core[node] >> i & 1:
                symbols[node*h+i] = 1
            elif cover[node] >> i & 1:
                symbols[node*h+i] = component
                component += 1
    assert h < 127
    if sys.byteorder != 'little':
        ranks.byteswap()
        core.byteswap()
    assert not output.exists(), 'Every attempt needs its own output path'
    output.write_bytes(struct.pack('<2I', h, n)+ranks.tobytes()+core.tobytes()+symbols.tobytes())


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dag', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    encode(args.dag, args.output)
