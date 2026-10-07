"""Declare one execution/coordination follow-up justified by measured host work."""
from lab import ROOT, save
out = ROOT / 'experiments/E016-device-plan-ids/v1'
if (out / 'protocol.json').exists():
    raise RuntimeError('Existing frozen protocol')
save(out / 'protocol.json', {
    'question': 'Does planning all-local groups on the GPU remove exposed host coordination without corrupting causal cache heat?',
    'evidence': 'E011 actual selected-layer empty plan spans8-9us, CPU-return4-5us floor; per-window source timings still include host plan/staging and all-resident barriers. Existing STRATA_VERIFY_DEVICE_PLAN is default-off and skips these waits for all-local groups.',
    'source_risk': 'The original mode still publishes into one shared h_ids row. Once GPU all-local groups skip host waits, the GPU can overwrite these IDs before the host visits an older layer. Actual expert math may remain correct at nonlocal barriers, but old-layer usage/diagnostic accounting can observe newer IDs. Do not treat that metadata as causal expert demand.',
    'changed_variables': 'Enable existing device-side resident plan plus local opt-in immutable-per-window routed ID snapshots per layer. Original host dispatch, true router, expert math, adaptation policy, capacities, K/PCIe/MTP/KV/workers remain frozen. No predictive routing or expert substitution.',
    'scope': 'Exactly frozen serial two-stage layer split, one group/window, no helper, no slot batching. Unsupported paths fail explicitly. No claim of a general upstream-ready implementation.',
    'budget': 'Official device-plan slot-offset array and64 skip bytes per GPU, plus per-stage mapped CPU ID array:25/23 layers *4 rows *10 IDs *4 bytes. Report actual bytes and VRAM. Preserve expert slot classes; new state must fit measured non-expert slack inside each24GiB envelope, otherwise reduce capacity/document practical comparison or stop.',
    'invariants': 'Each doorbell publishes into the current layer ID region before its sequence fence. GPU cannot overwrite that region within a window. Only truly nonlocal groups need the shared activation; their original host barriers prevent overwrite before CPU computation. No within-window adaptation; pending publications complete before the next window. Batch/group/helper modes rejected.',
    'funnel': 'Build/default-off upstream/native tests, direct kernel stable-ID overwrite reproducer and real IQ parity, saved10case greedy battery. Separate one-run/profile diagnostics must validate all true routed IDs/cache paths/usage and first-head parity before clean speed.',
    'batch_if_validated': 'Both profiles: fresh server, identical4096-input/64-output warmup, exactly3saved4096-output requests. Reuse E002 reference; no additional unchanged control repetitions. No background work during headline speed.',
    'completion': 'Preserve failure or both-profile confirmation; explain math/cache/trajectory parity, charged memory and actual latency. New candidate only, no production switch or historical numbers treated as fresh controls.'})
save(out / 'overrides.json', {'env': {'STRATA_VERIFY_DEVICE_PLAN': '1', 'STRATA_LAB_PLAN_IDS': '1'},
                             'policy': 'original EMA; device-planned all-local groups with stable per-layer IDs',
                             'scope': 'frozen serial two-stage one-group IQ3_S only'})
print(out)
