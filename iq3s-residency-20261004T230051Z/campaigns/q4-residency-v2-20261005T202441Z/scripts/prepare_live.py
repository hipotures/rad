"""Freeze candidate/OFF/diagnostic configs from verified identities; no runtime tuning."""
from campaign import C,load,save
from pathlib import Path

def main():
 assert (C/'phase-b/report.md').exists()
 definitions={
  'history-v2':('history-v2',{'STRATA_Q4_HISTORY':'1'},'clean speed, counters only'),
  'history-off':('history-v2',{},'OFF guard; original algorithm'),
  'early-v1':('early-v1',{'STRATA_Q4_EARLY':'1'},'clean speed, aggregate counters only'),
  'early-off':('early-v1',{},'OFF guard; no predictor/reserve/worker allocation'),
  'early-reactive':('early-v1',{'STRATA_Q4_EARLY':'1','STRATA_Q4_EARLY_REACTIVE':'1'},'matched2-spare scheduler without native prediction'),
  'early-diagnostic':('early-v1',{'STRATA_Q4_EARLY':'1','STRATA_Q4_EARLY_DIAGNOSTIC':'1'},'buffered transaction events and bounded backing-byte readback; never headline'),
  'early-wrong':('early-v1',{'STRATA_Q4_EARLY':'1','STRATA_Q4_EARLY_DIAGNOSTIC':'1','STRATA_Q4_EARLY_FORCE_EXPERT':'511'},'diagnostic wrong predictions; mathematics still routes true experts'),
  'early-delayed':('early-v1',{'STRATA_Q4_EARLY':'1','STRATA_Q4_EARLY_DIAGNOSTIC':'1','STRATA_Q4_EARLY_DELAY_US':'5000'},'diagnostic deliberately late producer; never headline')}
 for variant,(build,extra,scope) in definitions.items():
  ip=C/'git/builds'/build/'identity.json'
  if not ip.exists():continue
  ident=load(ip)
  for profile in ['32k','128k','256k']:
   out=C/'configs'/f'{variant}-{profile}.json';assert not out.exists(),'Config remains frozen; do not overwrite'
   cfg=load(C/'configs'/f'control-{profile}.json');cfg.update(exe=ident['exe'],cwd=ident['source'],Strata_HEAD=ident['source_sha'],source_sha=ident['source_sha'],binary_sha256=ident['binary_sha256'],build_variant=variant,headline_instrumentation=scope)
   cfg['env'].update(extra);cfg['variant_overrides']={'scope':scope,'default_OFF':True,'same_K24_and_pcie0_28':True,'extra_explicit_GPU_scratch_bytes':0,
     'charged_resident_capacity_reduction_per_device':1 if extra.get('STRATA_Q4_EARLY')=='1' else 0,
     'early_model':str(C/'checkpoints/linear.npz') if extra.get('STRATA_Q4_EARLY')=='1' else None}
   save(out,cfg)
 print('LIVE_CONFIGS_FROZEN',flush=True)
if __name__=='__main__':main()
