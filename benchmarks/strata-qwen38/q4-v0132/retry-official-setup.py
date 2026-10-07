from pathlib import Path
import os,json,subprocess,time
R=Path(__file__).resolve().parent;repo=Path('/srv/ai/strata-v0.1.32');data=Path('/srv/ai/models/strata-v0132');local=data/'gguf-local';local.mkdir(exist_ok=True)
proof=json.loads((R/'raw/model-provenance.json').read_text())
for f in proof['files']:
 src=Path(f['path']);s=src.stat();assert (s.st_size,s.st_mtime_ns,s.st_ino)==(f['bytes'],f['mtime_ns'],f['inode'])
 dst=local/src.name;dst.symlink_to(src)
 dst.with_name(dst.name+'.done').write_text('sha256 '+f['previous_verified_sha256']+'\nReused prior fullSHA256 verification; originalinode/size/mtimechecked. Provenance: '+str(R/'raw/model-provenance.json')+'\n')
env=dict(os.environ,XDG_CONFIG_HOME=str(R/'setup-xdg-config'),STRATA_GGUF_PY=str(repo/'third_party/llama.cpp-pinned/gguf-py'))
cmd=[str(repo/'.venv/bin/python'),str(repo/'setup.py'),'--setup','--family','unsloth','--model','UD-Q4_K_XL','--gpu','0','--context','65536','--kv','int8','--vision','none','--experimental-speed-projection','off','--gguf-dir',str(local),'--data-dir',str(data),'--yes','--no-start']
with (R/'logs/official-local-setup-isolated.log').open('w') as f:
 f.write('COMMAND '+json.dumps(cmd)+'\nXDG_CONFIG_HOME '+env['XDG_CONFIG_HOME']+'\n');f.flush();p=subprocess.run(cmd,cwd=repo,env=env,stdout=f,stderr=subprocess.STDOUT)
assert p.returncode==0,'Isolatedsetup failed; inspect log without retry/download'
for f in proof['files']:
 s=Path(f['path']).stat();assert (s.st_size,s.st_mtime_ns,s.st_ino)==(f['bytes'],f['mtime_ns'],f['inode'])
pack=Path('/srv/ai/models/strata/packs/ud-q4_k_xl-v0132');assert not (pack/'experts.bin').exists()
(R/'raw/local-setup-terminal.json').write_text(json.dumps({'status':'COMPLETE','ended':time.time(),'command':cmd,'environment_overrides':{'XDG_CONFIG_HOME':env['XDG_CONFIG_HOME']},'model_revision':'38bb39ee97821de2c9009abb7e93950eec396e66','HEAD':'c499bd102e7a4135c0de389dcfe38c399759ccc8','version':'0.1.32','build_variant':'default','pack':str(pack),'mtp':str(data/'mtp/rt'),'original_shard_stat_identity_retained':True,'no_engine_started':True},indent=2))
print('Isolatedofficialsetup COMPLETE',flush=True)
