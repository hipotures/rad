#!/usr/bin/env python3
"""Conjugate a frozen physical word by one address-coordinate permutation.

This does not rerun scalar input grouping or carrier matching. The scalar
roles, sources, XORs, events and dispatch are identical. Every address frame
and terminal label is transformed, then the independent full literal-word
checker reconstructs source supports, both dirty orientations and the actual
transition binary. A separately transformed original binary must agree byte
for byte. Exact CRT profiles are obtained from that reconstructed binary.
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
from itertools import combinations
import json
from pathlib import Path
import struct
import subprocess
import sys

from signed_positive_frame_interfaces import columns, normalize


def record(path):
    data = path.read_bytes()
    return {"path": str(path), "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}


def conjugate_frame(frame, order):
    rank, forced, symbols = frame
    return [rank, sum(((forced >> j) & 1) << i
                     for i, j in enumerate(order)),
            [symbols[j] for j in order]]


def conjugate_binary(data, order):
    h, v, roles, nf, nt, singles, mass, loss = struct.unpack_from('<6I2Q', data)
    assert len(order) == h
    output = bytearray(data[:40])
    offset = 40
    for _ in range(nf):
        forced, rank = struct.unpack_from('<QI', data, offset)
        symbols = struct.unpack_from('<' + str(h) + 'b', data, offset + 12)
        r, f, s = conjugate_frame((rank, forced, symbols), order)
        output.extend(struct.pack('<QI', f, r))
        output.extend(struct.pack('<' + str(h) + 'b', *s))
        offset += 12 + h
    assert offset + 16 * nt == len(data)
    output.extend(data[offset:])
    return bytes(output)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--graph-receipt', type=Path, required=True)
    ap.add_argument('--order-config', type=Path, required=True)
    ap.add_argument('--checker', type=Path, required=True)
    ap.add_argument('--native', type=Path, required=True)
    ap.add_argument('--basis', required=True)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.work.exists() and not args.output.exists()
    graph = json.loads(args.graph_receipt.read_text())
    proof = graph['independent']
    assert graph['source_only'] and proof['frame_format'] == 'positive-signed-v1'
    word_path = Path(proof['word_path'])
    packed = word_path.read_bytes()
    raw = gzip.decompress(packed)
    assert hashlib.sha256(raw).hexdigest() == proof['word_sha256']
    assert hashlib.sha256(packed).hexdigest() == proof['word_gzip_sha256']
    word = json.loads(raw)
    h = word['h']
    configuration = json.loads(args.order_config.read_text())
    order = configuration['order']
    assert sorted(order) == list(range(h))
    inverse = [0] * h
    for i, j in enumerate(order):
        inverse[j] = i
    old_q = word['source_permutation']
    assert old_q == graph['source_permutation'] == proof['source_permutation']
    new_q = [inverse[j] for j in old_q]
    transformed = dict(word)
    transformed['frames'] = [conjugate_frame(f, order) for f in word['frames']]
    transformed['source_permutation'] = new_q
    triples = list(combinations(range(h), 3))
    lookup = {t: i for i, t in enumerate(triples)}
    labels = [lookup[tuple(sorted(new_q[j] for j in t))] for t in triples]
    transformed['source_label_permutation'] = labels
    transformed['source_label_inverse'] = [0] * len(labels)
    for i, j in enumerate(labels):
        transformed['source_label_inverse'][j] = i
    transformed['outputs'] = [
        [slot, frame, inverse[common], sorted(inverse[j] for j in target)]
        for slot, frame, common, target in word['outputs']]
    for key in ('h', 'v', 'R', 'sources', 'ops', 'events', 'scatter', 'frame_format'):
        assert transformed[key] == word[key]
    # Integer-column covariance holds for EVERY actual frame, including signed
    # components and copied centers. H0=I-J/9 and L_beta=I-beta J commute with
    # every permutation; all column Gram products are consequently preserved.
    column_count = 0
    for old, new in zip(word['frames'], transformed['frames']):
        before, after = columns(normalize(old)), columns(normalize(new))
        assert after == tuple(tuple(v[j] for j in order) for v in before)
        column_count += len(before)
    args.work.mkdir(parents=True)
    changed_word = args.work / 'word.json.gz'
    changed_raw = json.dumps(transformed, separators=(',', ':')).encode()
    changed_word.write_bytes(gzip.compress(changed_raw, mtime=0))
    transitions = args.work / 'signed-transitions.bin'
    # The checker is an independently authored full source-support/F2/physical
    # replay, rather than a digest reader or a replay of candidate assertions.
    with (args.work / 'independent-word-check.log').open('x') as log:
        subprocess.run([sys.executable, str(args.checker), '--word', str(changed_word),
                        '--transitions', str(transitions)], stdout=log,
                       stderr=subprocess.STDOUT, check=True)
    independent_path = Path(str(transitions) + '.review.json')
    independent = json.loads(independent_path.read_text())
    old_binary = Path(proof['transition_path'])
    assert record(old_binary)['sha256'] == proof['transition_sha256']
    assert transitions.read_bytes() == conjugate_binary(old_binary.read_bytes(), order)
    assert independent['R'] == word['R'] and independent['rank_mass'] == proof['rank_mass']
    profile_path = args.work / 'profile.json'
    audit_path = args.work / 'transition-profiles.json'
    with (args.work / 'native-profile.log').open('x') as log:
        subprocess.run([str(args.native), str(transitions), args.basis,
                        str(profile_path), str(audit_path)], stdout=log,
                       stderr=subprocess.STDOUT, check=True)
    profile = json.loads(profile_path.read_text())
    assert profile['R'] == word['R'] and profile['rank_sum'] == independent['rank_mass']
    assert sum(i*n for i, n in enumerate(profile['blocks'])) == independent['rank_mass']
    result = {
        'utc': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS FIXED-WORD COORDINATE CONJUGATION AND EXACT CRT PROFILE',
        'classification': 'EXACT CANDIDATE; full recurrence and assembly pending',
        'h': h, 'v': word['v'], 'R': word['R'], 'basis': args.basis,
        'source': record(Path(__file__)), 'parent_graph_receipt': record(args.graph_receipt),
        'order_config': record(args.order_config), 'order': order, 'inverse_order': inverse,
        'parent_coordinate_order': old_q, 'coordinate_order': new_q,
        'integer_frame_columns_checked': column_count,
        'literal_scalar_and_binary_operations_preserved': True,
        'address_covariance': 'M_new[i,j]=M_old[order[i],order[j]]. All signed integer columns transform by this same permutation. Since H0=I-J/9 and L_beta=I-beta J commute with permutations, their rational projectors conjugate exactly.',
        'source_and_DATA_scope': 'The new coherent source triple map is inverse_order composed with the old source permutation. The complete Cartesian triple family is unchanged as a set; DATA reuse still requires the separately audited normalized source, terminal and center interface.',
        'independent_word_checker': record(args.checker),
        'independent_word_receipt': record(independent_path),
        'independent': independent,
        'word': record(changed_word),
        'transition': record(transitions),
        'binary_identity_scope': 'Independent transitions reconstructed from the transformed executed word equal the separately coordinate-conjugated parent binary byte for byte; role and rank denominators are preserved.',
        'native_profile': record(profile_path), 'native_audit': record(audit_path),
        'profile': profile,
        'limitations': 'The all-size address compiler, routing, prime setup, fixed tapes and analytic assembly remain conditional inherited interfaces. This receipt proves no kappa and adds no scalar graph input-order experiment.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'h', 'R', 'basis', 'order')}))


if __name__ == '__main__':
    main()
