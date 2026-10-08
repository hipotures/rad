#!/usr/bin/env python3
"""Exact small counterexamples to fundamental-only and unguarded reclamation."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import textwrap


def run_case(module, values, frames, blocks, retired, anchors, assign=None,
             uses=None, include=False, bypass_guard=False):
    slots = list(values)
    physical = list(frames)
    stats = Counter()
    ops = []

    def contains(a, b):
        return not (a & ~b)

    def xor(a, b, g):
        assert a != b
        for role in (a, b):
            assert contains(blocks[physical[role]]['frame'], blocks[g]['frame'])
            physical[role] = g
        slots[a] ^= slots[b]
        ops.append((a, b))

    def new(g):
        slots.append(0)
        physical.append(g)
        return len(slots)-1

    environment = dict(reclaim=True, slots=slots, frames=physical,
                       blocks=blocks, retired=set(retired), stats=stats,
                       assign=assign or {}, uses=uses or [], step=0,
                       region_place={i: i for i in range(len(blocks))},
                       last_compatible=[10]*len(blocks), contains=contains,
                       xor=xor, new=new, CYCLE_POLICY='short-word',
                       CYCLE_EXACT_LIMIT=8, CYCLE_PAIR_LIMIT=256)
    source = module.prepare_acquire(include)
    if bypass_guard:
        guard = '    if not all(contains(blocks[g][\'frame\'],blocks[target][\'frame\']) for target in targets):continue'
        assert source.count(guard) == 1
        source = source.replace(guard, '    # Deliberate negative control: omitted future guard')
    exec(compile(textwrap.dedent(source), '<exact-clearing-discriminator>', 'exec'), environment)
    selected = environment['acquire'](0, anchors)
    return dict(selected=selected, operations=ops,
                source_vector_after=slots[selected], stats=dict(stats),
                allocated_fresh_role=selected >= len(values))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--driver', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    path = Path(args.driver)
    spec = importlib.util.spec_from_file_location('nullspace_driver', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    block = dict(frame=7, rank=3)

    # Two independent relations share two donors. Their sum clears an earlier
    # retired target with two gates instead of its three-gate fundamental word.
    pair = run_case(module, [1, 2, 4, 7, 3], [0]*5, [block], {3, 4}, [0, 1, 2])
    assert pair['selected'] == 3 and len(pair['operations']) == 2
    assert pair['source_vector_after'] == 0
    assert pair['stats']['combined_zero_relations_selected'] == 1

    # A dependence entirely among anchors shortens the sole retired relation.
    values = [1, 2, 3, 4, 7]
    old = run_case(module, values, [0]*5, [block], {4}, [0, 1, 2, 3])
    full = run_case(module, values, [0]*5, [block], {4}, [0, 1, 2, 3], include=True)
    assert len(old['operations']) == 3 and len(full['operations']) == 2
    assert old['selected'] == full['selected'] == 4
    assert old['source_vector_after'] == full['source_vector_after'] == 0
    assert full['stats']['anchor_zero_relations'] == 1

    # The local signal relation alone is legal, but a live donor has a later
    # narrower frame. The real guard must refuse it; the omitted guard fails
    # that exact continuation containment even though scalar clearing succeeds.
    guarded_blocks = [dict(frame=3, rank=2), dict(frame=1, rank=1),
                      dict(frame=1, rank=1)]
    parameters = dict(values=[1, 3, 2], frames=[0, 1, 1], blocks=guarded_blocks,
                      retired={1}, anchors=[0], assign={0: 2}, uses=[(2, 2, None)])
    guarded = run_case(module, **parameters, include=True)
    omitted = run_case(module, **parameters, include=True, bypass_guard=True)
    assert guarded['allocated_fresh_role']
    assert omitted['selected'] == 1 and omitted['source_vector_after'] == 0
    illegal_future_inclusion = bool(guarded_blocks[0]['frame'] & ~guarded_blocks[2]['frame'])
    assert illegal_future_inclusion

    # Omitting one real clearing gate must leave a nonzero source signal.
    wrong = list(values)
    for a, b in full['operations'][:-1]:
        wrong[a] ^= wrong[b]
    assert wrong[4] != 0

    result = dict(status='EXACT SMALL DISCRIMINATORS PASS',
                  driver_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  pair_cancellation=pair,
                  fundamental_only_anchor_control=old,
                  complete_admitted_pool_kernel=full,
                  guarded_late_donor=guarded,
                  omitted_late_guard=omitted,
                  negative_controls=dict(omitted_guard_future_inclusion_fails=illegal_future_inclusion,
                                         omitted_clearing_gate_residual=wrong[4]),
                  scope='Small exact signal/frame discriminators. These do not certify native rational profiles, dirty-address schedules or an exponent.')
    output = Path(args.output)
    assert not output.exists()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
