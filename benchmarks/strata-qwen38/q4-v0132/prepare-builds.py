from pathlib import Path
import subprocess,json,time,hashlib,os,sys
R=Path(__file__).resolve().parent;repo=Path('/srv/ai/strata-v0.1.32');expected='c499bd102e7a4135c0de389dcfe38c399759ccc8'
def output(cmd,cwd=repo):
 p=subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 return {'command':cmd,'exit_code':p.returncode,'output':p.stdout}
def save(path,d):path.write_text(json.dumps(d,indent=2,ensure_ascii=False))
assert output(['git','rev-parse','HEAD'])['output'].strip()==expected
assert output(['git','rev-parse','v0.1.32^{commit}'])['output'].strip()==expected
assert (repo/'third_party/llama.cpp-pinned/ggml/CMakeLists.txt').exists()
assert (R/'evidence/llama-3cf032-source.tar.gz').exists()
commands={'git_status':['git','status','--porcelain'],'compiler':['c++','--version'],'CUDA':['/usr/local/cuda/bin/nvcc','--version'],'driver_GPU':['nvidia-smi','--query-gpu=index,name,driver_version,memory.total,pci.bus_id,pcie.link.gen.current,pcie.link.gen.max,pcie.link.width.current,pcie.link.width.max','--format=csv'],'CPU':['lscpu'],'RAM':['cat','/proc/meminfo'],'kernel':['uname','-a'],'PCIe_topology':['nvidia-smi','topo','-m'],'VM':['systemd-detect-virt'],'mount':['findmnt','-T','/srv/ai/models/strata/models/UD-Q4_K_XL'],'python':['.venv/bin/python','--version'],'pip':['.venv/bin/python','-m','pip','freeze']}
env={'tag':'v0.1.32','HEAD':expected,'source_frozen':True,'captured':time.time(),'commands':{k:output(v) for k,v in commands.items()},'build_variants':{}}
save(R/'environment.json',env)
old=Path('/srv/ai/benchmarks/strata-qwen38/q4-max-sweep')
model=json.loads((old/'raw/model-stat-checkpoint.json').read_text())
for f in model['files']:
 s=Path(f['path']).stat();assert s.st_size==f['bytes'] and s.st_mtime_ns==f['mtime_ns'] and s.st_ino==f['inode'],f
model.update(stat_rechecked=time.time(),status='EXISTING_VERIFIED_SHARDS_STAT_IDENTITY_MATCH',note='Reuses prior SHA256 verification; current size/inode/mtime match. No model download or111GB rehash.');save(R/'raw/model-provenance.json',model)
for variant,on in [('default','OFF'),('q4-fast','ON')]:
 build=repo/('build-'+variant)
 cmd=[str(repo/'.venv/bin/cmake'),'-S',str(repo),'-B',str(build),'-G','Ninja','-DCMAKE_BUILD_TYPE=Release','-DSTRATA_ENABLE_CUDA=ON','-DCMAKE_CUDA_ARCHITECTURES=89','-DSTRATA_GGML_DIR='+str(repo/'third_party/llama.cpp-pinned'),'-DSTRATA_BUILD_TESTS=ON','-DSTRATA_MMQ_KQUANTS='+on]
 env['build_variants'][variant]={'configure':cmd,'status':'BUILDING','started':time.time()};save(R/'environment.json',env)
 with (R/'logs'/('build-'+variant+'.log')).open('w') as log:
  for action in [cmd,[str(repo/'.venv/bin/cmake'),'--build',str(build),'--target','strata']+(['prefill_mmq_kquant_test'] if on=='ON' else [])+['-j','8']]:
   log.write('COMMAND '+json.dumps(action)+'\n');log.flush();p=subprocess.run(action,cwd=repo,stdout=log,stderr=subprocess.STDOUT)
   if p.returncode:
    env['build_variants'][variant].update(status='FAIL',exit_code=p.returncode);save(R/'environment.json',env);sys.exit(p.returncode)
 exe=build/'strata';help_record=output([str(exe),'--help']);save(R/'evidence'/('help-'+variant+'.json'),help_record)
 (R/'evidence'/('help-'+variant+'.txt')).write_text(help_record['output'])
 if on=='ON':
  test=output([str(repo/'.venv/bin/ctest'),'--test-dir',str(build),'-R','^prefill_mmq_kquant_test$','--output-on-failure']);save(R/'raw/q4-fast-kernel-test.json',test)
  assert test['exit_code']==0,'Upstream Q4 fast numerical test failed'
 env['build_variants'][variant].update(status='COMPLETE',ended=time.time(),exe=str(exe),sha256=hashlib.sha256(exe.read_bytes()).hexdigest());save(R/'environment.json',env)
save(R/'raw/builds-terminal.json',{'status':'COMPLETE','ended':time.time(),'variants':env['build_variants']})
print('Both separate builds complete. No benchmark requests started.',flush=True)
