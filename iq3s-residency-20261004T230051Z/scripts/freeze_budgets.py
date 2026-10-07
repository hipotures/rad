"""Reconcile independently traced slot classes with clean-control startup metrics."""
import json
from lab import ROOT,save
source=json.loads((ROOT/'analysis/control-budgets.json').read_text())
for profile,attempt in [('32k','v5'),('128k','v5-portfix')]:
 trace=json.loads((ROOT/'experiments/E003-diagnostics'/attempt/profile/'validation.json').read_text())['checks'][0]
 physical=trace['gpu_budgets'];startup=json.loads((ROOT/'experiments/E002-controls/v1'/profile/'raw/startup.json').read_text())['metrics']['engine']
 assert physical[0]['slots']==startup['expert_slots_primary']
 assert sum(g['slots'] for g in physical)==startup['expert_slots']
 assert physical[0]['bytes']>>20==startup['expert_cache_primary_mib']
 assert sum(g['bytes']>>20 for g in physical)==startup['expert_cache_mib']
 source[profile].update(exact_byte_classes=physical,diagnostic_provenance=trace['prefix'],effective_KV_resident=startup['kv_resident'],KV_note='32k reports0(full32768resident);128k reports32768resident with streaming. CLI unchanged32768 on both.')
target=ROOT/'analysis/control-budgets-v2.json'
if target.exists():raise RuntimeError('Refuse overwrite')
save(target,source);print(target)
