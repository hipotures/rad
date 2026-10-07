"""Pre-recording completeness corrections and source catalog; does not inspect routing."""
import hashlib,json,pathlib,re,sys
C=pathlib.Path(__file__).resolve().parents[1];R=C.parents[1];sys.path[:0]=[str(R/'src/control'),str(R/'src/control/tools')]
from serve.server import Service
from serve.frontend import ChatTemplate
import strata_tokenizer as ST
cfg=json.load(open(C/'configs.json'))['32k'];v=pathlib.Path(cfg['tokenizer']);d=json.load(open(v/'vocab.json'));tokens=[None]*len(d)
for t,i in d.items():tokens[i]=t
svc=Service(None,ST.Tokenizer(tokens,(v/'merges.txt').read_text().split('\n'),json.load(open(v/'token_type.json'))),ChatTemplate(v/'chat_template.jinja'),cfg['model_name'])
m=json.load(open(C/'benchmark-manifest.json'));pmanifest=json.load(open(C/'corpus/payload-manifest.json'))
for row in m['tasks']:
 n=row['task_id'];info=row['payload']
 if n=='code-archive':
  full=pathlib.Path(row['source_path']).read_text();ends=[x.end() for x in re.finditer(r'\n\s*\n',full)];excerpt=full[:ends[-1]]
  ep=pathlib.Path(row['excerpt_path']);ep.write_text(excerpt);p=json.load(open(info['path']));p['messages'][-1]['content']='Source material:\n'+excerpt+'\n\nTask:\n'+row['instruction'];pathlib.Path(info['path']).write_text(json.dumps(p,indent=2)+'\n');ids=svc.encode_prompt(p['messages'],None,{'enable_thinking':False});ip=pathlib.Path(info['token_ids_path']);ip.write_text(json.dumps(ids,separators=(',',':')))
  info.update(payload_sha256=hashlib.sha256(json.dumps(p,sort_keys=True,separators=(',',':')).encode()).hexdigest(),messages_sha256=hashlib.sha256(json.dumps(p['messages'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),input_ids_sha256=hashlib.sha256(ip.read_bytes()).hexdigest(),actual_input_tokens=len(ids));row.update(actual_input_tokens=len(ids),retained_source_characters=len(excerpt),excerpt_sha256=hashlib.sha256(ep.read_bytes()).hexdigest(),length_method='Coherent complete-paragraph prefix of historical zipfile excerpt; original26000-character source ends mid-comment and remains preserved')
  pmanifest['payloads'][n]=info
 row['source_urls']=([f'https://www.rfc-editor.org/rfc/rfc{num}.txt'] if (num:={'text-http':9111,'text-tls':8446,'mixed-fields':8941,'text-websocket':6455}.get(n)) else ['https://github.com/lerocha/chinook-database/tree/'+row['source_revision']] if n=='mixed-chinook' else ['https://github.com/python/cpython'] if n in ['code-queue','code-archive','math-rational'] else [])
for p,j in [(C/'benchmark-manifest.json',m),(C/'corpus/payload-manifest.json',pmanifest)]:p.write_text(json.dumps(j,indent=2)+'\n')
with (C/'prompt-catalog.md').open('a') as f:
 f.write('\n# Frozen Phase 0 core prompts\n\nAll are offline single requests, with no tool execution. The exact source/excerpt and full payload are linked; short inputs remain short.\n')
 for row in m['tasks']:
  source=pathlib.Path(row['excerpt_path']).read_text();f.write('\n## '+row['task_id']+'\n\n'+row['family']+' / '+row['subtask']+'; source group '+row['source_group']+'; split '+row['split']+'; configured limit '+str(row['context_limit'])+', actual input '+str(row['actual_input_tokens'])+' tokens.\n\nActual instruction:\n\n```text\n'+row['instruction']+'\n```\n\nRepresentative source:\n\n```text\n'+source[:750]+'\n```\n\nLength method: '+row['length_method']+'. [Complete payload]('+row['payload']['path']+'); [source snapshot]('+row['source_path']+').\n')
print('Corpus final freeze:12 tasks,8x32K+4x128K,one role per source group')
