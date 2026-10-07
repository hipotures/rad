"""Check real demand/accounting, fixed-input head and charged resources before speed."""
import json
import numpy as np
from lab import ROOT, load, save
from trace_reader import Trace

out = ROOT / 'experiments/E016-device-plan-ids/diagnostic-v1'
if (out / 'summary.json').exists():
    raise RuntimeError('Existing diagnostic summary')
summaries = {}
for profile in ('32k', '128k'):
    folder = out / profile
    trace = Trace(folder / 'traces/runtime-request2')
    validation = trace.validate()
    assert validation['state'] == 'PASS', validation
    run = load(folder / 'raw/trace-run1.json')
    assert run['state'] == 'VALID' and run['actual_output_tokens'] == 4096 and run['reuse'] == 0
    agreement = (validation['path_counts'][0] == run['local_vram_entries'] and
        validation['path_counts'][-1] == run['cpu_fallback_entries'] and
        validation['path_counts'][1] + validation['path_counts'][2] == run['offloaded_entries'] and
        validation['windows'] == run['verify_windows'] and int(trace.windows['accepted'].sum()) == run['mtp_accepted'])
    assert agreement
    old = Trace(ROOT / 'experiments/E008-router-boundary/v2' / profile / 'traces/runtime-request2')
    x = np.fromfile(old.prefix + '-first-logits.bin', '<f4')
    y = np.fromfile(trace.prefix + '-first-logits.bin', '<f4')
    assert np.isfinite(y).all() and x.shape == y.shape
    def softmax(a):
        a = a.astype(np.float64); a -= a.max(); z = np.exp(a); return z / z.sum()
    p, q = softmax(x), softmax(y)
    mask = p > 0
    kl = float((p[mask] * np.log(p[mask] / np.maximum(q[mask], np.finfo(float).tiny))).sum())
    count = min(len(old.output_ids), len(trace.output_ids))
    bad = np.flatnonzero(old.output_ids[:count] != trace.output_ids[:count])
    prefix = int(bad[0]) if len(bad) else count
    # Charge the upstream device-plan state; mapped snapshots are CPU memory.
    resources = load(folder / 'raw/resource-check.json')
    slots = [resources['primary_slots'], resources['stage1_slots']]
    explicit_device = [n * 8 + 64 for n in slots]
    mapped_ids = [25 * 4 * 10 * 4, 23 * 4 * 10 * 4]
    summaries[profile] = {'state': 'PASS', 'trace_validation': validation,
        'footer_agreement': agreement, 'first_head_top1': [int(x.argmax()), int(y.argmax())],
        'first_head_KL_old_to_new': kl, 'first_head_max_abs_difference': float(np.abs(x - y).max()),
        'first_head_bit_identical': bool(np.array_equal(x.view('u4'), y.view('u4'))),
        'common_output_prefix_tokens': prefix,
        'all_output_ids_identical': bool(np.array_equal(old.output_ids, trace.output_ids)),
        'initial_usage_identical': bool(np.array_equal(old.initial_usage, trace.initial_usage)),
        'final_usage_identical': bool(np.array_equal(old.final_usage, trace.final_usage)),
        'extra_explicit_device_bytes': explicit_device, 'mapped_CPU_ID_bytes': mapped_ids,
        'resource_check': resources,
        'limitations': 'Buffers preserve actual routed IDs after GPU advances; native plans can change FP execution details/free trajectories. Diagnostics are not headline TG. CUDA allocation rounding/internal page/event costs are not represented by explicit byte count.'}
    assert x.argmax() == y.argmax(), 'Investigate first-head correctness divergence before speed'
    save(folder / 'analysis.json', summaries[profile])
save(out / 'summary.json', {'state': 'PASS', 'profiles': summaries,
    'correctness': load(ROOT / 'experiments/E016-device-plan-ids/v1/correctness/device-plan-ids-v1/ground-truth-checks.json'),
    'changed_algorithm': 'Original EMA and true router; GPU resident plan + stable layer-ID buffers. Same physical expert slots; charged auxiliary bytes use existing per-device non-expert slack, never extra expert capacity.'})
print(json.dumps({p: {k: v for k, v in s.items() if k not in ('trace_validation', 'resource_check')} for p, s in summaries.items()}, indent=2))
