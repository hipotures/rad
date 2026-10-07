"""Select from confirmed KV candidates and measure unique actual-context requests."""
import run as r,json,copy,math,statistics,time,importlib.util
assert json.loads((r.ROOT/'raw/phase-kv-terminal.json').read_text())['status']=='COMPLETE'
# Independent standalone raw/PSS/provenance audit runs before starting any final engine.
import subprocess,sys
subprocess.run([sys.executable,str(r.ROOT/'audit-kv-progress.py')],check=True)
selection=json.loads((r.ROOT/'raw/kv-selection.json').read_text());rank=[]
for kv in {x['kv'] for x in selection['confirmed']}:
 cells=[x for x in selection['confirmed'] if x['kv']==kv]
 assert len(cells)==2 and {x['target'] for x in cells}=={127000,259500}
 for cell in cells:
  assert cell['status']=='COMPLETE' and len(cell['runs'])==3
  for i in range(1,4):
   row=json.loads((r.ROOT/'raw'/f"{cell['candidate']}-run{i}.json").read_text())
   assert row['Strata_HEAD']==r.HEAD and row['Strata_version']=='0.1.32'
   assert abs(row['actual_prompt_tokens']-cell['target'])<=8 and row['actual_prompt_tokens']==row['actual_prompt_tokens_tokenizer']
   assert row['generated_tokens']==256 and row['cache_reused_tokens']==0 and not row['abort']
  assert statistics.median(x['tg_tps'] for x in cell['runs'])==cell['median_TG']
 rank.append({'kv':kv,'geometric_TG':math.prod(x['median_TG'] for x in cells)**.5,'geometric_PP':math.prod(x['median_PP'] for x in cells)**.5,'cells':cells})
rank.sort(key=lambda x:(x['geometric_TG'],x['geometric_PP']),reverse=True)
best=rank[0];source=r.ROOT/'configs'/f"{best['cells'][0]['candidate']}.json"
cfg=json.loads(source.read_text());cfg['args']=r.setarg(cfg['args'],'--max-context',262144)
cfg['log']=str(r.ROOT/'logs/FINAL-v0132-Q4-engine.log')
r.c.save(r.ROOT/'configs/FINAL-v0132-Q4.json',cfg)
r.c.save(r.ROOT/'raw/final-selection.json',{'status':'SELECTED_FROM_CONFIRMED_RESULTS','rank':rank,'config':str(r.ROOT/'configs/FINAL-v0132-Q4.json'),'classification':'ROTATED_INT8_OPT_IN' if best['kv']=='rotated-int8' else 'DEFAULT_RUNTIME_KV_OPTION','quality_status':'Pending exact saved payload parity; no quality ranking inferred from throughput','rule':'Confirmed geometric median TG across128/256K primary, PP secondary; legal full-arena only. Configuration remains explicitly tagged if rotated.'})
label='FINAL-v0132-Q4';done=r.ROOT/'raw/final-matrix-summary.json'
assert not done.exists() and not list((r.ROOT/'raw').glob(label+'-ctx*-request.json')),'Partial final matrix must be preserved/reviewed before retry'
s=json.loads((r.ROOT/'STATUS.json').read_text());s['running']={'phase':'final context matrix','candidate':label};s['current_winners']['final']={'config':str(r.ROOT/'configs/FINAL-v0132-Q4.json'),'kv':best['kv']};s['next_exact_action']='Complete actual31400/63400/127000/259500 n3, then longdecode/agentic/compaction.';(r.ROOT/'STATUS.json').write_text(json.dumps(s,indent=2))
rows=[];cells=[]
with r.Session(label,cfg) as session:
 smoke=session.request(8000,64,'smoke','smoke');assert smoke['text'].strip() and smoke['draft_tokens']>0
 for target in [31400,63400,127000,259500]:
  session.request(target,256,f'ctx{target}-warmup','warmup')
  cell=[]
  for i in range(1,4):
   row=session.request(target,256,f'ctx{target}-run{i}')
   assert abs(row['actual_prompt_tokens']-target)<=8 and row['actual_prompt_tokens']==row['actual_prompt_tokens_tokenizer']
   assert row['generated_tokens']==256 and row['cache_reused_tokens']==0 and not row['abort']
   rows.append(row);cell.append(row)
  cells.append({'target':target,'actual_prompt_tokens':statistics.median(x['actual_prompt_tokens'] for x in cell),'PP':statistics.median(x['pp_tps'] for x in cell),'TG':statistics.median(x['tg_tps'] for x in cell),'TTFT':statistics.median(x['ttft_s'] for x in cell),'runs':cell})
r.c.save(done,{'status':'COMPLETE','config':str(r.ROOT/'configs/FINAL-v0132-Q4.json'),'runs':rows,'cells':cells})
r.c.save(r.ROOT/'raw/phase-final-matrix-terminal.json',{'status':'COMPLETE','ended':time.time(),'measured_requests':12})
s=json.loads((r.ROOT/'STATUS.json').read_text());s['running']=None;s['completed'].append('Final context matrix actual32/64/128/256K n3 verified');s['pending']=[x for x in s['pending'] if not x.startswith('finalmatrix')];s['next_exact_action']='Longdecode, agentic64/128K, compaction128/250K, parity/needle/IQ3 controls, report.';(r.ROOT/'STATUS.json').write_text(json.dumps(s,indent=2))
spec=importlib.util.spec_from_file_location('status_render',r.ROOT/'status-render.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.render()
