"""Independent read-only validation of completed KV cells; no active-process reads."""
import json, statistics, time, re
from pathlib import Path
root=Path(__file__).resolve().parent
cells=[]
nonces=set()
for p in sorted((root/'raw').glob('KV-*-done.json')):
 d=json.loads(p.read_text())
 if d['status']!='COMPLETE':
  cells.append({'candidate':d['candidate'],'status':d['status'],'raw':str(p)});continue
 expected=3 if d['candidate'].endswith('-confirm') else 2
 assert len(d['runs'])==expected
 rows=[]
 for i in range(1,expected+1):
  raw=root/'raw'/f"{d['candidate']}-run{i}.json"
  x=json.loads(raw.read_text())
  assert x['status']=='OK' and not x['abort']
  request=json.loads(raw.with_name(raw.stem+'-request.json').read_text())
  assert request['temperature']==0 and request['max_tokens']==256
  assert request['model']=='qwen3.8-flash-next-ud-q4_k_xl' and request['reasoning_effort']=='none'
  nonce=re.search(r'\[bench run ([0-9a-f]{32})\]',request['messages'][0]['content'])
  assert nonce and nonce[1] not in nonces,'Missing or repeated request nonce'
  nonces.add(nonce[1])
  assert x['actual_prompt_tokens']==x['actual_prompt_tokens_tokenizer']
  assert abs(x['actual_prompt_tokens']-d['target'])<=8
  assert x['usage']['prompt_tokens']==x['actual_prompt_tokens']
  assert x['generated_tokens']==x['usage']['completion_tokens']==256
  assert x['cache_reused_tokens']==0
  assert x['Strata_HEAD']=='c499bd102e7a4135c0de389dcfe38c399759ccc8'
  assert x['Strata_version']=='0.1.32' and x['build_variant']=='default'
  assert x['model_revision']=='38bb39ee97821de2c9009abb7e93950eec396e66'
  cfg=x['full_config'];args=cfg['args']
  def arg(k):return args[args.index(k)+1]
  assert cfg['gpu']==[0,1] and str(cfg['layer_split'])=='24'
  command=x['full_engine_command']
  assert command[0]==cfg['exe'] and command[1]=='--serve'
  assert command[2:]==args+['--layer-split','24']
  assert arg('--max-context')=='262144' and arg('--spec')=='3'
  assert arg('--pool-workers')=='12' and arg('--pcie-frac')=='0.28'
  assert arg('--prefill')=='16384' and arg('--spec-min-p')=='0.3'
  assert arg('--kv')==('int8' if d['kv']=='rotated-int8' else d['kv'])
  assert not any(k in args for k in ['--resident-budget-gib','--resident-cpu-experts','--kv-resident'])
  env=cfg['effective_experiment_environment']
  assert env['STRATA_KV_ROT']==('1' if d['kv']=='rotated-int8' else None)
  assert all(env[k] is None for k in ['STRATA_SPLIT_OWN','STRATA_REFILL_SERIAL','STRATA_SPEC_COUPLED'])
  samples=[json.loads(line) for line in Path(x['telemetry_file']).read_text().splitlines()]
  assert samples and min(t['mem_available_gib'] for t in samples)>12
  timestamps={}
  for t in samples:
   for proc in t['processes']:
    if proc.get('pss_sample_wall') is not None:
     timestamps.setdefault(proc['pid'],set()).add(proc['pss_sample_wall'])
  assert all(len(v)==1 for v in timestamps.values()),'PSS refreshed inside timed request'
  for pid,stamps in timestamps.items():
   assert stamps=={x['pss_before'][str(pid)]['pss_sample_wall']},'Telemetry PSS not from before-request snapshot'
  wall_start=samples[0]['wall_time']-(samples[0]['monotonic']-x['t_start_monotonic_s'])
  wall_end=wall_start+x['total_wall_s']
  assert all(z['pss_sample_wall']<wall_start for z in x['pss_before'].values())
  assert all(z['pss_sample_wall']>=wall_end for z in x['pss_after'].values())
  assert all(any(g['index']==j for g in t['gpus']) for t in samples for j in [0,1])
  for k in ['pp_tps','tg_tps','actual_prompt_tokens','generated_tokens']:
   assert x[k]==d['runs'][i-1][k]
  rows.append({'raw':str(raw),'actual':x['actual_prompt_tokens'],'output':x['generated_tokens'],
   'PP':x['pp_tps'],'TG':x['tg_tps'],'TTFT':x['ttft_s'],
   'decode_expert_file_blobs':x['expert_tiers']['file_blobs'],
   'decode_expert_file_MB':x['expert_tiers']['file_mb'],
   'min_MemAvailable_GiB':x['min_mem_available_gib'],'telemetry_samples':len(samples)})
 assert statistics.median(x['PP'] for x in rows)==d['median_PP']
 assert statistics.median(x['TG'] for x in rows)==d['median_TG']
 cells.append({'candidate':d['candidate'],'kv':d['kv'],'status':'VERIFIED','n':expected,
  'median_PP':d['median_PP'],'median_TG':d['median_TG'],'rows':rows})
result={'status':'PARTIAL_INDEPENDENT_AUDIT','created':time.time(),'cells':cells,
 'scope':'Completed raw cells only; running/pending formats and final selection not claimed complete.',
 'io_scope':'Normal decode file-fetch counters only; not proof of physical host SSD I/O through virtiofs.'}
out=root/'evidence/kv-progress-independent-audit.json'
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'audited_cells':len(cells),'measured_requests':sum(c.get('n',0) for c in cells),'evidence':str(out)}))
