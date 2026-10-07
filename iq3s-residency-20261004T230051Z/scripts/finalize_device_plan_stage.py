"""Attach the actual correctness repair and bounded clean result to E016."""
from lab import ROOT, load, save
out = ROOT/'experiments/E016-device-plan-ids'
s = load(out/'summary.json')
s['state'] = 'COMPLETE_NEGATIVE'
s['decision'] = 'Do not select safe device planning alone: no meaningful request-latency or TG gain in this finite batch.'
s['correctness'] = {
    'unsafe_v1': 'Stable per-layer IDs alone did not preserve the independent PLE producer dependency. No unsafe clean headline requests were run.',
    'native_fixture': str(out/'compare-r2'),
    'snapshot_capture_failure': str(out/'compare-v1/analysis-audit.json'),
    'repaired_same_binary_snapshots': str(out/'compare-r2/summary.json'),
    'full_demand_parity': str(out/'diagnostic-v2/summary.json'),
    'tests': str(out/'v2/tests/failure-audit.json'),
    'short_battery': str(out/'v2/correctness/device-plan-ids-v2/ground-truth-checks.json')}
s['resources'] = {'extra_explicit_GPU_bytes': {'32k':[81984,67880], '128k':[81528,67560]},
                  'mapped_CPU_ID_bytes_per_stage':[4000,3680],
                  'expert_capacity_change':0,
                  'scope':'Frozen serial two-stage G1 only; helper, peer and batched paths rejected.'}
save(out/'summary.json', s)
with (out/'report.md').open('a') as f:
    f.write('''\n## Correctness finding and repair\n\nThe first local version was unsafe. Stable per-layer ID snapshots fixed host demand accounting, but the GPU all-local path bypassed the layer-0 CPU completion flag. Layer 1 could then read PLE values before their CPU producer finished. A delayed-producer native fixture reproduced the stale read on both GPUs. This is an execution dependency failure, not harmless floating-point reordering. No unsafe headline runs were collected.\n\nThe repaired version waits for the independent PLE producer before layer 1. The strict same-binary snapshot experiment reproduced the original numerical error at window 3/layer 1 (relative L2 activation difference 0.24145), and the fenced version matched every captured activation, expert output and head row bit for bit. The first snapshot attempt had a directory-creation bug; its vacuous parity claim is withdrawn and both attempts are retained.\n\nBoth full-profile repaired diagnostics matched all 4096 output IDs, speculative window inputs, routing IDs, execution paths, initial/final heat and resident sets. The first captured head was bit-identical with KL 0. The clean 10-prompt battery also matched control. The native suite retains the same four documented VM/fixture failures, not four new waived correctness errors.\n\nThe six clean measurements have identical visible output hashes, MTP acceptance and input IDs to control. Median TG is 152.3 versus 155.9 at 32K and 133.3 versus 133.2 at 128K. This does not justify selecting the candidate. The first measured request includes lazy graph-capture work under the identical 64-output warmup policy. No extra unchanged repetitions were run.\n\nAuxiliary GPU bytes are 81,984/67,880 at 32K and 81,528/67,560 at 128K, plus mapped CPU ID snapshots of 4,000/3,680 bytes. Exact expert capacities are unchanged. This experiment motivates separately testing removal of now-redundant host plan construction; it does not change the cache admission algorithm.\n''')
print(s['state'])
