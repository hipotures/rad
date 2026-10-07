from pathlib import Path
import subprocess,json,time,os,statistics,hashlib
R=Path(__file__).resolve().parent
assert json.loads((R/'raw/controls-preparation.json').read_text())['status']=='READY'
for version,repo in [('v0131','/srv/ai/strata'),('v0132','/srv/ai/strata-v0.1.32')]:
 out=R/'controls'/version;done=out/'raw/control-done.json'
 if not done.exists():
  assert not list((out/'raw').glob('PP-CONTROL-*-run*.json')),'Partialcontrol requires explicitpreservation/recovery; neveroverwrite'
  with (out/'logs/driver.log').open('w') as f:
   cmd=[repo+'/.venv/bin/python',str(out/'control.py')];p=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
   state={'phase':'controlledPPupgradeAB','version':version,'pid':p.pid,'command':cmd,'started':time.time(),'directory':str(out)};(R/'pp-control-active-process.json').write_text(json.dumps(state))
   s=json.loads((R/'STATUS.json').read_text());s['running']=state;s['next_exact_action']='Wait current versioncontrol to complete16measured across8/16/32/64/128/256K,then other version,pairedrequestvalidation andcomparison. No concurrentengines.';(R/'STATUS.json').write_text(json.dumps(s,indent=2))
   (R/'STATUS.md').write_text('# v0.1.32 — IN_PROGRESS\n\nCompleted: singleGPUresident baseline and auto/Kscreen/TOP2. WinnerK24, PP3216.4,TG110.3.\n\nRunning: '+json.dumps(state)+'\n\nNext: '+s['next_exact_action']+'\n\nFullremainingplan: PLAN.md and STATUS.json. Fastbuild rejected by upstream numericalgate; oldcampaign frozen; immutableversioncontrols in separate directories.\n')
   rc=p.wait();(out/'raw/process-terminal.json').write_text(json.dumps({'exit_code':rc,'ended':time.time(),'version':version}))
   assert rc==0,f'{version}control failed; preservecurrentattempt andinspect'
 d=json.loads(done.read_text());assert d['status']=='COMPLETE' and len(d['runs'])==16
rows=[]
plan=json.loads((R/'controls-request-plan.json').read_text())
for cell in plan['cells']:
 target=cell['target'];by={}
 for v in ['v0131','v0132']:
  rr=[]
  for i in range(1,cell['n']+1):
   folder=R/'controls'/v/'raw';d=json.loads((folder/f'PP-CONTROL-{target}-run{i}.json').read_text());req=json.loads((folder/f'PP-CONTROL-{target}-run{i}-request.json').read_text())
   assert d['generated_tokens']==256 and d['cache_reused_tokens']==0 and d['actual_prompt_tokens']==d['actual_prompt_tokens_tokenizer'] and abs(d['actual_prompt_tokens']-target)<=8
   rr.append((d,req))
  by[v]=rr
 for (a,qa),(b,qb) in zip(by['v0131'],by['v0132']):
  assert qa==qb,'Versioncontrol APIpayload mismatch'
  assert a['actual_prompt_tokens']==b['actual_prompt_tokens']
 row={'target':target,'n_each':cell['n'],'paired_payloads_identical':True,'actual_tokens_v0131':[d['actual_prompt_tokens'] for d,q in by['v0131']],'actual_tokens_v0132':[d['actual_prompt_tokens'] for d,q in by['v0132']]}
 for key in ['pp_tps','tg_tps','ttft_s','total_wall_s']:
  a=statistics.median(d[key] for d,q in by['v0131']);b=statistics.median(d[key] for d,q in by['v0132']);row[key]={'v0131':a,'v0132':b,'delta_percent':100*(b/a-1)}
 rows.append(row)
(R/'comparison-pp-control.json').write_text(json.dumps({'status':'COMPLETE_CONTROLLED_VERSION_AB','rows':rows,'config_plan':str(R/'controls-request-plan.json'),'scope':'Whole runtimeversion comparison, not isolatedpatchcausality; samepairedAPIpayloads,CLIsettings,byteidenticaldensepack/MTP, profile, corpus andphysicalGPU pair. Naturalruntime allocation/timing may differ. Filesystemcoldcache not controlled.'},indent=2))
(R/'raw/phase-pp-control-terminal.json').write_text(json.dumps({'status':'COMPLETE','exit_code':0,'ended':time.time(),'measured_requests':32,'comparison':str(R/'comparison-pp-control.json')}))
s=json.loads((R/'STATUS.json').read_text());s['running']=None;s['completed'].append('Controlledversion PPmatrix32measured withpairedpayloads COMPLETE');s['pending']=[x for x in s['pending'] if not x.startswith('controlled old/new PP')];s['next_exact_action']='BestK24 prefillauto/auto:32768/8192/16384/32768 actual128Kscreens, TOP2x3at128/256K; sourcelegal/safetycheckfirst.';(R/'STATUS.json').write_text(json.dumps(s,indent=2))
print('ControlledPP comparison COMPLETE',flush=True)
