#!/usr/bin/env python3
"""Fresh replays of the frontier claims opened after job 2 was pinned (job 5).

For every entry of configs/job5-replays.json (#484 and #495-#502 at pinned SHAs):

  1. as-is attempt: job 2's procedure unchanged (job2_replays.run_one): fresh detached worktree, fresh output
     directory, the author's own entry point, /usr/bin/time -v, timeout;
  2. repair attempt, only if the as-is attempt stopped at the package's own integrity assertion
     ('Package manifest mismatch') and its verify.py contains that assertion in the form job4_launcher.py patches:
     job 4's procedure unchanged (job4_repair_replays.run_one) under <run>/repair/, with its own worktree, output
     directory and record. Job 4 itself declines (eligible=false) unless the package differs from its manifest
     only by the absent `.gitattributes`;
  3. checks on the passing attempt's outputs, written to <run>/checks/pr-N.json:
     - the claimed value (the title kappa, or the config's `claim` for a supplier PR whose title has no kappa)
       is searched in every JSON file under 5 MB; JSON numbers are parsed as exact decimals, strings such as
       'a/b', 'a/10^k' and decimals as exact fractions; exact and relative-1e-9 matches are listed;
     - every complex saving b found under a complex-saving key, to map which supplier each claim binds to.

{BOOST} in an entry's args is replaced by $BOOST_INCLUDE (default /usr/include). Replays run concurrently;
a failing replay never stops the others.

usage: job5_replays.py --config CFG --clone CLONE --work RUN --python PY [--jobs N] [--timeout-min M]
                       [--only 496,501] [--force]
"""
import argparse
import concurrent.futures as cf
import copy
import json
import os
import re
import sys
import time
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import job2_replays as J2  # noqa: E402  (shared procedures; earlier jobs' code is not modified)
import job4_repair_replays as J4  # noqa: E402
from job4_launcher import NEEDLE  # noqa: E402

COMPLEX_KEY = re.compile(r'complex.*(lower|saving)|^b$|complex_b|^b_(lower|complex)', re.I)
POWER = re.compile(r'^\s*([+-]?\d+)\s*/\s*10\s*(?:\^|\*\*)\s*(\d+)\s*$')
REL_TOL = Fraction(1, 10 ** 9)


def exact(v):
    """Exact Fraction of a JSON value, or None. Floats are refused (JSON numbers arrive as Decimal)."""
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, Decimal)):
        return Fraction(v)
    if isinstance(v, str):
        m = POWER.match(v)
        if m:
            return Fraction(int(m.group(1)), 10 ** int(m.group(2)))
        try:
            return Fraction(v.strip().replace(' ', '').replace('_', ''))
        except (ValueError, ZeroDivisionError):
            return None
    return None


def load_json(path):
    try:
        return json.loads(path.read_text(), parse_float=Decimal)
    except Exception:
        return None


def walk(obj, prefix=''):
    """(key path, last key, value) for every scalar, lists capped at 2000 items."""
    stack = [(obj, prefix, '')]
    while stack:
        o, pre, key = stack.pop()
        if isinstance(o, dict):
            stack.extend((v, f'{pre}.{k}' if pre else str(k), str(k)) for k, v in o.items())
        elif isinstance(o, list):
            stack.extend((v, f'{pre}[{i}]', key) for i, v in enumerate(o[:2000]))
        else:
            yield pre, key, o


def output_checks(out, claimed):
    """Exact/close occurrences of the claimed value and every complex saving b under `out`."""
    want = Fraction(claimed) if claimed is not None else None
    hits_exact, hits_close, bvals, files = [], [], {}, 0
    for p in sorted(out.rglob('*.json')) if out.exists() else []:
        if p.stat().st_size > 5_000_000:
            continue
        data = load_json(p)
        if data is None:
            continue
        files += 1
        rel = str(p.relative_to(out))
        for path, key, v in walk(data):
            f = exact(v)
            if f is None:
                continue
            if want is not None and want != 0:
                if f == want:
                    hits_exact.append(f'{rel}:{path}')
                elif abs(f / want - 1) < REL_TOL:
                    hits_close.append(f'{rel}:{path}={str(v)[:40]}')
            if COMPLEX_KEY.search(key) and 0 < f < 1:
                bvals.setdefault(str(f), []).append(f'{rel}:{path}')
    return dict(json_files_scanned=files, claim_exact=bool(hits_exact), claim_close=bool(hits_close),
                claim_exact_at=hits_exact[:10], claim_close_at=hits_close[:10],
                complex_b_values={k: dict(decimal=f'{float(Fraction(k)):.15e}', at=v[:4]) for k, v in bvals.items()})


def substitute(entry):
    e = copy.deepcopy(entry)
    boost = os.environ.get('BOOST_INCLUDE', '/usr/include')
    e['args'] = [a.replace('{BOOST}', boost) for a in e['args']]
    return e


def wants_repair(entry, rec, args):
    if rec.get('passed') or rec.get('timed_out') or 'Package manifest mismatch' not in (rec.get('log_tail') or ''):
        return False
    tree = Path(args.work) / 'trees' / f"pr-{entry['pr']}-{entry['sha'][:12]}"
    src = tree / entry['entry']
    return src.is_file() and src.read_text(encoding='utf-8').count(NEEDLE) == 1


def replay(entry, args):
    e = substitute(entry)
    work = Path(args.work)
    asis = J2.run_one(e, args)
    final, attempt = asis, 'as-is'
    repair = None
    if wants_repair(e, asis, args):
        rargs = copy.copy(args)
        rargs.work = str(work / 'repair')
        for sub in ('trees', 'out', 'records', 'logs'):
            (work / 'repair' / sub).mkdir(parents=True, exist_ok=True)
        try:
            repair = J4.run_one(e, rargs)
        except Exception as exc:  # keep the as-is record; report the repair harness error separately
            repair = dict(passed=False, eligible=None, harness_error=repr(exc))
        if repair.get('passed'):
            final, attempt = repair, 'repair (job 4 deviation)'
    claim = e.get('claim')
    claimed = J2.title_kappa(e['title']) if claim is None else str(Fraction(claim['value']))
    checks = dict(pr=e['pr'], sha=e['sha'], tier=e['tier'], claim_kind='title kappa' if claim is None else claim['kind'],
                  claimed=claimed, passing_attempt=attempt if final.get('passed') else None,
                  output=final.get('output'))
    if final.get('passed'):
        checks.update(output_checks(Path(final['output']), claimed))
    (work / 'checks').mkdir(exist_ok=True)
    (work / 'checks' / f"pr-{e['pr']}.json").write_text(json.dumps(checks, indent=1))
    return dict(pr=e['pr'], sha=e['sha'], tier=e['tier'], claim_kind=checks['claim_kind'], claimed=claimed,
                asis_passed=asis.get('passed'), asis_exit=asis.get('exit_code'), asis_wall=asis.get('wall_seconds'),
                asis_timed_out=asis.get('timed_out'), max_rss_kb=asis.get('max_rss_kb'),
                repair_attempted=repair is not None, repair_eligible=(repair or {}).get('eligible'),
                repair_passed=(repair or {}).get('passed'), repair_wall=(repair or {}).get('wall_seconds'),
                repair_harness_error=(repair or {}).get('harness_error'),
                passed=bool(final.get('passed')), passing_attempt=checks['passing_attempt'],
                claim_exact=checks.get('claim_exact'), claim_close=checks.get('claim_close'),
                complex_b_values=sorted(checks.get('complex_b_values', {}), key=Fraction)[:8])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--config', required=True)
    ap.add_argument('--clone', required=True)
    ap.add_argument('--work', required=True)
    ap.add_argument('--python', required=True)
    ap.add_argument('--jobs', type=int, default=0, help='default: number of replays, at most cores - 1')
    ap.add_argument('--timeout-min', type=float, default=150)
    ap.add_argument('--only', default='')
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    entries = json.loads(Path(a.config).read_text())['replays']
    if a.only:
        keep = {int(x) for x in a.only.split(',')}
        entries = [e for e in entries if e['pr'] in keep]
    a.jobs = a.jobs or max(1, min(len(entries), (os.cpu_count() or 2) - 1))
    work = Path(a.work)
    for sub in ('trees', 'out', 'records', 'logs'):
        (work / sub).mkdir(parents=True, exist_ok=True)
    print(f'{len(entries)} replays, {a.jobs} parallel, timeout {a.timeout_min} min', flush=True)
    t0, rows = time.monotonic(), []
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as pool:
        futs = {pool.submit(replay, e, a): e for e in entries}
        for fut in cf.as_completed(futs):
            e = futs[fut]
            try:
                r = fut.result()
            except Exception as exc:
                r = dict(pr=e['pr'], sha=e['sha'], tier=e['tier'], passed=False, harness_error=repr(exc))
            rows.append(r)
            print(f"[{time.monotonic() - t0:7.0f}s] PR {r['pr']}: passed={r.get('passed')} ({r.get('passing_attempt')}) "
                  f"as-is exit={r.get('asis_exit')} wall={r.get('asis_wall')}s repair={r.get('repair_passed')} "
                  f"claim_exact={r.get('claim_exact')} b={r.get('complex_b_values')}"
                  + (f" HARNESS_ERROR {r['harness_error']}" if r.get('harness_error') else ''), flush=True)
    rows.sort(key=lambda r: r['pr'])
    summary = dict(config=str(a.config), python=a.python, jobs=a.jobs, timeout_min=a.timeout_min,
                   wall_seconds=round(time.monotonic() - t0, 1), total=len(rows),
                   passed=sum(bool(r.get('passed')) for r in rows),
                   passed_as_is=sum(bool(r.get('asis_passed')) for r in rows),
                   claim_exact=sum(bool(r.get('claim_exact')) for r in rows),
                   harness_errors=sum('harness_error' in r for r in rows), rows=rows)
    (work / 'SUMMARY.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: v for k, v in summary.items() if k != 'rows'}, indent=1))


if __name__ == '__main__':
    main()
