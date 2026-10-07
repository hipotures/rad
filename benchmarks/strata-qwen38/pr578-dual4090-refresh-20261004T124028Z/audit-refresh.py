#!/usr/bin/env python3
"""Independent completion, replay, cache-capacity and provenance audit for refreshed campaign."""
import json,pathlib,hashlib,statistics,subprocess,time,math
R=pathlib.Path(__file__).resolve().parent;issues=[];limits=[]
def load(n,default=None):
 p=R/n
 return json.loads(p.read_text()) if p.exists() else default
def require(ok,message):
 if not ok:issues.append(message)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
S=load('summary.json',{'cells':[],'runs':[]});cells=S['cells'];runs=S['runs']
for name in ['LS-A','LS-B','PR-LS','H-OLD','H-OPT','H-OPT-FIXED']:
 c=next((x for x in cells if x['config']==name and x['actual_prompt']==31400),None)
 require(c is not None,'Primary32K candidate missing: '+name)
 if c and c['valid_runs']!=3:limits.append({'scope':name,'reason':'INCOMPLETE_HEADLINE_STATISTICS: '+str(c['valid_runs'])+'/3 valid; all attempts preserved'})
 if c:
  rr=[load(pathlib.Path(x).relative_to(R)) for x in c['raw_paths']]
  require(len(rr)==c['valid_runs'],'Valid raw-path count mismatch '+name)
  for k in ['pp_tps','tg_tps']:
   require(math.isclose(statistics.median(a[k] for a in rr),c[k],rel_tol=1e-10),'Median mismatch '+name+' '+k)
 for suffix in ['32K-warmup','32K-run1','32K-run2','32K-run3']:
  a=load(f'raw/{name}-{suffix}.json');require(a is not None,'Missing canonical raw '+name+' '+suffix)
  if not a:continue
  expected=64 if suffix.endswith('warmup') else 256
  if a.get('valid'):require(a.get('generated_tokens')==expected,'Valid generation length '+name+' '+suffix)
  else:
   require(not suffix.endswith('warmup'),'Invalid warmup '+name)
   require(any(x in ['tool_calls','stop'] for x in a.get('finish_reasons',[])) and a.get('generated_tokens',0)<expected,'Unexpected invalid condition '+name+' '+suffix)
   limits.append({'scope':name+' '+suffix,'reason':'Natural early stop preserved INVALID; excluded from headline median'})
  require(a.get('cache_reused_tokens')==0,'Nonzero prompt reuse '+name+' '+suffix)
  if suffix!='32K-warmup':require(a.get('actual_prompt_tokens')==31400,'Wrong actual32K count '+name)
for a in runs:
 if a.get('valid'):continue
 p=pathlib.Path(a.get('input_token_ids_path',''))
 require(p.is_file(),'Invalid raw input-token IDs missing '+a.get('raw_path',''))
 if p.is_file():require(digest(p)==a.get('input_ids_sha256') and len(json.loads(p.read_text()))==a.get('actual_prompt_tokens'),'Invalid raw token-ID/count mismatch '+a.get('raw_path',''))
 require(a.get('Strata_HEAD') and a.get('full_config') and a.get('exclusion'),'Invalid raw provenance/exclusion incomplete '+a.get('raw_path',''))
 limits.append({'raw':a.get('raw_path'),'reason':a.get('exclusion'),'finish_reasons':a.get('finish_reasons'),'generated':a.get('generated_tokens')})
for name in ['H-OLD','H-OPT','H-OPT-FIXED']:
 d=load(f'raw/{name}-startup-fairness.json',{});require(d.get('status')=='PASS','Initial cache fairness failed/missing '+name)
reference=load('auto-capacities.json',{})
for name in ['H-OLD','H-OPT','H-OPT-FIXED']:
 c=load(f'configs/{name}.json',{});a=c.get('args',[])
 require('--pcie-frac' in a and float(a[a.index('--pcie-frac')+1])==reference.get('frozen_pcie_frac'),'Helper PCIe setting not frozen '+name)
for c in cells:
 for p in c['raw_paths']:
  a=load(pathlib.Path(p).relative_to(R));require(a is not None,'Missing cell raw reference '+p)
  if not a:continue
  require(a.get('Strata_HEAD') is not None and a.get('full_config') is not None,'Raw provenance incomplete '+p)
  require(a.get('model_revision')=='ed59f92082b1e93c0e96d60a8b11aab089b52f09','Wrong model revision '+p)
  idfile=pathlib.Path(a.get('input_token_ids_path',''))
  require(idfile.is_file(),'Input token IDs missing '+p)
  if idfile.is_file():
   require(digest(idfile)==a['input_ids_sha256'],'Input token hash mismatch '+p)
   require(len(json.loads(idfile.read_text()))==a['actual_prompt_tokens'],'Token count mismatch '+p)
  require(a.get('cache_reused_tokens')==0,'Nonzero reuse '+p)
  if not a.get('valid'):limits.append({'raw':p,'reason':'INVALID_REQUEST'})
  config=a.get('full_config',{});args=config.get('args',[])
  for k,v in [('--spec','4'),('--spec-min-p','0.5'),('--kv','int8'),('--kv-resident','32768'),('--pool-workers','15'),('--max-context','262144')]:require(k in args and args[args.index(k)+1]==v,'Frozen setting changed '+p+' '+k)
  if c['config'] in ['LS-A','LS-B','PR-LS','H-OLD','H-OPT','H-OPT-FIXED'] or c['config'].endswith(('-FINAL','-FINAL-TOKFIX','-FINAL-TOKFIX-CLEAN32','-STEADY2048')):
   require('--suffix-draft' in args and args[args.index('--suffix-draft')+1]=='0','Primary result has lookup enabled '+p)
for n in ['test-review.json','diagnostic-test-review.json']:
 require(load(n,{}).get('benchmark_allowed') is True,'Native/Python test review incomplete '+n)
policy=load('headline-instrumentation-policy.json',{})
if policy.get('mode')=='UNMODIFIED_UPSTREAM_BINARIES_NO_DEBUG':
 for name in ['LS-A','LS-B','PR-LS','H-OLD','H-OPT','H-OPT-FIXED']+[x['config'] for x in cells if x['config'].endswith(('-FINAL','-FINAL-TOKFIX','-FINAL-TOKFIX-CLEAN32','-STEADY2048','-LOOKUP-ON','-LOOKUP-ON-W32')) or '-FRESH' in x['config'] and 'DIAG' not in x['config']]:
  config=load(f'configs/{name}.json',{});exe=pathlib.Path(config.get('exe',''))
  require(exe.name=='strata-original' and exe.is_file(),'Headline must use clean upstream binary '+name)
  if exe.is_file():require(config.get('binary_sha256')==digest(exe) and digest(exe) in policy['original_binary_SHA256'].values(),'Headline binary provenance mismatch '+name)
  require('STRATA_BENCH_CACHE_SNAPSHOT' not in config.get('extra_env',{}),'Debug instrumentation enabled in headline '+name)
 require(load('normal-counter-validation.json',{}).get('all_CPU_match') is True,'Normal CPU fallback exact-counter validation missing')
 limits.append({'scope':'Initial clean speed layout','reason':'Physical capacities logged; initial resident count/overlap follows deterministic constructor verified in separate diagnostics. ID sets not directly dumped in clean speed runs.'})
else:
 require(load('instrumentation-overhead.json',{}).get('within_1pct') is True,'Instrumentation overhead gate incomplete')
require(load('correctness/review.json',{}).get('benchmark_allowed') is True,'Paired correctness manual review incomplete')
correct=load('correctness/summary.json',[]);require(len(correct)==10,'Fewer than10 paired correctness cases')
require(all(x['input_identical'] and not x['malformed_output'] for x in correct),'Correctness battery failed')
selection=load('selection.json',{});matrix_policy=load('matrix-retry-policy.json',{});matrix_labels=matrix_policy.get('final_labels',{});matrix_contexts=[31400,63402,127002,259507] if matrix_labels else [31400,63400,127000,259500]
for k in ['best_layer_split','best_optimized_helper']:
 src=selection.get(k,{}).get('config');require(bool(src),'Missing finalist '+k)
 if not src:continue
 for context in matrix_contexts:
  c=next((x for x in cells if x['config']==matrix_policy.get('cell_overrides',{}).get(src,{}).get(str(context),matrix_labels.get(src,src+'-FINAL')) and x['actual_prompt']==context),None)
  require(c is not None and c['valid_runs']==3,'Incomplete final context '+src+' '+str(context))
# Independently compare both finalist ID sequences and context-specific warmups.
for context,tag in zip(matrix_contexts,['32K','64K','128K','256K']):
 names=[]
 for key in ['best_layer_split','best_optimized_helper']:
  src=selection[key]['config'];names.append(matrix_policy.get('cell_overrides',{}).get(src,{}).get(str(context),matrix_labels.get(src,src+'-FINAL')))
 for i in [1,2,3]:
  aa=[load(f'raw/{name}-{tag}-run{i}.json',{}) for name in names]
  require(aa[0].get('input_ids_sha256')==aa[1].get('input_ids_sha256') and aa[0].get('input_ids_sha256'),'Finalists input IDs differ '+tag+' run'+str(i))
  require(all(a.get('generated_tokens')==256 and a.get('actual_prompt_tokens')==context and a.get('cache_reused_tokens')==0 and a.get('valid') for a in aa),'Finalists exact request validity '+tag+' run'+str(i))
 warm=[load(f'raw/{name}-{tag}-warmup.json',{}) for name in names]
 require(warm[0].get('input_ids_sha256')==warm[1].get('input_ids_sha256') and warm[0].get('input_ids_sha256'),'Finalist warmup input IDs differ '+tag)
 require(all(a.get('generated_tokens')==64 and a.get('cache_reused_tokens')==0 for a in warm),'Finalist unequal warmup work '+tag)
for a in runs:
 if not a.get('valid'):continue
 st=a.get('initial_layout',{})
 if st.get('helper'):
  require(st.get('primary')==8586 and st.get('helper')==11796,'Helper initial physical capacities changed '+a.get('raw_path',''))
  if a.get('headline_eligible'):require(st.get('initial_resident_expert_count')==20382 and st.get('initial_overlap')==0,'Headline helper initial count/overlap missing or changed '+a.get('raw_path',''))
for src in [selection.get('best_layer_split',{}).get('config'),'H-OLD',selection.get('best_optimized_helper',{}).get('config')]:
 c=next((x for x in cells if src and x['config']==src+'-STEADY2048'),None);require(c is not None and c['valid_runs']==3,'Steady2048 incomplete '+str(src))
if selection.get('top2_within5pct'):
 for x in selection['top2']:
  for i in [1,2,3]:require((R/'raw'/f"{x['config']}-FRESH{i}-done.json").exists(),'Missing fresh-server replicate')
for src in [selection.get('best_layer_split',{}).get('config'),'H-OLD',selection.get('best_optimized_helper',{}).get('config')]:
 if src:require((R/'raw'/f'{src}-LOOKUP-ON-W32-done.json').exists(),'Secondary lookup incomplete '+src)
for name in ['H-OLD-DIAG','H-OPT-FIXED-DIAG']:
 require((R/'raw'/f'{name}-done.json').exists(),'Cache progression diagnostic incomplete '+name)
for f in ['report.md','summary.csv','summary.json','environment.json','release-and-source-audit.md','model-provenance.json','replay-provenance.json']:
 require((R/f).is_file() and (R/f).stat().st_size>0,'Missing artifact '+f)
model=load('model-provenance.json',{})
for item in model.get('unchanged_stat_checks',[]):
 p=pathlib.Path(item['path']);st=p.stat();require(st.st_size==item['size'] and st.st_mtime_ns==item['mtime_ns'],'Model file changed '+str(p))
apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
require(not any('strata-pr578-refresh-20261004' in x for x in apps.splitlines()),'Owned Strata engine remains running')
result={'status':'PASS' if not issues else 'FAIL','issues':issues,'limitations':limits,'time_UTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'measured_rows':len(runs),'cells':len(cells),'foreign_or_other_GPU_processes':apps,'no_physical_PSS_polling':'PSS snapshots only at request boundaries; periodic RSS/CPU/GPU counters','historical_results_used_as_new_repetitions':False}
(R/'audit-refresh.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(bool(issues))
