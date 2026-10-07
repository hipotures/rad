import run as r,json,time
assert json.loads((r.ROOT/'raw/local-setup-terminal.json').read_text())['status']=='COMPLETE'
label='BASELINE-resident-v0132';cfg=r.config(label,'resident1',context=65536)
res=r.candidate(label,cfg,3,True)
assert res['status']=='OK' and len(res['runs'])==3,res
assert all(x['generated_tokens']==256 and x['cache_reused_tokens']==0 and x['actual_prompt_tokens']==x['actual_prompt_tokens_tokenizer'] and abs(x['actual_prompt_tokens']-63400)<=8 for x in res['runs'])
r.c.save(r.ROOT/'raw/phase-baseline-terminal.json',{'status':'COMPLETE','exit_code':0,'ended':time.time(),'median_PP':res['median_pp'],'median_TG':res['median_tg'],'request_results':[str(r.ROOT/'raw'/f'{label}-run{i}.json') for i in [1,2,3]],'comparison_config_note':'Same v0.1.31 T0 CLI settings inclresident80/fullINT8/MTP4/.5, same frozen code corpus. Version/exe/independent equivalentpack/MTP paths changed. Officialsetup suggested KVstream32768/resident71, deliberately restored priorbaseline settings.'})
print('SingleGPUresident baseline COMPLETE',res['median_pp'],res['median_tg'],flush=True)
