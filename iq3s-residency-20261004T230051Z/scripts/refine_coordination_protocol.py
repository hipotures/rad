"""Preserve the initial plan and record the better same-binary diagnostic before any build."""
import shutil
from lab import ROOT,load,save
base=ROOT/'experiments/E021-device-plan-waits/v1'
assert not (base/'build').exists() and not (base/'protocol-initial.json').exists()
shutil.copy2(base/'protocol.json',base/'protocol-initial.json')
p=load(base/'protocol.json')
p['refinement']='Source inspection shows old phase0 begins after GPU resident_plan, so it cannot measure its cost. Addphase4 for GPU resident planning + true demand doorbell,60externalCUDAevents. SamebinaryOFF/ON diagnostics atbothprofiles, avoiding attribution to two independently rebuilt binaries.'
p['batch']='Fourfreshserverdiagnostics: OFF32k,OFF128k,ON32k,ON128k. Same64outputwarmup+one4096requesteach. Defaultsettings unchanged. No clean measurements or extraunchangedheadline requests.'
p['analysis']='Five phases, withphase4 scored separately; originalfourphases preserve meanings. Sameinput/output/router/MTP/heat/caps parity and fullcountervalidation. Compare distributions/all-local vsnonlocal andhostwork; diagnosticTGexcluded.'
p['budget']='60internalCUDAevents (not48); explicitGPU0OFF/orcorrecteddeviceplanoffsets/skipON; mappedCPU0OFF/4000+3680ON. Slots/bytesremainfrozen. Internaldriverallocationcostunknown.'
save(base/'protocol.json',p)
save(base/'off-overrides.json',{'env':{'STRATA_LAB_MISS_WAITS':'1'},'diagnostic_only':True})
save(base/'on-overrides.json',{'env':{'STRATA_VERIFY_DEVICE_PLAN':'1','STRATA_LAB_PLAN_IDS':'1','STRATA_LAB_SKIP_LOCAL_PLAN':'1','STRATA_LAB_MISS_WAITS':'1'},'diagnostic_only':True})
print(p['refinement'])
