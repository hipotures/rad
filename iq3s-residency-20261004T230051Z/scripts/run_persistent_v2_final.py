"""Final frozen candidate; exactly3 valid requests/point, no tuning duringmatrix."""
from lab import ROOT,Session,save,load
import subprocess
base=ROOT/'experiments/E029-persistent-runtime/v2-fixed';py=str(ROOT/'src/control/.venv/bin/python');assert load(base/'correctness/paired-summary.json')['state']=='PASS_LIMITED_BATTERY';assert load(base/'byte-audit/summary.json')['state']=='PASS_EXACT_PROMOTED_BYTES_BOTH_PROFILES'
assert not (base/'final').exists();save(base/'final/protocol.json',{'fresh_servers':'Each profile/rep/role freshserver, same64warmup and saved inputIDs, no reuse/lookup','measured':3,'output':4096,'pair_order':'rep1 OFF/ON, rep2 ON/OFF, rep3 OFF/ON;32/128interleaved','selected_policy':'v2 lifetime64/64MiB perdevice/alpha1; no changes duringmatrix','screen':'Noextra v2screen;finalrep1isfirstnewcleanpoint, retained evennegative.'})
for rep in [1,2,3]:
 for profile in ['32k','128k']:
  for role in (['off','on'] if rep%2 else ['on','off']):
   path=base/f'final/{profile}/{role}/rep{rep}';name='persistent-v2-'+role
   with Session(name,profile,path,diagnostic_env={'STRATA_LAB_PERSISTENT_LOG':'{attempt}/raw/admissions'}) as s:
    assert s.request('warmup','warmup','warmup')['state']=='VALID';r=s.request(f'{profile}-run{rep}','run','measured');save(path/'results.json',{'run':r,'valid_count':int(r['state']=='VALID')})
   if r['state']!='VALID':raise RuntimeError('Preservedinvalidrun; diagnosebeforeanyreplacement')
   subprocess.run([py,'scripts/analyze_persistent_live.py'],cwd=ROOT,check=True)
print('FINAL_MATRIX_COMPLETE',flush=True)
