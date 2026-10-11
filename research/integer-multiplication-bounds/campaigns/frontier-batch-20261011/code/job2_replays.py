#!/usr/bin/env python3
"""Parallel fresh replays of upstream claims at pinned SHAs (job 2).

For every entry of configs/job2-replays.json:
  1. create a fresh detached worktree of the local upstream clone at the pinned SHA
     (no network needed once the clone holds the commits);
  2. run the PR author's own entry point with a fresh output directory, under
     /usr/bin/time -v and a per-replay timeout;
  3. record exit status, wall time, peak RSS, receipt/result files and every kappa
     string found in them; compare with the kappa in the PR title;
  4. inventory produced global templates (path, bytes, sha256, version field).

Upstream verifiers are single-threaded, so replays run concurrently in a process
pool (default: cores - 1). Longest-expected replays start first. A failing or
timed-out replay never stops the others; reruns skip replays that already have a
final record (resume), unless --force.

usage: job2_replays.py --config CFG --clone UPSTREAM_CLONE --work WORKDIR --python PY
                       [--jobs N] [--timeout-min M] [--only 442,436] [--force]
"""
import argparse
import concurrent.futures as cf
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from fractions import Fraction
from pathlib import Path

KAPPA_IN_TITLE = re.compile(r'(?:κ|kappa)\s*(?:=|≈)?\s*(\d+\.\d+(?:e-?\d+)?|\d+/\d+)', re.I)
KAPPA_FIELD = re.compile(r'kappa|κ', re.I)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def title_kappa(title):
    m = KAPPA_IN_TITLE.search(title.replace('·10⁻³', 'e-3').replace('×10⁻³', 'e-3'))
    if not m:
        return None
    text = m.group(1)
    try:
        return str(Fraction(text))
    except (ValueError, ZeroDivisionError):
        return None


def kappa_values(obj, prefix=''):
    """All (path, value) pairs in a JSON object whose key mentions kappa."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f'{prefix}.{k}' if prefix else k
            if KAPPA_FIELD.search(k) and isinstance(v, (str, int, float)):
                out.append((p, v))
            out.extend(kappa_values(v, p))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:50]):
            out.extend(kappa_values(v, f'{prefix}[{i}]'))
    return out


def as_fraction(v):
    try:
        if isinstance(v, str):
            v = v.strip().replace(' ', '')
        return Fraction(v)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def scan_outputs(out_dir, claimed):
    receipts, templates, kappas = [], [], []
    if not out_dir.exists():
        return receipts, templates, kappas
    for p in sorted(out_dir.rglob('*')):
        if not p.is_file():
            continue
        name = p.name
        if name.endswith('.json') and p.stat().st_size < 5_000_000:
            try:
                data = json.loads(p.read_text())
            except Exception:
                continue
            rel = str(p.relative_to(out_dir))
            if isinstance(data, dict) and isinstance(data.get('status'), str):
                receipts.append(dict(path=rel, status=data['status']))
            for key, val in kappa_values(data):
                f = as_fraction(val)
                close = (f is not None and claimed is not None and Fraction(claimed) != 0
                         and abs(f / Fraction(claimed) - 1) < Fraction(1, 10 ** 6))
                kappas.append(dict(file=rel, key=key, value=str(val),
                                   equals_title_claim=(f is not None and claimed is not None and f == Fraction(claimed)),
                                   within_1e6_of_title=close))
        if 'TEMPLATE' in name.upper() and name.endswith(('.json', '.json.gz')):
            version = None
            try:
                raw = gzip.decompress(p.read_bytes()) if name.endswith('.gz') else p.read_bytes()
                if len(raw) < 2_000_000_000:
                    version = json.loads(raw).get('version')
            except Exception as exc:  # inventory only; never fatal
                version = f'unreadable: {exc.__class__.__name__}'
            templates.append(dict(path=str(p.relative_to(out_dir)), bytes=p.stat().st_size, sha256=sha256(p), version=version))
    return receipts, templates, kappas


NUMBER = re.compile(r'\b\d{3,}/\d{3,}\b|\b0\.\d{8,}\b|\b\d\.\d{8,}e-\d+\b')


def log_kappas(text, claimed):
    """Numbers in the run log that equal, or are within 1e-6 of, the title claim."""
    if claimed is None:
        return []
    want, hits = Fraction(claimed), []
    for tok in dict.fromkeys(NUMBER.findall(text)):
        f = as_fraction(tok)
        if f and abs(f / want - 1) < Fraction(1, 10 ** 6):
            hits.append(dict(token=tok, exact=(f == want)))
    return hits[:20]


GIT_LOCK = threading.Lock()


def run_one(entry, args):
    pr, sha = entry['pr'], entry['sha']
    work = Path(args.work)
    tree = work / 'trees' / f'pr-{pr}-{sha[:12]}'
    out = work / 'out' / f'pr-{pr}-{sha[:12]}'
    rec_path = work / 'records' / f'pr-{pr}.json'
    log = work / 'logs' / f'pr-{pr}.log'
    if rec_path.exists() and not args.force:
        return json.loads(rec_path.read_text())
    tmp = work / 'tmp' / f'pr-{pr}'
    with GIT_LOCK:  # concurrent worktree operations on one clone contend for git locks
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
    head = subprocess.check_output(['git', '-C', str(tree), 'rev-parse', 'HEAD'], text=True).strip()
    assert head == sha, (head, sha)
    entry_path = tree / entry['entry']
    argv = [a.replace('{OUT}', str(out)) for a in entry['args']]
    interp = ['bash'] if entry['runner'] == 'bash' else [args.python, '-B']
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0',
               PATH=str(Path(args.python).parent) + os.pathsep + os.environ.get('PATH', ''),
               CXX=os.environ.get('CXX', 'g++'), BOOST_INCLUDE=os.environ.get('BOOST_INCLUDE', '/usr/include'),
               OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
               TMPDIR=str(tmp), CX_RECORD=str(tmp / 'cx_record.json'), PYTHON=args.python)
    env.pop('PYTHONOPTIMIZE', None)
    cmd = ['/usr/bin/time', '-v', *interp, str(entry_path), *argv]
    t0 = time.monotonic()
    timed_out = False
    with log.open('w') as fh:
        fh.write(f'# PR {pr} at {sha}\n# cwd {tree}\n# cmd {" ".join(cmd)}\n')
        fh.flush()
        try:
            proc = subprocess.run(cmd, cwd=tree, env=env, stdout=fh, stderr=subprocess.STDOUT,
                                  timeout=args.timeout_min * 60)
            code = proc.returncode
        except subprocess.TimeoutExpired:
            timed_out, code = True, None
    wall = round(time.monotonic() - t0, 1)
    text = log.read_text(errors='replace')
    rss = re.search(r'Maximum resident set size \(kbytes\): (\d+)', text)
    claimed = title_kappa(entry['title'])
    receipts, templates, kappas = scan_outputs(out, claimed)
    dirty = subprocess.run(['git', '-C', str(tree), 'status', '--porcelain'], capture_output=True, text=True).stdout
    record = dict(pr=pr, sha=sha, tier=entry['tier'], author=entry['author'], title=entry['title'],
                  title_kappa=claimed, exit_code=code, timed_out=timed_out, wall_seconds=wall,
                  max_rss_kb=int(rss.group(1)) if rss else None,
                  passed=(code == 0 and not timed_out),
                  any_kappa_equals_title=any(k['equals_title_claim'] for k in kappas),
                  any_kappa_within_1e6_of_title=any(k['within_1e6_of_title'] for k in kappas),
                  log_kappa_matches=log_kappas(text, claimed),
                  receipts=receipts, kappas=kappas[:40], templates=templates,
                  worktree_modified_files=dirty.splitlines()[:50], log=str(log), output=str(out),
                  log_tail=text[-4000:])
    rec_path.write_text(json.dumps(record, indent=1))
    return record


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--config', required=True)
    ap.add_argument('--clone', required=True)
    ap.add_argument('--work', required=True)
    ap.add_argument('--python', required=True)
    ap.add_argument('--jobs', type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument('--timeout-min', type=float, default=150)
    ap.add_argument('--only', default='')
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args()
    cfg = json.loads(Path(args.config).read_text())
    entries = cfg['replays']
    if args.only:
        keep = {int(x) for x in args.only.split(',')}
        entries = [e for e in entries if e['pr'] in keep]
    work = Path(args.work)
    for sub in ('trees', 'out', 'records', 'logs'):
        (work / sub).mkdir(parents=True, exist_ok=True)
    # Longest first: package size in the pinned tree is the available proxy.
    def weight(e):
        try:
            return int(subprocess.check_output(
                f"git -C {args.clone} ls-tree -r {e['sha']} -- research | wc -l", shell=True, text=True))
        except Exception:
            return 0
    entries = sorted(entries, key=weight, reverse=True)
    print(f'{len(entries)} replays, {args.jobs} parallel, timeout {args.timeout_min} min', flush=True)
    t0 = time.monotonic()
    records = []
    with cf.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futs = {pool.submit(run_one, e, args): e for e in entries}
        for fut in cf.as_completed(futs):
            e = futs[fut]
            try:
                r = fut.result()
            except Exception as exc:
                r = dict(pr=e['pr'], sha=e['sha'], tier=e['tier'], passed=False, harness_error=repr(exc))
                (work / 'records' / f"pr-{e['pr']}.json").write_text(json.dumps(r, indent=1))
            records.append(r)
            print(f"[{time.monotonic() - t0:7.0f}s] PR {r['pr']}: passed={r.get('passed')} "
                  f"wall={r.get('wall_seconds')}s kappa_exact={r.get('any_kappa_equals_title')} "
                  f"kappa_close={r.get('any_kappa_within_1e6_of_title') or bool(r.get('log_kappa_matches'))}", flush=True)
    records.sort(key=lambda r: r['pr'])
    summary = dict(config=str(args.config), python=args.python, jobs=args.jobs, timeout_min=args.timeout_min,
                   wall_seconds=round(time.monotonic() - t0, 1),
                   passed=sum(bool(r.get('passed')) for r in records), total=len(records),
                   rows=[{k: r.get(k) for k in ('pr', 'sha', 'tier', 'title_kappa', 'passed', 'exit_code', 'timed_out',
                                                'wall_seconds', 'max_rss_kb', 'any_kappa_equals_title',
                                                'any_kappa_within_1e6_of_title', 'harness_error')}
                         for r in records])
    (work / 'SUMMARY.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: v for k, v in summary.items() if k != 'rows'}, indent=1))


if __name__ == '__main__':
    main()
