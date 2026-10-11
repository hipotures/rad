#!/usr/bin/env python3
"""Re-optimize carriers after genuinely changed scalar-future region merges.

Every region/frame and scalar coefficient is rebuilt from pinned PR62.
PR57's exact matroid capacities, invertible words and paid reclamation remain
literal. Actual rational matrix profiles guide matching; no weighted optimum
is claimed. The complete compiled word receives independent role replay and
fresh CRT profiles before any full recurrence/assembly claim is considered.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
import time

import joint_region_search_v3 as region
import joint_signed_word_recompile as joint
from joint_scalar_future_frames import assign, write_word
from joint_actual_future_recompile import transform
from matrix_weighted_joint_carriers import weighted_matcher
from source_only_matrix_weighted_joint import selected_match
from check_compiled_witness import contained
from joint_word_check_v4 import check

GEOMETRY = Path(__file__).resolve().parents[2] / 'geometry' / 'code'
sys.path.insert(0, str(GEOMETRY))
from decompose_common_context_profiles import pivot_run_histogram


def native(binary, transition, basis, target):
    target.mkdir(parents=True)
    profile, audit = target / 'profile.json', target / 'transitions.json'
    env = dict(os.environ)
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        env[key] = '1'
    command = [str(binary), str(transition), basis, str(profile), str(audit)]
    with (target / 'native.log').open('wb') as log:
        child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env)
        (target / 'process.json').write_text(json.dumps(dict(pid=child.pid, command=command), indent=2) + '\n')
        assert child.wait() == 0
    return json.loads(profile.read_text()), profile, audit


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--parents', type=Path, required=True)
    p.add_argument('--h', type=int, required=True)
    p.add_argument('--scope', choices=['all', 'terminal-only'], default='all')
    p.add_argument('--threshold', type=int, default=18)
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    start = time.monotonic()
    (args.work / 'process.json').write_text(json.dumps(dict(pid=os.getpid(), command=sys.argv,
        started_utc=datetime.now(timezone.utc).isoformat()), indent=2) + '\n')
    joint.initialize(args.source, args.work)
    document = next(d for d in json.loads(args.parents.read_text()) if d['h'] == args.h)
    h, Q = args.h, document['Q']
    config = {k: v for k, v in document['configuration'].items() if k != 'kind'}
    c, old_blocks, _, _, old_owner, _, _, _ = region.build_regions(h, config)
    labels, frame_summary = assign(c, old_blocks, old_owner, args.scope, args.threshold)
    built = joint.build(c, labels, old_owner, 'merge-aliases', 'original')
    _, blocks, uses, _, owner, _, order, _ = built
    # Discovery matrices use the final coherent source coordinate order.
    frames = [(0, 0, (0,) * h), (h, 0, (0,) * h)]
    lookup = {frame: i for i, frame in enumerate(frames)}
    ids = []
    for block in blocks:
        frame = transform(block['frame'], Q)
        if frame not in lookup:
            lookup[frame] = len(frames)
            frames.append(frame)
        ids.append(lookup[frame])
    pairs, zero = set(), set()
    carriers = []
    def add(a, b):
        A, B = frames[a], frames[b]
        if A[0] == B[0]:
            assert a == b or (contained(A, B) and contained(B, A))
            zero.add((a, b))
        else:
            assert A[0] < B[0] and (a == 0 or b == 1 or contained(A, B))
            pairs.add((a, b))
    for g, block in enumerate(blocks):
        for u, i in block['candidates']:
            value, target, terminal = uses[u]
            G, T, P = ids[g], ids[target], ids[owner[value]]
            for a, b in [(G, T), (G, 1), (0, P), (P, T)]:
                add(a, b)
            carriers.append((g, u, i, value, G, T, P))
    pairs = sorted(pairs)
    mass = sum(frames[b][0] - frames[a][0] for a, b in pairs)
    probe = args.work / 'carrier-cost-probe.bin'
    with probe.open('wb') as stream:
        stream.write(struct.pack('<6I2Q', h, len(c.inputs), 0, len(frames), len(pairs), 0, mass, 0))
        for rank, forced, symbols in frames:
            stream.write(struct.pack('<QI', forced, rank))
            stream.write(struct.pack('<' + str(h) + 'b', *symbols))
        for a, b in pairs:
            stream.write(struct.pack('<2Iq', a, b, 1))
    basis = 'beta:1:15' if h == 23 else 'beta:7:207'
    print(json.dumps(dict(status='NEW merged-future carrier matrices prepared', h=h,
                         regions=len(blocks), carriers=len(carriers), matrices=len(pairs))), flush=True)
    certified, probe_profile, probe_audit = native(args.binary, probe, basis, args.work / 'cost-probe')
    assert certified['R'] == 0 and certified['rank_sum'] == mass
    a = 1284995399 / 25000000000000
    costs = {pair: 0.0 for pair in zero}
    histograms = {}
    for row in json.loads(probe_audit.read_text())['transitions']:
        histogram = pivot_run_histogram(row['pivots'], 1)
        assert sum(t*n for t, n in histogram.items()) == row['rank']
        pair = row['a'], row['b']
        histograms[pair] = histogram
        costs[pair] = sum(t*n*math.expm1(a*math.log(575/t)) for t, n in histogram.items())
    total = Counter()
    for donor, recipient in pairs:
        pair = donor, recipient
        if pair not in histograms:
            rank = frames[recipient][0] - frames[donor][0]
            assert rank == 1 or pair == (0, 1)
            histograms[pair] = {rank: 1}
            costs[pair] = rank * math.expm1(a*math.log(575/rank))
        total.update(histograms[pair])
    assert [total[t] for t in range(h+1)] == certified['blocks']
    weights = {(g, u, i): costs[G, 1] + costs[0, P] + costs[P, T] - costs[G, T]
               for g, u, i, value, G, T, P in carriers}
    assert len(weights) == len(carriers)
    edges, chosen, _, _ = weighted_matcher(weights, 'gain-first')(blocks, uses, True)
    selection = [edges[e] for e in sorted(chosen)]
    selected_match(blocks, uses, order, selection)
    selected_path = args.work / 'selected-matching.json'
    selected_path.write_text(json.dumps(dict(h=h, parent=document, scope=args.scope, threshold=args.threshold,
        Q=Q, selected=selection), separators=(',', ':')) + '\n')
    region.COMPILER.build = lambda dim: built
    region.COMPILER.match = lambda bs, us, enabled: selected_match(bs, us, order, selection)
    compiled, word = region.COMPILER.compile_(h, matching=True, reclaim=True, dirty=True)
    word = joint.canonicalize(word, Q)
    word_path = args.work / 'word.json.gz'
    word_sha = write_word(word_path, word)
    transition = args.work / 'signed-transitions.bin'
    independent = check(word_path, transition)
    profile, profile_path, audit_path = native(args.binary, transition, basis, args.work / 'actual-word-profile')
    phi = sum(t*n*math.expm1(a*math.log(575/t)) for t, n in enumerate(profile['blocks']) if t and n)
    result = dict(status='EXACT CANDIDATE matrix-weighted genuinely merged scalar-future regions',
        h=h, case_id=f'h{h}-scalar-future-{args.scope}-{args.threshold}-matrix-gain-first',
        parent=document, configuration=dict(scope=args.scope, threshold=args.threshold, grouping='merge-aliases', basis=basis),
        frame_summary=frame_summary, scalar=c.verify(), old_regions=len(old_blocks),
        new_regions=len(blocks), compiled=compiled, independent=independent,
        selected_carriers=len(selection), selected_matching_path=str(selected_path),
        selected_matching_sha256=sha256(selected_path.read_bytes()).hexdigest(),
        cost_probe=dict(rank_mass=mass, carriers=len(carriers), matrices=len(pairs),
                        input_sha256=sha256(probe.read_bytes()).hexdigest(), profile_path=str(probe_profile), audit_path=str(probe_audit)),
        word_path=str(word_path), word_sha256=word_sha, profile=profile,
        profile_path=str(profile_path), profile_sha256=sha256(profile_path.read_bytes()).hexdigest(),
        transition_audit=str(audit_path), transition_audit_sha256=sha256(audit_path.read_bytes()).hexdigest(),
        screen_a=a, screen_Phi=phi, seconds=time.monotonic()-start,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        completed_utc=datetime.now(timezone.utc).isoformat(),
        limitations='Exact scalar/frame/physical/matrix candidate, not an accepted exponent. Fresh selected-only reproduction, independent source-pair DATA/stock, complete recurrence and 47+7 assembly plus inherited all-size gauge/tape assumptions remain separate.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], h=h, R=compiled['roles'], Phi=phi,
                         selected_carriers=len(selection), seconds=result['seconds'])), flush=True)


if __name__ == '__main__':
    main()
