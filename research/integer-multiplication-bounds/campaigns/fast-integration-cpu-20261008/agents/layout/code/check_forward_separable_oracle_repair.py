#!/usr/bin/env python3
"""Compare the exact axis-sum repair to the previous full-cell Gaussian sum."""
import argparse
import hashlib
import importlib.util
import json
from decimal import Decimal
from pathlib import Path
from time import perf_counter


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


parser = argparse.ArgumentParser()
parser.add_argument('--producer', required=True)
parser.add_argument('--legacy', required=True)
parser.add_argument('--config', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()
out = Path(args.output)
out.mkdir(parents=True, exist_ok=False)
new = load('repaired_forward_oracle', args.producer)
old = load('previous_forward_oracle', args.legacy)
small = {'name': 'exact-separable-vs-dense-oracle-control', 'source_shape': [251, 253],
         'target_side': 256, 'side': 16, 'radius': 7, 'alpha': '0.75',
         'shift': 0, 'cell_indices': [2, 7], 'seed': 202610102901}
started = perf_counter()
before = old.run_case(small)
after = new.run_case(small)
differences = []
for a, b in zip(before['outputs'], after['outputs']):
    assert a['local_target'] == b['local_target']
    difference = abs(Decimal(a['reference']) - Decimal(b['reference']))
    assert difference < Decimal('1e-125'), difference
    assert a['packed'] == b['packed']
    differences.append(str(difference))
control = {'status': 'bounded dense and distributive oracles agree', 'before': before,
           'after': after, 'reference_absolute_differences': differences,
           'seconds': perf_counter() - started,
           'legacy_sha256': hashlib.sha256(Path(args.legacy).read_bytes()).hexdigest()}
(out / 'repair-control.json').write_text(json.dumps(control, indent=2) + '\n')
rows = []
for i, config in enumerate(json.loads(Path(args.config).read_text())):
    row = new.run_case(config)
    rows.append(row)
    (out / f'row-{i}.json').write_text(json.dumps(row, indent=2) + '\n')
result = {'status': 'separable oracle repair and changed L128 cases passed',
          'control': control, 'rows': rows,
          'producer_sha256': hashlib.sha256(Path(args.producer).read_bytes()).hexdigest(),
          'wrapper_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'scope': 'rank-two input family; packed convolution still executes the entire tensor cell'}
(out / 'certificate.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'status': result['status'], 'seconds': [r['seconds'] for r in rows]}))
