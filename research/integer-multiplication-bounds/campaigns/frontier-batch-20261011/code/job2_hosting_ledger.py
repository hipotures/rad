#!/usr/bin/env python3
"""Independent post-hoc ledger of the hosted templates produced by job 2 (agent analysis step).

Reads every distinct *TEMPLATE*.json.gz under <job2 run>/out that carries a `hosting` section and checks it
without importing any upstream code:

  * layout: `slots` rows (child, copy, off, w, stage, helper) or `pieces` rows (stage, helper, child,
    [(copy, off, w), ...]); other layouts are reported as not parsed;
  * split ledger: hosted residuals, residuals whose coordinates lie on more than one data copy (cross-copy),
    helpers (stage, helper) that occur in more than one row;
  * coordinate ledger: per (child, copy) the hosted intervals must be disjoint and inside the child's rank;
  * windows: each hosted stage must lie in the template's stored window of its child; the window is also
    re-derived from the template's own schedule ("stages of local invocations on other pairs strictly between
    the last local/bridge touch of the child's pair and the child") when the schedule names pairs and child
    indices;
  * exchange events inside a window are counted (observation only; the rule text does not mention them).

usage: job2_hosting_ledger.py --run <job2 run dir> --out <ledger.json>
"""
import argparse
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def rederive_windows(schedule):
    """{idx: (pair, stages, exchanges_inside)} or None when the schedule does not name pairs/child indices."""
    last, locals_, exch, out = {}, [], [], {}
    for pos, e in enumerate(schedule):
        k = e.get('kind')
        if k in ('local', 'local_cover_sweep'):
            if 'pair' not in e:
                return None
            locals_.append((pos, e['stage'], e['pair']))
            last[e['pair']] = pos
        elif k == 'bridge':
            last[e['dst']] = pos
            last[e['src']] = pos
        elif k == 'exchange':
            exch.append(pos)
        elif k == 'idle':
            if 'idx' not in e:
                return None
            lo = last.get(e['pair'], -1)
            stages = {s for q, s, p in locals_ if lo < q < pos and p != e['pair']}
            out[e['idx']] = (e['pair'], stages, sum(lo < q < pos for q in exch))
        elif k == 'idle_cover_sweep':
            return None
    return out


def rows_of(hosting):
    """Normalised rows (stage, helper, child, [(copy, off, w)]) or None for an unknown layout."""
    if 'pieces' in hosting:
        return [(s, h, i, [tuple(x) for x in segs]) for s, h, i, segs in hosting['pieces']]
    rows = hosting.get('slots') or []
    if rows and all(len(r) == 6 for r in rows):
        return [(s, h, i, [(c, off, w)]) for i, c, off, w, s, h in rows]
    return None


def audit(t):
    ho = t['hosting']
    res = dict(version=t.get('version'), layout='pieces' if 'pieces' in ho else 'slots')
    rows = rows_of(ho)
    if rows is None:
        res.update(parsed=False, row_length=sorted({len(r) for r in ho.get('slots', [])}))
        return res
    win = {int(k): v for k, v in ho['windows'].items()}
    split = sum(len({c for c, _, _ in segs}) > 1 for _, _, _, segs in rows)
    helper_rows = Counter((s, h) for s, h, _, _ in rows)
    coords = defaultdict(list)
    for s, h, i, segs in rows:
        for c, off, w in segs:
            coords[(i, c)].append((off, off + w))
    overlaps = outside = 0
    for (i, _), iv in coords.items():
        iv.sort()
        overlaps += sum(a[1] > b[0] for a, b in zip(iv, iv[1:]))
        rank = win.get(i, [None, None])[1]
        outside += sum(lo < 0 or (rank is not None and hi > rank) for lo, hi in iv)
    not_in_window = sum(s not in set(win.get(i, [None, None, []])[2]) for s, _, i, _ in rows)
    res.update(parsed=True, hosted_residuals=len(rows), hosted_coordinates=sum(w for *_, segs in rows for _, _, w in segs),
               cross_copy_residuals=split, helpers_in_more_than_one_row=sum(n > 1 for n in helper_rows.values()),
               interval_overlaps=overlaps, intervals_outside_child_rank=outside, rows_outside_stored_window=not_in_window)
    sched = t.get('schedule') or t.get('execution_schedule') or []
    der = rederive_windows(sched)
    if der is None:
        res['window_rederivation'] = 'not applicable: schedule does not name pairs and child indices'
    else:
        diff = sorted(i for i in win if i not in der or der[i][0] != win[i][0] or der[i][1] != set(win[i][2]))
        used = {i for _, _, i, _ in rows}
        res['window_rederivation'] = dict(children=len(win), mismatched_children=diff[:20], n_mismatched=len(diff),
                                          used_children_with_exchange_inside=sorted(i for i in used if i in der and der[i][2]))
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--run', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    run = Path(a.run)
    records = {json.loads(p.read_text())['pr']: json.loads(p.read_text()) for p in (run / 'records').glob('pr-*.json')}
    by_sha, refs = {}, defaultdict(list)
    for pr, r in sorted(records.items()):
        for tpl in r.get('templates', []):
            refs[tpl['sha256']].append(dict(pr=pr, path=tpl['path']))
            if tpl['sha256'] in by_sha:
                continue
            p = Path(r['output']) / tpl['path']
            raw = p.read_bytes()
            assert hashlib.sha256(raw).hexdigest() == tpl['sha256'], p
            t = json.loads(gzip.decompress(raw) if p.name.endswith('.gz') else raw)
            if isinstance(t.get('hosting'), dict):
                by_sha[tpl['sha256']] = audit(t)
    ledger = [dict(sha256=sha, referenced_by=refs[sha], **res) for sha, res in by_sha.items()]
    ledger.sort(key=lambda x: (min(r['pr'] for r in x['referenced_by']), x['version'] or ''))
    clean = [x for x in ledger if x.get('parsed')]
    summary = dict(hosted_templates=len(ledger), parsed=len(clean),
                   with_cross_copy_residuals=sum(x['cross_copy_residuals'] > 0 for x in clean),
                   with_overlaps=sum(x['interval_overlaps'] > 0 for x in clean),
                   with_rows_outside_window=sum(x['rows_outside_stored_window'] > 0 for x in clean),
                   with_window_mismatch=sum(isinstance(x['window_rederivation'], dict) and x['window_rederivation']['n_mismatched'] > 0 for x in clean))
    Path(a.out).write_text(json.dumps(dict(summary=summary, templates=ledger), indent=1))
    print(json.dumps(summary, indent=1))
    for x in ledger:
        first = x['referenced_by'][0]
        if not x.get('parsed'):
            print(f"#{first['pr']:<4} {x['version']:<58} not parsed {x.get('row_length')}")
            continue
        wr = x['window_rederivation']
        wtxt = 'n/a' if isinstance(wr, str) else f"mismatch {wr['n_mismatched']}/{wr['children']}, exch-in-window {len(wr['used_children_with_exchange_inside'])}"
        print(f"#{first['pr']:<4} {x['version']:<58} rows {x['hosted_residuals']:>6} cross-copy {x['cross_copy_residuals']:>5} "
              f"dup-helper {x['helpers_in_more_than_one_row']:>4} overlap {x['interval_overlaps']} outside-rank {x['intervals_outside_child_rank']} "
              f"outside-window {x['rows_outside_stored_window']} windows {wtxt}  ({first['path']})")


if __name__ == '__main__':
    main()
