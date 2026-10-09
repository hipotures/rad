#!/usr/bin/env python3
"""Final bounded unequal-frame continuation from the best frozen endpoint plan.

Reconstruct the complete earlier seed selections, exclude every previously
tested seed in its corresponding direction, and examine the remaining seeds
in exactly two bounded passes. The fixed scalar word, gauges, aliases and read
deadlines are unchanged. All actual edge occurrences, G-nondegeneracy, source
and dirty F2 columns, full fallback moments and prime units are checked anew.
Prepared for RaD with OpenAI assistance; inherited source credits persist.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import json
from pathlib import Path
import random
import resource
import sys
import time

sys.dont_write_bytecode = True
from bit_current_control import HEAD, METHOD_HEAD, need, sha, read, modules, source_pins
from bit_current_discriminators import physical_experiment, global_bounds, closure_proposal
from audit_bit_projectors import audit


def earlier_selections(e, prior):
    """Recover both full old seed sets without retesting old rejected seeds.

    Lower seeds were ordered after the four accepted raise closures. Recreate
    exactly those accepted changes, checking their changed operation indices
    and complete moment, before recovering the lower order. No saved frame IDs
    are interpreted in a different interning context.
    """
    low, high = global_bounds(e)
    rng = random.Random(prior['protocol']['seed'])
    count = prior['protocol']['seed_limit']
    seeds = list(range(e.N))
    rng.shuffle(seeds)
    seeds.sort(key=lambda i: -(e.T.dim(high[i])-e.T.dim(e.frames[i])))
    old_raise = seeds[:count]
    accepted = [m for m in prior['mechanism']['moves'] if m['direction'] == 'raise']
    need([m['seed'] for m in accepted] == [i for i in old_raise if i in {m['seed'] for m in accepted}],
         'old accepted raises have the saved seed order')
    reconstructed = []
    for saved in accepted:
        plan, status = closure_proposal(e, low, high, saved['seed'], 'raise', prior['protocol']['max_nodes'])
        need(status == 'accepted', 'saved accepted raise reconstructs')
        need([i for i, _ in plan['frames']] == [i for i, _ in saved['frames']],
             'saved raise affects the same actual operations')
        need(abs(plan['delta_excess_local']-saved['delta_excess_local']) < 1e-14,
             'saved raise complete paid delta reconstructs')
        for i, f in plan['frames']:
            e.frames[i] = f
        reconstructed.append(dict(seed=saved['seed'], operations=[i for i, _ in plan['frames']],
                                  delta_excess_local=plan['delta_excess_local']))
    need(abs(e.profile()['numerical_root']-prior['mechanism']['passes'][0]['root']) < 1e-15,
         'complete post-raise characteristic agrees with old pass')
    seeds = list(range(e.N))
    rng.shuffle(seeds)
    seeds.sort(key=lambda i: -(e.T.dim(e.frames[i])-e.T.dim(low[i])))
    old_lower = seeds[:count]
    need(len(set(old_raise)) == len(set(old_lower)) == count, 'complete unique old directional seed sets')
    return old_raise, old_lower, reconstructed


def main():
    need(not sys.flags.optimize, 'assertions enabled')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--source170', type=Path, required=True)
    ap.add_argument('--control', type=Path, required=True)
    ap.add_argument('--endpoint', type=Path, required=True)
    ap.add_argument('--prior-transitive', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--seed', type=int, default=20261009)
    ap.add_argument('--max-nodes', type=int, default=128)
    args = ap.parse_args()
    started = time.monotonic()
    output = args.output.resolve()
    need(not output.exists(), 'fresh final continuation run ID')
    need(args.max_nodes == 128, 'authorized closure bound fixed at128 operations')
    output.mkdir(parents=True)
    endpoint = read(args.endpoint / 'result.json')
    prior = read(args.prior_transitive / 'result.json')
    own = Path(__file__).parent
    for filename, digest in prior['protocol']['code_sha256'].items():
        need(sha(own / filename) == digest, 'unchanged old seed policy code ' + filename)
    protocol = dict(source_head=HEAD, method_head=METHOD_HEAD, seed=args.seed, max_nodes=args.max_nodes,
                    passes_max=2, directions=['raise', 'lower'], workers=1, numerical_library_threads=1,
                    source_files=source_pins(args.source.resolve(), args.source170.resolve()),
                    endpoint_plan_sha256=sha(args.endpoint / 'selected/frames.json'),
                    endpoint_profile_sha256=sha(args.endpoint / 'selected/profile.json'),
                    endpoint_coarse=endpoint['native_moment']['saving'],
                    prior_transitive_result_sha256=sha(args.prior_transitive / 'result.json'),
                    control_receipt_sha256=sha(args.control / 'receipt.json'),
                    code_sha256={p.name: sha(p) for p in [Path(__file__), own/'bit_current_discriminators.py',
                                      own/'bit_current_control.py', own/'audit_bit_projectors.py']},
                    started_utc=datetime.now(timezone.utc).isoformat(),
                    sufficient_native_coarse='656266512/1000000000000',
                    seed_policy='All operations not in the corresponding direction of the old8000-seed selection; gaps descending, fixed random tie order.',
                    scope='Final targeted binary continuation; no final multiplication kappa.')
    (output / 'protocol.json').write_text(json.dumps(protocol, indent=2, sort_keys=True) + '\n')
    _, physical, lifetime, params = modules(args.source.resolve(), args.source170.resolve())
    e = physical_experiment(lifetime, physical, args.control.resolve())
    old_raise, old_lower, old_reconstruction = earlier_selections(e, prior)
    # A complete fixture is defined against named node frames, not against
    # whichever public or reconstructed partial physical plan is in memory.
    e.frames = list(e.base_frames)
    e.load(args.endpoint / 'selected/frames.json', require_pins=True)
    start_profile = e.verified_profile(replay=True)
    need(start_profile == read(args.endpoint / 'selected/profile.json'),
         'fresh complete best endpoint plan, F2 columns and paid profile match')
    need(start_profile['changed_operation_frames'] == 4212, 'best frozen endpoint identity')
    initial_frames = list(e.frames)
    low, high = global_bounds(e)
    tested = {'raise': set(old_raise), 'lower': set(old_lower)}
    inventory = [dict(operation=i, destination=e.ops[i][0], control=e.ops[i][1], node=e.ops[i][2],
                      endpoint_rank=e.T.dim(e.frames[i]), global_lower_rank=e.T.dim(low[i]),
                      global_upper_rank=e.T.dim(high[i]), old_raise_tested=i in tested['raise'],
                      old_lower_tested=i in tested['lower']) for i in range(e.N)]
    (output / 'complete-operation-seed-inventory.json').write_text(json.dumps(dict(
        operations=inventory, previous_raise_order=old_raise, previous_lower_order=old_lower,
        reconstructed_previous_accepted_raises=old_reconstruction), separators=(',', ':'), sort_keys=True) + '\n')
    print(json.dumps(dict(stage='best endpoint and complete prior seed inventory reconstructed',
                         seconds=time.monotonic()-started, operations=e.N,
                         previously_tested_raise=len(old_raise), previously_tested_lower=len(old_lower),
                         remaining_per_direction=e.N-len(old_raise), starting_coarse=protocol['endpoint_coarse'])), flush=True)
    rng = random.Random(args.seed)
    moves, obstructions, passes = [], [], []
    for direction in ('raise', 'lower'):
        seeds = [i for i in range(e.N) if i not in tested[direction]]
        rng.shuffle(seeds)
        seeds.sort(key=lambda i: -(e.T.dim(high[i])-e.T.dim(e.frames[i]) if direction == 'raise'
                                  else e.T.dim(e.frames[i])-e.T.dim(low[i])))
        need(set(seeds) | tested[direction] == set(range(e.N)) and not set(seeds) & tested[direction],
             'complete disjoint old/new seed partition')
        (output / (direction+'-complete-untested-seed-order.json')).write_text(json.dumps(seeds) + '\n')
        counts = Counter()
        tick = time.monotonic()
        for offset, i in enumerate(seeds):
            plan, status = closure_proposal(e, low, high, i, direction, args.max_nodes)
            counts[status] += 1
            if status == 'accepted':
                for j, f in plan['frames']:
                    e.frames[j] = f
                moves.append(plan)
            elif status == 'degenerate' and len(obstructions) < 8:
                obstructions.append(plan)
            if (offset+1) % 8000 == 0:
                print(json.dumps(dict(direction=direction, examined=offset+1, total=len(seeds),
                                     counts=dict(counts), seconds=time.monotonic()-tick)), flush=True)
        e.check()
        row = e.profile()
        summary = dict(direction=direction, seeds=len(seeds), counts=dict(counts),
                       wall_seconds=time.monotonic()-tick, numerical_root=row['numerical_root'])
        passes.append(summary)
        print(json.dumps(summary), flush=True)
    profile = e.save(output / 'selected', replay=True)
    native = params.select_supplier(params.counts(profile), bit=True)
    target = Fraction(656266512, 10**12)
    target_bounds = params.interval_moment(params.counts(profile), target, bit=True)
    need(native['saving'] >= Fraction(endpoint['native_moment']['saving']), 'complete paid native moment does not worsen')
    atom = params.choose_atom(native['saving'])
    prime = audit(e)
    (output / 'prime-witnesses.json').write_text(json.dumps(prime, indent=2, sort_keys=True) + '\n')
    compact_prime = {k: v for k, v in prime.items() if k != 'frame_witnesses'}
    result = dict(status='PASS_SOURCE_BOUND_FINITE_WITH_PRIME', protocol=protocol,
                  initial_profile=start_profile, profile=profile, passes=passes,
                  accepted_closures=len(moves), exact_degenerate_examples=obstructions,
                  changed_operations_from_endpoint=sum(a != b for a, b in zip(initial_frames, e.frames)),
                  native_moment=native, paid_atom=atom,
                  sufficient_target=target, sufficient_target_interval=target_bounds,
                  sufficient_target_passes=target_bounds[1] < 1,
                  prime_receipt=compact_prime,
                  plan_sha256=sha(output / 'selected/frames.json'), profile_sha256=sha(output / 'selected/profile.json'),
                  complete_inventory_sha256=sha(output / 'complete-operation-seed-inventory.json'),
                  wall_seconds=time.monotonic()-started, peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  exclusions=['independent full reflected physical-event audit', 'complete same-source final assembly'])
    (output / 'result.json').write_text(json.dumps(params.js(result), indent=2, sort_keys=True) + '\n')
    (output / 'moment.json').write_text(json.dumps(params.js(native), indent=2, sort_keys=True) + '\n')
    (output / 'accepted-closure-moves.json').write_text(json.dumps(moves, separators=(',', ':'), sort_keys=True) + '\n')
    (output / 'prime-receipt.json').write_text(json.dumps(compact_prime, indent=2, sort_keys=True) + '\n')
    print(json.dumps(dict(status=result['status'], seconds=result['wall_seconds'],
                         accepted_closures=len(moves), changed_operations_from_endpoint=result['changed_operations_from_endpoint'],
                         coarse=str(native['saving']), ordinary=str(atom['effective_saving']),
                         sufficient_target=str(target), sufficient_target_passes=result['sufficient_target_passes'],
                         all_used_prime_frames=prime['actual_used_frames'])), flush=True)


if __name__ == '__main__':
    main()
