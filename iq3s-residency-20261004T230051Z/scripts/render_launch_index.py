"""Index frozen launchers and honest normal-flow evidence, including later replay."""
import shlex
from lab import ROOT,load,save
states={'device-plan-ids-v1':'UNSAFE_PLE_DEPENDENCY_REPRODUCER_ONLY',
        'diagnostic-device-plan-ids-v1':'UNSAFE_PLE_DEPENDENCY_REPRODUCER_ONLY',
        'diagnostic-plan-compare-v1':'UNSAFE_AND_FENCED_ARITHMETIC_REPRODUCER_ONLY',
        'diagnostic-direct-parts-v1':'INVALID_FIRST_HEAD_CAPTURE_REPRODUCER_ONLY',
        'diagnostic-v6':'INVALID_EVENT_CAPTURE_REPRODUCER_ONLY'}
python=str(ROOT/'src/control/.venv/bin/python')
processes=[]
for path in (ROOT/'experiments').rglob('process.json'):
    conf=path.parent/'config.json'
    if conf.exists():processes.append((path,load(conf)))
records=[]
for folder in sorted((ROOT/'variants').iterdir()):
    if not (folder/'32k.json').exists():continue
    cfg=load(folder/'32k.json')
    usage=[]
    for path,c in processes:
        if c.get('build_variant')==folder.name:
            usage.append({'process_record':str(path),'profile':c.get('max_total_context'),
                          'source_sha':c['source_sha'],'binary_sha256':c['binary_sha256'],
                          'startup_record':str(path.parent/'raw/startup.json') if (path.parent/'raw/startup.json').exists() else None,
                          'warmup_record':str(path.parent/'raw/warmup.json') if (path.parent/'raw/warmup.json').exists() else None})
    state=states.get(folder.name,'DIAGNOSTIC_ONLY' if cfg['headline_instrumentation']!='OFF' else 'CLEAN_EXPERIMENTAL_OR_CONTROL')
    if not usage:state='UNEXERCISED_NOT_READY'
    if cfg['headline_instrumentation']!='OFF' and not list(folder.glob('diagnose-*.sh')):
        if folder.name=='diagnostic-plan-compare-v1':
            command=[python,str(ROOT/'scripts/reproduce_plan_comparison.py')]
            launcher=folder/'diagnose-plan-comparison.sh'
        else:
            command=[python,str(ROOT/'scripts/collect_traces.py'),'profiles','--variant',folder.name,
                     '--experiment','YOUR_NEW_DIAGNOSTIC','--attempt','v1']
            launcher=folder/'diagnose-profiles.sh'
        launcher.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec '+' '.join(shlex.quote(x) for x in command)+' "$@"\n')
        launcher.chmod(0o755)
    commands={mode:str(folder/f'{mode}.sh') for mode in ['start-32k','start-128k','benchmark-32k','benchmark-128k','reproduce','stop']}
    # Some original evidence wrappers used a relative script while the recorded
    # runner supplied cwd=ROOT. Make future copy/paste invocation independent
    # of the caller's terminal directory without changing frozen settings.
    for launcher in folder.glob('*.sh'):
        content=launcher.read_text()
        cd='cd '+shlex.quote(str(ROOT))+'\n'
        if cd not in content:
            launcher.write_text(content.replace('set -euo pipefail\n','set -euo pipefail\n'+cd,1))
            launcher.chmod(0o755)
    experiment_ids=sorted({str(p['process_record']).split('/experiments/',1)[1].split('/',1)[0].split('-')[0] for p in usage})
    records.append({'variant':folder.name,'state':state,'source_sha':cfg['source_sha'],
        'binary_sha256':cfg['binary_sha256'],'build':cfg['exe'],'source':cfg['cwd'],
        'configs':[str(folder/'32k.json'),str(folder/'128k.json')],
        'environment':cfg['env'],'launch_commands':commands,'exercised_sessions':usage,
        'experiment_ids':experiment_ids,
        'diagnostic_reproducers':[str(p) for p in sorted(folder.glob('diagnose-*.sh'))],
        'launcher_validation':'Shared Session launch backend exercised in linked smoke/benchmark/diagnostic flows. This does not assert every thin shell alias was separately invoked.' if usage else 'UNEXERCISED'})
    doc=[f'# {folder.name}','',f'State: {state}.',
         f'Frozen source: `{cfg["source_sha"]}`. Binary: `{cfg["exe"]}`; SHA256 `{cfg["binary_sha256"]}`.',
         '', 'Both frozen JSON configurations print at startup. The shared launcher checks source/binary identities, uses private host 127.0.0.1, supports an explicit port override, refuses collisions, and performs no build or update. Model weights are shared read-only.', '']
    if 'UNSAFE' in state or 'INVALID' in state or 'UNEXERCISED' in state:
        doc+=['This variant is retained for reproducing its documented failure, not advertised as a ready server or throughput candidate. Use the corresponding repaired variant for inference.','']
    else:
        doc+=['```bash',commands['start-32k']+' --port 18132',commands['start-128k']+' --port 18132',commands['stop'],'```','']
    if cfg['headline_instrumentation']=='OFF':
        doc+=['Later explicit replay (after the recorded campaign deadline):','```bash',
              commands['benchmark-32k']+' --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction',
              commands['benchmark-128k']+' --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction',
              commands['reproduce']+' --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction','```','']
    else:
        runner=records[-1]['diagnostic_reproducers'][0]
        opts=' --attempt YOUR_NEW_ATTEMPT --reproduction' if folder.name=='diagnostic-plan-compare-v1' else ' --experiment YOUR_NEW_DIAGNOSTIC --attempt v1 --reproduction'
        doc+=['Diagnostic replay only; rates must not enter clean speed tables:','```bash',runner+opts,'```','']
    doc+=['Use one server at a time and new versioned output directories. Existing attempts refuse overwrite. The --reproduction switch is permitted only after the hard deadline and cannot extend the active campaign. No normal user launcher changes.',
          '',records[-1]['launcher_validation'],'', 'Actual process/startup/warmup evidence is linked in ../../launch-index.json. The thin aliases are syntax checked during final audit; generated replay wrappers are not claimed to have been separately timed.']
    (folder/'README.md').write_text('\n'.join(doc)+'\n')
save(ROOT/'launch-index.json',records)
text=['# Frozen launch index','',
    'Use one server at a time. Starts verify the preserved binary hash and source SHA, print the resolved config, support an explicit private port and refuse active GPU/port collisions. No build, fetch or update occurs during launch. Stop commands validate PID creation time and stop only owned process groups.',
    '', 'Every experiment uses existing unchanged IQ3_S files. Actual start/config evidence is in the process records linked in launch-index.json. Diagnostic/unsafe entries are retained for investigation, not production or headline speed.',
    '', '| Experiments | Variant | State | Source | Build / config | 32K start | 128K start | Stop | Reproduce |',
    '|---|---|---|---|---|---|---|---|---|']
for r in records:
    relative='variants/'+r['variant']+'/'
    start32='`'+r['launch_commands']['start-32k']+' --port 18132`'
    start128='`'+r['launch_commands']['start-128k']+' --port 18132`'
    if 'UNSAFE' in r['state'] or 'INVALID' in r['state'] or 'UNEXERCISED' in r['state']:
        start32=start128='Not advertised as ready'
    diag=r['diagnostic_reproducers']
    opts=' --attempt NEW_ATTEMPT --reproduction' if r['variant']=='diagnostic-plan-compare-v1' else ' --experiment NEW_EXPERIMENT --attempt v1 --reproduction'
    reproduce='`'+(diag[0]+opts if diag else r['launch_commands']['reproduce']+opts)+'`'
    text.append(f"| {', '.join(r['experiment_ids'])} | {r['variant']} | {r['state']} | `{r['source_sha']}` | [{r['variant']} configs]({relative}README.md) | {start32} | {start128} | `{r['launch_commands']['stop']}` | {reproduce} |")
text += ['', 'Each benchmark command needs its own new versioned output path. Do not repeat unchanged campaign points beyond the recorded three-attempt limit. Exact binaries, full environment and both profile configs are included in launch-index.json. The explicit --reproduction flag is available only after the recorded campaign deadline; it never extends the active campaign. All replay examples override the experiment/attempt to avoid old results.',
         '', 'Validation evidence: the same Session launcher backend was exercised in each linked normal smoke/benchmark/diagnostic flow. Individual thin shell aliases are syntax checked, not all separately started. Newly generated replay wrappers do not create additional headline repetitions.',
         '', 'The clean selector/device-plan experiments are research candidates; the unchanged CURRENT control remains available. No normal user launcher is replaced. Unsafe device-plan v1 requires the independently repaired PLE fence (v2) for correct use. The failed event-capture variant has a separate repaired diagnostic variant.']
(ROOT/'launch-index.md').write_text('\n'.join(text)+'\n')
print('Indexed',len(records),'variants; actual exercised sessions',sum(len(r['exercised_sessions']) for r in records))
