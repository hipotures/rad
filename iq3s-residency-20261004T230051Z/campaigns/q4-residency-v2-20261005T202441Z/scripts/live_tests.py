"""Existing targeted numerical/cache/pool tests plus explicit known fixture failures."""
from campaign import C,R,load,save,guard
import subprocess,time,xml.etree.ElementTree as ET

def main():
 guard();assert (C/'phase-b/report.md').exists()
 results=[]
 for variant in ['history-v2','early-v1']:
  ip=C/'git/builds'/variant/'identity.json'
  if not ip.exists():continue
  ident=load(ip);out=C/'analysis/live-tests'/variant;out.mkdir(parents=True,exist_ok=False)
  cmd=[str(R/'src/control/.venv/bin/ctest'),'--test-dir',ident['build'],'--output-on-failure','--timeout','120','--output-junit',str(out/'junit.xml')]
  with (out/'suite.log').open('x') as f:
   start=time.time();res=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=900)
  root=ET.parse(out/'junit.xml').getroot();fail=[n.attrib['name'] for n in root.iter('testcase') if n.find('failure') is not None];known={'ple_parity','platform_memory_test','expert_parity','pool_test'}
  row={'variant':variant,'command':cmd,'exit_code':res.returncode,'wall_s':time.time()-start,'failures':fail,'known_fixture_failures':sorted(known),'new_failures':sorted(set(fail)-known)};save(out/'result.json',row);results.append(row)
  assert not row['new_failures'] and (not res.returncode or fail),row
  print('TARGETED_EXISTING_TESTS',variant,'no new failure; preserved known fixture cases',flush=True)
 save(C/'phase-c/existing-tests.json',results)
if __name__=='__main__':main()
