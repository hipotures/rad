"""Publish only this campaign's completion pointers; preserve older lab records."""
from campaign import C, R, load, save
import datetime


def main():
    campaign_status = load(C / 'STATUS.json')
    assert campaign_status['state'].startswith('COMPLETE')
    decision = load(C / 'decision.json')
    lab_status = load(R / 'STATUS.json')
    lab_status['latest_campaign'] = {
        'path': str(C),
        'status': str(C / 'STATUS.json'),
        'state': campaign_status['state'],
        'phases': campaign_status['phases'],
        'recommendation': decision['recommendation'],
        'report': str(C / 'report.md'),
        'baseline': 'Frozen Q4/100us control; no normal user launcher switch',
        'updated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    save(R / 'STATUS.json', lab_status)
    begin = '<!-- q4-residency-v2-latest -->'
    end = '<!-- /q4-residency-v2-latest -->'
    relative = str(C.relative_to(R))
    block = '\n'.join([
        begin, '## Q4 Residency v2 — complete', '',
        f"All three phases: COMPLETE_MIXED. Recommendation: {decision['recommendation']}.", '',
        'Completed 27/27 fixed-4096 primary attempts, OFF guards, independent application cases, transaction diagnostics, cancellation/drain tests and all nine advertised launcher smokes. No owned serving/training/profiling process remains.', '',
        'Frozen Q4: Strata 0.1.39, K=24, PCIe=0.28, pool=100 us, workers=15. Previous data and normal user launchers remain untouched.', '',
        f'[Report]({relative}/report.md) · [Status]({relative}/STATUS.md) · [Selected launchers]({relative}/launchers/control/README.md)', '',
        'Pending: none in the bounded protocol. Do not start a new research phase automatically.', end,
    ])
    status_path = R / 'STATUS.md'
    text = status_path.read_text()
    assert text.count(begin) == 1 and text.count(end) == 1
    first, rest = text.split(begin, 1)
    _, tail = rest.split(end, 1)
    status_path.write_text(first + block + tail)

    heading = '## Q4 Residency v2 handoff — 20261005T202441Z'
    index_path = R / 'launch-index.md'
    index = index_path.read_text()
    assert heading not in index, 'Completion index already written; no duplicate append'
    entries = [heading, '',
        f'Recommendation: `{decision["recommendation"]}`. [Campaign report]({relative}/report.md).', '',
        'Default bind is localhost. Explicit overrides: `--host 0.0.0.0 --port 8080`. Start one server at a time; all nine startup paths were smoked. Experimental ON variants may change generated output and are not selected for production.', '',
        '|Variant|Disposition|Source|Config and commands|', '|---|---|---|---|']
    commands = []
    for name, disposition in [('control', 'SELECTED_UNCHANGED_BASELINE'),
                               ('history-v2', 'EXPERIMENTAL_MIXED'),
                               ('early-v1', 'EXPERIMENTAL_NO_CONSISTENT_GAIN')]:
        path = C / 'launchers' / name
        config = load(path / '128k.json')
        entries.append(f'|{name}|{disposition}|`{config["source_sha"]}`|[README]({relative}/launchers/{name}/README.md)|')
        commands.extend(['', f'{name}:', '', f'```bash\ncd {path}\n./start-32k.sh\n./start-128k.sh\n./start-256k.sh\n./stop.sh\n./reproduce.sh --profile 128k --port 18140\n```', ''])
    entries.extend(commands)
    index_path.write_text(index + '\n' + '\n'.join(entries).rstrip() + '\n')
    (C / 'RECOVERY-NEXT.md').write_text(
        '# Completed campaign checkpoint\n\n'
        'All bounded A/B/C phases and handoff checks are complete. '
        f'Recommendation: {decision["recommendation"]}.\n\n'
        'No experiment is running and no new experiment should start automatically. '
        'The report, summaries, phase reports, manifest, local source commits and launchers preserve the evidence. '
        'Use launchers/control for real-prompt testing after review.\n')
    print('LAB_COMPLETION_POINTERS_WRITTEN')


if __name__ == '__main__':
    main()
