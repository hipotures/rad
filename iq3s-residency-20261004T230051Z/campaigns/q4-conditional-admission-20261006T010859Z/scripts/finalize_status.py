"""Consolidate this bounded campaign; preserve all previous research sections."""
from campaign import C, R, load, save
import datetime, json

now = datetime.datetime.now(datetime.timezone.utc)
decision = load(C/'decision.json')
assert load(C/'analysis/final-audit.json')['PASS']
assert load(C/'git/prior-v2-final-verification.json')['PASS']
assert load(C/'git/model-final-fullhash-verification.json')['PASS']
assert len(load(C/'analysis/launcher-smokes.json')) == 6
assert all(x['PASS'] for x in load(C/'analysis/launcher-smokes.json'))
elapsed = (now - datetime.datetime.fromisoformat(load(C/'deadline.json')['start'])).total_seconds()
state = {
    'state': 'COMPLETE_MECHANISM_ONLY', 'phase': 'A/B/C complete',
    'completed_utc': now.isoformat(), 'elapsed_s': elapsed,
    'deadline': load(C/'deadline.json'), 'running': None, 'pending': [],
    'completed': [
        'E033: reason decomposition; historical ambiguity preserved',
        'E034: 12 independent episodes, sealed splits, frozen logistic/rules and holdout',
        'E035: 18/18 valid primary requests, nine exact-input pairs, no retries',
        '12 independent application requests; three fresh pairs per task',
        'One candidate-OFF timing guard; matched reactive/unfiltered/conditional traces',
        '10 real CUDA scheduler/byte safety tests; HTTP cancel/drain/next request',
        '68 native tests: 62 pass, 2 skip, 4 preserved fixture/environment failures',
        'Six advertised launcher smoke checks and binary/model/source verification',
        'Full model hashes and 4776 prior-v2 artifact hashes verified unchanged',
        'Analysis, report, plots, exact launchers and owned-process/GPU cleanup'
    ],
    'recommendation': decision['recommendation'],
    'production_baseline': decision['production_baseline'], 'deployment_switch': False,
    'current_winner': 'Unchanged control remains the practical real-use reference',
    'excluded_runs': 'No invalid primary attempt; exploratory, instrumented traces, safety and OFF guard are excluded from headline matrix',
    'unfinished_due_to_deadline': [],
    'next_exact_action': 'Review the completed report. Do not start another research phase automatically.',
}
save(C/'STATUS.json', state)
(C/'STATUS.md').write_text(
    '# Q4 conditional admission v3 — complete\n\n'
    f"State: {state['state']}. Recommendation: {decision['recommendation']}. "
    'Production remains the unchanged Q4 100 µs control.\n\n'
    f'Completed after {elapsed/3600:.2f} h, before the eight-hour deadline. '
    'The admission mechanism improves, but throughput attribution is insufficient; '
    'the apparent 32K gain has an OFF-build/environment timing confound.\n\n'
    'All 18 primary requests, 12 application requests, diagnostics, failures and safety evidence are preserved. '
    'All six launchers passed smoke. No owned server/training/profiler remains; both GPU compute lists are empty.\n\n'
    '[Report](report.md) · [Machine-readable status](STATUS.json) · '
    '[Decisions](DECISIONS.md) · [Control](launchers/control/README.md) · '
    '[Experimental candidate](launchers/conditional/README.md)\n\n'
    'Pending: none in the bounded protocol. No automatic next experiment.\n'
)
ledger = C/'ledger.jsonl'
rows = [json.loads(line) for line in ledger.read_text().splitlines() if line.strip()]
if not any(row['id'] == 'E035' for row in rows):
    with ledger.open('a') as out:
        out.write(json.dumps({'id':'E035','phase':'C','state':state['state'],
            'time':now.isoformat(),'report':str(C/'phase-c/report.md'),
            'primary_valid':18,'independent_valid':12,'OFF_guard':1,
            'new_diagnostic_ablations':2,'advertised_launcher_smokes':6,
            'recommendation':decision['recommendation'],'production_baseline':decision['production_baseline'],
            'timing_attribution':'32K gain confounded by candidate-OFF; output/MTP diverge'})+'\n')
root_status = R/'STATUS.md'
text = root_status.read_text()
start = '<!-- q4-conditional-admission-latest -->'
end = '<!-- /q4-conditional-admission-latest -->'
section = start+'\n## Q4 conditional admission v3 — complete\n\n'+(
    f"E033–E035: {state['state']}. Recommendation: {decision['recommendation']}. "
    'Real-use production remains KEEP_Q4_100US_BASELINE.\n\n'
    'Completed 18/18 primary requests, 12 application requests, matched ablations, '
    'safety tests and six launcher smokes. Previous v2/model hashes match; both GPUs are free.\n\n'
    f'[Report](campaigns/{C.name}/report.md) · '
    f'[Status](campaigns/{C.name}/STATUS.md) · '
    f'[Control launchers](campaigns/{C.name}/launchers/control/README.md)\n\n'
    'Pending: none in the bounded protocol. No further research starts automatically.\n'
)+end
assert start in text and end in text
root_status.write_text(text[:text.index(start)]+section+text[text.index(end)+len(end):])
active = load(R/'active-campaign.json')
assert active['path'] == str(C)
active.update(state=state['state'],completed_utc=now.isoformat(),report=str(C/'report.md'),
              recommendation=decision['recommendation'],elapsed_s=elapsed)
save(R/'active-campaign.json', active)
root_ledger = load(R/'candidate-ledger.json')
root_ledger['followup_phases']['Q4_CONDITIONAL_ADMISSION_V3'] = {
    'experiments':['E033','E034','E035'],'report':str((C/'report.md').relative_to(R)),
    'state':state['state'],'recommendation':decision['recommendation'],
    'production_baseline':decision['production_baseline'],
    'next':'Same-binary OFF/ON timing attribution is a proposed future experiment, not started.'}
save(R/'candidate-ledger.json', root_ledger)
index = R/'launch-index.md'
marker = '<!-- q4-conditional-admission-v3-launchers -->'
if marker not in index.read_text():
    with index.open('a') as out:
        out.write('\n'+marker+'\n## Q4 conditional admission v3 handoff\n\n'
            f'[Report](campaigns/{C.name}/report.md). Scientific classification: '
            'PROMISING_CONDITIONAL_ADMISSION; practical production remains unchanged control.\n\n'
            '| Variant | Disposition | Source | Config and commands |\n'
            '|---|---|---|---|\n'
            f'| control | UNCHANGED_REAL_USE_BASELINE | `6f32ec070f23ced9f50e704d854d775da52591ab` | [README](campaigns/{C.name}/launchers/control/README.md) |\n'
            f'| conditional | SAFE_EXPERIMENTAL_MECHANISM_ONLY | `0266e540087acb98acd183546edeab3164aee8fd` | [README](campaigns/{C.name}/launchers/conditional/README.md) |\n\n'
            'Both variants have start-32k.sh, start-128k.sh, start-256k.sh and stop.sh. '
            'Explicit LAN bind: `--host 0.0.0.0 --port 8080`. Run one server at a time. '
            'All six starts were smoke-tested; no automatic rebuild or download. '
            'Normal user launchers were not altered.\n')
for owner in [C/'owned-process.json', C/'launchers/control/owned-process.json', C/'launchers/conditional/owned-process.json']:
    if owner.exists():
        record = load(owner)
        record.update(final_state='STOPPED_VERIFIED',final_audit=str(C/'analysis/final-audit.json'))
        save(owner,record)
print('STATUS_COMPLETE', state['state'], elapsed/3600, flush=True)
