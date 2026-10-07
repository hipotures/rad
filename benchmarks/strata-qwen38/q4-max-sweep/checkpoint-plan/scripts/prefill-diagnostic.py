#!/usr/bin/env python3
"""One upstream phase-timing diagnostic after the complete performance campaign."""
import json,os,re
import run as r
import topology as t

def main():
 for stage in ['tuning','contexts','extended','quality']:
  path=r.ROOT/'raw'/f'phase-{stage}-terminal.json'
  assert path.exists() and json.loads(path.read_text())['exit_code']==0,stage+' still incomplete'
 done=r.ROOT/'raw/prefill-diagnostic-done.json'
 if done.exists():
  assert json.loads(done.read_text())['status']=='OK'
  return
 # This is current upstream instrumentation, not an engine change. Its rates are excluded from selection.
 os.environ['STRATA_PREFILL_TIMING']='1'
 label='PP-DIAGNOSTIC-FINAL-A';cfg=t.clone(label,'FINAL-A')
 with r.Session(label,cfg) as s:
  s.request(8000,64,'smoke','diagnostic_smoke')
  rec=s.request(127000,256,'128K','diagnostic')
 log=r.ROOT/'raw'/f'{label}-128K-engine.log'
 lines=[x for x in log.read_text().splitlines() if 'strata prefill timing:' in x]
 assert lines,'Expected normal upstream prefill phase timing was not emitted'
 r.c.save(done,{'status':'OK','run':rec,'timing_lines':lines,'source':'src/prefill/prefill.cpp906-950,1893-1907 at frozen HEAD','instrumentation':'STRATA_PREFILL_TIMING=1','scope':'One actual127K request plus smoke. Diagnostic only; CUDA events can alter wall time. Not included in sweep ranking or finalist medians. Timelines include waits, may overlap across stages, and do not isolate pure kernel time. Lines without stage identity are not attributed to a particular GPU.'})
 print('Upstream prefill phase diagnostic complete',len(lines),'timing lines',flush=True)

if __name__=='__main__':main()
