"""Bounded source-supported row-copy experiment; diagnostics precede clean speed."""
import argparse, shlex, subprocess, time
from lab import ROOT, load, save, owned_stop
ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['prerequisites','diagnostic','confirmation'])
a=ap.parse_args();experiment='E023-direct-parts';attempt='diagnostic-v1' if a.stage=='diagnostic' else 'v1'
variant='diagnostic-direct-parts-v1' if a.stage=='diagnostic' else 'direct-parts-v1'
base=ROOT/'experiments'/experiment/attempt;out=base/('confirmation-commands' if a.stage=='confirmation' else 'commands')
assert not out.exists();out.mkdir(parents=True);records=[];py=str(ROOT/'src/control/.venv/bin/python')
def call(name,cmd,timeout=300):
    path=out/f'{name}.log';start=time.time()
    try:
        with path.open('w') as f:r=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
    except subprocess.TimeoutExpired:
        owner=ROOT/'variants'/variant/'owned-process.json'
        if owner.exists():p=load(owner);owned_stop(p['pid'],p['create_time'])
        save(out/f'{name}-timeout.json',{'command':cmd,'timeout_s':timeout});raise
    records.append({'name':name,'command':cmd,'returncode':r.returncode,'elapsed_s':time.time()-start,'log':str(path)})
    save(out/'commands.json',records);print(name,r.returncode,path.read_text()[-2200:],flush=True)
    if r.returncode:raise SystemExit(r.returncode)
if a.stage!='confirmation':
    cmd=[py,'scripts/register_variant.py',variant,'--source',str(ROOT/'src'/variant),
         '--binary',str(ROOT/'builds'/variant/'strata'),'--overrides',
         str(ROOT/'experiments'/experiment/'v1/overrides.json')]
    if a.stage=='diagnostic':cmd+=['--diagnostic']
    call('register',cmd,60)
if a.stage=='prerequisites':
    call('all-tests',[py,'scripts/test_variant.py',variant,'--experiment',experiment,'--attempt',attempt],900)
    call('test-failure-audit',[py,'scripts/check_test_failures.py',experiment,'--attempt',attempt,'--expected-native-tests','69'],60)
    call('battery',[py,'scripts/correctness_battery.py','--variant',variant,'--experiment',experiment,
         '--attempt',attempt,'--reference',str(ROOT/'experiments/E006-frequency/correctness-r2/correctness/control')],600)
    call('ground-truth',[py,'scripts/check_battery.py',str(base/'correctness'/variant)],60)
elif a.stage=='diagnostic':
    call('targeted-native',[str(ROOT/'src/control/.venv/bin/ctest'),'--test-dir',str(ROOT/'builds'/variant),
         '--output-on-failure','--timeout','60','-R','(cache|adapt|async|verify|split|expert_multi|native_expert_parity|lab_direct_parts)','-j','1'],300)
    cmd=[py,'scripts/collect_traces.py','profiles','--variant',variant,'--experiment',experiment,'--attempt',attempt]
    launcher=ROOT/'variants'/variant/'diagnose-profiles.sh'
    launcher.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec '+' '.join(shlex.quote(x) for x in cmd)+' "$@"\n');launcher.chmod(0o755)
    call('profiles',[str(launcher)],900)
    for p in ['32k','128k']:
        folder=base/p
        call('strict-parity-'+p,[py,'scripts/check_trace_parity.py',str(folder/'traces/runtime-request2'),
             str(ROOT/f'experiments/E015-lowrank-router/v1/{p}/traces/runtime-request2'),
             '--output',str(folder/'parity.json')],150)
    save(base/'summary.json',{'state':'PASS','headline':False,'scope':'Exact recorded output/router/MTP/path/heat/residency/first-head parity at both profiles.'})
else:
    assert load(ROOT/'experiments'/experiment/'v1/tests/failure-audit.json')['state']=='PASS_WITH_KNOWN_ENVIRONMENT_LIMITS'
    assert load(ROOT/'experiments'/experiment/'v1/correctness'/variant/'ground-truth-checks.json')['state']=='PASS'
    assert load(ROOT/'experiments'/experiment/'diagnostic-v1/summary.json')['state']=='PASS'
    call('confirmation',[str(ROOT/'variants'/variant/'reproduce.sh'),'--experiment',experiment,'--attempt',attempt],1400)
    call('analysis',[py,'scripts/compare_confirmation.py','--experiment',experiment,'--reference','E002-controls'],180)
