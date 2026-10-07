"""Open historical payloads/builders; record exact messages, lineages and repetition."""
import collections,hashlib,json,pathlib,re,shutil
C=pathlib.Path(__file__).resolve().parents[1];R=C.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
manifests=[R/'workloads/manifest.json',R/'experiments/E026-pool-generalization/workloads/manifest.json']+[R/'campaigns'/d/p for d,p in [('q4-residency-v2-20261005T202441Z','inputs/manifest.json'),('q4-conditional-admission-20261006T010859Z','inputs/manifest.json'),('q4-live-oracle-20261006T040656Z','inputs/manifest.json'),('q4-oracle-decomposition-20261006T100032Z','inputs/manifest.json'),('upstream-921-spin-validation-20261006T131023Z','workloads/manifest.json')]]
rows=[];seen=set();snaps=C/'provenance/historical-payloads';snaps.mkdir(exist_ok=True)
for mp in manifests:
 if not mp.exists():continue
 j=json.loads(mp.read_text());shutil.copyfile(mp,C/'provenance'/('historical-manifest-'+mp.parent.parent.name+'-'+mp.parent.name+'.json'))
 for name,v in j.get('payloads',{}).items():
  p=pathlib.Path(v['path'])
  if p in seen:continue
  seen.add(p);raw=p.read_bytes();payload=json.loads(raw);messages=payload.get('messages',[]);text='\n'.join(str(m.get('content','')) for m in messages)
  snap=snaps/(sha(raw)+'.json');snap.write_bytes(raw)
  if 'Independent pool validation' in text:lineage='E026-'+re.search(r'Document family (\w+)',text)[1]
  elif 'Repository files' in text:lineage='strata-repository-maintenance'
  elif 'Read and write ZIP files' in text:lineage='cpython-zipfile'
  elif 'asyncio' in text or 'class Queue' in text:lineage='cpython-asyncio-queues'
  elif 'ThreadPoolExecutor' in text:lineage='cpython-thread-executor'
  elif 'RotatingFileHandler' in text:lineage='cpython-logging-handlers'
  else:lineage='task-'+re.sub('^(quality-|safety-)','',name)
  nonces=[{'text':m.group(),'character_offset':m.start(),'length_characters':len(m.group()),'purpose':'benchmark run identification; historical evidence preserved'} for m in re.finditer(r'\[bench run [^\]]+\]|Nonce [^\s.]+',text)]
  lines=[x for x in text.splitlines() if len(x)>100];repeats=[{'line_sha256':sha(x.encode()),'count':n,'excerpt':x[:180]} for x,n in collections.Counter(lines).items() if n>1]
  start=text.find('===== SOURCE');end=text.rfind('\n\nTask:')
  if start<0:start=text.find('Repository files')
  if start<0:start=text.find('Source document:')
  row={'id':name,'manifest':str(mp),'path':str(p),'snapshot':str(snap),'file_sha256':sha(raw),'messages':messages,'metadata':v,'lineage':lineage,'source_text_character_bounds':{'start':start if start>=0 else None,'end':end if end>=0 else None},'nonces':nonces,'duplicated_long_lines':repeats,'requested_output':payload.get('max_tokens'),'output_instruction_artificially_extended':any(x in text for x in ['40 numbered sections','at least 30','at least 20','book-length','book length','4096','80 cases']),'tool_execution':False,'form':'single offline prompt','nonce_normalized_message_sha256':sha(re.sub(r'\[bench run [^\]]+\]|Nonce [^\s.]+','IDENTIFIER',text).encode())}
  idp=v.get('token_ids_path')
  if idp and pathlib.Path(idp).exists():
   ids=json.loads(pathlib.Path(idp).read_text());row['saved_input_token_count']=len(ids);row['saved_input_ID_sha256']=sha(json.dumps(ids,separators=(',',':')).encode())
  rows.append(row)
builders=[R/'scripts/prepare_workloads.py',R/'scripts/prepare_pool_independent.py',R/'campaigns/q4-residency-v2-20261005T202441Z/scripts/init_campaign.py',R/'campaigns/q4-conditional-admission-20261006T010859Z/scripts/episodes.py',R/'campaigns/upstream-921-spin-validation-20261006T131023Z/scripts/prepare.py',R/'campaigns/upstream-921-spin-validation-20261006T131023Z/scripts/qualify_q4.py',pathlib.Path('/srv/ai/benchmarks/strata-qwen38/threeway-32k-128k-longdecode-20261004T212330Z/workloads.py')]
b=[]
for p in builders:
 if not p.exists():continue
 raw=p.read_bytes();dest=C/'provenance'/('builder-'+p.parent.parent.name+'-'+p.name);dest.write_bytes(raw);b.append({'path':str(p),'snapshot':str(dest),'sha256':sha(raw)})
(C/'workload-inventory.json').write_text(json.dumps({'payloads_opened':len(rows),'items':rows,'builders_opened':b,'semantic_grouping_note':'Task-level source lineages; variants and context excerpts are not independent tasks. Same collections are reported separately from distinct documents.'},indent=2)+'\n')
cat=['# Historical prompt catalog\n\nExact messages are retained in workload-inventory.json and hashed payload snapshots. Representative excerpts below are quoted as historical data, including identifiers.']
for lineage in sorted(set(r['lineage'] for r in rows)):
 group=[r for r in rows if r['lineage']==lineage];r=group[0];m=r['messages'];u=m[-1]['content'] if m else '';task=u.rsplit('\n\nTask:',1)[-1] if '\n\nTask:' in u else u.rsplit('\n\nTask:\n',1)[-1]
 cat+=['\n## '+lineage,f"{len(group)} payloads; saved token lengths {sorted(set(x.get('saved_input_token_count') for x in group if x.get('saved_input_token_count') is not None))}. Full [payload]({r['snapshot']}).",'Actual instruction:\n\n```text\n'+task[-2000:]+'\n```','Representative source/prefix:\n\n```text\n'+u[:850]+'\n```']
(C/'prompt-catalog.md').write_text('\n\n'.join(cat)+'\n')
print('AUDITED',len(rows),'payloads',len(set(r['lineage'] for r in rows)),'lineages',len(b),'builders',flush=True)
