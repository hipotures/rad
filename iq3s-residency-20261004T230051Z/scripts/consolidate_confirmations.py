"""Falsify simple attribution using same-output and same-binary guard evidence."""
import hashlib
import json
from datetime import datetime, timezone
from lab import ROOT, load, save

out = ROOT / 'analysis/confirmation-falsification-v1'
if out.exists():
    raise RuntimeError('Existing consolidated attempt')
out.mkdir(parents=True)
experiments = ['E002-controls', 'E010-compatible-runtime',
               'E013-compatible-fast', 'E014-policy-off-guard']
cases = []
counts = ['mtp_proposed', 'mtp_accepted', 'verify_windows', 'local_vram_entries',
          'cpu_fallback_entries', 'offloaded_entries']
def digest(r):
    return r.get('output_text_sha256') or hashlib.sha256(
        (r.get('reasoning', '') + '\0' + r.get('text', '')).encode()).hexdigest()
for profile in ('32k', '128k'):
    for n in (1, 2, 3):
        records = {e: load(ROOT / 'experiments' / e / 'v1' / profile / 'raw' / f'run{n}.json')
                   for e in experiments}
        assert all(r['state'] == 'VALID' and r['actual_output_tokens'] == 4096 and r['reuse'] == 0
                   for r in records.values())
        assert len({r['payload']['input_ids_sha256'] for r in records.values()}) == 1
        for bname, cname, description in [
            ('E002-controls', 'E014-policy-off-guard', 'Original algorithm in different rebuilt binaries/batches'),
            ('E010-compatible-runtime', 'E013-compatible-fast', 'Exact-choice selector repair in different binaries/batches'),
            ('E014-policy-off-guard', 'E010-compatible-runtime', 'Same binary, policy OFF versus ON in different batches')]:
            b, c = records[bname], records[cname]
            cases.append({'profile': profile, 'run': n, 'comparison': description,
                'reference': bname, 'candidate': cname,
                'same_binary': b['binary_sha256'] == c['binary_sha256'],
                'same_visible_output': digest(b) == digest(c),
                'same_logical_counts': {k: b.get(k) == c.get(k) for k in counts},
                'reference_TG': b['TG'], 'candidate_TG': c['TG'],
                'TG_delta_pct': 100 * (c['TG'] / b['TG'] - 1),
                'reference_cpu_fallback': b.get('cpu_fallback_entries'),
                'candidate_cpu_fallback': c.get('cpu_fallback_entries'),
                'reference_log': str(ROOT / 'experiments' / bname / 'v1' / profile / 'raw' / f'run{n}-engine.log'),
                'candidate_log': str(ROOT / 'experiments' / cname / 'v1' / profile / 'raw' / f'run{n}-engine.log')})
summary = {'state': 'COMPLETE_MIXED', 'cases': cases,
    'findings': [
        'The heap repair produces the same visible trajectories/MTP but markedly different TG across batches; selector cost reduction is not a guaranteed TG improvement.',
        'Same-binary policy ON/OFF preserves capacities/settings but changes trajectories, so it is a practical workload comparison rather than fixed-execution timing.',
        'The first128k compatible result is not sufficient to establish a portable policy-only18.47% improvement.',
        'No extra unchanged repetitions are permitted. Binary layout, runtime/VM scheduling and hardware state remain possible factors rather than diagnosed causes.'],
    'interpretation': 'Preserve measured numbers; separate local scorer/selector cost, policy accounting and end-to-end free-generation evidence.'}
save(out / 'summary.json', summary)
(out / 'report.md').write_text('# Attribution falsification\n\n' +
    '\n\n'.join(summary['findings']) + '\n\nFull same-input/hash/counter comparisons: summary.json. '
    'No diagnostic rate or historical number is promoted to headline speed.\n')
status = load(ROOT / 'STATUS.json')
for e in ('E013', 'E014'):
    if e not in status['completed']:
        status['completed'].append(e)
status.update(running='E015', pending=[
    'E015 fresh-activation/router rank study: complete analysis and availability correction',
    'E016 bounded device-plan/stable-ID feasibility and conditional confirmation',
    'final report, launcher audit and owned cleanup'],
    next_exact_action='Finish E015 serial analyses; consolidate same-output/first-head/heldout evidence. Then build/test the predeclared E016 stable-ID device-plan variant in its own directory.',
    updated_utc=datetime.now(timezone.utc).isoformat())
save(ROOT / 'STATUS.json', status)
(ROOT / 'STATUS.md').write_text('# Research status\n\n' + json.dumps(status, indent=2) + '\n')
with (ROOT / 'experiments.jsonl').open('a') as stream:
    for e in ('E013', 'E014'):
        stream.write(json.dumps({'id': e, 'state': 'COMPLETE_MIXED',
            'updated_utc': status['updated_utc'], 'evidence': str(out / 'summary.json')}) + '\n')
print(json.dumps({'state': summary['state'], 'same_output_cases':
    sum(c['same_visible_output'] for c in cases), 'total_cases': len(cases)}, indent=2))
