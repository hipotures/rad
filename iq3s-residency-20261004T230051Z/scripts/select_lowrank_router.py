"""Freeze a rank before any held-out analysis, using dev/calibration only."""
from lab import ROOT, load, save
out = ROOT / 'experiments/E015-lowrank-router/v1'
path = out / 'rank-choice.json'
if path.exists():
    raise RuntimeError('Existing frozen rank choice')
rows = []
for episode in ('dev-code', 'dev-math', 'cal-prose'):
    result = load(out / 'analysis' / (episode + '.json'))
    assert result['split'] in ('development', 'calibration')
    rows += [r for r in result['records'] if not r['cold_graph_capture_window']]
scores = {}
for rank in (32, 128):
    candidate = [r for r in rows if r['rank'] == rank]
    bad = sum(r['true_nonlocal'] for r in candidate)
    scores[rank] = sum(r['predicted_true_nonlocal'] for r in candidate if r['optimistic_ready']['1.8']) / bad if bad else 0
selected = max((32, 128), key=lambda rank: (scores[rank], -rank))
save(path, {'state': 'FROZEN_BEFORE_HOLDOUT', 'selected_rank': selected,
    'criterion': 'Highest dev/calibration warm optimistic ready true-nonlocal recall at measured contended1.8GB/s; ties favor smaller rank. This is not a promotion utility or runtime acceptance criterion.',
    'eligible_episodes': ['dev-code', 'dev-math', 'cal-prose'],
    'scores': scores, 'heldout_accessed': False,
    'caveat': 'Both predeclared ranks remain in heldout tables; no further rank/threshold tuning.'})
print(selected, scores)
