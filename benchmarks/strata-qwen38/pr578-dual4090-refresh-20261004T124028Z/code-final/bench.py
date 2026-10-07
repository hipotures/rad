import run as r,workloads as w,json,copy,subprocess,re,hashlib,time,statistics,traceback,sys,os
from pathlib import Path
R=r.ROOT
SEED=json.loads((R/'configs/resident-baseline-seed.json').read_text())
OLD=json.loads((Path('/srv/ai/benchmarks/strata-qwen38/iq3s-v0138-replay-v0131-32k/configs/IQ3S-replay32.json')).read_text())
def save(p,d):r.c.save(p,d)
def status(action,completed=None):
 s=json.loads((R/'STATUS.json').read_text());s['running']=None if completed else action;s['next_exact_action']=action;s['status']='PHASE_COMPLETE' if completed else 'RUNNING'
 if completed:s['completed']=list(dict.fromkeys(s['completed']+completed))
 aliases={'Cache progression diagnostics':'cache progression diagnostics','Secondary lookup ON':'secondary lookup ON','Steady decode':'steady decode','Finalists context matrix':'final context matrix','Fresh-server confirmation if top two within 5%':'fresh-server confirmations or documented >5% gap'}
 s['pending']=[x for x in s.get('pending',[]) if aliases.get(x) not in s.get('completed',[])]
 if (R/'selection.json').exists():s['current_winners']=json.loads((R/'selection.json').read_text())
 save(R/'STATUS.json',s)
 import importlib.util
 spec=importlib.util.spec_from_file_location('status_render',R/'status-render.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.render()
def cfg(label,variant='control',top='split',suffix=False,primary='auto',helper='auto',opt=False,pcie=None,instrument=False,original=False):
 c=copy.deepcopy(OLD);repo=Path('/srv/ai/strata-pr578-refresh-20261004-'+variant)
 c.update(parallel=1,cwd=str(repo),exe=str(repo/'build-default'/('strata-original' if original else 'strata')),log=str(R/'logs'/f'{label}-engine.log'),Strata_HEAD=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip(),build_variant=variant+('-original' if original else '-clean-upstream'),upstream_base='6f32ec070f23ced9f50e704d854d775da52591ab',PR_head='b28121ff6ef117bec2558b3ece7e188dd33a2b7e',extra_env={'STRATA_BENCH_CACHE_SNAPSHOT':'1'} if instrument else {})
 c['args']=r.setarg(c['args'],'--suffix-draft',3 if suffix else 0)
 c['args']=r.setarg(c['args'],'--pool-workers',15)
 c['args']=r.setarg(c['args'],'--expert-cache',primary)
 if pcie is not None:c['args']=r.setarg(c['args'],'--pcie-frac',pcie)
 if top=='helper':
  c.pop('layer_split',None);c['args']=r.setarg(c['args'],'--expert-cache-device1',helper)
  if opt:c['args']+=['--remote-expert-opt']
 c['gpu']=[0,1] if top=='split' else 0
 c['env']['CUDA_VISIBLE_DEVICES']='0,1'
 if original:c['Strata_HEAD']=c['upstream_base']
 c['binary_sha256']=hashlib.sha256(Path(c['exe']).read_bytes()).hexdigest()
 save(R/'configs'/f'{label}.json',c);return c

def snapshots(log):return [json.loads(x) for x in re.findall(r'STRATA_BENCH_CACHE (\{[^\n]+\})',log)]
def startup(s):
 text=Path(s.cfg['log']).read_text();snaps=snapshots(text);snapshot=next((x for x in snaps if x['phase']=='startup'),None)
 p=re.search(r'expert cache (\d+) slots,',text);h=re.search(r'CUDA1: (\d+) additional experts',text)
 auto=re.search(r'expert cache auto:.*?-> (\d+) slots',text)
 budget=int(auto[1]) if auto else int(s.cfg['args'][s.cfg['args'].index('--expert-cache')+1]) if '--expert-cache' in s.cfg['args'] and s.cfg['args'][s.cfg['args'].index('--expert-cache')+1]!='auto' else None
 result={'primary':snapshot['primary_capacity'] if snapshot else int(p[1]) if p else None,'primary_cli_uniform_budget':budget,'helper':snapshot['helper_capacity'] if snapshot else int(h[1]) if h else 0,'snapshot':snapshot,'layer_split_K':int(re.search(r'auto: K=(\d+)',text)[1]) if re.search(r'auto: K=(\d+)',text) else int(s.cfg['layer_split']) if s.cfg.get('layer_split','auto')!='auto' else None,'text_path':s.cfg['log'],'primary_pcie_probe_fraction_reported':float(re.search(r'-> pcie_frac ([\d.]+)',text)[1]) if re.search(r'-> pcie_frac ([\d.]+)',text) else None,'stage_pcie_probe_fractions_reported':{m[0]:float(m[1]) for m in re.findall(r'CUDA(\d+) PCIe probe .*?-> pcie_frac ([\d.]+)',text)},'layer_slots_per_GPU':{m[0]:int(m[1]) for m in re.findall(r'layer split: CUDA(\d+) runs layers .*?expert cache (\d+) slots',text)}}
 if result['primary'] is not None:result['layer_slots_per_GPU'].setdefault('0',result['primary'])
 if snapshot:
  result['initial_resident_expert_count']=snapshot['primary_resident']+snapshot['helper_resident'];result['initial_overlap']=snapshot['overlap']
  for side in ['primary','helper']:result['initial_'+side+'_ids_SHA256']=hashlib.sha256(json.dumps(snapshot[side+'_ids'],separators=(',',':')).encode()).hexdigest()
 if not snapshot and s.cfg.get('required_initial_layout') and s.cfg.get('headline_instrumentation')=='OFF':
  expected=s.cfg['required_initial_layout'];policy=json.loads((R/'headline-instrumentation-policy.json').read_text())
  profile=Path(s.cfg['args'][s.cfg['args'].index('--expert-profile')+1]);assert hashlib.sha256(profile.read_bytes()).hexdigest()==policy['profile_SHA256']
  assert result['primary']==expected['primary'] and result['helper']==expected['helper'] and result['primary_cli_uniform_budget']==expected['primary_cli_uniform_budget']
  assert Path(s.cfg['exe']).name=='strata-original' and s.cfg['Strata_HEAD']==r.FROZEN_MAIN
  result.update(initial_resident_expert_count=result['primary']+result['helper'],initial_overlap=0,initial_sets_directly_observed=False,initial_layout_basis='CAPACITIES_LOGGED; COUNT_AND_OVERLAP_FROM_DETERMINISTIC_CONSTRUCTION_VERIFIED_SEPARATELY',diagnostic_initial_layout_reference=str(R/'auto-capacities.json'),profile_SHA256=policy['profile_SHA256'])
 return result

def request(s,p,tag,kind='measured',must256=True):
 status(s.label+' '+tag+' '+kind)  # checkpoint before the timing-critical request
 apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
 for row in apps.splitlines():
  if row.strip():assert os.getpgid(int(row.split(',')[0]))==s.proc.pid,'Foreign CUDA process at request boundary; no request sent'
 ids=s.run.encode_messages(p['messages'])
 encoded_ids=json.dumps(ids,separators=(',',':'))
 replay_key=hashlib.sha256(json.dumps(p['messages'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 provenance=R/'api-tokenization-provenance.json'
 expected=json.loads((provenance if provenance.exists() else R/'replay-provenance.json').read_text()).get(replay_key)
 if expected:
  assert hashlib.sha256(encoded_ids.encode()).hexdigest()==expected['input_ids_sha256'],'Saved replay input token IDs changed; stop before timed request'
  assert len(ids)==expected['actual_prompt_tokens']
 a=w.request(s,p['messages'],p['max_tokens'],tag,kind=kind,exact_payload=p)
 a['replay_reference']=expected
 a['input_ids_sha256']=hashlib.sha256(encoded_ids.encode()).hexdigest()
 idpath=R/'token-ids'/(a['input_ids_sha256']+'.json');idpath.parent.mkdir(exist_ok=True)
 if not idpath.exists():idpath.write_text(encoded_ids)
 a['input_token_ids_path']=str(idpath)
 a['output_text_sha256']=hashlib.sha256(a['text'].encode()).hexdigest()
 log=(R/'raw'/f'{s.label}-{tag}-engine.log').read_text();a['cache_snapshots']=snapshots(log)
 counter_matches=re.findall(r'STRATA_BENCH_COUNTERS (\{[^\n]+\})',log)
 a['boundary_counters']=json.loads(counter_matches[-1]) if counter_matches else None
 a['non_finite_head_diagnostic']=bool(re.search(r'logits non-finite',log))
 a['actual_token_ids_match_api_count']=(a['actual_prompt_tokens']==len(ids))
 postapps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
 foreign=[]
 for row in postapps.splitlines():
  if not row.strip():continue
  try:owned=os.getpgid(int(row.split(',')[0]))==s.proc.pid
  except ProcessLookupError:owned=False
  if not owned:foreign.append(row)
 a['CUDA_apps_at_request_end']=postapps
 a['foreign_CUDA_processes_at_request_end']=foreign
 a['valid']=a['actual_prompt_tokens']==s.run.count(p['messages']) and a['status']=='OK' and a['cache_reused_tokens']==0 and (not must256 or a['generated_tokens']==p['max_tokens']) and not a['abort'] and not foreign and not a['non_finite_head_diagnostic']
 a['exclusion']=None if a['valid'] else 'CONTAMINATED_FOREIGN_CUDA' if foreign else 'INVALID_EOS_OR_REQUEST'
 save(R/'raw'/f'{s.label}-{tag}.json',a)
 if not a['valid']:print('INVALID preserved',s.label,tag,flush=True)
 return a

def oldpayload(i,context='32K'):
 p=json.loads((R/'references'/f'IQ3_S-{context}-{i}-request.json').read_text());return p
warm=json.loads((R/'references/IQ3_S-warmup-request.json').read_text())
warm['max_tokens']=64  # equal generated warmup work for helper A/B


PROMPTS=[('math','Compute 37*48. Show a short calculation and the final result.'),('math','Solve 3x+7=31. Give x and verify it.'),('math','A fair six-sided die is rolled twice. What is the probability that the sum is 7? Explain briefly.'),('code','Fix this Python function and provide two tests:\ndef sum_even(xs):\n    return sum(x for x in xs if x % 2)\nThe function must sum even numbers.'),('code','Explain why this Python code changes both rows and fix it:\na=[[0]*3]*2\na[0][0]=1'),('code','Write a Python function binary_search(a,x) returning the index or -1. Include tests for an empty list and missing item.'),('prose','Explain in five sentences why seasons occur on Earth.'),('prose','Write a short professional email asking to reschedule a meeting from Monday to Wednesday.'),('structured','Return ONLY valid JSON with exactly these keys: name, count, enabled. Values: "test", 3, true.'),('structured','Return ONLY valid JSON: an array of three objects with integer keys "id" and "square", for IDs 1,2,3.')]
def battery(label,c):
 # Protocol tee is correctness-only; never used for any speed result.
 wrap=R/'correctness'/f'{label}-engine.sh';trace=R/'correctness'/f'{label}-protocol.txt'
 wrap.write_text('#!/bin/bash\nset -o pipefail\n'+c['exe']+' "$@" | tee '+str(trace)+'\n');wrap.chmod(0o755)
 c=copy.deepcopy(c);c['extra_env']['STRATA_DBG_NAN']='1';c['exe']=str(wrap)
 c['binary_sha256']=hashlib.sha256(wrap.read_bytes()).hexdigest()
 rows=[]
 with r.Session(label,c) as s:
  st=startup(s);save(R/'correctness'/f'{label}-startup.json',st)
  if c.get('required_initial_layout'):
   keys=['primary','helper','initial_resident_expert_count','initial_overlap','initial_primary_ids_SHA256','initial_helper_ids_SHA256']
   if st.get('initial_sets_directly_observed') is False:keys=keys[:4]
   assert all(st.get(k) is not None and st[k]==c['required_initial_layout'].get(k) for k in keys),'Correctness helper initial cache mismatch before requests'
  for i,(category,text) in enumerate(PROMPTS):
   status('correctness '+label+f' prompt{i+1}/10')
   p={'model':c['model_name'],'messages':[{'role':'system','content':f'[correctness case {i}] Answer directly. No tools are available.'},{'role':'user','content':text}],'max_tokens':256,'stream':True,'stream_options':{'include_usage':True},'temperature':0,'reasoning_effort':'none'}
   a=request(s,p,f'case{i+1}',kind='correctness',must256=False);a['category']=category
   rows.append(a)
 lines=trace.read_text().splitlines();chunks=[];cur=[]
 for line in lines:
  if line.startswith('T '):cur.append(int(line.split()[1]))
  if line.startswith('DONE '):chunks.append(cur);cur=[]
 assert len(chunks)==10,(label,len(chunks))
 for i,a in enumerate(rows):a['generated_token_ids']=chunks[i];save(R/'correctness'/f'{label}-case{i+1}.json',a)
 save(R/'correctness'/f'{label}-all.json',rows)
 return rows

def sweep(label,c,contexts=('32K',),replicate=0):
 done=R/'raw'/f'{label}-done.json'
 if done.exists():return json.loads(done.read_text())
 if any(list((R/'raw').glob(label+'-'+context+'-run[123].json')) for context in contexts):raise RuntimeError('Partial candidate already has raw requests; preserve them and review a separately named retry rather than overwrite')
 status(label+' startup/warmup')
 rows=[]
 with r.Session(label,c) as s:
  st=startup(s);save(R/'raw'/f'{label}-layout.json',st)
  if c.get('required_initial_layout'):
   required=c['required_initial_layout']
   keys=['primary','helper','initial_resident_expert_count','initial_overlap','initial_primary_ids_SHA256','initial_helper_ids_SHA256']
   if st.get('initial_sets_directly_observed') is False:keys=keys[:4]
   mismatch={k:[required.get(k),st.get(k)] for k in keys if required.get(k) is None or required.get(k)!=st.get(k)}
   save(R/'raw'/f'{label}-startup-fairness.json',{'status':'FAIL' if mismatch else 'PASS','mismatch':mismatch,'expected':required,'actual':st})
   if mismatch:raise RuntimeError('Initial helper cache fairness failure; stop before warmup: '+str(mismatch))
  for context in contexts:
   # All context warmups use exact old 4096 payload, except when followed by a previously run context.
   wp=copy.deepcopy(warm)
   if c.get('warmup_output_tokens'):wp['max_tokens']=c['warmup_output_tokens']
   if len(contexts)>1 or c.get('force_matrix_warmup_prefix'):wp['messages'][0]['content']='[PR578 matrix warmup '+context+'] '+wp['messages'][0]['content']
   wa=request(s,wp,f'{context}-warmup',kind='warmup')
   if not wa['valid']:raise RuntimeError('Warmup did not complete identical 64-token work; no measured request sent')
   for i in [1,2,3]:
    status(label+' '+context+f' measured{i}/3')
    a=request(s,oldpayload(i,context),f'{context}-run{i}');a.update(context_label=context,initial_layout=st,suffix_lookup=('ON' if '--suffix-draft' not in c['args'] or c['args'][c['args'].index('--suffix-draft')+1]!='0' else 'OFF'));save(R/'raw'/f'{label}-{context}-run{i}.json',a);rows.append(a)
 save(done,{'label':label,'layout':st,'runs':rows});return {'label':label,'layout':st,'runs':rows}

if __name__=='__main__':
 phase=sys.argv[1]
 try:
  if phase=='pilot':
   # Untouched PR binary is preserved and tested before using local diagnostic commit.
   label='PR-original-auto-pilot';c=cfg(label,'optimized','helper',opt=True,instrument=False,original=True)
   with r.Session(label,c) as s:
    st=startup(s);save(R/'auto-capacities.json',st)
    request(s,warm,'warmup',kind='warmup');request(s,oldpayload(1),'replay32',kind='pilot')
  elif phase=='correctness':
   st=json.loads((R/'auto-capacities.json').read_text())
   a=battery('CORRECT-H-OLD',cfg('CORRECT-H-OLD','control','helper',primary=st['primary_cli_uniform_budget'],helper=st['helper']))
   b=battery('CORRECT-H-OPT',cfg('CORRECT-H-OPT','optimized','helper',primary=st['primary_cli_uniform_budget'],helper=st['helper'],opt=True))
   results=[]
   for i,(x,y) in enumerate(zip(a,b)):
    idsx=x['generated_token_ids'];idsy=y['generated_token_ids'];n=min(len(idsx),len(idsy));div=next((j for j in range(n) if idsx[j]!=idsy[j]),n if len(idsx)!=len(idsy) else None)
    text=y['text'];bad='\ufffd' in text or not text.strip() or bool(re.search(r'(?i)\b(?:nan|infinity)\b',text))
    structured=None
    if i>=8:
     try:structured=json.loads(text)
     except:bad=True
    results.append({'case':i+1,'category':x['category'],'input_identical':x['input_ids_sha256']==y['input_ids_sha256'],'first_diverging_token':div,'equal_position_tokens':sum(idsx[j]==idsy[j] for j in range(n)),'positions_compared':n,'teacher_forced_top1_agreement':None,'malformed_output':bad,'structured':structured,'control_finish':x['finish_reasons'],'pr_finish':y['finish_reasons']})
   save(R/'correctness/summary.json',results)
   if any(z['malformed_output'] or not z['input_identical'] for z in results):raise RuntimeError('Correctness battery flagged malformed output; inspect before speed')
   status('correctness complete; prepare32K sweep',['10 paired correctness cases'])
  elif phase=='sweep32':
   st=json.loads((R/'auto-capacities.json').read_text());p,h=st['primary_cli_uniform_budget'],st['helper']
   configs=[('LS-A',cfg('LS-A',instrument=False)),('LS-B',cfg('LS-B',pcie=.28,instrument=False)),('PR-LS',cfg('PR-LS','optimized',instrument=False)),('H-OLD',cfg('H-OLD','control','helper',primary=p,helper=h,instrument=False)),('H-OPT',cfg('H-OPT','optimized','helper',opt=True,instrument=False)),('H-OPT-FIXED',cfg('H-OPT-FIXED','optimized','helper',primary=p,helper=h,opt=True,instrument=False))]
   for label,c in configs:sweep(label,c)
   status('32K primary sweep complete; inspect finalists',['primary32K sweep'])
  else:raise ValueError(phase)
 except BaseException:
  (R/'logs'/f'{phase}-exception.txt').write_text(traceback.format_exc());raise
