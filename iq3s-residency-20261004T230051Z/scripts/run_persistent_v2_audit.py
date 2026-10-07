"""Real full4K placements at bothprofiles, exact GPU/RAM readback outsidedecode timer."""
from lab import ROOT,Session,load,save
import re
base=ROOT/'experiments/E029-persistent-runtime/v2-fixed';assert load(base/'correctness/paired-summary.json')['state']=='PASS_LIMITED_BATTERY';rows=[]
for profile in ['32k','128k']:
 path=base/f'byte-audit/{profile}';assert not path.exists()
 with Session('persistent-v2-on',profile,path,diagnostic_env={'STRATA_LAB_PERSISTENT_CHECK':'1','STRATA_LAB_PERSISTENT_LOG':'{attempt}/raw/admissions'}) as s:
  assert s.request('warmup','warmup','warmup')['state']=='VALID';r=s.request(profile+'-run1','run','diagnostic');save(path/'results.json',{'run':r,'headline':False,'posttiming_readback':True})
 log=(path/'raw/run-engine.log').read_text();m=re.search(r'exact RAM/GPU expert bytes PASS, checked=(\d+) bytes=(\d+)',log);assert m and int(m[1])>100 and r['actual_output_tokens']==4096 and r['reuse']==0,(profile,log[-1000:])
 rows.append({'profile':profile,'state':'PASS','checked_experts':int(m[1]),'checked_bytes':int(m[2]),'raw':str(path),'generated':r['actual_output_tokens'],'actualinput':r['actual_input_tokens'],'claim':'Byteidentity of livepromotedexperts stillresident plus ownership/size invariants. Check afterallpendingcopyevents, outside timer. Not a speedrun.'});print(rows[-1],flush=True)
save(base/'byte-audit/summary.json',{'state':'PASS_EXACT_PROMOTED_BYTES_BOTH_PROFILES','rows':rows})
