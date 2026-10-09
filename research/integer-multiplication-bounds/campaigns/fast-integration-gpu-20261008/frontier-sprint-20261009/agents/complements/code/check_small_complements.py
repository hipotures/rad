#!/usr/bin/env python3
"""Exhaustive small GF(2)^4 complement check against independent rank arithmetic."""
import argparse
import importlib.util
from itertools import combinations
import json
from pathlib import Path
from screen_complements import MODES, alternate_part, check_part

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--source', required=True, type=Path)
p.add_argument('--output', required=True, type=Path)
a = p.parse_args()
s = importlib.util.spec_from_file_location('upstream', a.source / 'research/deferred-replayed/complex_deferred.py')
u = importlib.util.module_from_spec(s)
s.loader.exec_module(u)
spaces = {u.sat_basis(vs) for vs in combinations(range(1, 16), 3)}
records, counts, checked = [], {m: 0 for m in MODES}, 0
for B in sorted(spaces):
    if len(B) != 3 or u.sat_nondeg(B):
        continue
    control = u.sat_nonsingular_part(B)
    row = {'intersection': B, 'control': control, 'variants': {}}
    for mode in MODES[1:]:
        z = alternate_part(u, B, mode, 20261009)
        check_part(B, z)
        row['variants'][mode] = z
        counts[mode] += z != control
    checked += 1
    if any(tuple(z) != control for z in row['variants'].values()):
        records.append(row)
result = {'ambient_dimension': 4, 'checked_degenerate_dimension_three_spaces': checked,
          'changed_subspaces_by_mode': counts, 'first_witnesses': records[:3]}
a.output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
