#!/usr/bin/env python3
"""Deferred isolated builds. Never compile or use CUDA beside hardware measurements."""
import hashlib,json,os,pathlib,subprocess,sys,time,traceback
R=pathlib.Path(__file__).resolve().parent
HW=pathlib.Path('/srv/ai/benchmarks/qwen-hardware-characterization/run-20261004T104353Z')
os.environ['UV_CACHE_DIR']=str(R/'uv-cache')
HEAD=json.loads((R/'git/main.json').read_text())['sha']
def save(name,data):
 p=R/name;tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');os.replace(tmp,p)
def command(argv,label,cwd=None,timeout=3600,allowed=(0,)):
 print('Starting '+label,flush=True)
 save('build-progress.json',{'status':'BUILDING','phase':label,'command':argv,'pid':os.getpid()})
 with (R/'logs'/f'{label}.log').open('w') as out:
  p=subprocess.run(argv,cwd=cwd,stdout=out,stderr=subprocess.STDOUT,timeout=timeout)
 info={'command':argv,'cwd':str(cwd) if cwd else None,'returncode':p.returncode,'log':str(R/'logs'/f'{label}.log')};save('git/'+label+'-command.json',info)
 if p.returncode not in allowed:raise RuntimeError(label+' failed; inspect '+info['log'])
 return info
save('build-progress.json',{'status':'WAITING_HARDWARE_FINAL_AUDIT','pid':os.getpid(),'hardware_run':str(HW)})
try:
 while True:
  audit=HW/'final-audit.json'
  if audit.exists() and json.loads(audit.read_text()).get('status')=='PASS':break
  for name in ['progress.json','followup-progress.json']:
   p=HW/name
   if p.exists() and json.loads(p.read_text()).get('status') in ['STOPPED','FAILED']:
    raise RuntimeError('Hardware campaign needs attention; not starting Strata.')
  time.sleep(10)
 gpu=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
 if gpu.strip():raise RuntimeError('CUDA processes still active; defer builds/benchmarks.')
 save('build-progress.json',{'status':'BUILDING','pid':os.getpid()})
 vendor=R/'vendor';vendor.mkdir(exist_ok=True)
 archive=vendor/'ggml-pinned.tar.gz';pinned='3cf03257f219afbe7334045ff7c6a06ac68c627d'
 if not archive.exists():
  with archive.open('xb') as f:subprocess.run(['gh','api','repos/ggml-org/llama.cpp/tarball/'+pinned],stdout=f,check=True,timeout=600)
 import tarfile
 with tarfile.open(archive) as tar:
  dirname=tar.getmembers()[0].name.split('/')[0]
  if not (vendor/dirname).exists():tar.extractall(vendor,filter='data')
 ggml=vendor/dirname
 save('git/ggml-source.json',{'pinned_commit':pinned,'archive_SHA256':hashlib.sha256(archive.read_bytes()).hexdigest(),'path':str(ggml),'acquisition':'gh api commit tarball; isolated source, not a model download'})
 env={'frozen_main':HEAD,'release':'v0.1.39','builds':{},'captured_wall':time.time()}
 for variant in ['control','optimized']:
  repo=pathlib.Path('/srv/ai/strata-pr578-refresh-20261004-'+variant)
  assert subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()==HEAD
  if not (repo/'.venv/bin/python').exists():
   command(['uv','venv','--python','/usr/bin/python3',str(repo/'.venv')],variant+'-venv')
  command(['uv','pip','install','--python',str(repo/'.venv/bin/python'),'-r',str(repo/'requirements.txt')],variant+'-pip')
  command(['uv','pip','install','--python',str(repo/'.venv/bin/python'),'jsonschema==4.26.0'],variant+'-jsonschema')
  cmake=str(repo/'.venv/bin/cmake');build=repo/'build-default'
  configure=[cmake,'-S',str(repo),'-B',str(build),'-G','Ninja','-DCMAKE_MAKE_PROGRAM='+str(repo/'.venv/bin/ninja'),'-DCMAKE_BUILD_TYPE=Release','-DSTRATA_ENABLE_CUDA=ON','-DCMAKE_CUDA_ARCHITECTURES=89','-DSTRATA_GGML_DIR='+str(ggml),'-DSTRATA_BUILD_TESTS=ON']
  command(configure,variant+'-configure')
  command([cmake,'--build',str(build),'-j','6'],variant+'-build')
  exe=build/'strata';assert exe.is_file()
  env['builds'][variant]={'HEAD':HEAD,'git_status':subprocess.check_output(['git','-C',str(repo),'status','--short'],text=True),'configure':configure,'build':[cmake,'--build',str(build),'-j','6'],'binary':str(exe),'binary_SHA256':hashlib.sha256(exe.read_bytes()).hexdigest()}
  command([str(repo/'.venv/bin/ctest'),'--test-dir',str(build),'--output-on-failure','-j','1'],variant+'-ctest',timeout=1800,allowed=(0,8))
  # Persist before classifying; any real failures prevent benchmarking.
  xml=build/'Testing/Temporary/LastTestsFailed.log'
  failures=[x.split(':',1)[1] for x in xml.read_text().splitlines()] if xml.exists() else []
  known={'ple_parity','expert_parity','pool_test','platform_memory_test'}
  unknown=set(failures)-known
  env['builds'][variant]['CTest_failed']=failures
  save('environment.json',env)
  if unknown:raise RuntimeError('Unclassified CTest failure(s): '+str(sorted(unknown)))
  command([str(repo/'.venv/bin/python'),'-m','unittest','discover','-s','serve','-p','test_*.py'],variant+'-python-tests',cwd=repo,timeout=600)
  helptext=subprocess.check_output([str(exe),'--help'],text=True,stderr=subprocess.STDOUT)
  (R/'logs'/f'{variant}-help.txt').write_text(helptext)
 for label,argv in [('compiler',['g++','--version']),('cuda',['/usr/local/cuda/bin/nvcc','--version']),('driver_gpu',['nvidia-smi','-q']),('CPU',['lscpu','-J']),('RAM',['cat','/proc/meminfo']),('kernel',['uname','-a']),('PCIe_topology',['nvidia-smi','topo','-m']),('PCIe_details',['lspci','-vv'])]:
  p=subprocess.run(argv,capture_output=True,text=True);env[label]={'returncode':p.returncode,'output':p.stdout,'stderr':p.stderr}
 save('environment.json',env)
 save('build-progress.json',{'status':'BUILDS_AND_TESTS_COMPLETE_REVIEW_REQUIRED','pid':os.getpid(),'next':'Inspect actual CTest failures and help, then preserve clean binaries and run fairness/correctness gates.'})
except BaseException:
 (R/'logs/build-exception.txt').write_text(traceback.format_exc())
 save('build-progress.json',{'status':'STOPPED_NEEDS_REVIEW','exception':traceback.format_exc()});raise
