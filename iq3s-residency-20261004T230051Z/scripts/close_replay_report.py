"""Expose already-completed corrected replay evidence; do not run another replay."""
from lab import ROOT, load, save
base = ROOT / 'experiments/E004-replay'
rows = []
for profile in ['32k', '128k']:
    for policy in ['current', 'frequency', 'future-nextuse']:
        path = base / 'v6-corrected-peak' / f'{profile}-rate12p6' / f'{policy}.json'
        r = load(path)
        row = {k: r[k] for k in ['nonlocal_entries', 'promotion_bytes', 'useful_promotion_bytes',
             'unused_promotion_bytes', 'victim_demand_while_absent', 'modeled_pending_wait_s']}
        row.update(profile=profile, policy=policy, raw=str(path)); rows.append(row)
save(ROOT / 'analysis/replay-closure.json', {'state': 'COMPLETE_DERIVED_CORRECTED_REPLAY', 'rows': rows,
     'limits': 'Fixed-trajectory replay at an optimistic aggregate12.6GB/s. Corrected publication queue; no new simulation, request, or measured TG. Future-nextuse uses real future labels and is a heuristic, not a proven optimum.'})
text = '## Closing authoritative replay evidence\n\n'
text += 'The peak-envelope figures below use the completed v6 numerical queue repair. Earlier attempts/tables remain retained with their precision caveats; v4 slow-rate data are invalid. Contended-rate sensitivity remains in v5-sensitivity.\n\n'
text += '| Profile | Policy | Nonlocal entries | Promotion GB | Useful GB | Unused GB | Victim demand | Modeled publication wait s |\n|---|---|---:|---:|---:|---:|---:|---:|\n'
for r in rows:
    text += f'| {r["profile"]} | {r["policy"]} | {r["nonlocal_entries"]} | {r["promotion_bytes"]/1e9:.3f} | {r["useful_promotion_bytes"]/1e9:.3f} | {r["unused_promotion_bytes"]/1e9:.3f} | {r["victim_demand_while_absent"]} | {r["modeled_pending_wait_s"]:.4f} |\n'
text += '\nUseful means a transferred expert is used subsequently in the fixed trace; it does not establish saved exposed latency. Victim demand counts entries while displaced, not a disjoint timing cost. The clairvoyant heuristic pays queue/slot/copy costs under the stated assumptions but has unavailable future labels. The separate transfer-free capacity reference relaxes timing and needs roughly42/59GB of replacement. No simulated metric is headline TG.\n'
(ROOT / 'analysis/replay-closure.md').write_text(text)
existing = (base / 'report.md').read_text().split('## Closing authoritative replay evidence', 1)[0]
(base / 'report.md').write_text(existing.rstrip() + '\n\n' + text)
print('Closed six retained corrected replay projections.')
