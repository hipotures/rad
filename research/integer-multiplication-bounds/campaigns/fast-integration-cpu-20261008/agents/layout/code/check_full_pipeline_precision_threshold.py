#!/usr/bin/env python3
"""Changed work-grid family, retaining complete-pipeline rounding failures."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from time import perf_counter


def check(config):
    started = perf_counter()
    spec = importlib.util.spec_from_file_location('frozen_pipeline', config['producer'])
    producer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(producer)
    expected_failure = config['expected_recovery_failure']
    try:
        result = producer.run_case(config)
    except AssertionError as error:
        details = error.args[0] if error.args else None
        if not isinstance(details, tuple) or len(details) != 4 or not isinstance(details[2], list):
            traceback = error.__traceback__
            while traceback.tb_next:
                traceback = traceback.tb_next
            values = traceback.tb_frame.f_locals
            if not all(name in values for name in ('actual', 'oracle', 'maximum_real_error')):
                raise
            details = config, values['maximum_real_error'], values['actual'], values['oracle']
        _, numerical_error, actual, oracle = details
        result = {'config': config, 'status': 'expected insufficient work-grid failure retained',
                  'maximum_coefficient_error': str(numerical_error),
                  'incorrect_integer_coefficients': sum(x != y for x, y in zip(actual, oracle)),
                  'maximum_integer_difference': max(abs(x - y) for x, y in zip(actual, oracle)),
                  'source_volume': len(actual), 'producer_sha256': producer.SOURCE_SHA256_AT_IMPORT,
                  'seconds': perf_counter() - started}
        if not expected_failure:
            result['status'] = 'unexpected coefficient failure retained'
        if actual == oracle:
            result['status'] = 'integer recovery passed but required quarter-unit margin failed'
    else:
        result['producer_sha256'] = producer.SOURCE_SHA256_AT_IMPORT
        if expected_failure is True:
            result['status'] = 'unexpected successful recovery retained'
    Path(config['row_output']).write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--producer', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--workers', type=int, default=2)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        parser.error('one to four allocated CPU workers')
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[key] = '1'
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    configs = json.loads(Path(args.config).read_text())
    for j, row in enumerate(configs):
        row['producer'] = args.producer
        row['row_output'] = str(output / f'row-{j}.json')
    started = perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        rows = list(executor.map(check, configs))
    result = {'status': 'complete-pipeline precision observations retained',
              'rows': rows, 'workers': args.workers, 'seconds': perf_counter() - started,
              'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'limitations': ['finite observed threshold, not an all-size precision theorem']}
    (output / 'certificate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'rows': [(r['config']['q'], r['status']) for r in rows]}))


if __name__ == '__main__':
    main()
