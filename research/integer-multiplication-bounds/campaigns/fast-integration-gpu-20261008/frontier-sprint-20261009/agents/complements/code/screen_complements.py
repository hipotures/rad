#!/usr/bin/env python3
"""Fresh bounded PR120 control and exact alternate-complement screens.

Loads pinned Apache-2.0 upstream source without mutating it. PR120's scalar DAG,
matching, placement priority, stopping policy, and paid histogram compiler are
unchanged. Only its nondegenerate-complement extractor is substituted. Numerical
moments are high-precision DISCOVERY scores, not accepted kappa certificates.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from functools import lru_cache
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import resource
import sys
import time

PIN = 'bfc5466b028923a1f8655602994ea56c70b5c329'
MODES = ('control', 'reverse_pivots', 'sparse_pivots', 'mixed_basis')
TRIALS = ('0.000109140237', '0.00012', '0.0005622769')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rank(vectors):
    piv = {}
    for v in vectors:
        while v:
            p = v.bit_length() - 1
            if p not in piv:
                piv[p] = v
                break
            v ^= piv[p]
    return len(piv)


def check_part(original, selected):
    k = len(selected)
    gram = [sum(((a & b).bit_count() & 1) << j for j, b in enumerate(selected)) for a in selected]
    original_gram = [sum(((a & b).bit_count() & 1) << j for j, b in enumerate(original)) for a in original]
    if rank(selected) != k or rank(gram) != k:
        raise ValueError('Alternative complement is dependent or degenerate')
    if rank(tuple(original) + tuple(selected)) != rank(original):
        raise ValueError('Alternative complement escapes the candidate intersection')
    if k != rank(original_gram):
        raise ValueError('Alternative complement does not exhaust the nondegenerate quotient')


def alternate_part(mod, B, mode, seed):
    rows = list(B)
    if mode == 'mixed_basis':
        local_seed = int.from_bytes(hashlib.sha256(json.dumps([seed, list(B)]).encode()).digest()[:8], 'big')
        rng = random.Random(local_seed)
        for _ in range(3 * len(rows)):
            if len(rows) > 1:
                a, b = rng.sample(range(len(rows)), 2)
                rows[a] ^= rows[b]
        rng.shuffle(rows)
    elif mode == 'sparse_pivots':
        rows.sort(key=lambda x: (x.bit_count(), x))
    out = []
    while rows:
        eligible = [i for i, x in enumerate(rows) if (x.bit_count() & 1)]
        if eligible:
            i = eligible[-1] if mode == 'reverse_pivots' else eligible[0]
            a = rows.pop(i)
            out.append(a)
            rows = [x ^ a if (x & a).bit_count() & 1 else x for x in rows]
        else:
            pairs = [(i, j) for i in range(len(rows)) for j in range(i + 1, len(rows))
                     if (rows[i] & rows[j]).bit_count() & 1]
            if not pairs:
                break
            i, j = pairs[-1] if mode == 'reverse_pivots' else pairs[0]
            a, b = rows[i], rows[j]
            out.extend((a, b))
            rows = [x ^ (a if (x & b).bit_count() & 1 else 0) ^ (b if (x & a).bit_count() & 1 else 0)
                    for k, x in enumerate(rows) if k not in (i, j)]
        if mode == 'sparse_pivots':
            rows.sort(key=lambda x: (x.bit_count(), x))
    return mod.sat_basis(out)


def moments(profile):
    with localcontext() as ctx:
        ctx.prec = 70
        m, W = Decimal(profile['m']), Decimal(profile['W'])
        result = {}
        for ss in TRIALS:
            s = Decimal(ss)
            H = sum(Decimal(n) * Decimal(t) / (m * W) * (s * (m / Decimal(t)).ln()).exp()
                    for t, n in profile['child_multiplicities'].items())
            result[ss] = {'H': str(H), 'one_minus_H': str(Decimal(1) - H)}
        return result


def worker(source, output, mode, seed):
    started = time.perf_counter()
    dest = Path(output) / mode
    dest.mkdir(parents=True, exist_ok=False)
    source = Path(source)
    module_path = source / 'research/deferred-replayed/complex_deferred.py'
    spec = importlib.util.spec_from_file_location('upstream_deferred', module_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    original = mod.sat_nonsingular_part
    trace = []

    @lru_cache(None)
    def extract(B):
        baseline = original(B)
        selected = baseline if mode == 'control' else alternate_part(mod, B, mode, seed)
        check_part(B, selected)
        trace.append({'intersection': list(B), 'selected': list(selected), 'control': list(baseline),
                      'changed_subspace': selected != baseline, 'gram_rank': len(selected),
                      'radical_dimension': len(B) - len(selected)})
        return selected

    mod.sat_nonsingular_part = extract
    mod.OUT = dest / 'complex-profile.json'
    mod.WRITE = True
    os.environ['DEFER_DUMP'] = str(dest / 'word.json')
    with (dest / 'run.log').open('w') as log, redirect_stdout(log), redirect_stderr(log):
        mod.main()
    profile = json.loads(mod.OUT.read_text())
    receipt = {
        'status': 'DISCOVERY', 'variant': mode, 'seed': seed,
        'source_pr': 120, 'source_head': PIN,
        'source_sha256': digest(module_path), 'dag_sha256': digest(mod.WITNESS),
        'script_sha256': digest(__file__),
        'completed_utc': datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds': time.perf_counter() - started,
        'max_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'thread_pool_size': 1,
        'unique_extractions': len(trace),
        'distinct_from_control_extractions': sum(t['changed_subspace'] for t in trace),
        'independent_exact_extraction_checks': True,
        'profile': profile, 'common_trial_complete_moments': moments(profile),
        'word_sha256': digest(dest / 'word.json'),
        'profile_sha256': digest(mod.OUT),
        'validation_scope': ['upstream fresh scalar-output replay', 'two upstream arbitrary-dirty forward replays',
                             'all upstream exact role and target chain checks', 'fresh complete paid child histogram',
                             'independent exact extraction rank, containment and quotient dimension'],
        'not_verified': ['independent reflected-word replay', 'rigorous moment enclosure',
                         'final 47-constraint assembly', 'all-size transfer assumptions'],
    }
    (dest / 'extraction-trace.json').write_text(json.dumps(trace, indent=2) + '\n')
    (dest / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--summary', required=True, type=Path)
    p.add_argument('--seed', default=20261009, type=int)
    p.add_argument('--workers', default=4, type=int)
    args = p.parse_args()
    if not __debug__:
        raise SystemExit('Assertion-disabled execution is not supported by the upstream evaluator')
    for env in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        os.environ[env] = '1'
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(worker, str(args.source.resolve()), str(args.output.resolve()), mode, args.seed): mode
                   for mode in MODES}
        for future in as_completed(futures):
            r = future.result()
            results.append(r)
            print(json.dumps({k: r[k] for k in ('variant', 'elapsed_seconds', 'distinct_from_control_extractions')}) , flush=True)
    result = {'status': 'DISCOVERY', 'workers': args.workers, 'variants': sorted(results, key=lambda x: x['variant'])}
    control = next(r for r in results if r['variant'] == 'control')
    expected = json.loads((args.source / 'research/deferred-replayed/complex-profile.json').read_text())
    if control['profile'] != expected:
        raise ValueError('Fresh control did not reproduce pinned complete profile')
    with localcontext() as ctx:
        ctx.prec = 70
        for r in result['variants']:
            r['delta_H_vs_control'] = {s: str(Decimal(r['common_trial_complete_moments'][s]['H']) -
                                                      Decimal(control['common_trial_complete_moments'][s]['H'])) for s in TRIALS}
    args.summary.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
