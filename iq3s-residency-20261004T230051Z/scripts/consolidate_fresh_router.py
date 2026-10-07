"""Report repaired availability, bounded low-rank cost and independent holdout."""
import csv
import json
import numpy as np
from datetime import datetime, timezone
from lab import ROOT, load, save
from trace_reader import Trace

out = ROOT / 'experiments/E015-lowrank-router'
attempt = out / 'v1'
if (out / 'summary.json').exists():
    raise RuntimeError('Existing stage summary; preserve it')
episodes = ['dev-code', 'dev-math', 'cal-prose', 'hold-code', 'hold-structured', 'hold-math', '32k', '128k']
data = [load(attempt / 'analysis' / (episode + '.json')) for episode in episodes]
records = [r for d in data for r in d['records']]
tables = []
for d in data:
    for rank, metrics in d['summary'].items():
        tables.append({'episode': d['episode'], 'split': d['split'], 'rank': int(rank), **metrics})
parity = {}
for profile in ('32k', '128k'):
    fresh = Trace(attempt / profile / 'traces/runtime-request2')
    previous_path = ROOT / 'experiments/E008-router-boundary/v2' / profile / 'traces/runtime-request2'
    old = Trace(previous_path)
    new_logits = np.fromfile(fresh.prefix + '-first-logits.bin', '<f4')
    old_logits = np.fromfile(old.prefix + '-first-logits.bin', '<f4')
    assert np.isfinite(new_logits).all() and new_logits.shape == old_logits.shape
    parity[profile] = {'all_output_ids_identical': bool(np.array_equal(fresh.output_ids, old.output_ids)),
        'all_router_entries_identical': bool(np.array_equal(fresh.entries, old.entries)),
        'all_T_identical': bool(np.array_equal(fresh.windows['T'], old.windows['T'])),
        'all_accepted_identical': bool(np.array_equal(fresh.windows['accepted'], old.windows['accepted'])),
        'first_head_bit_identical': bool(np.array_equal(new_logits.view('u4'), old_logits.view('u4'))),
        'first_head_max_abs_difference': float(np.abs(new_logits - old_logits).max()),
        'initial_usage_identical': bool(np.array_equal(fresh.initial_usage, old.initial_usage)),
        'final_usage_identical': bool(np.array_equal(fresh.final_usage, old.final_usage))}
layer_tables = []
for split in ('development', 'calibration', 'holdout', 'benchmark'):
    for layer in (6, 21, 25, 26, 41, 47):
        for rank in (0, 32, 128):
            rows = [r for r in records if r['split'] == split and r['target_layer'] == layer and r['rank'] == rank and not r['cold_graph_capture_window']]
            if not rows:
                continue
            bad = sum(r['true_nonlocal'] for r in rows)
            proposed = sum(r['predicted_current_nonresident'] for r in rows)
            layer_tables.append({'split': split, 'target_layer': layer, 'rank': rank, 'rows': len(rows),
                'nonlocal_entries': bad, 'nonlocal_recall_pct': 100 * sum(r['predicted_true_nonlocal'] for r in rows) / bad if bad else None,
                'nonresident_proposal_precision_pct': 100 * sum(r['predicted_true_nonlocal'] for r in rows) / proposed if proposed else None,
                'median_batch_score_plus_top10_us': float(np.median([r['batch_score_us'] + r['batch_top10_us'] for r in rows])),
                'median_host_lead_us': float(np.median([r['lead_to_true_router_host_observation_us'] for r in rows])),
                'optimistic_ready_nonlocal_recall_pct': {rate: 100 * sum(r['predicted_true_nonlocal'] for r in rows if r['optimistic_ready'][rate]) / bad if bad else None for rate in ('12.6', '1.8')}})
summary = {'state': 'COMPLETE_NEGATIVE', 'scope': 'CPU gate and rank32/rank128 next-router versions only; GPU projection remains a separate supported follow-up.',
    'protocol': load(attempt / 'protocol.json'), 'source': load(attempt / 'build/identity.json'),
    'rank_choice': load(attempt / 'rank-choice.json'), 'episodes': tables, 'by_layer': layer_tables,
    'parity': parity, 'old_fresh_filter': load(attempt / 'old-fresh-filter/summary.json'),
    'decision': 'Do not put these CPU predictors into the hot path: optimistic ready-tail recall is limited and false nonresident proposals cost transfers/victims. Measure GPU gate cost/availability before dismissing router lookahead as a whole.',
    'limitations': [
        'Six short independent tasks provide separated dev/calibration/holdout, not broad agentic quality coverage.',
        'Fresh forced copies repair unavailable host inputs but perturb timing and add mapped traffic.',
        'CPU numeric cost includes projection/top10, not CPU-expert contention, capture or admission selection.',
        'One-blob readiness ignores competing proposals, full slots and victim damage; it is not a feasible speed forecast.',
        'Old full router-quality/readiness aggregates were withdrawn; real old output and boundary timings remain preserved.',
        'No new auxiliary model downloaded; original weights and routing untouched.']}
save(out / 'summary.json', summary)
with (out / 'summary.csv').open('w') as stream:
    columns = ['episode', 'split', 'rank', 'rows', 'top10_precision_pct', 'nonlocal_recall_pct',
               'true_nonlocal_entries', 'predicted_nonresident_entries', 'false_positive_nonresident_entries',
               'nonresident_proposal_precision_pct', 'CPU_factor_bytes']
    writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore')
    writer.writeheader(); writer.writerows(tables)
lines = ['# Fresh-activation CPU router study', '', f"Status: {summary['state']} (CPU versions only).", '',
    'The original host activation capture was unavailable/stale for all-local groups. The real kernel reproducer confirms that rule. Fresh diagnostic copies preserve the actual inference outputs while making numeric signals valid.', '',
    '| Episode | Rank | Top10 precision | Nonlocal recall | Ready recall12.6GB/s | Ready recall1.8GB/s | CPU bytes |',
    '|---|---:|---:|---:|---:|---:|---:|']
for row in tables:
    ready = row['warm_ready_true_nonlocal_recall_pct']
    lines.append(f"| {row['episode']} | {row['rank']} | {row['top10_precision_pct']:.2f}% | "
                 f"{row['nonlocal_recall_pct']} | {ready['12.6']} | {ready['1.8']} | {row['CPU_factor_bytes']} |")
lines += ['', summary['decision'], '',
    f"Rank frozen before holdout: {summary['rank_choice']}.", '',
    f"Same-input first-head/output/accounting parity: {parity}.", '',
    'Per-layer costs/readiness and false proposal counts are in summary.json. No diagnostic TG is a headline result.', '',
    *summary['limitations']]
(out / 'report.md').write_text('\n'.join(lines) + '\n')
status = load(ROOT / 'STATUS.json')
if 'E015' not in status['completed']:
    status['completed'].append('E015')
status['running'] = 'E016'
status['next_exact_action'] = 'Finish E016 native/battery prerequisites, build isolated demand/head diagnostic and validate stable true IDs/heat before any clean speed. Prepare bounded GPU-router cost follow-up E017; no concurrent GPU experiments.'
status['updated_utc'] = datetime.now(timezone.utc).isoformat()
save(ROOT / 'STATUS.json', status)
(ROOT / 'STATUS.md').write_text('# Research status\n\n' + json.dumps(status, indent=2) + '\n')
ledger = load(ROOT / 'candidate-ledger.json')
for family in ledger['families']:
    if family['id'] == 'F05':
        family.update(state='RUNNING', next=summary['decision'])
    if family['id'] == 'F07':
        family['next'] = 'E013 exact-choice repair and E014 same-binary guard complete; attribution is mixed and identical trajectories show substantial runtime/build/batch variation. E016 device-plan/stable-ID execution follow-up in progress.'
save(ROOT / 'candidate-ledger.json', ledger)
with (ROOT / 'experiments.jsonl').open('a') as stream:
    stream.write(json.dumps({'id': 'E015', 'state': summary['state'], 'updated_utc': status['updated_utc'], 'evidence': str(out / 'summary.json')}) + '\n')
print(json.dumps({'state': summary['state'], 'parity': parity}, indent=2))
