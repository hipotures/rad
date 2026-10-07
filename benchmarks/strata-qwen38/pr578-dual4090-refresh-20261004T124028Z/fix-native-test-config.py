import json,subprocess,hashlib,pathlib
R=pathlib.Path(__file__).resolve().parent
e=json.loads((R/'environment.json').read_text())
for v in ['control','optimized']:
 repo=pathlib.Path('/srv/ai/strata-pr578-refresh-20261004-'+v)
 cmd=e['builds'][v]['configure']+['-DSTRATA_NATIVE_EXPERTS=ON']
 for label,argv in [('native-configure',cmd),('native-build',e['builds'][v]['build'])]:
  (R/'build-progress.json').write_text(json.dumps({'status':'BUILDING','phase':v+'-'+label,'command':argv})+'\n')
  with (R/'logs'/f'{v}-{label}.log').open('w') as f:subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT,check=True)
 e['builds'][v]['configure']=cmd;e['builds'][v]['binary_SHA256']=hashlib.sha256((repo/'build-default/strata').read_bytes()).hexdigest()
 if v=='optimized':
  argv=[str(repo/'.venv/bin/ctest'),'--test-dir',str(repo/'build-default'),'--output-on-failure','-j','1']
  with (R/'logs/optimized-ctest.log').open('w') as f:p=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT)
  assert p.returncode==8
  failed=(repo/'build-default/Testing/Temporary/LastTestsFailed.log').read_text();assert set(x.split(':',1)[1] for x in failed.splitlines())=={'ple_parity','expert_parity','pool_test','platform_memory_test'}
(R/'environment.json').write_text(json.dumps(e,indent=2)+'\n')
(R/'build-progress.json').write_text(json.dumps({'status':'BUILDS_AND_TESTS_COMPLETE_REVIEW_REQUIRED','next':'Review both72-test suites and Python suites; original upstream pilot'})+'\n')
