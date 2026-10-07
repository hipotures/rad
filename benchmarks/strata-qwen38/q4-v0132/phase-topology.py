"""v0.1.32 full arena auto/manualsplit, sequential candidate boundaries."""
import run as r,json,statistics,re,time,copy

def validate(label,res,n):
 assert res['status']=='OK' and len(res['runs'])==n,(label,res.get('error'))
 for i in range(1,n+1):
  p=r.ROOT/'raw'/f'{label}-run{i}.json';d=json.loads(p.read_text())
  assert d['Strata_HEAD']==r.HEAD and d['Strata_version']=='0.1.32' and d['build_variant']=='default'
  assert d['generated_tokens']==256 and d['cache_reused_tokens']==0 and abs(d['actual_prompt_tokens']-63400)<=8 and d['actual_prompt_tokens']==d['actual_prompt_tokens_tokenizer'] and not d['abort']
 return res

def checkpoint(running,winners=None):
 p=r.ROOT/'STATUS.json';s=json.loads(p.read_text());s['running']=running
 if winners:s['current_winners']['topology']=winners
 s['next_exact_action']='Finish currentauto/manualsplitcandidate; verify raw request count/tokenizer/reuse. Then TOP2warmup+3. No concurrent engines. Subsequentphase controlledPPversioncomparison then prefill.'
 p.write_text(json.dumps(s,indent=2));(r.ROOT/'STATUS.md').write_text('# v0.1.32 — IN_PROGRESS\n\nRunning: '+json.dumps(running)+'\n\nCurrentwinners: '+json.dumps(s['current_winners'])+'\n\nNext: '+s['next_exact_action']+'\n\n## Completed\n\n'+'\n'.join('- '+x for x in s['completed'])+'\n\n## Pending\n\n'+'\n'.join('- '+x for x in s['pending'])+'\n')

assert json.loads((r.ROOT/'raw/phase-baseline-terminal.json').read_text())['status']=='COMPLETE'
label='SPLIT-auto-v0132';checkpoint({'phase':'auto layer split smoke8K then measured64K','candidate':label})
auto=validate(label,r.candidate(label,r.config(label,'split','auto'),1),1)
text=(r.ROOT/'logs'/f'{label}-engine.log').read_text();m=re.search(r'layer split auto: K=(\d+)',text);assert m,'AutoK absent from realstartup log'
K=int(m[1]);ks=[20,22,24,26]
if K not in ks:ks=sorted(set(ks+[K,K-2,K+2]))
ks=[k for k in ks if 2<=k<=46];screens=[]
for k in ks:
 label=f'SPLIT-K{k}-screen-v0132';checkpoint({'phase':'manual Kscreen','candidate':label,'K':k})
 screens.append(validate(label,r.candidate(label,r.config(label,'split',k),1),1))
leaders=sorted(screens,key=lambda d:(d['median_tg'],d['median_pp']),reverse=True)[:2];confirmed=[]
for candidate in leaders:
 src=candidate['candidate'];cfg=json.loads((r.ROOT/'configs'/f'{src}.json').read_text());label=src.replace('-screen-','-confirm-');cfg.update(log=str(r.ROOT/'logs'/f'{label}-engine.log'));r.c.save(r.ROOT/'configs'/f'{label}.json',cfg)
 checkpoint({'phase':'TOP2warmup+3','candidate':label,'K':cfg['layer_split']})
 confirmed.append(validate(label,r.candidate(label,cfg,3,True),3))
rank=sorted(confirmed,key=lambda d:(d['median_tg'],d['median_pp']),reverse=True);best=rank[0]
r.c.save(r.ROOT/'raw/topology-selection.json',{'status':'COMPLETE','auto_K':K,'screen_K':ks,'auto':auto,'screens':screens,'confirmed':confirmed,'winner':best['candidate'],'note':'TGprimary, PPsecondary; freshengines per candidate, no enginepatch, arena has allroutedexperts, samefrozen sourcecorpus.'})
r.c.save(r.ROOT/'raw/phase-topology-terminal.json',{'status':'COMPLETE','exit_code':0,'ended':time.time(),'auto_K':K,'best':best['candidate'],'median_PP':best['median_pp'],'median_TG':best['median_tg']})
s=json.loads((r.ROOT/'STATUS.json').read_text());s['completed'].append('auto/fullarena layer split and Kscreen/TOP2confirm COMPLETE');s['pending']=[x for x in s['pending'] if not x.startswith('auto layer split') and not x.startswith('manual K20')];(r.ROOT/'STATUS.json').write_text(json.dumps(s,indent=2));checkpoint(None,{'candidate':best['candidate'],'TG':best['median_tg'],'PP':best['median_pp'],'config':str(r.ROOT/'configs'/f"{best['candidate']}.json")})
print('Topologyphase COMPLETE',best['candidate'],best['median_tg'],flush=True)
