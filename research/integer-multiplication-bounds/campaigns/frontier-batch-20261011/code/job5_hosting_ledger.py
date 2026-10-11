#!/usr/bin/env python3
"""Independent post-hoc ledger of the hosted templates produced by job 5 (agent analysis step).

Extends job2_hosting_ledger.py without changing it:

  * one more slot layout: #471's 9-field rows (child, copy, off, footprint, w, stage, replica, helper, spectator),
    whose helper identity includes the replica; job 2's ledger reported this layout as not parsed;
  * a per-call owner summary for every template with `calls[].owners` (also templates without a hosting section):
    owners per call, owner kinds, families holding more than one owner within one call, the largest such count,
    and owners whose family recurs within the call with an identical descriptor (a literal alias).

The split, overlap, rank and window checks are job 2's (job2_hosting_ledger.audit). Templates are read from the
records of the given runs (as-is records/ and job 5's repair/records/).

usage: job5_hosting_ledger.py --run <job5 run> [--run <job4 run> ...] --out <ledger.json>
"""
import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import job2_hosting_ledger as L  # noqa: E402

_rows_of_job2 = L.rows_of


def rows_of(hosting):
    rows = hosting.get('slots') or []
    if rows and 'pieces' not in hosting and all(len(r) == 9 for r in rows):
        # (stage, helper id incl. replica, child, [(copy, off, active width)])
        return [(s, (rep, h), i, [(cp, off, w)]) for i, cp, off, fp, w, s, rep, h, spec in rows]
    pieces = hosting.get('pieces') or []
    if pieces and all(len(p) == 4 and all(len(seg) == 4 for seg in p[3]) for p in pieces):
        # replica pooling (#471 bit side): (stage, replica, helper, [(child, family, off, w)]); the family is the copy
        out = []
        for s, rep, h, segs in pieces:
            if len({seg[0] for seg in segs}) != 1:
                return None  # a residual over two children: not this layout's contract, reported as not parsed
            out.append((s, (rep, h), segs[0][0], [(fam, off, w) for _, fam, off, w in segs]))
        return out
    return _rows_of_job2(hosting)


L.rows_of = rows_of  # audit() looks the layout reader up at call time


def audit_pooled(t):
    """#496's cross-replica whole-owner layout (`hosting.pooled_slots`), checked from the template alone.

    Every hosted (child, family) must be tiled exactly from coordinate 0: up to the stated `hosted` count when a
    paid remainder record exists (remainder at pending_offset == hosted), else over the child's whole rank.
    Family numbering is inferred, then verified on every slot: family = replica*F + (2*pair+side)*P
    + port, with P = ports and F = 4*2*P families per replica. Windows are re-derived from the cover-sweep schedule:
    a child of pair p admits the stages of local sweeps strictly between the last local sweep or bridge touching p
    and the child's idle sweep, on stages whose active pair (from `calls`) is not p.
    """
    ho, slots = t['hosting'], t['hosting']['pooled_slots']
    P = 1 + max(s['port'] for s in slots)
    F = 8 * P
    pair_of_stage = {}
    for c in t['calls']:
        assert pair_of_stage.setdefault(c['stage'], c['pair']) == c['pair']
    last, allowed, child_pair, local_stages = {}, {}, {}, []
    for pos, e in enumerate(t['execution_schedule']):
        k = e.get('kind')
        if k == 'local_cover_sweep':
            local_stages.append((pos, e['stage']))
            last[pair_of_stage[e['stage']]] = pos
        elif k == 'bridge':
            last[e['src']] = last[e['dst']] = pos
        elif k == 'idle_cover_sweep':
            lo = last.get(e['pair'], -1)
            for ci in e['child_indices']:
                child_pair[ci] = e['pair']
                allowed[ci] = {s for q, s in local_stages if lo < q < pos and pair_of_stage[s] != e['pair']}
    helper = Counter((s['stage'], s['replica'], s['helper']) for s in slots)
    per_call = Counter((s['stage'], s['replica'], s['family']) for s in slots)
    remainder = {(r['child'], r['family']): r for r in t['idle_children']}
    coords, bad_family, bad_window, outside = defaultdict(list), 0, 0, 0
    for s in slots:
        f = s['family']
        rep, pair, port = f // F, (f % F) // (2 * P), f % P
        bad_family += (rep != s['owner_replica'] or port != s['port'] or pair != child_pair.get(s['child']))
        bad_window += s['stage'] not in allowed.get(s['child'], ())
        coords[(s['child'], f)].append((s['offset'], s['offset'] + s['width']))
    child_rank = defaultdict(set)
    for (ci, f), r in remainder.items():
        child_rank[ci].add(r['hosted'] + r['rank'])
    overlaps = fully_hosted = 0
    for key, iv in coords.items():
        iv.sort()
        overlaps += sum(a[1] > b[0] for a, b in zip(iv, iv[1:]))
        tiles = iv[0][0] == 0 and all(a[1] == b[0] for a, b in zip(iv, iv[1:]))
        r = remainder.get(key)
        if r is None:  # no paid remainder: the hosted intervals must tile the whole child
            fully_hosted += 1
            ranks = child_rank.get(key[0], set())
            outside += not (tiles and len(ranks) == 1 and iv[-1][1] == next(iter(ranks)))
        else:          # hosted [0, hosted), paid remainder [hosted, hosted + rank)
            outside += not (tiles and iv[-1][1] == r['hosted'] == r['pending_offset'])
    return dict(version=t.get('version'), layout='pooled_slots', parsed=True, hosted_residuals=len(slots),
                hosted_coordinates=sum(s['width'] for s in slots), cross_copy_residuals=0,
                helpers_in_more_than_one_row=sum(n > 1 for n in helper.values()),
                distinct_helper_occurrences=len(helper),
                cross_replica_slots=sum(s['owner_replica'] != s['replica'] for s in slots),
                helpers_per_family_per_call_max=max(per_call.values()),
                family_numbering_mismatches=bad_family, interval_overlaps=overlaps,
                children_fully_hosted=fully_hosted, children_with_paid_remainder=len(coords) - fully_hosted,
                intervals_outside_child_rank=outside, rows_outside_stored_window=bad_window,
                child_ranks_constant=all(len(v) == 1 for v in child_rank.values()),
                window_rederivation=dict(children=len(allowed), mismatched_children=[], n_mismatched=0,
                                         note='windows are not stored in this layout; rows_outside_stored_window '
                                              'counts slots outside the re-derived window'))


def owner_summary(t):
    calls = t.get('calls')
    if not isinstance(calls, list) or not calls or not isinstance(calls[0], dict) or 'owners' not in calls[0]:
        return None
    kinds, per_call, shared, worst, alias = Counter(), Counter(), 0, 0, 0
    for c in calls:
        owners = c['owners']
        per_call[len(owners)] += 1
        fam = Counter(o[0] for o in owners)
        shared += sum(n > 1 for n in fam.values())
        worst = max(worst, max(fam.values()))
        seen = Counter(json.dumps(o, sort_keys=True) for o in owners)
        alias += sum(n - 1 for n in seen.values() if n > 1)
        for o in owners:
            d = o[1] if isinstance(o, (list, tuple)) and len(o) > 1 else None
            kinds[str(d[0]) if isinstance(d, list) and d else type(d).__name__] += 1
    return dict(calls=len(calls), owners_per_call=dict(per_call), owner_kinds=dict(kinds),
                families_shared_within_a_call=shared, max_owners_per_family_in_a_call=worst,
                identical_owner_entries_within_a_call=alias)


def records_of(run):
    run = Path(run)
    for d in (run / 'records', run / 'repair' / 'records'):
        for p in sorted(d.glob('pr-*.json')) if d.exists() else []:
            r = json.loads(p.read_text())
            if r.get('output'):
                yield ('repair' if d.parent.name == 'repair' else 'as-is'), r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--run', action='append', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    by_sha, refs = {}, defaultdict(list)
    for run in a.run:
        for attempt, r in records_of(run):
            for tpl in r.get('templates', []):
                refs[tpl['sha256']].append(dict(pr=r['pr'], attempt=attempt, path=tpl['path']))
                if tpl['sha256'] in by_sha:
                    continue
                p = Path(r['output']) / tpl['path']
                if not p.exists():
                    continue
                raw = p.read_bytes()
                assert hashlib.sha256(raw).hexdigest() == tpl['sha256'], p
                t = json.loads(gzip.decompress(raw) if p.name.endswith('.gz') else raw)
                ho = t.get('hosting')
                if isinstance(ho, dict) and 'pooled_slots' in ho:
                    res = audit_pooled(t)
                elif isinstance(ho, dict):
                    res = L.audit(t)
                else:
                    res = dict(version=t.get('version'), layout=None)
                own = owner_summary(t)
                if own is not None:
                    res['owners'] = own
                if res.get('layout') or own is not None:
                    by_sha[tpl['sha256']] = res
    ledger = [dict(sha256=sha, referenced_by=refs[sha], **res) for sha, res in by_sha.items()]
    ledger.sort(key=lambda x: (min(r['pr'] for r in x['referenced_by']), str(x.get('version'))))
    hosted = [x for x in ledger if x.get('layout')]
    clean = [x for x in hosted if x.get('parsed')]
    summary = dict(templates=len(ledger), hosted_templates=len(hosted), parsed=len(clean),
                   with_cross_copy_residuals=sum(x['cross_copy_residuals'] > 0 for x in clean),
                   with_duplicate_helpers=sum(x['helpers_in_more_than_one_row'] > 0 for x in clean),
                   with_overlaps=sum(x['interval_overlaps'] > 0 for x in clean),
                   with_intervals_outside_rank=sum(x['intervals_outside_child_rank'] > 0 for x in clean),
                   with_rows_outside_window=sum(x['rows_outside_stored_window'] > 0 for x in clean),
                   with_window_mismatch=sum(isinstance(x['window_rederivation'], dict)
                                            and x['window_rederivation']['n_mismatched'] > 0 for x in clean),
                   with_identical_owner_entries=sum(x.get('owners', {}).get('identical_owner_entries_within_a_call', 0) > 0
                                                    for x in ledger))
    Path(a.out).write_text(json.dumps(dict(summary=summary, templates=ledger), indent=1))
    print(json.dumps(summary, indent=1))
    for x in ledger:
        first = x['referenced_by'][0]
        own = x.get('owners')
        otxt = '' if own is None else (f" | owners/call {list(own['owners_per_call'])} kinds {own['owner_kinds']} "
                                       f"shared-family {own['families_shared_within_a_call']} max/family {own['max_owners_per_family_in_a_call']} "
                                       f"alias {own['identical_owner_entries_within_a_call']}")
        if not x.get('layout'):
            print(f"#{first['pr']:<4} {str(x['version']):<52} (no hosting section){otxt}  ({first['path']})")
        elif not x.get('parsed'):
            print(f"#{first['pr']:<4} {str(x['version']):<52} hosting not parsed {x.get('row_length')}{otxt}")
        else:
            wr = x['window_rederivation']
            wtxt = 'n/a' if isinstance(wr, str) else f"mismatch {wr['n_mismatched']}/{wr['children']}"
            print(f"#{first['pr']:<4} {str(x['version']):<52} rows {x['hosted_residuals']:>6} cross-copy {x['cross_copy_residuals']:>5} "
                  f"dup-helper {x['helpers_in_more_than_one_row']} overlap {x['interval_overlaps']} "
                  f"outside-rank {x['intervals_outside_child_rank']} outside-window {x['rows_outside_stored_window']} "
                  f"windows {wtxt}{otxt}  ({first['path']})")


if __name__ == '__main__':
    main()
