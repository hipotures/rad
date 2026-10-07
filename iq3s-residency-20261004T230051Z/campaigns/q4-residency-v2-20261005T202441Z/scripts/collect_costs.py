"""Serial diagnostic plan, after the existing collector; never headline timing."""
from pathlib import Path
import json, os, subprocess, time
import psutil
import xml.etree.ElementTree as ET
from campaign import C, R, load, save, guard, point, status

def main():
    # This specific PID and start identity are retained in the process record.
    prior=1814502
    while psutil.pid_exists(prior):
        guard()
        time.sleep(15)
    ident=load(C/'git/builds/cost-router-v1/identity.json')
    env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']='0,1'
    test_dir=C/'analysis/cost-router-tests';test_dir.mkdir(exist_ok=False)
    command=[str(R/'src/control/.venv/bin/ctest'),'--test-dir',ident['build'],
             '--output-on-failure','--timeout','120','--output-junit',str(test_dir/'junit.xml')]
    with (test_dir/'suite.log').open('x') as f:
        start=time.time();res=subprocess.run(command,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900)
    save(test_dir/'result.json',{'command':command,'exit_code':res.returncode,'wall_s':time.time()-start,
                               'interpretation':'Read each failure before any correctness claim; tests precede diagnostic requests'})
    print('TEST_SUITE',res.returncode,flush=True)
    # Suite includes negative native formats and fixture-dependent cases. A
    # failure is preserved, not automatically called a new runtime regression.
    text=(test_dir/'suite.log').read_text()
    root=ET.parse(test_dir/'junit.xml').getroot()
    failures=[node.attrib.get('name') for node in root.iter('testcase') if node.find('failure') is not None]
    known={'ple_parity','platform_memory_test','expert_parity','pool_test'}
    save(test_dir/'failure-classification.json',{'failures':failures,'known_previous_failures':sorted(known),
            'new_failures':sorted(set(failures)-known),
            'prior_log':str(R/'experiments/E003-diagnostics/v5/tests/native-tests.log')})
    if set(failures)-known or (res.returncode and not failures):
        raise RuntimeError('New/incomplete correctness failure; inspect before diagnostic inference')
    for horizon in [8,1,4]:
        variant=f'cost-h{horizon}'
        for profile in ['32k','128k','256k']:
            cfg=load(C/'configs'/f'control-{profile}.json')
            cfg.update(exe=ident['exe'],cwd=ident['source'],source_sha=ident['source_sha'],
                       Strata_HEAD=ident['source_sha'],binary_sha256=ident['binary_sha256'],
                       build_variant=variant,headline_instrumentation='ON: costs/native-router diagnostic only')
            cfg['env'].update(STRATA_LAB_GPU_ROUTER='1',STRATA_LAB_MISS_WAITS='1',
                              STRATA_Q4_COPY_COST='1',STRATA_Q4_ROUTER_HORIZON=str(horizon))
            cfg['variant_overrides']={'diagnostic_only':True,'native_gate_pilot_layers':[5,12,25,32,38],
                                      'horizon_layers':horizon,'extra_explicit_GPU_bytes_per_device':320,
                                      'timing_event_resources':'charged by observed capacities/VRAM; not assumed free'}
            save(C/'configs'/f'{variant}-{profile}.json',cfg)
        if horizon==8:
            for profile in ['32k','128k','256k']:point(variant,profile,1,True)
            names=['dev-code','dev-math','cal-prose','hold-code','hold-structured','hold-math']
        else:
            names=['dev-code','dev-math','cal-prose']
        for name in names:point(variant,'32k',1,True,name)
    status('A_COSTS_COLLECTED',phase='A',running=None,next_exact_action='Validate costs, causal prediction timing and current replay; write Phase A')

if __name__=='__main__':main()
