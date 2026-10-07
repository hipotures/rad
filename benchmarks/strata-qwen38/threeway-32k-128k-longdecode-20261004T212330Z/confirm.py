import driver as d,run as r, json,copy
R=r.ROOT
out=[]
for variant in ['CURRENT','HELPER']:
 label=variant+'-32K-16K';cfg=json.loads((R/'configs'/f'{variant}.json').read_text());cfg['log']=str(R/'logs'/f'{label}-engine.log');d.save(R/'configs'/f'{label}.json',cfg)
 result={'variant':variant,'context':'32K-16K','mode':'long','runs':[],'invalid':[]}
 d.status(label+' fresh startup')
 with r.Session(label,cfg) as s:
  result['layout']=d.layout(s);wa=d.request(s,d.warm,'warmup','warmup');assert wa['valid']
  for i in [1,2,3]:
   p=json.loads((R/'payloads'/f'32K-long-run{i}.json').read_text());p['max_tokens']=16384
   a=d.request(s,p,f'run{i}')
   if a['valid']:result['runs'].append(str(R/'raw'/f'{label}-run{i}.json'))
   else:
    result['invalid'].append(str(R/'raw'/f'{label}-run{i}.json'));break
 result['status']='COMPLETE' if len(result['runs'])==3 else 'OPTIONAL_FIXED_LENGTH_UNAVAILABLE_EARLY_STOP'
 d.save(R/'raw'/f'{label}-done.json',result);out.append(result)
d.save(R/'analysis/confirmation-results.json',out);d.status('Optional confirmation finished; analyze and audit')
