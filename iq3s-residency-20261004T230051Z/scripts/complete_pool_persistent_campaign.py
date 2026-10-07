"""Close the bounded campaign after evidence, cleanup and reproduction audits pass."""
import datetime
import pathlib
from lab import ROOT, load, save

active = load(ROOT/'active-campaign.json')
campaign = pathlib.Path(active['path'])
assert load(campaign/'end-state.json')['state'] == 'PASS_IDLE_OWNED_PROCESSES'
assert load(campaign/'reproducibility-audit.json')['state'] == 'PASS_REPRODUCIBLE_HEADLINE_MATRIX'
p2 = load(ROOT/'experiments/E029-persistent-runtime/summary.json')
assert p2['state'] == 'COMPLETE_BOUNDED_PERSISTENT_RESIDENCY'
now = datetime.datetime.now(datetime.timezone.utc)
deadline = load(campaign/'deadline.json')
assert now.timestamp() < deadline['deadline_epoch']
active.update(state='COMPLETE', completed_utc=now.isoformat(), recommendation=p2['decision'])
save(ROOT/'active-campaign.json', active)
status = load(ROOT/'STATUS.json')
status.update(state='COMPLETE', running=None, pending=[],
              completed=['E026-pool-generalization', 'E027-pool-baseline', 'E028-persistent-replay', 'E029-persistent-runtime', 'Final reproducibility/report/cleanup'],
              updated_utc=now.isoformat(), elapsed_wall_s=now.timestamp()-deadline['start_epoch'],
              remaining_wall_s=deadline['deadline_epoch']-now.timestamp(), recommendation=p2['decision'],
              next_exact_action='Use the frozen P1 launchers for user real-prompt testing. No further research or residency implementation starts automatically.')
for path in [ROOT/'STATUS.json', campaign/'STATUS.json']:
    save(path, status)
text = f'''# Pool and persistent-residency follow-up

State: COMPLETE. Recommendation: {p2['decision']}.

Completed: P0 independent-workload validation, P1 CPU-pool freeze and stress tests, P2 replay/live persistent residency, final reporting and cleanup.

P1 fixed 100 µs is the recommended real-prompt configuration. P2 is a completed negative performance result, not unfinished because of the deadline. The bounded policy study does not exhaust all possible residency algorithms.

The headline matrix contains 60 valid measured requests, with exactly three per point. Previous results and all failed/diagnostic attempts remain preserved.

Both GPU compute-process lists are empty; no owned Strata/training/profiling process remains. Source/binary identities, old archived hashes and 648 headline-related artifact hashes passed their audits.

Start: {deadline['start_utc']}. Absolute upper bound: {deadline['deadline_utc']}. Completed: {now.isoformat()}, elapsed {(now.timestamp()-deadline['start_epoch'])/3600:.2f} h.

Pending: none in the bounded protocol. Next action: user real-prompt testing with variants/p1-baseline/start-32k.sh or start-128k.sh. No automatic additional research.
'''
for path in [ROOT/'STATUS.md', campaign/'STATUS.md']:
    path.write_text(text)
transition = {'id': 'FINAL', 'state': 'COMPLETE', 'updated_utc': now.isoformat(),
              'campaign': deadline['campaign'], 'recommendation': p2['decision'],
              'note': 'Bounded P0/P1/P2 complete early; raw data preserved, reproducibility and idle-process audits PASS.'}
import json
for path in [ROOT/'experiments.jsonl', campaign/'transitions.jsonl']:
    with path.open('a') as stream:
        stream.write(json.dumps(transition)+'\n')
print('COMPLETE', p2['decision'], flush=True)
