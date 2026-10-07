"""Evaluate two frozen rank projections on fresh, causally available activations."""
import os
for key in ('OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'OMP_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import hashlib
import pathlib
import time
import numpy as np
from lab import save
from trace_reader import Trace

ACT = np.dtype([(x, '<u8') for x in ('window', 'available_ns', 'offset')] +
               [(x, '<i4') for x in ('layer', 'token_base', 'tokens', 'width')])
BOUND = np.dtype([(x, '<u8') for x in ('window', 'begin_ns', 'end_ns', 'bytes')] +
                 [(x, '<i4') for x in ('device', 'stage_begin', 'stage_end', 'kind')] +
                 [('gpu_ms', '<f4'), ('reserved', '<i4')])
assert ACT.itemsize == 40 and BOUND.itemsize == 56

def distribution(values):
    x = np.asarray(values, dtype=float)
    return dict(n=len(x), min=float(x.min()), median=float(np.median(x)),
                p95=float(np.percentile(x, 95)), max=float(x.max()), sum=float(x.sum())) if len(x) else None

ap = argparse.ArgumentParser()
ap.add_argument('prefix')
ap.add_argument('--output', required=True)
ap.add_argument('--factors', required=True)
ap.add_argument('--episode', required=True)
ap.add_argument('--split', choices=['development', 'calibration', 'holdout', 'benchmark'], required=True)
a = ap.parse_args()
prefix = str(pathlib.Path(a.prefix))
base = prefix.rsplit('-request', 1)[0]
trace = Trace(prefix)
validation = trace.validate()
assert validation['state'] == 'PASS'
activations = np.fromfile(prefix + '-activations.bin', ACT)
values = np.fromfile(prefix + '-activation-values.bin', '<f4')
boundaries = np.fromfile(prefix + '-boundaries.bin', BOUND)
assert len(activations) and np.isfinite(values).all()
factors = pathlib.Path(a.factors)
factors.mkdir(parents=True, exist_ok=True)
truth, observation, current = {}, {}, {}
for layer, entries in trace.grouped():
    w, l = int(layer['window']), int(layer['layer'])
    current[w, l] = np.concatenate([current[w, l], entries]) if (w, l) in current else entries
    for row in np.unique(entries['token']):
        key = w, l, int(row)
        truth[key] = entries[entries['token'] == row]
        observation[key] = int(layer['t0'])
events = []
for p in trace.promotions:
    events.append((int(p['issue']), 0, p))
    if p['observed_ready']:
        events.append((int(p['observed_ready']), 1, p))
events.sort(key=lambda e: (e[0], e[1]))
state, next_event = trace.initial.copy(), 0
gates, models, construction, records = {}, {}, {}, []
for capture in activations:
    layer, target = int(capture['layer']), int(capture['layer']) + 1
    w, first, n = int(capture['window']), int(capture['token_base']), int(capture['tokens'])
    width, available = int(capture['width']), int(capture['available_ns'])
    if target not in gates:
        raw = np.fromfile(base + f'-gate-layer{target}.bin', '<u2')
        assert raw.size == 512 * width
        gate = (raw.astype('<u4') << 16).view('<f4').reshape(512, width)
        assert np.isfinite(gate).all()
        gates[target] = gate
        factor_path = factors / f'layer{target}.npz'
        gate_hash = hashlib.sha256(raw.tobytes()).hexdigest()
        if factor_path.exists():
            loaded = np.load(factor_path)
            assert str(loaded['gate_sha256']) == gate_hash
            models[target] = {rank: (loaded[f'B{rank}'], loaded[f'U{rank}']) for rank in (32, 128)}
            energy = [float(loaded[f'energy{rank}']) for rank in (32, 128)]
            construction[target] = {'loaded': str(factor_path), 'gate_sha256': gate_hash,
                                    'energy_fraction': dict(zip((32, 128), energy))}
        else:
            begin = time.perf_counter()
            eigenvalues, eigenvectors = np.linalg.eigh(gate @ gate.T)
            order = np.argsort(eigenvalues)[::-1]
            eigenvalues = np.maximum(eigenvalues[order], 0)
            eigenvectors = eigenvectors[:, order]
            models[target], persisted, energy = {}, {'gate_sha256': gate_hash}, {}
            for rank in (32, 128):
                u = np.ascontiguousarray(eigenvectors[:, :rank], dtype=np.float32)
                b = np.ascontiguousarray(u.T @ gate, dtype=np.float32)
                models[target][rank] = b, u
                energy[rank] = float(eigenvalues[:rank].sum() / eigenvalues.sum())
                persisted.update({f'B{rank}': b, f'U{rank}': u, f'energy{rank}': energy[rank]})
            np.savez_compressed(factor_path, **persisted)
            construction[target] = {'elapsed_s': time.perf_counter() - begin,
                                    'gate_sha256': gate_hash, 'factor_path': str(factor_path),
                                    'energy_fraction': energy}
        # Warm numeric kernels before one cost observation per captured batch.
        z = np.zeros((n, width), dtype=np.float32)
        z @ gates[target].T
        for b, u in models[target].values():
            z @ b.T @ u.T
    at = int(capture['offset'])
    x = values[at:at + n * width].reshape(n, width)
    group = current[w, layer]
    group = group[(group['token'] >= first) & (group['token'] < first + n)]
    originally_fresh = bool(np.any(group['path'] != 0))
    while next_event < len(events) and events[next_event][0] <= available:
        _, kind, p = events[next_event]
        l = int(p['layer'])
        if kind == 0:
            outgoing_layer = int(p['outgoing_layer']) if 'outgoing_layer' in p.dtype.names else l
            state[outgoing_layer, int(p['outgoing'])] = -1
        else:
            state[l, int(p['incoming'])] = int(p['slot'])
        next_event += 1
    cold = boundaries[(boundaries['window'] == w) & (boundaries['kind'] == 5)]
    cold = bool(np.any(cold['end_ns'] - cold['begin_ns'] > 100000))
    # Rotate evaluation order; this is offline cost, not in-process contention.
    candidates = [0, 32, 128]
    shift = w % 3
    candidates = candidates[shift:] + candidates[:shift]
    for rank in candidates:
        begin = time.perf_counter_ns()
        scores = x @ gates[target].T if rank == 0 else x @ models[target][rank][0].T @ models[target][rank][1].T
        score_us = (time.perf_counter_ns() - begin) / 1000
        begin = time.perf_counter_ns()
        ids = np.argpartition(scores, -10, axis=1)[:, -10:]
        select_us = (time.perf_counter_ns() - begin) / 1000
        assert np.isfinite(scores).all()
        for row, predicted in enumerate(ids):
            key = w, target, first + row
            actual = truth[key]
            bad = actual[actual['path'] != 0]['expert']
            missing = predicted[state[target, predicted] < 0]
            matched_bad = np.intersect1d(bad, predicted)
            lead = (observation[key] - available) / 1000
            copies = {str(rate): float(trace.blob_bytes[target] / (rate * 1e9) * 1e6 + 4.2)
                      for rate in (12.6, 1.8)}
            records.append({'episode': a.episode, 'split': a.split, 'rank': rank,
                'window': w, 'current_layer': layer, 'target_layer': target, 'row': first + row,
                'batch_tokens': n, 'original_doorbell_would_copy_activation': originally_fresh,
                'fresh_diagnostic_copy_bytes': n * width * 4,
                'top10_matched': int(np.isin(predicted, actual['expert']).sum()),
                'true_nonlocal': len(bad), 'predicted_true_nonlocal': len(matched_bad),
                'predicted_current_nonresident': len(missing),
                'false_positive_nonresident': int(np.count_nonzero(~np.isin(missing, actual['expert']))),
                'lead_to_true_router_host_observation_us': lead,
                'batch_score_us': score_us, 'batch_top10_us': select_us,
                'cold_graph_capture_window': cold,
                'optimistic_one_blob_copy_us': copies,
                'optimistic_ready': {rate: score_us + select_us + cost < lead for rate, cost in copies.items()}})
summary = {}
for rank in (0, 32, 128):
    selected = [r for r in records if r['rank'] == rank]
    warm = [r for r in selected if not r['cold_graph_capture_window']]
    total_bad = sum(r['true_nonlocal'] for r in selected)
    proposals = sum(r['predicted_current_nonresident'] for r in selected)
    summary[str(rank)] = {'rows': len(selected),
        'top10_precision_pct': 100 * sum(r['top10_matched'] for r in selected) / (10 * len(selected)),
        'true_nonlocal_entries': total_bad,
        'nonlocal_recall_pct': 100 * sum(r['predicted_true_nonlocal'] for r in selected) / total_bad if total_bad else None,
        'predicted_nonresident_entries': proposals,
        'false_positive_nonresident_entries': sum(r['false_positive_nonresident'] for r in selected),
        'nonresident_proposal_precision_pct': 100 * sum(r['predicted_true_nonlocal'] for r in selected) / proposals if proposals else None,
        'warm_ready_fraction': {rate: sum(r['optimistic_ready'][rate] for r in warm) / len(warm) if warm else None for rate in ('12.6', '1.8')},
        'warm_ready_true_nonlocal_recall_pct': {rate: 100 * sum(r['predicted_true_nonlocal'] for r in warm if r['optimistic_ready'][rate]) / sum(r['true_nonlocal'] for r in warm) if sum(r['true_nonlocal'] for r in warm) else None for rate in ('12.6', '1.8')},
        'warm_lead_us': distribution([r['lead_to_true_router_host_observation_us'] for r in warm]),
        'batch_score_us': distribution([r['batch_score_us'] for r in selected]),
        'batch_top10_us': distribution([r['batch_top10_us'] for r in selected]),
        'CPU_factor_bytes': sum(g.nbytes for pair in models.values() for g in pair[rank]) if rank else sum(g.nbytes for g in gates.values())}
result = {'state': 'PASS', 'prefix': prefix, 'episode': a.episode, 'split': a.split,
          'trace_validation': validation, 'construction': construction, 'summary': summary,
          'records': records, 'limitations': [
              'Fresh diagnostic copies change timing and add activation traffic; no headline TG measurement.',
              'CPU scoring cost is single-thread offline including numeric allocations/top10, excluding capture, scheduling and CPU-expert contention.',
              'One-blob readiness is optimistic: ignores full slots, competing proposals, eviction victims and in-flight reader hazards.',
              'Original gate weights define the factors; no labels were used to fit SVD. Rank decisions must use development/calibration only.',
              'Current MoE activation predicts the next router; true future router IDs are labels only.',
              'Lead is between host observations, includes altered doorbell traffic, and is not a GPU clock duration.']}
save(a.output, result)
print(a.episode, a.split, {r: {k: v for k, v in s.items() if k in ('top10_precision_pct', 'nonlocal_recall_pct', 'warm_ready_true_nonlocal_recall_pct', 'CPU_factor_bytes')} for r, s in summary.items()}, flush=True)
