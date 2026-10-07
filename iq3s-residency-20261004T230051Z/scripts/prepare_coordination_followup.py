"""Predeclare the scoped GPU event explanation of all-local coordination results."""
from lab import ROOT,save
out=ROOT/'experiments/E021-device-plan-waits/v1'
assert not out.exists()
save(out/'protocol.json',{'question':'Why does safe GPU-local planning alone fail to improve end-to-end TG? Does host-plan suppression reduce measured GPU plan/CPU-completion waits, or only host work?',
 'evidence':'E016 exact-output clean confirmation unchanged; E019 removes redundant host work. E011 preserved original GPU event phases at layers2/24/40 are a same-workload diagnostic reference.',
 'change':'Separate default-off diagnostic build combines safe stable-ID+PLEfence+host-plan suppression with the same48externalCUDAevents and buffered real demand trace. Cache, GPU expert math, MTP, routing and resources unchanged.',
 'batch':'One fresh server/profile; same4096-input64-outputwarmup; one4096request/profile. No headline measurements or extra unchanged clean repetitions.',
 'validation':'13targetedtests and full actual output/router/MTP/heat/residency/head parity. Join event groups to true paths, stratify all-local/CPU/mapped. Onlythree selectedlayers; do notmultiply by48 or add overlapping timers.',
 'budget':'Same corrected device-plan explicit offsets/skip/CPU snapshots;48CUDAevents internalresource cost unknown. Exactexpertbytes/classes unchanged. No timing-overheadcertificate.',
 'completion':'Report phase distributions/hostplanning counts, preserve timing differences; discriminate exposed waits from redundant work. Choose any further kernel-copy experiment only from actual source/evidence.'})
save(out/'overrides.json',{'env':{'STRATA_VERIFY_DEVICE_PLAN':'1','STRATA_LAB_PLAN_IDS':'1','STRATA_LAB_SKIP_LOCAL_PLAN':'1','STRATA_LAB_MISS_WAITS':'1'},'diagnostic_only':True})
print(out)
