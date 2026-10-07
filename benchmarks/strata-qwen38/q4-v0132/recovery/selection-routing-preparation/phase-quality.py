"""Literal saved payloads and text diffs only; no judge or quality scores."""
import run as r,workloads as w,json,copy,hashlib,difflib,time
assert json.loads((r.ROOT/'raw/phase-final-matrix-terminal.json').read_text())['status']=='COMPLETE'
old_manifest=json.loads((r.ROOT/'quality/source-manifest.json').read_text());keys=[x['key'] for x in old_manifest['items']]
# Controlled oldresident/default comparison plus separate layer-mode parity.
resident=json.loads((r.ROOT/'configs/BASELINE-resident-v0132.json').read_text())
policy=json.loads((r.ROOT/'raw/prefill-policy-reviewed.json').read_text());layer=json.loads(r.Path(policy['config']).read_text());layer['args']=r.setarg(layer['args'],'--max-context',65536)
variants=[('v0132-resident-default',resident,'v0131'),('v0132-layer-default',layer,'v0131')]
owned=copy.deepcopy(layer);owned['environment_overrides']={'STRATA_SPLIT_OWN':'1'};variants.append(('v0132-layer-own',owned,'v0132-layer-default'))
no_borrow=copy.deepcopy(layer);no_borrow['args'] += ['--no-prefill-borrow'];variants.append(('v0132-layer-no-borrow',no_borrow,'v0132-layer-default'))
rotated=copy.deepcopy(layer);rotated['args']=r.setarg(rotated['args'],'--kv','int8');rotated['environment_overrides']={'STRATA_KV_ROT':'1'};variants.append(('v0132-layer-rotated-int8',rotated,'v0132-layer-default'))
# Legal alternative KV modes keep all other layer-default settings identical.
kv_evidence=json.loads((r.ROOT/'raw/kv-selection.json').read_text())
for mode in ['k8v4','q4_0']:
 cells=[x for x in kv_evidence['screens'] if x['kv']==mode]
 if len(cells)==2 and all(x['status']=='COMPLETE' for x in cells):
  alternate=copy.deepcopy(layer);alternate['args']=r.setarg(alternate['args'],'--kv',mode);alternate['args']=r.setarg(alternate['args'],'--kv-resident',None);alternate['environment_overrides']={}
  variants.append(('v0132-layer-'+mode,alternate,'v0132-layer-default'))
final=json.loads((r.ROOT/'configs/FINAL-v0132-Q4.json').read_text());variants.append(('v0132-final',final,'v0131'))
results=[]
for variant,cfg,reference in variants:
 label='QUALITY-'+variant;folder=r.ROOT/'quality'/variant;folder.mkdir(exist_ok=True);done=r.ROOT/'raw'/f'{label}-done.json'
 if done.exists():results.append(json.loads(done.read_text()));continue
 assert not list((r.ROOT/'raw').glob(label+'-*-request.json')),'Partialqualityvariant requires preservation before restart'
 cfg=copy.deepcopy(cfg);cfg['log']=str(r.ROOT/'logs'/f'{label}-engine.log');r.c.save(r.ROOT/'configs'/f'{label}.json',cfg)
 state=json.loads((r.ROOT/'STATUS.json').read_text());state['running']={'phase':'quality/parity','variant':variant};state['next_exact_action']='Finish exactthree savedqualitypayloads per default/opt-in configuration; hash/textdiff only, no judge.';(r.ROOT/'STATUS.json').write_text(json.dumps(state,indent=2));rows=[]
 try:
  with r.Session(label,cfg) as session:
   sm=session.request(8000,64,'smoke','smoke');assert sm['text'].strip() and sm['draft_tokens']>0
   for key in keys:
    payload=json.loads((r.ROOT/'quality/requests'/f'{key}.json').read_text())
    row=w.request(session,payload['messages'],payload['max_tokens'],key,kind='quality',exact_payload=payload,reuse=True)
    assert row['status']=='OK';r.c.save(folder/f'{key}.json',row);(folder/f'{key}.txt').write_text(row['text']);(folder/f'{key}-reasoning.txt').write_text(row.get('reasoning',''))
    old=(r.ROOT/'quality'/reference/f'{key}.txt').read_text();digest=hashlib.sha256(row['text'].encode()).hexdigest();diff=''.join(difflib.unified_diff(old.splitlines(keepends=True),row['text'].splitlines(keepends=True),fromfile=f'{reference}/{key}.txt',tofile=f'{variant}/{key}.txt'))
    (folder/f'{key}.diff').write_text(diff);(folder/f'{key}-full-response.json').write_text(json.dumps({'content':row['text'],'reasoning':row.get('reasoning',''),'tool_call_events':row.get('tool_call_events',[]),'finish_reasons':row.get('finish_reasons',[]),'raw_stream':str(r.ROOT/'raw'/f'{label}-{key}-stream.json')},indent=2));meta={'key':key,'output_sha256':digest,'request_sha256':hashlib.sha256((r.ROOT/'raw'/f'{label}-{key}-request.json').read_bytes()).hexdigest(),'same_exact_saved_payload':True,'reference':reference,'text_identical':old==row['text'],'reached_output_limit':row['generated_tokens']==payload['max_tokens'],'generated_tokens':row['generated_tokens'],'cache_reused_tokens':row['cache_reused_tokens'],'comparison_scope':'Same saved greedy APIpayload. Resident versionpair sharesoldtopology; otherpairs differ in topology or opt-in config, no automaticquality interpretation.'};(folder/f'{key}-parity.json').write_text(json.dumps(meta,indent=2));rows.append(meta)
  result={'status':'COMPLETE','variant':variant,'rows':rows,'classification':'NON_BIT_IDENTICAL_OPT_IN' if variant=='v0132-layer-own' else 'ROTATED_INT8_OPT_IN' if variant=='v0132-layer-rotated-int8' else 'DEFAULT_OR_SEPARATE_TOPOLOGY'}
 except Exception as e:result={'status':'FAILED','variant':variant,'rows':rows,'error':repr(e)}
 r.c.save(done,result);results.append(result)
assert all(x['status']=='COMPLETE' for x in results if x['variant'] in ['v0132-resident-default','v0132-layer-default','v0132-final']),'Required default quality failed; preserve and inspect'
r.c.save(r.ROOT/'raw/quality-parity-summary.json',{'status':'COMPLETE','variants':results,'old_source_manifest':str(r.ROOT/'quality/source-manifest.json'),'judgement':'NONE'})
r.c.save(r.ROOT/'raw/phase-quality-terminal.json',{'status':'COMPLETE','ended':time.time()})
s=json.loads((r.ROOT/'STATUS.json').read_text());s['running']=None;s['completed'].append('Exactsaved3qualitypayloads: old/archive,newdefaults,opt-in outputs/SHA256/textdiff; no judge');s['pending']=[x for x in s['pending'] if not x.startswith('exactqualitygreedy')];s['excluded_runs'] += [{'phase':'quality','variant':x['variant'],'status':x['status']} for x in results if x['status']!='COMPLETE'];s['next_exact_action']='Upstreamneedle and IQ3runtime controls, then plots/report/completionaudit.';(r.ROOT/'STATUS.json').write_text(json.dumps(s,indent=2))
