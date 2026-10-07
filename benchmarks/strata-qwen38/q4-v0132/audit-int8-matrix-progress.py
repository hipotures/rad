"""Independently validate complete n3 INT8 cells while preserving K8V4 audit."""
import json,time,statistics,importlib.util
from pathlib import Path
R=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('audit',R/'completion-audit.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
label='FINAL-v0132-Q4-INT8-stability';cells=[]
for target in [31400,63400,127000,259500]:
    names=[f'{label}-ctx{target}-run{i}' for i in range(1,4)]
    paths=[R/'raw'/f'{name}.json' for name in names]
    if not all(p.exists() for p in paths):continue
    rows=[json.loads(p.read_text()) for p in paths]
    if not all(row.get('pss_note') for row in rows):continue
    audit.fixed(names,target,256)
    for row,name in zip(rows,names):
        cfg=row['full_config'];args=cfg['args']
        assert cfg['gpu']==[0,1] and cfg['layer_split']=='24'
        assert args[args.index('--kv')+1]=='int8' and args[args.index('--max-context')+1]=='262144'
        assert cfg['benchmark_prompt_policy']=='offline-no-tools-system-v2'
        payload=json.loads((R/'raw'/f'{name}-request.json').read_text())
        assert 'No tools are available. Answer directly using only the supplied repository excerpts.' in payload['messages'][0]['content']
    cells.append({'target':target,'n':3,'actual_prompt_tokens':[x['actual_prompt_tokens'] for x in rows],'median_PP':statistics.median(x['pp_tps'] for x in rows),'median_TG':statistics.median(x['tg_tps'] for x in rows),'median_TTFT':statistics.median(x['ttft_s'] for x in rows),'raw':[str(p) for p in paths]})
result={'status':'VERIFIED_COMPLETED_INT8_CELLS_ONLY','created':time.time(),'label':label,'cells':cells,'measured_requests_verified':sum(x['n'] for x in cells),'required_requests':12,'scope':'Independent raw/API/tokenizer/output/greedy/no-reuse/identity/config/RAM/PSS checks. Separate INT8 candidate; prior K8V4 results unchanged. Production promotion not implied.'}
(R/'evidence/int8-final-matrix-progress-independent-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
