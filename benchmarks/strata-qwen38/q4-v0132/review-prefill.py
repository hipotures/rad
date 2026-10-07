"""Evidence gate and balanced two-context policy selection, after completed measurements."""
import json,math,importlib.util
from pathlib import Path
R=Path(__file__).resolve().parent
assert json.loads((R/'raw/phase-prefill-terminal.json').read_text())['status']=='COMPLETE'
spec=importlib.util.spec_from_file_location('alloc',R/'prompt-allocation.py');alloc=importlib.util.module_from_spec(spec);spec.loader.exec_module(alloc)
d=json.loads((R/'raw/prefill-selection.json').read_text());groups={};evidence=[]
for result in d['confirmed']:
 assert result['status']=='COMPLETE' and len(result['runs'])==3
 cfg=json.loads((R/'configs'/f"{result['candidate']}.json").read_text());allocation=alloc.parse(cfg['log'],result['prefill_argument']);assert allocation['resolved_chunk_tokens'] is not None
 for i in range(1,4):
  row=json.loads((R/'raw'/f"{result['candidate']}-run{i}.json").read_text())
  assert row['Strata_HEAD']=='c499bd102e7a4135c0de389dcfe38c399759ccc8' and row['build_variant']=='default'
  assert row['generated_tokens']==256 and row['cache_reused_tokens']==0 and abs(row['actual_prompt_tokens']-result['target'])<=8
  assert row['actual_prompt_tokens']==row['actual_prompt_tokens_tokenizer'] and not row['abort']
 evidence.append(dict(candidate=result['candidate'],target=result['target'],**allocation))
 groups.setdefault(result['prefill_argument'],[]).append(result)
rank=[]
for arg,rows in groups.items():
 assert sorted(x['target'] for x in rows)==[127000,259500]
 rank.append({'argument':arg,'geometric_mean_PP':math.prod(x['median_PP'] for x in rows)**.5,'geometric_mean_TG':math.prod(x['median_TG'] for x in rows)**.5,'cells':[{k:x[k] for k in ['candidate','target','median_PP','median_TG']} for x in rows]})
rank.sort(key=lambda x:(x['geometric_mean_PP'],x['geometric_mean_TG']),reverse=True);best=rank[0];tie_note=None
# A larger configured chunk that upstream halves is the same allocation. Keep
# both measured results, but prefer its tested explicit size within a3% tie.
if best['argument'].isdigit():
 leader_evidence=[x for x in evidence if x['configured_prefill']==best['argument']]
 sizes={x['resolved_chunk_tokens'] for x in leader_evidence}
 if len(sizes)==1:
  actual=next(iter(sizes));canonical=next((x for x in rank if x['argument']==str(actual)),None)
  canonical_evidence=[x for x in evidence if x['configured_prefill']==str(actual)]
  if canonical and canonical['argument']!=best['argument'] and canonical['geometric_mean_PP']>=.97*best['geometric_mean_PP'] and len(canonical_evidence)==2 and all(x['resolved_chunk_tokens']==actual for x in canonical_evidence):
   tie_note={'ranked_PP_leader':best['argument'],'selected_explicit_size':canonical['argument'],'reason':'Both tested policies resolve to samechunk; confirmed PP within3%. Prefer explicit actualsize rather than relying on startup shrink.'};best=canonical
source=next(x for x in d['confirmed'] if x['prefill_argument']==best['argument'] and x['target']==127000)
policy={'status':'REVIEWED_FROM_RAW','selection_rule':'Geometric mean of confirmed median PP across actual127000/259500; TG secondary; default modes only. Equivalent actualchunk policies within3% use tested explicit actualsize. Explicit unchanged chunk interpreted with upstream no-reduction log contract.','equivalent_chunk_tie':tie_note,'config':str(R/'configs'/f"{source['candidate']}.json"),'argument':best['argument'],'rank':rank,'allocation_evidence':evidence}
(R/'raw/prefill-policy-reviewed.json').write_text(json.dumps(policy,indent=2));(R/'raw/prefill-allocation-evidence.json').write_text(json.dumps(evidence,indent=2))
s=json.loads((R/'STATUS.json').read_text());s['current_winners']['prefill']=policy;s['next_exact_action']='Run separate default/SPLIT_OWN/no-borrow A/B, then default adaptive/static control.';(R/'STATUS.json').write_text(json.dumps(s,indent=2))
print(json.dumps({'selected':best,'allocation':evidence},indent=2))

import importlib.util
_spec=importlib.util.spec_from_file_location('status_render',Path(__file__).resolve().parent/'status-render.py' if 'Path' in globals() else r.ROOT/'status-render.py');_module=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_module);_module.render()
