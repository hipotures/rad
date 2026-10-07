"""Consolidate wide-lookahead signal and physically charged temporary placement."""
import csv
from lab import ROOT, load, save
base = ROOT/'experiments/E020-wide-gate-lookahead'; attempt = base/'v1'
names = ['dev-code','dev-math','cal-prose','hold-code','hold-structured','hold-math','32k','128k']
selection = load(attempt/'selection.json'); rows = []; signals = []
for name in names:
    a = load(attempt/'analysis'/f'{name}.json'); assert a['state'] == 'PASS'
    signals.append({'episode': name, 'selected_horizon': selection['horizon'],
                    **a['by_horizon'][str(selection['horizon'])]})
    result = load(attempt/'transactions/results'/f'{name}.json')
    for r in result['results']:
        rows.append({'episode': name, **{k:v for k,v in r.items() if k!='choices'}})
state = 'COMPLETE_BOUNDED_FEASIBILITY'
save(base/'summary.json', {'state': state, 'selection': selection, 'signals': signals,
                          'transactions': rows, 'headline': False,
    'decision': 'Assess charged readiness and victim restoration before any live persistent policy; no simulated TG claim.'})
with (base/'summary.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
text = '# E020: wider GPU router lookahead\n\n'
text += 'The horizon was frozen from development/calibration tasks before examining held-out and benchmark labels. '
text += f'Selected horizon: {selection["horizon"]} layers. Native routing weights are confidence ranks, not calibrated future-use probabilities. '
text += 'Both benchmark traces preserve actual output IDs, routing, MTP windows, execution paths, resident sets, heat and first-head bits. All timing runs are diagnostic.\n\n'
text += '| Task | Policy | Copy GB/s | Admissions | Ready tail % | Promotion MB | Restore MB | Modeled restore wait s |\n|---|---|---:|---:|---:|---:|---:|---:|\n'
for r in rows:
    tail = 'unavailable' if r['warm_tail_coverage_pct'] is None else f'{r["warm_tail_coverage_pct"]:.2f}'
    text += f'| {r["episode"]} | {r["policy"]} | {r["rate_GB_s"]} | {r["admissions"]} | {tail} | {r["promotion_bytes"]/1e6:.2f} | {r["restore_bytes"]/1e6:.2f} | {r["modeled_restore_wait_s"]:.4f} |\n'
text += '\nThe queue model charges exact physical slot classes, one admission per origin, distinct in-window reservations, victim restoration and baseline promotion traffic. Victims are earlier same-device layers. The fixed trajectory and optimistic host observation deadlines do not model changed scheduling or output. Restore waits are not measured request slowdowns. This evaluates one temporary schedule; it does not close persistent placement or all wider predictors.\n'
text += '\nArtifacts: v1/selection.json, v1/analysis/, v1/transactions/inputs/, v1/transactions/results/, and diagnostic source/build identity in v1/build/.\n'
(base/'report.md').write_text(text)
print(state, 'horizon', selection['horizon'])
