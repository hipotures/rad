"""Persist the closing decision and bounded open branches without resetting time."""
import argparse
from datetime import datetime, timezone
import time
from lab import ROOT, load, save

ap = argparse.ArgumentParser()
ap.add_argument('--complete', action='store_true')
a = ap.parse_args()
state = load(ROOT / 'STATUS.json')
deadline = load(ROOT / 'deadline.json')
state.update(state='COMPLETE' if a.complete else 'CONSOLIDATING', running=None,
             recommendation='PROMISING_NEEDS_MORE_WORK',
             updated_utc=datetime.now(timezone.utc).isoformat())
state['pending'] = [] if a.complete else ['Final evidence/launcher audit, final rendering, local commit and owned cleanup.']
state['next_exact_action'] = 'STOP: review report.md and preserved artifacts; no deployment or further experiment authorized by this completed campaign.' if a.complete else 'Finish audits and report; do not launch new inference, builds, training or candidate experiments.'
state['future_work'] = [
    {'state': 'NOT_ATTEMPTED', 'topic': 'Independent-workload paired fresh-start validation of the 100us pool setting',
     'reason': 'Strong CPU reduction and positive scoped latency comparison, but serial-batch variation and increased CPU wakeup tails prevent a portable performance claim.'},
    {'state': 'NOT_ATTEMPTED', 'topic': 'Persistent byte-aware same-device GPU-lookahead admissions',
     'reason': 'One-layer and development-selected eight-layer signals measured; temporary reservation/restoration schedules completed. Persistent reader/publication safety and exposed interference are not implemented within the time budget.'},
    {'state': 'NOT_ATTEMPTED', 'topic': 'Cross-device expert execution/scheduling with staged transfers',
     'reason': 'No direct P2P and no freely interchangeable GPU capacities. Existing measured copy/activation costs and complementary placement constraints need a new charged protocol.'}]
for item in state['excluded']:
    if item['path'].endswith('E016-device-plan-ids/diagnostic-v1'):
        item['reason'] = 'UNSAFE_PLE_PRODUCER_DEPENDENCY: first-head initially matches but same-input divergence occurs at window3/layer1. Root cause reproduced on both GPUs and repaired in v2; unsafe v1 remains excluded, with no headline requests.'
    if item['path'].endswith('E023-direct-parts/diagnostic-v1'):
        item['reason'] = 'INVALID_DIAGNOSTIC_CAPTURE: first-head hook absent. Actual outputs/demand retained but numeric prerequisite incomplete. Separate diagnostic-v2 repairs only capture; clean binary unchanged and six clean requests subsequently completed.'
state['current_winners'] = {
    'reference': 'Unchanged rebuilt CURRENT layer split K25/PCIe0.28. Keep normal user launcher unchanged.',
    '32k': {'TG_median': 155.9, 'PP_median': 4739.5, 'path': str(ROOT / 'experiments/E002-controls/v1/32k')},
    '128k': {'TG_median': 133.2, 'PP_median': 5985.2, 'path': str(ROOT / 'experiments/E002-controls/v1/128k')},
    'scoped_followup': {'variant': 'pool-wait-v1', 'TG32': 178.5, 'TG128': 154.0,
        'decode_system_CPU32_pct': 28.043478260869566, 'decode_system_CPU128_pct': 25.848148148148148,
        'same_binary': True, 'state': 'PROMISING_NEEDS_MORE_WORK',
        'scope': 'Same saved workload, outputs, MTP and capacity. Do not interpret separate serial batches as independent fresh paired trials.'}}
state['elapsed_s'] = time.time() - deadline['start_epoch']
if a.complete:
    assert load(ROOT / 'analysis/final-audit.json')['state'] == 'PASS_WITH_DOCUMENTED_LIMITS'
    assert load(ROOT / 'analysis/cleanup.json')['owned_active_inference_or_training'] == []
    state['completed_utc'] = state['updated_utc']
save(ROOT / 'STATUS.json', state)
ledger = load(ROOT / 'candidate-ledger.json')
for family in ledger['families']:
    if family['id'] == 'F07':
        family.update(state='COMPLETE_MIXED_ATTRIBUTION_NOT_ESTABLISHED',
            next='Same-device compatible placement has modest simulated tail gains, but full confirmations and exact-choice/same-binary guards do not establish a portable benefit. Safe GPU planning and direct rows completed with numeric parity. Direct rows regress32K vsOFF and retain uncertain128K advantage. Persistent admission and cross-device scheduling remain NOT_ATTEMPTED under the time budget.')
    if family['id'] == 'F08':
        family.update(state='COMPLETE_MIXED_SCOPED_POSITIVE',
            next='Coordination and row-copy changes are mixed or unisolated. Existing100us pool threshold preserves the control binary/output/MTP/capacity, improves scoped TG/latency, and sharply reduces spinning CPU; measured CPU-positive wakeup wait rises. Independent-workload paired validation is the strongest next experiment.')
save(ROOT / 'candidate-ledger.json', ledger)
text = '# Research status\n\n'
text += f'State: {state["state"]}. Recommendation: {state["recommendation"]}.\n\n'
text += 'Completed finite stages: ' + ', '.join(state['completed']) + '.\n\n'
text += 'No new GPU experiment, training, build or sweep will be started. All raw/invalid records and repaired attempts remain preserved.\n\n'
text += f'Next exact action: {state["next_exact_action"]}\n\n'
text += f'Start: {deadline["start_utc"]}; hard deadline: {deadline["deadline_utc"]}; elapsed at update: {state["elapsed_s"]/3600:.2f}h. Deadline never reset.\n\n'
text += 'Open research is explicitly NOT_ATTEMPTED in STATUS.json, not required work silently described as completed negative. Read GOAL.md and persistent state before any later authorized follow-up.\n'
(ROOT / 'STATUS.md').write_text(text)
print(state['state'], state['recommendation'])
