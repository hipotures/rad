"""Append laboratory references only after completion audit passes."""
import datetime
import json
import time
from pathlib import Path

from owned import C

R = C.parents[1]


def load(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def append_once(path, marker, text):
    existing = Path(path).read_text()
    assert marker not in existing, 'Completion already appended; refuse duplication'
    Path(path).write_text(existing.rstrip() + '\n\n' + marker + '\n\n' + text + '\n')


def main():
    assert load(C / 'analysis/final-audit.json')['state'] == 'PASS'
    deadline = load(C / 'deadline.json')
    assert time.monotonic() < deadline['deadline_monotonic']
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    decision = load(C / 'analysis/final-decision.json')
    summary = load(C / 'summary.json')
    assert len(summary['rows']) == 33
    assert len(load(C / 'phase-c/independent-summary.json')['rows']) == 9
    summary.update(state='COMPLETE', completed_utc=now,
                   conclusion=decision['conclusion'],
                   audit=str(C / 'analysis/final-audit.json'))
    save(C / 'summary.json', summary)
    state = load(C / 'STATUS.json')
    state.update(state='COMPLETE', phase='COMPLETE', running=None, error=None,
                 pending=[], completed=[
                     'Phase A: typed E/I/V/P audit, tests and ordinary/replay guards',
                     'Phase B: ten sparse offline points and one preserved negative repair',
                     'Phase C: 33/33 primary and 9/9 independent-task requests',
                     'Comparable native/oracle victim, readiness and lifetime accounting',
                     '18 replay and 3 unchanged normal launcher validations',
                     'Reports, source/binary/model provenance and cleanup audit'],
                 conclusion=decision['conclusion'], updated_utc=now,
                 elapsed_wall_s=time.monotonic() - deadline['start_monotonic'],
                 next_exact_action='Review report; use unchanged Q4/100us normal serving '
                                   'launchers. No predictor or additional experiment starts automatically.')
    save(C / 'STATUS.json', state)
    (C / 'STATUS.md').write_text('# Q4 oracle decomposition — complete\n\n```json\n'
                                + json.dumps(state, indent=2) + '\n```\n')
    relative = C.relative_to(R)
    latest = {'path': str(C), 'state': 'COMPLETE',
              'conclusion': decision['conclusion'], 'completed_utc': now,
              'report': str(C / 'report.md'), 'summary': str(C / 'summary.json'),
              'deadline_path': str(C / 'deadline.json'),
              'serving_baseline_changed': False}
    root_state = load(R / 'STATUS.json')
    root_state['latest_campaign'] = latest
    save(R / 'STATUS.json', root_state)
    save(R / 'active-campaign.json', dict(latest, running=None))
    root_summary = load(R / 'summary.json')
    root_summary['latest_q4_information_decomposition'] = latest
    save(R / 'summary.json', root_summary)
    marker = '<!-- ' + C.name + ' -->'
    append_once(R / 'STATUS.md', marker,
                f'Latest research campaign is complete: [{C.name}]({relative}/report.md). '
                f'{decision["conclusion"]}, scoped fixed-work replay. '
                '33 primary and 9 task-transfer requests retained; no fourth attempts. '
                'GPUs and owned processes are clear. Normal Q4 serving remains unchanged.')
    append_once(R / 'launch-index.md', marker,
                '# Q4 incoming/victim information decomposition\n\n'
                f'[{decision["conclusion"]}]({relative}/report.md), not a serving upgrade. '
                'Common replay source bbfea2955ec238f7e6406b11c74e577c996c4a8d. '
                f'[Experimental command index]({relative}/launchers/README.md). '
                'All 18 wrapper identity/config checks passed; actual live coverage '
                'is the report table. A manual reproduction creates a new namespace.\n\n'
                'Normal real-use [Q4/100us launchers]('
                'campaigns/q4-live-oracle-20261006T040656Z/launchers/control/README.md) '
                'remain unchanged and never enable replay/oracle. Their three check modes passed. '
                'No predictor training or runtime deployment follows automatically.')
    ledger = R / 'experiments.jsonl'
    old = ledger.read_text()
    experiments = [
        ('E036-q4-oracle-information-A', 'phase-a/report.md'),
        ('E037-q4-oracle-information-B', 'phase-b/report.md'),
        ('E038-q4-oracle-information-C', 'phase-c/report.md')]
    with ledger.open('a') as stream:
        for name, report in experiments:
            assert '"' + name + '"' not in old
            stream.write(json.dumps({'id': name, 'status': 'COMPLETE',
                                     'campaign': str(C), 'report': str(C / report),
                                     'recommendation': decision['conclusion'], 'utc': now}) + '\n')
    with (C / 'ledger.jsonl').open('a') as stream:
        stream.write(json.dumps({'phase': 'FINAL', 'state': 'COMPLETE', 'utc': now,
                                 'conclusion': decision['conclusion'],
                                 'primary_requests': 33, 'task_transfer_requests': 9,
                                 'serving_baseline_changed': False}) + '\n')
    print('LABORATORY_HANDOFF_COMPLETE', now, decision['conclusion'], flush=True)


if __name__ == '__main__':
    main()
