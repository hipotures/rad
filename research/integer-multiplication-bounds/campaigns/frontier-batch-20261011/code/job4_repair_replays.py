#!/usr/bin/env python3
"""Repair replays of packages whose manifest lists a file their pinned commit lacks (job 4).

Job 2 found that #471, #476, #478, #483 and #492 (one author, browser uploads) stop at their own integrity check:
MANIFEST.json lists `.gitattributes`, which the pinned commits do not contain; every other file matches. #493,
#473, #490 and #491 cite #471's complex saving b = 1305231506267591/10^18 from #471's receipt, so #471 decides
whether the current top claims rest on a reproducible input.

Each replay is job 2's procedure (fresh detached worktree at the pinned SHA, fresh output directory, author's
verify.py, /usr/bin/time -v, timeout), with one documented deviation applied in memory by job4_launcher.py:
the manifest key `.gitattributes` is tolerated only if that file is absent. The record states the deviation, the
pre-check of the package against its manifest, the title kappa match and every complex saving found in the output.

usage: job4_repair_replays.py --config CFG --clone CLONE --work WORKDIR --python PY [--jobs N] [--timeout-min M]
                              [--only 471,492]
"""
import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import job2_replays as J2  # noqa: E402  (shared helpers; job 2's code is not modified)

DEFAULT_PRS = (471, 476, 478, 483, 492)
TOLERATE = '.gitattributes'
CITED_471_B = Fraction(1305231506267591, 10 ** 18)
COMPLEX_KEY = re.compile(r'complex.*(lower|saving)|^b$|complex_b', re.I)


def manifest_precheck(pkg):
    """Package vs its MANIFEST.json under the verifier's own exclusion of the root manifest."""
    m = json.loads((pkg / 'MANIFEST.json').read_text(encoding='utf-8'))
    actual = {p.relative_to(pkg).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in pkg.rglob('*') if p.is_file() and p != pkg / 'MANIFEST.json' and '__pycache__' not in p.parts}
    return dict(manifest_entries=len(m), package_files=len(actual),
                missing=sorted(set(m) - set(actual)), extra=sorted(set(actual) - set(m)),
                changed=sorted(k for k in m if k in actual and m[k] != actual[k]))


def complex_values(out):
    found = {}
    for p in sorted(out.rglob('*.json')) if out.exists() else []:
        if p.stat().st_size > 5_000_000:
            continue
        try:
            data = json.loads(p.read_text())
        except Exception:
            continue
        stack = [(data, '')]
        while stack:
            obj, pre = stack.pop()
            if isinstance(obj, dict):
                for k, v in obj.items():
                    key = f'{pre}.{k}' if pre else k
                    if COMPLEX_KEY.search(k) and isinstance(v, (str, int, float)):
                        f = J2.as_fraction(v)
                        if f is not None and 0 < f < 1:
                            found.setdefault(str(f), []).append(f'{p.relative_to(out)}:{key}')
                    stack.append((v, key))
            elif isinstance(obj, list):
                stack.extend((v, f'{pre}[{i}]') for i, v in enumerate(obj[:200]))
    return {k: v[:5] for k, v in found.items()}


def run_one(entry, args):
    pr, sha = entry['pr'], entry['sha']
    work = Path(args.work)
    tree, out = work / 'trees' / f'pr-{pr}-{sha[:12]}', work / 'out' / f'pr-{pr}-{sha[:12]}'
    tmp, log = work / 'tmp' / f'pr-{pr}', work / 'logs' / f'pr-{pr}.log'
    with J2.GIT_LOCK:
        for d in (tree, out, tmp):
            if d.exists():
                if d == tree:
                    subprocess.run(['git', '-C', args.clone, 'worktree', 'remove', '--force', str(d)], check=False)
                if d.exists():
                    shutil.rmtree(d)
        subprocess.run(['git', '-C', args.clone, 'worktree', 'prune'], check=False)
        subprocess.run(['git', '-C', args.clone, 'worktree', 'add', '--detach', str(tree), sha],
                       check=True, capture_output=True)
    tmp.mkdir(parents=True)
    assert subprocess.check_output(['git', '-C', str(tree), 'rev-parse', 'HEAD'], text=True).strip() == sha
    entry_path = tree / entry['entry']
    pre = manifest_precheck(entry_path.parent)
    eligible = pre['missing'] == [TOLERATE] and not pre['extra'] and not pre['changed']
    record = dict(pr=pr, sha=sha, author=entry['author'], title=entry['title'], title_kappa=J2.title_kappa(entry['title']),
                  deviation=f'manifest key {TOLERATE!r} tolerated only if the file is absent (job4_launcher.py)',
                  manifest_precheck=pre, eligible=eligible)
    if not eligible:
        record.update(passed=False, skipped='package differs from its manifest beyond the tolerated key')
    else:
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0',
                   PATH=str(Path(args.python).parent) + os.pathsep + os.environ.get('PATH', ''),
                   CXX=os.environ.get('CXX', 'g++'), BOOST_INCLUDE=os.environ.get('BOOST_INCLUDE', '/usr/include'),
                   OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
                   TMPDIR=str(tmp), CX_RECORD=str(tmp / 'cx_record.json'), PYTHON=args.python)
        env.pop('PYTHONOPTIMIZE', None)
        launcher = Path(__file__).resolve().parent / 'job4_launcher.py'
        argv = [a.replace('{OUT}', str(out)) for a in entry['args']]
        cmd = ['/usr/bin/time', '-v', args.python, '-B', str(launcher), '--tolerate', TOLERATE, str(entry_path), *argv]
        t0, timed_out = time.monotonic(), False
        with log.open('w') as fh:
            fh.write(f'# PR {pr} at {sha} (job 4 repair replay)\n# cwd {tree}\n# cmd {" ".join(cmd)}\n')
            fh.flush()
            try:
                code = subprocess.run(cmd, cwd=tree, env=env, stdout=fh, stderr=subprocess.STDOUT,
                                      timeout=args.timeout_min * 60).returncode
            except subprocess.TimeoutExpired:
                timed_out, code = True, None
        text = log.read_text(errors='replace')
        rss = re.search(r'Maximum resident set size \(kbytes\): (\d+)', text)
        receipts, templates, kappas = J2.scan_outputs(out, record['title_kappa'])
        cvals = complex_values(out)
        dirty = subprocess.run(['git', '-C', str(tree), 'status', '--porcelain'], capture_output=True, text=True).stdout
        record.update(exit_code=code, timed_out=timed_out, wall_seconds=round(time.monotonic() - t0, 1),
                      max_rss_kb=int(rss.group(1)) if rss else None, passed=(code == 0 and not timed_out),
                      deviation_line=next((l for l in text.splitlines() if l.startswith('# JOB4 DEVIATION')), None),
                      any_kappa_equals_title=any(k['equals_title_claim'] for k in kappas),
                      any_kappa_within_1e6_of_title=any(k['within_1e6_of_title'] for k in kappas),
                      log_kappa_matches=J2.log_kappas(text, record['title_kappa']),
                      complex_values=cvals, cited_471_b_found=str(CITED_471_B) in cvals,
                      receipts=receipts, kappas=kappas[:40], templates=templates,
                      worktree_modified_files=dirty.splitlines()[:50], log=str(log), output=str(out),
                      log_tail=text[-4000:])
    (work / 'records' / f'pr-{pr}.json').write_text(json.dumps(record, indent=1))
    return record


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--config', required=True)
    ap.add_argument('--clone', required=True)
    ap.add_argument('--work', required=True)
    ap.add_argument('--python', required=True)
    ap.add_argument('--jobs', type=int, default=len(DEFAULT_PRS))
    ap.add_argument('--timeout-min', type=float, default=150)
    ap.add_argument('--only', default=','.join(map(str, DEFAULT_PRS)))
    a = ap.parse_args()
    want = {int(x) for x in a.only.split(',')}
    entries = [e for e in json.loads(Path(a.config).read_text())['replays'] if e['pr'] in want]
    work = Path(a.work)
    for sub in ('trees', 'out', 'records', 'logs'):
        (work / sub).mkdir(parents=True, exist_ok=True)
    print(f'{len(entries)} repair replays, {a.jobs} parallel, timeout {a.timeout_min} min', flush=True)
    t0, records = time.monotonic(), []
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as pool:
        futs = {pool.submit(run_one, e, a): e for e in entries}
        for fut in cf.as_completed(futs):
            e = futs[fut]
            try:
                r = fut.result()
            except Exception as exc:
                r = dict(pr=e['pr'], sha=e['sha'], passed=False, harness_error=repr(exc))
                (work / 'records' / f"pr-{e['pr']}.json").write_text(json.dumps(r, indent=1))
            records.append(r)
            print(f"[{time.monotonic() - t0:7.0f}s] PR {r['pr']}: passed={r.get('passed')} wall={r.get('wall_seconds')}s "
                  f"kappa_exact={r.get('any_kappa_equals_title')} cited_471_b={r.get('cited_471_b_found')}", flush=True)
    records.sort(key=lambda r: r['pr'])
    keys = ('pr', 'sha', 'title_kappa', 'eligible', 'passed', 'exit_code', 'timed_out', 'wall_seconds', 'max_rss_kb',
            'any_kappa_equals_title', 'any_kappa_within_1e6_of_title', 'cited_471_b_found', 'harness_error')
    summary = dict(wall_seconds=round(time.monotonic() - t0, 1), passed=sum(bool(r.get('passed')) for r in records),
                   total=len(records), cited_471_b=str(CITED_471_B), rows=[{k: r.get(k) for k in keys} for r in records])
    (work / 'SUMMARY.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: v for k, v in summary.items() if k != 'rows'}, indent=1))


if __name__ == '__main__':
    main()
