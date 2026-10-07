"""One existing coarse pool sleep setting, evaluated separately from the row-copy change."""
import argparse, os, shlex, subprocess, time
from lab import ROOT,load,save,owned_stop
ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['prerequisites','diagnostic','confirmation'])
a=ap.parse_args();experiment='E024-pool-wait';attempt='diagnostic-v1' if a.stage=='diagnostic' else 'v1'
variant='diagnostic-pool-wait-v1' if a.stage=='diagnostic' else 'pool-wait-v1'
base=ROOT/'experiments'/experiment/attempt;out=base/('confirmation-commands' if a.stage=='confirmation' else 'commands')
assert not out.exists();out.mkdir(parents=True);records=[];py=str(ROOT/'src/control/.venv/bin/python')
def call(name,cmd,timeout=300,env=None):
    path=out/f'{name}.log';start=time.time()
    try:
        with path.open('w') as f:r=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=timeout,env=env)
    except subprocess.TimeoutExpired:
        owner=ROOT/'variants'/variant/'owned-process.json'
        if owner.exists():p=load(owner);owned_stop(p['pid'],p['create_time'])
        save(out/f'{name}-timeout.json',{'command':cmd,'timeout_s':timeout});raise
    records.append({'name':name,'command':cmd,'returncode':r.returncode,'elapsed_s':time.time()-start,
                    'log':str(path),'pool_spin_us':env.get('STRATA_POOL_SPIN_US') if env else None})
    save(out/'commands.json',records);print(name,r.returncode,path.read_text()[-2200:],flush=True)
    if r.returncode:raise SystemExit(r.returncode)
if a.stage!='confirmation':
    source='diagnostic-coordination-v1' if a.stage=='diagnostic' else 'control'
    overrides=ROOT/'experiments'/experiment/'v1/overrides.json'
    if a.stage=='diagnostic':
        p=load(overrides);p['env']['STRATA_LAB_MISS_WAITS']='1';p['diagnostic_only']=True
        overrides=base/'overrides.json';save(overrides,p)
    cmd=[py,'scripts/register_variant.py',variant,'--source',str(ROOT/'src'/source),
         '--binary',str(ROOT/'builds'/source/'strata'),'--overrides',str(overrides)]
    if a.stage=='diagnostic':cmd+=['--diagnostic']
    call('register',cmd,60)
if a.stage=='prerequisites':
    env=os.environ.copy();env['STRATA_POOL_SPIN_US']='100'
    call('sleep-wakeup-stress',[str(ROOT/'builds/control/pool_stress'),'8'],60,env)
    call('real-IQ',[str(ROOT/'builds/control/native_expert_parity'),
         '/srv/ai/models/strata/models/IQ3_S/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf','0','1','2','12'],300,env)
    call('battery',[py,'scripts/correctness_battery.py','--variant',variant,'--experiment',experiment,
         '--attempt',attempt,'--reference',str(ROOT/'experiments/E006-frequency/correctness-r2/correctness/control')],600)
    call('ground-truth',[py,'scripts/check_battery.py',str(base/'correctness'/variant)],60)
    save(base/'prerequisites.json',{'state':'PASS','full_suite_reference':{'native':str(ROOT/'logs/native-tests.log'),'Python':str(ROOT/'logs/python-tests.log')},
         'scope':'Unchanged control binary; new100us pool sleep stress, real native experts and ten identical greedy inputs.',
         'native_environment_limits':'Original four missing-fixture/VM failures are unchanged; no new source or dependency.'})
elif a.stage=='diagnostic':
    cmd=[py,'scripts/collect_traces.py','profiles','--variant',variant,'--experiment',experiment,'--attempt',attempt]
    launcher=ROOT/'variants'/variant/'diagnose-profiles.sh'
    launcher.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec '+' '.join(shlex.quote(x) for x in cmd)+' "$@"\n');launcher.chmod(0o755)
    call('profiles',[str(launcher)],900)
    for p in ['32k','128k']:
        folder=base/p;reference=ROOT/f'experiments/E021-device-plan-waits/v1/off/{p}'
        call('strict-parity-'+p,[py,'scripts/check_trace_parity.py',str(folder/'traces/runtime-request2'),
             str(reference/'traces/runtime-request2'),'--output',str(folder/'parity.json')],150)
        call('wait-analysis-'+p,[py,'scripts/analyze_coordination_waits.py',p,'--experiment',experiment,
             '--attempt',attempt,'--reference-experiment','E021-device-plan-waits',
             '--reference-attempt','v1/off'],150)
    save(base/'summary.json',{'state':'PASS','headline':False,'same_diagnostic_binary_reference':'E021 OFF',
         'scope':'Exact recorded outputs/router/MTP/path/cache/heat/first-head at both profiles.'})
else:
    assert load(ROOT/'experiments'/experiment/'v1/prerequisites.json')['state']=='PASS'
    assert load(ROOT/'experiments'/experiment/'diagnostic-v1/summary.json')['state']=='PASS'
    call('confirmation',[str(ROOT/'variants'/variant/'reproduce.sh'),'--experiment',experiment,'--attempt',attempt],1400)
    call('analysis',[py,'scripts/compare_confirmation.py','--experiment',experiment,'--reference','E002-controls'],180)
