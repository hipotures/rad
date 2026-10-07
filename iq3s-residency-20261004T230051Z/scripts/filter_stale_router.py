"""Retain only old activation groups whose original doorbell actually copied x."""
import json
import numpy as np
from lab import ROOT, save
from trace_reader import Trace

out = ROOT / 'experiments/E015-lowrank-router/v1/old-fresh-filter'
if out.exists():
    raise RuntimeError('Existing freshness analysis; preserve it')
out.mkdir(parents=True)
ACT = np.dtype([(x, '<u8') for x in ('window', 'available_ns', 'offset')] +
               [(x, '<i4') for x in ('layer', 'token_base', 'tokens', 'width')])
results = {}
for profile in ('32k', '128k'):
    prefix = str(ROOT / 'experiments/E008-router-boundary/v2' / profile / 'traces/runtime-request2')
    trace = Trace(prefix)
    assert trace.validate()['state'] == 'PASS'
    old = json.loads((ROOT / 'experiments/E008-router-boundary/analysis-r2' /
                      profile / 'analysis.json').read_text())
    captures = np.fromfile(prefix + '-activations.bin', ACT)
    groups = {}
    for layer, entries in trace.grouped():
        key = int(layer['window']), int(layer['layer'])
        groups.setdefault(key, []).append(entries)
    freshness = {}
    for capture in captures:
        win, layer = int(capture['window']), int(capture['layer'])
        entries = np.concatenate(groups[win, layer])
        first, n = int(capture['token_base']), int(capture['tokens'])
        entries = entries[(entries['token'] >= first) & (entries['token'] < first + n)]
        fresh = bool(np.any(entries['path'] != 0))
        for row in range(first, first + n):
            freshness[win, layer, row] = fresh
    kept, excluded = [], []
    for r in old['records']:
        key = r['window'], r['current_layer'], r['row']
        (kept if freshness[key] else excluded).append(r)
    warm = [r for r in kept if not r['cold_graph_capture_window']]
    bad = sum(r['true_nonlocal'] for r in kept)
    result = {'original_analysis': str(ROOT / 'experiments/E008-router-boundary/analysis-r2' / profile / 'analysis.json'),
        'original_rows': len(old['records']), 'fresh_rows': len(kept),
        'unavailable_or_stale_rows': len(excluded),
        'fresh_top10_precision_pct': 100 * sum(r['top10_matched'] for r in kept) / (10 * len(kept)) if kept else None,
        'fresh_nonlocal_entries': bad,
        'fresh_nonlocal_recall_pct': 100 * sum(r['predicted_true_nonlocal'] for r in kept) / bad if bad else None,
        'fresh_warm_optimistic_ready_fraction': sum(r['optimistic_score_plus_one_blob_ready_before_true_router'] for r in warm) / len(warm) if warm else None,
        'selection_bias': 'Fresh groups have a current-layer nonlocal; they are not representative of all-local groups. Do not extrapolate.',
        'kept_records': kept, 'excluded_record_keys': [
            {'window': r['window'], 'current_layer': r['current_layer'], 'row': r['row']} for r in excluded]}
    save(out / f'{profile}.json', result)
    results[profile] = {k: v for k, v in result.items() if k not in ('kept_records', 'excluded_record_keys')}
save(out / 'summary.json', {'state': 'PASS', 'profiles': results,
     'source_rule': 'doorbell_publish_res copies all activation rows iff any entry of this group is nonresident.',
     'old_data': 'No old raw or derived file overwritten. Old full aggregate verdict withdrawn.'})
print(json.dumps(results, indent=2))
