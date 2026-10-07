"""Update bounded branch dispositions after the attribution guard and wide replay."""
from lab import ROOT,load,save
p=ROOT/'candidate-ledger.json';a=load(p)
for f in a['families']:
    if f['id']=='F05':
        f.update(state='COMPLETE_BOUNDED_FEASIBILITY',next='Fresh CPU, low-rank CPU, native GPU and 4/8-layer GPU signals evaluated. Development-frozen horizon8 improves lead but charged temporary swaps have low benchmark tail coverage and substantial false-copy/restoration cost. No live router policy justified; persistent placement remains open.')
    if f['id']=='F06':
        f.update(state='COMPLETE_NEGATIVE_BOUNDED',next='Causal heat/Markov and learned hybrids evaluated. E018/E020 router plus EMA guard avoids churn but captures little ready tail. This closes these bounded variants, not all hybrid representations.')
    if f['id']=='F07':
        f.update(state='COMPLETE_MIXED_ATTRIBUTION_NOT_ESTABLISHED',next='Compatible placement, heap selector, safe device IDs and host-plan suppression tested. E014/E022 same-binary guards falsify broad isolated gains; PLE producer race repaired and actual parity established. E021 diagnoses coordination; E023 tests direct expert output rows. Cross-device expert scheduling remains unimplemented and must pay staging/activation/capacity costs.')
save(p,a)
with (ROOT/'DECISIONS.md').open('a') as f:
    f.write('\n## E016–E022 checkpoint\n\nSafe stable IDs also require the independent PLE producer dependency. The unsafe variant is retained only as a diagnostic reproducer; repaired full traces preserve actual routing and outputs. Safe device planning alone did not improve confirmed TG.\n\nThe E019 apparent 128K gain does not survive E022 same-binary OFF: 159.0 OFF versus 158.7 ON, identical outputs/MTP/capacities. The 32K ranges overlap. No production switch or further unchanged repetitions.\n\nE020 selected horizon8 from development/calibration before held-out labels. Queues, exact physical slots, victims and restoration materially reduce optimistic ready coverage. These temporary schemes do not justify a live cache-prediction build. Persistent placement and richer predictors are not claimed exhausted.\n\nUse E021 same-binary timing to explain coordination; E023 changes only redundant output-row storage/copying, with captured row-ownership tests and full correctness before clean speed.\n')
