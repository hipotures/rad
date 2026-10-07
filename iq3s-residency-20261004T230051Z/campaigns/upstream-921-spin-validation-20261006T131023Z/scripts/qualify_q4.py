"""One deterministic length-eligibility repair, before any valid Q4 pair.

Saved Q4 code variant1 naturally stopped at3788. Preserve original inputs and
invalid attempt. Add one common long-form instruction to all Q4 measured inputs;
never rank prompts by timing, and never alter IQ3 inputs or engine settings.
"""
import hashlib,json,pathlib,sys
import run
C=run.C;S=C/'source';sys.path[:0]=[str(S),str(S/'tools')]
from serve.server import Service
from serve.frontend import ChatTemplate
import strata_tokenizer as ST
manifest=run.load(C/'workloads/manifest-v1.json');cfg=run.load(C/'configs-base.json')['Q4']
v=pathlib.Path(cfg['tokenizer']);vocab=run.load(v/'vocab.json');tokens=[None]*len(vocab)
for s,i in vocab.items():tokens[i]=s
tok=ST.Tokenizer(tokens,(v/'merges.txt').read_text().split('\n'),run.load(v/'token_type.json'));svc=Service(None,tok,ChatTemplate(v/'chat_template.jinja'),cfg['model_name'])
instruction='\n\nCompletion requirement: Write a book-length treatment of at least 18000 words. Develop at least 60 numbered, fully worked cases, each with a detailed derivation or incident, explicit code or messages, verification, and implications. Spend at least 250 words on each case. Proceed in sequence and expand the early cases thoroughly before moving on. Do not compress later cases into a list, skip steps, or jump to a conclusion. Continue the detailed document until the output limit interrupts it; no concluding summary is needed.'
changes=[]
for key,old in list(manifest['payloads'].items()):
 if not key.startswith('Q4/') or key=='Q4/warmup':continue
 p=run.load(old['path']);p['messages'][-1]['content']+=instruction
 ids=svc.encode_prompt(p['messages'],None,{'enable_thinking':False});limit=32768 if old['profile']=='32k' else 131072
 assert len(ids)+4096+8<=limit,(key,len(ids),'NO_SOURCE_TRIM_ALLOWED')
 digest=hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest()
 name=key.split('/')[1];path=C/'workloads/Q4-v2'/f'{name}.json';run.save(path,p);ip=path.with_name(f'{name}-ids.json');ip.write_text(json.dumps(ids,separators=(',',':')))
 new={**old,'path':str(path),'payload_sha256':run.hashjson(p),'input_ids_sha256':digest,'token_ids_path':str(ip),'actual_input_tokens':len(ids),'length_qualification_version':2,'original_path':old['path'],'qualification_reason':'Variant1codeA natural EOS3788 before any valid Q4 A/B evidence'}
 manifest['payloads'][key]=new;changes.append({'key':key,'old_hash':old['input_ids_sha256'],'new_hash':digest,'old_tokens':old['actual_input_tokens'],'new_tokens':len(ids)})
 print(key,len(ids),flush=True)
manifest['policy']+=' Q4-v2: common deterministic book-length instruction appended to all Q4 families/profiles/variants after originalcode naturalEOS3788. No original source text removed; budget unchanged; repair frozen before any valid Q4 pair.'
run.save(C/'workloads/manifest.json',manifest)
run.save(C/'workloads/Q4-length-qualification.json',{'frozen_utc':run.utc(),'instruction':instruction,'reason':'Original saved code Q4 variant1 failed outputlength eligibility with EOS3788. No valid Q4 pair existed and no100us timing was collected.','changes':changes,'no_timing_based_selection':True,'maximum_replacements_per_cell_unchanged':2})
with (C/'DECISIONS.md').open('a') as f:f.write('\nQ4-v1code32K first arm naturally stopped3788 tokens. Preserve and objectively invalidate entire original pair1; no B measured. Freeze common book-length instruction for all Q4 measured payloads (code/math/prose,32K/128K,all3savedvariants), retain all source text and greedy4096budget, before any valid Q4 pair. Exact inputIDs re-rendered and admission-checked. IQ3payloads unchanged. At most two replacement slots per cell remains binding.\n')
