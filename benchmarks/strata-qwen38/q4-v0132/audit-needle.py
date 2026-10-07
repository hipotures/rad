"""Offline proof of upstream needle payloads/actualcounts and mechanical recall outcomes."""
from pathlib import Path
import json,hashlib,random,time,importlib.util
import campaign as c
from final_identity import final_config_path
R=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_text())
summary=load(R/'raw/needle-summary.json');source=Path(summary['source'])
assert source==Path('/srv/ai/strata-v0.1.32/tools/needle_bench.py') and hashlib.sha256(source.read_bytes()).hexdigest()==summary['source_SHA256']
assert summary['status']=='COMPLETE' and len(summary['results'])==9
spec=importlib.util.spec_from_file_location('needle_source',source);upstream=importlib.util.module_from_spec(spec);spec.loader.exec_module(upstream)
rnd=random.Random(7);results=[]
tokenizer_path=Path(load(final_config_path())['tokenizer']);vocab=load(tokenizer_path/'vocab.json');tokens=[None]*len(vocab)
for token,index in vocab.items():tokens[index]=token
tok=c.ST.Tokenizer(tokens,(tokenizer_path/'merges.txt').read_text().split('\n'),load(tokenizer_path/'token_type.json'));template=c.ChatTemplate(tokenizer_path/'chat_template.jinja')
for item,(target,depth) in zip(summary['results'],[(t,d) for t in [31400,127000,259500] for d in [10,50,90]]):
    assert item['target']==target and item['depth']==depth
    expected_word=f'{rnd.choice(upstream.WORDS)}-{rnd.choice(upstream.WORDS)}-{rnd.randint(100,999)}';assert item['word']==expected_word
    request_path=Path(item['request']);payload=load(request_path);rawpath=request_path.with_name(request_path.name.replace('-request.json','.json'));row=load(rawpath)
    assert payload['temperature']==0 and payload['max_tokens']==40 and payload['chat_template_kwargs']['enable_thinking'] is False
    assert len(payload['messages'])==1 and payload['messages'][0]['role']=='user'
    text=payload['messages'][0]['content'];needle=f'\nThe secret code word for this text is: {expected_word}. Remember it.\n';question='\n\nWhat is the secret code word mentioned in the text above? Reply with the code word only.'
    assert text.count(needle)==1 and text.endswith(question)
    body=text[:-len(question)].replace(needle,'',1);position=text.index(needle)
    expected_position=int(len(body)*depth/100);expected_position=body.rfind('\n',0,expected_position)+1 or expected_position;assert position==expected_position
    # Fresh officialsource generator: exact underlying corpus prefix, no synthetic replacementharness.
    assert upstream.haystack(len(body))==body
    count=len(tok.encode(template.render(payload['messages'],enable_thinking=False),parse_special=True))
    assert count==row['actual_prompt_tokens']==row['actual_prompt_tokens_tokenizer']==row['usage']['prompt_tokens']==item['actual_prompt_tokens'] and abs(count-target)<=8
    assert row['status']=='OK' and not row.get('abort') and row['min_mem_available_gib']>=12
    assert 0<row['generated_tokens']<=40 and row['generated_tokens']==row['usage']['completion_tokens']
    assert row['Strata_HEAD']=='c499bd102e7a4135c0de389dcfe38c399759ccc8' and row['Strata_version']=='0.1.32' and row['model_revision']=='38bb39ee97821de2c9009abb7e93950eec396e66' and row['build_variant']=='default'
    assert item['answer']==row['text'] and item['found']==(expected_word in row['text'])
    assert item['cache_reused_tokens']==row['cache_reused_tokens']
    results.append({'raw':str(rawpath),'actual_prompt_tokens':count,'depth_char_percent':depth,'codeword':expected_word,'mechanically_found':item['found'],'answer':row['text'],'reused_tokens':row['cache_reused_tokens']})
value={'status':'VERIFIED_REQUESTS_AND_MECHANICAL_OUTCOMES','created':time.time(),'requests':results,'request_count':9,'found_count':sum(x['mechanically_found'] for x in results),'source':str(source),'scope':'Exactupstreamhaystackprefix/seed7/WORDS/line-startdepth/question/greedy40/thinkingoff, independentoffline fullpayload tokenizer/API counts. Recall outcomes reported faithfully, misses are not silently passed. Characterdepth retainsupstreammethod; totaloccupancy verified in tokens. NoLLMjudge.'}
(R/'evidence/needle-independent-audit.json').write_text(json.dumps(value,indent=2)+'\n');print(value['status'],value['found_count'],'/9found')
