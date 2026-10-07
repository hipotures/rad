"""Record the finite selection rule before any E020 labeled analysis."""
from datetime import datetime,timezone
from lab import ROOT,load,save
out=ROOT/'experiments/E020-wide-gate-lookahead/v1'
assert not (out/'selection.json').exists() and not (out/'analysis').exists()
p=load(out/'protocol.json')
p['selection_rule_recorded_utc']=datetime.now(timezone.utc).isoformat()
p['selection_rule']='Choose horizon4or8 by pooled warm optimistic ready-tail recall at1.8GB/s on dev-code/dev-math/cal-prose only; tie fewer false nonresident proposals. Freeze before holds/benchmarks. No confidence threshold tuning; native top10 ordering. Then fixed rank-first vsEMA min2/gain1.5 queue/physical-slot feasibility, not a TGclaim.'
save(out/'protocol.json',p)
print(p['selection_rule'])
