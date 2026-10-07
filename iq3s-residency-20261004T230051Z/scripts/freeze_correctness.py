"""Freeze preserved correctness requests with the frozen service's real tokenizer."""
import hashlib, json, pathlib, sys
from lab import ROOT, save, hashjson
sys.path[:0]=[str(ROOT/'src/control'),str(ROOT/'src/control/tools')]
import strata_tokenizer as ST
from serve.frontend import ChatTemplate
from serve.server import Service
out=ROOT/'workloads/correctness-manifest.json'
if out.exists():raise RuntimeError('Frozen correctness manifest already exists')
vocabdir=pathlib.Path('/srv/ai/models/strata/packs/iq3_s/tokenizer')
vocab=json.loads((vocabdir/'vocab.json').read_text());tokens=[None]*len(vocab)
for token,number in vocab.items():tokens[number]=token
svc=Service.__new__(Service)
svc.tok=ST.Tokenizer(tokens,(vocabdir/'merges.txt').read_text().split('\n'),json.loads((vocabdir/'token_type.json').read_text()))
svc.template=ChatTemplate(vocabdir/'chat_template.jinja');svc.effort_end=False
old=pathlib.Path('/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/raw')
manifest={'source_sha':'6f32ec070f23ced9f50e704d854d775da52591ab','policy':'Replay saved requests without editing messages, sampling or output budget. Saved 512-token extensions used for cases 5/6; all others original 256-token requests. Natural EOS permitted in correctness only.','payloads':{}}
for n in range(1,11):
    source=old/(f'CORRECT-EXT-CONTROL-case{n}-request.json' if n in (5,6) else f'CORRECT-H-OLD-case{n}-request.json')
    p=json.loads(source.read_text());ids=svc.encode_prompt(p['messages'],None,{'enable_thinking':False})
    path=ROOT/'workloads'/f'correct-case{n}.json'
    if path.exists():raise RuntimeError('Correctness payload exists')
    save(path,p);h=hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest()
    idpath=ROOT/'workloads/token-ids'/f'{h}.json'
    if not idpath.exists():idpath.write_text(json.dumps(ids,separators=(',',':')))
    manifest['payloads'][f'case{n}']={'path':str(path),'payload_sha256':hashjson(p),'input_ids_sha256':h,'actual_input_tokens':len(ids),'token_ids_path':str(idpath),'source_payload':str(source),'source_file_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'requested_output':p['max_tokens']}
    print(n,len(ids),p['max_tokens'],flush=True)
save(out,manifest)
