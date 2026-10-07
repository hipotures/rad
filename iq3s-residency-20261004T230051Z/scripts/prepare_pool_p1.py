"""Freeze P1 after the scoped P0-A gate; no new CPU scheduling implementation."""
import copy, pathlib, subprocess
from lab import ROOT, load, save
base=ROOT/'experiments/E027-pool-baseline'
assert not base.exists()
p0=load(ROOT/'experiments/E026-pool-generalization/summary.json')
assert p0['decision']=='P0-A' and p0['state']=='COMPLETE_SCOPED_VALIDATION'
save(base/'protocol.json',{
 'phase':'P1','selected_policy':'STRATA_POOL_SPIN_US=100, unchanged CURRENT executable',
 'reason':'Independent P0 latency improvements, math128K neutral; no serious consistent miss-heavy regression. Avoid an unjustified new synchronization subsystem.',
 'stress':'Existing random wake stress plus separately compiled targeted test linked to unchanged CURRENT CPU library: many short bursts, long all-local/no-job intervals, alternating bursts, repeated destructor/wakeup.',
 'confirmation':'Standard saved workload, paired fresh server each policy/replicate; fixed saved4096input64output warmup then4096output.3valid maximum each/profile/policy. This differs from old E024 serial cache-history protocol and common frontend captures actual IDs.',
 'independent_confirmation_reused':'E026 all3families/bothprofiles/3replicas. Do not repeat any unchanged independent point.',
 'frozen_architecture':'K25/pcie0.28/workers15/spec4/minp0.5/INT8/prefillauto/suffix0/reuse0; max32768 or131072',
 'off_control':'Same control source and binary; only100us env differs',
 'invalid':'Retain early stop/crash/protocol failure; no favorable retries',
 'new_experiment_scope':'Paired fresh-server standard workload confirmation and targeted wakeup safety; not a threshold sweep.'})
old=load(ROOT/'workloads/manifest.json');new=copy.deepcopy(old)
new['payloads']={'warmup':old['payloads']['warmup']}
for profile in ['32k','128k']:
 for n in [1,2,3]:new['payloads'][f'standard-{profile}-run{n}']=old['payloads'][f'{profile}-run{n}']
save(base/'workloads/manifest.json',new)
py=str(ROOT/'src/control/.venv/bin/python')
for name,role in [('p1-pool-default','pool-p0-default'),('p1-baseline','pool-p0-100')]:
 override=base/(name+'-overrides.json');env={} if role=='pool-p0-default' else {'STRATA_POOL_SPIN_US':'100'}
 save(override,{'env':env,'extra_explicit_GPU_bytes':0,'scheduling_only':'P1 frozen existing pool knob; no source/runtime change'})
 subprocess.run([py,'scripts/register_variant.py',name,'--source',str(ROOT/'src/control'),'--binary',str(ROOT/'builds/control/strata'),'--overrides',str(override)],cwd=ROOT,check=True)
 for profile in ['32k','128k']:
  cfg=load(ROOT/'variants'/name/f'{profile}.json');cfg['server_entrypoint']=str(ROOT/'scripts/serve_capture.py');cfg['frontend_capture']='Common actual-ID wrapper; no binary changes';save(ROOT/'variants'/name/f'{profile}.json',cfg)
# Preserve a dedicated driver and analyzer rather than silently changing E026.
s=(ROOT/'scripts/run_pool_independent.py').read_text().replace('E026-pool-generalization','E027-pool-baseline').replace("['code','math','prose']","['standard']").replace("choices=['code','math','prose']","choices=['standard']").replace("'pool-p0-default' if role=='default' else 'pool-p0-100'","'p1-pool-default' if role=='default' else 'p1-baseline'").replace('P0_REQUESTS_COMPLETE','P1_REQUESTS_COMPLETE')
(ROOT/'scripts/run_pool_p1.py').write_text(s)
s=(ROOT/'scripts/analyze_pool_independent.py').read_text().replace('E026-pool-generalization','E027-pool-baseline').replace("['code','math','prose']","['standard']").replace("'phase':'P0'","'phase':'P1'").replace('E026: P0 independent-workload pool validation','E027: P1 paired standard-workload confirmation')
(ROOT/'scripts/analyze_pool_p1.py').write_text(s)
print('P1_PREDECLARED',flush=True)
