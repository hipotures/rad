import sys,json,hashlib
from pathlib import Path
repo=Path(sys.argv[1]);root=Path(sys.argv[2]);variant=sys.argv[3]
sys.path[:0]=[str(repo),str(repo/'tools')]
import strata_tokenizer as ST
from serve.frontend import ChatTemplate
from serve.server import Service
vocab_path=Path('/srv/ai/models/strata/packs/iq3_s/tokenizer');vocab=json.loads((vocab_path/'vocab.json').read_text());tokens=[None]*len(vocab)
for token,idx in vocab.items():tokens[idx]=token
svc=Service.__new__(Service);svc.tok=ST.Tokenizer(tokens,(vocab_path/'merges.txt').read_text().split('\n'),json.loads((vocab_path/'token_type.json').read_text()));svc.template=ChatTemplate(vocab_path/'chat_template.jinja');svc.effort_end=False
out={}
for p in sorted((root/'payloads').glob('*.json')):
 payload=json.loads(p.read_text());ids=svc.encode_prompt(payload['messages'],None,{'enable_thinking':False}) if hasattr(svc,'encode_prompt') else svc.tok.encode(svc.template.render(payload['messages'],tools=None,enable_thinking=False),parse_special=True);encoded=json.dumps(ids,separators=(',',':'));sha=hashlib.sha256(encoded.encode()).hexdigest();path=root/'token-ids'/f'{sha}.json';path.write_text(encoded)
 key=hashlib.sha256(json.dumps(payload['messages'],sort_keys=True,separators=(',',':')).encode()).hexdigest();out[key]={'actual_prompt_tokens':len(ids),'input_ids_sha256':sha,'token_ids_path':str(path),'payload_file':str(p)}
(root/'analysis'/f'encoding-{variant}.json').write_text(json.dumps(out,indent=2));print(variant,[(Path(x['payload_file']).name,x['actual_prompt_tokens']) for x in out.values()])
