from pathlib import Path
import json,subprocess,hashlib,collections,re
R=Path(__file__).resolve().parent
issues=[];checked=[];negative=[];groups=collections.defaultdict(list)
for p in sorted(R.glob('raw/*-run[123].json')):
 a=json.loads(p.read_text())
 if not a.get('candidate'):continue
 for k in ['Strata_HEAD','Strata_version','build_variant','model_revision','full_config','full_engine_command','input_ids_sha256']:
  if k not in a:issues.append((str(p),'missing '+k))
 assert a['model_revision']=='ed59f92082b1e93c0e96d60a8b11aab089b52f09'
 cfg=a['full_config'];args=cfg['args']
 for flag,expected in [('--spec','4'),('--spec-min-p','0.5'),('--kv','int8'),('--kv-resident','32768'),('--max-context','262144'),('--pool-workers','15')]:
  assert args[args.index(flag)+1]==expected,(p,flag)
 assert a['cache_reused_tokens']==0,(p,'reuse')
 if args[args.index('--suffix-draft')+1]=='0':
  log=p.with_name(p.stem+'-engine.log').read_text();assert not re.search(r'suffix drafts: [1-9]',log),(p,'suffix was enabled')
 request=json.loads(p.with_name(p.stem+'-request.json').read_text())
 if a['valid']:assert a['generated_tokens']==request['max_tokens'] and a['finish_reasons']==['length'],p
 if not a['valid']:negative.append({'path':str(p),'generated':a['generated_tokens'],'finish':a['finish_reasons'],'tools':len(a.get('tool_call_events',[])),'exclusion':a.get('exclusion')})
 if a.get('input_token_ids_path'):
  ip=Path(a['input_token_ids_path']);assert hashlib.sha256(ip.read_bytes()).hexdigest()==a['input_ids_sha256'];assert len(json.loads(ip.read_text()))==a['actual_prompt_tokens']
 # For literal old replay, exactpayload must match source; steady sharedprompt is a differentworkload.
 m=re.search(r'-(32K|64K|128K|256K)-run([123])$',p.stem)
 if m:
  source=json.loads((R/'references'/f'IQ3_S-{m[1]}-{m[2]}-request.json').read_text());assert request==source,p
  groups[(m[1],m[2])].append((p,a['input_ids_sha256']))
 checked.append(str(p))
steady=[]
for p in R.glob('raw/*STEADY2048-steady-run[123].json'):
 a=json.loads(p.read_text());payload=json.loads(p.with_name(p.stem+'-request.json').read_text());assert payload==json.loads((R/'references/steady2048-request.json').read_text());steady.append(a['input_ids_sha256'])
assert len(set(steady))==1
for p in R.glob('raw/*STEADY2048-done.json'):
 a=json.loads(p.read_text());lay=a['layout']
 if lay.get('helper'):assert lay['primary']==8586 and lay['helper']==11796
 warm=json.loads((R/'raw'/(a['label']+'-steady-warmup.json')).read_text());assert warm['generated_tokens']==64 and warm['cache_reused_tokens']==0
for key,items in groups.items():assert len(set(x[1] for x in items))==1,(key,'inputIDs acrossconfigs differ')
models=json.loads((R/'git/model-files-before.json').read_text())
for m in models:
 p=Path(m['path']);st=p.stat();assert st.st_size==m['size'] and st.st_mtime_ns==m['mtime_ns'],p
for v in ['control','optimized','helper-priority']:
 repo=Path('/srv/ai/strata-pr578-'+v);assert not subprocess.check_output(['git','-C',str(repo),'status','--porcelain'],text=True)
# Initialcachefairness from identical diagnostic snapshots.
a=json.loads((R/'raw/H-OLD-DIAG-layout.json').read_text())['snapshot'];b=json.loads((R/'raw/H-OPT-DIAG-layout.json').read_text())['snapshot']
assert a['primary_capacity']==b['primary_capacity']==8586 and a['helper_capacity']==b['helper_capacity']==11796
assert a['primary_ids']==b['primary_ids'] and a['helper_ids']==b['helper_ids'] and a['overlap']==b['overlap']==0
for p in R.glob('raw/*-layout.json'):
 d=json.loads(p.read_text())
 if d.get('helper') and 'H-OPT-LOOKUP-ON-layout' not in p.name:
  assert d['primary']==8586 and d['helper']==11796,(p,d['primary'],d['helper'])
fair={'primary_slots':8586,'helper_slots':11796,'initial_resident_count':20382,'initial_overlap':0,'identical_primary_ids':True,'identical_helper_ids':True}
(R/'fairness-audit.json').write_text(json.dumps(fair,indent=2))
apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'],text=True)
result={'checked_raw_requests':len(checked),'issues':issues,'negative_measured_runs':negative,'model_files_unchanged':True,'same_input_ids_across_configurations':True,'fairness':fair,'GPU_apps_after':apps,'checked_paths':checked}
(R/'independent-final-audit.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='checked_paths'},indent=2))
if issues:raise SystemExit(1)
