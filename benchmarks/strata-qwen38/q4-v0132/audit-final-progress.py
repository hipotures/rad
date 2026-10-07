from pathlib import Path
import json,importlib.util,time,statistics
from final_identity import final_label
r=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('final_audit',r/'completion-audit.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
label=final_label();cells=[]
for target in [31400,63400,127000,259500]:
 names=[f'{label}-ctx{target}-run{i}' for i in range(1,4)]
 if not all((r/'raw'/f'{n}.json').exists() for n in names):continue
 paths=m.fixed(names,target,256);rows=[json.loads(Path(p).read_text()) for p in paths]
 for row,name in zip(rows,names):
  cfg=row['full_config'];args=cfg['args'];assert cfg['gpu']==[0,1] and cfg['layer_split']=='24'
  assert args[args.index('--kv')+1]=='k8v4' and args[args.index('--max-context')+1]=='262144'
  assert cfg['benchmark_prompt_policy']=='offline-no-tools-system-v2'
  request=json.loads((r/'raw'/f'{name}-request.json').read_text())
  assert 'No tools are available. Answer directly using only the supplied repository excerpts.' in request['messages'][0]['content']
 cells.append({'target':target,'actual_prompt_tokens':[x['actual_prompt_tokens'] for x in rows],'n':3,'median_PP':statistics.median(x['pp_tps'] for x in rows),'median_TG':statistics.median(x['tg_tps'] for x in rows),'median_TTFT':statistics.median(x['ttft_s'] for x in rows),'raw':paths})
out={'status':'VERIFIED_COMPLETED_CELLS_ONLY','created':time.time(),'label':label,'cells':cells,'scope':'Completed n3 cells only. Original first attempt retained/excluded. Explicit system offline policy differs from historical speed prompts; not controlled old/new A/B. Pending cells are not completion proof.'}
(r/'evidence/final-matrix-progress-independent-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
