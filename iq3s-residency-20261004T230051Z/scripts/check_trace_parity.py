"""Strict demand, output, cache and first-head parity for two diagnostic profiles."""
import argparse
import numpy as np
from lab import load, save
from trace_reader import Trace
ap = argparse.ArgumentParser()
ap.add_argument('candidate'); ap.add_argument('reference'); ap.add_argument('--output', required=True)
a = ap.parse_args()
t, r = Trace(a.candidate), Trace(a.reference)
validation = t.validate(); assert validation['state'] == 'PASS', validation
pairs = [
    ('output_IDs', t.output_ids, r.output_ids),
    ('window_inputs', t.windows['tokens'], r.windows['tokens']),
    ('window_T', t.windows['T'], r.windows['T']),
    ('accepted', t.windows['accepted'], r.windows['accepted']),
    ('router_IDs', t.entries['expert'], r.entries['expert']),
    ('paths', t.entries['path'], r.entries['path']),
    ('initial_residency', t.initial, r.initial), ('final_residency', t.final, r.final),
    ('initial_heat', t.initial_usage, r.initial_usage), ('final_heat', t.final_usage, r.final_usage),
    ('blob_sizes', t.blob_bytes, r.blob_bytes),
]
for device in (0, 1):
    pairs.append((f'GPU{device}_slot_sizes', t.slot_bytes[device], r.slot_bytes[device]))
x = np.fromfile(r.prefix + '-first-logits.bin', '<f4')
y = np.fromfile(t.prefix + '-first-logits.bin', '<f4')
assert len(x) and x.shape == y.shape and np.isfinite(y).all()
pairs.append(('first_head_bits', x.view('u4'), y.view('u4')))
parity = {name: bool(np.array_equal(left, right)) for name, left, right in pairs}
result = {'state': 'PASS' if all(parity.values()) else 'INVESTIGATE',
          'candidate': t.prefix, 'reference': r.prefix, 'parity': parity,
          'validation': validation, 'limit': 'Recorded workload only; first head is not every position.'}
save(a.output, result); print(result['state'], parity, flush=True)
if result['state'] != 'PASS': raise SystemExit(1)
