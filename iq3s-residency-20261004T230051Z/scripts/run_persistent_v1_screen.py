"""One counted exploratory point, fresh warmup and 4096 output, same-binaryOFF vsON."""
from lab import ROOT,Session,load,save
import subprocess
base=ROOT/'experiments/E029-persistent-runtime/v1-fixed';assert load(base/'correctness/paired-summary.json')['state']=='PASS_LIMITED_BATTERY'
rows=[]
for role in ['off','on']:
 name='persistent-v1-fixed-'+role;path=base/f'screen/32k/{role}/rep1';assert not path.exists()
 with Session(name,'32k',path,diagnostic_env={'STRATA_LAB_PERSISTENT_LOG':'{attempt}/raw/admissions'}) as session:
  assert session.request('warmup','warmup','warmup')['state']=='VALID'
  r=session.request('32k-run1','run','measured');rows.append(r);save(path/'results.json',{'run':r,'counts_toward_maximum3':True})
 assert r['state']=='VALID',r.get('invalid_reasons')
a,b=rows;save(base/'screen-summary.json',{'state':'COMPLETE_SCREEN','rows':rows,'deltaTG':100*(b['TG']/a['TG']-1),'deltaWall':100*(b['wall_s']/a['wall_s']-1),'sameOutput':load(base/'screen/32k/off/rep1/raw/output-ids-request2.json')==load(base/'screen/32k/on/rep1/raw/output-ids-request2.json'),'not_final_median':True});print('SCREEN',a['TG'],b['TG'],flush=True)
