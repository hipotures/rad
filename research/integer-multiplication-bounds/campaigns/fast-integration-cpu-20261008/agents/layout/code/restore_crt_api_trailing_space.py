#!/usr/bin/env python3
"""Restore one historical source byte without whitespace in the Git patch.

The original compiled CRT API's inverse-check line ended in one space. A
later cosmetic cleanup removes it. This helper recreates the exact executed
snapshot in an ignored reproduction file and checks its receipt hash.
"""
import argparse
import hashlib
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--path', required=True)
parser.add_argument('--expected-sha256', required=True)
args = parser.parse_args()
path = Path(args.path)
lines = path.read_text().splitlines(keepends=True)
matches = [j for j, line in enumerate(lines) if "machine.inverse();assert machine.payload==initial" in line]
assert len(matches) == 1
j = matches[0]
lines[j] = lines[j].rstrip(' \t\r\n') + ' ' + '\n'
source = ''.join(lines)
assert hashlib.sha256(source.encode()).hexdigest() == args.expected_sha256
path.write_text(source)
print(args.expected_sha256)
