#!/usr/bin/env python3
"""Exact Q sample comparison keeping each actual permutation fixed."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work-root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    assert not args.output.exists()
    source = Path(__file__).with_name('gpu_basis_parameter_vectorized.py')
    spec = importlib.util.spec_from_file_location('counterfactual_gpu_source', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = args.work_root/'derived/scout'
    inputs = [root/'gpu-basis-20261008T1507-device0/candidate-001.json',
              root/'gpu-basis-gamma-20261008T1538-device0/candidate-001.json',
              root/'gpu-basis-gamma-20261008T1538-device0/candidate-002.json',
              root/'gpu-basis-gamma-20261008T1538-device1/candidate-001.json']
    permutations = [('inherited_baseline', module.base.upstream.baseline(), None)]
    for path in inputs:
        value = json.loads(path.read_text())
        permutations.append((str(path), np.asarray(value['permutations'], np.int32),
                             hashlib.sha256(path.read_bytes()).hexdigest()))
    pairs = [('negative_both', (F(2, 39), F(1, 21))),
             ('negative23_gamma_half25', (F(2, 39), F(1, 57))),
             ('negative23_IplusJ25', (F(2, 39), F(-1))),
             ('gamma_half_both', (F(1, 51), F(1, 57)))]
    rows = []
    for name, permutation, digest in permutations:
        for pair_name, pair in pairs:
            for source_id, triple in enumerate(module.base.SOURCES):
                pivots = module.exact_reference(permutation, pair, triple)
                runs = module.base.upstream.widths(pivots) if pivots is not None else None
                rows.append({'permutation_input': name, 'input_sha256': digest,
                             'pair_name': pair_name,
                             'beta23': module.base.serial_fraction(pair[0]),
                             'beta25': module.base.serial_fraction(pair[1]),
                             'source_id': source_id, 'exact_Q_pivots': pivots,
                             'runs': runs,
                             'entropy': sum(x*math.log(x) for x in runs) if runs else None})
    result = {'completed_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'Exact Q sampled counterfactuals only; same actual permutation, varied beta family; two actual source fixtures. No full source or local-frame certificate.',
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'counterfactual_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'records': rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'output': str(args.output), 'records': len(rows),
                      'entropy_by_permutation': [
                          {'permutation': name,
                           'profiles': [(r['pair_name'], r['source_id'], r['runs'], r['entropy'])
                                        for r in rows if r['permutation_input'] == name]}
                          for name, _, _ in permutations]}))


if __name__ == '__main__':
    main()
