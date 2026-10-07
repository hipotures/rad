"""Freeze one availability repair and two separated-rank predictor experiments."""
from lab import ROOT,save
out=ROOT/'experiments/E015-lowrank-router/v1'
if (out/'protocol.json').exists():raise RuntimeError('Protocol already frozen')
save(out/'protocol.json',{
    'question':'With actually fresh current-layer activations, can rank32/rank128 next-gate CPU projections arrive early enough and recall useful nonresidents?',
    'source_problem':'Frozen verify.cpp uses doorbell_publish_res; elementwise.cu308-326 copies x_out only when any expert in the group is nonresident. E008signals.activation unconditionally sampled h_x, so all-local groups may contain stale prior activations. Previous timing/outputs remain valid; prediction quality/readiness requires freshness separation.',
    'repair':'Diagnostic-only selected6currentlayer activation snapshots force x publication by passing null to the doorbell residency-check pointer. Does not change actualGPUexpertcache/routerIDs/weights, CPUclassification or math. Extra selected-layer mapped activation traffic explicitly charged; not a headline binary.',
    'ranks':[32,128],
    'predictor':'Truncated SVD/left eigenspace of the existing next-layer BF16gate converted exactly to float32; auxiliary CPU projection matrices. Original model weights untouched and actual router always chooses true experts. No releasedJevbackbone or extra downloadedmodel.',
    'splits':'Same6savedindependenttasks:2dev,1calibration,3holdout; first64windows/6layerpairs. Decomposition uses existing gateweights only, rank selection based on dev/calibration, heldout not tuned. Complete bothprofile frozenrun1diagnostics if useful for lead comparisons; no64k/256k.',
    'budget':'Rank32 perlayer(2560+512)*32*4=393216CPUbytes;rank128=1572864CPUbytes. Capture max64windows,6pairs,<=4rows each. No explicit newGPUbuffers; old4CUDAevents/device for actual handoff only.',
    'batch':'After E013/E014clean speed has finished, build/testfreshdiagnostic then one bounded6episodecollection. Keep same64warmup. No concurrent timing/training/build with headline runs.',
    'measure':'Top10precision, true-nonlocal recall, false-positive currentnonresident proposals, causal availability/hostlead. Single-thread numeric score+top10 time, memory, oneblob readiness optimistic12.6GB/s and measured contended1.8GB/s. No cost-freeTGprojection.',
    'caveats':'Fresh activation copying extends measured lead; productionCPUhas no fresh x for all-local groups without paying this transfer. GPUlookahead avoids this copy but is a separate unimplemented path. CPU scoring delays currentCPUexpertwork if done on its calling thread. Missing those costs is not a ready runtime policy.',
    'completion':'Bounded decomposition/timing/independentholdoutevaluation, bothranks preserved and explicit decision whetherruntime integration is justified. Oldstaleinputresults retained/labeled, no rewrites of original raw data.'})
save(out/'overrides.json',{'env':{'STRATA_LAB_SIGNAL':'1'},'diagnostic_only':True,'question':'Fresh selected-layer activation gate prediction; correct the observed stale-host-input instrumentation flaw.'})
(out/'source-audit.md').write_text('''# Activation availability audit

Frozen base6f32ec0: src/core/verify.cpp953-960 passes per-layer device residency to doorbell_publish_res. src/kernels/cuda/elementwise.cu308-326 publishes expert IDs always, but copies the activation rows only if __syncthreads_or(any_miss) is true. Consequently h_x is not a current-layer numeric signal for all-local groups, although IDs and the inference result remain correct. E008 patch sampled h_x unconditionally before any_cpu check. Its router-quality/readiness aggregates mixed fresh and potentially stale groups; they must not be treated as a reliable full-CPU-gate deployment verdict.

Repair changes only a diagnostic doorbell argument for the six selected current layers while STRATA_LAB_SIGNAL is enabled. A null residency pointer forces the existing activation copy, without changing actual expert placement, routing or the host classifier. Quantization/expert computations stay original. Raw old outputs and real boundary CUDA events remain valid. Extra copies and CPU snapshot costs perturb timings; no headline TG claim or production CPU availability guarantee.
''')
print(out)
