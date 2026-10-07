from lab import ROOT,save,load
import subprocess
base=ROOT/'experiments/E029-persistent-runtime';py=str(ROOT/'src/control/.venv/bin/python')
for role,enabled in [('off',False),('on',True)]:
 name='persistent-v1-'+role;overrides={'env':{'STRATA_POOL_SPIN_US':'100'},'policy':'OFF originalP1 math/cache' if not enabled else 'Persistent h8 same-device alpha1 conservativeutility','experimental':enabled,'safe_serve_only':True,'extra_explicit_GPU_bytes_per_device':320 if enabled else 0}
 if enabled:overrides['env']['STRATA_LAB_PERSISTENT']='1'
 path=base/f'{name}-overrides.json';save(path,overrides)
 subprocess.run([py,'scripts/register_variant.py',name,'--source',str(ROOT/'src/persistent-runtime-v1'),'--binary',str(ROOT/'builds/persistent-runtime-v1/strata'),'--overrides',str(path)],cwd=ROOT,check=True)
 for profile in ['32k','128k']:
  p=ROOT/'variants'/name/(profile+'.json');cfg=load(p);cfg['server_entrypoint']=str(ROOT/'scripts/serve_capture.py');save(p,cfg)
