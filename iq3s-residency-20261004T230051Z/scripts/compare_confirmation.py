"""Derive guard/repair comparisons from retained clean request records only."""
import argparse
import csv
import hashlib
import json
import statistics
from lab import ROOT, load, save

ap = argparse.ArgumentParser()
ap.add_argument('--experiment', required=True)
ap.add_argument('--reference', required=True)
ap.add_argument('--attempt', default='v1')
ap.add_argument('--reference-attempt', default='v1')
args = ap.parse_args()
out = ROOT / 'experiments' / args.experiment
reference = ROOT / 'experiments' / args.reference

def distribution(values):
    values = [v for v in values if v is not None]
    return dict(min=min(values), median=statistics.median(values), max=max(values)) if values else None

def digest(r):
    return r.get('output_text_sha256') or hashlib.sha256(
        (r.get('reasoning', '') + '\0' + r.get('text', '')).encode()).hexdigest()

def decode_system(r):
    start = r['started_epoch'] + r['TTFT_s']
    end = r['started_epoch'] + r['wall_s']
    samples = [json.loads(line) for line in open(r['telemetry']['path'])]
    samples = [s for s in samples if start <= s['wall_time'] <= end]
    if not samples:
        return {'samples': 0, 'CPU': None, 'GPU': None}
    cpu = [sum(p['cpu_pct'] for p in s['processes']) for s in samples]
    result = {'samples': len(samples),
              'mean_process_cpu_pct_one_core': statistics.mean(cpu),
              'mean_process_cpu_pct_16vcpu': statistics.mean(cpu) / 16,
              'mean_system_cpu_pct': statistics.mean(s['system_cpu_pct'] for s in samples),
              'peak_sum_rss_gib': max(sum(p['rss_gib'] for p in s['processes']) for s in samples),
              'GPU': {}}
    for gpu in (0, 1):
        rows = [g for s in samples for g in s.get('gpus', []) if g['index'] == gpu]
        result['GPU'][str(gpu)] = {
            'util_pct': statistics.mean(g['util_pct'] for g in rows),
            'power_w': statistics.mean(g['power_w'] for g in rows),
            'peak_vram_mib': max(g['vram_mib'] for g in rows)} if rows else None
    return result

keys = ['PP', 'TG', 'TTFT_s', 'wall_s', 'mtp_acceptance_pct',
        'mtp_accepted_per_window', 'hit_rate_pct', 'cpu_fallback_entries', 'offloaded_entries']
records, cells, comparisons = [], [], []
for profile in ('32k', '128k'):
    raw = {}
    for name, base, attempt in [('reference', reference, args.reference_attempt),
                                ('candidate', out, args.attempt)]:
        folder = base / attempt / profile
        runs = []
        for n in (1, 2, 3):
            path = folder / 'raw' / f'run{n}.json'
            if not path.exists():
                continue
            r = load(path)
            row = {k: r.get(k) for k in keys + ['state', 'actual_input_tokens',
                'actual_output_tokens', 'finish_reason', 'reuse', 'source_sha',
                'binary_sha256', 'application_status', 'verify_windows',
                'mtp_proposed', 'mtp_accepted']}
            row.update(profile=profile, role=name, run=n, path=str(path),
                       output_sha256=digest(r), input_sha256=r['payload']['input_ids_sha256'],
                       system=decode_system(r))
            records.append(row)
            runs.append(row)
            raw[name, n] = r
        valid = [r for r in runs if r['state'] == 'VALID']
        resource_path = folder / 'raw/resource-check.json'
        if resource_path.exists():
            resource = load(resource_path)
        elif base.name == 'E002-controls' and attempt == 'v1':
            # The first control predates the resource-check harness. Use its
            # retained engine log and exact traced physical classes, never
            # fabricate a new raw control request or mutate prior artifacts.
            resource = load(ROOT / 'analysis/control-budgets-v2.json')[profile].copy()
            resource['stage1_slots'] = resource['helper_or_stage1_slots']
            resource['resource_evidence'] = str(ROOT / 'analysis/control-budgets-v2.json')
        else:
            raise FileNotFoundError(resource_path)
        warmup = load(folder / 'raw/warmup.json')
        cells.append({'profile': profile, 'role': name, 'valid': len(valid),
                      'attempts': len(runs), 'resource': resource,
                      'warmup': {k: warmup.get(k) for k in ['state', 'actual_input_tokens', 'actual_output_tokens']},
                      'statistics': {k: distribution([r[k] for r in valid]) for k in keys}})
    paired = []
    for n in (1, 2, 3):
        if ('reference', n) not in raw or ('candidate', n) not in raw:
            continue
        b, c = raw['reference', n], raw['candidate', n]
        btext, ctext = b.get('text', ''), c.get('text', '')
        differing = next((i for i, (x, y) in enumerate(zip(btext, ctext)) if x != y),
                         min(len(btext), len(ctext)) if btext != ctext else None)
        paired.append({'run': n, 'same_input_ids': b['payload']['input_ids_sha256'] == c['payload']['input_ids_sha256'],
                       'same_output_hash': digest(b) == digest(c),
                       'first_diverging_visible_character': differing,
                       'reference_TG': b.get('TG'), 'candidate_TG': c.get('TG'),
                       'TG_delta_pct': 100 * (c['TG'] / b['TG'] - 1) if c.get('TG') and b.get('TG') else None,
                       'MTP_acceptance_delta_pp': c.get('mtp_acceptance_pct', 0) - b.get('mtp_acceptance_pct', 0)})
    b, c = [x for x in cells if x['profile'] == profile]
    capacity = all(b['resource'][key] == c['resource'][key] for key in ('primary_slots', 'stage1_slots'))
    assert capacity
    assert all(p['same_input_ids'] for p in paired)
    assert all(x['warmup']['actual_output_tokens'] == 64 for x in (b, c))
    delta = {k: 100 * (c['statistics'][k]['median'] / b['statistics'][k]['median'] - 1)
             if b['statistics'][k] and c['statistics'][k] and b['statistics'][k]['median'] else None
             for k in ('PP', 'TG', 'TTFT_s', 'wall_s')}
    comparisons.append({'profile': profile, 'median_delta_pct': delta,
                        'capacity_identical': capacity, 'paired': paired})
complete = all(c['valid'] == 3 for c in cells)
summary = {'state': 'COMPLETE_MIXED' if complete else 'PARTIAL',
           'experiment': args.experiment, 'reference': args.reference,
           'protocol': load(out / args.attempt / 'protocol.json'),
           'cells': cells, 'comparisons': comparisons, 'runs': records,
           'limitations': ['Three serial requests per fresh server/profile, not independent fresh-server replicates.',
               'Batches occurred at different wall times; CPU scheduling and numerical trajectories can affect TG.',
               'Output hashes compare visible answer plus reasoning, not unavailable clean output token IDs.',
               'No diagnostic timings are headline measurements. Unavailable expert-specific I/O is not zero.']}
save(out / 'summary.json', summary)
columns = ['role', 'profile', 'run', 'state', 'actual_input_tokens', 'actual_output_tokens'] + keys + ['path']
with (out / 'summary.csv').open('w') as stream:
    writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(records)
lines = [f'# {args.experiment}: controlled confirmation', '',
         f"Status: {summary['state']}. Reference: {args.reference}.", '',
         '| Profile | Role | PP median | TG min / median / max | TTFT s | Wall s | MTP accept |',
         '|---|---|---:|---:|---:|---:|---:|']
for c in cells:
    s = c['statistics']
    if not s['TG']:
        continue
    tg = s['TG']
    lines.append(f"| {c['profile']} | {c['role']} | {s['PP']['median']:.1f} | "
                 f"{tg['min']:.1f} / {tg['median']:.1f} / {tg['max']:.1f} | "
                 f"{s['TTFT_s']['median']:.3f} | {s['wall_s']['median']:.3f} | "
                 f"{s['mtp_acceptance_pct']['median']:.2f}% |")
for comparison in comparisons:
    lines.extend(['', f"{comparison['profile']} median delta (%): {comparison['median_delta_pct']}.",
                  f"Per-saved-payload comparisons: {comparison['paired']}."])
lines.extend(['', *summary['limitations'], '',
              'All raw attempts remain intact. No additional unchanged repetitions or production switch.'])
(out / 'report.md').write_text('\n'.join(lines) + '\n')
print(json.dumps({'state': summary['state'], 'comparisons': comparisons}, indent=2))
