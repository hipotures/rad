#!/usr/bin/env python3
"""Independent global cyclic-band inverse reference and precision receipts."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from random import Random
from time import perf_counter

import mpmath as mp

parser = argparse.ArgumentParser()
parser.add_argument('--api', required=True)
parser.add_argument('--config', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()
output = Path(args.output)
output.mkdir(parents=True, exist_ok=False)
spec = importlib.util.spec_from_file_location('frozen_cyclic_reference', args.api)
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)
source_hash = hashlib.sha256(Path(args.api).read_bytes()).hexdigest()
rows = []
for index, config in enumerate(json.loads(Path(args.config).read_text())):
    started = perf_counter()
    reference = api.CyclicGaussianReference(config['s'], config['t'], config['alpha'], config['bits'])
    rng = Random(config['seed'])
    rhs = [mp.mpf(rng.randrange(-8, 9)) / 64 for _ in range(config['s'])]
    solution = reference.solve(rhs)
    receipt = reference.residual_certificate(rhs, solution)
    assert receipt['solution_error_upper'] < receipt['target'], receipt
    row = {'config': config, 'status': 'global cyclic-band inverse residual passed',
           'receipt': {name: str(value) if hasattr(value, '_mpf_') else value for name, value in receipt.items()},
           'api_sha256': source_hash, 'seconds': perf_counter() - started,
           'limitations': ['numerical coefficients with analytic all-alias tail, not directed interval proof',
                           'out-of-theorem u*theta rows remain labeled explicitly']}
    (output / f'row-{index}.json').write_text(json.dumps(row, indent=2) + '\n')
    rows.append(row)
result = {'status': 'cyclic inverse reference family passed', 'rows': rows,
          'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(output / 'certificate.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'status': result['status'], 'seconds': [row['seconds'] for row in rows]}))
