#!/usr/bin/env python3
"""Finish artifacts only after both timed cohorts have completed; never overlaps measurements."""
import json,pathlib,subprocess,sys,time,os,traceback,shutil,hashlib
ROOT=pathlib.Path(__file__).resolve().parent
R=pathlib.Path(sys.argv[1]).resolve()
def save(data):
 p=R/'finalization-progress.json';t=p.with_suffix('.json.tmp');t.write_text(json.dumps(data,indent=2)+'\n');os.replace(t,p)
save({'status':'WAITING_MEASUREMENTS','pid':os.getpid()})
try:
 while True:
  states=[json.loads((R/n).read_text()) for n in ['progress.json','followup-progress.json']]
  if all(x.get('status')=='MEASUREMENTS_COMPLETE' and not x.get('running') for x in states):break
  if any(x.get('status') in ['FAILED','STOPPED'] for x in states):raise RuntimeError('Measurement phase needs manual review; not finalizing or starting Strata')
  time.sleep(10)
 time.sleep(5)
 gpu=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
 assert not gpu.strip(),'CUDA processes remain after measurement phases'
 code=R/'code-final';code.mkdir(exist_ok=True)
 files=list(ROOT.glob('*.py'))+[ROOT/'README.md',ROOT/'run_campaign.sh']+list((ROOT/'src').glob('*'))
 manifest=[]
 for p in files:
  if not p.is_file():continue
  relative=p.relative_to(ROOT);dst=code/relative;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
  manifest.append({'source':str(p),'snapshot':str(dst),'SHA256':hashlib.sha256(p.read_bytes()).hexdigest()})
 (R/'final-code-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 for phase in ['analyze.py','normalize.py','report-final.py','final-audit.py']:
  save({'status':'FINALIZING','phase':phase,'pid':os.getpid()})
  with (R/'raw'/('finalization-'+phase+'.log')).open('w') as out:
   p=subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/phase),str(R)],stdout=out,stderr=subprocess.STDOUT)
  if p.returncode:raise RuntimeError(phase+' failed; inspect finalization log')
 save({'status':'COMPLETE','report':str(R/'report.md'),'audit':str(R/'final-audit.json'),'pid':os.getpid()})
 print('Hardware final report and independent audit COMPLETE',flush=True)
except BaseException:
 (R/'raw/finalization-exception.txt').write_text(traceback.format_exc());save({'status':'STOPPED_NEEDS_REVIEW','exception':traceback.format_exc(),'pid':os.getpid()});raise
