"""IQ3 runtime upgrade only:64Kx3/256Kx3 on original best config, no other sweep."""
import run as r,json,statistics,time,re
label='IQ3-upgrade-control';cfg=json.loads((r.ROOT/'configs'/f'{label}.json').read_text());done=r.ROOT/'raw'/f'{label}-done.json'
assert json.loads((r.ROOT/'raw/phase-quality-terminal.json').read_text())['status']=='COMPLETE'
assert not done.exists(),'Already complete: inspect saved proof instead of rerunning'
assert not list((r.ROOT/'raw').glob(label+'-*-run*.json')),'PartialIQ3control requires preservation/review'
state=json.loads((r.ROOT/'STATUS.json').read_text());state['running']={'phase':'IQ3runtime64/256control','candidate':label};state['next_exact_action']='Finish only IQ3 actual63400/259500 threeeach on previous best config, then final comparisons/report/audit.';(r.ROOT/'STATUS.json').write_text(json.dumps(state,indent=2));rows=[]
with r.Session(label,cfg) as session:
 smoke=session.request(8000,64,'smoke','smoke');assert smoke['text'].strip() and smoke['draft_tokens']>0
 for target in [63400,259500]:
  session.request(target,256,f'{target}-warmup','warmup')
  for i in range(1,4):rows.append(session.request(target,256,f'{target}-run{i}'))
text=r.Path(cfg['log']).read_text();m=re.search(r'layer split auto: K=(\d+)',text);assert m and 'CUDA1 runs layers' in text,'BothGPUs/autoK not verified'
for row in rows:
 assert row['status']=='OK' and row['generated_tokens']==256 and row['cache_reused_tokens']==0 and not row['abort']
 key=r.ROOT/'raw'/f"{label}-{row['actual_prompt_tokens']}-run1.json"
# Standalone metadata contains the actualIQ3revision, never hard-coded Q4revision.
for target in [63400,259500]:
 for i in range(1,4):
  rec=json.loads((r.ROOT/'raw'/f'{label}-{target}-run{i}.json').read_text());assert rec['model_revision']=='ed59f92082b1e93c0e96d60a8b11aab089b52f09' and rec['Strata_version']=='0.1.32'
oldroot=r.ROOT.parent/'results/raw';comparison=[]
for target,context in [(63400,'64K'),(259500,'256K')]:
 old=[json.loads((oldroot/f'IQ3_S-{context}-{i}.json').read_text()) for i in range(1,4)];new=[x for x in rows if abs(x['actual_prompt_tokens']-target)<=8];assert len(new)==3
 entry={'context':context,'actual_v0131':[x['actual_prompt_tokens'] for x in old],'actual_v0132':[x['actual_prompt_tokens'] for x in new],'old_config':str(r.ROOT.parent/'IQ3_S-runtime.json'),'new_config':str(r.ROOT/'configs'/f'{label}.json'),'auto_K_v0131':25,'auto_K_v0132':int(m[1]),'classification':'SAME_REQUESTED_CONFIG_RUNTIME_UPGRADE' if int(m[1])==25 else 'NOT_CONTROLLED_A_B','note':'New unique prompts use samefrozen code corpus and tokenizer sizing; APIpayloads not pair-identical. Auto split maintained exactly as previousconfig.'}
 for key in ['pp_tps','tg_tps','ttft_s']:
  a=statistics.median(x[key] for x in old);b=statistics.median(x[key] for x in new);entry[key]={'v0131':a,'v0132':b,'delta_percent':100*(b/a-1)}
 comparison.append(entry)
r.c.save(done,{'status':'COMPLETE','runs':rows,'comparison':comparison,'only_two_contexts_tested':True})
r.c.save(r.ROOT/'raw/phase-iq3-terminal.json',{'status':'COMPLETE','ended':time.time()})
s=json.loads((r.ROOT/'STATUS.json').read_text());s['running']=None;s['completed'].append('IQ3runtimeupgrade ONLY64/256K threeeach on previousconfig');s['pending']=[x for x in s['pending'] if not x.startswith('IQ3control')];s['next_exact_action']='Finish needle/diagnostics if pending; assemble comparison/plots/report/productionconfigs; exhaustivecompletionaudit.';(r.ROOT/'STATUS.json').write_text(json.dumps(s,indent=2))
