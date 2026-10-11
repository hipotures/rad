#!/usr/bin/env python3
"""Mutation controls for job5_hosting_ledger.audit_pooled on a real pooled template (seconds).

The unmodified template must pass every check; each mutation must be flagged by the check it targets:
  stage-in-active   move one slot to a stage where its host's pair is active (window)
  duplicate         host one helper occurrence twice (duplicate helper)
  overlap           shift one slot onto its neighbour's coordinates (overlap / tiling)
  drop              remove one slot (tiling of its child)
  foreign-family    relabel one slot to a family of another replica without updating owner_replica (numbering)
  same-call-family  give two helpers of one invocation the same host family (one owner per family per call)

usage: test_job5_ledger_mutations.py <pooled GLOBAL-TEMPLATE.json.gz>
"""
import copy
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from job5_hosting_ledger import audit_pooled  # noqa: E402

CHECKS = ('helpers_in_more_than_one_row', 'family_numbering_mismatches', 'interval_overlaps',
          'intervals_outside_child_rank', 'rows_outside_stored_window')


def flags(res):
    out = {k: res[k] for k in CHECKS if res[k]}
    if res['helpers_per_family_per_call_max'] > 1:
        out['helpers_per_family_per_call_max'] = res['helpers_per_family_per_call_max']
    return out


def main():
    t = json.loads(gzip.decompress(Path(sys.argv[1]).read_bytes()))
    base = flags(audit_pooled(t))
    failures = [] if not base else ['unmodified template flagged']
    print(('ok   ' if not base else 'FAIL ') + f'unmodified template: {base or "no flags"}')
    slots = t['hosting']['pooled_slots']
    pair_of_stage = {c['stage']: c['pair'] for c in t['calls']}
    P = 1 + max(s['port'] for s in slots)
    i0 = next(i for i, s in enumerate(slots) if s['offset'] == 0 and any(
        o['family'] == s['family'] and o['child'] == s['child'] and o['offset'] == s['width'] for o in slots))

    def mutated(fn):
        m = copy.deepcopy(t)
        fn(m['hosting']['pooled_slots'])
        return flags(audit_pooled(m))

    def stage_in_active(sl):
        s = sl[i0]
        pair = (s['family'] % (8 * P)) // (2 * P)
        s['stage'] = next(st for st, p in pair_of_stage.items() if p == pair)

    def duplicate(sl):
        sl.append(dict(sl[i0]))

    def overlap(sl):
        nb = next(o for o in sl if o['family'] == sl[i0]['family'] and o['child'] == sl[i0]['child']
                  and o['offset'] == sl[i0]['width'])
        nb['offset'] -= 1

    def drop(sl):
        del sl[i0]

    def foreign_family(sl):
        sl[i0]['family'] = (sl[i0]['family'] + 8 * P) % (8 * P * (1 + max(s['owner_replica'] for s in sl)))

    def same_call_family(sl):
        s = sl[i0]
        other = next(o for o in sl if o is not s and (o['stage'], o['replica']) == (s['stage'], s['replica'])
                     and o['family'] != s['family'])
        other['family'] = s['family']

    want = dict(stage_in_active='rows_outside_stored_window', duplicate='helpers_in_more_than_one_row',
                overlap='interval_overlaps', drop='intervals_outside_child_rank',
                foreign_family='family_numbering_mismatches', same_call_family='helpers_per_family_per_call_max')
    for name, fn in (('stage_in_active', stage_in_active), ('duplicate', duplicate), ('overlap', overlap),
                     ('drop', drop), ('foreign_family', foreign_family), ('same_call_family', same_call_family)):
        f = mutated(fn)
        ok = want[name] in f
        print(('ok   ' if ok else 'FAIL ') + f'{name}: {f}')
        failures += [] if ok else [name]
    print(f'\n{len(failures)} failure(s)')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
