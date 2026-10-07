"""Strict real-output, routing, cache and counter parity before E019 headlines."""
import json
import numpy as np
from lab import ROOT, load, save
from trace_reader import Trace
out = ROOT/'experiments/E019-skip-local-host-plan/diagnostic-v1'
if (out/'summary.json').exists():
    raise RuntimeError('Existing diagnostic summary')
profiles = {}
for p in ['32k', '128k']:
    folder = out/p
    trace = Trace(folder/'traces/runtime-request2')
    reference = Trace(ROOT/f'experiments/E016-device-plan-ids/diagnostic-v2/{p}/traces/runtime-request2')
    validation = trace.validate()
    assert validation['state'] == 'PASS', validation
    result = load(folder/'raw/trace-run1.json')
    assert result['state'] == 'VALID' and result['actual_output_tokens'] == 4096 and result['reuse'] == 0
    parity = {name: bool(np.array_equal(left, right)) for name, left, right in [
        ('actual_output_IDs', trace.output_ids, reference.output_ids),
        ('window_inputs', trace.windows['tokens'], reference.windows['tokens']),
        ('window_T', trace.windows['T'], reference.windows['T']),
        ('accepted', trace.windows['accepted'], reference.windows['accepted']),
        ('router_IDs', trace.entries['expert'], reference.entries['expert']),
        ('execution_paths', trace.entries['path'], reference.entries['path']),
        ('initial_residency', trace.initial, reference.initial),
        ('final_residency', trace.final, reference.final),
        ('initial_heat', trace.initial_usage, reference.initial_usage),
        ('final_heat', trace.final_usage, reference.final_usage)]}
    x = np.fromfile(reference.prefix+'-first-logits.bin', '<f4')
    y = np.fromfile(trace.prefix+'-first-logits.bin', '<f4')
    assert len(x) and x.shape == y.shape and np.isfinite(y).all()
    parity['first_head_bits'] = bool(np.array_equal(x.view('u4'), y.view('u4')))
    footer = {'local': validation['path_counts'][0] == result['local_vram_entries'],
        'CPU': validation['path_counts'][-1] == result['cpu_fallback_entries'],
        'mapped': validation['path_counts'][1]+validation['path_counts'][2] == result['offloaded_entries'],
        'windows': validation['windows'] == result['verify_windows'],
        'accepted': int(trace.windows['accepted'].sum()) == result['mtp_accepted']}
    profiles[p] = {'state': 'PASS' if all(parity.values()) and all(footer.values()) else 'INVESTIGATE',
        'parity': parity, 'footer': footer, 'trace_validation': validation,
        'resources': load(folder/'raw/resource-check.json'),
        'limitations': 'Diagnostic timing is excluded from headline speed; exact recorded first head and demand parity do not prove every possible input.'}
    save(folder/'analysis.json', profiles[p])
summary = {'state': 'PASS' if all(v['state'] == 'PASS' for v in profiles.values()) else 'INVESTIGATE', 'profiles': profiles}
save(out/'summary.json', summary)
print(json.dumps({k: {'state': v['state'], 'parity': v['parity'], 'footer': v['footer']} for k,v in profiles.items()}, indent=2))
if summary['state'] != 'PASS':
    raise SystemExit('Correctness/accounting difference: do not run clean headlines')
