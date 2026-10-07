"""Predeclare persistent-residency research after the complete P1 gate."""
from lab import ROOT,load,save
base=ROOT/'experiments/E028-persistent-replay';assert not base.exists()
assert load(ROOT/'experiments/E027-pool-baseline/summary.json')['state']=='COMPLETE_FROZEN_BASELINE'
save(base/'protocol.json',{
 'phase':'P2-A','baseline':'p1-baseline, frozen CURRENT + STRATA_POOL_SPIN_US=100',
 'hypothesis':'Persistent residence can amortize promotion across future repeated demand; never immediate restore.',
 'signal':'Reuse E020 selected horizon8 exact existingGPUgate/top10 at5->13,12->20,25->33,32->40,38->46, same-device only. Confidence is normalized router weight, not calibrated future probability.',
 'new_signal_capture_reason':'OldE020 captures onlyfirst64windows and old pool scheduling. Full4K causal trajectory atP1 pool100 is needed to replay persistent lifetimes/traffic/victim damage. New diagnostic only, no headline speed.',
 'reader_safety_initial_design':'Issue from existing end-of-verify adaptive boundary after all expert readers finish. Async copy overlaps commit/draft; existing completion events gate publication before next-window maps. No host CUDA API call inside a spinning verify graph (upstream issue31). First current-window prediction demand has already occurred; explicitly charge this lateness and evaluate later reuse, never pretend8layerlead became a current-window copy deadline.',
 'placement':'Per-device fixed physical variable-size slots; fitting cross-layer victims allowed onlywithin ownerstage. Full immutableRAM arena stays canonical; clean eviction has noD2H restore. Pending slots reserved and notreused until completed/published.',
 'policy_candidates':'Small persistent utility variants: observedheat + horizon8 confidence/recurrence, byte-equivalent transfer penalty, age/recency victim guard and admission margin. Coarse choices fixed before fullbenchmark ranking; no Cartesian/dense sweep. Choose on preserveddevelopment/calibration signals then validate32/128 traces.',
 'cost_model':'Charge shared transferqueue and perdevice queues at measuredcontended1.8GB/s, with12.6GB/s isolated sensitivity and4.2us submission floor; score/host CPU cost explicit separately. No exactTG forecast.',
 'metrics':'Nonlocal demand, pending waits, bytes, useful/late/wasted admissions, repeated subsequent uses, victim reuse/miss damage, churn, physical slots/budget/owner invariants.',
 'live_funnel':'Separate source/build, defaultOFF. Correctness andOFFguard first.1–2screenings counted toward3maximum unchanged benchmark point; final32/128 up to3valid each. P1 original measured controls reused, not rerun beyond3. Same modified-binary OFF control is a separately identified newimplementation point for controlledON/OFF and binary-layout guard.',
 'scope':'No helper/v0138/predictor retraining/newmodel/crossGPU execution/global changes. Preserve failures and modified versions separately.',
 'deadline':'2026-10-05T19:03:00Z experimentcutoff;19:48 absolute stop'})
save(base/'signal-overrides.json',{'env':{'STRATA_POOL_SPIN_US':'100','STRATA_LAB_GPU_ROUTER':'1'},'extra_explicit_GPU_bytes_per_device':320,'mapped_CPU_bytes_per_device':1664,'diagnostic_only':True,'no_duplicate_gate_weights':True,'horizon':8,'full_window_signal_capture':True})
print('P2_PREDECLARED',flush=True)
